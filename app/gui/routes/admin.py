import gettext
import os

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

current_locale = "fr_FR"
locale_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "locales")
gnu_translations = gettext.translation(
    domain="admin", localedir=locale_path, languages=[current_locale]
)
gnu_translations.install()

templates = Jinja2Templates(
    directory="./app/templates",
    extensions=["jinja2.ext.i18n"],
)
env = templates.env
env.install_gettext_translations(gnu_translations, newstyle=True)

router = APIRouter()


@router.get("")
async def overview(request: Request):
    """Return the overview page in the admin gui"""
    return templates.TemplateResponse(
        "index.html.jinja", {"request": request, "page": "overview"}
    )


@router.get("/retrieve")
async def get_retrieve(request: Request):
    """Return the retrieve page in the admin gui"""
    return templates.TemplateResponse(
        "retrieve.html.jinja", {"request": request, "page": "retrieve"}
    )


@router.get("/history")
async def get_history(request: Request):
    """Return the history page in the admin gui"""
    return templates.TemplateResponse(
        "history.html.jinja", {"request": request, "page": "history"}
    )


@router.get("/list_endpoints/")
def list_endpoints(request: Request):  # pragma: no cover
    """Convenience function to list all endpoints"""
    url_list = [
        {"path": route.path, "name": route.name} for route in request.app.routes
    ]
    return url_list
