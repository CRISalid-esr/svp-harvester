import re
from typing import List, Dict


def extract_idref_identifiers(identifier: str) -> List[Dict[str, str]]:
    """
    Extract idref identifier from an IdRef URI.

    Example:
        >>> extract_idref_identifiers("http://www.idref.fr/05163239X/id")
        [{'type': 'idref', 'value': '05163239X'}]

    Args:
        identifier: A string representing the identifier URI.

    Returns:
        A list of dicts with keys 'type' and 'value'.
    """
    ext_identifiers: List[Dict[str, str]] = []
    if not identifier:
        return ext_identifiers

    match = re.search(r"^https?://www\.idref\.fr/([^/]+)/id", str(identifier))
    if match:
        ext_identifiers.append({"type": "idref", "value": match.group(1)})

    return ext_identifiers
