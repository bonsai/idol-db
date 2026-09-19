# Idol Data API Contract

`idol-db` is the canonical public-data source for the Idol Data ecosystem.

## Purpose

Provide structured public idol, music, event, observation, ranking, trend, and feature data to independent clients.

The API is the interface between the canonical database and downstream research / analysis systems.

## Resources

### Core

- `GET /events`
- `GET /events/:id`
- `GET /idols`
- `GET /idols/:id`
- `GET /groups`
- `GET /groups/:id`
- `GET /observations`
- `GET /observations/:id`

### Music

- `GET /songs`
- `GET /songs/:id`
- `GET /rankings`
- `GET /trends`
- `GET /features`

## Query principles

Resources should support machine-readable filtering where available:

- `date` / `from` / `to`
- `artist_id` / `group_id`
- `song_id`
- `source`
- pagination

Responses are JSON.

## Data boundary

`idol-db` owns:

- canonical structured public data
- provenance
- schema
- public-data API contract

It does not own:

- general-purpose music ML
- customer-specific analytics
- SaaS presentation
- the commercial analysis product

Those belong downstream.

## Analysis boundary

```text
idol-db
   ↓ public data API
idol-playlist / music-bigdata / BQML
   ↓
analysis artifacts
   ↓
commercial analysis API
   ↓
SaaS
```

Analysis artifacts are the product layer. Examples include rankings, trend signals, scores, similarity, market aggregates, predictions, and research reports.

## Loose coupling

Clients must depend on the API contract or exchanged artifacts, not on internal Python modules or repository files.

The implementation remains loosely coupled from canonical data files.

## Commercial principle

**Public data is the input. Analysis is the product. API/SaaS is the delivery mechanism.**

A commercial service may add authentication, quotas, historical depth, derived features, reports, and customer-specific analysis.

Before commercial use, check the applicable terms, licenses, source attribution requirements, and any restrictions attached to each public source.
