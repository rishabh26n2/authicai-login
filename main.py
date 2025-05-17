# from fastapi import FastAPI, Request, Form
# from fastapi.responses import HTMLResponse
# from fastapi.templating import Jinja2Templates
# from starlette.middleware.sessions import SessionMiddleware
# from starlette.responses import RedirectResponse
# from db import database, insert_log
# import socket

# app = FastAPI()

# templates = Jinja2Templates(directory="templates")

# @app.on_event("startup")
# async def startup():
#     await database.connect()

# @app.on_event("shutdown")
# async def shutdown():
#     await database.disconnect()

# @app.get("/", response_class=HTMLResponse)
# async def login_form(request: Request):
#     return templates.TemplateResponse("login.html", {"request": request})

# @app.post("/login")
# async def login(username: str = Form(...), password: str = Form(...), request: Request = None):
#     ip = request.client.host
#     user_agent = request.headers.get("user-agent", "Unknown")
#     location = "Dummy Location"  # You can use geolocation logic here

#     await insert_log(ip, location, user_agent)
#     return {"message": f"Welcome {username}!"}

#main.py

# from context_collector import get_location_from_ip  # new import

# from fastapi import FastAPI, Request, Form
# from fastapi.responses import HTMLResponse
# from fastapi.templating import Jinja2Templates
# from starlette.middleware.sessions import SessionMiddleware
# from starlette.responses import RedirectResponse
# from db import database, insert_log
# import requests

# app = FastAPI()

# templates = Jinja2Templates(directory="templates")

# # Geolocation API URL and key (replace with actual API key)
# GEOLOCATION_API_URL = "http://api.ipstack.com/"
# API_KEY = "YOUR_API_KEY"  # Replace with your actual API key

# @app.on_event("startup")
# async def startup():
#     await database.connect()

# @app.on_event("shutdown")
# async def shutdown():
#     await database.disconnect()

# @app.get("/", response_class=HTMLResponse)
# async def login_form(request: Request):
#     return templates.TemplateResponse("login.html", {"request": request})

# # Function to get location using IP address
# def get_location_from_ip(ip_address: str) -> str:
#     try:
#         response = requests.get(f"{GEOLOCATION_API_URL}{ip_address}?access_key={API_KEY}")
#         response.raise_for_status()  # Raise an exception if the API call fails
#         data = response.json()
#         country = data.get("country_name")
#         city = data.get("city")

#         if country and city:
#             return f"{city}, {country}"
#         else:
#             return "Unknown Location"
#     except requests.RequestException:
#         return "Unknown Location"

# @app.post("/login")
# async def login(username: str = Form(...), password: str = Form(...), request: Request = None):
#     ip = request.client.host
#     user_agent = request.headers.get("user-agent", "Unknown")
#     location = get_location_from_ip(ip)

#     print("---- Login Attempt ----")
#     print("Username:", username)
#     print("IP Address:", ip)
#     print("Location:", location)
#     print("User-Agent:", user_agent)

#     await insert_log(ip, location, user_agent)

#     return {"message": f"Welcome {username}!"}


############################################################################################
### Working with location update ###########################################################
############################################################################################

# from fastapi import FastAPI, Request, Form
# from db import database, insert_log
# from context_collector import get_location_from_ip

# app = FastAPI()

# @app.on_event("startup")
# async def startup():
#     await database.connect()

# @app.on_event("shutdown")
# async def shutdown():
#     await database.disconnect()

# @app.post("/login")
# async def login(username: str = Form(...), password: str = Form(...), request: Request = None):
#     ip = request.client.host
#     user_agent = request.headers.get("user-agent", "Unknown")
#     location = get_location_from_ip("8.8.8.8")  # test IP

#     print("---- Login Attempt ----")
#     print("Username:", username)
#     print("IP Address:", ip)
#     print("Location:", location)
#     print("User-Agent:", user_agent)

#     await insert_log(ip, location, user_agent)
#     return {"message": f"Welcome {username}!"}



############################################################################################
### Working with location and location allow pop-up    #####################################
############################################################################################


# from fastapi import FastAPI, Request, Form
# from fastapi.responses import HTMLResponse
# from fastapi.templating import Jinja2Templates
# from db import database, insert_log
# from context_collector import get_location_from_ip

# app = FastAPI()
# templates = Jinja2Templates(directory="templates")

# @app.on_event("startup")
# async def startup():
#     await database.connect()

# @app.on_event("shutdown")
# async def shutdown():
#     await database.disconnect()

# # Serve login form
# @app.get("/", response_class=HTMLResponse)
# async def login_form(request: Request):
#     return templates.TemplateResponse("login.html", {"request": request})

# # Handle login submission
# @app.post("/login")
# async def login(
#     username: str = Form(...),
#     password: str = Form(...),
#     latitude: float = Form(None),
#     longitude: float = Form(None),
#     request: Request = None
# ):
#     # Get client IP (from proxy if deployed behind one)
#     ip = request.headers.get("x-forwarded-for", request.client.host)
#     user_agent = request.headers.get("user-agent", "Unknown")

