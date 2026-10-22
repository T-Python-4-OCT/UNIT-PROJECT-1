import requests

def get_crisis_weather(latitude: float, longitude: float):
    """Fetch live current weather for a crisis location using Open-Meteo API"""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            weather = data.get("current_weather", {})
            return {
                "temperature": weather.get("temperature"),
                "windspeed": weather.get("windspeed"),
                "weathercode": weather.get("weathercode")
            }
    except requests.RequestException:
        pass
    
    return None