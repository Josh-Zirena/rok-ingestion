# Rok Ingestion & Leaderboard Backend (POC)

This project implements the backend ingestion and query pipeline for a player analytics dashboard.

## Design Principles

The system is designed to be:

- **S3-first** – Object storage as the source of truth
- **Event-driven** – Triggered by file uploads
- **Expandable** – Multi-kingdom, new metrics, future DB if needed
- **POC-friendly** – Minimal infrastructure, no auth, no database initially

## What This System Does

1. You manually upload a CSV or JSON snapshot of player data
2. The system ingests the file and stores it as an immutable historical snapshot
3. A curated, query-optimized dataset is produced
4. A public API serves leaderboard data to a frontend
5. The most recent snapshot available is treated as the "current" state

## Core Concepts

### Snapshot-based

- Each upload represents the full state of players at a point in time
- Data is append-only; nothing is overwritten

### Stable Identity

- `id` is the stable unique identifier for a player
- `id` must be unique within a single file
- `id` is expected to repeat across weeks (this is intentional)

### Separation of Concerns

- **Ingestion** builds the data lake
- **Query/API** serves the frontend
- Frontend never talks directly to S3 or Athena

## S3 Key Conventions

These are logical conventions used by the system.

### Inbox (manual upload — the only human touchpoint)

```
inbox/source=rok_players/kingdom=51/dt=2026-01-26/players.csv
```

### Raw (immutable, audit-safe snapshot)

```
raw/source=rok_players/kingdom=51/dt=2026-01-26/run_ts=20260126T153012Z/players.csv
```

### Curated (query-ready, Parquet)

```
curated/source=rok_players/kingdom=51/dt=2026-01-26/players.parquet
```

## Backend Components

### Ingestion Service (`ingest_players`)

Triggered automatically when a file is uploaded to the inbox path.

**Responsibilities:**

- Parse S3 key to determine kingdom and snapshot date
- Validate schema and enforce unique `id` within the file
- Normalize data types and column names
- Add metadata (`kingdom`, `snapshot_date`, `ingested_at`, `run_id`, `record_hash`)
- Write immutable raw snapshot
- Write curated Parquet snapshot

This service is **stateless** and **idempotent**.

### API Service (`leaderboard-api`)

Invoked via API Gateway and used by the public frontend.

**Responsibilities:**

- Validate incoming requests
- Resolve "latest" snapshot for a kingdom
- Query Athena for leaderboard results
- Return UI-friendly JSON responses

Athena is used as the initial query engine and can be swapped later.

## Infrastructure & Deployment (POC)

This POC uses Terraform to provision AWS infrastructure and Docker-based Lambda deployment to avoid manual AWS configuration and dependency packaging issues.

**The goal is:**

- **Zero click-ops** in the AWS console
- **Fully reproducible infrastructure**
- **Clean separation** between application code and infrastructure code

### Infrastructure as Code

All AWS resources are managed using Terraform.

**Terraform is responsible for provisioning:**

- S3 bucket (data lake)
- S3 event notifications for ingestion
- IAM roles and policies
- Lambda functions
- API Gateway (public HTTP API)
- CloudWatch log groups
- Rate limiting / throttling

Infrastructure lives alongside the application code but is managed separately.

### Lambda Deployment Strategy

#### Why Docker-based Lambda

The ingestion service uses:

- `pandas`
- `pyarrow`

These dependencies are difficult to package reliably using ZIP-based Lambdas.

To simplify deployment and avoid dependency issues, this project uses:

- **Container-based AWS Lambda**
- Docker images built locally
- Images pushed to Amazon ECR
- Terraform references the image by digest or tag

**This approach:**

- Avoids Lambda layer complexity
- Ensures parity between local and cloud runtime
- Makes the ingestion service easier to evolve

#### Ingestion Service Deployment

The `ingest_players` service is deployed as:

- **AWS Lambda (container image)**
- Triggered by S3 `ObjectCreated` events on the `inbox/` prefix

**Deployment flow:**

1. Build Docker image locally
2. Push image to ECR
3. Apply Terraform to update Lambda

Local ingestion (used in earlier steps) mirrors the same logic as the Lambda runtime.

#### API Service Deployment

The `leaderboard-api` service is deployed as:

- **AWS Lambda** (ZIP-based or container-based, depending on dependencies)
- Fronted by **API Gateway** (public)
- Protected by basic rate limiting

Athena is used as the initial query engine and may be replaced later.

### Project Layout (Conceptual)

**Application code:**

- Ingestion logic
- API logic

**Infrastructure code:**

- Terraform definitions
- IAM policies
- Event wiring

Application code does not create or manage AWS resources directly.

### Why This Matters for Contributors and Tooling

This repository intentionally avoids:

- Manual AWS console setup
- Ad-hoc IAM policies
- Environment-specific configuration

**Any developer with Docker, Terraform, and AWS credentials should be able to:**

- Deploy the infrastructure
- Deploy the ingestion service
- Tear everything down safely

## Query Behavior

The "current" snapshot is defined as the **latest snapshot date available** for a given kingdom.

**Leaderboards supported:**

- Top 100 DKP
- Top 100 Kills
- Top 100 Deaths

Queries are partitioned by `kingdom` and `snapshot_date`.

## Development Approach

This project is built incrementally.

### Step 1

Project structure, module layout, local runner, and test scaffolding.

### Step 2

S3 key parsing and output key construction.

### Step 3

Local ingestion logic:

- CSV/JSON reading
- Validation
- Parquet writing

### Step 4 (current)

Infrastructure setup using Terraform:

- S3 bucket
- ECR repository
- Ingestion Lambda (Docker-based)
- IAM permissions
- S3 event triggers

### Later Steps

May add:

- Athena table definitions
- API query optimization
- Precomputed leaderboards
- Multi-kingdom enablement
- Change diffs
- Optional database materialization

## Design Philosophy

- **S3 is the source of truth**
- **Infrastructure is code**
- **Lambdas are stateless**
- **Containers over ZIPs** for heavy dependencies
- **Athena is used only where it makes sense**
- **Everything is designed to be replaceable, not rewritten**

## Status

This is an intentionally incremental POC designed to evolve into a production-grade system without architectural rewrites.
