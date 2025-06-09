from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from urllib.parse import urlencode

from db import (
    database,
    insert_log,
    fetch_last_login,
    fetch_login_history,
    count_recent_attempts
)
from context_collector import get_location_from_ip, get_location_from_coordinates
from risk_engine import calculate_risk_score
from policy_engine import evaluate_policy
from routers import mfa, challenge, verify_email

app = FastAPI()
app.include_router(mfa.router)
app.include_router(challenge.router)
app.include_router(verify_email.router)

templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login_xloc.html", {
        "request": request,
        "use_ml": True  # default to ML enabled
    })

@app.post("/login", response_class=HTMLResponse)
async def login(
    username: str = Form(...),
    password: str = Form(...),
    latitude: str = Form(None),
    longitude: str = Form(None),
    use_ml: str = Form("true"),
    request: Request = None
):
    # 1) Determine client IP
    xff = request.headers.get("x-forwarded-for")
    fallback = request.client.host
    ip_address = xff.split(",")[0].strip() if xff else fallback

    # 2) Capture user-agent
    user_agent = request.headers.get("user-agent", "Unknown")

    # 3) Get location from coordinates or fallback to IP
    ip_location_str, ip_coords = get_location_from_ip(ip_address)
    location = ip_location_str
    curr_coords = ip_coords

    if latitude and longitude:
        try:
            lat = float(latitude)
            lon = float(longitude)
            coord_based_location = get_location_from_coordinates(lat, lon)

            if coord_based_location != "Unknown Location":
                location = coord_based_location
            else:
                print("⚠️ Reverse geocoding failed. Falling back to IP-based location.")

            curr_coords = (lat, lon)
        except Exception as e:
            print(f"⚠️ Invalid coordinates provided: {latitude}, {longitude} → {e}")

    # 4) Historical login data
    last_login = await fetch_last_login(username)
    last_login = dict(last_login) if last_login else None  # ✅ FIXED HERE
    login_history = await fetch_login_history(username, limit=20)
    recent_attempts = await count_recent_attempts(username, seconds=60)

    # 5) Risk calculation
    now = datetime.utcnow()
    use_ml_bool = (use_ml == "true")
    risk_score, reasons = calculate_risk_score(
        ip=ip_address,
        location=location,
        user_agent=user_agent,
        last_login=last_login,
        curr_time=now,
        curr_coords=curr_coords,
        login_history=login_history,
        recent_attempts=recent_attempts,
        use_ml=use_ml_bool,
        return_reasons=True
    )

    # Add scoring method prefix
    scoring_method = "Scoring: ML" if use_ml_bool else "Scoring: Rule-Based"
    reasons = [scoring_method] + reasons if reasons else [scoring_method]
    note_str = " | ".join(reasons)

    # 6) Decide policy action
    policy_action = evaluate_policy(risk_score)

    # 7) Log the login
    await insert_log(
        ip_address=ip_address,
        location=location,
        user_agent=user_agent,
        risk_score=risk_score,
        is_suspicious=(policy_action != "allow"),
        username=username,
        latitude=curr_coords[0],
        longitude=curr_coords[1],
        note=note_str
    )

    # 8) Adaptive authentication response
    if policy_action == "allow":
        return templates.TemplateResponse("login_xloc.html", {
            "request": request,
            "message": username,
            "location": location,
            "risk_score": risk_score,
            "is_suspicious": False,
            "use_ml": use_ml_bool,
            "reasons": reasons
        })
    
    # Challenge or verification step
    query = urlencode({
        "username": username,
        "risk_score": risk_score,
        "reasons": "|".join(reasons)
    })
    if policy_action == "challenge":
        return RedirectResponse(f"/challenge-question?{query}", status_code=302)
    elif policy_action == "otp":
        return RedirectResponse(f"/mfa/start?{query}", status_code=302)
    elif policy_action == "otp_email":
        return RedirectResponse(f"/verify-email?{query}", status_code=302)

    # Block fallback
    return templates.TemplateResponse("login_xloc.html", {
        "request": request,
        "message": "Blocked due to high risk.",
        "location": location,
        "risk_score": risk_score,
        "is_suspicious": True,
        "use_ml": use_ml_bool,
        "reasons": reasons
    })
