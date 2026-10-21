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
    
    
    
    
    






