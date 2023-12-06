from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse

from app.gui.routes.templating import get_templating_engine
from app.i18n.get_request_locale import get_request_locale

I18N_DOMAIN = "admin"
HISTORY_SUBPAGES = ["collect", "publication"]  # Update this list as you add subpages
router = APIRouter()


@router.get("")
async def overview(request: Request):
    """Return the overview page in the admin gui"""
    return get_templating_engine(I18N_DOMAIN, get_request_locale(request)).TemplateResponse(
        "overview.html.jinja",
        {"request": request, "page": "overview", "locale": get_request_locale(request)},
    )


@router.get("/retrieve")
async def get_retrieve(request: Request):
    """Return the retrieve page in the admin gui"""
    return get_templating_engine(I18N_DOMAIN, get_request_locale(request)).TemplateResponse(
        "retrieve.html.jinja",
        {"request": request, "page": "retrieve", "locale": get_request_locale(request)},
    )


@router.get("/history/{subpage}")
async def get_history(request: Request, subpage: str):
    """Return the history page in the admin gui"""
    if subpage not in HISTORY_SUBPAGES:
        # If invalid subpage, raise 404 error
        raise HTTPException(status_code=404, detail="Subpage not found")
    return get_templating_engine(
        I18N_DOMAIN, get_request_locale(request)
    ).TemplateResponse(
        "history.html.jinja",
        {"request": request, "page": "history", "subpage": f"{subpage}_history",
         "locale": get_request_locale(request)},
    )


@router.get("/history")
async def redirect_to_default_history_subpage(request: Request):
    """
    Redirects the user to the default History subpage specified in the URL.
    """
    # Fetch the current locale using provided function
    current_locale = get_request_locale(request)
    # Include it in your redirect URL
    return RedirectResponse(url=f"/admin/history/collect?locale={current_locale}", status_code=303)


@router.get("/settings")
async def get_settings(request: Request):
    """Return the settings page in the admin gui"""
    return get_templating_engine(I18N_DOMAIN, get_request_locale(request)).TemplateResponse(
        "base.html.jinja",
        {"request": request, "page": "settings", "locale": get_request_locale(request)},
    )


@router.get("/list_endpoints/")
def list_endpoints(request: Request):  # pragma: no cover
    """Convenience function to list all endpoints"""
    url_list = [
        {"path": route.path, "name": route.name} for route in request.app.routes
    ]
    return url_list
