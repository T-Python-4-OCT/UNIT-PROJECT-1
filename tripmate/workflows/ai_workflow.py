"""Interactive Gemini travel recommendation workflow."""

from tripmate.services.ai_helper import (
    display_ai_recommendations,
    display_selected_recommendation,
    get_travel_recommendations,
    select_ai_destination
)

from tripmate.core.colors import (
    ai,
    error,
    info,
    warning
)

from tripmate.workflows.location_workflow import (
    get_confirmed_location
)

from tripmate.services.storage import (
    get_next_trip_id,
    save_trips
)

from tripmate.models.trip import (
    create_trip
)

from tripmate.core.ui import (
    choose_from
)

from tripmate.core.validation import (
    calculate_end_date,
    get_date,
    get_positive_float,
    get_positive_int,
    get_yes_no
)

from tripmate.services.weather import (
    find_location
)


def ai_recommendation_workflow(
    trips: list
):

    ai(
        "\n================================"
    )

    ai(
        "        AI TRAVEL PLANNER"
    )

    ai(
        "================================"
    )

    ai(
        "Gemini will use your answers "
        "to recommend destinations."
    )


    ai(
        "\nSTEP 1 - DEPARTURE LOCATION"
    )


    print(
        "Where are you traveling from?"
    )


    departure = (
        get_confirmed_location(
            "Departure Location",
            ai_mode=True
        )
    )


    if departure is None:

        return


    ai(
        "\nSTEP 2 - BUDGET"
    )


    budget = get_positive_float(
        "Enter your total budget (SAR): "
    )


    ai(
        "\nSTEP 3 - TRIP DURATION"
    )


    days = get_positive_int(
        "How many days do you "
        "want to travel? "
    )


    ai(
        "\nSTEP 4 - START DATE"
    )


    start_date = get_date(
        "Enter start date "
        "(YYYY-MM-DD): "
    )


    end_date = calculate_end_date(
        start_date,
        days
    )


    info(
        f"End date calculated "
        f"automatically: {end_date}"
    )


    weather_preference = (
        choose_from(
            "STEP 5 - WEATHER PREFERENCE",
            {
                1: "Cold",
                2: "Mild",
                3: "Warm",
                4: "No preference"
            },
            "Choose weather: "
        )
    )


    activity_preference = (
        choose_from(
            "STEP 6 - ACTIVITIES",
            {
                1: "Nature",
                2: "Shopping",
                3: "Culture and History",
                4: "Relaxation",
                5: "Adventure"
            },
            "Choose activity type: "
        )
    )


    travel_style = (
        choose_from(
            "STEP 7 - TRAVEL STYLE",
            {
                1: "Budget",
                2: "Comfortable",
                3: "Luxury"
            },
            "Choose travel style: "
        )
    )


    ai(
        "\nGemini is analyzing "
        "your travel preferences..."
    )


    ai(
        "Generating AI recommendations..."
    )


    info(
        "Budget fit is estimated "
        "and does not use live "
        "flight prices."
    )


    recommendations = (
        get_travel_recommendations(
            budget,
            days,
            start_date,
            end_date,
            departure[
                "city"
            ],
            departure[
                "country"
            ],
            weather_preference,
            activity_preference,
            travel_style
        )
    )


    if not recommendations:

        return


    display_ai_recommendations(
        recommendations
    )


    create_from_ai = get_yes_no(
        "\nWould you like to create "
        "a trip from one of these "
        "AI recommendations? (y/n): "
    )


    if not create_from_ai:

        return


    selected = (
        select_ai_destination(
            recommendations
        )
    )


    if selected is None:

        warning(
            "Trip creation cancelled."
        )

        return


    display_selected_recommendation(
        selected
    )


    selected_city = selected.get(
        "city"
    )

    selected_country = selected.get(
        "country"
    )


    if (
        not selected_city
        or
        not selected_country
    ):

        error(
            "Invalid destination information."
        )

        return


    ai(
        "\nAI recommendation selected."
    )


    info(
        "Validating destination "
        "with location service..."
    )


    location = find_location(
        selected_city,
        selected_country
    )


    if location is None:

        error(
            "The AI recommendation "
            "could not be validated "
            "as a real location."
        )

        return


    city = location.get(
        "name",
        selected_city
    )


    country = location.get(
        "country",
        selected_country
    )


    print(
        "\nValidated Destination:"
    )


    print(
        f"{city}, {country}"
    )


    trip_id = get_next_trip_id(
        trips
    )


    create_trip(
        trips,
        trip_id,
        country,
        city,
        start_date,
        end_date,
        budget
    )


    save_trips(
        trips
    )


    ai(
        "\nAI recommendation completed."
    )


    info(
        "Trip added to My Trips."
    )
    