import math
from datetime import datetime, timezone
from typing import Optional, Any, List, Tuple
import joblib
import pandas as pd
import shap

USE_ML_MODEL = True
MODEL_PATH = "models/risk_model_v2.pkl"

try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    print("\u26a0\ufe0f Failed to load ML model:", e)
    model = None
    USE_ML_MODEL = False

explainer = None
preprocessor = None
classifier = None

if model:
    try:
        preprocessor = model.named_steps['pre']
        classifier = model.named_steps['clf']

        sample_raw = pd.DataFrame([{
            "hour": 12,
            "weekday": 1,
            "latitude": 0.0,
            "longitude": 0.0,
            "user_agent": "browser",
            "country": "India",
            "ip_1": 1.0,
            "ip_2": 1.0
        }])
        
        sample_transformed = preprocessor.transform(sample_raw)
        explainer = shap.TreeExplainer(
            classifier,
            data=sample_transformed,
            feature_perturbation="auto"
        )

        print("\u2705 SHAP TreeExplainer initialized")

    except Exception as e:
        print("\u26a0\ufe0f SHAP explainer init failed:", e)
        explainer = None

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    φ1, φ2 = math.radians(lat1), math.radians(lat2)
    Δφ = math.radians(lat2 - lat1)
    Δλ = math.radians(lon2 - lon1)
    a = math.sin(Δφ / 2)**2 + math.cos(φ1) * math.cos(φ2) * math.sin(Δλ / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def extract_country(loc_str: str) -> str:
    if not loc_str or "," not in loc_str:
        return loc_str.strip()
    return loc_str.split(",")[-1].strip()

def calculate_risk_score_ml(features: dict) -> Tuple[int, List[str]]:
    try:
        df = pd.DataFrame([features])
        
        # Run prediction through pipeline (it handles preprocessing)
        score = model.predict_proba(df)[0][1] * 100
        reasons = []

        if explainer:
            # Run only the preprocessor to transform input
            transformed_df = model.named_steps['pre'].transform(df)
            shap_values = explainer(transformed_df)
            values = shap_values.values[0]
            feature_names = shap_values.feature_names
            top_contributors = sorted(
                zip(feature_names, values), key=lambda x: abs(x[1]), reverse=True
            )[:3]
            for feat, val in top_contributors:
                reasons.append(f"{feat} contributed ({val:+.2f})")
        else:
            reasons.append("SHAP not available")

        return int(score), reasons

    except Exception as e:
        print("⚠️ ML model prediction failed:", e)
        return 0, ["ML model failed, fallback to rule-based"]

def calculate_risk_score_rules(
    ip: str,
    location: str,
    user_agent: str,
    last_login: Optional[Any] = None,
    curr_time: Optional[datetime] = None,
    curr_coords: Optional[tuple] = None,
    login_history: Optional[List[datetime]] = None,
    recent_attempts: Optional[int] = None
) -> Tuple[int, List[str]]:
    score = 0
    reasons = []
    now = curr_time or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    if last_login and curr_coords:
        try:
            last_ts = last_login["timestamp"]
            last_lat = last_login["latitude"]
            last_lon = last_login["longitude"]
            if last_ts.tzinfo is None:
                last_ts = last_ts.replace(tzinfo=timezone.utc)
            hours = max((now - last_ts).total_seconds() / 3600.0, 0.01)
            dist = haversine(last_lat, last_lon, curr_coords[0], curr_coords[1])
            speed = dist / hours
            if speed > 500:
                score += 50
                reasons.append(f"Impossible travel detected: {int(speed)} km/h")
        except Exception:
            pass

    last_country = extract_country(last_login.get("location", "")) if last_login else None
    curr_country = extract_country(location)
    if last_country and curr_country and last_country != curr_country:
        score += 20
        reasons.append(f"Country changed: {last_country} → {curr_country}")

    if "Unknown" in location:
        score += 40
        reasons.append("Location could not be determined")

    ua = user_agent.lower()
    if any(tok in ua for tok in ("curl", "python", "wget")):
        score += 30
        reasons.append(f"Suspicious user-agent: {user_agent}")

    if login_history:
        hours_hist = [dt.astimezone(timezone.utc).hour for dt in login_history]
        if hours_hist:
            min_h, max_h = min(hours_hist), max(hours_hist)
            if now.hour < min_h or now.hour > max_h:
                score += 10
                reasons.append(f"Login at unusual hour: {now.hour}")
        weekdays = [dt.astimezone(timezone.utc).weekday() for dt in login_history]
        if weekdays and now.weekday() not in set(weekdays):
            score += 10
            reasons.append("Login on unusual day of week")

    if recent_attempts is not None:
        if recent_attempts >= 5:
            score += 20
            reasons.append("Multiple login attempts detected")
        elif recent_attempts >= 3:
            score += 10
            reasons.append("Login bursts in short period")

    return min(score, 100), reasons

def calculate_risk_score(
    ip: str,
    location: str,
    user_agent: str,
    last_login: Optional[Any] = None,
    curr_time: Optional[datetime] = None,
    curr_coords: Optional[tuple] = None,
    login_history: Optional[List[datetime]] = None,
    recent_attempts: Optional[int] = None,
    use_ml: bool = True,
    return_reasons: bool = False
) -> Any:
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
            score, reasons = calculate_risk_score_ml(features)
            return (score, reasons) if return_reasons else score
        except Exception as e:
            print("\u26a0\ufe0f ML failed, using rules:", e)

    score, reasons = calculate_risk_score_rules(
        ip, location, user_agent, last_login, curr_time, curr_coords, login_history, recent_attempts
    )
    return (score, reasons) if return_reasons else score

def is_suspicious_login(score: int) -> bool:
    return score >= 50
