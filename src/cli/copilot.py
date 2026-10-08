"""Minimal CLI client for CP3 (talks to API)."""

from __future__ import annotations

import argparse
import os
import sys

try:
    import httpx
except ImportError:  # pragma: no cover
    httpx = None


def base_url() -> str:
    return os.environ.get("COPILOT_API_URL", "http://localhost:8000")


def token() -> str | None:
    return os.environ.get("COPILOT_TOKEN")


def login(args: argparse.Namespace) -> None:
    if httpx is None:
        print("httpx not installed", file=sys.stderr)
        raise SystemExit(2)
    payload = {
        "tenant_id": args.tenant,
        "username": args.username,
        "password": args.password or os.environ.get("COPILOT_PASSWORD", ""),
    }
    try:
        r = httpx.post(f"{base_url()}/auth/login", json=payload, timeout=30)
        r.raise_for_status()
    except (httpx.RequestError, httpx.HTTPStatusError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
    data = r.json()
    print(data.get("access_token"))
    print("Do not store this token in a file.", file=sys.stderr)


def ask(args: argparse.Namespace) -> None:
    if httpx is None:
        print("httpx not installed", file=sys.stderr)
        raise SystemExit(2)
    t = token() or args.token
    if not t:
        print("missing token", file=sys.stderr)
        raise SystemExit(2)
    try:
        r = httpx.post(
            f"{base_url()}/ask",
            json={"question": args.question},
            headers={"Authorization": f"Bearer {t}"},
            timeout=120,
        )
        r.raise_for_status()
    except (httpx.RequestError, httpx.HTTPStatusError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
    print(r.text)


def run(args: argparse.Namespace) -> None:
    pass


def acknowledge(args: argparse.Namespace) -> None:
    pass


def approve(args: argparse.Namespace) -> None:
    pass


def status(args: argparse.Namespace) -> None:
    pass


def main() -> None:
    p = argparse.ArgumentParser(prog="copilot")
    sub = p.add_subparsers(required=True)
    pl = sub.add_parser("login")
    pl.add_argument("--tenant", required=True)
    pl.add_argument("--username", required=True)
    pl.add_argument("--password", default="")
    pl.set_defaults(func=login)
    pa = sub.add_parser("ask")
    pa.add_argument("question")
    pa.add_argument("--token", default="")
    pa.set_defaults(func=ask)
    pr = sub.add_parser("run")
    pr.set_defaults(func=run)
    pc = sub.add_parser("acknowledge")
    pc.set_defaults(func=acknowledge)
    pp = sub.add_parser("approve")
    pp.set_defaults(func=approve)
    ps = sub.add_parser("status")
    ps.set_defaults(func=status)
    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
