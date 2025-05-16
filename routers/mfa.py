from fastapi import APIRouter, Request, Query, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import random

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Mock in-memory store (for PoC only)
mfa_store = {}

@router.get("/mfa/start", response_class=HTMLResponse)
async def start_mfa(request: Request, username: str = Query(...)):
    code = str(random.randint(100000, 999999))
    mfa_store[username] = code
    print(f"[MFA] Verification code for {username}: {code}")  # Simulate SMS/email delivery
    return templates.TemplateResponse("mfa_verify.html", {"request": request, "username": username})

@router.post("/mfa/verify", response_class=HTMLResponse)
async def verify_mfa(request: Request, username: str = Form(...), code: str = Form(...)):
    expected = mfa_store.get(username)
    if expected and code == expected:
        del mfa_store[username]
        return templates.TemplateResponse("login_xloc.html", {
            "request": request,
            "message": f"{username} authenticated after MFA",
            "location": "verified",
            "risk_score": 100,
            "is_suspicious": False,
        })
    return templates.TemplateResponse("mfa_verify.html", {
        "request": request,
        "username": username,
        "error": "Invalid code. Please try again."
    })
