# idol-db

アイドル領域の**正規データ・Crawler・Schema・Provenance・API**を管理するリポジトリ。

## Role

- `idol-lab` — 理論・民俗学・概念・文化研究
- `idol-research` — 実証研究・マーケティング・分析・研究コード
- `idol-playlist` — 音楽研究・プレイリスト
- `idol-db` — canonical data / crawler / schema / API

## Principle

構造化された事実データは `idol-db` を正本とする。
データ取得・正規化・検証・公開用APIまでを `idol-db` が責任を持つ。
研究・アプリ側は必要なデータを利用し、独自に canonical DB を持たない。

## Structure

```text
crawler/  # external source collectors / normalization
schema/   # canonical data schemas
data/     # canonical structured data
api/      # API contract / implementation
rss/      # generated feeds
```

## Ownership

`idol-lab` に残すのは、理論・民俗学・概念・解釈・ontology。
`idol-research` は、マーケティング・研究設計・分析・研究コードを担当する。
`idol-playlist` は音楽データとプレイリスト研究を担当する。

## Provenance

データには可能な限り `source`, `source_url`, `accessed_at`, `retrieved_at` を保持する。
未検証の情報を canonical fact に昇格させない。
