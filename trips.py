from datetime import datetime
from traffic_data import estimate_trip_duration




def plan_trip():
    print("\n----PLAN a Trip----")
    
    
    origin=input("Enter starting location:").strip()
    destination=input("Enter destination:").strip()
    
    
    if not origin or not destination:
        print("Error: loactions cannot be empty!")
        return None
    
    
    departure_time=input("Enter departure time (HH:MM):").strip()
    
    
    try:
        base_minutes=float(input("Enter estimated base trip duration in Minutes:"))
        
        if base_minutes <=0:
            print("Duration must br greater than zero.")
            return None
        
    except ValueError :
        print("Please enter a valid number for the duration.")
        return None
    
    period,estimated_minutes=estimate_trip_duration(
        base_minutes,departure_time
        )
    
    
    trip={
        "origin":origin,
        "destination":destination,
        "departure_time":departure_time,
        "base_minutes":base_minutes,
        "traffic_period":period,
        "estimated_minutes":estimated_minutes
        }
        

    print("\n ----Trip Estimate----")
    print(f"from:{origin}")
    print(f"To: {destination}")
    print(f"Departure: {departure_time}")
    print(f"Traffic period: {period}")
    print(f"Estimated duration: {estimated_minutes} Minutes")
    
    
    return trip
        
        
        