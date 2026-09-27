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
- **The rule (Dustin, Sept 27; RUN5 "When post-freeze data is read"), fixed before any result is read:**
  - Re-pull periodically and count sizes outcome-blind, as above.
  - Read once, when the pull reaches half the development half: 804 panel matches and 303 on the new cells. At the current pace (about 65 matches a day) that is roughly mid-October.
  - If Mega Garchomp ex's release comes first, read at the last pull before it, with the size printed beside the result.
  - One pull, every pending check, from the list below. After the read, these events become development data (a rolling freeze).
  - A failure reads "not confirmed at this size", never "no better".

## The checks waiting on this pull (pre-registered list; final version committed before the data is opened)

| Check | Rule | Source |
|---|---|---|
| kpg's confirmation | on the post-freeze cells alone, τ̂ margin over kp3 at least +0.74 (half of +1.47), its own 90% interval above zero; pooled and sign reported beside | `../kpg_2026-09-27/REGISTRATION.md` section 5 |
| koa's no-harm re-check | τ̂ margin (kp3 minus koa) 90% lower bound at −1.0 or above, no veto; Altaria's post-freeze cells reported | RUN5 "Confirming a reserve-route (no-harm) fix" |

- Anything else adopted before the read joins this list, by a commit here, before the data is opened: the composed pilot (kp3 + koa's A + F), kph, kt.
- Each check is read on the same engine as its baselines.

## Files

| File | What it is |
|---|---|
| `collect.py` | freeze (membership from metadata), fetch (cached raw), matches (the skill model's serializer) |
| `events.json` | the frozen membership, pull time and the rule |
| `raw/` | gzipped API bodies with headers |
| `matches.csv`, `completeness.json` | one row per pairing entry; unfinished and empty events (none) |
| `count_n.py` | the outcome-blind size count |
