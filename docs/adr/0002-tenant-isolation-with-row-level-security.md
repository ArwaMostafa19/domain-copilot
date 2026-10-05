# ADR 0002: Enforce tenant isolation with PostgreSQL Row-Level Security

## Status
Accepted

## Context
The twist for this project is multi-tenancy: at least two tenants with fully isolated documents, users and runs. The brief requires the isolation to be enforced at the data layer, with a test proving that cross-tenant leakage is impossible. A bug in application code must not be able to expose one tenant's data to another.

## Decision
- Every tenant-owned table has a tenant_id column and Row-Level Security enabled.
- The policy lets a row be read or written only when its tenant_id equals the tenant set for the current transaction. The policy has no separate write condition, so PostgreSQL applies the same condition to new and updated rows. A test confirms this.
- The tenant is set with set_config(..., true), so it lasts only for one transaction and cannot leak to the next request on the same connection.
- When no tenant is set, nothing matches, so the default is to show no data.
- The API connects as a limited user, copilot_app, that cannot bypass Row-Level Security. Migrations run as the admin user in a separate container, so the API never holds the admin password.
- A test fails if any table with a tenant_id column lacks Row-Level Security.

## Alternatives considered
- Filtering by tenant in application code: one forgotten filter leaks data, and nothing proves it cannot happen.
- A database per tenant: strongest isolation, but migrations, connections and tooling multiply with every tenant.
- A schema per tenant: similar operational cost, and every query must name the right schema.

## Consequences
- The database engine enforces isolation on every query, and the tests prove it against a real database.
- Every query must run inside a tenant context, through the helper in src/infrastructure/database.py.
- A superuser would silently bypass the policies, so the API must never connect as one. A test checks the application user.
- Tenants are added by a migration. There is no tenant administration interface yet.