# The floor check on the unplayed brews (Sept 28)

**Who wrote this and why.** The session "Opus agents progress" (Claude Code, Desktop), on Dustin's Sept 28 evening
instruction "Work with the opus agents to continue towards our goal". Written and committed before any game of this
run was played.

**What this is.** The floor check (`decks/screen/floor.py`), run once on each brew Dustin has not yet played on the
ladder and that has never had a floor page: 02, 03b, 07, 08, 09, 10. It is the bot's one approved job right now
(RUN5, "A2: the hold lifts for the floor check only"). It is not a ranking: nothing here says which brew is best,
and a brew that clears the floor is not thereby good. It says which brews the bot can already tell are weak, and how.

**Why now.** The ladder log has 33 games (12-21) and none since Sept 24. Brews 07-10 have been waiting since Sept 25
with only the tempo harness's dated prediction (`decks/consistency_2026-09-25/ANCHORS.md`: 08 and 07 fastest, 10
slowest). The floor is the other half of the question "which brew gets ladder games next", and it costs about three
minutes per brew on an idle laptop (`../floor_recheck_2026-09-28/timing.txt`).

**Nothing new is decided here.** Every rule is the one already fixed:
- pilot kog3 on both sides, the official engine `rl/engine-2026-09-28/`, 240 games per matchup against each of the
  eight panel decks (1,920 per brew), seeds 7,100 + 1,000 x opponent (+500 for seat 1): floor.py's own defaults;
- verdicts by the A2 bar (20% under the panel on both sides; within the floor's own noise of 20% reads "borderline";
  "untrusted" keys on the coverage flag only), read from floor.py's page as printed;
- card roles are floor.py's defaults (from each card's flag). No role was set for any of these decks; if a page's
  printed role looks wrong to Dustin, that is his to say on the page, as A2 already provides;
- the pre-use check (both Payback lists "fail", deck 14 control "untrusted") passed under kog3 today
  (`../floor_recheck_2026-09-28/`), so the floor is usable.

**What is not claimed.** No prediction about these floor verdicts is registered, so nothing here can confirm or
refute one. The tempo harness's prediction stands as it was, scored only by Dustin's ladder games.

**Run:** `run_floor.sh`, at the lowest CPU priority so it never slows another run. Pages, per-game files and coverage
land in this folder; timing in `timing.txt`; the readings go in a results section below once they exist.

## Reading note (added Sept 28, about 18:20, before any page of this run was read; changes no rule and no verdict)

Each page prints every flagged card's role and where the role came from ("default from the flag" or "set for this
deck"). No role was set for any of these six decks. So on any page where a flagged card carries a default role, a
verdict is **provisional**: a "fail", "borderline" or "untrusted" there may be a wrong-role problem rather than a deck
problem, and the reading below will say so beside the verdict. Nothing in this folder ranks the brews.
