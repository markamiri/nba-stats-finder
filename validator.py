# validator.py

import re

def validate_sql(query: str):

    q = query.strip()
    q_lower = q.lower()

    # ---------- must start with SELECT ----------
    if not q_lower.startswith("select"):
        raise Exception("Only SELECT queries allowed.")

    # ---------- prevent multiple statements ----------
    if ";" in q[:-1]:
        raise Exception("Multiple SQL statements are not allowed.")

    # ---------- block dangerous SQL ----------
    dangerous_keywords = [
        "drop", "delete", "insert", "update",
        "alter", "truncate", "create", "grant"
    ]

    for word in dangerous_keywords:
        if word in q_lower:
            raise Exception("Dangerous SQL detected.")

    # ---------- normalize whitespace ----------
    normalized = re.sub(r"\s+", " ", q_lower)

    # ---------- enforce correct table ----------
    if " from player_game_logs " not in normalized and not normalized.endswith(" from player_game_logs"):
        raise Exception("Query must use player_game_logs table.")

    # ---------- prevent joins (LLM hallucination) ----------
    if " join " in normalized:
        raise Exception("JOINs are not allowed.")

    # ---------- prevent SELECT * ----------
    if "select *" in normalized:
        raise Exception("SELECT * is not allowed.")

    # ---------- enforce PLAYER_ID filter ----------
    if "player_id" not in normalized:
        raise Exception("Query must filter by PLAYER_ID.")

    # ---------- prevent massive queries ----------
    if "limit" not in normalized:
        raise Exception("Query must include LIMIT.")

    return True