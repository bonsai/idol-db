# Idol Data API

'idol-db' exposes canonical structured idol data through a stable API boundary.

## Role

    sources
      ↓
    idol-db
      ├─ canonical data
      ├─ schema
      └─ API contract
           ↓
       consumers

The API is designed for loose coupling. Consumers use JSON responses and the documented contract rather than importing internal implementation code.

## Consumers

- `idol-research` — research and observations
- `idol-playlist` — rankings and playlist-oriented aggregation
- `music-bigdata` — data science and ML
- `bqml-ga4` — behavioral and marketing analysis
- SaaS clients — search, comparison, trends, and dashboards

## Initial endpoints

- `GET /events`
- `GET /idols`
- `GET /groups`
- `GET /observations`
- `GET /songs`
- `GET /rankings`
- `GET /trends`
- `GET /features`

See [CONTRACT.md](./CONTRACT.md) for the interface definition.

## Product

The API is the delivery layer for an Idol Data product:

**observe → normalize → analyze → expose → subscribe**

Commercial API plans can later add authentication, quotas, historical depth, derived features, and premium datasets without changing the canonical database boundary.
