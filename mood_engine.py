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


def all_tags(library):
    """Every distinct tag that appears in the library, sorted alphabetically."""
    tags = set()
    for game in library:
        tags.update(game["tags"].keys())
    return sorted(tags)


def score_game(game, profile):
    """How well one game matches a mood profile, from 0 to 1."""
    strengths = tag_strengths(game["tags"])

    total = 0
    for tag, weight in profile.items():
        total += weight * strengths.get(tag, 0)

    return round(total / sum(profile.values()), 2)


def rank_library(library, profile, top_n=10):
    scored = []
    for game in library:
        score = score_game(game, profile)
        # TODO: backlog bonus goes here
        if score > 0:
            scored.append({"name": game["name"], "playtime": game["playtime"], "score": score})

    scored.sort(key=lambda g: g["score"], reverse=True)
    return scored[:top_n]


if __name__ == "__main__":
    library = load_library()

    # uncomment to see every tag you can use in a profile
    # print(all_tags(library))

    relax = {"Relaxing": 1.0, "Cozy": 0.8, "Casual": 0.6, "Atmospheric": 0.5}
    anger = {"Violent": 1.0, "Action": 0.8, "Shooter": 0.7, "Hack and Slash": 0.7, "Gore": 0.5, "Fast-Paced": 0.5}
    challenge = {"Difficult": 1.0, "Souls-like": 0.8, "Puzzle": 0.5, "Roguelike": 0.5}

    profiles = {"relax": relax, "anger": anger, "challenge": challenge}

    for mood, profile in profiles.items():
        print("\n===", mood, "===")
        for game in rank_library(library, profile):
            print(game["score"], "-", game["name"], "-", game["playtime"], "min")