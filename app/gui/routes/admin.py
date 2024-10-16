from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse

from app.config import get_app_settings
from app.gui.routes.templating import get_templating_engine
from app.i18n.get_request_locale import get_request_locale

I18N_DOMAIN = "admin"
HISTORY_SUBPAGES = ["collection", "publication"]  # Update this list as you add subpages
router = APIRouter()


def with_api_informations():
    """
    Function to add api informations to the response for the admin gui.
    API information will be printed in hidden inputs in the HTML
    where they are available for the JavaScript code to make API calls from the GUI.

    Now also includes Git branch and Git commit ID information.

    :return: dict containing API informations and Git metadata
    """
    settings = get_app_settings()
    return {
        "api_host": settings.api_host,
        "api_path": f"{settings.api_prefix}/{settings.api_version}",
        "institution_name": settings.institution_name,
        "git_commit": settings.git_commit,
        "git_branch": settings.git_branch,
        "docker_digest": settings.docker_digest,
    }


def with_locale(request: Request):
    """
    Function to add locale to the response for the admin gui
    :param request: request object
    :return: dict containing locale
    """
    return {"locale": get_request_locale(request)}


@router.get("")
async def overview(request: Request):
    """Return the overview page in the admin gui"""
    return get_templating_engine(
        I18N_DOMAIN, get_request_locale(request)
    ).TemplateResponse(
        "overview.html.jinja",
        {"request": request, "page": "overview"}
        | with_locale(request)
        | with_api_informations(),
    )


@router.get("/retrieve")
async def get_retrieve(request: Request):
    """Return the retrieve page in the admin gui"""
    return get_templating_engine(
        I18N_DOMAIN, get_request_locale(request)
    ).TemplateResponse(
        "retrieve.html.jinja",
        {"request": request, "page": "retrieve"}
        | with_locale(request)
        | with_api_informations(),
    )


@router.get("/history/{subpage}")
async def get_history(request: Request, subpage: str):
    """Return the history page in the admin gui"""
    if subpage not in HISTORY_SUBPAGES:
        raise HTTPException(status_code=404, detail="Subpage not found")
    return get_templating_engine(
        I18N_DOMAIN, get_request_locale(request)
    ).TemplateResponse(
        "history.html.jinja",
        {
            "request": request,
            "page": "history",
            "subpage": f"{subpage}_history",
        }
        | with_locale(request)
        | with_api_informations(),
    )


@router.get("/history")
async def redirect_to_default_history_subpage(request: Request):
    """
    Redirects the user to the default History subpage specified in the URL.
    """
    # Fetch the current locale using provided function
    current_locale = get_request_locale(request)
    # Include it in your redirect URL
    return RedirectResponse(
        url=f"/admin/history/collection?locale={current_locale}", status_code=303
    )


@router.get("/settings")
async def get_settings(request: Request):
    """Return the settings page in the admin gui"""
    return get_templating_engine(
        I18N_DOMAIN, get_request_locale(request)
    ).TemplateResponse(
        "base.html.jinja",
        {"request": request, "page": "settings"}
        | with_locale(request)
        | with_api_informations(),
    )


@router.get("/list_endpoints/")
def list_endpoints(request: Request):  # pragma: no cover
    """Convenience function to list all endpoints"""
    url_list = [
        {"path": route.path, "name": route.name} for route in request.app.routes
    ]
    return url_list
