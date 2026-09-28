# The floor's Payback pre-use check, re-run under kog3 on the new engine (Sept 28)

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
