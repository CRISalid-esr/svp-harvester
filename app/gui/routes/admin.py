from fastapi import APIRouter, Request

from app.gui.routes.templating import get_templating_engine
from app.i18n.get_request_locale import get_request_locale

I18N_DOMAIN = "admin"

router = APIRouter()


@router.get("")
async def overview(request: Request):
    """Return the overview page in the admin gui"""
    return get_templating_engine("admin", get_request_locale(request)).TemplateResponse(
        "index.html.jinja",
        {"request": request, "page": "overview", "locale": get_request_locale(request)},
    )


@router.get("/retrieve")
async def get_retrieve(request: Request):
    """Return the retrieve page in the admin gui"""
    return get_templating_engine("admin", get_request_locale(request)).TemplateResponse(
        "retrieve.html.jinja",
        {"request": request, "page": "retrieve", "locale": get_request_locale(request)},
    )


@router.get("/history")
async def get_history(request: Request):
    """Return the history page in the admin gui"""
    return get_templating_engine(
        I18N_DOMAIN, get_request_locale(request)
    ).TemplateResponse(
        "history.html.jinja",
        {"request": request, "page": "history", "locale": get_request_locale(request)},
    )


@router.get("/list_endpoints/")
def list_endpoints(request: Request):  # pragma: no cover
    """Convenience function to list all endpoints"""
    url_list = [
        {"path": route.path, "name": route.name} for route in request.app.routes
    ]
    return url_list
