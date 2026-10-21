"""SkyRoute entry point: create the data files and list the destinations."""
import sys

from agency import seed
from agency.services import countries
from agency.ui import views
from agency.ui.console import console, info, show_banner


def main() -> None:
    """Program entry: seed data, banner, then the destination table."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass

    seed.run()
    show_banner()
    views.show_countries(countries.list_all())
    console.print()
    info("Safe travels ✈️")


if __name__ == "__main__":
    main()
