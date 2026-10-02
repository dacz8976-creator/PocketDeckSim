# The floor's pre-use re-check under km3, after the rules engine switch (Oct 2026)

**Written and committed with the pin, before any game of this check** (the rules switch's `PLAN.md` step 13). The result is the RESULT line at the top of `verdicts.txt`, which `run_check.sh` writes. This plan is not edited afterwards.

**Why:**
- The rules switch (`../engine_switch_rules_2026-10/`) pins the programs sitting 1 built from candidate 5a18d31 (main c9f4224 + R f8cfa9c; engine/ is R's tree 38af8b0) as the new official engine in `rl/engine-2026-10-02/`, named main-<the pin's merge commit> (its engine/ is the same tree). It changes game rules, not pilots. The working pilot stays km3 on both sides of the screen and the floor, and `floor.py` and `run_screen.py` don't change.
- The switch's `PLAN.md` step 15: "The floor's pre-use re-check under km3. brew-06 and 06b must read 'fail', and the deck 14 k3 control 'untrusted'. `run_screen` must give the floor's wins exactly. It should equal Sept 30 exactly: 125, 262, 196, 577 and 1,098. If it fails, the floor isn't used until you have seen the pages."
- Dustin, Oct 1 evening (the switch README, "Dustin's word on game 28 and the pin"): "Complete the planned checks after the pin. Bring me any new failure or judgment call; otherwise proceed."
- The model is Sept 30's re-check (`../floor_recheck_2026-09-30/`), with the same five decks, calls, pilots, opponents and seeds.

**What it decides:** whether the floor stays usable on Dustin's decks on the new engine. All of these must hold:
- **brew-06 and brew-06b** (the two Payback lists, known ladder failures) read **"fail"**, with km3 on both sides, in 1,920 games.
- **The deck 14 control** (Comfey/Raticate/Hypno, k3 on both sides) reads **"untrusted"** (as a control reading).
- **A plain `run_screen.py`** at 240 games per matchup on brew-06 and brew-06b (km3, its default, same seeds) gives exactly the floor's wins against every opponent.
- Every page names `rl/engine-2026-10-02/deckgym`.
- **The wins equal Sept 30's exactly:** brew-06 125, brew-06b 262, the control 196, brew-05b 577 and deck 07 1,098, each of 1,920.
- **Every output equals Sept 30's** in the way described below.
- If any of these fails, the result reads NOT PASSED, and the floor isn't used until Dustin has seen the pages.

**What's expected, and why: Sept 30's games, exactly.**
- No list here holds a card either repair is about. None of the five decks or the 8 panel lists has a coin-Ability Pokémon (Meowth B2 124/204, Togekiss A4 080, Bastiodon A2 114, Hisuian Goodra B3b 050) or a Victini (B3 025, P-B 049). So neither repair's gate ever holds in these games.
- The games do run B's rewritten lines, but only where the gate doesn't hold. These come from deck 14's Team Rocket's Hypno and the panel's Heatmor (t-blaziken), Chien-Pao ex (t-suicune), Hitmonlee (t-lucario), Grovyle (t-sceptile) and Vespiquen ex's Chase Order (t-vespiquen). The switch has already shown that those lines play the old games:
  - **step 7:** every pilot's identity replays, 151,240 games equal, including k3 on scoreboard v3's 45 cells (the control's pilot);
  - **step 7b:** 28,000 table games where both off-gate counters fired (in 12,246 and 3,353 games), equal to the plain ones, with every repair counter 0;
  - **step 7c:** Dustin's decks 02, 06, 08 and 14 replayed through `floor.py`'s own call on the new deckgym, 1,920 of 1,920 games each equal (deck 14 is the control's deck, played there under km3);
  - **step 10:** this same `run_screen` on brew-06 and 06b, on the new deckgym before the pin, equal to Sept 30's `run_screen.txt`; and the new goldfish's coverage output byte-equal to the old one's.
- The coverage reads the engine's card-status texts. The switch changed one of them, Victini's caveat in `card_validation.rs`, and no list here holds a Victini.
- **So every output should be byte-equal to Sept 30's, except for the engine lines:**
  - on each floor page, two lines name the programs. The "- Engine:" line names `rl/engine-2026-10-02/deckgym` in place of `rl/engine-2026-09-30/deckgym`. The "- Coverage from" line names `rl/engine-2026-10-02/goldfish` with its sha256 (cecc76fb…) in place of `rl/engine-2026-09-30/goldfish` (8f6056a0…). Nothing else on a page may differ;
  - in `run_screen.txt`, each deck's header line names `engine rl/engine-2026-10-02/deckgym`;
  - no `_games.jsonl` or `_coverage.json` file names an engine, so each must be byte-equal with no exceptions.

**The comparison.** Sept 30's files are as committed at 654d139, and each is checked against its blob before any game.

| This run (here) | Sept 30's (`../floor_recheck_2026-09-30/`) |
|---|---|
| `brew-06-pyukumuku-silvally-payback.md`, `_coverage.json`, `_games.jsonl` | the same three names |
| `brew-06b-pyukumuku-silvally-scyther-grass.md`, `_coverage.json`, `_games.jsonl` | the same three names |
| `control_k3/14-comfey-raticate-hypno.md`, `_coverage.json`, `_games.jsonl` | the same three names, in `control_k3/` |
| `brew-05b-meowstic-hatterene-comfey.md`, `_coverage.json`, `_games.jsonl` | the same three names |
| `07-skarmory-stall.md`, `_coverage.json`, `_games.jsonl` | the same three names |
| `run_screen.txt` | `run_screen.txt` |

- **How it compares:** the runner puts the new engine lines into Sept 30's file, then needs every byte to match. Each old line must occur exactly once per page, and twice in `run_screen.txt`.
- **A difference** is listed with its line numbers and its first differing line.
- `timing.txt` (wall times) is not compared.

**Code and engine:**
- **Code:** `floor.py` and `run_screen.py` as they are on main, both unchanged by the switch (`FLOOR_PILOT = "km3"`, and the screen's defaults are km3). `run_screen.py` differs from Sept 30's only by the opt-in `--weights` readout (6d74513, 950f112). This run doesn't use it; step 10 ran this `run_screen.py`, without `--weights`, and matched Sept 30's `run_screen.txt`.
- **Engine, checked before any game:**
  - the committed manifest's available release is `rl/engine-2026-10-02/deckgym`, named main-<the first 7 characters of its source commit>;
  - its deckgym, legality_scan and goldfish hashes are sitting 1's builds (`../engine_switch_rules_2026-10/programs.sha256`: 2f7e5fd6…, 97891274…, cecc76fb…). So are the committed files on disk, their `SHA256SUMS`, and what `current_engine.py` resolves;
  - its source commit is on main and holds R (f8cfa9c), and its engine/ is R's tree 38af8b0;
  - main-d363ba8 is in the manifest's history, marked superseded;
  - `engine/src/players/public_pricing_player.rs` equals the source commit's (`floor.py` reads its pricing-pilot pattern from it).
- **Games, opponents and seeds:** 240 games per matchup against `decks/screen/opponents/`, with seeds 7,100 + 1,000 × opponent (+500 for seat 1), the same as Sept 25, 28 and 30. No new seed range.
- **Reported, not a gate:** each input's sha256, and whether it has changed since 654d139. The inputs are `floor.py`, `run_screen.py`, `current_engine.py`, `lib/deckgym-database.json`, `lib/brew_pages.py`, the pricing file, the five decks and the panel lists. If an output differs, a changed input is the first place to look.

**Run:** after the pin commit, run `bash rl/results/floor_recheck_2026-10/run_check.sh` in WSL. It plays 13,440 games and takes about 25-60 minutes (Sept 30's took 23).
- **When:** at home or overnight, not during class or travel. On the Oct 1-2 schedule the laptop leaves at 7 am Central. So the runner won't start between 5:30 am and 5 pm Central (10:30-22:00 UTC) unless `ALLOW_DAYTIME=1` is set, for a day Dustin is home.
- **It refuses to start, and writes nothing, unless:**
  - this plan and the runner are committed unchanged;
  - no earlier run's outputs are here;
  - the engine checks above pass;
  - Sept 30's files are as committed.
- **What it writes:** the 15 floor files (the control's in `control_k3/`), `run_screen.txt`, `timing.txt`, `run_check.log` and `verdicts.txt`. The first line of `verdicts.txt` is the RESULT line:
  - `RESULT PASSED main-…: the floor stays usable under km3 on rl/engine-2026-10-02/deckgym …` (exit 0);
  - `RESULT NOT PASSED main-…: … the floor isn't used until Dustin has seen the pages` (exit 1).
- **A stop mid-run** (a program or system stop) writes "RECHECK STOPPED" to the log and no RESULT line. That is not a result. Its files are moved aside and the check is run again.
