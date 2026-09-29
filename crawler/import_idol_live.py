#!/usr/bin/env python3
"""Import the current idol-live canonical event feed into idol-db JSONL.

The importer is idempotent by event_id. Existing records are preserved.
Each imported record also emits an observation so the database grows
longitudinally rather than overwriting history.
"""
from pathlib import Path
from urllib.request import urlopen
import json
import hashlib
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
EVENTS = DATA / "events.jsonl"
OBS = DATA / "observations.jsonl"
URL = "https://raw.githubusercontent.com/bonsai/idol-live/main/.data/events.json"

def load_jsonl(path):
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]

def event_id(e):
    raw = "|".join(str(e.get(k, "")) for k in ("date", "start_at", "venue", "title"))
    return "event:" + hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]

def main():
    DATA.mkdir(parents=True, exist_ok=True)
    with urlopen(URL, timeout=30) as r:
        payload = json.loads(r.read().decode("utf-8"))

    existing = {x.get("event_id"): x for x in load_jsonl(EVENTS)}
    observations = load_jsonl(OBS)
    seen_obs = {(x.get("event_id"), x.get("source_url"), x.get("observed_at")) for x in observations}
    now = datetime.now(timezone.utc).isoformat()

    added = 0
    observed = 0
    for event in payload.get("events", []):
        eid = event_id(event)
        event = dict(event)
        event["event_id"] = eid
        event["source"] = "idol-live"
        existing[eid] = event
        added += 1

        key = (eid, event.get("source_url"), now[:10])
        if key not in seen_obs:
            observations.append({
                "observation_id": "obs:" + hashlib.sha1(("|".join(map(str, key))).encode()).hexdigest()[:16],
                "event_id": eid,
                "source": "idol-live",
                "source_url": event.get("source_url"),
                "observed_at": now,
                "facts": {
                    "price": event.get("admission", {}).get("price"),
                    "free": event.get("free_status", {}).get("free"),
                    "drink_required": event.get("free_status", {}).get("drink_required"),
                    "reservation_required": event.get("free_status", {}).get("reservation_required")
                }
            })
            observed += 1

    EVENTS.write_text("".join(json.dumps(x, ensure_ascii=False, separators=(",", ":")) + "\n" for x in existing.values()), encoding="utf-8")
    OBS.write_text("".join(json.dumps(x, ensure_ascii=False, separators=(",", ":")) + "\n" for x in observations), encoding="utf-8")
    print(f"imported events={added} observations_added={observed}")

if __name__ == "__main__":
    main()
