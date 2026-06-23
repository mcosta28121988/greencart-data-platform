# ADR-001: Synthetic generator over public dataset

## Status
Accepted

## Context
The platform needs a realistic e-commerce dataset. The two options
were downloading a public dataset or building a generator.

Public datasets have a few problems for this use case. The data
models tables rather than behaviour — you get rows, but no sense of
why those rows exist. There is no repeat buyer logic, no churn, no
cancellation patterns. The numbers are what they are and you cannot
change them.

The platform also needs to operate across Australia, the United
States and the United Kingdom with local currencies. No public
dataset covers all three in a way that felt realistic enough to
build meaningful analytics on top of.

## Decision
Build a synthetic business simulation engine that models behaviour
first and produces data as a byproduct.

## Rationale
The core idea is that a customer does things over time — registers,
browses, buys, comes back, eventually stops. If the data reflects
that, the analytics built on top of it reflect that too. Cohort
retention means something. Repeat purchase rate means something.
Churn shows up as a pattern rather than a random gap in the data.

Reproducibility was also important. A fixed seed produces identical
output every time, which means the entire platform can be rebuilt
from scratch by anyone who clones the repo. A downloaded CSV cannot
guarantee that.

## Consequences
Building the generator adds time before the platform work starts.
The upside is that the data shape is fully controlled — volume,
countries, currencies, business scenarios — and can be adjusted
without touching the platform layer.

The simulator data will never be as messy as real operational data.
Edge cases that appear naturally in production systems have to be
explicitly modelled here.