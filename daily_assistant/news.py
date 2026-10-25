
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


class NewsManager:

    @staticmethod
    def format_arabic(text):
        return get_display(arabic_reshaper.reshape(text))

    @staticmethod
    def format_date(value):
        try:
            return datetime.fromisoformat(
                value.replace("Z", "+00:00")
            ).strftime("%d %b %Y, %H:%M")
        except (ValueError, AttributeError):
            return "Date unavailable"

    @staticmethod
    def print_article(
        number,
        title,
        link,
        source=None,
        published=None,
        color="cyan",
    ):
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

        lines.append(
            Text(link, style="blue underline", overflow="fold")
        )

        console.print(
            Panel(
                Group(*lines),
                title=f"[bold {color}]{number}[/]",
                title_align="left",
                border_style=color,
                padding=(0, 2),
            )
        )

    def show_newsapi(self, query, heading, color):
        api_key = os.getenv("NEWS_API_KEY")

        if not api_key:
            error("News API key not found. Check your .env file.")
            return []

        params = {
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 5,
            "apiKey": api_key,
        }

        try:
            with console.status(
                f"[{color}]Loading {heading.lower()}...[/]",
                spinner="dots",
            ):
                response = requests.get(
                    NEWS_API_URL,
                    params=params,
                    timeout=10,
                )
                response.raise_for_status()
                data = response.json()

            if data.get("status") != "ok":
                error(data.get("message", "News service failed."))
                return []

            articles = data.get("articles", [])

        except (requests.exceptions.RequestException, ValueError) as err:
            error(f"The news request failed: {err}")
            return []

        if not articles:
            info(f"No {heading.lower()} available right now.")
            return []

        section(heading, color)

        for number, article in enumerate(articles, start=1):
            source = article.get("source") or {}

            if isinstance(source, dict):
                source_name = source.get("name", "Unknown")
            else:
                source_name = str(source)

            self.print_article(
                number,
                article.get("title") or "No title",
                article.get("url") or "No link",
                source=source_name,
                published=self.format_date(
                    article.get("publishedAt")
                ),
                color=color,
            )

        return articles

    def show_top_news(self):
        return self.show_newsapi(
            "world OR international",
            "WORLD NEWS",
            "cyan",
        )

    def show_saudi_news(self):
        url = "https://www.alwatan.com.sa/rssFeed/1"

        try:
            with console.status(
                "[yellow]Loading Saudi news...[/]",
                spinner="dots",
            ):
                response = requests.get(url, timeout=15)
                response.raise_for_status()
                feed = feedparser.parse(response.content)

        except requests.exceptions.RequestException as err:
            error(f"Connection error: {err}")
            return []

        articles = []

        for item in feed.entries[:5]:
            raw_title = item.get("title", "No title")

            articles.append({
                "title": self.format_arabic(raw_title),
                "description": item.get("summary", ""),
                "url": item.get("link", ""),
                "source": {"name": "Al Watan"},
                "publishedAt": item.get("published", ""),
            })

        if not articles:
            info("No Saudi news available.")
            return []

        section("AL WATAN - SAUDI NEWS", "yellow")

        for number, article in enumerate(articles, start=1):
            self.print_article(
                number,
                article["title"],
                article["url"] or "No link",
                source="Al Watan",
                published=article["publishedAt"] or None,
                color="yellow",
            )

        return articles

    def show_sports_news(self):
        return self.show_newsapi(
            "sports OR football OR soccer",
            "SPORTS NEWS",
            "green",
        )

    def show_technology_news(self):
        return self.show_newsapi(
            "technology OR artificial intelligence OR programming",
            "TECHNOLOGY NEWS",
            "magenta",
        )

    def search_news(self):
        keyword = console.input(
            "[bold cyan]Enter a keyword to search for:[/] "
        ).strip()

        if not keyword:
            info("Please enter a keyword.")
            return []

        return self.show_newsapi(
            keyword,
            f"SEARCH RESULTS: {keyword.upper()}",
            "cyan",
        )
