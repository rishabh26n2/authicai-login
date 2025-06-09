import math
from datetime import datetime, timezone
from typing import Optional, Any, List, Tuple
import joblib
import pandas as pd
import shap
import numpy as np

USE_ML_MODEL = True
MODEL_PATH = "models/risk_model_v2.pkl"

model = None
explainer = None
preprocessor = None
classifier = None

# =======================
# Load ML model and SHAP
# =======================
try:
    model = joblib.load(MODEL_PATH)
    preprocessor = model.named_steps['pre']
    classifier = model.named_steps['clf']

    sample_df = pd.DataFrame([{
        "hour": 12,
        "weekday": 1,
        "latitude": 0.0,
        "longitude": 0.0,
        "user_agent": "browser",
        "country": "India",
        "ip_1": 1.0,
        "ip_2": 1.0
    }])
    background = preprocessor.transform(sample_df)
    explainer = shap.TreeExplainer(classifier, background, feature_perturbation="auto")
    print("✅ SHAP explainer initialized")

except Exception as e:
    print("⚠️ SHAP explainer init failed:", e)
    model = None
    USE_ML_MODEL = False
    explainer = None

# =======================
# Utilities
# =======================
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

# =======================
# ML-based Risk Scoring
# =======================
def calculate_risk_score_ml(features: dict) -> Tuple[int, List[str]]:
    try:
        df = pd.DataFrame([features])
        df = df.astype({
            "hour": float,
            "weekday": float,
            "latitude": float,
            "longitude": float,
            "ip_1": float,
            "ip_2": float,
            "user_agent": str,
            "country": str
        })

        score = model.predict_proba(df)[0][1] * 100
        reasons = []

        if explainer:
            transformed_df = preprocessor.transform(df)
            shap_values = explainer.shap_values(transformed_df)
            values = shap_values[1][0] if isinstance(shap_values, list) else shap_values[0]

            try:
                feature_names = preprocessor.get_feature_names_out()
            except:
                feature_names = [f"feature_{i}" for i in range(len(values))]

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
        print("Features passed:", features)
        return 0, ["ML model failed, fallback to rule-based"]

# =======================
# Rule-based Risk Scoring
# =======================
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

    # Impossible travel detection
    if last_login and curr_coords:
        try:
            last_ts = last_login.get("timestamp")
            last_lat = last_login.get("latitude")
            last_lon = last_login.get("longitude")

            if last_ts and last_ts.tzinfo is None:
                last_ts = last_ts.replace(tzinfo=timezone.utc)
            if last_ts and last_lat is not None and last_lon is not None:
                hours = max((now - last_ts).total_seconds() / 3600.0, 0.01)
                dist = haversine(last_lat, last_lon, curr_coords[0], curr_coords[1])
                speed = dist / hours
                if speed > 500:
                    score += 50
                    reasons.append(f"Impossible travel detected: {int(speed)} km/h")
        except Exception:
            pass

    # Country change detection
    last_country = extract_country(last_login.get("location", "")) if last_login else None
    curr_country = extract_country(location)
    if last_country and curr_country and last_country != curr_country:
        score += 20
        reasons.append(f"Country changed: {last_country} → {curr_country}")

    # Location failure
    if "Unknown" in location:
        score += 40
        reasons.append("Location could not be determined")

    # Suspicious user-agent
    ua = user_agent.lower()
    if any(tok in ua for tok in ("curl", "python", "wget")):
        score += 30
        reasons.append(f"Suspicious user-agent: {user_agent}")

    # Time and frequency anomalies
    if login_history:
        hours_hist = [dt.astimezone(timezone.utc).hour for dt in login_history]
        if hours_hist:
            if now.hour < min(hours_hist) or now.hour > max(hours_hist):
                score += 10
                reasons.append(f"Login at unusual hour: {now.hour}")
        weekdays = [dt.astimezone(timezone.utc).weekday() for dt in login_history]
        if now.weekday() not in set(weekdays):
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

# =======================
# Unified Scoring API
# =======================
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
            print("⚠️ ML failed, falling back to rules:", e)

    # Fallback or rule-based scoring
    score, reasons = calculate_risk_score_rules(
        ip, location, user_agent, last_login, curr_time, curr_coords, login_history, recent_attempts
    )
    return (score, reasons) if return_reasons else score

# =======================
# Flag suspicious score
# =======================
def is_suspicious_login(score: int) -> bool:
    return score >= 50
