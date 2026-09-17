# AW — Idol Live Discovery

アイドルライブは「イベントを探す」だけでなく、Event / Venue / Provider / Organizer / Performer / Ticket をつなぐ Asset Discovery として扱う。

## 基本方針

- イベントは価格に関係なく可能な限り crawl / discover する
- canonical DB には収集したイベントを保持する
- 公開 Discovery の掲載対象は **500円以下**
- 500円を超えるイベント、価格不明イベントは収集DBには残すが、公開掲載対象から除外または `要確認` とする
- 500円という公開基準は法律上の転載許可ラインではなく、このサービス独自の掲載基準
- source URL / accessed_at / retrieved_at / confidence を保持する
- 元サイトの文章・画像を大量転載せず、事実項目と出典URLを中心に正規化する

## Search Sources

一次・準一次ソースを横断する。

- TIGET
- LivePocket
- チケットぴあ等のプレイガイド
- アイドル運営・所属事務所の公式サイト
- ライブハウス・会場公式サイト
- 主催者公式ページ
- その他、公開イベント情報源

TIGET は実際に「アイドル」をカテゴリとして提供しており、イベント検索・チケット販売・予約を提供している。検索対象の重要なProviderとして扱う。

## Semantic Search

自然言語 Intent を以下の Facet に分解する。

```text
Intent
  ↓
Genre / Idol / Performer
Price
Time
Area
Venue
Provider
Organizer
Event type
  ↓
Search Graph
  ↓
Candidate Events
  ↓
Normalize
  ↓
Dedupe
  ↓
Verify
  ↓
Asset / Relation
  ↓
Public Discovery (<=500円)
```

## Asset Graph

```text
Provider
   ↓ lists
Event ← organized_by → Organizer
   ↓ held_at
Venue
   ↓ part_of / contains
Venue Complex → Hall / Space
   ↑
Performer / Idol
   ↓ appears_in
Event
   ↓ has_ticket
Ticket
   ↓ verified_by
Source
```

## Query Examples

- 「新宿で今日の無銭アイドルライブ」
- 「500円以下のアイドルライブ」
- 「TIGETのアイドルライブ」
- 「女性アイドルで今週」
- 「この会場で過去にやったアイドルライブ」
- 「特典会ありの無料ライブ」
- 「東新宿・新宿・池袋で500円以下」

## Price Policy

価格はイベント全体を単純に一つの数字へ潰さない。

```text
ticket_options[]
  ├─ price
  ├─ label
  ├─ condition
  ├─ drink_required
  └─ source_url
```

例えば「無銭 0円 + 1D」「優先 1000円 + 1D」のような複数券種がある場合、0円券を正しく識別する。

公開掲載判定:

```text
eligible_for_public =
  exists(ticket_option.price <= 500)
```

ただし、必須ドリンク代など追加費用は別フィールドで表示し、総支払額を隠さない。

## Time Model

```text
history → latest → now → action
```

- `history`: 過去イベント・過去観測
- `latest`: 最新crawl / 最新イベント情報
- `now`: 現在公開すべきイベント状態
- `action`: 検索・通知・予約ページへの導線

## STAGE-Search Connection

```text
idol-db
   ↓ normalized Event + Asset
STAGE-Search
   ↓
Event × Venue cross-domain index
   ↓
AW semantic discovery
   ↓
500円以下の公開イベント
```

`idol-db` はアイドル領域の canonical source、`stage-search` はジャンル横断の検索・統合レイヤーとする。
