# ADR-002: Snowflake warehouse design and role hierarchy

## Status
Accepted

## Context
The platform needs a Snowflake setup that separates concerns cleanly
across the ingestion, transformation and serving layers. The naive
approach — one database, one schema, one user doing everything — works
for a single developer but creates problems as soon as more than one
process touches the warehouse. Permissions become implicit, mistakes
in one layer can affect another, and there is no clear boundary
between raw data and transformed data.

The platform also needs to run automated processes (the ingestion
pipeline, dbt) without using a personal admin account. Personal
accounts have broad permissions, get recycled when people leave, and
make audit trails meaningless.

## Decision
Three databases (RAW, DEV, PROD), four roles (SYSADMIN, LOADER,
TRANSFORMER, REPORTER), and one service account per automated
function.

## Rationale
**Three databases, not one**
RAW holds exactly what the simulator produces — no transformations,
no business logic. DEV is where dbt runs during development. PROD
is what dashboards read. This means a broken dbt model in DEV
cannot affect a dashboard reading from PROD, and raw data is never
overwritten by a transformation gone wrong.

**Role per function, not per person**
Each role owns exactly what it needs and nothing else:

- LOADER writes to RAW.GREENCART only. It cannot read DEV or PROD.
- TRANSFORMER reads RAW, writes to DEV and PROD. It cannot create
  users or modify roles.
- REPORTER reads PROD.MARTS only. It cannot see raw data or
  intermediate models.

This is the principle of least privilege applied to a data warehouse.
If the ingestion pipeline is compromised, the blast radius is limited
to RAW. If a reporting tool is misconfigured, it cannot touch source
data.

**Service account per automated function**
The ingestion pipeline runs as GREENCART_INGESTION_SVC, a non-human
service account of TYPE = SERVICE. This means no password login, no
Snowflake UI access, and key-pair authentication only. The account
is tied to the LOADER role and nothing else.

Using a personal admin account for automated pipelines is a common
shortcut that creates real problems: the pipeline breaks when the
person leaves, audit logs show a human name for automated actions,
and the process has far more permissions than it needs.

## Consequences
**Positive:**
- Clear boundary between raw, development and production data
- Broken transformations in DEV cannot affect PROD
- Automated processes run with minimum required permissions
- Audit trail distinguishes human actions from pipeline actions
- Easy to extend: adding a new service (e.g. dbt Cloud) means
  creating a new service account and granting an existing role

**Negative:**
- More upfront setup than a single database approach
- Role grants need to be re-applied when new tables are created
  in RAW (mitigated by FUTURE TABLES grants)
- Key-pair authentication adds setup complexity compared to
  password auth

## Alternatives considered
**Single database with schema separation (RAW_SCHEMA, DEV_SCHEMA,
PROD_SCHEMA):** Simpler to set up but permissions are harder to
isolate cleanly. A role with USAGE on the database can potentially
see all schemas. Separate databases make the boundary explicit.

**One role for everything:** Common in small projects. Works until
something goes wrong — a bad dbt run that truncates a table it
should not have touched, or a reporting tool that has write access
it should never have had.

**Password authentication for service accounts:** Simpler initially
but passwords expire, get rotated inconsistently, and can be shared.
Key-pair authentication is the Snowflake-recommended approach for
non-human accounts and is required for TYPE = SERVICE users anyway.
