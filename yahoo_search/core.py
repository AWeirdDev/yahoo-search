"""Simple Yahoo Search with Python API."""

import json
from typing import Any, Dict, List, Literal, Optional
from urllib.parse import quote_plus, unquote, urlsplit

import httpx
from pydantic import BaseModel
from selectolax.lexbor import LexborHTMLParser as Parser

MD_TAGS = ["strong", "b", "s", "i"]
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 OPR/102.0.0.0 "
        "(Edition GX-CN)"
    )
}

class AlsoTryItem(BaseModel):
    link: str
    text: str

class PageResult(BaseModel):
    title: str
    link: str
    text: Optional[str] = None

class CardResultSource(BaseModel):
    link: str
    text: str

class CardResult(BaseModel):
    image: Optional[str] = None
    heading: Optional[str] = None
    text: Optional[str] = None
    source: Optional[CardResultSource] = None

class RelatedSearch(BaseModel):
    link: str
    text: str

class SearchResult(BaseModel):
    also_try: List[AlsoTryItem]
    pages: List[PageResult]
    card: Optional[CardResult] = None
    related_searches: List[RelatedSearch]

class News(BaseModel):
    title: str
    thumbnail: Optional[str] = None
    source: Optional[str] = None
    last_updated: Optional[str] = None
    text: Optional[str] = None

class NewsSearchResult(BaseModel):
    news: List[News]

class Video(BaseModel):
    age: Optional[str] = None
    cite: Optional[str] = None
    thumbnail: Optional[str] = None
    video_preview: Optional[str] = None
    title: str
    link: str

class VideoSearchResult(BaseModel):
    videos: List[Video]

class HighLowTemperature(BaseModel):
    highest: int
    lowest: int

class WeatherForecastInner(BaseModel):
    text: str
    icon: str

class Precipitation(BaseModel):
    icon: str
    percentage: str

class WeatherForecast(BaseModel):
    fahrenheit: HighLowTemperature
    celsius: HighLowTemperature
    weather: WeatherForecastInner
    precipitation: Precipitation

class WeatherInformation(BaseModel):
    location: str
    country: str
    time: str
    celsius: int
    fahrenheit: int
    weather: str
    weather_icon: str
    forecast: Dict[
        Literal[
            "Monday", 
            "Tuesday", 
            "Wednesday", 
            "Thursday", 
            "Friday", 
            "Saturday", 
            "Sunday"
        ],
        WeatherForecast
    ]
    

def get_abs_link(r_search_link: Optional[str]) -> str:
    if not r_search_link:
        return ""

    return unquote(
        urlsplit(r_search_link).path.split("RU=")[1].split('/')[0] # type: ignore
    )

def get_abs_image(yimg_link: Optional[str]) -> str:
    if not yimg_link:
        return ""

    return "https://" + yimg_link.split('https://')[1]

def search(query: str) -> SearchResult:
    """Searches Yahoo using a text query.

    Args:
        query (str): The query.

    Example:
        .. code-block :: python

            s = search("chocolate")
            print(s.pages[0].title)
            # Chocolate - Wikipedia
            print(s.related_searches[0])
            # RelatedSearch(
            #   link='https://sg.search.yahoo.com/(...)'
            #   text='awfully chocolate'
            # )

    Returns:
        SearchResult: The search result.
    """
    client = httpx.Client()
    res = client.get(
        "https://sg.search.yahoo.com/search?q={}".format(
            quote_plus(query)
        ), 
        headers=headers
    )
    res.raise_for_status()

    parser = Parser(res.text)
    search = parser.css_first(".reg.searchCenterMiddle")
    contents = {
        "also_try": [],
        "pages": [],
        "card": {},
        "related_searches": []
    }

    assert search, "Could not find '.reg.searchCCenterMiddle' (search results)"

    for webpage in search.css(".dd.algo.algo-sr"):
        page_results = {}
    
        for title in webpage.css("div.compTitle h3 a"):
            link = title.attributes['href']
            absLink = get_abs_link(link)
            title = title.last_child.text() if title.last_child else ""
            page_results.update({
                "title": title,
                "link": absLink
            })

        for texts in webpage.css(".compText.aAbs p"):
            texts.unwrap_tags(MD_TAGS)
            text = texts.text(deep=True, separator=" ", strip=True)
            page_results.update({
                "text": text
            })

        contents['pages'].append(page_results)

    card = parser.css_first(".cardReg.searchRightTop")

    if card:
        image = card.css_first('img')

        if image:
            contents["card"]["image"] = get_abs_image(
                image.attributes['src']
            )

        heading_2 = card.css_first('p.pl-15.pr-10 span')

        if heading_2:
            heading_2.unwrap_tags(MD_TAGS)
            text = heading_2.text(deep=True, separator=" ", strip=True)
            contents["card"]["heading"] = text

        inner_content = card.css_first('div.compText p')

        if inner_content:
            text = inner_content.first_child
            contents["card"]["text"] = text.text() if text else ""

            source = inner_content.css_first("a")
    
            if source:
                contents["card"]["source"] = {
                    "link": get_abs_link(
                        source.attributes.get("href")
                    ),
                    "text": source.text()
                }

    also_try = parser.css(
        'ol.cardReg.searchTop .compDlink li span a'
    )

    if also_try:
        for item in also_try:
            contents["also_try"].append({
                "link": item.attributes['href'],
                "text": item.text()
            })

    related_searches = parser.css(
        'ol.scf.reg.searchCenterFooter tbody tr td a'
    )

    if related_searches:
        for item in related_searches:
            item.unwrap_tags(MD_TAGS)
            text = item.text(deep=True, separator=" ", strip=True)

            contents["related_searches"].append({
                "link": item.attributes['href'],
                "text": text
            })
    

    return SearchResult(**contents)

