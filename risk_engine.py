import math
from datetime import datetime, timezone
from typing import Optional, Any, List
import joblib
import os
import pandas as pd

# Toggle: switch to ML or fallback to rules
USE_ML_MODEL = True
MODEL_PATH = "models/risk_model_v2.pkl"

try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    print("⚠️ Failed to load ML model:", e)
    model = None
    USE_ML_MODEL = False

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    φ1, φ2 = math.radians(lat1), math.radians(lat2)
    Δφ = math.radians(lat2 - lat1)
    Δλ = math.radians(lon2 - lon1)
    a = math.sin(Δφ / 2) ** 2 + math.cos(φ1) * math.cos(φ2) * math.sin(Δλ / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def extract_country(loc_str: str) -> str:
    if not loc_str or "," not in loc_str:
        return loc_str.strip()
    return loc_str.split(",")[-1].strip()

def calculate_risk_score_ml(features: dict) -> int:
    try:
        df = pd.DataFrame([features])
        score = model.predict_proba(df)[0][1] * 100  # Get probability for class 1
        return int(score)
    except Exception as e:
        print("⚠️ ML model prediction failed:", e)
        return 0

def calculate_risk_score_rules(
    ip: str,
    location: str,
    user_agent: str,
    last_login: Optional[Any] = None,
    curr_time: Optional[datetime] = None,
    curr_coords: Optional[tuple] = None,
    login_history: Optional[List[datetime]] = None,
    recent_attempts: Optional[int] = None
) -> int:
    score = 0
    now = curr_time or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

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

    last_loc_str = None
    if last_login:
        try:
            last_loc_str = last_login["location"]
        except Exception:
            pass
    if last_loc_str:
        last_country = extract_country(last_loc_str)
        curr_country = extract_country(location)
        if last_country and curr_country and last_country != curr_country:
            score += 20

    if "Unknown" in location:
        score += 40

    ua = user_agent.lower()
    if any(tok in ua for tok in ("curl", "python", "wget")):
        score += 30

    if login_history:
        hours_hist = [dt.astimezone(timezone.utc).hour for dt in login_history]
        if hours_hist:
            min_h, max_h = min(hours_hist), max(hours_hist)
            if now.hour < min_h or now.hour > max_h:
                score += 10
        weekdays = [dt.astimezone(timezone.utc).weekday() for dt in login_history]
        if weekdays and now.weekday() not in set(weekdays):
            score += 10

    if recent_attempts is not None:
        if recent_attempts >= 5:
            score += 20
        elif recent_attempts >= 3:
            score += 10

    return min(score, 100)

def calculate_risk_score(
    ip: str,
    location: str,
    user_agent: str,
    last_login: Optional[Any] = None,
    curr_time: Optional[datetime] = None,
    curr_coords: Optional[tuple] = None,
    login_history: Optional[List[datetime]] = None,
    recent_attempts: Optional[int] = None,
    use_ml: bool = True  # ✅ NEW
) -> int:
    if use_ml and model and curr_coords:
        try:
            features = {
                "hour": curr_time.hour,
                "weekday": curr_time.weekday(),
                "latitude": curr_coords[0],
                "longitude": curr_coords[1],
                "user_agent": user_agent,
                "country": extract_country(location),
                "ip_1": float(ip.split(".")[0]),
                "ip_2": float(ip.split(".")[1]),
            }
            return calculate_risk_score_ml(features)
        except Exception as e:
            print("⚠️ ML failed, using rules:", e)

    return calculate_risk_score_rules(
        ip, location, user_agent, last_login, curr_time, curr_coords, login_history, recent_attempts
    )

def is_suspicious_login(score: int) -> bool:
    return score >= 50
