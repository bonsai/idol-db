#!/usr/bin/env python3
"""idol-db AW growth loop.

Canonical data lives in data/*.jsonl.
This driver is intentionally small: collectors can be added incrementally.
Each run should append observations, normalize entities, validate JSONL,
and rebuild derived indexes without making SQLite the source of truth.
"""
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FILES = [
    "events.jsonl",
    "artists.jsonl",
    "groups.jsonl",
    "venues.jsonl",
    "providers.jsonl",
    "observations.jsonl",
    "sources.jsonl",
    "hypotheses.jsonl",
    "marketing.jsonl",
]

def validate_jsonl():
    errors = []
    for name in FILES:
        path = DATA / name
        if not path.exists():
            continue
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"{name}:{n}: {exc}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return False
    return True

def main():
    DATA.mkdir(parents=True, exist_ok=True)

    # Collectors are deliberately optional at first.
    # Add source-specific Python modules under crawler/ as they become ready.
    for script in sorted((ROOT / "crawler").glob("*.py")) if (ROOT / "crawler").exists() else []:
        if script.name.startswith("_"):
            continue
        subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)

    if not validate_jsonl():
        return 1

    # SQLite is a rebuildable derived index, never the canonical store.
    rebuild = ROOT / "scripts" / "rebuild_sqlite.py"
    if rebuild.exists():
        subprocess.run([sys.executable, str(rebuild)], cwd=ROOT, check=True)

    print("idol-db AW loop: JSONL validated")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