def query_to_tabs(query: str) -> Dict[str, str]:
    """Converts a query to tab item links.

    Including: ``images``, ``news``, ``videos``.

    Args:
        query (str): Quoted query.

    Example:
        .. code-block :: python

            query_to_tabs("hello")
            # {
            #   "images": "https://sg.image.search.yahoo.com/(...)",
            #   "news": "https://sg.news.search.yahoo.com/(...)",
            #   "videos": "https://sg.video.search.yahoo.com/(...)"
            # }

    Returns:
        Dict[str, str]
    """
    return {
        "images": "https://sg.image.search.yahoo.com/search?q=" + query,
        "news": "https://sg.news.search.yahoo.com/search?q=" + query,
        "videos": "https://sg.video.search.yahoo.com/search?q=" + query
    }

def search_news(query: str) -> NewsSearchResult:
    """Searches news on Yahoo.

    Args:
        query (str): The query.

    Example:
        .. code-block :: python

            n = search_news("taiwan")
            print(n.news[0].title)
            # Nearly 200 people injured as Typhoon Koinu brings(...)
    """
    tabs = query_to_tabs(quote_plus(query))

    client = httpx.Client()
    res = client.get(
        tabs['news'],
        headers=headers
    )

    parser = Parser(res.text)
    page = parser.css_first('#main #web')
    assert page, "Could not find '#main #web' (news results)"

    contents = []

    for news in page.css('li .dd.NewsArticle li'):
        this = {}
        thumbnail = news.css_first('img')

        if thumbnail:
            src = thumbnail.attributes['src']
            this.update({
                "thumbnail": None if src.startswith('data:image/') else src # type: ignore
            })

        title = news.css_first('h4 a')

        if title:
            this.update({
                "title": title.text(),
                "link": title.attributes['href']
            })

        source = news.css_first('span.s-source')

        if source:
            this.update({
                "source": source.text()
            })

        last_updated = news.css_first('span.fc-2nd.s-time')

        if last_updated:
            this.update({
                "time": last_updated.text()[2:]
            })

        description = news.css_first('p.s-desc')

        if description:
            description.unwrap_tags(MD_TAGS)
            text = description.text(deep=True, separator=" ", strip=True)
            this.update({
                "text": text
            })


        contents.append(this)

    return NewsSearchResult(news=contents)

