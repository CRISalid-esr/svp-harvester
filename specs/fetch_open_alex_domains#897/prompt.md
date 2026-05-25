# Fetch OpenAlex Topics — Issue #897

## Context

OpenAlex work records include a `topics` array. Each topic carries a relevance score for the work, a URI, and a human-readable label. Domain / field / subfield are static hierarchy levels that all clients already have access to independently; they are not stored.

The `source_id` (e.g. `T10153`) is not provided as a separate field — it must be extracted from the trailing path segment of the URI (e.g. `https://openalex.org/T10153`).

Example payload (excerpt from an OpenAlex work response):

```json
[
  {
    "id": "https://openalex.org/T10153",
    "display_name": "Education, sociology, and vocational training",
    "score": 0.9588000178337097,
    "domain":   { "display_name": "Social Sciences", "id": "https://openalex.org/domains/2" },
    "field":    { "display_name": "Social Sciences",  "id": "https://openalex.org/fields/33" },
    "subfield": { "display_name": "Sociology and Political Science", "id": "https://openalex.org/subfields/3312" }
  },
  {
    "id": "https://openalex.org/T11475",
    "display_name": "French Urban and Social Studies",
    "score": 0.9485999941825867,
    "domain":   { "display_name": "Social Sciences", "id": "https://openalex.org/domains/2" },
    "field":    { "display_name": "Social Sciences",  "id": "https://openalex.org/fields/33" },
    "subfield": { "display_name": "Sociology and Political Science", "id": "https://openalex.org/subfields/3312" }
  }
]
```

Fields retained: `id` (URI), `display_name`, `score`.  
Fields discarded: `domain`, `field`, `subfield`.

---

## Data model

### SQLAlchemy — `Topic` table

| Column         | Type    | Notes                                 |
|----------------|---------|---------------------------------------|
| `id`           | Integer | PK                                    |
| `source_id`    | String  | OpenAlex identifier, e.g. `T10153`    |
| `uri`          | String  | Full URI, e.g. `https://openalex.org/T10153` |
| `display_name` | String  |                                       |

### SQLAlchemy — `Reference` ↔ `Topic` association table (`reference_topics`)

Stores the per-reference relevance score:

| Column          | Type    | Notes                        |
|-----------------|---------|------------------------------|
| `reference_id`  | FK      |                              |
| `topic_id`      | FK      |                              |
| `score`         | Float   | Score as returned by OpenAlex|

### Pydantic — `Topic` entity

```python
class Topic(BaseModel):
    source_id: str   # e.g. "T10153"
    uri: str         # e.g. "https://openalex.org/T10153"
    label: str       # maps from display_name in the ORM
    score: float
```

`score` lives on the `Topic` Pydantic entity (it is relationship-scoped in SQL but reference-scoped in the domain model). `label` is the wire name for `display_name`.

---

## Harvesting behaviour

- Topics are extracted from the `topics` array of each OpenAlex work response by `OpenAlexReferencesConverter`.
- Topics are looked up by `source_id`. **Missing topics are created on the fly** using the data received in the payload. No remote look-up against the OpenAlex topics endpoint is performed.
- If the `display_name` of an existing topic has changed, it is updated in the `topics` table.
- When a fresh version of an OpenAlex record is received, **all topics and scores for that reference are replaced** with the new values.
- If a topic is no longer referenced by any reference, it remains in the `topics` table (no cascade delete).
- References from harvesters other than OpenAlex carry an **empty `domains` array** for now.

---

## AMQP serialisation

Topics are included in the result message under the key `domains`:

```json
"domains": [
  {
    "source_id": "T10153",
    "uri": "https://openalex.org/T10153",
    "label": "Education, sociology, and vocational training",
    "score": 0.9588
  }
]
```

The internal Pydantic field is named `topics`; `domains` is applied as a `serialization_alias` and emitted via `model_dump(by_alias=True)` in the AMQP factory.

---

## Scope and non-goals

- Domain, field, and subfield hierarchy levels are **not stored** (clients hold this mapping statically).
- No validation of topic identifiers against the OpenAlex topics API.
- No topic deletion when a topic becomes unreferenced.
- Other harvesters (HAL, IdRef, Scanr, Scopus) produce empty `domains` arrays until further notice.