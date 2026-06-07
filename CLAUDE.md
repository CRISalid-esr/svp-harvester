# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**svp-harvester** is a message-driven Python service that harvests scholarly publication metadata from multiple bibliographic aggregators (OpenAlex, Scanr) and open archives (HAL, IdRef) on behalf of researchers. It is part of the CRISalid / SoVisu+ ecosystem.

The primary interface is **AMQP** (RabbitMQ): upstream systems send a `Person` message describing a researcher by their identifiers; the service runs the relevant harvesters and publishes results back. The REST API (`app/api/`) is secondary — mainly used for monitoring, history queries, and manual triggering.

## Common Commands

### Development

```bash
# Install dependencies
poetry install

# Run the service locally
APP_ENV=DEV uvicorn app.main:app --reload

# Apply database migrations
APP_ENV=DEV alembic upgrade head

# Generate a new migration from model changes
APP_ENV=DEV alembic revision --autogenerate -m "short description"
```

### Testing

Tests require a running PostgreSQL instance (local or Docker) with the test database and credentials from `.test.env`. The fixture creates and drops all tables for each test automatically.

```bash
# Run all tests
APP_ENV=TEST pytest

# Run specific tests
# Add `import pytest` and `@pytest.mark.current` to the target test functions, then:
APP_ENV=TEST pytest -m current
# Always run from the project root. Never use -k "not integration" — ignore @pytest.mark.integration entirely.
# Always remove @pytest.mark.current before committing.
```

### Linting & Formatting

```bash
pylint --rcfile=.pylintrc app/
black app/ tests/
```

### Frontend Assets

```bash
cd app/templates
npm install
npm run build
```

### Translations

```bash
pybabel extract --mapping babel.cfg --output-file=locales/admin.pot .
pybabel update --domain=admin --input-file=locales/admin.pot --output-dir=locales
pybabel compile --domain=admin --directory=locales --use-fuzzy
```

## Architecture

### Message-Driven Flow

1. An upstream system publishes a JSON message to the RabbitMQ exchange with a `Person` payload (type + identifier list).
2. `AMQPInterface` (`app/amqp/amqp_interface.py`) receives the message and dispatches it to one of several async `AMQPMessageProcessor` workers.
3. The processor validates the payload into a `Person` Pydantic model and hands it to `RetrievalService` (`app/services/retrieval/`).
4. The retrieval service selects and runs the appropriate harvesters, persists results via SQLAlchemy, and publishes result/event messages back to RabbitMQ.
5. A Redis cache wraps the costliest outbound HTTP calls to third-party APIs.

### AMQP Message Types

All messages flow through the `publications` RabbitMQ topic exchange. Routing keys have **5 segments**; the last is the mode (`interactive` or `batch`, see below).

**Inbound — retrieval task** (`task.entity.references.retrieval.<mode>`): sent by crisalid-ikg to trigger harvesting for a researcher. Payload carries `type: "person"`, an identifier list, an optional harvester filter, and requested event types. `AMQPMessageProcessor` validates it into a `Person` model and hands it to `RetrievalService`.

**Outbound — harvesting state** (`event.references.harvesting.state.<mode>`): emitted by each individual harvester as it transitions through `idle → running → completed / failed / skipped`. One message per state change per harvester. Built by `AMQPHarvestingMessageFactory`.

**Outbound — reference event** (`event.references.reference.<action>.<mode>`): emitted once per publication per harvesting run. `<action>` is `created`, `updated`, `deleted`, or `unchanged` depending on whether the reference is new, changed, absent, or identical to the stored version. This is the primary payload for downstream consumers. Built by `AMQPReferenceEventMessageFactory`.

**Outbound — retrieval acknowledgement** (`event.references.retrieval.state.<mode>`): sent only when the inbound message carries `reply: true`, immediately after the `Retrieval` record is created in DB. Lets the caller track that harvesting has started. Built by `AMQPRetrievalMessageFactory`.

**Outbound — retrieval error** (`event.references.retrieval.error.<mode>`): sent when the inbound payload is invalid (Pydantic validation failure or no usable identifiers). No DB record is created; the mode is carried in the error content dict and read back by the factory.

### Routing Mode — interactive vs batch

The last routing key segment is a `MessageMode` (`StrEnum` in `app/models/message_mode.py`): `BATCH = "batch"` for ETL/bulk loads, `INTERACTIVE = "interactive"` for real-time user-triggered requests.

`AMQPInterface` opens **two independent AMQP channels** with separate prefetch counts and worker pools — one per queue (`svp-harvester-interactive`, `svp-harvester-batch`) — so batch traffic cannot starve interactive processing. The mode is extracted from the inbound routing key (`MessageMode(message.routing_key.split(".")[-1])`), written to `Retrieval.mode` in the DB (single source of truth), and appended to every outbound routing key by the message factories via `self.mode` (populated from the already-loaded ORM graph).

### Researcher Identifiers

Harvesting is always triggered by **researcher identifiers**, never by name alone. Supported identifier types are declared in `identifiers.yml` (priority-ordered):

