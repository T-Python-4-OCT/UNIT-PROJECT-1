import json
import os
def load_trips():
    if not os.path.exists("trips.json"):
        return[]
    
    with open("trips.json","r",encoding="utf-8")as file:
        return json.load(file)
    
    
    
    
def save_trip(trip):
    trips=load_trips()
    trips.append(trip)
    
    
    with open("trips.json","w",encoding="utf-8") as file:
        json.dump(trips,file,indent=4,ensure_ascii=False)