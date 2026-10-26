import os
import re

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

MODEL = "openai/gpt-oss-120b"
MAX_TOKENS = 1500

EN_HEADING = re.compile(r"english\s+summary", re.IGNORECASE)
AR_HEADING = re.compile(
    r"arabic\s+summary|الملخص\s+باللغة\s+العربية|الملخص\s+العربي",
    re.IGNORECASE,
)


def _clean_heading(line):
    return line.strip().strip("*#:- ").strip()


def _headlines(articles):
    """عناوين الأخبار الأصلية، تُستخدم كبديل عند فشل التلخيص."""
    return "\n".join(
        f"- {article.get('title', '').strip()}"
        for article in articles
        if article.get("title")
    )


def _parse_summary(text):
    """استخراج القسمين الإنجليزي والعربي مع تحمل اختلاف صيغة العناوين."""
    english, arabic = [], []
    current = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        cleaned = _clean_heading(line)

        if EN_HEADING.search(cleaned) and len(cleaned) < 40:
            current = "english"
            continue
        if AR_HEADING.search(cleaned) and len(cleaned) < 60:
            current = "arabic"
            continue

        if current == "english":
            english.append(line)
        elif current == "arabic":
            arabic.append(line)

    return "\n".join(english).strip(), "\n".join(arabic).strip()


def summarize_news(news_sections):
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        print("GROQ_API_KEY was not found.")
        return None

    if not news_sections:
        print("No news sections are available.")
        return None

    client = Groq(api_key=api_key)
    summaries = {}

    for section_name, articles in news_sections.items():
        articles_text = []

        for article in articles:
            title = article.get("title", "")
            description = article.get("description", "")

            if title or description:
                articles_text.append(
                    f"Title: {title}\nDescription: {description}"
                )

        if not articles_text:
            continue

        news_block = "\n\n".join(articles_text)
        headlines = _headlines(articles)

        prompt = f"""
Summarize the following {section_name} news.

Return exactly these sections, with these exact headings:

ENGLISH SUMMARY:
- Write 2 to 3 short bullet points in English.

ARABIC SUMMARY:
- Write 2 to 3 short bullet points in Arabic.

Summarize only the news provided. Do not invent facts.
Do not add any text before or after the two sections.

News:
{news_block}
"""

        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You summarize news accurately. "
                            "Always return both English and Arabic sections "
                            "using the exact headings requested."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=MAX_TOKENS,
                temperature=0.2,
            )

            choice = response.choices[0]

            if choice.finish_reason == "length":
                print(f"Warning: summary for {section_name} was cut off.")

            text = choice.message.content or ""
            english, arabic = _parse_summary(text)

            if not english and not arabic:
                print(f"Warning: could not parse summary for {section_name}.")
                print(f"Raw response: {text[:300]}")

            summaries[section_name] = {
                "english": english or headlines,
                "arabic": arabic,
            }

        except Exception as err:
            print(f"Failed to summarize {section_name}: {err}")
            summaries[section_name] = {
                "english": headlines,
                "arabic": "",
            }

    return summaries or None