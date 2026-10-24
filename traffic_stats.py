
import json


def load_traffic_stats():
    with open("traffic_stats.json", "r", encoding="utf-8") as file:
        return json.load(file)


def display_traffic_report():
    stats = load_traffic_stats()

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

    print("\n  MORNING RUSH HOUR")
    morning = stats["morning_rush_hour"]
    print(f"  Congestion: {morning['average_congestion_percent']}%")
    print(f"  Average speed: {morning['average_speed_kmh']} km/h")
    print(f"  Time for 10 km: {morning['travel_time_10km_minutes']} min")

    print("\n  EVENING RUSH HOUR")
    evening = stats["evening_rush_hour"]
    print(f"  Congestion: {evening['average_congestion_percent']}%")
    print(f"  Average speed: {evening['average_speed_kmh']} km/h")
    print(f"  Time for 10 km: {evening['travel_time_10km_minutes']} min")

    print("=" * 45)


if __name__ == "__main__":
    display_traffic_report()
