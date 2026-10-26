"""Display Riyadh traffic statistics from the sample data file."""
from __future__ import annotations

import json

STATS_FILE = "traffic_stats.json"


def load_traffic_stats() -> dict | None:
    """Load traffic statistics. Return None if they cannot be loaded."""
    try:
        with open(STATS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"\nTraffic statistics unavailable: {STATS_FILE} not found.")
    except json.JSONDecodeError:
        print(f"\nTraffic statistics unavailable: {STATS_FILE} is invalid.")

    return None


def _print_rush_hour(title: str, data: dict) -> None:
    """Print the statistics of one rush hour."""
    print(f"\n  {title}")
    print(f"  Congestion: {data['average_congestion_percent']}%")
    print(f"  Average speed: {data['average_speed_kmh']} km/h")
    print(f"  Time for 10 km: {data['travel_time_10km_minutes']} min")


def display_traffic_report() -> None:
    """Print the traffic report."""
    stats = load_traffic_stats()

    if stats is None:
        return

    try:
        print("\n" + "=" * 45)
        print("       RIYADH TRAFFIC REPORT")
        print("=" * 45)

        print(f"  City: {stats['city']}")
        print(f"  Year: {stats['year']}")
        print(f"  Source: {stats['source']}")
        print("-" * 45)

        print(
            f"  Average congestion: "
            f"{stats['average_congestion_percent']}%"
        )
        print(f"  Average speed: {stats['average_speed_kmh']} km/h")
        print(
            f"  Rush-hour speed: "
            f"{stats['average_speed_rush_hour_kmh']} km/h"
        )

        _print_rush_hour("MORNING RUSH HOUR", stats["morning_rush_hour"])
        _print_rush_hour("EVENING RUSH HOUR", stats["evening_rush_hour"])
        print("=" * 45)
    except KeyError as error:
        print(f"\nTraffic statistics are incomplete: missing {error}.")


if __name__ == "__main__":
    display_traffic_report()