def search_videos(query: str) -> VideoSearchResult:
    """Searches videos on Yahoo.

    Args:
        query (str): The query.

    Example:
        .. code-block :: python

            v = search_videos("jvke - this is what autumn feels like")
            print(v.videos[0].link)
            # https://sg.video.search.yahoo.com/video/play;_ylt(...)

    Returns:
        VideoSearchResult: Search results.
    """
    tabs = query_to_tabs(quote_plus(query))

    client = httpx.Client()
    res = client.get(
        tabs['videos'],
        headers=headers
    )
    res.raise_for_status()

    parser = Parser(res.text)
    contents = []

    results = parser.css('#search li.vr.vres')
    assert results, "Couldn't find any results for '#search li.vr.vres'"
    
    for result in results:
        this = {}
        anchor = result.css_first("a")

        if anchor:
            this.update({
                "link": "https://sg.video.search.yahoo.com" + anchor.attributes['href'] # type: ignore
            })

            preview = anchor.attributes.get("data")

            if preview:
                meta = json.loads(preview)
                if meta['m']: # sometimes nothing
                    this.update({
                        "video_preview": meta['m']['u']
                    })

        thumbnail = result.css_first("img")

        if thumbnail:
            this.update({
                "thumbnail": thumbnail.attributes['src']
            })


        duration = result.css_first('div.pos-box .vthm .stack.grad span.v-time')

        if duration:
            this.update({
                "duration": duration.text()
            })

        metadata = result.css_first('div.v-meta')

        if metadata:
            title = metadata.first_child

            if title:
                title.unwrap_tags(MD_TAGS)
                this.update({
                    "title": title.text(deep=True, separator=" ", strip=True)
                })

            age = metadata.css_first('.v-age')

            if age:
                this.update({
                    "age": age.text()
                })

            cite = metadata.last_child

            if cite:
                this.update({
                    "cite": cite.text()
                })

        contents.append(this)

    return VideoSearchResult(videos=contents)

def weather() -> WeatherInformation:
    """Fetches weather in this location.

    Example:
        .. code-block :: python

            w = weather()
            print(w.celsius)
            # 38
            print(
                w.forecast['Monday'].fahrenheit # monday weather forecast
            )
            # HighLowTemperature(
            #   highest=92
            #   lowest=78
            # )
    """
    client = httpx.Client()
    res = client.get(
        "https://sg.news.yahoo.com/weather/",
        headers=headers
    )
    parser = Parser(res.text)

    data: Dict[str, Any] = {
        "forecast": {}
    }

    location = parser.css_first('div.M\\(10px\\) h1')

    if location:
        data.update({
            "location": location.text()
        })

    country = parser.css_first('h2.D\\(b\\)')

    if country:
        data.update({
            "country": country.text()
        })

    now = parser.css_first('time')

    if now:
        data.update({
            "time": now.text()
        })

    celsius = parser.css_first('.celsius.celsius_D\\(b\\)')

    if celsius:
        data.update({
            "celsius": int(celsius.text())
        })

    fahrenheit = parser.css_first('.fahrenheit')

    if fahrenheit:
        data.update({
            "fahrenheit": int(fahrenheit.text())
        })

    weather = parser.css_first('div#module-location-heading')

    if weather:
        img = weather.css_first('img')

        if img:
            data.update({
                "weather_icon": img.attributes['src']
            })

        text = weather.css_first('p')

        if text:
            data.update({
                "weather": text.text()
            })

        weather_table = parser.css('table[data-slk="sec:forecast;"] tbody tr')

        if weather_table:
            for row in weather_table[:7]:
                day = row.first_child.last_child.text() # type: ignore
                info = {
                    "fahrenheit": {},
                    "celsius": {}
                }

                weather = row.css_first('td.Ta\\(c\\) img')

                if weather:
                    info.update({
                        "weather": {
                            "text": weather.attributes['alt'],
                            "icon": weather.attributes['src']
                        }
                    })

                precipitation = row.css_first('td.D\\(f\\).Jc\\(c\\)')

                if precipitation:
                    img = precipitation.first_child
                    percentage = precipitation.last_child.last_child # type: ignore
                    
                    info.update({
                        "precipitation": {
                            "icon": img.attributes['src'], # type: ignore
                            "percentage": percentage.text() # type: ignore
                        }
                    })

                hl_temp = row.css('td.D\\(f\\).Jc\\(fe\\).Ta\\(end\\) dl dd')

                if hl_temp:
                    for index, item in enumerate(hl_temp):
                        text = item.text()[:-1]

                        if index == 0:
                            info["fahrenheit"].update({
                                "highest": int(text)
                            })

                        elif index == 1:
                            info["celsius"].update({
                                "highest": int(text)
                            })

                        elif index == 2:
                            info["fahrenheit"].update({
                                "lowest": int(text)
                            })

                        else:
                            info["celsius"].update({
                                "lowest": int(text)
                            })

                data["forecast"][day] = info

    return WeatherInformation(**data)

def autocomplete(query: str) -> List[str]:
    """Autocompletes a query.

    Args:
        query (str): The query.

    Example:
        .. code-block :: python

            while True:
                print(
                    autocomplete(
                        input("search: ")
                    )
                )
    """

    client = httpx.Client()
    res = client.get(
        "https://ff.search.yahoo.com/gossip?output=fxjson&query={}".format(
            quote_plus(query)
        ),
        headers=headers
    )
    return res.json()[1]
