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
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from db import database, insert_log
from context_collector import get_location_from_ip, get_location_from_coordinates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Serve login form
@app.get("/", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login_xloc.html", {"request": request})

# Handle login submission (browser geolocation preferred, IP fallback)
@app.post("/login")
async def login(
    username: str    = Form(...),
    password: str    = Form(...),
    latitude: str    = Form(""),   # accept empty by default
    longitude: str   = Form(""),   # accept empty by default
    request: Request = None
):
    # 1) Extract client IP (first entry of X-Forwarded-For or fallback)
    raw_xff = request.headers.get("x-forwarded-for")
    fallback_ip = request.client.host
    ip = raw_xff.split(",")[0].strip() if raw_xff else fallback_ip

    user_agent = request.headers.get("user-agent", "Unknown")

    # 2) Determine location
    if latitude != "" and longitude != "":
        try:
            lat = float(latitude)
            lon = float(longitude)
            location = get_location_from_coordinates(lat, lon)
        except ValueError:
            location = get_location_from_ip(ip)
    else:
        location = get_location_from_ip(ip)

    # 3) Logging to console
    print("---- Login Attempt ----")
    print("Username:", username)
    print("Final IP Used:", ip)
    print("Latitude field:", repr(latitude), "Longitude field:", repr(longitude))
    print("Location:", location)
    print("User-Agent:", user_agent)

    # 4) Store in database
    await insert_log(ip, location, user_agent)

    # 5) Render response
    return templates.TemplateResponse("login_xloc.html", {
        "request": request,
        "message": f"Welcome {username}!",
        "location": location
    })
