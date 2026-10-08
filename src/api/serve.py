"""Launcher for Domain Copilot Web UI & API.

Validates AUTH_SECRET configuration, starts uvicorn server, and opens the
browser pointing to http://localhost:8000/.
"""

from __future__ import annotations

import sys
import webbrowser
from threading import Timer

import uvicorn

from src.infrastructure.config import load_settings_from_environ


def main() -> None:
    try:
        settings = load_settings_from_environ()
        if not settings.auth_secret or len(settings.auth_secret) < 32:
            print("error: AUTH_SECRET must be set and at least 32 characters long", file=sys.stderr)
            sys.exit(1)
    except Exception as exc:  # noqa: BLE001
        print(f"configuration error: {exc}", file=sys.stderr)
        sys.exit(1)

    url = "http://localhost:8000/"
    print(f"Starting Domain Copilot at {url} ...")

    # Open browser automatically after 1 second
    Timer(1.0, lambda: webbrowser.open(url)).start()

    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()
