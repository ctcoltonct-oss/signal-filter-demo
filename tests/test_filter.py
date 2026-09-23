import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from filter_feed import load_json, scan  # noqa: E402

RULES = load_json(ROOT / "fixtures" / "rules.json")
FEED = load_json(ROOT / "fixtures" / "feed.json")


def test_first_scan_keeps_two_cards():
    result = scan(FEED, RULES, set())
    assert result["status"] == "SIGNAL"
    titles = [card["OPPORTUNITY"] for card in result["cards"]]
    assert titles == [
        "Add CSV export to the demo CLI",
        "Normalize the sample supplier file",
    ]
    assert result["cards"][0]["PAYMENT"] == 40
    reasons = {item["id"]: item["reason"] for item in result["rejected"]}
    assert reasons["n-1"] == "rejected kind: newsletter"
    assert reasons["w-1"] == "rejected kind: waitlist"
    assert "outside" in reasons["b-low"]
    assert reasons["b-40"] == "already seen"
    assert "claimants" in reasons["b-crowd"]
    assert "missing url" in reasons["t-broken"]


def test_second_scan_is_silent():
    first = scan(FEED, RULES, set())
    second = scan(FEED, RULES, set(first["seen"]))
    assert second["status"] == "NO SIGNAL"
    assert second["cards"] == []


def test_new_event_after_state_passes():
    first = scan(FEED, RULES, set())
    extra = {
        "id": "b-new",
        "kind": "bounty",
        "title": "New issue after the first scan",
        "pay": 75,
        "claimants": 0,
        "url": "https://example.com/bounties/new",
        "work": "Add one test",
        "action": "Claim b-new.",
    }
    result = scan([extra], RULES, set(first["seen"]))
    assert result["status"] == "SIGNAL"
    assert result["cards"][0]["ACTION NOW"] == "Claim b-new."


def test_state_file_round_trip(tmp_path):
    from filter_feed import run_file

    state = tmp_path / "state.json"
    first = run_file(ROOT / "fixtures" / "feed.json", ROOT / "fixtures" / "rules.json", state)
    saved = json.loads(state.read_text())
    assert saved == first["seen"]
    second = run_file(ROOT / "fixtures" / "feed.json", ROOT / "fixtures" / "rules.json", state)
    assert second["status"] == "NO SIGNAL"
