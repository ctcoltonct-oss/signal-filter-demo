#!/usr/bin/env python3
"""Turn a noisy event feed into action cards, or NO SIGNAL.

Generic demonstration. Inputs are synthetic. No inbox access.
"""

from __future__ import annotations

import json
from pathlib import Path

CARD_FIELDS = [
    "OPPORTUNITY",
    "WHY IT PASSED",
    "PAYMENT",
    "EXACT WORK",
    "ACCESS / COMPETITION",
    "ACTION NOW",
]


def load_json(path: Path):
    return json.loads(path.read_text())


def _missing(event: dict, fields: list[str]) -> list[str]:
    missing = []
    for field in fields:
        value = event.get(field)
        if value is None or str(value).strip() == "":
            missing.append(field)
    return missing


def evaluate(event: dict, rules: dict) -> tuple[bool, str]:
    kind = str(event.get("kind") or "")
    if kind in set(rules.get("reject_kinds") or []):
        return False, f"rejected kind: {kind}"
    missing = _missing(event, rules.get("require_fields") or [])
    if missing:
        return False, "missing " + ",".join(missing)
    allowed = rules.get("allowed_kinds")
    if allowed and kind not in allowed:
        return False, f"kind not allowed: {kind}"
    pay = event.get("pay")
    try:
        amount = float(pay)
    except (TypeError, ValueError):
        return False, "pay is not a number"
    if amount < float(rules["min_pay"]) or amount > float(rules["max_pay"]):
        return False, f"pay {amount:g} outside {rules['min_pay']}-{rules['max_pay']}"
    claimants = event.get("claimants")
    if claimants is not None and int(claimants) > int(rules.get("max_claimants", 3)):
        return False, f"claimants {claimants} over max"
    return True, "passed pay, kind, required fields, and competition cap"


def to_card(event: dict, why: str) -> dict:
    return {
        "OPPORTUNITY": event.get("title"),
        "WHY IT PASSED": why,
        "PAYMENT": event.get("pay"),
        "EXACT WORK": event.get("work") or "",
        "ACCESS / COMPETITION": f"{event.get('kind')} / claimants={event.get('claimants', 'n/a')}",
        "ACTION NOW": event.get("action") or event.get("url") or "",
    }


def scan(events: list[dict], rules: dict, seen: set[str]) -> dict:
    cards = []
    rejected = []
    new_seen = set(seen)
    for event in events:
        event_id = str(event.get("id") or "")
        if not event_id:
            rejected.append({"id": "", "reason": "missing id"})
            continue
        if event_id in new_seen:
            rejected.append({"id": event_id, "reason": "already seen"})
            continue
        ok, reason = evaluate(event, rules)
        new_seen.add(event_id)
        if not ok:
            rejected.append({"id": event_id, "reason": reason})
            continue
        cards.append(to_card(event, reason))
    status = "NO SIGNAL" if not cards else "SIGNAL"
    return {"status": status, "cards": cards, "rejected": rejected, "seen": sorted(new_seen)}


def run_file(feed_path: Path, rules_path: Path, state_path: Path) -> dict:
    events = load_json(feed_path)
    rules = load_json(rules_path)
    seen = set(load_json(state_path)) if state_path.exists() else set()
    result = scan(events, rules, seen)
    state_path.write_text(json.dumps(result["seen"], indent=2) + "\n")
    return result
