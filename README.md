# Signal filter demo

A small rules engine that reads a noisy JSON feed and either prints action cards or `NO SIGNAL`.

The feed is synthetic. Nothing here connects to email, a marketplace, or a personal account. The point is the filter: kind checks, pay bounds, required fields, a competition cap, and a seen-id state file so the same item is not raised twice.

## What goes in

- `fixtures/feed.json` — events with `id`, `kind`, `title`, `pay`, `claimants`, `url`, `work`.
- `fixtures/rules.json` — the threshold.
- `examples/state.json` — created on the first run. Ids already written there are skipped.

Default rules:

- Kinds `newsletter`, `waitlist`, and `screener` are rejected.
- Allowed kinds are `bounty` and `fixed_task`.
- Pay must be from 20 to 250.
- More than 3 claimants is rejected.
- `id`, `title`, `pay`, `url`, and `work` are required.

## What comes out

First run of the sample feed:

- Two cards (a $40 bounty with 1 claimant, a $30 fixed task with 2 claimants).
- Rejections for the newsletter, the waitlist, the $8 item, the crowded item, the duplicate id, and the row with no URL.

Second run of the same feed:

```
NO SIGNAL
```

A new id that passes the rules produces one card.

## How to run

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m pytest
python run_demo.py
```

`run_demo.py` deletes `examples/state.json`, runs the feed, runs it again, and writes [examples/demo_report.json](examples/demo_report.json).

## How this differs from the other two projects

The catalog transformer and the opportunity pipeline both turn a source file into a table. This one keeps state between runs and is allowed to return nothing. That is the behavior under test.

## Limitations

- Rules are a flat JSON file, not a general expression language.
- Dedup is an id set on disk. There is no expiry.
- "Claimants" is whatever the feed says. This demo does not verify a live listing.
- There is no scheduler in the repository. A cron job or task runner would call `run_file` and notify only when status is `SIGNAL`.
