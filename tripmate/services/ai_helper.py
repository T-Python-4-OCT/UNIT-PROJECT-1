import json
import re

from google import genai

from rich.markup import escape
from rich.panel import Panel
from rich.table import Table

from tripmate.core.colors import (
    console,
    error,
    warning
)

from tripmate.core.config import (
    GEMINI_API_KEY,
    MODEL_NAME
)

from tripmate.core.validation import (
    get_menu_choice
)


_client = None

_missing_key_reported = False


def get_ai_client():

    global _client, _missing_key_reported


    if _client is not None:

        return _client


    if not GEMINI_API_KEY:

        if not _missing_key_reported:

            warning(
                "Gemini API key was not found. "
                "Add GEMINI_API_KEY to your "
                ".env file to enable AI features."
            )


            _missing_key_reported = True


        return None


    _client = genai.Client(
        api_key=GEMINI_API_KEY
    )


    return _client


def clean_json_response(
    text: str
) -> str:

    text = text.strip()


    match = re.search(
        r"```(?:json)?\s*(.*?)```",
        text,
        re.DOTALL
    )


    if match:

        return match.group(
            1
        ).strip()


    return text


def _clean_input(
    value
) -> str:

    return " ".join(
        str(
            value
        ).split()
    )[:100]


def _ask_gemini_json(
    prompt: str,
    report=error
):

    client = get_ai_client()


    if client is None:

        return None


    try:

        response = (
            client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config={
                    "response_mime_type":
                    "application/json"
                }
            )
        )


    except Exception:

        report(
            "Could not reach Gemini "
            "right now. Check your "
            "internet connection and "
            "try again."
        )

        return None


    if not response.text:

        report(
            "Gemini returned an "
            "empty response."
        )

        return None


    try:

        return json.loads(
            clean_json_response(
                response.text
            )
        )


    except json.JSONDecodeError:

        report(
            "Gemini returned an "
            "invalid response format."
        )

        return None


def correct_location_name(
    city: str,
    country: str
) -> dict:

    original = {
        "city": city,
        "country": country
    }


    prompt = f"""
Correct the spelling and formatting of this travel destination.

City: {_clean_input(city)}
Country: {_clean_input(country)}

Return ONLY valid JSON in this format:

{{
    "city": "Dammam",
    "country": "Saudi Arabia"
}}

Rules:
- Correct spelling mistakes.
- Use common official English place names.
- Do not change the intended location.
- Do not explain anything.
"""


    result = _ask_gemini_json(
        prompt,
        report=warning
    )


    if not isinstance(
        result,
        dict
    ):

        return original


    corrected_city = result.get(
        "city"
    )

    corrected_country = result.get(
        "country"
    )


    if (
        not isinstance(
            corrected_city,
            str
        )
        or
        not corrected_city.strip()
    ):

        corrected_city = city


    if (
        not isinstance(
            corrected_country,
            str
        )
        or
        not corrected_country.strip()
    ):

        corrected_country = country


    return {
        "city": corrected_city.strip(),
        "country": corrected_country.strip()
    }


def _valid_recommendation(
    item
) -> bool:

    if not isinstance(
        item,
        dict
    ):

        return False


    city = item.get(
        "city"
    )

    country = item.get(
        "country"
    )

    activities = item.get(
        "activities",
        []
    )


    return (
        isinstance(
            city,
            str
        )
        and
        bool(
            city.strip()
        )
        and
        isinstance(
            country,
            str
        )
        and
        bool(
            country.strip()
        )
        and
        isinstance(
            activities,
            list
        )
    )


