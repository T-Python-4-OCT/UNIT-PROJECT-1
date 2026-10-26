
import requests
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("FOOTBALL_API_KEY")

def get_club_info(team_id):
    url = f"https://api.football-data.org/v4/teams/{team_id}"

    headers = {
        "X-Auth-Token": api_key
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as error:
        print(f"API Error: {error}")
        return None

def get_club_matches(team_id):
    url = f"https://api.football-data.org/v4/teams/{team_id}/matches"

    headers = {
        "X-Auth-Token": api_key
    }

    params = {
        "status": "SCHEDULED",
        "limit": 5
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=10
        )

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as error:
        print(f"API Error: {error}")
        return None