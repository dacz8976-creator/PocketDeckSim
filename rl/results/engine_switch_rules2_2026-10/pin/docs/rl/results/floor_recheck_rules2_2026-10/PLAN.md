# The floor's pre-use re-check under km3, and the new floor pages, after rules switch 2 (Oct 2026)

**Written and committed with the pin, before any game of this step** (rules switch 2's `PLAN.md` steps 11-14 and 15). Part A's result is the RESULT line at the top of `verdicts.txt`, which `run_check.sh` writes. This plan is not edited afterwards.

**Why:**
- Rules switch 2 (`../engine_switch_rules2_2026-10/`) pins the programs sitting 1 built from candidate 08a9b3a (main c4f27f2 + P c7a25df; its `engine/` is P's tree 70652ff) as the new official engine in `rl/engine-2026-10-12/`, named main-<the pin's merge commit> (the same `engine/` tree). It changes game rules, not pilots. The working pilot stays km3 on both sides of the screen and the floor, and `floor.py` and `run_screen.py` don't change.
- The switch's `PLAN.md` step 15 (and section 0 for brews 07 and 09): the floor's pre-use re-check under km3; deck 12's new page; draft D's victini-passive page remade as on Oct 2; brew 07's and brew 09's new pages; deck 10's new page only if its t-weezing row changed; D's root and amended pages (text) from step 7c's replays.
- Dustin, Oct 9 (`PLAN.md`, the Oct 9 status; verbatim): "1-3 sure". His yes to the release package's question 3 (`RELEASE_PACKAGE.md`) covers the new floor pages after the pin: deck 12, deck 10 if its row changed, draft D's three, brew 07 and brew 09. Brew 07's and 09's conclusions stay provisional until their new pages are read (Dustin, Oct 7; `PLAN.md` section 0).
- The switch's `pin/README.md`, "After the pin": each new page goes to Dustin beside its old one, and a new failure or judgment call stops and goes to him.

**Who runs it:** the laptop session, on the laptop, after the pin commit is pushed (Push origin in GitHub Desktop). Part A first; Part B only once Part A has passed.

**When:** at home or overnight, not during class or travel. On a weekday the laptop is away from about 7 am to 5 pm Central, so no game starts after 5:15 am Central (RUN5, "Laptop schedule", Oct 4). The runner refuses to start between 5:15 am and 5 pm Central (10:15-22:00 UTC) unless `ALLOW_DAYTIME=1` is set, for a day Dustin is home. No `DECKGYM_*` variable is ever set.

## Part A: the floor's pre-use re-check (13,440 games)

The model is Oct 2's re-check (`../floor_recheck_2026-10/`), with the same five decks, calls, pilots, opponents and seeds.

**What it decides:** whether the floor stays usable on Dustin's decks on the new engine. All of these must hold:
- **brew-06 and brew-06b** (the two Payback lists, known ladder failures) read **"fail"**, with km3 on both sides, in 1,920 games.
- **The deck 14 control** (Comfey/Raticate/Hypno, k3 on both sides) reads **"untrusted"** (as a control reading).
- **A plain `run_screen.py`** at 240 games per matchup on brew-06 and brew-06b (km3, its default, the same seeds) gives exactly the floor's wins against every opponent.
- Every page names `rl/engine-2026-10-12/deckgym`.
- **The wins equal Oct 2's exactly:** brew-06 125, brew-06b 262, the control 196, brew-05b 577 and deck 07 1,098, each of 1,920.
- **Every output equals Oct 2's** in the way described below.
- If any of these fails, the result reads NOT PASSED, and the floor isn't used until Dustin has seen the pages.

**What's expected, and why: Oct 2's games, exactly.**
- No card that a rule of the switch reads is in these lists. None of the five decks or the 8 panel lists holds a coin-Ability Pokémon, a Guts or Perish Body Pokémon, Victini, Will, Ariados, Gholdengo, a Fossil, a block-coin attacker, an attack copier, Bounded Field, or one of the five hit-back attackers (a name check of the 13 files, Oct 11, against the card lists in `../coin_prevention_round2_2026-10-01/second_read_dbscan_output.txt` and the switch's `PLAN.md` section 0). Deck 14's Team Rocket's Goo-zooka raises a Retreat Cost too, but it is a Trainer's effect, not the Trap Territory Ability the switch changed.
- The switch has already shown that its rewritten lines play the old games:
  - **step 7:** every pilot's identity replays, 151,240 games equal, including k3 on scoreboard v3's 45 cells (the control's pilot);
  - **step 7b:** 28,000 table games where the off-gate counters fired, equal to the plain ones, with every round-2 exact counter 0;
  - **step 7c:** Dustin's decks 02, 06, 08, 14 and 10 replayed through `floor.py`'s own call on the new deckgym, 1,920 of 1,920 games each equal (deck 14 is the control's deck, played there under km3);
  - **step 10:** this same `run_screen` on brew-06 and 06b, on the new deckgym before the pin, equal to Sept 30's `run_screen.txt` (which Oct 2's equals but for the engine lines), and the new goldfish's coverage output byte-equal to the old one's on its check.
- The coverage reads the engine's card-status texts. The switch changed two of them, Victini's and Gholdengo's caveats in `card_validation.rs`, and no list here holds either card.
- **So every output should be byte-equal to Oct 2's, except for the engine lines:**
  - on each floor page, two lines name the programs. The "- Engine:" line names `rl/engine-2026-10-12/deckgym` in place of `rl/engine-2026-10-02/deckgym`. The "- Coverage from" line names `rl/engine-2026-10-12/goldfish` with its sha256 (d8cfb779…) in place of `rl/engine-2026-10-02/goldfish` (cecc76fb…). Nothing else on a page may differ;
  - in `run_screen.txt`, each deck's header line names `engine rl/engine-2026-10-12/deckgym`;
  - no `_games.jsonl` or `_coverage.json` file names an engine, so each must be byte-equal with no exceptions.

**The comparison.** Oct 2's files are as committed at 2d7082cf, and each is checked against its blob before any game.

| This run (here) | Oct 2's (`../floor_recheck_2026-10/`) |
|---|---|
| `brew-06-pyukumuku-silvally-payback.md`, `_coverage.json`, `_games.jsonl` | the same three names |
| `brew-06b-pyukumuku-silvally-scyther-grass.md`, `_coverage.json`, `_games.jsonl` | the same three names |
| `control_k3/14-comfey-raticate-hypno.md`, `_coverage.json`, `_games.jsonl` | the same three names, in `control_k3/` |
| `brew-05b-meowstic-hatterene-comfey.md`, `_coverage.json`, `_games.jsonl` | the same three names |
| `07-skarmory-stall.md`, `_coverage.json`, `_games.jsonl` | the same three names |
| `run_screen.txt` | `run_screen.txt` |

- **How it compares:** the runner puts the new engine lines into Oct 2's file, then needs every byte to match. Each old line must occur exactly once per page, and twice in `run_screen.txt`.
- **A difference** is listed with its line numbers and its first differing line.
- `timing.txt` (wall times) is not compared.

**Code and engine:**
- **Code:** `floor.py` and `run_screen.py` as they are on main, both unchanged by the switch (`FLOOR_PILOT = "km3"`, and the screen's defaults are km3). `run_screen.py` is the one Oct 2's re-check and the switch's step 10 ran (d7bde1af…). `floor.py` differs from the one Oct 2's re-check ran (8e5395e6…) only in draft A's entry of its ATTACKERS table (9e139e65; `../engine_switch_rules2_2026-10/floor_7c.tsv`), which no deck here reaches; step 7c ran today's `floor.py`.
- **Engine, checked before any game:**
  - the committed manifest's available release is `rl/engine-2026-10-12/deckgym`, named main-<the first 7 characters of its source commit>;
  - its deckgym, legality_scan and goldfish hashes are sitting 1's builds (`../engine_switch_rules2_2026-10/programs.sha256`: 0a9199bc…, bf9d7502…, d8cfb779…). So are the committed files on disk, their `SHA256SUMS`, and what `current_engine.py` resolves;
  - its source commit is on main and holds P (c7a25df4), and its `engine/` is P's tree 70652fff;
  - main-8626a35 is in the manifest's history, marked superseded;
  - `engine/src/players/public_pricing_player.rs` equals the source commit's (`floor.py` reads its pricing-pilot pattern from it);
  - no `DECKGYM_*` variable is set.
- **Games, opponents and seeds:** 240 games per matchup against `decks/screen/opponents/`, with seeds 7,100 + 1,000 × opponent (+500 for seat 1), the same as Sept 25, 28 and 30 and Oct 2. No new seed range.
- **Reported, not a gate:** each input's sha256, and whether it has changed since 2d7082cf. The inputs are `floor.py`, `run_screen.py`, `current_engine.py`, `lib/deckgym-database.json`, `lib/brew_pages.py`, the pricing file, the five decks and the panel lists. If an output differs, a changed input is the first place to look.

**Run:** after the pin commit is pushed, run `bash rl/results/floor_recheck_rules2_2026-10/run_check.sh` in WSL. It plays 13,440 games; Oct 2's took about 18 minutes.
- **The runner** is `run_check.sh` here: a copy of `../floor_recheck_2026-10/run_check.sh` with the new engine's folder and hashes, P and its tree, main-8626a35 as the superseded release, Oct 2's files at 2d7082cf as the reference, and the start rule above. It is committed before any game.
- **It refuses to start, and writes nothing, unless:**
  - this plan and the runner are committed unchanged;
  - no earlier run's outputs are here;
  - the engine checks above pass;
  - Oct 2's files are as committed.
- **What it writes:** the 15 floor files (the control's in `control_k3/`), `run_screen.txt`, `timing.txt`, `run_check.log` and `verdicts.txt`. The first line of `verdicts.txt` is the RESULT line:
  - `RESULT PASSED main-…: the floor stays usable under km3 on rl/engine-2026-10-12/deckgym …` (exit 0);
  - `RESULT NOT PASSED main-…: … the floor isn't used until Dustin has seen the pages` (exit 1).
- **A stop mid-run** (a program or system stop) writes "RECHECK STOPPED" to the log and no RESULT line. That is not a result. Its files are moved aside and the check is run again.

## Part B: the new floor pages (the laptop, once Part A has passed)

Each page is `floor.py`'s own call with its defaults (km3 on both sides, the official engine, 240 games per matchup, seed 7,100), unless said otherwise, written to `pages/<name>/` here. **Each new page goes to Dustin beside its old one**, and a new failure or judgment call stops and goes to him. `floor.py` has no watch build, so a page's changed games are not checked one by one: each is judged through the switch's rows that played the same mechanic, where step 8c accounted for every changed game (the switch's `PLAN.md` section 3).

1. **Deck 12** (`decks/dustin/12-ariados-whimsicott-ogerpon.txt`; 1,920 games; `pages/12/`).
   - Old page: `../floor_dustin_2026-09-30/12-ariados-whimsicott-ogerpon.md` (Sept 30 engine): clears, 602 of 1,920.
   - Expected to change in all 8 rows: each of its two Ariados now adds 1 to the Retreat Cost, which also feeds Grass Knot. Judged through B2e's pairings 80-87, the same list against the same panel (step 9).
2. **Brew 07 and brew 09** (`decks/brews/brew-07-hoopa-darkrai-sableye.txt` and `brew-09-sableye-obstagoon.txt`; 2 × 1,920 games; `pages/brew-07/`, `pages/brew-09/`).
   - Old pages: `../floor_dustin_2026-09-30/` (km3, Sept 30 engine): brew 07 clears, 1,168 of 1,920; brew 09 clears, 835.
   - They can change where a panel attacker weak to Darkness hits a Mega Sableye ex in the turn after its Cursed Jewel: the hit back now takes Weakness. Judged through step 8b's brew-07 and brew-09 v t-altaria rows (pairings 36-37 of the 23,100,000,000 block).
   - Until these pages are read, brew 07's and 09's conclusions stay provisional (Dustin, Oct 7; the switch's `PLAN.md` section 0).
3. **Draft D's victini-passive page, remade the way it was made on Oct 2** (1,920 games; `pages/D_victini-passive/`).
   - As on Oct 2 (`../floor_drafts_2026-10-02/draft-D_victini-passive/run_d2.sh`): a private copy of `floor.py` with one ROLES entry (`floor_copy.diff` there: Victini as "bench piece/passive ability", a proposed role, Dustin's to confirm), run through `run_copy.py` on D's first list.
   - D's first list is the 9cc6667 blob (sha256 4821877f…), copied to `../engine_switch_rules2_2026-10/floor_7c/d_first/draft-D-entei-grimhound.txt`. The file at the Oct 2 path was changed in place at 9e139e6. The copy's ROLES entry names the list by its path, so the rebuilt copy names the path this run uses; that is its only difference from Oct 2's diff. The copy is today's `floor.py` plus that entry.
   - Old page: `../floor_drafts_2026-10-02/draft-D_victini-passive/draft-D-entei-grimhound.md`: clears, 693 of 1,920 (a reading for Dustin, not D's floor page).
   - Expected: the same games as Oct 2's, since its games are the root page's and step 7c replayed the root page equal on the new engine. Only the engine lines and Victini's caveat text change. A game that differs is a stop, and it goes to Dustin.
4. **Draft D's root and amended pages** (text, no games; `pages/D_root/`, `pages/D_amended/`).
   - Their games are step 7c's replays (`../engine_switch_rules2_2026-10/floor_7c/D_root/` and `D_amended/`), equal to Oct 2's pages: clears, 693 and 597 of 1,920 (`../floor_drafts_2026-10-02/draft-D-entei-grimhound.md` and `draft-D_amended/`).
   - Those replays took their coverage from the old goldfish, since the manifest still named it then. So the new page is the replay's page with the new engine named and with Victini's row and the coverage file from the new goldfish (`--games 0 --coverage`, no game).
   - Expected: only the engine lines and Victini's caveat text differ from Oct 2's pages.
5. **Deck 10: no new page.** Step 7c's page check found its t-weezing row unchanged (0 of 240 games differ, wins 8 to 8; the switch's `STATUS.txt`, STEP 7c), so its Sept 30 page stands (`../floor_dustin_2026-09-30/10-xatu-oricorio-tr-weezing.md`: fails, 324 of 1,920).

Part B plays 7,680 games (deck 12, brews 07 and 09, and D's victini-passive page, 1,920 each), a few minutes a page. With Part A that is 21,120 games, under an hour at Oct 2's pace.

**Then, outside this plan:** kx3 is rebuilt on the new engine and checked, and the slow report's program is rebuilt, its self-checks replayed, and pinned again (the switch's `RELEASE_PACKAGE.md`).
