# The floor's Payback pre-use check, re-run under km3 on the Sept 30 engine

**Written and committed with the pin, before any game of this check was played.** The verdicts go in a `README.md` beside this file afterwards; this plan is not edited.

**Why:**
- The floor check (`decks/screen/floor.py`) was cleared for use by the Sept 25 pre-use check (`../floor_payback_check_2026-09-25/`, kp3) and re-checked under kog3 after the Sept 28 switch (`../floor_recheck_2026-09-28/`).
- The Sept 30 engine switch (`../engine_switch_2026-09-30/`) moves the floor's pilot to km3 on both sides, on the new official engine `rl/engine-2026-09-30/`.
- Dustin, Sept 30 (RUN5, km, "The official engine switch carrying kta and km"): the default pilot "km3 (Recommended)"; the plan he approved ends with "the floor's pre-use re-check under km3" (step 12 of `../engine_switch_2026-09-30/PLAN.md`, the Sept 28 precedent).

**What it decides:** whether the floor stays usable on Dustin's decks under km3.
- **brew-06 and brew-06b** (the two Payback lists, known ladder failures) must both read **"fail"**, with km3 on both sides.
- **The deck 14 control** (Comfey/Raticate/Hypno, k3 on both sides, a deck k3 is known to misplay) must read **"untrusted"** (as a control reading).
- **A plain `run_screen.py`** at 240 games per matchup on brew-06 and brew-06b (km3, its new default, same seeds) must give exactly the floor's wins against every opponent. This shows that the floor's tracing changes no game.
- If any of these fails, the floor isn't used until Dustin has seen the pages (the Sept 28 rule).
- **Reported beside, not part of the test:** brew-05b and deck 07, the anchors. Under kog3 on Sept 28 they had 584 (30.4%) and 903 (47.0%) of 1,920; under kp3 on Sept 25, 597 and 908. A pilot change can move them.
- **Also reported, not a gate:** whether the k3 control repeats Sept 28's games exactly (196 wins, and the same wins against each opponent). k3 plays unchanged on the new engine (the switch's identity check), and the opponents and seeds are the same, so it should. A difference would be looked at, but it can't change the verdict above.

**Numbers from Sept 28 (kog3, for comparison, not thresholds):** brew-06 124 of 1,920, brew-06b 259, the control 196 (Goo-zooka played on 66 of 4,486 chances).

**Code and engine:**
- `floor.py` and `run_screen.py` as committed in the pin: `FLOOR_PILOT = "km3"` and the screen's defaults km3. The pricing-pilot pattern matches km3 (and every public-pricing code), so kp's 62 audited texts apply as they did for kog3 and kp3 (`decks/screen/test_floor_pricing_pilot.py`).
- The official engine `rl/engine-2026-09-30/`, and the coverage from its goldfish, checked by hash.
- The same games per matchup (240), opponents (`decks/screen/opponents/`) and seeds (7,100 + 1,000 × opponent, +500 for seat 1) as Sept 25 and Sept 28. No new seed range.

**Run:** `run_check.sh` (about 30-60 minutes; at home or overnight, not during class or travel). It refuses to start unless the manifest names the new engine, the screen and the floor both default to km3, and this plan and the runner are committed unchanged. `check_verdicts.py` then writes `verdicts.txt`: each verdict against what is needed, the run_screen comparison per opponent, and the anchors.
