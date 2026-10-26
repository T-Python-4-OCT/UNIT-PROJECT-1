"""Traffic period lookup and trip duration estimation.

All traffic data here is simulated. It is not retrieved from a live
traffic service.
"""
from __future__ import annotations

from datetime import datetime

TIME_FORMAT = "%H:%M"
SEARCH_STEP_MINUTES = 15
OFF_PEAK = "Off-Peak"

TRAFFIC_PERIODS = {
    "Morning Peak": {"start_hour": 7, "end_hour": 10, "multiplier": 1.7},
    "Midday": {"start_hour": 10, "end_hour": 16, "multiplier": 1.2},
    "Evening Peak": {"start_hour": 16, "end_hour": 19, "multiplier": 1.6},
    OFF_PEAK: {"start_hour": 0, "end_hour": 24, "multiplier": 1.0},
}


def get_traffic_info(departure_time: str) -> tuple[str, float]:
    """Return the traffic period name and its multiplier.

    Args:
        departure_time: Time in ``HH:MM`` format.

    Raises:
        ValueError: If the time is not in ``HH:MM`` format.
    """
    hour = datetime.strptime(departure_time, TIME_FORMAT).hour

    for period, details in TRAFFIC_PERIODS.items():
        if period == OFF_PEAK:
            continue

        if details["start_hour"] <= hour < details["end_hour"]:
            return period, details["multiplier"]

    return OFF_PEAK, TRAFFIC_PERIODS[OFF_PEAK]["multiplier"]


def estimate_trip_duration(
    base_minutes: int, departure_time: str
) -> tuple[str, int]:
    """Estimate the car duration for a departure time.

    Returns:
        A tuple of (traffic period, estimated minutes).
    """
    period, multiplier = get_traffic_info(departure_time)
    return period, round(base_minutes * multiplier)


def find_departure_time(base_minutes: int, arrival_time: str) -> dict | None:
    """Find the latest departure that still arrives by ``arrival_time``.

    Departure times are checked every 15 minutes during the day.

    Returns:
        A dict with the departure time, arrival time, duration and traffic
        period, or ``None`` if no departure time works.

    Raises:
        ValueError: If ``arrival_time`` is not in ``HH:MM`` format.
    """
    arrival = datetime.strptime(arrival_time, TIME_FORMAT)
    target_minutes = arrival.hour * 60 + arrival.minute

    best = None
    best_arrival = -1

    for hour in range(24):
        for minute in range(0, 60, SEARCH_STEP_MINUTES):
            departure_time = f"{hour:02d}:{minute:02d}"
            period, duration = estimate_trip_duration(
                base_minutes, departure_time
            )
            estimated_arrival = hour * 60 + minute + duration

            if best_arrival < estimated_arrival <= target_minutes:
                best_arrival = estimated_arrival
                best = {
                    "departure_time": departure_time,
                    "arrival_minutes": estimated_arrival,
                    "duration": duration,
                    "period": period,
                }

    return best


def suggest_departure_time(base_minutes: int, arrival_time: str) -> str | None:
    """Print a departure time suggestion and return the suggested time."""
    suggestion = find_departure_time(base_minutes, arrival_time)

    print("\n" + "=" * 42)
    print("        DEPARTURE TIME SUGGESTION")
    print("=" * 42)
    print(f"  Desired arrival : {arrival_time}")

    if suggestion is None:
        print("  No suitable departure time found.")
        print("  Try a later arrival time or shorter trip.")
        print("=" * 42)
        return None

    arrival_minutes = suggestion["arrival_minutes"]
    print(f"  Leave at        : {suggestion['departure_time']}")
    print(
        f"  Estimated arrival: "
        f"{arrival_minutes // 60:02d}:{arrival_minutes % 60:02d}"
    )
    print(f"  Driving duration: {suggestion['duration']} minutes")
    print(f"  Traffic period  : {suggestion['period']}")
    print("=" * 42)

    return suggestion["departure_time"]
