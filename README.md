# yahoo-search

![GitHub issues](https://img.shields.io/github/issues/AWeirdScratcher/yahoo-search?style=for-the-badge&logo=github)
![PyPI - License](https://img.shields.io/pypi/l/yahoo-search?style=for-the-badge&logo=pypi&logoColor=white)

Search anything on Yahoo: web pages, news, videos, autocomplete, and weather.

## Simple API

Simple and Pythonic API with Pydantic.

Get almost every result: `also_try`, `pages`, `card`, and `related_searches`.

```python
from yahoo_search import search

result = search("chocolate")
print(result.pages[0])
```

<details>
    <summary>See Example Output</summary>

```python
PageResult(
    title='Chocolate - Wikipedia',
    link='https://en.wikipedia.org/wiki/Chocolate',
    text='A "cocoa product" is defined as a food product that is sourced from cocoa beans and contains "cocoa nibs, cocoa liquor, cocoa mass, unsweetened chocolate, bitter chocolate, chocolate liquor, cocoa, low-fat cocoa, cocoa powder, or low-fat cocoa powder". Conching. Main article: Conching.'
)
```

</details>

## Yahoo News Search

You can also search news with ease.

```python
from yahoo_search import search_news

result = search_news("taiwan")
print(result.news[0])
```

<details>
    <summary>See Example Output</summary>

```python
News(
    title='How to take the Taiwan Design Expo personality test that\'s trending on IG Stories',
    thumbnail='https://s.yimg.com/fz/api/res/1.2/(...)',
    source='Lifestyle Asia via Yahoo Style Singapore',
    text='If you\'ve always wanted to know your personality type beyond the conventional MBTI variants, it\'s...'
)
```

</details>

## Yahoo Videos Search

Search and preview online videos easily.

```python
from yahoo_search import search_videos

result = search_videos("jvke - golden hour")
print(result.videos[0].video_preview)
```

<details>
    <summary>See Example Output</summary>

```
https://tse3.mm.bing.net/th?id=OM.7UQt_nfsv8nF0A_1687237113&pid=Api
```

</details>

## Yahoo Weather

Get the weather, because why not.

```python
from yahoo_search import weather

w = weather()
print(w.celsius)
print(w.forecast["Monday"])
```

<details>
    <summary>See Example Output</summary>

```python
30
WeatherForecast(
    fahrenheit=HighLowTemperature(
        highest=92,
        lowest=78
    ),
    celsius=HighLowTemperature(
        highest=34,
        lowest=26
    ),
    weather=WeatherForecastInner(
        text='Haze',
        icon='https://s.yimg.com/g/images/spaceball.gif'
    ),
    precipitation=Precipitation(
        icon='https://s.yimg.com/g/images/spaceball.gif',
        percentage='0%'
    )
)
```

</details>

## Yahoo Autocomplete

You can add autocompletes to your applications.

```python
from yahoo_search import autocomplete

print(autocomplete("hello"))
```

<details>
    <summary>See Example Output</summary>

```python
["hello fresh", "hello kitty", "hello molly", "hello neighbor", "hello october", "hello fresh log in to my account", "hello october images", "hello kitty coloring pages", "hello magazine", "hellosign"]
```

</details>

## Models & Functions Definitions

Below are the models & functions type definitions.

<details>
    <summary>See All Models (15)</summary>

```python
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
```

</details>

<details>
    <summary>See All Functions (4)</summary>

```python
def search(query: str) -> SearchResult: ...
def search_news(query: str) -> NewsSearchResult: ...
def weather() -> WeatherInformation: ...
def autocomplete(query: str) -> List[str]: ...
```

</details>