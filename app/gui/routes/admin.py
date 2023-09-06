from fastapi import APIRouter, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="./app/templates")

router = APIRouter()


@router.get("/list_endpoints/")
def list_endpoints(request: Request):
    url_list = [
        {"path": route.path, "name": route.name} for route in request.app.routes
    ]
    return url_list


@router.get("")
async def admin(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
