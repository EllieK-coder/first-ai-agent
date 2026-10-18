import json
import time
import requests
from steam_library import get_owned_games

SKIP_WORDS = ["Public Test", "PTS", "Multiplayer", "Zombies"]


def get_tags(appid):
    response = requests.get(
        "https://steamspy.com/api.php",
        params={"request": "appdetails", "appid": appid}
    )
    data = response.json()
    tags = data.get("tags", {})
    if not tags:          # SteamSpy returns [] instead of {} when a game has no tags
        return {}
    return tags


def build_library():
    games = get_owned_games()
    library = []

    for game in games:
        name = game["name"]

        # skip test servers and separate modes
        if any(word in name for word in SKIP_WORDS):
            continue

        print("Fetching tags for", name)
        tags = get_tags(game["appid"])

        library.append({
            "appid": game["appid"],
            "name": name,
            "playtime": game["playtime_forever"],
            "tags": tags,
        })

        time.sleep(1)     # be polite to SteamSpy: 1 request per second

    with open("library.json", "w", encoding="utf-8") as f:
        json.dump(library, f, indent=2, ensure_ascii=False)

    print("Saved", len(library), "games to library.json")


if __name__ == "__main__":
    build_library()