# ADR-003: dbt layered architecture

## Status
Accepted

## Context
The transformation layer needs a structure that makes it clear
where business logic lives, who owns each layer, and what
guarantees each layer provides to its consumers.

A single models/ folder with no structure works for small projects
but breaks down quickly — models start doing too many things,
business logic gets duplicated, and it becomes impossible to know
what a downstream model can safely depend on.

## Decision
Three layers: staging, intermediate, marts. Each layer has a
single responsibility and a strict contract with the layers
around it.

## Rationale

**Staging — one model per source table**
Staging models do exactly three things: select from the raw
source, rename columns to snake_case, and cast types. No business
logic. No joins. No filtering. The output of a staging model is
a clean, typed representation of what the source sent us.

This matters because it creates a single place to fix source
issues. If a column name changes in RAW, you fix one staging
model and nothing downstream breaks.

**Intermediate — business logic lives here**
Intermediate models join staging models together and apply
business rules. An order enriched with its customer's country,
an order line with its product category, a customer flagged as
a repeat buyer. These models are not exposed to dashboards —
they exist to keep mart models readable.

**Marts — consumer-facing, pre-aggregated**
Mart models are what dashboards and analysts query. They are
wide, denormalised, and optimised for reads. A mart model
should answer a business question without requiring the consumer
to write joins.

Mart models are materialised as tables in Snowflake, not views.
This means query performance is predictable regardless of the
complexity of the upstream logic.

## Consequences
**Positive:**
- Business logic has one home — intermediate models
- Staging models are easy to test and reason about independently
- Mart models are fast because they are pre-materialised tables
- dbt lineage graph shows a clear left-to-right flow from
  source to serving layer

**Negative:**
- More files than a flat structure
- Intermediate models add a layer of indirection that requires
  understanding the full DAG to trace a metric back to its source

## Layer contracts

| Layer        | Reads from        | Materialisation | Schema       |
|--------------|-------------------|-----------------|--------------|
| Staging      | RAW sources       | View            | DEV.STAGING  |
| Intermediate | Staging models    | View            | DEV.INTERMEDIATE |
| Marts        | Intermediate      | Table           | DEV.MARTS    |

No layer may skip a level. Marts reference intermediate, not
staging. Intermediate references staging, not raw sources
directly.
