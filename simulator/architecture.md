# GreenCart Simulator — Architecture

## Purpose
Generate realistic synthetic e-commerce data for the GreenCart
Modern Data Platform. Replaces public datasets with a reproducible,
configurable business simulation engine.

## Design principles
- Business-first: models behaviour, not tables
- Deterministic: same seed always produces identical output
- Configurable: scale, country, scenario via CLI
- Extensible: new domains added without breaking existing ones

## v0.1 scope
Entities: Customers, Products, Orders, Payments
Output: Apache Parquet
Countries: AU, US, UK

## Component overview
[Diagram to be added end of week 2]