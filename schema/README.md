# Schema

## Source of truth

Python + Pydantic が canonical schema の source of truth。
JSON Schema / JSONL / OpenAPI は Python model から生成する。

## Lang 三兄弟

| layer | role |
|---|---|
| LangChain | Pydantic schema に沿った structured output / extraction |
| LangGraph | observe -> normalize -> resolve -> validate -> persist の状態遷移 |
| LangSmith | trace / dataset / evaluation / schema drift の監視 |

public sources
  -> LangChain structured extraction
  -> LangGraph observe / normalize / resolve / validate
  -> Pydantic Canonical Schema
  -> JSONL / API / DB
  -> LangSmith trace + eval
  -> schema improvement
  -> loop

## Core entities

- Idol
- Group
- Venue
- Event
- Observation
- Hypothesis
- Feature
- Recommendation

Fact と Inference を分離する。

- Observation.facts = 観測した事実
- Hypothesis = そこから立てた仮説
- Feature = 分析用に生成した値
- Recommendation = 利用系で生成した結果

推薦や分析結果が canonical data を汚染しない構造にする。

## Growth loop

source
 -> observation
 -> schema validation
 -> entity resolution
 -> canonical data
 -> feature / hypothesis
 -> analysis / recommendation
 -> new observations
 -> schema evolution

Schema version は Pydantic model を基準に管理し、破壊的変更は version を上げる。
