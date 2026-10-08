"""Seed one technician and one supervisor per tenant.

The password comes ONLY from the named environment variable; there is no default
and it is never printed.
"""

from __future__ import annotations

import os
import sys

from src.application import security
from src.infrastructure.database import tenant_connection


def seed(tenant_id: str, password: str) -> None:
    tech = f"{tenant_id.split('-')[1] if '-' in tenant_id else tenant_id}-tech"
    sup = f"{tenant_id.split('-')[1] if '-' in tenant_id else tenant_id}-sup"
    pwh = security.hash_password(password)
    with tenant_connection(tenant_id) as conn:
        conn.execute(
            """
            INSERT INTO users (tenant_id, username, role, password_hash, active)
            VALUES (%s, %s, %s, %s, true)
            ON CONFLICT (tenant_id, username) DO UPDATE
            SET password_hash = EXCLUDED.password_hash, active = true
            """,
            (tenant_id, tech, "technician", pwh),
        )
        conn.execute(
            """
            INSERT INTO users (tenant_id, username, role, password_hash, active)
            VALUES (%s, %s, %s, %s, true)
            ON CONFLICT (tenant_id, username) DO UPDATE
            SET password_hash = EXCLUDED.password_hash, active = true
            """,
            (tenant_id, sup, "supervisor", pwh),
        )


def main() -> None:
    env_var = sys.argv[1] if len(sys.argv) > 1 else "DEMO_USER_PASSWORD"
    if env_var.startswith("--password-env="):
        env_var = env_var.split("=", 1)[1]
    password = os.environ.get(env_var)
    if not password:
        print(f"error: {env_var} is not set", file=sys.stderr)
        raise SystemExit(2)
    for tenant in ("tenant-alpha", "tenant-beta"):
        seed(tenant, password)
    print("seeded users", file=sys.stderr)


if __name__ == "__main__":
    main()
