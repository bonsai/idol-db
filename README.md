# idol-db

アイドル領域の**正規データ・Schema・Provenance・API**を管理するリポジトリ。

## Role

- `idol-lab` — 理論・民俗学・概念・文化研究
- `idol-research` — 実証研究・マーケティング・分析・コード
- `idol-playlist` — 音楽研究・プレイリスト
- `idol-db` — canonical data / schema / API

## Principle

構造化された事実データは `idol-db` を正本とする。
研究・アプリ側は必要なデータを API 経由で利用し、独自に canonical DB を持たない。

## Planned structure

```text
schema/   # canonical data schemas
data/     # canonical structured data
api/      # API contract / implementation
```

## Provenance

データには可能な限り `source`, `source_url`, `accessed_at`, `retrieved_at` を保持する。
未検証の情報を canonical fact に昇格させない。
