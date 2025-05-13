# risk_engine.py

def calculate_risk_score(ip: str, location: str, user_agent: str) -> int:
    """
    Compute a simple heuristic risk score (0–100):
    - Unknown Location: +40
    - Outside India: +20
    - Suspicious User-Agent (curl, python, wget): +30
    """
    score = 0

    # Unknown or failed geolocation
    if "Unknown" in location:
        score += 40

    # Location outside India
    if "India" not in location:
        score += 20

    # Suspicious clients
    ua = user_agent.lower()
    if any(token in ua for token in ("curl", "python", "wget")):
        score += 30

    return min(score, 100)


def is_suspicious_login(score: int) -> bool:
    """
    Flag logins with score >= 60 as suspicious.
    """
    return score >= 60
