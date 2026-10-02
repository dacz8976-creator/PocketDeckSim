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

## Addendum, Oct 2 afternoon: floor.py's ATTACKERS change

Added Oct 2, about 19:05 UTC, by a Claude Code subagent (Opus 5.5) on a job from the coordinator. Nothing above was changed. Still
not a ranking. How it was run, and the hashes, are in README.md under the same heading.

**What changed and why.** Astra's review (Oct 2) found that draft A's failure-modes table tracked the wrong card. floor.py takes a
list's "main attacker" from `lib/brew_pages.py`, or else the Pokémon with the highest printed damage. For draft A that fallback
picked Alolan Ninetales ex (Binding Snow 80), not the deck's centerpiece, Mega Sharpedo ex (Turbo Shark 70). Sonnet's 5678b63,
integrated at 9e139e6, gives floor.py an ATTACKERS table that it reads first; its only entry is draft A, with Mega Sharpedo ex.
floor.py's sha256 went from `8e5395e6…` to `76327865…`. By the code, the table feeds only the main-attacker columns of the
failure-modes table (could attack, did attack, the opponent's points before the first main attack, and "never attacked with a
main attacker", which comes from "did attack"). The wins, the verdict, the matchups and the flagged-card counts don't read it.

**The Payback check, run again.** A change that redefines the floor needs the Payback pre-use check again. This change is meant
not to, so the check was re-run to show it: floor.py as it is now, on brew 06 and brew 06b with its defaults (km3 on both sides,
seed 7,100, 1,920 games each), compared byte for byte with this morning's re-check (`../floor_recheck_2026-10/`, same engine
main-8626a35, the old floor.py). **All six files are byte-equal.** The pages don't print floor.py's own sha256, so no line had to
be set aside.

| file | sha256, both runs |
|---|---|
| `brew-06-pyukumuku-silvally-payback.md` (fail, 125 wins) | `5df067e787316f4eede7dcb3cddbed485e38ff3a76b36ad0d9607c43cf015730` |
| `brew-06-pyukumuku-silvally-payback_coverage.json` | `ac11deae471500d8c0e68ad4c6dda9188ceb8e1e7e18cf57486609ddc8fbbdea` |
| `brew-06-pyukumuku-silvally-payback_games.jsonl` | `e601ab3cf8b8c51a18bee21f83980e91ba5d69f92cf0b98d80154b61156b36c9` |
| `brew-06b-pyukumuku-silvally-scyther-grass.md` (fail, 262 wins) | `996135a9125745357358df4ec7cb73ec157ccf5639faaffe94eab97a160efec3` |
| `brew-06b-pyukumuku-silvally-scyther-grass_coverage.json` | `8124187cb9e32c49ae41a9ded0b29f4636609ae9bb6a005fcee60a4766db27f3` |
| `brew-06b-pyukumuku-silvally-scyther-grass_games.jsonl` | `69dbe7989a516126d852fdc1d053184b4db61ed2ad02b4d9b482f00ca1643bb2` |

### Draft A again: the main-attacker columns, old and new

`draft-A_attackers-sharpedo/draft-A-shark-tempo.md` beside this morning's `draft-A-shark-tempo.md`. **Equal:** the verdict
(clears the floor), the wins (950 in 1920, 49.48%), every matchup line, the flagged row (Alolan Ninetales ex, attacker, default
from the flag: 3598 of 3903, 92.2%), the engine's printed lines per call, and the coverage file (byte-equal). **The page differs
on three lines only:** the two failure-mode rows and the "Main attackers for these measures" line.

| | could attack with a main attacker by turn 2 / 3 / 4 | did by turn 2 / 3 / 4 | opponent's points before the first main attack | never attacked with a main attacker |
|---|---|---|---|---|
| went first (923 games), old: Alolan Ninetales ex | 0% / 34% / 48% | 0% / 34% / 47% | 1.15 | 26% |
| went first (923 games), new: Mega Sharpedo ex | 18% / 32% / 52% | 18% / 32% / 51% | 1.21 | 30% |
| went second (997 games), old: Alolan Ninetales ex | 15% / 32% / 47% | 15% / 32% / 47% | 1.27 | 32% |
| went second (997 games), new: Mega Sharpedo ex | 24% / 40% / 50% | 23% / 39% / 49% | 1.22 | 38% |

The other columns are unchanged on both rows (Stage 2 by turn 3 0%; dead cards per turn 1.19 and 1.23; won 49% and 50%).
"Main attackers for these measures" now reads "(set for this list in floor.py's ATTACKERS): Mega Sharpedo ex" (it read
"(fallback: the Pokemon with the highest printed damage …): Alolan Ninetales ex"). Draws: 1 on both.

**The games file is not byte-equal**, though the job expected it to be: each game's record stores its own `could`, `did` and
`conceded` values, which are the main-attacker measures. Those three fields differ in 1,721 of the 1,920 records. With those three
fields left out, the two files are the same text, and every game's `won` and `flagged` fields are equal
(`draft-A_attackers-sharpedo/compare_with_oct2.txt`).

### Amended draft D (one Mega Houndoom ex plus a Copycat): a first page

`draft-D_amended/draft-D-entei-grimhound.md`, the amended list as committed at 9e139e6. Victini has floor.py's default role; the
passive-role variant was not run this time. Beside it: the earlier draft D page (the two-copy list, this morning) and the cousin
brew 08 (Sept 30 engine).

| | verdict as printed | wins | weakest matchups (each ±6) | coverage flag (role, source: used of opportunities) | provisional? |
|---|---|---|---|---|---|
| **Draft D, amended** | clears the floor | 597 in 1920 (31.09%) | Suicune 34/240 = 14%, Weezing 46/240 = 19%, Blaziken 59/240 = 25% (Hydreigon 61/240 also 25%) | Victini (B3 025), attacker, default from the flag: 916 of 1064 (86.1%); flagged for its engine status, the same text as the earlier page | no (clears; Victini's role is default from the flag) |
| Draft D, two-copy list (earlier page) | clears the floor | 693 in 1920 (36.09%) | Suicune 53/240 = 22%, Weezing 53/240 = 22%, Blaziken 63/240 = 26% | Victini (B3 025), attacker, default from the flag: 898 of 1070 (83.9%) | no (clears; Victini's role is default from the flag) |
| cousin brew 08 | clears the floor | 1067 in 1920 (55.57%) | Blaziken 86/240 = 36%, Suicune 104/240 = 43%, Altaria 110/240 = 46% | none | no |

The amended page's main attacker for the failure-mode columns is Mega Houndoom ex, from the fallback (draft D has no ATTACKERS
entry), as on the earlier draft D page. Draws: 0.

Every matchup, as printed (wins of 240, and the page's percentage):

| opponent | draft D, amended | draft D, two-copy list | brew 08 |
|---|---|---|---|
| t-altaria | 76 (32%) | 80 (33%) | 110 (46%) |
| t-blaziken | 59 (25%) | 63 (26%) | 86 (36%) |
| t-hydreigon | 61 (25%) | 77 (32%) | 156 (65%) |
| t-lucario | 84 (35%) | 98 (41%) | 130 (54%) |
| t-sceptile | 113 (47%) | 116 (48%) | 157 (65%) |
| t-suicune | 34 (14%) | 53 (22%) | 104 (43%) |
| t-vespiquen | 124 (52%) | 153 (64%) | 200 (83%) |
| t-weezing | 46 (19%) | 53 (22%) | 124 (52%) |

**Not done here:** no ranking, no explanation of any difference between the pages, no role or attacker set for draft D, and no
comparison with the ladder record.
