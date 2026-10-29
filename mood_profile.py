import json
import ollama
from mood_engine import load_library, clean_library, all_tags, rank_library, BACKLOG_MINUTES





MODEL = "qwen2.5:7b"
DEBUG = True



SYNONYMS = {           # invented words the model likes -> the real Steam tag
    "Chill": "Relaxing",
    "Calming": "Relaxing",
    "Unwinding": "Relaxing",
    "Leisure": "Casual",
    "Challenge": "Difficult",
    "Hardcore": "Difficult",
    "Smash": "Destruction",
    "Angry": "Violent",
}

MOOD_TAGS = [          # <-- NEW: only tags that describe a feeling
    # calm / comfort
    "Relaxing", "Cozy", "Casual", "Wholesome", "Atmospheric", "Beautiful",
    "Great Soundtrack", "Exploration", "Walking Simulator", "Farming Sim",
    "Life Sim", "Building", "Sandbox", "Family Friendly",
    # venting / energy
    "Action", "Fast-Paced", "Violent", "Gore", "Shooter", "FPS",
    "Hack and Slash", "Beat 'em up", "Fighting", "Destruction", "Combat",
    # challenge / focus
    "Difficult", "Souls-like", "Unforgiving", "Perma Death", "Roguelike",
    "Roguelite", "Precision Platformer", "Puzzle", "Strategy", "Tactical",
    "Competitive",
    # fear / tension
    "Horror", "Psychological Horror", "Survival Horror", "Thriller", "Survival",
    # story / feelings
    "Story Rich", "Emotional", "Choices Matter", "Mystery",
    # fun / social
    "Funny", "Comedy", "Co-op", "Online Co-Op", "Party Game", "Arcade",
]


def mood_tags(library):            # <-- NEW
    """The curated mood tags that actually exist in this library."""
    available = set(all_tags(library))
    return [tag for tag in MOOD_TAGS if tag in available]


def pick_games(mood_text, candidates):
    """Let the LLM choose 1-3 games from the ranked candidates and explain why."""
    top = candidates[:5]

    lines = []
    for game in top:
        if game["playtime"] < BACKLOG_MINUTES:
            lines.append(f"- {game['name']} | owned but never or barely played")
        else:
            hours = round(game["playtime"] / 60, 1)
            lines.append(f"- {game['name']} | played {hours} hours")

    candidate_text = "\n".join(lines)
    if DEBUG:
        print(candidate_text)

    system = (
        "You are a friendly assistant that recommends Steam games the player already owns. "
        "Recommend 1 to 3 games ONLY from the list you are given. "
        "For each game, write 1-2 sentences on why it fits the player's mood. "
        "If a game is marked as never or barely played, mention that they already own it "
        "and haven't really tried it yet. "
        "Do not mention scores, hours or other numbers from the list."
    )

    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": f"My mood: {mood_text}\n\nGames I own:\n{candidate_text}"},
        ],
        options={"temperature": 0.3},
    )

    return response.message.content


def mood_to_profile(mood_text, allowed_tags):
    """Ask the LLM to turn the user's words into a weighted tag profile."""
    system = (
            "You turn a player's mood into a weighted profile of Steam tags. "
            "Always choose between 5 and 8 tags. Cover the different ways the mood could be satisfied. "
            "Use ONLY tags from this list, spelled exactly as written: "
            + ", ".join(allowed_tags) + ". "
                                        "Give each tag a weight from 0.1 to 1.0, where 1.0 is the most important. "
                                        "Reply with only a JSON object.\n\n"
                                        "Example 1\n"
                                        'Mood: "I\'m bored and want to explore somewhere new"\n'
                                        'Profile: {"Exploration": 1.0, "Atmospheric": 0.7, "Beautiful": 0.6, '
                                        '"Great Soundtrack": 0.5, "Walking Simulator": 0.4, "Sandbox": 0.4}\n\n'
                                        "Example 2\n"
                                        'Mood: "I want to laugh with my friends tonight"\n'
                                        'Profile: {"Funny": 1.0, "Co-op": 0.9, "Party Game": 0.8, '
                                        '"Comedy": 0.7, "Online Co-Op": 0.6, "Casual": 0.5}'
    )

    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": mood_text},
        ],
        format="json",
        options={"num_predict": 200, "num_ctx": 8192, "temperature": 0},
    )

    try:
        raw = json.loads(response.message.content)
    except json.JSONDecodeError:
        return {}

    if not isinstance(raw, dict):
        return {}

    profile = {}
    for tag, weight in raw.items():
        tag = SYNONYMS.get(tag, tag)
        if tag not in allowed_tags or not isinstance(weight, (int, float)):
            if DEBUG:
                print(f"[dropped invalid tag: {tag}]")
            continue
        if weight <= 0:
            if DEBUG:
                print(f"[dropped zero/negative weight: {tag}]")
            continue
        weight = min(float(weight), 1.0)
        profile[tag] = max(profile.get(tag, 0), weight)

    return profile




if __name__ == "__main__":
    library = clean_library(load_library())
    tags = mood_tags(library)
    print("Mood tags available:", len(tags))

    moods = [
        "I had a long day and just want to relax",
        "I'm so angry I want to smash something",
        "I want something that really tests my skills",
    ]

    for mood in moods:
        print("\n>", mood)
        profile = mood_to_profile(mood, tags)
        print("Profile:", profile)

        if not profile:
            print("Couldn't understand that mood.")
            continue

        ranked = rank_library(library, profile)
        print(pick_games(mood, ranked))


