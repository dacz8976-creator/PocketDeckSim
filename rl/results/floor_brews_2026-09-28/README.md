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

## Readout (Sept 28, about 18:45; the run finished 18:34 CDT, 6 of 6 pages, `timing.txt`)

Floor bar: 349 wins of 1,920 or fewer fail, 350-418 borderline, 419 or more clear. Every number below is on the page
named after the brew. **Nothing here ranks the brews, and clearing the floor is not a recommendation.**

| brew | floor | wins of 1,920 | weakest matchups (each ±6) | why, from the page's own numbers | provisional? |
|---|---|---|---|---|---|
| 07 Hoopa / Darkrai / Sableye | clears | 1,177 (61.3%) | Sceptile 37%, Vespiquen 50% | fast: attacks with its main attacker by turn 3 in 74-79% of games; gives up 0.4 points before its first attack | yes, mildly: Mega Sableye ex's Cursed Jewel is priced at its printed damage (attack used on 90.6% of chances, so not a role problem) |
| 08 Entei / Rainbow Cave | clears | 1,040 (54.2%) | Blaziken 36%, Altaria 41%, Suicune 43% | fastest of the six: attacks by turn 3 in 92-98% of games; gives up 0.06-0.07 points | no: no flagged cards |
| 09 Sableye / Obstagoon | clears | 835 (43.5%) | Sceptile 32%, Weezing 32%, Suicune 35% | middle tempo: 0.6-0.8 points given up before its first attack; 34 draws in 1,920 games, the most of any brew here | yes, mildly: Obstagoon and Mega Sableye ex damage effects priced at printed damage (both used 96-98%) |
| 10 Diancie / Giratina | clears | 779 (40.6%) | Weezing 20%, Suicune 27%, Blaziken 35% | slowest of the four that clear: attacks by turn 3 in only 39% of games going first (0% by turn 2), gives up about 1.0 point, never attacks with its main attacker in 29-36% of games | no: no flagged cards |
| 02 Arceus / Tandemaus / Persian | **fail** | 273 (14.2%) | every matchup at 29% or below; Weezing 5%, Suicune 6%, Lucario 11% | its main attacker (Arceus ex) never attacks in 75% of games going first (56% second) and attacks by turn 4 in only 13% / 31%; gives up 2.0-2.5 points first | yes, for the "why" only: the page had no A1 entry for this list, so the main attacker is a guess (highest printed damage), and Maushold's coin-flip attack is priced at printed damage; the fail itself is 76 wins under the line |
| 03b Arceus / Crobat / Nihilego / Toxapex | **borderline** | 397 (20.7%) | Lucario 13%, Suicune 15%, Weezing 15% | same Arceus ex tempo problem as 02: attacks by turn 4 in 16% / 35%, never attacks in 67% / 51%; Team Rocket's Goo-zooka is played on only 95 of 4,445 chances (2.1%, under the 25% flag) | **yes, and it likely understates the deck:** Goo-zooka is a known blind spot (the Sept 25 trainer audit already had it at 2.1% for this deck, and deck 14's control reads "untrusted" for the same card); the role is the default, not set for this deck |

Two things worth saying plainly:
- **The order of first-attack tempo matches the tempo harness's dated prediction** (`decks/consistency_2026-09-25/ANCHORS.md`:
  08 and 07 fastest, then 09, then 10 slowest): points given up before the first main attack are 08 0.06-0.07, 07 0.4,
  09 0.6-0.8, 10 1.0-1.1. This is a different measure (kog3 against the eight panel decks, not the scripted pilot against
  `aa`), so it does not score that prediction. Only Dustin's ladder games with 07-10 score it.
- **The two Arceus ex brews (02, 03b) show the same "main attacker rarely online" pattern** as the Arceus ex CCC lists
  Dustin has already played (brew-01 and 03a, 1-3 each on the ladder; four games each, too few to say more than that
  the two point the same way). 02 is a clear fail; 03b is borderline and probably better than it reads.

**Not done here:** no role was set for any deck (A2 leaves that to whoever wrote the page), no ranking, no calibration,
no comparison with the ladder record beyond the line above.

