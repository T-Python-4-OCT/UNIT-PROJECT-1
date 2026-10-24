
class Trip:
    def __init__(
        self, origin, destination,
        departure_time, base_minutes,
        traffic_period, estimated_minutes
    ):
        self.origin = origin
        self.destination = destination
        self.departure_time = departure_time
        self.base_minutes = base_minutes
        self.traffic_period = traffic_period
        self.estimated_minutes = estimated_minutes

    def display_trip(self):
        print(f"From: {self.origin}")
        print(f"To: {self.destination}")
        print(f"Departure: {self.departure_time}")
        print(f"Traffic period: {self.traffic_period}")
        print(f"Estimated duration: {self.estimated_minutes} minutes")
