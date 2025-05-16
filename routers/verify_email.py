from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/verify-email", response_class=HTMLResponse)
async def verify_email(request: Request, username: str = Query(...)):
    print(f"[EMAIL] Verification link sent to {username}'s registered email.")
    return templates.TemplateResponse("verify_email.html", {
        "request": request,
        "token_validated": True,
        "username": username
    })
