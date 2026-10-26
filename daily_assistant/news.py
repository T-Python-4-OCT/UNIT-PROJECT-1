import os
from datetime import datetime
from email.utils import parsedate_to_datetime

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
SAUDI_RSS_URL = "https://www.alwatan.com.sa/rssFeed/1"


class NewsManager:

    @staticmethod
    def format_arabic(text):
        """Reshape Arabic text so it displays correctly in the terminal."""
        return get_display(arabic_reshaper.reshape(text))

    @staticmethod
    def format_date(value):
        """Convert ISO or RFC 822 dates to a readable string."""
        if not value:
            return None
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            try:
                dt = parsedate_to_datetime(value)
            except (TypeError, ValueError):
                return None
        return dt.strftime("%d %b %Y, %H:%M")

    @staticmethod
    def print_article(number, title, link, source, published, color):
        meta = Text(source, style=f"bold {color}")
        if published:
            meta.append("  •  ", style="dim")
            meta.append(published, style="dim")

        body = Group(
            Text(title, style="bold white"),
            meta,
            Text(link, style="blue underline", overflow="fold"),
        )
        console.print(
            Panel(
                body,
                title=f"[bold {color}]{number}[/]",
                title_align="left",
                border_style=color,
                padding=(0, 2),
            )
        )

    def show_articles(self, articles, heading, color, arabic=False):
        """Print a list of articles. Both NewsAPI and RSS go through here."""
        if not articles:
            info(f"No {heading.lower()} available right now.")
            return []

        section(heading, color)

        for number, article in enumerate(articles, start=1):
            title = article.get("title") or "No title"
            source = (article.get("source") or {}).get("name", "Unknown")

            self.print_article(
                number,
                self.format_arabic(title) if arabic else title,
                article.get("url") or "No link",
                source=source,
                published=self.format_date(article.get("publishedAt")),
                color=color,
            )

        return articles

    def newsapi(self, query, heading, color):
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
            with console.status(f"[{color}]Loading {heading.lower()}...[/]", spinner="dots"):
                response = requests.get(NEWS_API_URL, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
        except (requests.exceptions.RequestException, ValueError) as err:
            error(f"The news request failed: {err}")
            return []

        if data.get("status") != "ok":
            error(data.get("message", "News service failed."))
            return []

        return self.show_articles(data.get("articles", []), heading, color)

    def saudi_news(self):
        try:
            with console.status("[yellow]Loading Saudi news...[/]", spinner="dots"):
                response = requests.get(SAUDI_RSS_URL, timeout=15)
                response.raise_for_status()
                feed = feedparser.parse(response.content)
        except requests.exceptions.RequestException as err:
            error(f"Connection error: {err}")
            return []

        articles = [
            {
                "title": item.get("title", "No title"),
                "description": item.get("summary", ""),
                "url": item.get("link", ""),
                "source": {"name": "Al Watan"},
                "publishedAt": item.get("published", ""),
            }
            for item in feed.entries[:5]
        ]

        return self.show_articles(
            articles, "AL WATAN - SAUDI NEWS", "yellow", arabic=True
        )

    def top_news(self):
        return self.newsapi("world OR international", "WORLD NEWS", "cyan")

    def sports_news(self):
        return self.newsapi("sports OR football OR soccer", "SPORTS NEWS", "green")

    def technology_news(self):
        return self.newsapi(
            "technology OR artificial intelligence OR programming",
            "TECHNOLOGY NEWS",
            "magenta",
        )

   
    
    def search_news(self):
        while True:
            keyword = console.input(
                "[bold cyan]Enter a search phrase (or type 'back' to return):[/] "
            ).strip()

            if keyword.lower() == "back":
                info("Returning to the main menu.")
                return []

            if not keyword:
                error("Input cannot be empty! Please enter a search phrase.")
                continue

            if len(keyword.split()) < 2:
                error("Please enter at least 2 words to search for news.")
                continue

            articles = self.newsapi(
                keyword,
                f"SEARCH RESULTS: {keyword.upper()}",
                "cyan"
            )

            return articles
