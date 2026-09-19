# Idol Data API

`idol-db` exposes canonical public data through a stable API boundary.

## Role

```text
Public sources
      ↓
   idol-db
      ├─ canonical public data
      ├─ schema / provenance
      └─ API contract
             ↓
      analysis repositories
             ↓
       analysis results
             ↓
          SaaS / API
```

The API is designed for loose coupling. Consumers use JSON responses and the documented contract rather than importing internal implementation code.

## Consumers

- `idol-research` — research and observations
- `idol-playlist` — rankings and playlist-oriented aggregation
- `music-bigdata` — data science, ML, BQML and analysis
- `bqml-ga4` — behavioral and marketing analysis
- future Idol SaaS — delivery of derived analysis results

## Data API

Current canonical-data resources include:

- `GET /events`
- `GET /idols`
- `GET /groups`
- `GET /observations`
- `GET /songs`
- `GET /rankings`
- `GET /trends`
- `GET /features`

See [CONTRACT.md](./CONTRACT.md) for the interface definition.

## Product API

A future commercial API should primarily expose **derived analysis results**, for example:

- rankings
- trend signals
- interest scores
- song / artist comparisons
- similarity
- market aggregates
- model outputs
- research reports

The canonical public-data API and the commercial analysis API are separate boundaries.

## Product flow

**observe → normalize → analyze → expose → subscribe**

`idol-db` does not become the paid product merely because it has an API. The paid value is the analysis generated downstream from public data.
