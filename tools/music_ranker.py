#!/usr/bin/env python3
"""Deterministic six-axis idol-song ranking engine."""
import json
from pathlib import Path

WEIGHTS = {"M": 0.25, "C": 0.15, "U": 0.20, "L": 0.20, "O": 0.10, "R": 0.10}
AXES = tuple(WEIGHTS)


def load_jsonl(path):
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def score(row):
    values = {axis: max(0, min(100, float(row.get(axis, 0)))) for axis in AXES}
    return round(sum(values[a] * WEIGHTS[a] for a in AXES), 2)


def rank(rows, limit=100):
    ranked = []
    for row in rows:
        item = dict(row)
        item.update({a: round(max(0, min(100, float(item.get(a, 0)))), 2) for a in AXES})
        item["score"] = score(item)
        ranked.append(item)
    ranked.sort(key=lambda x: (-x["score"], x.get("artist", ""), x.get("title", ""), x.get("track_id", "")))
    for i, item in enumerate(ranked[:limit], 1):
        item["rank"] = i
    return ranked[:limit]


def main():
    root = Path(__file__).resolve().parents[1]
    source = root / "data/music/2026/scores.jsonl"
    out = root / "playlists/2026-best100.json"
    rows = load_jsonl(source)
    ranked = rank(rows, 100)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "year": 2026,
        "method": "six-axis-weighted-score",
        "weights": WEIGHTS,
        "count": len(ranked),
        "tracks": ranked,
    }
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"generated {out}: {len(ranked)} tracks")


if __name__ == "__main__":
    main()
