# Event Data Architecture

## Principle

**イベントそのものと、イベントをどう探すかを分離する。**

idol-db is the canonical data layer. It does not own the research UI or presentation.

## Three layers

Go crawls. Python decides. TypeScript presents.

```
Go
  crawl / harvest
      ↓
raw observations
      ↓
Python
  select / normalize / resolve / score
      ↓
published JSONL
      ↓
TypeScript
  read-only UI
```

### Go — Crawl

Go is the collection machine.

- crawl domains and source URLs
- fetch HTML / RSS / JSON / API
- retain URL, fetched_at and raw payload metadata
- crawl repeatedly
- do not make the final event/no-event decision
- discard as little as practical

**Goal: maximum recall.**

### Python — Select

Python is the semantic/selection layer.

- extract event candidates
- normalize date, venue, performers, admission
- entity resolution
- deduplication
- classify free / 1D / reservation conditions
- assign provenance and confidence
- publish canonical JSONL
- evaluate selection rules

**Goal: precision with explainable decisions.**

### TypeScript — Live

idol-live is a thin presentation layer.

- read generated JSONL
- search/filter
- calendar/map/card UI
- no crawler
- no research logic
- no canonical DB
- no mutation of source data

**Goal: make the data useful and beautiful.**

## Discovery Intelligence

This is separate from Event data.

It records **how to find idol events**:

- source/domain
- entry URLs
- discovery method
- keywords
- URL patterns
- crawl strategy
- update frequency
- observed yield
- noise
- coverage
- reliability
- notes
- provenance

Example:

```json
{
  "source_id": "source:livepocket",
  "domain": "livepocket.jp",
  "source_type": "ticket_platform",
  "entry_urls": ["https://livepocket.jp/"],
  "discovery_method": ["category_search", "keyword_search", "venue_search"],
  "search_keywords": ["アイドル", "ライブ", "無銭", "フリー"],
  "crawl_strategy": "category -> event detail -> pagination"
}
```

Discovery Intelligence answers **how to search**. Event data answers **what the event is**.

## Boundaries

| Asset | Owner | Purpose |
|---|---|---|
| source/discovery knowledge | idol-research | how to find |
| raw crawl observations | idol-db | what was fetched |
| canonical events JSONL | idol-db | what the event is |
| analysis/selection rules | idol-research | why selected |
| UI | idol-live | how users see it |

## Publication contract

The UI consumes only generated artifacts such as:

```
published/events.jsonl
published/artists.jsonl
published/venues.jsonl
```

Internal crawler/research implementation can change without making idol-live a data system.

## Growth loop

```
discovery knowledge
   ↓
Go crawler
   ↓
raw observations
   ↓
Python selection
   ↓
canonical events
   ↓
research / live
   ↓
evidence about useful sources
   ↓
better discovery knowledge
   ↺
```
