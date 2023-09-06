from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="./app/templates")

router = APIRouter()


@router.get("")
async def admin(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/list_endpoints/")
def list_endpoints(request: Request):  # pragma: no cover
    """Convenience function to list all endpoints"""
    url_list = [
        {"path": route.path, "name": route.name} for route in request.app.routes
    ]
    return url_list