| Key | Label | In use by clients |
|-----|-------|-------------------|
| `idref` | IdRef | yes |
| `orcid` | ORCID | yes |
| `idhali` | idHal-i | yes |
| `idhals` | idHal-s | yes |
| `researcherid` | ResearcherID | no |
| `arxiv` | arXiv | no |
| `pubmed` | PubMed | no |
| `scopus` | ScopusEID | yes |
| `eppn` | EPPN | no |
| `local` | Local | no |

Identifier keys use lowercase only, with no dashes or carets — this is a normalization convention shared across svp-harvester and other CRISalid apps.

Each harvester factory (`app/harvesters/<name>/<name>_harvester_factory.py`) declares which identifier types it can handle; the retrieval service uses this to route requests. Identifier handling is complex — a `Person` message may carry multiple identifiers of different types, and each harvester selects only those it understands.

### Harvester Plugin System

Harvesters are declared in `harvesters.yml` and loaded dynamically. Each harvester under `app/harvesters/<name>/` provides:
- A concrete subclass of `AbstractHarvester`
- A concrete subclass of `AbstractReferencesConverter`
- A factory subclassing `AbstractHarvesterFactory`

Current harvesters: **idref** (SPARQL + RDF — indirection system: queries IdRef to obtain publication identifiers/URIs, then resolves them against secondary harvesters covering Persée, Science+, OpenEdition), **hal** (TEI/XML API), **scanr** (Elasticsearch), **openalex** (JSON REST API), **scopus** (JSON REST API).

#### AbstractHarvester — template method pattern

`run()` is the fixed orchestration template. Subclasses must only override `fetch_results()` and declare `supported_identifier_types`.

`run()` flow:
1. Sets harvesting state to RUNNING, notifies via result queue.
2. Snapshots pre-existing references for this entity (to detect deletions later).
3. Iterates the async generator returned by `fetch_results()`.
4. For each raw result: calls `converter.build()` to get a candidate reference, checks if it already exists in DB, calls `converter.convert()` only if the reference is new, changed, or harvested by a newer harvester version.
5. Fires a `ReferenceEvent` (CREATED / UPDATED / UNCHANGED) per reference and pushes it to the result queue.
6. After the loop, registers DELETED events for references present before but absent now (only if DELETED is in the requested event types).
7. Sets state to COMPLETED, or FAILED on any unrecovered exception.

Key extension points for subclasses:
- `supported_identifier_types: list[str]` — class-level list of identifier keys this harvester handles (e.g. `["idref"]`).
- `is_relevant(entity) -> bool` — returns True if the entity carries at least one identifier from `supported_identifier_types`; override to add extra conditions.
- `fetch_results()` — async generator that queries the external platform using the entity's relevant identifiers and yields `AbstractHarvesterRawResult` objects.

Error handling contract: `ExternalEndpointFailure` should be let to bubble up to `run()` (stops the harvesting); `UnexpectedFormatException` can be caught per-item to skip one record and continue, or bubble up to abort.

### Key Directories

| Path | Purpose |
|------|---------|
| `app/amqp/` | RabbitMQ interface, message processor workers, result publisher |
| `app/harvesters/` | One subdirectory per bibliographic source |
| `app/services/retrieval/` | Orchestrates harvester selection and execution |
| `app/services/concepts/` | SKOS concept resolution (Wikidata, IdRef, JEL via SPARQL) |
| `app/services/organizations/` | ROR API integration for organization normalization |
| `app/api/routes/` | Secondary REST API (monitoring, history, manual triggers) |
| `app/models/` | Pydantic domain models |
| `app/db/models/` | SQLAlchemy ORM models |
| `app/settings/` | Pydantic-based settings for DEV/TEST/PROD |
| `app/gui/` | Optional admin web UI (Jinja2 templates + vanilla JS in `app/templates/`, HTTP Basic Auth) — the service runs without it |
| `tests/fixtures/` | Shared pytest fixtures: DB entities, API response mocks |

### Settings

Environment is selected by `APP_ENV` (DEV / TEST / PROD). Settings classes in `app/settings/` inherit from `AppSettings`; env vars override `.env` file values. See `.env.example` for all variables.

## Database

- PostgreSQL 16 with `asyncpg` driver and SQLAlchemy 2.0 async sessions
- Alembic manages migrations; always set `APP_ENV` before running Alembic commands
- Test suite auto-creates and drops tables per test via fixtures in `tests/conftest.py`

## Testing Notes

- `asyncio_mode = "auto"` is set in `pyproject.toml`; no `@pytest.mark.asyncio` needed
- External HTTP calls are mocked at the fixture level (see `tests/fixtures/`)
- Integration tests (marked `integration`) require live external services and are excluded in CI

## Infrastructure Dependencies

The service requires PostgreSQL, RabbitMQ, and Redis. A `docker-compose.yml` is provided at the repo root for local development. Startup sequence: run migrations, then start uvicorn.

## CI/CD

- **PR to dev-main**: runs `pytest` (with a PostgreSQL service container) and `pylint`
- **Push to dev-main**: compiles translations, builds and pushes Docker image to DockerHub (`crisalidesr/svp-harvester:dev`)
- **Release workflow**: builds versioned Docker image

## Scripts

Utility scripts in `scripts/` for user management (`add_basic_user.py`, `remove_basic_user.py`), AMQP testing (`amqp_listen.py`, `amqp_publish.py`), and concept resolution debugging (`dereference_concept.py`).