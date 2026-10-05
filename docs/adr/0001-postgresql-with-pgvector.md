# ADR 0001: Use PostgreSQL with pgvector as the single data store

## Status
Accepted

## Context
The platform needs a relational store for documents, users and runs, and a vector store for embeddings, both with migrations. The multi-tenancy twist also requires isolation to be enforced at the data layer.

## Decision
Use one PostgreSQL database, running in Docker with the pgvector extension. Embeddings will be added to the chunks table in a later migration, once the embedding model is chosen. The schema is versioned as numbered SQL files in migrations/, applied in order by a small runner that records each applied file in a table.

## Alternatives considered
- A separate vector database next to a relational one: two systems to run and secure, and tenant isolation would have to be rebuilt on the vector side with filters we write ourselves.
- MongoDB alone: it does not meet the requirement for a relational store, and Row-Level Security is a PostgreSQL feature.
- Alembic for migrations: a standard tool, but it adds two dependencies and wraps SQL, which is the real content here, in Python. Reasonable to adopt later.

## Consequences
- One system to run and back up, and one place to enforce isolation.
- Row-Level Security can protect chunks and embeddings in the same database.
- The hand-written runner has known limits: no rollback, no check that an applied file was edited, and no lock if two runners start at once.
- pgvector is less specialised than a dedicated vector database, which is not a limit at this corpus size.