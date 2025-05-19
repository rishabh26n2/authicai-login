from fastapi import APIRouter, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from db import insert_log

router = APIRouter()
templates = Jinja2Templates(directory="templates")

CHALLENGE_ANSWER = "fluffy"

@router.get("/challenge-question", response_class=HTMLResponse)
async def challenge_page(request: Request, username: str = Query(...)):
    return templates.TemplateResponse("challenge_question.html", {
        "request": request,
        "username": username
    })

@router.post("/challenge-question/verify", response_class=HTMLResponse)
async def verify_answer(request: Request, username: str = Form(...), answer: str = Form(...)):
    if answer.strip().lower() == CHALLENGE_ANSWER:
        # ✅ Log challenge success
        await insert_log(
            ip_address="verified",
            location="verified",
            user_agent="verified",
            risk_score=10,
            is_suspicious=False,
            username=username,
            latitude=None,
            longitude=None,
            note="Security question passed"  # ✅ Added note
        )
        return templates.TemplateResponse("login_xloc.html", {
            "request": request,
            "message": f"{username} authenticated after challenge!",
            "location": "verified",
            "risk_score": 10,
            "is_suspicious": False,
            "use_ml": True
        })
    return templates.TemplateResponse("challenge_question.html", {
        "request": request,
        "username": username,
        "error": "Incorrect answer. Try again."
    })
