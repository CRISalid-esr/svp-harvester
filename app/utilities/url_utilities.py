import re


def is_web_url(url: str) -> bool:
    """
    Check that the value is a valid url beginning by http or https,
    with a domain name (no IP address)
    :param url: URL to check
    :return: True if the URL is valid, False otherwise
    """
    url_regex = re.compile(
        r"^(https?://)?"  # http:// or https://
        r"(([A-Za-z0-9-]+\.)+[A-Za-z]{2,6})"  # domain
        r"(/[A-Za-z0-9-._~:/?#[\]@!$&\'()*+,;=]*)?$"  # path and query
    )
    return re.match(url_regex, url) is not None
