# The floor check under km3 on Dustin's decks and the brews (Sept 30)

**Who wrote this and why.** The laptop session ("Project familiarization", Claude Code, Desktop). The job came through the Fable coordinator session ("Work delegation and task routing"), under the operational authority Dustin gave it on Sept 30; his own gates are unchanged. This README was written and committed before any game of this run was played.

**What this is.** The floor check (`decks/screen/floor.py`) under the new working pilot, run once on:
- each of Dustin's 15 decks (`decks/dustin/01` to `15`);
- the six brews that have a kog3 floor page (`../floor_brews_2026-09-28/`: 02, 03b, 07, 08, 09, 10).

It is the bot's approved job (RUN5, "A2: the hold lifts for the floor check only"). **It is not a ranking.** Nothing here says which deck is best, and a deck that clears the floor is not thereby good. It says which decks the bot can already tell are weak, and how.

**Why now.** The Sept 30 engine switch moved the screen and the floor from kog3 to km3 (`../engine_switch_2026-09-30/`). The floor's pre-use re-check passed under km3 (`../floor_recheck_2026-09-30/`: both Payback lists "fail", the deck 14 k3 control "untrusted"). Each deck's floor page so far is under kp3 or kog3; this gives each one its page under the pilot now in use.

**Reused, not re-run.** These pages already exist from today's re-check, with the same defaults and seeds:
- Dustin's deck 07 (`../floor_recheck_2026-09-30/07-skarmory-stall.md`);
- brew 05b (`../floor_recheck_2026-09-30/brew-05b-meowstic-hatterene-comfey.md`).

Deck 14's k3 control was also run today and is not repeated. Deck 14 is run here like any other deck, under km3 on both sides.

**Nothing new is decided here.** Every rule is the one already fixed:
- floor.py's own defaults:
  - pilot km3 on both sides;
  - the official engine `rl/engine-2026-09-30/` (the manifest's available release, hash checked);
  - 240 games per matchup against each of the eight panel decks in `decks/screen/opponents/` (1,920 per deck);
  - seeds 7,100 + 1,000 × opponent (+500 for seat 1).
- Verdicts by the A2 bar, read from floor.py's page as printed:
  - under 20% of the panel on both sides fails;
  - within the floor's own noise of 20% reads "borderline";
  - "untrusted" keys on the coverage flag only.
- Card roles are floor.py's defaults, from each card's flag. No role is set for any deck here. If a page's printed role looks wrong to Dustin, that is his to say on the page, as A2 already provides.

**Reading note, fixed before any game.** Each page prints every flagged card's role and where it came from. Where a flagged card carries a default role, a "fail", "borderline" or "untrusted" there may be a wrong-role problem rather than a deck problem, and the readout will mark that verdict **provisional**. For the six brews, the readout sets each km3 page beside its kog3 page (Sept 28) with the wins and the verdict, and says only "changed" or "unchanged". No other interpretation is made.

**What is not claimed.** No prediction about these verdicts is registered, so nothing here confirms or refutes one. Dustin's ladder games stay the only score of a deck.

**Run:** `run_floor.sh`, at the lowest CPU priority, with nothing else on the laptop beside it. Pages, per-game files and coverage land in this folder, and timing goes in `timing.txt`. The readout goes below once the pages exist.
