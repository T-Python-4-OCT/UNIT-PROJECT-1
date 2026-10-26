
import re
from datetime import datetime
from html import escape
from pathlib import Path

import arabic_reshaper
from bidi.algorithm import get_display

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

from ui import console, error


OUTPUT_DIR = Path(__file__).resolve().parent
FONT_PATH = OUTPUT_DIR / "NotoNaskhArabic-Regular.ttf"

BLUE = colors.HexColor("#1565C0")
BLACK = colors.black

if not FONT_PATH.exists():
    raise FileNotFoundError(
        f"Arabic font not found: {FONT_PATH}"
    )

pdfmetrics.registerFont(
    TTFont("ArabicFont", str(FONT_PATH))
)


class PDFReport:
    def __init__(self):
        styles = getSampleStyleSheet()

        self.title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Title"],
            fontName="ArabicFont",
            fontSize=22,
            leading=30,
            alignment=TA_CENTER,
            textColor=BLACK,
            spaceAfter=10,
        )

        self.heading_style = ParagraphStyle(
            "CategoryHeading",
            parent=styles["Heading1"],
            fontName="ArabicFont",
            fontSize=16,
            leading=22,
            textColor=BLACK,
            spaceBefore=14,
            spaceAfter=8,
        )

        self.article_style = ParagraphStyle(
            "ArticleTitle",
            parent=styles["Heading2"],
            fontName="ArabicFont",
            fontSize=12,
            leading=18,
            textColor=BLACK,
            spaceBefore=8,
            spaceAfter=4,
        )

        self.body_style = ParagraphStyle(
            "ReportBody",
            parent=styles["BodyText"],
            fontName="ArabicFont",
            fontSize=10,
            leading=16,
            textColor=BLACK,
            spaceAfter=5,
        )

        self.arabic_style = ParagraphStyle(
            "ArabicBody",
            parent=self.body_style,
            alignment=2,
        )

    def format_text(self, text):
        text = str(text or "")

        if re.search(r"[\u0600-\u06FF]", text):
            text = arabic_reshaper.reshape(text)
            text = get_display(text)

        return text

    def make_paragraph(self, text, style=None):
        formatted = self.format_text(text)
        safe_text = escape(formatted)

        if style is None:
            style = (
                self.arabic_style
                if re.search(r"[\u0600-\u06FF]", str(text or ""))
                else self.body_style
            )

        return Paragraph(safe_text, style)

    def generate_report(self, news_sections, weather_data=None):
        output_path = (
            OUTPUT_DIR
            / f"daily_report_{datetime.now():%Y%m%d_%H%M%S}.pdf"
        )

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
                story.extend(
                    self._news_section(category, articles)
                )

            if weather_data:
                story.extend(
                    self._weather_section(weather_data)
                )

            doc.build(story)

        except Exception as err:
            error(f"PDF generation failed: {err}")
            return None

        console.print(
            "\n[bold green]PDF saved successfully![/]"
        )
        console.print(f"[dim]Location: {output_path}[/]")

        return str(output_path)

    def _header(self):
        return [
            self.make_paragraph(
                "Daily News & Weather",
                self.title_style,
            ),
            self.make_paragraph(
                "Generated: "
                + datetime.now().strftime("%d %B %Y, %H:%M"),
                self.body_style,
            ),
            Spacer(1, 8),
            HRFlowable(
                width="100%",
                thickness=1,
                color=BLUE,
            ),
        ]

    def _news_section(self, category, articles):
        flow = [
            self.make_paragraph(
                category,
                self.heading_style,
            )
        ]

        if not articles:
            flow.append(
                self.make_paragraph("No articles available.")
            )
            return flow

        for number, article in enumerate(articles, start=1):
            title = article.get("title") or "No title"
            source = (
                (article.get("source") or {}).get("name")
                or "Unknown"
            )
            description = (
                article.get("description")
                or "No description available."
            )

            flow.append(
                self.make_paragraph(
                    f"{number}. {title}",
                    self.article_style,
                )
            )

            flow.append(
                self.make_paragraph(
                    f"Source: {source}"
                )
            )

            flow.append(
                self.make_paragraph(
                    f"Description: {description}"
                )
            )

            link = article.get("url") or ""

            if link.startswith(("https://", "http://")):
                safe_link = escape(link, quote=True)
                flow.append(
                    Paragraph(
                        f'<link href="{safe_link}" color="blue">'
                        "Read full article</link>",
                        self.body_style,
                    )
                )

            flow.append(Spacer(1, 6))

        return flow

    def _weather_section(self, weather):
        flow = [
            self.make_paragraph(
                "Weather Report",
                self.heading_style,
            )
        ]

        weather_fields = [
            ("City", "city", ""),
            ("Condition", "condition", ""),
            ("Temperature", "temperature", " °C"),
            ("Feels like", "feels_like", " °C"),
            ("Humidity", "humidity", "%"),
            ("Wind speed", "wind_speed", " km/h"),
            ("Updated at", "time", ""),
        ]

        for label, key, suffix in weather_fields:
            value = weather.get(key)

            if value is not None:
                flow.append(
                    self.make_paragraph(
                        f"{label}: {value}{suffix}"
                    )
                )

        return flow
