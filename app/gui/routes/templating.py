import gettext
import os

from starlette.templating import Jinja2Templates

DEFAULT_LOCALE = "en_US"


def get_templating_engine(
    i18n_domain: str,
    current_locale: str = DEFAULT_LOCALE,
):
    """
    Return a i18n enabled templating engine

    :param i18n_domain: gettext domain
    :param current_locale: current locale
    :return: templating engine with i18n capabilities
    """
    locale_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "..", "..", "..", "locales"
    )
    gnu_translations = gettext.translation(
        domain=i18n_domain, localedir=locale_path, languages=[current_locale]
    )
    gnu_translations.install()

    templates = Jinja2Templates(
        directory=os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "..",
            "..",
            "templates",
        ),
        extensions=["jinja2.ext.i18n"],
    )
    env = templates.env
    env.install_gettext_translations(gnu_translations, newstyle=True) # pylint: disable=no-member
    return templates
