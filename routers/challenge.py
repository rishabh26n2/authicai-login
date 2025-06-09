from fastapi import APIRouter, Request, Form, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from db import insert_log

router = APIRouter()
templates = Jinja2Templates(directory="templates")

CHALLENGE_ANSWER = "fluffy"

@router.get("/challenge-question", response_class=HTMLResponse)
async def challenge_page(
    request: Request,
    username: str = Query(...),
    risk_score: int = Query(...),
    reasons: str = Query(None)
):
    reason_list = reasons.split("|") if reasons else []
    return templates.TemplateResponse("challenge_question.html", {
        "request": request,
        "username": username,
        "risk_score": risk_score,
        "reasons": reason_list
    })

@router.post("/challenge-question/verify", response_class=HTMLResponse)
async def verify_answer(
    request: Request,
    username: str = Form(...),
    answer: str = Form(...),
    risk_score: int = Form(...),
    reasons: str = Form(...)
):
    reason_list = reasons.split("|") if reasons else []

    if answer.strip().lower() == CHALLENGE_ANSWER:
        # ✅ Log verification pass with score = 10
        await insert_log(
            ip_address="verified",
            location="verified",
            user_agent="verified",
            risk_score=10,
            is_suspicious=False,
            username=username,
            latitude=None,
            longitude=None,
            note="Security question passed"
        )

        return templates.TemplateResponse("login_xloc.html", {
            "request": request,
            "message": f"{username} authenticated after challenge!",
            "location": "verified",
            "risk_score": risk_score,  # original
            "is_suspicious": False,
            "use_ml": True,
            "reasons": reason_list     # original
        })

    # ❌ Incorrect answer
    return templates.TemplateResponse("challenge_question.html", {
        "request": request,
        "username": username,
        "error": "Incorrect answer. Try again.",
        "risk_score": risk_score,
        "reasons": reason_list
    })
