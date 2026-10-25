from datetime import datetime
from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer

from ui import console, error

BLUE = colors.HexColor("#1565C0")
OUTPUT_DIR = Path(__file__).resolve().parent

WEATHER_FIELDS = [
    ("City", "city", ""),
    ("Condition", "condition", ""),
    ("Temperature", "temperature", " °C"),
    ("Feels like", "feels_like", " °C"),
    ("Humidity", "humidity", "%"),
    ("Wind speed", "wind_speed", " km/h"),
    ("Updated at", "time", ""),
]


class PDFReport:

    def __init__(self):
        styles = getSampleStyleSheet()

        self.title_style = ParagraphStyle(
            "ReportTitle", parent=styles["Title"], fontSize=22, leading=28,
            alignment=TA_CENTER, textColor=BLUE, spaceAfter=10,
        )
        self.heading_style = ParagraphStyle(
            "CategoryHeading", parent=styles["Heading1"], textColor=BLUE,
            spaceBefore=14, spaceAfter=8,
        )
        self.article_style = ParagraphStyle(
            "ArticleTitle", parent=styles["Heading2"], fontSize=11, leading=15,
            spaceBefore=8, spaceAfter=4,
        )
        self.body_style = ParagraphStyle(
            "ReportBody", parent=styles["BodyText"], fontSize=9, leading=13,
            spaceAfter=5,
        )

    def generate_report(self, news_sections, weather_data=None):
        output_path = OUTPUT_DIR / f"daily_report_{datetime.now():%Y%m%d_%H%M%S}.pdf"

        try:
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=A4,
                leftMargin=2 * cm,
                rightMargin=2 * cm,
                topMargin=2 * cm,
                bottomMargin=2 * cm,
            )

            story = self._header()

            for category, articles in (news_sections or {}).items():
                story += self._news_section(category, articles)

            if weather_data:
                story += self._weather_section(weather_data)

            doc.build(story)

        except Exception as err:
            error(f"PDF generation failed: {err}")
            return None

        console.print("\n[bold green]PDF saved successfully![/]")
        console.print(f"[dim]Location: {output_path}[/]")
        return str(output_path)

    def _header(self):
        return [
            Paragraph("Daily News &amp; Weather", self.title_style),
            Paragraph("Generated: " + datetime.now().strftime("%d %B %Y, %H:%M"), self.body_style),
            Spacer(1, 8),
            HRFlowable(width="100%", thickness=1, color=BLUE),
        ]

    def _news_section(self, category, articles):
        flow = [Paragraph(escape(str(category)), self.heading_style)]

        if not articles:
            flow.append(Paragraph("No articles available.", self.body_style))
            return flow

        for number, article in enumerate(articles, start=1):
            title = escape(article.get("title") or "No title")
            source = escape((article.get("source") or {}).get("name", "Unknown"))
            description = escape(article.get("description") or "No description available.")

            flow.append(Paragraph(f"{number}. {title}", self.article_style))
            flow.append(Paragraph(f"<b>Source:</b> {source}", self.body_style))
            flow.append(Paragraph(f"<b>Description:</b> {description}", self.body_style))

            link = article.get("url") or ""
            if link.startswith(("https://", "http://")):
                flow.append(Paragraph(
                    f'<link href="{escape(link, quote=True)}" color="blue">Read full article</link>',
                    self.body_style,
                ))

            flow.append(Spacer(1, 6))

        return flow

    def _weather_section(self, weather):
        flow = [Paragraph("Weather Report", self.heading_style)]

        for label, key, suffix in WEATHER_FIELDS:
            value = weather.get(key)
            if value is not None:
                flow.append(Paragraph(
                    f"<b>{escape(label)}:</b> {escape(str(value))}{suffix}",
                    self.body_style,
                ))

        return flow