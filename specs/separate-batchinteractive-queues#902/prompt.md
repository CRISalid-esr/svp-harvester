# Separate batch/interactive queues — Issue #902

## Context

The CRISalid bus convention (see `message_catalog.qmd`) splits every consumer queue into two queues suffixed
`-interactive` and `-batch`, with a corresponding 5th routing key segment on every message.

- **`.interactive`** — triggered by a real-time user action; must not be starved by bulk loads.
- **`.batch`** — produced by an ETL/import job; higher latency is acceptable.

Each split queue has its own channel, prefetch count, and worker pool so that a slow batch job cannot block
interactive message processing.

svp-harvester currently listens on a single queue (`svp-harvester`) bound to
`task.entity.references.retrieval` and publishes outbound messages with 4-segment routing keys. This issue
adds the split and propagates the mode through the full pipeline.

---

## Inbound queues

### Queue declarations

| Queue | Exchange | Binding key | Prefetch |
|---|---|---|---|
| `svp-harvester-interactive` | `publications` | `task.entity.references.retrieval.interactive` | 5 |
| `svp-harvester-batch` | `publications` | `task.entity.references.retrieval.batch` | 20 |

Each queue is declared with `durable=True` and the existing `x-consumer-timeout` argument.

Each queue has its own AMQP **channel** (one channel per queue). The publisher shares neither channel.

### Dead-letter queues

Each queue carries the dead-letter exchange argument so that nacked messages (without requeue) are routed to a
DLQ. The `dlx.publications` exchange must be pre-created in the RabbitMQ deployment before svp-harvester
starts.

| DLQ | Bound to | Routing key |
|---|---|---|
| `dlq.svp-harvester-interactive` | `dlx.publications` | `svp-harvester-interactive` |
| `dlq.svp-harvester-batch` | `dlx.publications` | `svp-harvester-batch` |

DLQ declaration is a **deployment prerequisite** (outside svp-harvester's scope). svp-harvester only passes
`x-dead-letter-exchange: dlx.publications` and `x-dead-letter-routing-key: <queue-name>` in the queue
arguments.

### Old queue

The old `svp-harvester` queue (bound to the 4-segment key `task.entity.references.retrieval`) is **removed**.
Deployment must migrate producers (crisalid-ikg) to the new 5-segment routing keys simultaneously.

---

## Worker pool isolation

Two independent worker pools replace the current single pool.

| Pool | Task queue | Workers | Feeds from |
|---|---|---|---|
| interactive | `interactive_task_queue` | `inner_interactive_parallelism_limit` | `svp-harvester-interactive` |
| batch | `batch_task_queue` | `inner_batch_parallelism_limit` | `svp-harvester-batch` |

Workers are `AMQPMessageProcessor` instances. Each pool's processors share a single `result_queue` (outbound
publishing is serialised and mode-tagged, so a shared result queue is safe).

---

## Mode propagation

### Extraction at ingestion

When `AMQPInterface` picks up a message from a queue iterator, it extracts the mode from the last segment of
`message.routing_key`:

```python
mode = message.routing_key.split(".")[-1]  # "interactive" or "batch"
```

It enqueues `(message, mode)` as a tuple to the appropriate task queue.

### Persistence on the Retrieval record

`AMQPMessageProcessor.wait_for_message()` unpacks the tuple and passes `mode` to `_process_message()`.
`_process_message()` forwards it to `RetrievalService` (constructor parameter), which passes it to
`RetrievalDAO.create_retrieval()`. Mode is stored as a column on the `retrievals` table (see DB model
change below).

This is the single source of truth for mode throughout the processing pipeline. No `"mode"` field is
needed in the content dicts on the result queue.

### In the message factories

All three factories already perform a DB query during `_build_payload()` that loads the full ORM graph.
Each factory sets `self.mode` from the loaded record, following the same pattern already used by
`AMQPReferenceEventMessageFactory` for `self.reference_event_type`:

| Factory | ORM path to mode |
|---|---|
| `AMQPRetrievalMessageFactory` | `retrieval.mode` |
| `AMQPHarvestingMessageFactory` | `harvesting.retrieval.mode` |
| `AMQPReferenceEventMessageFactory` | `reference_event.harvesting.retrieval.mode` |

Each `_build_routing_key()` appends `.{self.mode}` to the base key. `AbstractAMQPMessageFactory`
initialises `self.mode = "batch"` as a conservative fallback.

