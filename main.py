from trips import plan_trip
from storage import load_trips, save_trip, update_trip, delete_trip
from traffic_data import estimate_trip_duration , suggest_departure_time
from datetime import datetime
from transport_advisor import compare_transport_options
from traffic_stats import display_traffic_report

def display_menu():
    print("\n" + "=" * 46)
    print("          RIYADH SMART TRIP")
    print("   Your Smart Journey Planning Assistant")
    print("=" * 46)

    print("\n  MAIN MENU")
    print("  " + "-" * 42)
    print("  [1]  Plan a Trip")
    print("  [2]  View Saved Trips")
    print("  [3]  View Trip Report")
    print("  [4]  Update a Trip")
    print("  [5]  Delete a Trip")
    print("  [6]  Compare Transport Options")
    print("  [7]  Suggest Departure Time")
    print("  [8]  Exit")
    print("  " + "-" * 42)

def main():
    while True:
        display_menu()

        choice = input("Enter your choice (1-8): ").strip()

        if choice == "1":
            plan_trip()

        
        elif choice == "2":
            trips = load_trips()

            print("\n" + "=" * 46)
            print("             SAVED TRIPS")
            print("=" * 46)

            if not trips:
                print("  No saved trips found!")
            else:
                for index, trip in enumerate(trips, start=1):
                    print(f"\n  TRIP #{index}")
                    print("  " + "-" * 42)
                    print(f"  From       : {trip['origin']}")
                    print(f"  To         : {trip['destination']}")
                    print(f"  Departure  : {trip['departure_time']}")
                    print(f"  Traffic    : {trip['traffic_period']}")
                    print(f"  Duration   : {trip['estimated_minutes']} minutes")

            print("=" * 46)



            
        elif choice == "3":
            trips = load_trips()

            print("\n" + "=" * 46)
            print("              TRIP REPORT")
            print("=" * 46)

            if not trips:
                print("  No saved trips available for reporting.")
            else:
                total = len(trips)
                average = sum(
                    trip["estimated_minutes"] for trip in trips
                ) / total

                print(f"  Total Saved Trips : {total}")
                print(f"  Average Duration  : {average:.1f} minutes")

                fastest = min(
                    trips, key=lambda trip: trip["estimated_minutes"]
                )
                longest = max(
                    trips, key=lambda trip: trip["estimated_minutes"]
                )

                print("\n  FASTEST CAR TRIP")
                print(f"  {fastest['origin']} -> {fastest['destination']}")
                print(f"  {fastest['estimated_minutes']} minutes")

                metro_trips = [
                    trip for trip in trips
                    if isinstance(trip.get("metro_duration"), (int, float))
                    and trip["metro_duration"] > 0
                ]

                print("\n  FASTEST METRO TRIP")

                if metro_trips:
                    fastest_metro = min(
                        metro_trips,
                        key=lambda trip: trip["metro_duration"]
                    )

                    print(
                        f"  {fastest_metro['origin']} -> "
                        f"{fastest_metro['destination']}"
                    )
                    print(f"  {fastest_metro['metro_duration']} minutes")
                else:
                    print("  No saved metro trip data available yet.")

            print("=" * 46)
            display_traffic_report()

        
        elif choice == "4":
            trips = load_trips()

            if not trips:
                print("\nNo saved trips found!")
                continue

            for index, trip in enumerate(trips, start=1):
                print(f"{index}. {trip['origin']} -> {trip['destination']}")

            try:
                number = int(input("Enter trip number to update: "))

                if not 1 <= number <= len(trips):
                    print("Invalid trip number!")
                    continue

                new_time = input("Enter new departure time (HH:MM): ").strip()
                datetime.strptime(new_time, "%H:%M")

                trip = trips[number - 1]

                period, duration = estimate_trip_duration(
                    trip["base_minutes"], new_time
                )

                updated_trip = {
                    "departure_time": new_time,
                    "traffic_period": period,
                    "estimated_minutes": duration,
                    "car_duration": duration
                }

                result = compare_transport_options(
                    trip["origin"],
                    trip["destination"],
                    new_time
                )

                if result is not None:
                    updated_trip.update(result)

                update_trip(number - 1, updated_trip)

            except ValueError:
                print("Invalid time!")


        elif choice == "5":
            trips = load_trips()

            if not trips:
                print("\nNo saved trips found!")
                continue

            for index, trip in enumerate(trips, start=1):
                print(f"{index}. {trip['origin']} -> {trip['destination']}")

            try:
                number = int(input("Enter trip number to delete: "))

                if not 1 <= number <= len(trips):
                    print("Invalid trip number!")
                    continue

                delete_trip(number - 1)

            except ValueError:
                print("Invalid trip number!")
                
         
      
        elif choice == "6":
            origin = input("Enter starting location: ").strip()
            destination = input("Enter destination: ").strip()
            departure_time = input("Enter departure time (HH:MM): ").strip()

            if not origin or not destination:
                print("\nError: Locations cannot be empty.")
                continue

            try:
                datetime.strptime(departure_time, "%H:%M")
                result = compare_transport_options(
                    origin, destination, departure_time
                )

                if result is not None:
                    save_trip(result)
                    print("Trip comparison saved successfully.")
            except ValueError:
                print("\nInvalid time. Please use HH:MM, for example 08:30.")
                
                
            
        elif choice == "7":
            trips = load_trips()

            if not trips:
                print("\nNo saved trips found!")
                continue

            print("\nSAVED TRIPS")
            print("-" * 42)

            for index, trip in enumerate(trips, start=1):
                print(
                    f"{index}. {trip['origin']} -> "
                    f"{trip['destination']}"
                )

            try:
                number = int(input("Choose a trip number: "))

                if not 1 <= number <= len(trips):
                    print("Invalid trip number!")
                    continue

                arrival_time = input(
                    "Enter desired arrival time (HH:MM): "
                ).strip()

                datetime.strptime(arrival_time, "%H:%M")

                trip = trips[number - 1]
                base_minutes = trip.get("base_minutes")

                if base_minutes is None:
                    print("Base trip duration is unavailable.")
                    continue

                suggest_departure_time(
                    base_minutes, arrival_time
                )

            except ValueError:
                print("Please enter a valid trip number and time.")

                
                
        elif choice == "8":
            print("\nThank you for using Riyadh Smart Trip!")
            break

        else:
            print("\nInvalid choice, Please enter a number from 1 to 8. ")


if __name__ == "__main__":
    main()
