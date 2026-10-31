from mood_engine import tag_strengths, score_game , rank_library, clean_library, EXCLUDE_APPIDS


def test_top_tag_gets_strength_one():
    tags = {"Relaxing": 200, "Cozy": 100}

    strengths = tag_strengths(tags)

    assert strengths["Relaxing"] == 1.0


def test_other_tags_are_relative_to_the_top_tag():
    tags = {"Relaxing": 200, "Cozy": 100}
    strengths = tag_strengths(tags)
    assert strengths["Cozy"] == 0.5


def test_empty_tags_give_empty_strengths():
    strengths = tag_strengths({})

    assert strengths == {}


def make_game(tags, playtime=0, name="Test Game", appid=1):
    """Build a fake game in the same shape as the entries in library.json."""
    return {"appid": appid, "name": name, "playtime": playtime, "tags": tags}


def test_game_with_the_mood_tag_as_top_tag_scores_one():
    game = make_game({"Relaxing": 100})
    profile = {"Relaxing": 1.0}
    assert score_game(game, profile) == 1.0


def test_game_without_any_mood_tags_scores_zero():
  game = make_game({"Horror": 100})
  profile = {"Relaxing": 1.0}
  assert score_game(game, profile) == 0.0


def test_score_is_capped_at_one():
    game = make_game({"Relaxing": 50, "Cozy": 50, "Casual": 50, "Atmospheric": 50})
    profile = {"Relaxing": 1.0, "Cozy": 1.0, "Casual": 1.0, "Atmospheric": 1.0}
    assert score_game(game, profile) == 1.0


def test_results_are_sorted_best_first():
    strong = make_game({"Relaxing": 100}, playtime=5000, name="Strong")
    medium = make_game({"Action": 100, "Relaxing": 60}, playtime=5000, name="Medium")
    profile = {"Relaxing": 1.0}

    results = rank_library([medium, strong], profile)

    assert [game["name"] for game in results] == ["Strong", "Medium"]



def test_weak_matches_are_left_out():
    game = make_game({"Action": 100, "Relaxing": 30})
    profile = {"Relaxing": 1.0}

    results = rank_library([game], profile)

    assert results == []

def test_unplayed_game_ranks_above_played_game_with_same_tags():
    played = make_game({"Relaxing": 100}, playtime=5000, name="Played")
    unplayed = make_game({"Relaxing": 100}, playtime=0, name="Unplayed")
    profile = {"Relaxing": 1.0}

    results = rank_library([played, unplayed], profile)

    assert [game["name"] for game in results] == ["Unplayed", "Played"]


def test_games_without_tags_are_removed():
    tagged = make_game({"Relaxing": 100}, name="Tagged")
    untagged = make_game({}, name="Untagged")

    cleaned = clean_library([tagged, untagged])

    assert [game["name"] for game in cleaned] == ["Tagged"]

def test_excluded_appids_are_removed():
    excluded_id = next(iter(EXCLUDE_APPIDS))

    normal = make_game({"Relaxing": 100}, name="Normal game", appid=2)
    launcher = make_game({"Action": 100}, name="Launcher", appid=excluded_id)

    cleaned = clean_library([normal, launcher])

    assert [game["name"] for game in cleaned] == ["Normal game"]




def test_duplicates_keep_the_most_played_copy():
    less_played = make_game({"Strategy": 100}, playtime=10, name="Civilization IV", appid=1)
    more_played = make_game({"Strategy": 100}, playtime=500, name="Civilization IV", appid=2)

    cleaned = clean_library([less_played, more_played])

    assert len(cleaned) == 1
    assert cleaned[0]["playtime"] == 500