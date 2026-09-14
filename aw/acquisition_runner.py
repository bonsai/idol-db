#!/usr/bin/env python3
"""Execute one agent-selected acquisition action safely.

The runner is deliberately stdlib-only and never bypasses robots.txt.
Automated adapters currently support RSS, sitemap XML and JSON-LD structured data.
Input: acquisition plan JSON on stdin.
Output: acquisition result JSON on stdout.
"""
from __future__ import annotations

import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

UA = "idol-db-agent/0.1"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def robots_allowed(url: str, user_agent: str = UA) -> bool:
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return False
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
        return rp.can_fetch(user_agent, url)
    except Exception:
        return False


def fetch(url: str) -> tuple[bytes, str]:
    request = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read(), response.headers.get_content_type()


class JSONLDParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_script = False
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "script" and dict(attrs).get("type", "").lower() == "application/ld+json":
            self.in_script = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script" and self.in_script:
            self.in_script = False

    def handle_data(self, data: str) -> None:
        if self.in_script:
            self.parts.append(data)


def rss_records(body: bytes) -> list[dict]:
    root = ET.fromstring(body)
    records = []
    for item in root.findall(".//item"):
        def text(name: str) -> str | None:
            node = item.find(name)
            return node.text.strip() if node is not None and node.text else None
        records.append({"title": text("title"), "url": text("link"), "published_at": text("pubDate")})
    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
        link = entry.find("{http://www.w3.org/2005/Atom}link")
        records.append({
            "title": (entry.findtext("{http://www.w3.org/2005/Atom}title") or "").strip() or None,
            "url": link.attrib.get("href") if link is not None else None,
            "published_at": (entry.findtext("{http://www.w3.org/2005/Atom}published") or "").strip() or None,
        })
    return records


def sitemap_records(body: bytes) -> list[dict]:
    root = ET.fromstring(body)
    records = []
    for node in root.findall("{*}url"):
        loc = node.find("{*}loc")
        lastmod = node.find("{*}lastmod")
        if loc is not None and loc.text:
            records.append({"url": loc.text.strip(), "last_modified": lastmod.text.strip() if lastmod is not None and lastmod.text else None})
    return records


def jsonld_records(body: bytes) -> list[dict]:
    parser = JSONLDParser()
    parser.feed(body.decode("utf-8", errors="replace"))
    records = []
    for raw in parser.parts:
        cleaned = re.sub(r"<!--|-->", "", raw).strip()
        if not cleaned:
            continue
        try:
            value = json.loads(cleaned)
        except json.JSONDecodeError:
            continue
        values = value if isinstance(value, list) else [value]
        records.extend(v for v in values if isinstance(v, dict))
    return records


def acquire(method: str, location: str) -> tuple[str, list[dict], str | None]:
    if not location:
        return "invalid", [], "selected action has no location/url"
    if not robots_allowed(location):
        return "blocked", [], "robots.txt denied or unavailable; automated acquisition not executed"
    try:
        body, content_type = fetch(location)
        if method == "rss":
            return "succeeded", rss_records(body), content_type
        if method == "sitemap":
            return "succeeded", sitemap_records(body), content_type
        if method == "structured_data":
            return "succeeded", jsonld_records(body), content_type
        return "adapter_required", [], f"No source adapter registered for method: {method}"
    except Exception as exc:
        return "failed", [], f"acquisition error: {type(exc).__name__}: {exc}"


def run(plan: dict) -> dict:
    decision = plan.get("decision") or {}
    action = decision.get("selected_action") or plan.get("selected_action") or {}
    method = action.get("method") or action.get("type") or "manual"
    location = action.get("source_url") or action.get("location") or action.get("url")
    now = utc_now()
    result = {
        "seed_id": plan.get("seed_id"),
        "run_id": f"acq-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "selected_action": action,
        "method": method,
        "status": "planned",
        "retrieved_at": now,
        "provenance": {"source": location, "agent": "idol-db/acquisition-runner", "user_agent": UA},
        "evidence": [],
    }
    if method in {"rss", "sitemap", "structured_data"}:
        status, records, detail = acquire(method, location)
        result["status"] = status
        if detail:
            result["content_type_or_error"] = detail
        result["evidence"] = [
            {
                "evidence_id": f"{result['run_id']}:{i}",
                "kind": "dataset",
                "source": location,
                "retrieved_at": now,
                "provenance": "direct source acquisition",
                "observed": record,
            }
            for i, record in enumerate(records)
        ]
        return result
    if method == "crawler":
        if not location or not robots_allowed(location):
            result["status"] = "blocked"
            result["reason"] = "robots.txt denied or unavailable; crawler not executed"
            return result
    if method in {"api", "official_page", "repository", "archive", "crawler"}:
        result["status"] = "adapter_required"
        result["reason"] = f"No source adapter registered for method: {method}"
    else:
        result["status"] = "manual_review"
        result["reason"] = "Acquisition requires explicit/manual verification"
    return result


def main() -> None:
    plan = json.load(sys.stdin)
    json.dump(run(plan), sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
