#!/usr/bin/env python3
"""Validate, import and export the idol-live event dataset."""

import json
import sqlite3
import sys
from hashlib import sha1
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / ".data"
EVENTS_JSON = DATA / "events.json"
DB = DATA / "events.db"
SCHEMA = DATA / "schema.sql"


def load_document():
    data = json.loads(EVENTS_JSON.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return {"dataset": "idol_free_live", "events": data}
    if isinstance(data, dict) and isinstance(data.get("events"), list):
        return data
    raise ValueError("events.json must be an array or an object containing an events array")


def load_events():
    data = load_document()
    events = data["events"]
    for i, event in enumerate(events, 1):
        for key in ("date", "title", "venue"):
            if not event.get(key):
                raise ValueError(f"event #{i}: missing {key}")
    return data, events


def event_id(event, index):
    return event.get("id") or f"event-{event['date']}-{index:04d}"


def stable_id(prefix, value):
    return prefix + sha1(value.encode("utf-8")).hexdigest()[:12]


def build_db(events):
    if DB.exists():
        DB.unlink()
    conn = sqlite3.connect(DB)
    conn.executescript(SCHEMA.read_text(encoding="utf-8"))

    for index, event in enumerate(events, 1):
        eid = event_id(event, index)
        venue_name = event["venue"]
        vid = stable_id("venue-", venue_name)
        conn.execute("INSERT OR IGNORE INTO venues(id,name,area) VALUES(?,?,?)", (vid, venue_name, event.get("area")))

        budget = event.get("budget") or {}
        admission_obj = event.get("admission") or {}
        free_obj = event.get("free_status") or {}
        metadata = event.get("metadata") or {}
        admission = budget.get("admission_price", admission_obj.get("price"))
        drink = budget.get("drink_price")
        total = budget.get("total_price")
        if total is None and admission is not None and drink is not None:
            total = admission + drink
        status = "unknown" if total is None else ("under" if total < 1000 else "over")

        conn.execute(
            """INSERT INTO events
            (id,date,start_at,end_at,title,venue_id,admission_price,drink_price,
             total_price,budget_status,reservation_required,note,source_url,fetched_at)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (eid, event["date"], event.get("start_at", event.get("start")), event.get("end_at", event.get("end")),
             event["title"], vid, admission, drink, total, status,
             int(bool(event.get("reservation_required", free_obj.get("reservation_required", False)))),
             event.get("note"), event.get("source_url"), metadata.get("checked_at", event.get("fetched_at"))),
        )

        for artist in event.get("artists", []):
            aid = stable_id("artist-", artist)
            conn.execute("INSERT OR IGNORE INTO artists(id,name) VALUES(?,?)", (aid, artist))
            conn.execute("INSERT OR IGNORE INTO event_artists(event_id,artist_id) VALUES(?,?)", (eid, aid))

        if event.get("source_url"):
            conn.execute(
                "INSERT OR IGNORE INTO sources(event_id,url,source_type,checked_at,confidence) VALUES(?,?,?,?,?)",
                (eid, event["source_url"], metadata.get("source_type"), metadata.get("checked_at", event.get("fetched_at")), metadata.get("confidence")),
            )

    conn.commit()
    conn.close()


def export_json():
    """Export normalized DB rows back to the current UI-compatible JSON shape."""
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""SELECT e.*, v.name AS venue, v.area AS area
                          FROM events e LEFT JOIN venues v ON v.id=e.venue_id
                          ORDER BY e.date, COALESCE(e.start_at,''), e.id""").fetchall()
    result = []
    for row in rows:
        artists = [r[0] for r in conn.execute("""SELECT a.name FROM artists a
                    JOIN event_artists ea ON ea.artist_id=a.id WHERE ea.event_id=? ORDER BY a.name""", (row["id"],))]
        event = {
            "id": row["id"], "date": row["date"], "start_at": row["start_at"], "end_at": row["end_at"],
            "title": row["title"], "artists": artists, "venue": row["venue"], "area": row["area"],
            "admission": {"price": row["admission_price"], "currency": "JPY", "label": ""},
            "free_status": {"free": row["admission_price"] == 0, "drink_required": row["drink_price"] is not None and row["drink_price"] > 0,
                             "reservation_required": bool(row["reservation_required"]), "conditions": []},
            "budget": {"admission_price": row["admission_price"], "drink_price": row["drink_price"],
                       "total_price": row["total_price"], "within_budget": row["budget_status"] == "under"},
            "source_url": row["source_url"], "fetched_at": row["fetched_at"]
        }
        result.append(event)
    document = {"dataset": "idol_free_live", "period": {"from": result[0]["date"] if result else None, "to": result[-1]["date"] if result else None}, "events": result}
    EVENTS_JSON.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    conn.close()
    print(f"exported {len(result)} events to {EVENTS_JSON}")


def validate():
    _, events = load_events()
    print(f"validated {len(events)} events")


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else "validate"
    if command == "validate":
        validate()
    elif command == "import":
        _, events = load_events()
        build_db(events)
        print(f"imported {len(events)} events into {DB}")
    elif command == "export":
        if not DB.exists():
            _, events = load_events()
            build_db(events)
        export_json()
    else:
        raise SystemExit(f"unknown command: {command}")


if __name__ == "__main__":
    main()
