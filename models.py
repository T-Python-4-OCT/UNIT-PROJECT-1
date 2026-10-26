"""Data model for a planned trip."""
from __future__ import annotations


class Trip:
    """A planned car trip with its estimated duration."""

    def __init__(
        self,
        origin: str,
        destination: str,
        departure_time: str,
        base_minutes: int,
        traffic_period: str,
        estimated_minutes: int,
    ) -> None:
        self.origin = origin
        self.destination = destination
        self.departure_time = departure_time
        self.base_minutes = base_minutes
        self.traffic_period = traffic_period
        self.estimated_minutes = estimated_minutes

    def to_dict(self) -> dict:
        """Return the trip as a dict that can be saved as JSON."""
        return {
            "origin": self.origin,
            "destination": self.destination,
            "departure_time": self.departure_time,
            "base_minutes": self.base_minutes,
            "traffic_period": self.traffic_period,
            "estimated_minutes": self.estimated_minutes,
        }

    def display_trip(self) -> None:
        """Print the trip details."""
        print(f"From: {self.origin}")
        print(f"To: {self.destination}")
        print(f"Departure: {self.departure_time}")
        print(f"Traffic period: {self.traffic_period}")
        print(f"Estimated duration: {self.estimated_minutes} minutes")
