from starlette.requests import Request

LANGUAGES_LIST = ["en", "fr", "en_US", "fr_FR"]


def get_request_locale(request: Request) -> str:
    """
    Extrate the locale from the request

    :param request: incoming request
    :return:  locale
    """
    locale = (
        request.headers.get("locale", None)
        or request.path_params.get("locale", None)
        or request.query_params.get("locale", None)
        or "en_US"
    )

    if locale not in LANGUAGES_LIST:
        locale = "en_US"
    return locale
