from fastapi import APIRouter, Request

from app.gui.routes.templating import get_templating_engine

I18N_DOMAIN = "admin"

router = APIRouter()


@router.get("")
async def overview(request: Request):
    """Return the overview page in the admin gui"""
    return get_templating_engine("admin", request.state.locale).TemplateResponse(
        "index.html.jinja", {"request": request, "page": "overview", "locale": request.state.locale}
    )


@router.get("/retrieve")
async def get_retrieve(request: Request):
    """Return the retrieve page in the admin gui"""
    return get_templating_engine("admin", request.state.locale).TemplateResponse(
        "retrieve.html.jinja",
        {"request": request, "page": "retrieve", "locale": request.state.locale}
    )


@router.get("/history")
async def get_history(request: Request):
    """Return the history page in the admin gui"""
    return get_templating_engine(I18N_DOMAIN, request.state.locale).TemplateResponse(
        "history.html.jinja",
        {"request": request, "page": "history", "locale": request.state.locale}
    )


@router.get("/list_endpoints/")
def list_endpoints(request: Request):  # pragma: no cover
    """Convenience function to list all endpoints"""
    url_list = [
        {"path": route.path, "name": route.name} for route in request.app.routes
    ]
    return url_list
