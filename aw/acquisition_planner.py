#!/usr/bin/env python3
"""Seed -> acquisition plan -> decision record.

Pure-stdlib, deterministic first-pass planner. It ranks acquisition methods
from source capability metadata and never bypasses robots constraints.
Input/output are JSON so the planner can be called by AW/WF runners.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone

METHODS = {
    "api": {"gain": 1.00, "cost": 0.20, "risk": 0.10},
    "rss": {"gain": 0.85, "cost": 0.15, "risk": 0.10},
    "sitemap": {"gain": 0.80, "cost": 0.15, "risk": 0.10},
    "structured_data": {"gain": 0.75, "cost": 0.20, "risk": 0.15},
    "repository": {"gain": 0.90, "cost": 0.15, "risk": 0.10},
    "archive": {"gain": 0.60, "cost": 0.35, "risk": 0.20},
    "crawler": {"gain": 0.70, "cost": 0.60, "risk": 0.35},
    "manual": {"gain": 0.50, "cost": 0.80, "risk": 0.05},
}


def score(method: str, source: dict) -> float:
    spec = METHODS[method]
    access = source.get("access", {})
    robots = access.get("robots", "unknown")
    if robots == "denied" and method == "crawler":
        return float("-inf")
    provenance = float(source.get("provenance_quality_score", 0.5))
    freshness = float(source.get("freshness_score", 0.5))
    gain = spec["gain"] * (0.6 + 0.4 * provenance) * (0.6 + 0.4 * freshness)
    return gain / (spec["cost"] + spec["risk"] + 0.01)


def plan(payload: dict) -> dict:
    seed_id = payload["seed_id"]
    sources = payload.get("sources", [])
    candidates = []
    for source in sources:
        allowed = set(source.get("methods", []))
        for method in METHODS:
            if method not in allowed:
                continue
            candidates.append({
                "source_id": source.get("source_id"),
                "method": method,
                "score": score(method, source),
                "source_url": source.get("source_url"),
            })

    candidates.sort(key=lambda x: x["score"], reverse=True)
    selected = candidates[0] if candidates else None
    now = datetime.now(timezone.utc).isoformat()
    return {
        "seed_id": seed_id,
        "search_domain": payload.get("search_domain", []),
        "queries": payload.get("queries", []),
        "methods": sorted({x["method"] for x in candidates}),
        "locations": payload.get("locations", []),
        "term_scores": payload.get("term_scores", []),
        "search_plan": candidates,
        "decision": {
            "decision_id": f"decision:{seed_id}:{now}",
            "selected_action": selected,
            "reason": [
                "rank acquisition methods by expected evidence gain versus cost/risk",
                "respect source capability metadata",
                "never bypass robots.txt",
            ],
        },
        "provenance": {"planner": "idol-db/aw/acquisition_planner.py", "created_at": now},
    }


def main() -> None:
    payload = json.load(sys.stdin)
    json.dump(plan(payload), sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
