"""Location input, AI correction and validation workflow."""

from tripmate.services.ai_helper import (
    correct_location_name
)

from tripmate.core.colors import (
    ai,
    error,
    info,
    warning
)

from tripmate.core.validation import (
    get_text_input,
    get_yes_no
)

from tripmate.services.weather import (
    find_location
)

from tripmate.core.colors import (
    ai,
    console,
    error,
    info,
    warning
)


def get_confirmed_location(
    title: str,
    ai_mode: bool = False
):

    while True:

        if ai_mode:

            ai(
                f"\n--- AI: {title} ---"
            )

        else:

            info(
                f"\n--- {title} ---"
            )


        country = get_text_input(
            "Enter country: "
        )

        city = get_text_input(
            "Enter city: "
        )


        # Try normal location validation first.
        with console.status(
            "[cyan]Validating location...[/cyan]",
            spinner="dots"
        ):

            location = find_location(
                city,
                country,
                silent=True
            )


        # Location is already valid.
        if location is not None:

            location_city = location.get(
                "name",
                city
            )

            location_country = location.get(
                "country",
                country
            )


            print(
                "\nLocation found:"
            )

            print(
                f"{location_city}, "
                f"{location_country}"
            )


            confirmed = get_yes_no(
                "Use this location? (y/n): "
            )


            if confirmed:

                return {
                    "city": location_city,
                    "country": location_country
                }


            warning(
                "Please enter "
                "the location again."
            )

            continue


        # Normal validation failed.
        # Use Gemini quietly as a fallback.
        with console.status(
            "[blue]Checking spelling with AI...[/blue]",
            spinner="dots"
        ):

            corrected = correct_location_name(
                city,
                country
            )


        corrected_city = corrected[
            "city"
        ]

        corrected_country = corrected[
            "country"
        ]


        # Gemini could not suggest anything different.
        if (
            corrected_city.lower()
            == city.lower()
            and
            corrected_country.lower()
            == country.lower()
        ):

            error(
                "Location could not be verified."
            )


            retry = get_yes_no(
                "Try another location? (y/n): "
            )


            if retry:

                continue


            return None


        ai(
            f"\nAI suggestion: "
            f"{corrected_city}, "
            f"{corrected_country}"
        )


        with console.status(
            "[cyan]Validating AI suggestion...[/cyan]",
            spinner="dots"
        ):

            corrected_location = find_location(
                corrected_city,
                corrected_country,
                silent=True
            )


        if corrected_location is None:

            error(
                "The suggested location "
                "could not be verified."
            )


            retry = get_yes_no(
                "Try another location? (y/n): "
            )


            if retry:

                continue


            return None


        location_city = corrected_location.get(
            "name",
            corrected_city
        )

        location_country = corrected_location.get(
            "country",
            corrected_country
        )


        print(
            "\nCorrected location:"
        )

        print(
            f"{location_city}, "
            f"{location_country}"
        )


        confirmed = get_yes_no(
            "Use this corrected "
            "location? (y/n): "
        )


        if confirmed:

            return {
                "city": location_city,
                "country": location_country
            }


        warning(
            "Please enter "
            "the location again."
        )

    while True:

        if ai_mode:

            ai(
                f"\n--- AI: {title} ---"
            )

        else:

            info(
                f"\n--- {title} ---"
            )


        country = get_text_input(
            "Enter country: "
        )

        city = get_text_input(
            "Enter city: "
        )


        # First, validate the location exactly
        # as the user entered it.
        info(
            "\nValidating location..."
        )


        location = find_location(
            city,
            country
        )


        # If the location is valid,
        # do not call Gemini.
        if location is not None:

            location_city = location.get(
                "name",
                city
            )

            location_country = location.get(
                "country",
                country
            )


            print(
                "\nLocation found:"
            )

            print(
                f"{location_city}, "
                f"{location_country}"
            )


            confirmed = get_yes_no(
                "Use this location? (y/n): "
            )


            if confirmed:

                return {
                    "city": location_city,
                    "country": location_country
                }


            warning(
                "Please enter "
                "the location again."
            )

            continue


        # If the location was not found,
        # use Gemini as a fallback.
        warning(
            "\nLocation could not be "
            "verified as entered."
        )


        ai(
            "Gemini is checking "
            "the spelling of the location..."
        )


        corrected = correct_location_name(
            city,
            country
        )


        corrected_city = corrected[
            "city"
        ]

        corrected_country = corrected[
            "country"
        ]


        # If Gemini did not change anything,
        # there is nothing useful to validate again.
        if (
            corrected_city.lower()
            == city.lower()
            and
            corrected_country.lower()
            == country.lower()
        ):

            error(
                "Gemini could not find "
                "a different correction."
            )


            retry = get_yes_no(
                "Try entering the location "
                "again? (y/n): "
            )


            if retry:

                continue


            return None


        ai(
            f"AI suggestion: "
            f"{corrected_city}, "
            f"{corrected_country}"
        )


        info(
            "Validating corrected location..."
        )


        corrected_location = find_location(
            corrected_city,
            corrected_country
        )


        if corrected_location is None:

            error(
                "The corrected location "
                "could not be verified."
            )


            retry = get_yes_no(
                "Try entering the location "
                "again? (y/n): "
            )


            if retry:

                continue


            return None


        location_city = corrected_location.get(
            "name",
            corrected_city
        )

        location_country = corrected_location.get(
            "country",
            corrected_country
        )


        print(
            "\nCorrected location:"
        )

        print(
            f"{location_city}, "
            f"{location_country}"
        )


        confirmed = get_yes_no(
            "Use this corrected "
            "location? (y/n): "
        )


        if confirmed:

            return {
                "city": location_city,
                "country": location_country
            }


        warning(
            "Please enter "
            "the location again."
        )