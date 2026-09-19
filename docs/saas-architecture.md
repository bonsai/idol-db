# Analysis SaaS Architecture

## Goal

アイドル領域の公開データそのものを販売するのではなく、公開データから継続的に生成する**分析結果を商品化**する。

> Public data is the input. Analysis is the product. API/SaaS is the delivery mechanism.

## System boundary

```text
                    Public Sources
                         │
                         ▼
                   idol-research
                  observe / normalize
                         │
                         ▼
                      idol-db
              canonical public data API
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
        idol-playlist         music-bigdata
        ranking / playlist    DS / ML / BQML
              │                     │
              └──────────┬──────────┘
                         ▼
                 Analysis Artifacts
                         │
                         ▼
                Commercial API
                         │
                         ▼
                       SaaS
```

## Repository responsibilities

### idol-db

Owns:

- public-data collection and normalization
- canonical schemas
- provenance
- stable public-data API

Does not own:

- customer-specific analysis
- SaaS UI
- commercial product logic

### idol-playlist

Owns music-specific aggregation such as:

- weekly ranking
- monthly aggregation
- playlist matching
- music-interest indicators

### music-bigdata

Owns:

- EDA
- feature engineering
- ML / BQML
- segmentation
- market analysis
- reusable analysis artifacts

### SaaS

Owns:

- customer authentication
- dashboard
- search / compare / trend views
- saved analysis
- reports
- billing / plan limits
- commercial analysis API

## TypeScript application stack

Use the smallest stack that matches the boundary:

- **Next.js** — SaaS web UI and application layer
- **FrourioNext** — typed API / OpenAPI boundary for new TypeScript APIs
- **Hono** — optional edge/lightweight API when a separate Worker endpoint is actually needed

Do not introduce Hono merely because it is available. If FrourioNext already owns the typed application API, Hono is unnecessary overlap.

## API separation

There are two different meanings of API:

### Public-data API

`idol-db`:

```text
GET /songs
GET /artists
GET /events
GET /observations
```

This exposes the canonical public-data layer.

### Commercial analysis API

SaaS:

```text
GET /analysis/rankings
GET /analysis/trends
GET /analysis/scores
GET /analysis/similarity
GET /analysis/market
GET /analysis/reports
```

This exposes derived value.

The commercial API should not simply put a price tag on the raw public-data API.

## First SaaS screen

Start with one useful dashboard rather than a full CRM:

```text
Idol Music Intelligence

[ Rising Songs ]
[ Artist Trends ]
[ Song Compare ]
[ Market Trends ]

period: 7d / 30d / 90d

song        score   trend   rank
---------------------------------
...
```

The first MVP should prove that an analysis result is useful before adding billing, teams, or complex account management.

## Artifact contract

Analysis repositories exchange JSON / JSONL artifacts rather than importing each other's Python code.

Example:

```json
{
  "song_id": "xxx",
  "observed_at": "2026-09-19",
  "score": 82.4,
  "rank": 7,
  "trend_7d": 0.23,
  "trend_30d": 0.41
}
```

This keeps collection, analysis, and product delivery loosely coupled.

## Product loop

```text
observe
  ↓
normalize
  ↓
analyze
  ↓
validate
  ↓
publish artifact
  ↓
API
  ↓
SaaS
  ↓
customer usage
  ↓
new research questions
  └──────────────→ analyze
```

The SaaS is therefore not the center of the data ecosystem. It is the delivery surface for continuously improved analysis.
