from sqlalchemy.orm import Mapped, mapped_column, validates

from app.db.session import Base
from app.utilities.url_utilities import is_web_url


class ReferenceManifestation(Base):
    """
    Model for persistence of reference manifestations
    """

    __tablename__ = "reference_manifestations"

    id: Mapped[int] = mapped_column(primary_key=True)
    page: Mapped[str] = mapped_column(nullable=False)
    download_url: Mapped[str] = mapped_column(nullable=True)

    def _validate_url(self, key, url):
        """
        Validate that the given URL is valid and starts with http or https.

        :param key: key
        :param url: url to validate
        :return: url if valid
        """
        if url and not is_web_url(url):
            raise ValueError(f"{key.capitalize()} URL {url} is not a valid URL")
        return url

    @validates("page")
    def validate_page(self, key, page):
        return self._validate_url(key, page)

    @validates("download_url")
    def validate_download_url(self, key, download_url):
        return self._validate_url(key, download_url)
