from nba_api.stats.static import players
from rapidfuzz import process, fuzz

ALL_PLAYERS = players.get_players()

ACTIVE_PLAYERS = [p for p in ALL_PLAYERS if p["is_active"]]

PLAYER_NAMES = [p["full_name"] for p in ACTIVE_PLAYERS]


def extract_player_name(user_query: str) -> str:
    words = user_query.lower().split()

    best_match = None
    best_score = 0

    # ---- PRIORITIZE 2-WORD MATCHES ----
    for i in range(len(words) - 1):
        candidate = words[i] + " " + words[i + 1]

        match, score, _ = process.extractOne(
            candidate,
            PLAYER_NAMES,
            scorer=fuzz.token_set_ratio
        )

        if score > best_score:
            best_match = match
            best_score = score

    # If strong 2-word match found, return immediately
    if best_score >= 75:
        return best_match

    # ---- FALLBACK TO SINGLE WORD (STRICTER THRESHOLD) ----
    for word in words:
        match, score, _ = process.extractOne(
            word,
            PLAYER_NAMES,
            scorer=fuzz.token_set_ratio
        )

        if score > best_score:
            best_match = match
            best_score = score

    if best_score >= 85:  # stricter for single words
        return best_match

    raise Exception(
        f"No confident player match found. Best guess: {best_match} ({best_score})"
    )