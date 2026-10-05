## Domain Copilot - Industrial Maintenance

# 

# An agentic RAG platform for field maintenance.

# 



# ## Assigned variant

# 

# - Domain: D5 (Industrial - field maintenance)

# - Twist: T0 (Multi-tenancy)

# -Source: derived from the National ID, as the brief allows
 Domain rule: last two digits mod 7 = 5, so D5
- Twist rule: sum of all digits mod 8 = 0, so T0

# 

## Quick start

1. Copy .env.example to .env and fill in every value. Use letters and digits only for the passwords.
2. Run: docker compose up --build
3. Open http://localhost:8000/health

Two database users are used. The admin user (POSTGRES_USER) only runs the migrations and can bypass Row-Level Security. The application user (copilot_app, password APP_DB_PASSWORD) is what the API uses, and Row-Level Security always applies to it.

## Status

# 

# Work in progress. Quick start, environment variables and the demo path will be added as features land.

