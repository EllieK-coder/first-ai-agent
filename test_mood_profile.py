from mood_profile import validate_profile

ALLOWED = ["Relaxing", "Cozy", "Horror"]


def test_real_tags_are_kept():
    raw = {"Relaxing": 1.0, "Cozy": 0.7}

    assert validate_profile(raw, ALLOWED) == {"Relaxing": 1.0, "Cozy": 0.7}


def test_invented_tags_are_dropped():
    raw = {"Relaxing": 1.0, "Chillvibes": 0.8}

    assert validate_profile(raw, ALLOWED) == {"Relaxing": 1.0}


def test_zero_or_negative_weights_are_dropped():
    raw = {"Relaxing": 1.0, "Horror": -0.5}

    assert validate_profile(raw, ALLOWED) == {"Relaxing": 1.0}


def test_weights_above_one_are_capped():
    raw = {"Relaxing": 5}

    assert validate_profile(raw, ALLOWED) == {"Relaxing": 1.0}

def test_synonyms_are_mapped_to_real_tags():
    raw = {"Chill": 0.9}

    assert validate_profile(raw, ALLOWED) == {"Relaxing": 0.9}




def test_non_dictionary_gives_empty_profile():
    raw = ["Relaxing"]

    assert validate_profile(raw, ALLOWED) == {}