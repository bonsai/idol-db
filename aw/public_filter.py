#!/usr/bin/env python3
"""Filter canonical idol-live events for public Discovery.

Canonical collection is intentionally broader than the public listing policy.
An event may remain in the canonical DB even when it is not publicly listed.
Only a ticket option with a known price <= 500 JPY makes an event eligible.
Required drink charges are retained and are not silently folded into the ticket
price.
"""
from __future__ import annotations

import json
import sys

PUBLIC_MAX_PRICE = 500


def ticket_options(event: dict) -> list[dict]:
    value = event.get("ticket_options", [])
    return value if isinstance(value, list) else []


def eligible_for_public(event: dict, max_price: int = PUBLIC_MAX_PRICE) -> bool:
    for option in ticket_options(event):
        if not isinstance(option, dict):
            continue
        price = option.get("price")
        if isinstance(price, (int, float)) and not isinstance(price, bool) and price <= max_price:
            return True
    return False


def filter_events(events: list[dict], max_price: int = PUBLIC_MAX_PRICE) -> list[dict]:
    return [event for event in events if eligible_for_public(event, max_price)]


def main() -> None:
    payload = json.load(sys.stdin)
    events = payload.get("events", payload) if isinstance(payload, (dict, list)) else []
    if not isinstance(events, list):
        raise SystemExit("input must be an event list or {events: [...]}")
    result = {
        "policy": {
            "public_max_price_jpy": PUBLIC_MAX_PRICE,
            "basis": "service_listing_policy",
            "legal_permission": False,
        },
        "events": filter_events(events),
    }
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
