# risk_engine.py

import math
from datetime import datetime
from typing import Optional, Any

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Compute great-circle distance between two points (in kilometers).
    """
    R = 6371.0  # Earth radius in km
    φ1, φ2 = math.radians(lat1), math.radians(lat2)
    Δφ = math.radians(lat2 - lat1)
    Δλ = math.radians(lon2 - lon1)
    a = math.sin(Δφ / 2) ** 2 + math.cos(φ1) * math.cos(φ2) * math.sin(Δλ / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def calculate_risk_score(
    ip: str,
    location: str,
    user_agent: str,
    last_login: Optional[Any]    = None,
    curr_time: Optional[datetime]= None,
    curr_coords: Optional[tuple] = None
) -> int:
    """
    Compute a heuristic risk score (0–100):
      • Unknown Location: +40
      • Outside India:     +20
      • Suspicious UA:     +30
      • Teleport anomaly:  +50 if implied speed > 500 km/h
    """
    score = 0

    # 1) Unknown / failed geolocation
    if "Unknown" in location:
        score += 40

    # 2) Outside India
    if "India" not in location:
        score += 20

    # 3) Suspicious User agents
    ua = user_agent.lower()
    if any(tok in ua for tok in ("curl", "python", "wget")):
        score += 30

    # 4) Teleportation check
    if last_login and curr_coords and curr_time:
        try:
            last_ts  = last_login["timestamp"]
            last_lat = last_login["latitude"]
            last_lon = last_login["longitude"]
        except (KeyError, TypeError):
            # Missing fields or wrong record shape → skip this check
            pass
        else:
            if last_ts and last_lat is not None and last_lon is not None:
                hours = (curr_time - last_ts).total_seconds() / 3600.0
                hours = max(hours, 0.01)
                dist  = haversine(last_lat, last_lon, curr_coords[0], curr_coords[1])
                speed = dist / hours
                if speed > 500:
                    score += 50

    return min(score, 100)

def is_suspicious_login(score: int) -> bool:
    """
    Flag logins with score >= 60 as suspicious.
    """
    return score >= 60
