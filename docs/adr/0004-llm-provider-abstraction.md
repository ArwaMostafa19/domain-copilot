# ADR 0004: One provider interface with a fallback chain and one fixed embedding model

## Status
Accepted

## Context
The platform calls language models for answers and for embeddings. Providers differ in availability, quota and quality, and the free tiers of hosted providers have usage limits. The business logic must not depend on any vendor.

## Decision
- One synchronous interface covers completion, streaming, tool calling and embeddings. Business logic depends only on that interface.
- The order of providers is configuration (LLM_CHAIN). A fallback chain in the application layer moves to the next provider when a provider is unavailable or out of quota. It does not fall back on a bad request or on an authentication error, because the next provider would fail the same way.
- A single adapter speaks the OpenAI-compatible protocol and serves both Groq and Gemini. A second adapter serves Ollama as the local provider. A fake provider serves the tests.
- Embeddings use one fixed model for the whole index. Its name and size are stored in the database and checked before ingesting or searching, so a fallback can never mix embedding models.
- API keys are read from environment variables in one place, and tests enforce that no other file reads them.

## Alternatives considered
- LiteLLM or LangChain: more features, but an extra dependency with behaviour that is hard to see and to teach.
- Vendor SDKs: provider code leaks into the application and adds dependencies.
- An asynchronous interface: the code base is synchronous, so this is deferred.

## Consequences
- Switching providers is a configuration change.
- There is no fallback after the first streamed token.
- The cooldown state is per process and is not shared between workers.
- Changing the embedding model requires a full re-index.
- Token counts are estimated at about four characters per token when a provider does not report them.