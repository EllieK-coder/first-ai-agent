import json


def load_library():
    with open("library.json", "r", encoding="utf-8") as f:
        return json.load(f)


def tag_strengths(tags):
    """Turn raw vote counts into 0-1 strengths, relative to the game's top tag."""
    if not tags:
        return {}

    top_votes = max(tags.values())
    strengths = {}
    for tag, votes in tags.items():
        strengths[tag] = round(votes / top_votes, 2)

    return strengths


if __name__ == "__main__":
    library = load_library()

    for game in library:
        if game["name"] == "Stardew Valley":
            print(game["name"])
            print(tag_strengths(game["tags"]))