import os
from datetime import datetime

import arabic_reshaper
import feedparser
import requests
from bidi.algorithm import get_display
from dotenv import load_dotenv
from rich.console import Group
from rich.panel import Panel
from rich.text import Text

from ui import console, section, error, info

load_dotenv()

NEWS_API_URL = "https://newsapi.org/v2/everything"


def format_arabic(text):
    return get_display(arabic_reshaper.reshape(text))


def format_date(value):
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%d %b %Y, %H:%M")
    except (ValueError, AttributeError):
        return "Date unavailable"


def print_article(number, title, link, source=None, published=None, color="cyan"):
    lines = [Text(title, style="bold white")]

    meta = Text()
    if source:
        meta.append(source, style=f"bold {color}")
    if source and published:
        meta.append("  •  ", style="dim")
    if published:
        meta.append(published, style="dim")
    if meta.plain:
        lines.append(meta)

    lines.append(Text(link, style="blue underline", overflow="fold"))

    console.print(
        Panel(
            Group(*lines),
            title=f"[bold {color}]{number}[/]",
            title_align="left",
            border_style=color,
            padding=(0, 2),
        )
    )


def show_newsapi(query, heading, color):
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        error("News API key not found. Add NEWS_API_KEY to your .env file.")
        return

    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 5,
        "apiKey": api_key,
    }

    try:
        with console.status(f"[{color}]Loading {heading.lower()}...[/]", spinner="dots"):
            response = requests.get(NEWS_API_URL, params=params, timeout=10)
            response.raise_for_status()
            articles = response.json().get("articles", [])
    except requests.exceptions.RequestException as err:
        error(f"The news request failed: {err}")
        return

    if not articles:
        info(f"No {heading.lower()} available right now.")
        return

    section(heading, color)
    for number, article in enumerate(articles, start=1):
        print_article(
            number,
            article.get("title") or "No title",
            article.get("url") or "No link",
            source=article.get("source", {}).get("name", "Unknown"),
            published=format_date(article.get("publishedAt")),
            color=color,
        )
def show_top_news():
    return show_newsapi(
        "world OR international",
        "WORLD NEWS",
        "cyan",
    )


def show_sports_news():
    return show_newsapi(
        "sports OR football OR soccer",
        "SPORTS NEWS",
        "green",
    )

def show_technology_news():
    return show_newsapi(
        "technology OR artificial intelligence OR programming",
        "TECHNOLOGY NEWS",
        "magenta",
    )


def show_saudi_news():
    url = "https://www.alwatan.com.sa/rssFeed/1"

    try:
        with console.status("[yellow]Loading Saudi news...[/]", spinner="dots"):
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            news = feedparser.parse(response.content)
    except requests.exceptions.RequestException as err:
        error(f"Connection error: {err}")
        return

    if not news.entries:
        info("No news available.")
        return

    section("AL WATAN - SAUDI NEWS", "yellow")
    for number, article in enumerate(news.entries[:5], start=1):
        print_article(
            number,
            format_arabic(article.get("title", "No title")),
            article.get("link", "No link"),
            color="yellow",
        )