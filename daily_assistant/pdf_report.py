import re
from datetime import datetime
from pathlib import Path
from html import escape

import arabic_reshaper
from bidi.algorithm import get_display

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
)

from ui import console, error


OUTPUT_DIR = Path(__file__).resolve().parent
FONT_PATH = OUTPUT_DIR / "NotoNaskhArabic-Regular.ttf"
ARABIC_RE = re.compile(r"[\u0600-\u06FF]")

# عرض الإطار المتاح داخل A4 بعد الهوامش (تقريبًا)
MAX_LINE_WIDTH = 470
ARABIC_FONT_SIZE = 10

if FONT_PATH.exists():
    if "ArabicFont" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("ArabicFont", str(FONT_PATH)))
else:
    print(f"تحذير: لم يُعثر على الخط العربي في {FONT_PATH}")


class PDFReport:

    def __init__(self):
        self.output_path = OUTPUT_DIR / "daily_news_weather_report.pdf"
        self.has_arabic_font = FONT_PATH.exists()

        styles = getSampleStyleSheet()

        self.title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=26,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#123B5D"),
            spaceAfter=8,
        )

        self.subtitle_style = ParagraphStyle(
            "ReportSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#64748B"),
            spaceAfter=18,
        )

        self.section_style = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=19,
            textColor=colors.HexColor("#087E8B"),
            spaceBefore=12,
            spaceAfter=8,
        )

        self.heading_style = ParagraphStyle(
            "SummaryHeading",
            parent=styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#334155"),
            spaceBefore=5,
            spaceAfter=5,
        )

        self.body_style = ParagraphStyle(
            "SummaryBody",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=14,
            alignment=TA_LEFT,
            spaceAfter=5,
        )

        self.arabic_style = ParagraphStyle(
            "ArabicBody",
            parent=styles["BodyText"],
            fontName="ArabicFont" if self.has_arabic_font else "Helvetica",
            fontSize=ARABIC_FONT_SIZE,
            leading=17,
            alignment=TA_RIGHT,
            spaceAfter=6,
        )

        self.arabic_heading_style = ParagraphStyle(
            "ArabicHeading",
            parent=self.heading_style,
            fontName="ArabicFont" if self.has_arabic_font else "Helvetica-Bold",
            alignment=TA_RIGHT,
        )

    @staticmethod
    def is_arabic(text):
        return bool(ARABIC_RE.search(str(text)))

    @staticmethod
    def shape_arabic(text):
        """تشكيل الحروف وترتيب الاتجاه لسطر واحد."""
        return get_display(arabic_reshaper.reshape(text))

    def wrap_arabic(self, text):
        """تقسيم النص إلى أسطر منطقيًا قبل التشكيل، ثم تشكيل كل سطر."""
        words = text.split()
        lines, current = [], ""

        for word in words:
            candidate = f"{current} {word}".strip()
            width = stringWidth(
                self.shape_arabic(candidate), "ArabicFont", ARABIC_FONT_SIZE
            )
            if width <= MAX_LINE_WIDTH:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word

        if current:
            lines.append(current)

        return [self.shape_arabic(line) for line in lines]

    def format_text(self, text):
        text = str(text)

        if not (self.is_arabic(text) and self.has_arabic_font):
            return text

        shaped_lines = []
        for raw_line in text.splitlines():
            if raw_line.strip():
                shaped_lines.extend(self.wrap_arabic(raw_line))
            else:
                shaped_lines.append("")

        return "\n".join(shaped_lines)

    def make_paragraph(self, text):
        text = str(text)
        safe_text = escape(self.format_text(text)).replace("\n", "<br/>")

        if self.is_arabic(text):
            return Paragraph(safe_text, self.arabic_style)

        return Paragraph(safe_text, self.body_style)

    def _header(self):
        return [
            Paragraph("DAILY NEWS &amp; WEATHER REPORT", self.title_style),
            Paragraph(
                f"Generated on {datetime.now().strftime('%d %B %Y, %I:%M %p')}",
                self.subtitle_style,
            ),
            HRFlowable(
                width="100%",
                thickness=1,
                color=colors.HexColor("#087E8B"),
                spaceAfter=12,
            ),
        ]

    def _summary_section(self, summaries):
        story = [
            Paragraph("NEWS SUMMARIES", self.section_style),
        ]

        if not summaries:
            story.append(self.make_paragraph("No news summaries are available."))
            story.append(self.make_paragraph("لا تتوفر ملخصات للأخبار."))
            return story

        for section_name, summary in summaries.items():
            story.append(Spacer(1, 8))
            story.append(Paragraph(escape(section_name), self.section_style))

            english = summary.get("english", "")
            arabic = summary.get("arabic", "")

            story.append(Paragraph("English Summary", self.heading_style))

            if english:
                for line in english.splitlines():
                    line = line.strip()
                    if line:
                        story.append(self.make_paragraph(line))
            else:
                story.append(self.make_paragraph("Summary unavailable."))

            story.append(Spacer(1, 4))
            story.append(
                Paragraph(
                    self.format_text("الملخص باللغة العربية"),
                    self.arabic_heading_style,
                )
            )

            if arabic:
                for line in arabic.splitlines():
                    line = line.strip()
                    if line:
                        story.append(self.make_paragraph(line))
            else:
                story.append(self.make_paragraph("الملخص العربي غير متاح."))

            story.append(
                HRFlowable(
                    width="100%",
                    thickness=0.5,
                    color=colors.HexColor("#CBD5E1"),
                    spaceBefore=6,
                    spaceAfter=8,
                )
            )

        return story

    def _weather_section(self, weather_data):
        story = [
            Paragraph("WEATHER REPORT", self.section_style),
        ]

        if not weather_data:
            story.append(self.make_paragraph("No weather information was collected."))
            story.append(self.make_paragraph("لم يتم جمع معلومات الطقس."))
            return story

        fields = [
            ("City", "city"),
            ("Condition", "condition"),
            ("Temperature", "temperature"),
            ("Feels Like", "feels_like"),
            ("Humidity", "humidity"),
            ("Wind Speed", "wind_speed"),
            ("Time", "time"),
        ]

        for label, key in fields:
            value = weather_data.get(key)

            if value is not None and value != "":
                story.append(self.make_paragraph(f"{label}: {value}"))

        return story

    def generate_report(
        self,
        news_sections=None,
        weather_data=None,
        ai_summary=None,
    ):
        try:
            story = self._header()
            story.extend(self._summary_section(ai_summary))
            story.extend(self._weather_section(weather_data))

            document = SimpleDocTemplate(
                str(self.output_path),
                pagesize=A4,
                rightMargin=2 * cm,
                leftMargin=2 * cm,
                topMargin=1.5 * cm,
                bottomMargin=1.5 * cm,
                title="Daily News and Weather Report",
            )

            document.build(story)

            console.print(
                f"[green]PDF saved successfully: {self.output_path}[/]"
            )

            return str(self.output_path)

        except Exception as err:
            error(f"Could not create PDF report: {err}")
            return None