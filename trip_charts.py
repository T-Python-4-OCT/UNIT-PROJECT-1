"""Charts that compare car and metro trip durations."""
from __future__ import annotations

import matplotlib.pyplot as plt


def show_transport_chart(
    car_duration: int,
    metro_duration: int,
    origin: str,
    destination: str,
) -> None:
    """Show a bar chart comparing car and metro duration.

    The program waits until the chart window is closed.
    """
    transport_options = ["Car", "Metro"]
    durations = [car_duration, metro_duration]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(transport_options, durations)

    plt.title(f"Trip Duration: {origin} to {destination}")
    plt.xlabel("Transport Type")
    plt.ylabel("Duration (minutes)")

    for bar, duration in zip(bars, durations):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{duration} min",
            ha="center",
            va="bottom",
        )

    plt.tight_layout()
    plt.show()
