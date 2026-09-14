#!/usr/bin/env python3
"""Execute the acquisition action selected by the planner.

This PoC deliberately does not bypass robots.txt. It records a decision and
an acquisition result; actual source-specific adapters can be added later.
Input: acquisition plan JSON on stdin.
Output: evidence/result JSON on stdout.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def robots_allowed(url: str, user_agent: str = "idol-db-agent") -> bool:
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return False
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = RobotFileParser(robots_url)
    try:
        rp.read()
        return rp.can_fetch(user_agent, url)
    except Exception:
        return False


def run(plan: dict) -> dict:
    action = plan.get("selected_action") or {}
    method = action.get("method") or action.get("type") or "manual"
    location = action.get("location") or action.get("url")

    result = {
        "seed_id": plan.get("seed_id"),
        "run_id": f"acq-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "selected_action": action,
        "method": method,
        "status": "planned",
        "retrieved_at": utc_now(),
        "provenance": {
            "source": location,
            "agent": "idol-db/acquisition-runner",
        },
    }

    if method == "crawler" and location:
        if not robots_allowed(location):
            result["status"] = "blocked"
            result["reason"] = "robots.txt denied or unavailable; crawler not executed"
            return result

    # The runner is intentionally conservative until a source adapter exists.
    if method in {"api", "rss", "sitemap", "structured_data", "official_page", "crawler"}:
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
