def normalize_orcid(value: str) -> str:
    """Insert hyphens into a bare 16-digit ORCID string; idempotent if hyphens already present."""
    v = value.replace("-", "")
    return f"{v[:4]}-{v[4:8]}-{v[8:12]}-{v[12:]}"