#     # Determine location
#     if latitude is not None and longitude is not None:
#         location = f"{latitude}, {longitude} (from browser)"
#     else:
#         location = get_location_from_ip(ip)

#     print("---- Login Attempt ----")
#     print("Username:", username)
#     print("IP Address:", ip)
#     print("Location:", location)
#     print("User-Agent:", user_agent)

#     # Store login attempt in DB
#     await insert_log(ip, location, user_agent)

#     return templates.TemplateResponse("login.html", {
#         "request": request,
#         "message": f"Welcome {username}!",
#         "location": location
#     })

############################################################################################
### Working with location and location allow pop-up  and gio-location extracted ############
############################################################################################


# from fastapi import FastAPI, Request, Form
# from fastapi.responses import HTMLResponse
# from fastapi.templating import Jinja2Templates
# from db import database, insert_log
# from context_collector import get_location_from_ip, get_location_from_coordinates  # 👈 new import

# app = FastAPI()
# templates = Jinja2Templates(directory="templates")

# @app.on_event("startup")
# async def startup():
#     await database.connect()

# @app.on_event("shutdown")
# async def shutdown():
#     await database.disconnect()

# # Serve login form
# @app.get("/", response_class=HTMLResponse)
# async def login_form(request: Request):
#     return templates.TemplateResponse("login.html", {"request": request})

# # Handle login submission
# @app.post("/login")
# async def login(
#     username: str = Form(...),
#     password: str = Form(...),
#     latitude: float = Form(None),
#     longitude: float = Form(None),
#     request: Request = None
# ):
#     # Get client IP
#     ip = request.headers.get("x-forwarded-for", request.client.host)
#     user_agent = request.headers.get("user-agent", "Unknown")

#     # Determine location: first try browser coordinates
#     if latitude is not None and longitude is not None:
#         location = get_location_from_coordinates(latitude, longitude)
#     else:
#         location = get_location_from_ip(ip)

#     print("---- Login Attempt ----")
#     print("Username:", username)
#     print("IP Address:", ip)
#     print("Location:", location)
#     print("User-Agent:", user_agent)

#     # Insert log in DB
#     await insert_log(ip, location, user_agent)

#     return templates.TemplateResponse("login.html", {
#         "request": request,
#         "message": f"Welcome {username}!",
#         "location": location
#     })

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime

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
    return templates.TemplateResponse("login_xloc.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login(
    username: str = Form(...),
    password: str = Form(...),
    latitude: str = Form(None),
    longitude: str = Form(None),
    use_ml: str = Form("true"),  # ✅ Checkbox toggle
    request: Request = None
):
    # 1) Determine client IP
    xff = request.headers.get("x-forwarded-for")
    fallback = request.client.host
    ip_address = xff.split(",")[0].strip() if xff else fallback

    # 2) Capture user-agent
    user_agent = request.headers.get("user-agent", "Unknown")

    # 3) Get IP-based and/or browser-provided coordinates
    ip_location_str, ip_coords = get_location_from_ip(ip_address)
    if latitude and longitude:
        lat, lon = float(latitude), float(longitude)
        curr_coords = (lat, lon)
        location = get_location_from_coordinates(lat, lon)
    else:
        curr_coords = ip_coords
        location = ip_location_str

    # 4) Get login history
    last_login = await fetch_last_login(username)
    login_history = await fetch_login_history(username, limit=20)
    recent_attempts = await count_recent_attempts(username, seconds=60)

    # 5) Risk scoring
    now = datetime.utcnow()
    risk_score = calculate_risk_score(
        ip=ip_address,
        location=location,
        user_agent=user_agent,
        last_login=last_login,
        curr_time=now,
        curr_coords=curr_coords,
        login_history=login_history,
        recent_attempts=recent_attempts,
        use_ml=(use_ml == "true")  # ✅ Form toggle interpreted
    )

    # 6) Determine policy action
    policy_action = evaluate_policy(risk_score)

    # 7) Store log
    await insert_log(
        ip_address=ip_address,
        location=location,
        user_agent=user_agent,
        risk_score=risk_score,
        is_suspicious=(policy_action != "allow"),
        username=username,
        latitude=curr_coords[0],
        longitude=curr_coords[1]
    )

    # 8) Respond based on policy
    if policy_action == "allow":
        return templates.TemplateResponse("login_xloc.html", {
            "request": request,
            "message": username,
            "location": location,
            "risk_score": risk_score,
            "is_suspicious": False,
        })
    elif policy_action == "challenge":
        return RedirectResponse(f"/challenge-question?username={username}", status_code=302)
    elif policy_action == "otp":
        return RedirectResponse(f"/mfa/start?username={username}", status_code=302)
    elif policy_action == "otp_email":
        return RedirectResponse(f"/verify-email?username={username}", status_code=302)
    else:
        return templates.TemplateResponse("login_xloc.html", {
            "request": request,
            "message": "Blocked due to high risk.",
            "location": location,
            "risk_score": risk_score,
            "is_suspicious": True,
        })
