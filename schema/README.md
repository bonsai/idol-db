# Schema

## Schema authority

Schema is **not decided in idol-db**.

The authority is:

`bonsai/idol-research/schema/`

idol-db owns canonical data and generated artifacts. It receives a published
schema mirror from idol-research so collectors and validators can inspect the
same contract locally.

## Distribution

```
idol-research/schema
        |
        | cp + commit + push
        v
idol-db/schema
```

Two consumption modes are supported:

1. **Mirror mode** — copy the schema into idol-db for local/offline use.
2. **Reference mode** — read the canonical schema directly from idol-research,
   preferably pinned to a commit SHA for reproducibility.

The local `models.py` is a generated mirror. Do not edit it by hand.

## Lang 三兄弟

| layer | role |
|---|---|
| LangChain | structured extraction against the published schema |
| LangGraph | observe -> normalize -> resolve -> validate -> persist |
| LangSmith | trace / dataset / evaluation / schema drift |

## Data boundary

- idol-research: schema, discovery intelligence, selection rules, research
- idol-db: raw observations, canonical records, published JSONL
- idol-live: generated JSONL read-only presentation

> Go crawls. Python decides. TypeScript presents.
