from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter()
templates = Jinja2Templates(directory="templates")



@router.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    """Página de inicio con enlace a login."""
    return templates.TemplateResponse("login.html", {"request": request})
