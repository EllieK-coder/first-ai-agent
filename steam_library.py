# 1. import os, requests, and load_dotenv from dotenv
# 2. call load_dotenv(), then read STEAM_API_KEY and STEAM_ID with os.getenv()
# 3. requests.get() on:
#    https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/
#    with params: key, steamid, include_appinfo=1
# 4. .json() it, then print it and find where the list of games is
# 5. print each game's name and playtime_forever (that's in minutes)
# 6. bonus: print only games with playtime under 60 minutes, your backlog

import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("STEAM_API_KEY")
steam_id = os.getenv("STEAM_ID")

print("Key loaded:", api_key is not None)
print("Key length:", len(api_key) if api_key else 0)

def get_owned_games():
    response = requests.get(
        "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/",
        params={"key": api_key, "steamid": steam_id, "include_appinfo": 1}
    )
    print("Status:", response.status_code)
    print(response.text[:300])
    data = response.json()
    return data["response"]["games"]

if __name__ == "__main__":
    games = get_owned_games()
    print("You own", len(games), "games")

    for game in games:
        if game["playtime_forever"] < 60:
            print(game["name"], "-", game["playtime_forever"], "minutes")