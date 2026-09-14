#!/usr/bin/env python3
"""Deterministically generate data/feature-map.json from canonical idol data.

Canonical data is the source of truth. RAG may contribute only explicitly
structured `features.observed` evidence; no free-text inference is performed.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "idols.json"
TAXONOMY = ROOT / "taxonomy" / "idol-features.yaml"
RAG_DIR = ROOT / "rag" / "people"
OUTPUT = ROOT / "data" / "feature-map.json"

AXES = {
    "expression": {"vocal", "dance", "acting", "comedy", "art", "language", "character"},
    "body": {"visual", "costume", "body_expression", "gender_expression", "norm_deviation"},
    "performance": {"live", "contact", "streaming", "sns", "content_creation"},
    "relationship": {"fan_proximity", "group_relation", "collaboration", "community"},
    "identity": {"mainstream", "underground", "alternative", "conceptual", "local", "cross_boundary"},
    "career": {"idol_only", "comedian", "actor", "artist", "writer", "entrepreneur", "multi_role"},
    "market": {"cheki", "live", "streaming", "subscription", "goods", "fanclub", "advertising"},
    "mobility": {"join", "graduate", "transfer", "rename", "rejoin", "solo"},
    "temporal": {"active", "former", "transition", "intermittent"},
    "deviation": {"body", "career", "expression", "relationship", "institution", "market"},
}

DEVIATION_NORMALIZE = {
    "body-shape": "body",
    "body": "body",
    "career": "career",
    "expression": "expression",
    "relationship": "relationship",
    "institution": "institution",
    "market": "market",
}


def add(features, axis, *values):
    bucket = features.setdefault(axis, set())
    for value in values:
        if value in AXES[axis]:
            bucket.add(value)


def load_json(path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def map_entry(entry):
    observed = {}
    tags = set(entry.get("tags", []))
    roles = set(entry.get("roles", []))
    activities = entry.get("activities", [])

    if "vocal" in roles:
        add(observed, "expression", "vocal")
    if "dance" in roles:
        add(observed, "expression", "dance")
    if "actor" in roles:
        add(observed, "expression", "acting")
        add(observed, "career", "actor")
    if "comedian" in roles or "comedy" in tags:
        add(observed, "expression", "comedy",)
        add(observed, "career", "comedian")
    if "performer" in roles:
        add(observed, "performance", "live")
    if "underground" in tags or "地下アイドル" in tags:
        add(observed, "identity", "underground")
    if "mainstream" in tags:
        add(observed, "identity", "mainstream")
    if "alternative" in tags:
        add(observed, "identity", "alternative")
    if "conceptual" in tags:
        add(observed, "identity", "conceptual")

    non_idol = {
        a.get("type") for a in activities
        if a.get("type") and a.get("type") != "idol"
    }
    if non_idol:
        add(observed, "career", "multi_role")

    idol_statuses = {
        a.get("status") for a in activities if a.get("type") == "idol"
    }
    if "active" in idol_statuses:
        add(observed, "temporal", "active")
    if "ended" in idol_statuses:
        add(observed, "temporal", "former")
    if "active" in idol_statuses and "ended" in idol_statuses:
        add(observed, "temporal", "transition")

    # Mobility/transition is emitted only when explicitly represented in canonical tags.
    if "activity-transition" in tags:
        add(observed, "mobility", "join")
        add(observed, "deviation", "institution")

    for raw in entry.get("deviation_axes", []):
        normalized = DEVIATION_NORMALIZE.get(raw)
        if normalized:
            add(observed, "deviation", normalized)

    return observed


def merge_rag_observed(result, person_id):
    """Merge only explicit structured RAG observations for the same person."""
    if not RAG_DIR.exists():
        return
    for path in sorted(RAG_DIR.glob("*.json")):
        try:
            doc = load_json(path)
        except (OSError, json.JSONDecodeError):
            continue
        if doc.get("id") != person_id:
            continue
        observed = doc.get("features", {}).get("observed", {})
        if not isinstance(observed, dict):
            continue
        for axis, values in observed.items():
            if axis not in AXES or not isinstance(values, list):
                continue
            for value in values:
                add(result, axis, value)


def serialize(features):
    return {
        axis: sorted(values)
        for axis, values in sorted(features.items())
        if values
    }


def main():
    data = load_json(INPUT)
    entities = []
    for entry in data.get("entries", []):
        person_id = entry["id"]
        observed = map_entry(entry)
        merge_rag_observed(observed, person_id)
        entities.append(
            {
                "id": person_id,
                "features": {
                    "observed": serialize(observed),
                    "inferred": {},
                    "hypotheses": [],
                },
                "evidence": [f"idol-db:data/idols.json:{person_id}"],
            }
        )

    output = {
        "_schema_version": "0.2",
        "_description": "Generated multi-axis feature map. Canonical idol data is authoritative; RAG contributes only explicit structured observations.",
        "coordinate_system": "multi-axis categorical",
        "entities": entities,
    }
    OUTPUT.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
