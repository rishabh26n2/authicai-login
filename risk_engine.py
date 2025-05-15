import math
from datetime import datetime, timezone
from typing import Optional, Any, List


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


def extract_country(loc_str: str) -> str:
    """
    Extract the country portion from a location string like 'City, Country'.
    """
    if not loc_str or "," not in loc_str:
        return loc_str.strip()
    parts = loc_str.split(",")
    return parts[-1].strip()


def calculate_risk_score(
    ip: str,
    location: str,
    user_agent: str,
    last_login: Optional[Any] = None,
    curr_time: Optional[datetime] = None,
    curr_coords: Optional[tuple] = None,
    login_history: Optional[List[datetime]] = None,
    recent_attempts: Optional[int] = None
) -> int:
    """
    Compute a heuristic risk score (0–100) combining several rules:
      • Teleport anomaly:        +50 if implied speed > 500 km/h
      • Country change:          +20 if country differs from last login
      • Unknown Location:        +40
      • Suspicious user agents:  +30
      • Time-of-day outlier:     +10 if outside user's typical login hours
      • Day-of-week outlier:     +10 if outside user's typical login days
      • Burst/frequency spike:   +20 if recent_attempts >= 5
    """
    score = 0

    # Normalize current time to aware UTC
    now = curr_time or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    # 1) Teleportation check
    if last_login and curr_coords:
        try:
            last_ts  = last_login["timestamp"]
            last_lat = last_login["latitude"]
            last_lon = last_login["longitude"]
        except Exception:
            last_ts = last_lat = last_lon = None
        if last_ts and last_lat is not None and last_lon is not None:
            if last_ts.tzinfo is None:
                last_ts = last_ts.replace(tzinfo=timezone.utc)
            hours = max((now - last_ts).total_seconds() / 3600.0, 0.01)
            dist  = haversine(last_lat, last_lon, curr_coords[0], curr_coords[1])
            speed = dist / hours
            if speed > 500:
                score += 50

    # 2) Country change check
    last_loc_str = None
    if last_login:
        try:
            last_loc_str = last_login["location"]
        except Exception:
            last_loc_str = None
    if last_loc_str:
        last_country = extract_country(last_loc_str)
        curr_country = extract_country(location)
        if last_country and curr_country and last_country != curr_country:
            score += 20

    # 3) Unknown / failed geolocation
    if "Unknown" in location:
        score += 40

    # 4) Suspicious user agents
    ua = user_agent.lower()
    if any(tok in ua for tok in ("curl", "python", "wget")):
        score += 30

    # 5) Time-of-day outlier
    if login_history:
        hours_hist = [dt.astimezone(timezone.utc).hour for dt in login_history]
        if hours_hist:
            min_h, max_h = min(hours_hist), max(hours_hist)
            curr_h = now.hour
            if curr_h < min_h or curr_h > max_h:
                score += 10

    # 6) Day-of-week outlier
    if login_history:
        weekdays = [dt.astimezone(timezone.utc).weekday() for dt in login_history]
        if weekdays and now.weekday() not in set(weekdays):
            score += 10

    # 7) Burst/frequency spike
    if recent_attempts is not None and recent_attempts >= 5:
        score += 20

    return min(score, 100)


def is_suspicious_login(score: int) -> bool:
    """
    Flag logins with score >= 50 (any significant anomaly or higher) as suspicious.
    """
    return score >= 50
