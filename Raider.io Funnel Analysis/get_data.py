import requests
import time

API_KEY = "RIO7ytwWRZ387DM6iPhMjpXdy"
BASE_URL = "https://raider.io/"
STATIC_DATA_URL = "api/v1/mythic-plus/static-data"
RUNS_URL = "api/v1/mythic-plus/runs"
REGION = "us"
SEASON = "season-tww-1"
EXPANSION_ID = 10      #Expansion number in order. 10 = TWW, 9 = Dragonflight, etc.

def api_call(suffix, params):
    r = requests.get(BASE_URL + suffix,params)
    r.raise_for_status()
    return r.json()

def fetch_dungeons():
    """Gets the pool of the dungeons for the season."""
    params = {
        "expansion_id": EXPANSION_ID
    }
    r = api_call(STATIC_DATA_URL, params)["seasons"]
    season_static_data = next((item for item in r if item["slug"] == SEASON), None)
    dungeons = season_static_data["dungeons"]
    names = [item["name"] for item in dungeons]
    return names

def fetch_runs(page):
    """Fetch one batch of runs from the raider.io API"""
    params = {
        "region": REGION,
        "season": SEASON,
        "page": page
    }
    return api_call(RUNS_URL, params)['rankings']
