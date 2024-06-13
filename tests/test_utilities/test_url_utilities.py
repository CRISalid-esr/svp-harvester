import pytest

from app.utilities.url_utilities import is_web_url


def test_is_web_url():
    """
    Test that is_web_url returns True for valid URLs and False for invalid URLs
    """
    assert is_web_url("http://www.example.com")
    assert is_web_url("https://www.example.com")
    assert is_web_url("http://example.com")
    assert is_web_url("https://example.com")
    assert is_web_url("http://example.co.uk")
    assert is_web_url("https://example.co.uk")
    assert is_web_url("http://example.com.au")
    assert is_web_url("https://example.com.au")
    assert is_web_url("http://example.com/page")
    assert is_web_url("https://example.com/page")
    assert is_web_url("http://example.com/page.html")
    assert is_web_url("https://example.com/page.html")
    assert is_web_url("http://example.com/page.html?query=string")
    assert is_web_url("https://example.com/page.html?query=string")
    assert is_web_url("http://example.com/page.html#fragment")
    assert is_web_url("https://example.com/page.html#fragment")
    assert is_web_url("http://example.com/page.html?query=string#fragment")
    assert is_web_url("https://example.com/page.html?query=string#fragment")
    assert not is_web_url("http://")
    assert not is_web_url("https://")
    assert not is_web_url("http://example")
    assert not is_web_url("https://example")
    assert not is_web_url("http://example.")
    assert not is_web_url("https://example.")
    assert not is_web_url("http://example.c")
    assert not is_web_url("https://example.c")
    assert not is_web_url("http://example.com.")
    assert not is_web_url("https://example.com.")
    assert not is_web_url("http://example.com#/")
    assert not is_web_url("https://example.com!/")
    assert is_web_url("http://example.com/page.html?query=string/")
    assert is_web_url("https://example.com/page.html?query=string/")
    assert is_web_url("http://example.com/page.html#fragment/")
    assert is_web_url("https://example.com/page.html#fragment/")
    assert is_web_url("http://example.com/page.html?query=string#fragment/")
    assert is_web_url("https://example.com/page.html?query=string#fragment/")
    assert not is_web_url("http://example.com:80")
    assert not is_web_url("https://example.com:443")
    assert not is_web_url("http://example.com:80/")
    assert not is_web_url("https://example.com:443/")
    assert not is_web_url("http://example.com:80/page")
    assert not is_web_url("https://example.com:443/page")
    assert is_web_url("https://hal.science/hal-01987430")
    assert is_web_url("https://hal.science/hal-01987430/document")
    assert is_web_url(
        "https://hal.science/hal-01987430/file/MonginJP-CM2019_postprint.pdf"
    )
    assert is_web_url(
        "https://lirias.kuleuven.be/bitstream/123456789/625218/2/Medeghini%20Crut%20Gandolfi%20NanoLetters%202018.pdf"
    )