---

## Outbound routing keys (after the change)

| Factory | Current key | New key pattern |
|---|---|---|
| `AMQPHarvestingMessageFactory` | `event.references.harvesting.state` | `event.references.harvesting.state.<mode>` |
| `AMQPRetrievalMessageFactory` (success) | `event.references.retrieval.state` | `event.references.retrieval.state.<mode>` |
| `AMQPRetrievalMessageFactory` (error) | `event.references.retrieval.error` | `event.references.retrieval.error.<mode>` |
| `AMQPReferenceEventMessageFactory` | `event.references.reference.<action>` | `event.references.reference.<action>.<mode>` |

Downstream consumers (`crisalid-ikg-publications`, `crisalid-ikg-harvesting-events`) must update their
binding keys to 5-segment patterns. This is a **deployment coordination point** outside svp-harvester's scope.

---

## Settings changes

New settings in `AppSettings` (all overridable by env var):

```python
amqp_interactive_queue_name: str = "svp-harvester-interactive"
amqp_batch_queue_name: str = "svp-harvester-batch"
amqp_interactive_routing_key: str = "task.entity.references.retrieval.interactive"
amqp_batch_routing_key: str = "task.entity.references.retrieval.batch"
amqp_interactive_prefetch_count: int = 5
amqp_batch_prefetch_count: int = 20
inner_interactive_parallelism_limit: int = 5
inner_batch_parallelism_limit: int = 10
```

The existing `amqp_queue_name`, `amqp_retrieval_routing_key`, `amqp_prefetch_count`, and
`inner_task_parallelism_limit` settings are **removed**.

---

## Database model change

A `mode` column is added to the `retrievals` table:

```python
mode: Mapped[str] = mapped_column(String, nullable=False, default="batch")
```

Values are `"interactive"` or `"batch"`. Default `"batch"` covers retrievals triggered via the REST API,
which carry no routing key.

A new Alembic migration adds the column with `server_default='batch'` so existing rows remain valid.

`RetrievalDAO.create_retrieval()` accepts `mode: str` and passes it through.

---

## Code changes overview

### `app/amqp/amqp_interface.py`

- Add `interactive_task_queue`, `batch_task_queue` (replace `task_queue`).
- Add `interactive_channel`, `batch_channel` (replace `pika_channel`).
- Add `interactive_queue`, `batch_queue` (replace `pika_queue`).
- `_attach_message_processing_workers()` creates two worker pools.
- `_bind_queue()` → `_bind_queues()`: declares both queues on their respective channels with DLX arguments.
- `listen()` → two concurrent `_listen_queue()` coroutines started in `SvpHarvester.open_rabbitmq_connexion()`.
- `stop_listening()` drains both task queues.

### `app/amqp/amqp_message_processor.py`

- `wait_for_message()` unpacks `(message, mode)` tuples from the task queue.
- `_process_message(payload, mode)` — mode added as parameter, forwarded to `RetrievalService`.

### `app/services/retrieval/retrieval_service.py`

- `RetrievalService.__init__()` accepts `mode: str = "batch"`.
- `register()` passes `mode` to `RetrievalDAO.create_retrieval()`.

### `app/db/daos/retrieval_dao.py`

- `create_retrieval()` accepts `mode: str` and sets it on the new `Retrieval` instance.

### `app/amqp/abstract_amqp_message_factory.py`

- Adds `self.mode: str = "batch"` to `__init__()`.

### `app/amqp/amqp_harvesting_message_factory.py`, `amqp_retrieval_message_factory.py`, `amqp_reference_event_message_factory.py`

- Each `_build_payload()` sets `self.mode` from the ORM object it loads.
- Each `_build_routing_key()` appends `.{self.mode}`.

### `app/svp_harvester.py`

- `open_rabbitmq_connexion()` creates two listen tasks (one per queue) instead of one.

---

## Scope and non-goals

- A single publisher channel is kept for outbound messages (no split on the publish side).
- No changes to harvester logic, persistence, or the REST API.
- No DLQ declaration inside svp-harvester — this is a deployment responsibility.
- The old 4-segment `svp-harvester` queue is dropped with no transition period; producers must be migrated in
  the same deployment.
- Interactive/batch distinction has no effect on which harvesters run or how results are persisted; it affects
  only throughput parameters and routing keys.
