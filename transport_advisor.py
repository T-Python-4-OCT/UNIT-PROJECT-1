import json 



def load_transport_options():
    with open("transport_options.json","r",encoding="utf-8") as file:
        data=json.load(file)
        
        
    return data["routes"]



def find_transport_options(origin,destination):
    routes=load_transport_options()


    for route in routes:
        if(
            route["origin"].lower()==origin.lower()
            and route["destination"].lower()== destination.lower()
            
                ):
            
            return route["options"]
        
        
        
    return None

def compare_transport_options(origin,destination):
    options=find_transport_options(origin, destination)
    
    
    if options is None:
        print("this route in not available.")
        return None
    
    
    
    print("\n----- Transport Options -----")
    
    
    for option in options:
        print(f"\nTransport : {option['mode']}")
        print(f"Estimated duration: {option['base_duration_minutes']} minutes ")
        print(f"Estimated cost: {option['cost_sar']} SAR")
        print(f"Walking time:{option['walking_minutes']} minutes ")
        
        
    fastest_option=min(
        options,
        key=lambda option:option["base_duration_minutes"]
        )
    print("\n---Recommendation---")
    
    print(f"Fastes option:{fastest_option['mode']}")
    
    
    return fastest_option
        
        





















