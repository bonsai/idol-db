# idol-db

アイドル領域の**公開データを正規化し、分析のための基盤として提供するリポジトリ**。

## Role

- `idol-lab` — 理論・民俗学・概念・文化研究
- `idol-research` — 実証研究・マーケティング・分析・研究コード
- `idol-playlist` — 音楽研究・プレイリスト
- `idol-db` — canonical public data / crawler / schema / API

## Principle

`idol-db` のデータ原料は、公開情報として提供されているデータである。

`idol-db` は公開情報を取得・正規化・検証し、再利用可能な canonical data として保持する。
**商品そのものは raw public data ではなく、そこから生成される分析結果である。**

```text
Public Data
    ↓
idol-research
    ↓ observe / normalize
idol-db
    ↓
music-bigdata / idol-playlist / BQML
    ↓ analyze
Analysis Results
    ↓
API / SaaS
```

## Structure

```text
crawler/  # external source collectors / normalization
schema/   # canonical data schemas
data/     # canonical structured public data
api/      # API contract / implementation
rss/      # generated feeds
docs/     # architecture and product boundary
```

## Ownership

`idol-lab` に残すのは、理論・民俗学・概念・解釈・ontology。
`idol-research` は、研究設計・観測・マーケティング・分析を担当する。
`idol-playlist` は、楽曲ランキング・プレイリスト研究を担当する。
`music-bigdata` は、音楽データの DS / ML / BQML / 分析を担当する。
`idol-db` は、公開データの canonical layer とそのインターフェースを担当する。

## Provenance

データには可能な限り `source`, `source_url`, `accessed_at`, `retrieved_at` を保持する。

公開データを分析商品として利用する場合も、原典の利用規約・ライセンス・帰属表示などを個別に確認する。

## Product boundary

> **Public data is the input. Analysis is the product. API/SaaS is the delivery mechanism.**

raw data の再販売を中心にせず、継続的な観測・集計・比較・特徴量化・モデル化によって得られる分析結果を価値の中心とする。
