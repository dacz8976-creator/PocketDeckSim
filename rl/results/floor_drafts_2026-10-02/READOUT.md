# Readout: the floor check under km3 on the four brew drafts (Oct 2)

**Not a ranking, and no recommendation.** The floor is a pass/fail floor (A2). Clearing it does not make a list good, and nothing
here says which draft to play. Every number below is copied from the page named beside it. The plan is `README.md` in this folder,
written before any game.

Floor bar, as printed on every page: 349 wins of 1920 or fewer fail, 350-418 are borderline, 419 or more clear. The four draft
pages say "km3 on the deck, km3 on the panel" and engine `rl/engine-2026-10-02/deckgym`. The cousins' pages are from the Sept 30
engine (`rl/engine-2026-09-30/deckgym`), also km3 on both sides, with the same seeds.

How to read the columns (the Sept 30 readout's way):
- **Weakest matchups:** the first three lines of the page's "Worst matchups" list (it lists all eight, lowest first; each line is
  ±6 points at 240 games). A tie at the third line is named.
- **Coverage flag:** every flagged card on the page, its role and where the role came from, and its use (used of opportunities).
  No page here prints "under 25%".
- **Provisional?:** floor.py's pages print no provisional note of their own. Per the README's reading note, a "fail",
  "borderline" or "untrusted" verdict is marked provisional where a flagged card carries a default role.

## Which cousin goes with which draft

From the drafts' README ("What the floor said about close cousins") and each draft's own notes:

