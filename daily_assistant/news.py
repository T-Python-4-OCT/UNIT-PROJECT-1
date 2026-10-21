import feedparser
import os
import requests
import arabic_reshaper
from dotenv import load_dotenv
from bidi.algorithm import get_display


load_dotenv()

def format_arabic(text):
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)



def show_top_news():
    url = "https://newsapi.org/v2/everything"

    api_key = os.getenv("NEWS_API_KEY")

    if not api_key:
        print("News API key not found.")
        return

    params = {
        "q": "world OR international",
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 5,
        "apiKey": api_key
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        articles = data.get("articles", [])

        if not articles:
            print("No world news available right now.")
            return

        print("\n" + "=" * 50)
        print("             WORLD NEWS")
        print("=" * 50)

        for number, article in enumerate(articles, start=1):
            title = article.get("title") or "No title"
            link = article.get("url") or "No link"
            published = article.get("publishedAt") or "Date unavailable"
            source = article.get("source", {}).get("name", "Unknown")

            print(f"\n{number}. {title}")
            print(f"Source: {source}")
            print(f"Published: {published}")
            print(f"Link: {link}")
            print("-" * 50)

    except requests.exceptions.RequestException as error:
        print(f"The news request failed: {error}")




def show_saudi_news():
    url = "https://www.alwatan.com.sa/rssFeed/1"

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        news = feedparser.parse(response.content)

        if not news.entries:
            print("No news available.")
            return

        print("\n" + "=" * 50)
        print("       AL WATAN - SAUDI NEWS")
        print("=" * 50)

        for number, article in enumerate(news.entries[:5], start=1):
            title = article.get("title", "No title")
            link = article.get("link", "No link")

            print(f"\n{number}. {format_arabic(title)}")
            print(f"Link: {link}")
            print("-" * 50)

    except requests.exceptions.RequestException as error:
        print(f"Connection error: {error}")



def show_sports_news():
    pass                    


def show_technology_news():
    pass

