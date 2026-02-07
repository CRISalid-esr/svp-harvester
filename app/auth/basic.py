from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBasic()


def _load_users(path: Path) -> Dict[str, str]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid users file JSON: {path}") from e


def require_basic_user(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """
    Validates Basic Auth against a local JSON file of bcrypt hashes.
    Returns the username if OK.
    """
    users_file = Path(__file__).resolve().parent / "users.json"
    users = _load_users(users_file)

    hashed = users.get(credentials.username)
    if not hashed or not pwd_context.verify(credentials.password, hashed):
        # WWW-Authenticate header required for browsers to show the login prompt
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username