| draft | cousin | why they match | cousin's km3 page |
|---|---|---|---|
| A, Shark tempo | deck 13, Alolan Ninetales / Raticate | both run Alolan Ninetales ex (draft A's notes name deck 13) | `../floor_dustin_2026-09-30/13-a-ninetales-raticate.md` |
| B, Tide heal | deck 03, Wailord / Indeedee wall | the heal-and-wall plan, and both run Wailord (draft B's notes name deck 03) | `../floor_dustin_2026-09-30/03-wailord-indeedee-wall.md` |
| C, Meowstic / Hatterene v2 | brew 05b, Meowstic / Hatterene / Comfey | draft C is brew 05b with Dustin's edits | `../floor_recheck_2026-09-30/brew-05b-meowstic-hatterene-comfey.md` |
| D, Entei / Grimhound | brew 08, Entei / Rainbow Cave | both run Entei ex, Rainbow Cave and Flame Patch | `../floor_dustin_2026-09-30/brew-08-entei-rainbow-cave.md` |

Brew 05b has no page in `floor_dustin_2026-09-30/`: that run reused its page from the Sept 30 re-check, which is the one used
here. This morning's re-check on the new engine (`../floor_recheck_2026-10/brew-05b-meowstic-hatterene-comfey.md`) has the same
577 wins; its `verdicts.txt` says all its outputs equal Sept 30's except the engine lines.

## The drafts beside their cousins

| | verdict as printed | wins | weakest matchups (each ±6) | coverage flag (role, source: used of opportunities) | provisional? |
|---|---|---|---|---|---|
| **Draft A** | clears the floor | 950 in 1920 (49.48%) | Altaria 95/240 = 40%, Sceptile 105/240 = 44%, Weezing 109/240 = 45% | Alolan Ninetales ex (B2 029), attacker, default from the flag: 3598 of 3903 (92.2%); flagged as printed: "attack Binding Snow: pays off during the opponent's turn, which the search doesn't play out" | no (clears; Alolan Ninetales ex's role is default from the flag) |
| cousin deck 13 | clears the floor | 1068 in 1920 (55.62%) | Altaria 94/240 = 39%, Hydreigon 110/240 = 46%, Weezing 122/240 = 51% | Alolan Ninetales ex (B2 029), attacker, default from the flag: 4251 of 4369 (97.3%); the same flag | no |
| **Draft B** | **fail** | 236 in 1920 (12.29%) | Vespiquen 16/240 = 7%, Suicune 17/240 = 7%, Altaria 25/240 = 10% (Weezing also 25/240 = 10%) | none | no (no flagged cards) |
| cousin deck 03 | clears the floor | 1178 in 1920 (61.35%) | Lucario 127/240 = 53%, Vespiquen 134/240 = 56%, Suicune 146/240 = 61% | none | no |
| **Draft C** | **borderline** | 366 in 1920 (19.06%) | Suicune 7/240 = 3%, Hydreigon 15/240 = 6%, Weezing 22/240 = 9% | Hatterene (B3 071), attacker, default from the flag: 2302 of 2376 (96.9%); flagged for "Mental Crush: ExtraDamageIfDefenderStatus estimated at printed damage (k's damage estimate)" | **yes**: Hatterene, attacker, default from the flag |
| cousin brew 05b | clears the floor | 577 in 1920 (30.05%) | Hydreigon 32/240 = 13%, Weezing 43/240 = 18%, Suicune 52/240 = 22% (Vespiquen 52/240 and Sceptile 54/240 also 22%) | Hatterene (B3 071), attacker, default from the flag: 2416 of 2496 (96.8%); the same flag | no |
| **Draft D** | clears the floor | 693 in 1920 (36.09%) | Suicune 53/240 = 22%, Weezing 53/240 = 22%, Blaziken 63/240 = 26% | Victini (B3 025), attacker, default from the flag: 898 of 1070 (83.9%); flagged for its engine status (summary; the page prints "engine: Implemented with unverified rule boundaries; …") | no (clears; Victini's role is default from the flag) |
| cousin brew 08 | clears the floor | 1067 in 1920 (55.57%) | Blaziken 86/240 = 36%, Suicune 104/240 = 43%, Altaria 110/240 = 46% | none | no |

### Draft C: Hatterene's 140 is priced at its printed 70

Mental Crush is 70, and 70 more into a Confused Active (`lib/card.py`). The page's flag line says the bot's damage estimate
prices it at its printed damage: the damage estimate counts 70; the game, and any attack the search plays out, deals 140 (README, "After the runs", has where this comes
from). The cousin brew 05b's page carries the same flag. Draft C's own notes say: "The page's role for Hatterene is 'attacker',
which is right."

### Draft D: Victini's role (proposed role, Dustin's to confirm)

Victini's default role on draft D's page is **"attacker"**, not "bench piece/passive ability". So draft D was run a second time
from a **modified private copy** of floor.py whose only change is one ROLES entry, Victini as "bench piece/passive ability"
(README, "After the runs"). **That role is proposed, Dustin's to confirm; he hasn't answered.** Draft D's floor page is the first
one.

| draft D page | verdict as printed | wins | Victini's row (role, source: used of opportunities) |
|---|---|---|---|
| `draft-D-entei-grimhound.md` (floor.py as committed) | clears the floor | 693 in 1920 (36.09%) | attacker, default from the flag: 898 of 1070 (83.9%) |
| `draft-D_victini-passive/draft-D-entei-grimhound.md` (modified copy) | clears the floor | 693 in 1920 (36.09%) | bench piece/passive ability, set for this deck: 2332 of 2603 (89.6%) |

The two runs played the same games (same coverage file, same per-game records but for Victini's counts), so the matchups and
failure modes are the same on both pages.

## Every matchup, as printed (wins of 240, and the page's percentage)

| opponent | draft A | deck 13 | draft B | deck 03 | draft C | brew 05b | draft D | brew 08 |
|---|---|---|---|---|---|---|---|---|
| t-altaria | 95 (40%) | 94 (39%) | 25 (10%) | 148 (62%) | 101 (42%) | 111 (46%) | 80 (33%) | 110 (46%) |
| t-blaziken | 152 (63%) | 172 (72%) | 37 (15%) | 160 (67%) | 55 (23%) | 93 (39%) | 63 (26%) | 86 (36%) |
| t-hydreigon | 122 (51%) | 110 (46%) | 45 (19%) | 154 (64%) | 15 (6%) | 32 (13%) | 77 (32%) | 156 (65%) |
| t-lucario | 121 (50%) | 144 (60%) | 34 (14%) | 127 (53%) | 116 (48%) | 140 (58%) | 98 (41%) | 130 (54%) |
| t-sceptile | 105 (44%) | 124 (52%) | 37 (15%) | 149 (62%) | 24 (10%) | 54 (22%) | 116 (48%) | 157 (65%) |
| t-suicune | 114 (48%) | 163 (68%) | 17 (7%) | 146 (61%) | 7 (3%) | 52 (22%) | 53 (22%) | 104 (43%) |
| t-vespiquen | 132 (55%) | 139 (58%) | 16 (7%) | 134 (56%) | 26 (11%) | 52 (22%) | 153 (64%) | 200 (83%) |
| t-weezing | 109 (45%) | 122 (51%) | 25 (10%) | 160 (67%) | 22 (9%) | 43 (18%) | 53 (22%) | 124 (52%) |

**Not done here:** no ranking, no draft named best or recommended, no explanation of any difference between a draft and its
cousin (the cousins are different lists, and their pages are on the Sept 30 engine), no role set in the committed floor.py, and
no comparison with the ladder record.
