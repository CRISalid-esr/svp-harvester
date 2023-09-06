from fastapi import APIRouter, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="./templates")

router = APIRouter()

router.mount("/static", StaticFiles(directory="./static", html=True), name="static")


@router.get('')
async def admin(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
