#!/usr/bin/env python3
from __future__ import annotations
import html, json
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path

BASE = "https://bonsai.github.io/idol-db/"
DATA = Path("data/idolwatch.jsonl")
OUT = Path("rss/idolwatch.xml")


def esc(v):
    return html.escape(str(v or ""), quote=True)


def main():
    records = []
    if DATA.exists():
        for line in DATA.read_text(encoding="utf-8").splitlines():
            if line.strip():
                records.append(json.loads(line))
    records.sort(key=lambda x: x.get("retrieved_at", ""), reverse=True)
    now = datetime.now(timezone.utc)
    items = []
    for r in records[:100]:
        url = r.get("source_url") or r.get("url") or BASE
        published = r.get("retrieved_at")
        try:
            dt = datetime.fromisoformat(published.replace("Z", "+00:00")) if published else now
        except ValueError:
            dt = now
        items.append(f'''<item>\n<title>{esc(r.get("name"))}</title>\n<link>{esc(url)}</link>\n<guid isPermaLink="true">{esc(url)}</guid>\n<pubDate>{format_datetime(dt)}</pubDate>\n<description>{esc(r.get("description"))}</description>\n</item>''')
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0">\n<channel>\n<title>IDOL Watch — idol-db</title>\n<link>{BASE}</link>\n<description>IDOL Watch public event data collected by the bonsai/idol-db data pipeline.</description>\n<lastBuildDate>{format_datetime(now)}</lastBuildDate>\n{chr(10).join(items)}\n</channel>\n</rss>\n'''
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(xml, encoding="utf-8")

if __name__ == "__main__":
    main()
