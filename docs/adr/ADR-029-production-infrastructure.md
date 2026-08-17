# ADR-029 — Production infrastructure baseline

## Status
Accepted

## Context

AMIP already has separate web/worker processes and durable jobs, but the default Compose stack uses SQLite and one local data volume. Stack 14 needs a production baseline without introducing microservices or managed-cloud lock-in prematurely.

## Decision

Production uses PostgreSQL 16, persistent filesystem storage for audio, separate web/worker processes, Alembic one-shot migrations, database-aware readiness, periodic database+storage backups, and Docker Compose as the portable deployment reference.

SQLite remains supported for development/test. PostgreSQL is the production database. Storage remains behind the existing application abstraction/path so an object-store adapter can be introduced later without coupling the domain to a cloud vendor.

## Consequences

Positive:
- production database supports concurrent web/worker access better than SQLite;
- no public database port is required;
- deployment remains understandable and portable;
- backup/restore responsibilities are explicit;
- readiness distinguishes a live process from a usable application.

Trade-offs:
- filesystem storage requires durable host/platform volumes;
- backup replication off-host is an operational responsibility;
- horizontal scaling of storage will eventually require object storage or a shared filesystem;
- Compose is a reference topology, not a full orchestrator.

## Rejected for now

- Kubernetes: operational complexity is disproportionate to the current product stage.
- Redis solely for infrastructure: durable jobs already use the database and do not justify another stateful dependency yet.
- mandatory S3-compatible storage: useful later, but would add provider/configuration complexity before horizontal scaling is required.
