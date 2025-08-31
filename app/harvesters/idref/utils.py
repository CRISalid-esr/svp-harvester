import re
from typing import List, Dict


def filter_idref_identifiers(identifier: str) -> List[Dict[str, str]]:
    """
    Check if the identifier is an IdRef URI. If yes, return it as-is.

    Examples:
        >>> filter_idref_identifiers("http://www.idref.fr/05163239X/id")
        [{'type': 'idref', 'value': 'http://www.idref.fr/05163239X/id'}]

        >>> filter_idref_identifiers("http://www.idref.fr/05163239X")
        [{'type': 'idref', 'value': 'http://www.idref.fr/05163239X'}]

    Args:
        identifier: A string representing the identifier URI.

    Returns:
        A list of dicts with keys 'type' and 'value'.
    """
    ext_identifiers: List[Dict[str, str]] = []
    if not identifier:
        return ext_identifiers

    # Regex accepts trailing /id as optional
    if re.match(r"^https?://www\.idref\.fr/[^/]+(/id)?$", str(identifier)):
        ext_identifiers.append({"type": "idref", "value": identifier})

    return ext_identifiers
