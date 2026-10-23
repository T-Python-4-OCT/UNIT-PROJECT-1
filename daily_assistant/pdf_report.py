
from datetime import datetime
from html import escape                  


from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
)
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
)


class PDFReport:

    def generate_report(self, news_sections, weather_data=None):
        filename = (
            "daily_report_"
            + datetime.now().strftime("%Y%m%d_%H%M%S")
            + ".pdf"
        )

        document = SimpleDocTemplate(
            filename,
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
            alignment=TA_CENTER,
            textColor=colors.darkblue,
            fontSize=20,
            spaceAfter=15,
        )

        story = []

        story.append(
            Paragraph("DAILY NEWS &amp; WEATHER REPORT", title_style)
        )

        story.append(
            Paragraph(
                "Generated: "
                + datetime.now().strftime("%d %B %Y, %H:%M"),
                styles["Normal"],
            )
        )

        story.append(Spacer(1, 20))

        story.append(
            Paragraph("NEWS SUMMARY", styles["Heading1"])
        )

        if not news_sections:
            story.append(
                Paragraph("No news was collected.", styles["BodyText"])
            )

        for category, articles in news_sections.items():
            story.append(
                Paragraph(escape(category), styles["Heading2"])
            )

            for number, article in enumerate(articles, start=1):
                title = escape(article.get("title") or "No title")
                description = (
                    article.get("description")
                    or article.get("content")
                    or "No summary available for this article."
                )
                description = escape(description)

                source = escape(
                    article.get("source", {}).get("name", "Unknown")
                )

                story.append(
                    Paragraph(
                        f"<b>{number}. {title}</b>",
                        styles["BodyText"],
                    )
                )

                story.append(Spacer(1, 5))

                story.append(
                    Paragraph(
                        f"<b>Source:</b> {source}",
                        styles["BodyText"],
                    )
                )

                story.append(Paragraph(description, styles["BodyText"]))

                link = article.get("url", "")

                if link.startswith(("https://", "http://")):
                    safe_link = escape(link, quote=True)
                    story.append(
                        Paragraph(
                            f'<link href="{safe_link}" '
                            'color="blue">Read full article</link>',
                            styles["BodyText"],
                        )
                    )

                story.append(Spacer(1, 12))

        story.append(Spacer(1, 15))
        story.append(
            Paragraph("WEATHER SUMMARY", styles["Heading1"])
        )

        if weather_data:
            weather_rows = [
                ("City", weather_data.get("city", "Unknown")),
                ("Condition", weather_data.get("condition", "Unknown")),
                ("Temperature", f"{weather_data.get('temperature', 'N/A')} °C"),
                ("Feels like", f"{weather_data.get('feels_like', 'N/A')} °C"),
                ("Humidity", f"{weather_data.get('humidity', 'N/A')}%"),
                ("Wind speed", f"{weather_data.get('wind_speed', 'N/A')} km/h"),
                ("Updated", weather_data.get("time", "Unknown")),
            ]

            for label, value in weather_rows:
                story.append(
                    Paragraph(
                        f"<b>{escape(label)}:</b> {escape(str(value))}",
                        styles["BodyText"],
                    )
                )
                story.append(Spacer(1, 6))

        else:
            story.append(
                Paragraph(
                    "No weather data collected. Select Check Weather "
                    "before generating the report to include it.",
                    styles["BodyText"],
                )
            )

        document.build(story)

        return filename
