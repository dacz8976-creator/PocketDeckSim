# Post-freeze Limitless pull (Sept 27)

**What it is for:** confirmations on events after the freeze, never the spent Sept 25 holdout.
- kpg's confirmation: size as well as direction (kpg REGISTRATION section 5).
- The reserve-route no-harm re-check for koa (RUN5 "Rules").

**Pulled on Dustin's word** ("Now is fine with me", Sept 27). The rule is in `collect.py`'s header, fixed before any outcome was fetched:
- Pocket Standard events, scheduled start on or after Sept 25 UTC and at least 24 hours before the pull.
- The skill model's own fetch code, and its match serializer unchanged.

## What came in (sizes only; no result has been read)

- **4 events finished** (Sept 25-26, 593 players), 1,641 pairing rows, none unfinished. 4 more started too recently to take.
- **Matches per scoreboard cell, counted outcome-blind** by `count_n.py` (n only, no winners):

  | | post-freeze | development half |
  |---|---:|---:|
  | the 28 panel cells | 176 | 1,608 |
  | the 17 new cells | 83 (one cell empty) | 606 |

- That is about an eighth of the development half. Most panel cells have under 10 matches.

## Why no confirmation is read yet

- kpg's rule needs its post-freeze τ̂ margin at +0.74 or more, with its own 90% interval above zero. At this size the interval can't be narrow enough, so reading it now would spend a look for nothing.
- The registration already says confirmation "waits until they are enough to fill the cells", but "enough" was never given a number.
- **Proposed size rule, for Dustin, fixed before any result is read:**
  - Re-pull periodically and count sizes outcome-blind, as above.
  - Read each confirmation (kpg's, koa's no-harm re-check) once, when the post-freeze pull reaches half the development half: 804 panel matches and 303 on the new cells.
  - At the current pace (about 65 matches a day) that is roughly mid-October.
  - If Mega Garchomp ex's release (mid or late October) comes first, read at the last pull before it and report the size beside the result, since the meta shifts after it.

## Files

| File | What it is |
|---|---|
| `collect.py` | freeze (membership from metadata), fetch (cached raw), matches (the skill model's serializer) |
| `events.json` | the frozen membership, pull time and the rule |
| `raw/` | gzipped API bodies with headers |
| `matches.csv`, `completeness.json` | one row per pairing entry; unfinished and empty events (none) |
| `count_n.py` | the outcome-blind size count |
