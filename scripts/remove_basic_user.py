from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    """
    Remove a basic auth user from the users.json file.
    :return: 0 on success, 1 on error, 2 on usage error
    """
    if len(sys.argv) != 2:
        print("Usage: python scripts/remove_basic_user.py <username>")
        return 2

    username = sys.argv[1]
    users_file = Path("app/auth/users.json")

    if not users_file.exists():
        print(f"No users file found at {users_file}")
        return 1

    try:
        users = json.loads(users_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print(f"Invalid JSON in {users_file}")
        return 1

    if username not in users:
        print(f"User '{username}' does not exist")
        return 1

    del users[username]

    if users:
        users_file.write_text(
            json.dumps(users, indent=2, sort_keys=True),
            encoding="utf-8",
        )
    else:
        # Optional: remove file entirely if no users left
        users_file.unlink()

    print(f"User '{username}' removed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
