# Idol Data API Contract

'idol-db' is the canonical public-data source for the Idol Data API.

## Purpose

Provide structured idol, music, event, observation, ranking, trend, and feature data to independent clients.

The API is the interface between the canonical database and downstream applications such as research tools, analytics, and SaaS.

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

'idol-db' owns canonical structured data and the public API contract.

It does not own:

- general-purpose music ML
- GA4 collection
- customer-specific analytics
- SaaS presentation

Those are downstream consumers.

## Product layers

    idol-db
      ↓ API
    music-bigdata
      ↓ analysis
    bqml-ga4
      ↓ marketing / behavior
    SaaS

## Coupling

Clients must depend on the API contract, not on internal Python modules or repository files.

The implementation remains loosely coupled from canonical data files.

## Productization

The same API can support:

- public endpoints
- rate-limited API access
- API-key access
- paid data plans
- SaaS authentication and quotas

The data license and source attribution requirements must be defined separately before commercial distribution.
