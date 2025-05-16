from fastapi import APIRouter, Request, Form, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Hardcoded challenge answers (for demo only)
EXPECTED_ANSWER = "shadow"  # or anything you like


@router.get("/challenge-question", response_class=HTMLResponse)
async def challenge_question(request: Request, username: str = Query(...)):
    return templates.TemplateResponse("challenge_question.html", {
        "request": request,
        "username": username
    })

@router.post("/challenge-question/verify", response_class=HTMLResponse)
async def verify_challenge(request: Request, username: str = Form(...), answer: str = Form(...)):
    if answer.strip().lower() == EXPECTED_ANSWER.lower():
        return templates.TemplateResponse("login_xloc.html", {
            "request": request,
            "message": f"{username} authenticated after challenge",
            "location": "verified",
            "risk_score": 10,
            "is_suspicious": False,
        })
    return templates.TemplateResponse("challenge_question.html", {
        "request": request,
        "username": username,
        "error": "Incorrect answer. Please try again."
    })

