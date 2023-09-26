from starlette.requests import Request

LANGUAGES_LIST = ["en", "fr", "en_US", "fr_FR"]


async def i18n_middleware(request: Request, call_next):
    """
    Middleware to set the locale in the request state

    :param request: incoming request
    :param call_next: next call in the chain
    :return:
    """
    locale = (
        request.headers.get("locale", None)
        or request.path_params.get("locale", None)
        or request.query_params.get("locale", None)
        or "en_US"
    )

    if locale not in LANGUAGES_LIST:
        locale = "en_US"
    request.state.locale = locale

    return await call_next(request)
