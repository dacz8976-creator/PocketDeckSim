# The floor's Payback pre-use check, re-run under kog3 on the new engine (Sept 28)

## Result: the check passes, and the floor stays usable under kog3

| deck | pilots | wins of 1,920 | verdict | needed | Sept 25 (kp3, old engine) |
|---|---|---:|---|---|---|
| brew-06 (Pyukumuku/Silvally Payback) | kog3, kog3 | 124 (6.5%) | **fail** | fail ✔ | 128, fail |
| brew-06b (Grass, Team Rocket's Scyther) | kog3, kog3 | 259 (13.5%) | **fail** | fail ✔ | 281, fail |
| deck 14 (Comfey/Raticate/Hypno), control | k3, k3 | 196 (10.2%) | **control reading: untrusted** | untrusted ✔ | 195, untrusted |
| brew-05b (Meowstic/Hatterene/Comfey) | kog3, kog3 | 584 (30.4%) | clears the floor | descriptive | 597 (31.1%) |
| deck 07 (Skarmory stall) | kog3, kog3 | 903 (47.0%) | clears the floor | descriptive | 908 (47.3%) |

- **The Payback lists fail with their plan in use**, so a fail isn't the bot ignoring it:
  - brew-06: Silvally attacks on 587 of 589 chances, Pyukumuku is benched on 58%, Rocky Helmet is played on 90%.
  - brew-06b: Silvally 591 of 598, Team Rocket's Scyther 178 of 184, Pyukumuku 66%, Rocky Helmet 62%.
- **The control works.** Team Rocket's Goo-zooka is played on 66 of 4,486 chances (1.5%), under the 25% flag.
- **Tracing changed no game.** A plain `run_screen.py` at 240 games per matchup, same seeds (`run_screen.txt`), gives exactly the floor's wins against every opponent for brew-06 and brew-06b.
- **The anchors moved by under 1 point,** within the floor's own noise (about ±1.8 at 1,920 games).
- Pages, per-game files, coverage and timing are in this folder; the control's are in `control_k3/`.

---

**Written and committed before any game of this check was played.**

**Why:**
- The floor check (`decks/screen/floor.py`) was cleared for use by the Sept 25 pre-use check (`../floor_payback_check_2026-09-25/`). That check ran on the Sept 25 engine under kp3.
- With the kog engine switch (`../engine_switch_2026-09-28/`), the floor's pilot is kog3 on both sides, on the new official engine.
- Dustin (Sept 28): "the Payback pre-use check re-run under kog3 with both lists still failing". Astra's review asked for renewed floor controls.

**What it decides:** whether the floor stays usable on Dustin's decks under the new pilot and engine.
- **brew-06 and brew-06b** (the two Payback lists, known ladder failures) must both read **"fail"**, under kog3 on both sides.
- **The deck 14 control** (Comfey/Raticate/Hypno under k3 on both sides, a deck k3 is known to misplay) must read **"untrusted"**.
- If any of these fails, the floor isn't used until Dustin and Fable have seen the pages.
- **Reported beside, not part of the test:** brew-05b and deck 07, the Sept 25 anchors (31.1% and 47.3% under kp3 on the old engine; a pilot change can move them).
- Also a plain `run_screen.py` at 240 games per matchup on brew-06 and 06b. It must give exactly the floor's wins per opponent, which shows that tracing changes no game.

**Code and engine:**
- `floor.py` as re-pointed in the pin commit: `FLOOR_PILOT = "kog3"`, with kog3 added to the pricing-pilot pattern so the audited card texts apply as they did for kp3.
- The official engine `rl/engine-2026-09-28/`, and the coverage from its goldfish, checked by hash.
- The same games per matchup (240), opponents (`decks/screen/opponents/`) and seeds (7,100 + 1,000 × opponent, +500 for seat 1) as Sept 25.

**Run:** `run_check.sh`. The pages and per-game files go in this folder; the verdicts go in a results section below.
