#!/usr/bin/env python3
"""Fetch public IDOL Watch event pages and emit normalized JSONL."""
from __future__ import annotations
import json, re, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser
import requests
from bs4 import BeautifulSoup

BASE = "https://idolwatch.jp/"
LIVE = urljoin(BASE, "live")
OUT = Path("data/idolwatch.jsonl")
UA = "idol-db-crawler/1.0 (+https://github.com/bonsai/idol-db)"

def allowed(url: str) -> bool:
    rp = RobotFileParser(urljoin(BASE, "robots.txt"))
    try:
        rp.read()
        return rp.can_fetch(UA, url)
    except Exception:
        return False

def get(url: str, session: requests.Session) -> str:
    r = session.get(url, headers={"User-Agent": UA}, timeout=20)
    r.raise_for_status()
    r.encoding = r.apparent_encoding or r.encoding
    return r.text

def clean(s: str | None) -> str | None:
    if not s:
        return None
    return re.sub(r"\s+", " ", s).strip() or None

def parse_event(url: str, html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    title = clean(soup.title.get_text(" ", strip=True) if soup.title else None)
    text = clean(soup.get_text(" ", strip=True)) or ""
    canonical = soup.find("link", rel="canonical")
    source_url = canonical.get("href") if canonical and canonical.get("href") else url
    tail = source_url.rstrip("/").split("/")[-1]
    return {
        "type": "Event",
        "id": "idolwatch:event:" + re.sub(r"[^a-zA-Z0-9_-]", "", tail) if tail else "idolwatch:event:" + str(abs(hash(source_url))),
        "name": title,
        "url": source_url,
        "description": text[:1000],
        "source": "IDOL Watch",
        "source_url": source_url,
        "retrieved_at": datetime.now(timezone.utc).isoformat()
    }

def discover_event_links(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    return sorted({urljoin(BASE, a["href"]).split("#", 1)[0]
                   for a in soup.select('a[href]')
                   if urljoin(BASE, a["href"]).startswith(BASE)
                   and "/live/" in urljoin(BASE, a["href"]).rstrip("/")})

def main() -> None:
    if not allowed(LIVE):
        raise SystemExit("robots.txt does not allow the crawler for /live")
    session = requests.Session()
    html = get(LIVE, session)
    urls = discover_event_links(html)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    records = []
    for url in urls:
        try:
            if not allowed(url):
                continue
            records.append(parse_event(url, get(url, session)))
            time.sleep(1.0)
        except requests.RequestException as e:
            print(f"skip {url}: {e}")
    with OUT.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"wrote {len(records)} records to {OUT}")

if __name__ == "__main__":
    main()
