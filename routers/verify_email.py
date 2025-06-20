from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from db import insert_log

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/verify-email", response_class=HTMLResponse)
async def verify_email(
    request: Request,
    username: str = Query(...),
    risk_score: int = Query(...),
    reasons: str = Query(None)
):
    # ✅ Log email verification success
    await insert_log(
        ip_address="verified",
        location="verified",
        user_agent="verified",
        risk_score=10,
        is_suspicious=False,
        username=username,
        latitude=None,
        longitude=None,
        note="Email verification passed"
    )

    reason_list = reasons.split("|") if reasons else []

    return templates.TemplateResponse("verify_email.html", {
        "request": request,
        "token_validated": True,
        "username": username,
        "risk_score": risk_score,
        "reasons": reason_list
    })
