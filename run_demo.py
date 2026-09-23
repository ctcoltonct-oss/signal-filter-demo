#!/usr/bin/env python3
"""Run the synthetic feed twice to show deduped silence."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from filter_feed import run_file  # noqa: E402


def main() -> None:
    state = ROOT / "examples" / "state.json"
    if state.exists():
        state.unlink()
    first = run_file(ROOT / "fixtures" / "feed.json", ROOT / "fixtures" / "rules.json", state)
    second = run_file(ROOT / "fixtures" / "feed.json", ROOT / "fixtures" / "rules.json", state)
    report = {"first_run": first, "second_run": {"status": second["status"], "cards": second["cards"]}}
    (ROOT / "examples" / "demo_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(first["status"], "cards", len(first["cards"]))
    print(second["status"])


if __name__ == "__main__":
    main()
