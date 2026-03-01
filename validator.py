# validator.py
import re

def validate_sql(query: str):
    q = query.strip()
    q_lower = q.lower()

    if not q_lower.startswith("select"):
        raise Exception("Only SELECT queries allowed.")

    if ";" in q[:-1]:
        raise Exception("Multiple statements not allowed.")

    dangerous_keywords = ["drop", "delete", "insert", "update", "alter", "pragma"]
    for word in dangerous_keywords:
        if word in q_lower:
            raise Exception("Dangerous SQL detected.")

    # ✅ allow newlines/extra spaces
    normalized = re.sub(r"\s+", " ", q_lower)
    if " from games " not in normalized and not normalized.endswith(" from games"):
        raise Exception("Query must select from games table.")