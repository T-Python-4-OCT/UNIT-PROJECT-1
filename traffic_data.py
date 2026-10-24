from datetime import datetime

TRAFFIC_PERIODS={
   "Morning Peak":{
       "start_hour":7,
       "end_hour":10,
       "multiplier":1.7
       },
   "Midday":{
       "start_hour":10,
       "end_hour":16,
       "multiplier":1.2
       },
   "Evening Peak":{
       "start_hour":16,
       "end_hour":19,
       "multiplier":1.6
       },
   "Off-Peak":{
       "start_hour":0,
       "end_hour":24,
       "multiplier":1.0
      
       }
    }

def get_traffic_info(departure_time):
    time=datetime.strptime(departure_time,"%H:%M")
    hour=time.hour
    
    
    for period,details in TRAFFIC_PERIODS.items():
        if period =="Off-Peak":
            continue
        
        
        if details["start_hour"] <= hour <details["end_hour"]:
            return period,details["multiplier"]
        
        
    return "Off-Peak", TRAFFIC_PERIODS["Off-Peak"]["multiplier"]



def estimate_trip_duration(base_minutes,departure_time):
    period,multiplier=get_traffic_info(departure_time)        
    
    estimated_minutes =round(base_minutes*multiplier)
    return period,estimated_minutes
    
    
    

def suggest_departure_time(base_minutes, arrival_time):
    arrival = datetime.strptime(arrival_time, "%H:%M")
    target_minutes = arrival.hour * 60 + arrival.minute

    best_time = None
    best_duration = None
    best_arrival = -1

    for hour in range(24):
        for minute in range(0, 60, 15):
            departure_time = f"{hour:02d}:{minute:02d}"

            period, duration = estimate_trip_duration(
                base_minutes, departure_time
            )

            departure_minutes = hour * 60 + minute
            estimated_arrival = departure_minutes + duration

            if (
                estimated_arrival <= target_minutes
                and estimated_arrival > best_arrival
            ):
                best_time = departure_time
                best_duration = duration
                best_arrival = estimated_arrival
                best_period = period

    print("\n" + "=" * 42)
    print("        DEPARTURE TIME SUGGESTION")
    print("=" * 42)
    print(f"  Desired arrival : {arrival_time}")

    if best_time is None:
        print("  No suitable departure time found.")
        print("  Try a later arrival time or shorter trip.")
        print("=" * 42)
        return None

    print(f"  Leave at        : {best_time}")
    print(f"  Estimated arrival: {best_arrival // 60:02d}:{best_arrival % 60:02d}")
    print(f"  Driving duration: {best_duration} minutes")
    print(f"  Traffic period  : {best_period}")
    print("=" * 42)

    return best_time
