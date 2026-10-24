
from datetime import datetime
from pathlib import Path
from html import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
)


class PDFReport:
    def generate_report(self, news_sections, weather_data=None):
        filename = (
            f"daily_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        output_path = Path(__file__).resolve().parent / filename

        try:
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=A4,
                rightMargin=2 * cm,
                leftMargin=2 * cm,
                topMargin=2 * cm,
                bottomMargin=2 * cm,
            )

            styles = getSampleStyleSheet()

            title_style = ParagraphStyle(
                "ReportTitle",
                parent=styles["Title"],
                fontSize=22,
                leading=28,
                alignment=TA_CENTER,
                textColor=colors.HexColor("#1565C0"),
                spaceAfter=10,
            )

            heading_style = ParagraphStyle(
                "CategoryHeading",
                parent=styles["Heading1"],
                textColor=colors.HexColor("#1565C0"),
                spaceBefore=14,
                spaceAfter=8,
            )

            article_style = ParagraphStyle(
                "ArticleTitle",
                parent=styles["Heading2"],
                fontSize=11,
                leading=15,
                spaceBefore=8,
                spaceAfter=4,
            )

            body_style = ParagraphStyle(
                "ReportBody",
                parent=styles["BodyText"],
                fontSize=9,
                leading=13,
                spaceAfter=5,
            )

            story = [
                Paragraph("Daily News &amp; Weather", title_style),
                Paragraph(
                    "Generated: "
                    + datetime.now().strftime("%d %B %Y, %H:%M"),
                    body_style,
                ),
                Spacer(1, 8),
                HRFlowable(
                    width="100%",
                    thickness=1,
                    color=colors.HexColor("#1565C0"),
                ),
            ]

            for category, articles in (news_sections or {}).items():
                story.append(
                    Paragraph(escape(str(category)), heading_style)
                )

                if not articles:
                    story.append(
                        Paragraph("No articles available.", body_style)
                    )
                    continue

                for number, article in enumerate(articles, start=1):
                    title = article.get("title") or "No title"
                    source = article.get("source") or {}

                    if isinstance(source, dict):
                        source_name = source.get("name", "Unknown")
                    else:
                        source_name = str(source)

                    description = (
                        article.get("description")
                        or "No description available."
                    )

                    story.append(
                        Paragraph(
                            f"{number}. {escape(str(title))}",
                            article_style,
                        )
                    )
                    story.append(
                        Paragraph(
                            f"<b>Source:</b> {escape(str(source_name))}",
                            body_style,
                        )
                    )
                    story.append(
                        Paragraph(
                            f"<b>Description:</b> "
                            f"{escape(str(description))}",
                            body_style,
                        )
                    )

                    link = article.get("url") or ""

                    if link.startswith(("https://", "http://")):
                        story.append(
                            Paragraph(
                                f'<link href="{escape(link, quote=True)}" '
                                'color="blue">Read full article</link>',
                                body_style,
                            )
                        )

                    story.append(Spacer(1, 6))

            if weather_data:
                story.append(
                    Paragraph("Weather Report", heading_style)
                )

                fields = [
                    ("City", "city", ""),
                    ("Condition", "condition", ""),
                    ("Temperature", "temperature", " °C"),
                    ("Feels like", "feels_like", " °C"),
                    ("Humidity", "humidity", "%"),
                    ("Wind speed", "wind_speed", " km/h"),
                    ("Updated at", "time", ""),
                ]

                for label, key, suffix in fields:
                    value = weather_data.get(key)

                    if value is not None:
                        story.append(
                            Paragraph(
                                f"<b>{escape(label)}:</b> "
                                f"{escape(str(value))}{suffix}",
                                body_style,
                            )
                        )

            doc.build(story)

            print(f"\nPDF saved successfully:\n{output_path}")
            return str(output_path)

        except Exception as err:
            print(f"\nPDF generation failed: {err}")
            return None
