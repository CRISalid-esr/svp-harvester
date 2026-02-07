from __future__ import annotations

import json
import sys
from getpass import getpass
from pathlib import Path

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def main() -> int:
    """
    Add or update a basic auth user in the users.json file.
    :return: 0 on success, 1 on error, 2 on usage error
    """
    if len(sys.argv) != 2:
        print("Usage: python scripts/add_basic_user.py <username>")
        return 2

    username = sys.argv[1]
    password = getpass(f"Password for {username}: ")
    pw_bytes = password.encode("utf-8")
    if len(pw_bytes) > 72:
        print("Error: bcrypt only supports passwords up to 72 BYTES (UTF-8).")
        print(f"Your password is {len(pw_bytes)} bytes. Use a shorter one.")
        return 1
    password2 = getpass("Confirm password: ")
    if password != password2:
        print("Passwords do not match")
        return 1

    users_file = Path("app/auth/users.json")
    users_file.parent.mkdir(parents=True, exist_ok=True)

    users = {}
    if users_file.exists():
        users = json.loads(users_file.read_text(encoding="utf-8"))

    users[username] = pwd_context.hash(password)
    users_file.write_text(json.dumps(users, indent=2, sort_keys=True), encoding="utf-8")
    print(f"User '{username}' added/updated in {users_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