def get_travel_recommendations(
    budget: float,
    days: int,
    start_date: str,
    end_date: str,
    departure_city: str,
    departure_country: str,
    weather_preference: str,
    activity_preference: str,
    travel_style: str
) -> list:

    prompt = f"""
You are a travel recommendation assistant
inside a Python CLI application called TripMate.

Traveler information:

Departure location:
{_clean_input(departure_city)}, {_clean_input(departure_country)}

Total trip budget:
{budget} SAR

Trip duration:
{days} days

Travel dates:
{start_date} to {end_date}

Preferred weather:
{_clean_input(weather_preference)}

Preferred activities:
{_clean_input(activity_preference)}

Travel style:
{_clean_input(travel_style)}

Recommend exactly 3 realistic international travel destinations.

Important:
- Consider the departure location, season, duration and total budget.
- Treat budget suitability as an estimate based on general travel costs.
- Do NOT claim to have live airfare, hotel prices, or booking availability.
- Avoid destinations that are clearly unrealistic for the budget.

Return ONLY valid JSON using this structure:

[
    {{
        "city": "City Name",
        "country": "Country Name",
        "reason": "Short reason",
        "budget_suitability": "Short estimated budget explanation",
        "activities": [
            "Activity 1",
            "Activity 2",
            "Activity 3"
        ]
    }}
]
"""


    recommendations = (
        _ask_gemini_json(
            prompt
        )
    )


    if recommendations is None:

        return []


    if not isinstance(
        recommendations,
        list
    ):

        error(
            "Invalid recommendation format."
        )

        return []


    valid = [
        item
        for item in recommendations
        if _valid_recommendation(
            item
        )
    ][:3]


    if not valid:

        warning(
            "No valid destinations "
            "were recommended."
        )

        return []


    return valid


def display_ai_recommendations(
    recommendations: list
):

    if not recommendations:

        return


    table = Table(
        title="AI Travel Recommendations",
        header_style="bold blue"
    )


    table.add_column(
        "#",
        justify="center",
        width=3
    )

    table.add_column(
        "Destination",
        max_width=25
    )

    table.add_column(
        "Why It Fits",
        max_width=50
    )


    for index, recommendation in enumerate(
        recommendations,
        start=1
    ):

        city = recommendation.get(
            "city",
            "Unknown"
        )

        country = recommendation.get(
            "country",
            "Unknown"
        )

        reason = recommendation.get(
            "reason",
            "No reason provided."
        )


        table.add_row(
            str(
                index
            ),
            escape(
                f"{city}, {country}"
            ),
            escape(
                str(
                    reason
                )
            )
        )


    console.print()


    console.print(
        table
    )


    console.print(
        "[dim]"
        "Budget suitability is an AI estimate, "
        "not a live flight or hotel quote."
        "[/dim]"
    )


def display_selected_recommendation(
    recommendation: dict
):

    city = recommendation.get(
        "city",
        "Unknown"
    )

    country = recommendation.get(
        "country",
        "Unknown"
    )

    reason = recommendation.get(
        "reason",
        "Not available."
    )

    budget = recommendation.get(
        "budget_suitability",
        "Not available."
    )

    activities = recommendation.get(
        "activities",
        []
    )


    activities_text = "\n".join(
        f"• {escape(str(activity))}"
        for activity in activities
    )


    if not activities_text:

        activities_text = (
            "No activities provided."
        )


    content = (
        f"[bold]Destination:[/bold] "
        f"{escape(f'{city}, {country}')}\n\n"

        f"[bold]Why it fits:[/bold]\n"
        f"{escape(str(reason))}\n\n"

        f"[bold]Estimated budget fit:[/bold]\n"
        f"{escape(str(budget))}\n\n"

        f"[bold]Suggested Activities:[/bold]\n"
        f"{activities_text}"
    )


    console.print()


    console.print(
        Panel(
            content,
            title="Selected AI Recommendation",
            border_style="blue"
        )
    )


def select_ai_destination(
    recommendations: list
):

    if not recommendations:

        return None


    choice = get_menu_choice(
        "\nChoose a destination number "
        "or enter 0 to cancel: ",
        0,
        len(
            recommendations
        )
    )


    if choice == 0:

        return None


    return recommendations[
        choice - 1
    ]