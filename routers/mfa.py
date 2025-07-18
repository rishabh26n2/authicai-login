from fastapi import APIRouter, Request, Query, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from db import insert_log
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# In-memory mock store
mfa_store = {}

@router.get("/mfa/start", response_class=HTMLResponse)
async def start_mfa(
    request: Request,
    username: str = Query(...),
    risk_score: int = Query(...),
    reasons: str = Query(None)
):
    import random
    code = str(random.randint(100000, 999999))
    mfa_store[username] = code
    print(f"[MFA] Verification code for {username}: {code}")
    reason_list = reasons.split("|") if reasons else []

    return templates.TemplateResponse("mfa_verify.html", {
        "request": request,
        "username": username,
        "otp": code,
        "risk_score": risk_score,
        "reasons": reason_list
    })

@router.post("/mfa/verify", response_class=HTMLResponse)
async def verify_mfa(
    request: Request,
    username: str = Form(...),
    code: str = Form(...),
    risk_score: int = Form(...),
    reasons: str = Form(...)
):
    expected = mfa_store.get(username)
    reason_list = reasons.split("|") if reasons else []

    if expected and code == expected:
        del mfa_store[username]
        # ✅ Log success with note
        await insert_log(
            ip_address="verified",
            location="verified",
            user_agent="verified",
            risk_score=10,
            is_suspicious=False,
            username=username,
            latitude=None,
            longitude=None,
            note="MFA passed"
        )
        return templates.TemplateResponse("login_xloc.html", {
            "request": request,
            "message": f"{username} authenticated after MFA",
            "location": "verified",
            "risk_score": risk_score,
            "is_suspicious": False,
            "use_ml": True,
            "reasons": reason_list
        })
    return templates.TemplateResponse("mfa_verify.html", {
        "request": request,
        "username": username,
        "error": "Invalid code. Please try again.",
        "risk_score": risk_score,
        "reasons": reason_list
    })
