from fastapi import APIRouter, Request

from app.config import get_app_settings
from app.gui.routes.templating import get_templating_engine
from app.i18n.get_request_locale import get_request_locale

I18N_DOMAIN = "admin"

router = APIRouter()


def with_api_informations():
    """
    Function to add api informations to the response for the admin gui
    API information will be printed in hidden inputs in the html
    where they are available for the javascript code
    to make api calls from the gui

    :return: decorated function
    """
    return {
        "api_host": get_app_settings().api_host,
        "api_path": f"{get_app_settings().api_prefix}/{get_app_settings().api_version}",
    }


def with_locale(request: Request):
    """
    Function to add locale to the response for the admin gui

    :return: decorated function
    """
    return {"locale": get_request_locale(request)}


@router.get("")
async def overview(request: Request):
    """Return the overview page in the admin gui"""
    return get_templating_engine("admin", get_request_locale(request)).TemplateResponse(
        "overview.html.jinja",
        {"request": request, "page": "overview"}
        | with_locale(request)
        | with_api_informations(),
    )


@router.get("/retrieve")
async def get_retrieve(request: Request):
    """Return the retrieve page in the admin gui"""
    return get_templating_engine("admin", get_request_locale(request)).TemplateResponse(
        "retrieve.html.jinja",
        {"request": request, "page": "retrieve"}
        | with_locale(request)
        | with_api_informations(),
    )


@router.get("/history")
async def get_history(request: Request):
    """Return the history page in the admin gui"""
    return get_templating_engine(
        I18N_DOMAIN, get_request_locale(request)
    ).TemplateResponse(
        "history.html.jinja",
        {"request": request, "page": "history"}
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
