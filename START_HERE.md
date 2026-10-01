# START HERE — PocketDeckSim

Read this before anything else in the folder.
- **This page carries no status, on purpose** (Fable, Sept 28, after it went stale twice in three days). It holds only what doesn't expire: what the project is for, which engine is official, the rules for agents, where things are, and the seed registry.
- **What is running, finished or next** lives in `rl/RUN5.md`: "The plan, revised Sept 25 (approved by Dustin)", with its "Where things stand", order of work and rules. Each result's own dated folder under `rl/results/` holds its reading.
- If another file disagrees with this page on a standing fact, the other file is history. On status, RUN5 wins.

> Pocket Deck Lab (the folder beside this repo) is the archived predecessor. Deck building stays there; the simulator and bot work lives here. Anything marked *(Pocket Deck Lab only)* wasn't copied.

## What this project is for

Find 20-card Pokémon TCG Pocket decks that are creative **and** win: off-meta, catch people off guard, built around what Dustin enjoys playing (Arceus/Crobat, Xatu, poison, weird pairings). Not "the optimized deck that wins 0.1% more often." The output that counts is a deck Dustin plays on the ladder and wins with.

## The official engine (one line; the engine-switch procedure updates it)

`rl/engine-2026-09-30/` (`deckgym`, `legality_scan`, `goldfish`), main-d363ba8: rules4 plus the ten rules/09 repairs, with the km pilot (kta + N2) on both sides of the screen and the floor. `project_manifest.json` names it with its hashes, and `current_engine.py` and the screen resolve to it. Earlier engines are history there. Since Sept 30, `kt3`, `kta3`, `ktb3` and `ktc3` name the kog-based presets; the older kp-based ones replay on `rl/engine-2026-09-28/`.

## Standing facts

- **The engine rules are `0.1.0-pdl.rules4` plus the rules/09 repairs.**
  - Every engine switch follows RUN5's procedure: replays, the mechanic check, and for a rules-file refactor, games that reach the touched code.
  - The RL add-on stays at 0.7.2 on rules4. Its wheel is copied, never rebuilt ([recheck](rl/results/astra-review/rules4-addon-recheck-2026-09-22/README.md)).
  - Any new run identifies the add-on explicitly and has a fresh result identity.
- **Every deck ranking produced before 2026-09-10 is void.** They ran on an engine where Asleep/Paralyzed Pokémon could still attack and retreat. Don't re-run them; don't cite them.
- **What the simulator is for.**
  - The yardstick is the scoreboard: 45 cells scored against Limitless (the current version and its numbers are in RUN5).
  - The target real error is 5.5.
  - The simulator hasn't been shown to rank decks, so brews are judged on the ladder.
  - Card A vs card B in the same shell needs paired seeds and ≥1,000 games; differences under 5 points are noise.
- **What "competitive" means is read off Limitless**, not simulated. Snapshot and top-30 table: `decks/classifier/limitless_2026-09-10.json`. Refresh roughly monthly or when a set drops.

## The loop

Deck building has its own folder and rules: **`decks/README.md`** (*Pocket Deck Lab only*; kept separate from the bot/RL work).
- In short: draft in `decks/brews/`, then QR + Ladder Log, then Dustin plays 10-15 games, then keep, adjust or retire.
- What the bot screen may be used for at the moment (the floor check, holds on ranking) is in RUN5.

## Before you do anything

Read `RULES_FOR_AGENTS.md` (one page: Pocket's rules, where they differ from the physical TCG).
Never state a card's text from memory — `python lib/card.py "<name or id>"` prints it.
When your session ends, add one dated line to `LOG.md` (*Pocket Deck Lab only*) in plain words: who you are, what changed.

## Where things are

- `rl/RUN5.md`: the approved plan, its rules and "Where things stand" (all status). `rl/results/<topic>_<date>/`: each run's files and reading. `project_manifest.json`: the official engine and its hashes.
- `RULES_FOR_AGENTS.md` — the rules. `lib/card.py` — card lookup. `LOG.md` — one line per session (*Pocket Deck Lab only*).
- `decks/dustin/` — Dustin's 15 real decks, decoded from in-game QR codes.
- `decks/README.md` — deck-building rules, the quick screen and its pass bar (*Pocket Deck Lab only*).
- `decks/brews/` — draft lists to playtest + `BREW_NOTES_2026-09-10.md` (the ideas and why).
- `decks/classifier/` — classifier inputs, Limitless snapshot, full classifier report.
- `decks/history/` (*Pocket Deck Lab only*) — what the Sept 5–9 battle recordings were (mostly AI games; don't re-mine).
- Ladder results this season: the **Ladder Log** artifact (Claude-hosted page); read it back before adjusting a list.
- `lib/deck_classifier.py` (what a deck is built to do, what pairs with a card),
  `lib/decode_qr.py` (QR screenshot → decklist), `lib/deck_check.py` (20-card legality).
- `docs/AUDIT_2026-09-10/` — the independent audit: engine findings, project history, known failures
  (`02_PROCESS_AND_HISTORY.md` has the KNOWN_FAILURES table), recommendations.
- `engine/UPSTREAM.md` — how the fork differs from upstream and what to do at the
  next set merge. Five B4a cards are still `RulesUnverified` (listed there).

## What NOT to treat as current

`HANDOFF.md`, `CURRENT.md`, `CURRENT-CORE.md`, `current_best_decklists.txt`, the historical
entries in `decks/index.json`, `STATIONS.md`, `station.sh`, `gates.sh`, the `claims/` folder,
`meta9_SPEC.md` and every `meta*`/`zoroark*`/`s1NN_*` file in the root (all *Pocket Deck Lab only*). `Boss Folder/` (Pocket Deck Lab) is
Astra's working area; its dated packages are records of runs, not instructions.

## Who does what (updated Sept 24)

Dustin owns it and decides.
- **Changed Sept 24 evening:** the roles below are Pocket Deck Lab's earlier text; current roles are in `PROJECT_INSTRUCTIONS.md`.
- **Opus (Claude)** leads and builds the RL work, runs checks, analyses and sim runs, and does deck
  discovery (classifier, brews, Limitless reading). Its tokens are cheap, so it runs checks, follow-up
  analyses and cloud runs without asking at every step, unless Dustin says tokens are low. It still
  asks before changing direction or editing shared instruction files (this page, AGENTS.md in Pocket Deck Lab, the plan
  in rl/RUN5.md).
- **Fable (Claude)** reviews designs and results. Its tokens are expensive, so it builds or runs
  things only when Dustin asks.
- **Astra (Codex)** owns the engine and reviews code; keep its use targeted (AGENTS.md cost principle, Pocket Deck Lab).
- **All agents, against clutter and over-engineering:** report in plain language. No new gates,
  stations, process documents or top-level files unless Dustin asks; results for asked work go in that
  run's results folder. Build the simplest thing that answers the question, and skip side studies
  unless they decide something.

## The mistakes this project has already made (don't repeat them)

Ranking decks on an engine nobody had checked against the rules. Publishing findings before
replicating them (~28 retractions in the old ledgers). Building process — 34 gates, stations,
claim files, 1,100+ root files — instead of decks. Four different "current" engines at once.
Sixty sessions on video/OCR that never read a single card. Fixating on one deck (Zoroark) that
the sim liked and the ladder didn't. Full list with what catches each: `docs/AUDIT_2026-09-10/`.

## Seed ranges already used

**Seed ranges already used.** Pick a new block outside all of these for any new measurement. Everything up to
Run 5 stage 1 is from `rl/results/run5_build/BUILD_NOTES.md` ("Ranges already used", read from the code) and
its seed-overlap check; the rest was added since.

| Seeds | Used by |
|---|---|
| 1,000,000,000+ | run 1 training |
| 2,000,000,000+ | run 2 training |
| 3,000,000,000 – about 3,106,000,000 | runs 3–4 training (Run 5 step 0 reused run 4's pilot seeds) |
| 5,000,000,000+ | Run 5 practice runs (cloud) |
| 6,000,000,000 – 8,901,999,999 | Run 5 stage 1 training (attempts 0–29) |
| 9,000,000,000 – 9,800,000,000 blocks | the launcher's practice block (Run 5 build tests) |
| 10,000,000,000 – 12,901,999,999 | Hydreigon run training |
| 13,000,000,000 – 13,300,000,000 blocks | Hydreigon run evaluation (k3, random, confirmation, held-out) |
| 14,000,000,000 – 17,999,999,999 | reserved: Altaria detector network training (not started; after kd is read) |
| 18,000,000,000 – 18,300,000,000 blocks | reserved: Altaria detector network evaluation (k3, random, confirmation, transfer) |
| 19,000,000,000 – 19,800,000,000 blocks | Opus's cloud practice test of the Hydreigon settings (program test only) |
| 20,000,000,000+ | Claude Code diagnostics (Caterpie counterplay from 20.0B); 21,000,000,000 – 21,001,999,999: Hydreigon pair checks and readout smoke tests (Sept 24); 21,002,000,000+: the laptop's A1 build (branch `laptop/engine-first-2026-09-24`); 21,020,000,000 + pairing × 100,000 + i, i < 200: discard-attack census (Sept 25); 21,030,000,000 – 21,032,079,999: Raticate brew pilot check; 21,050,000,000 – 21,064,079,999: all-15-decks pilot check (Sept 25); 21,070,000,000 – 21,093,079,999: A2 screen re-run with kp3 (Sept 25); 21,100,000,000 – 21,100,999,999: floor.py development runs and checks (Sept 25); 21,101,000,000 – 21,101,300,001: the Altaria detector network's pair checks (Sept 25); 21,102,000,000 – 21,102,999,999: Skarmory Tool/Jasmine causal test (Sept 25); 21,103,000,000 – 21,103,999,999: blind-quiz candidate games (Sept 25); 21,104,000,000 – 21,104,999,999: Trainer audit (Sept 25); 21,105,000,000 – 21,105,999,999: Field Blower/Stadium run (Sept 25); 21,106,000,000 – 21,106,999,999: B2e held-out rows and their smokes (Sept 26; the gauntlet variation check reuses pairings 40–47's deals for Charizard Y, on purpose, for pairing); 21,107,000,000 – 21,107,199,999: ladder-panel calibration, reserved (`decks/screen/panel_ladder_2026-09-26/`); 21,108,000,000 – 21,108,249,999: gauntlet additions, 21,108,000,000 + pairing × 10,000 + i, i < 500, 25 pairings (Scizor coverage row, pairings 0–7, reserved and not run until the repaired engine; Rayquaza and Altaria/Greninja scoreboard cells, 8–24), k3 and kp3, smokes included (Sept 26, `rl/results/gauntlet_runs_2026-09-26/`; kpr3 on the same deals in `kpr3/`); 21,108,900,000 – 21,108,999,999: pilot traces with deckgym simulate `--seed-stream` (Sept 26, `rl/results/gauntlet_runs_2026-09-26/pilot_trace/`); 21,109,000,000 – 21,109,000,499: koa's variant-list row, LaNora's Altaria list against the table's own Altaria list (koa registration amendment 2, Sept 27); 21,110,000,000 – 21,200,799,999: Altaria B2c play-outs (21.110B+) and kp3 probes (21.160B+), smokes included (Sept 26); 22,000,000,000 – 22,599,999,999: the cloud's Sept 25 overnight list (its own row below); new blocks go above the last one used |
| 7,100 – 14,719 | the quick screen and the A2 floor check: seed 7,100 + 1,000 × opponent (deck in seat 0) and + 500 (seat 1), `--seed-stream`, 8 opponents; the floor plays 120 games per call (240 per matchup) |
| 1M, 2M, 8M, 9M | step-3 checks |
| 5M, 6M | v2.2 checks (Astra's rules4 recheck also 6M) |
| 18M, 18.5M, 18.9M, 28.5M | step-1 checks (18M, 18.5M); Astra's interface checks (18.5M, 28.5M) and mirror benchmark (18.9M) |
| 20M, 21M, 22M, 30M | run 1 (k3, random, previous checkpoints, confirmation) |
| 40M, 41M, 43M | matchup tests; knockout audit v2 (43M) |
| 50M | k3 screen; speed tests; Astra's screen benchmark |
| 60M, 61M, 62M, 70M | run 2 (k3, random, previous checkpoints, confirmation); speed tests (60M); step-3 checks (70M) |
| 72,000,000 – 72,279,999 | Limitless check k3 table (72,000,000 + pairing × 10,000 + game), deeper-search tables k4–k6, the d3/p3/y3 probes, list-refresh variant games, Hydreigon transcripts, option B first look and option B table (Sept 24, i < 500); every later table and mixed row (b3n1, kp3, kq3, kd3; Hydreigon, Vespiquen and kd3 mixed rows), the rules/09 fix replays and the gauntlet variation check (Sept 26) reuse these deals on purpose, for pairing |
| 73,000,000+ | auditor's part 2 (bot vs bot) |
| 80,000,000 – 80,951,000 | runs 3–4 k3 evaluation (also step 0) |
| 81,000,000 – 81,100,000 | runs 3–4 random-move games (also step 0) |
| 81,000,000 – 81,070,000 | Claude Code Quick Growth diagnostic. **Overlaps the runs 3–4 random-move range above**; it matters only if these games are compared or pooled with those |
| 82M | run 3 previous-checkpoint games |
| 83,000,000 – 83,505,199 | Run 5 stage 1 (k3 from 83.0M, random from 83.5M) |
| 84M – 87M | Run 5 practice runs (cloud) |
| 88,000,000 – 88,999,999 | reserved for Run 5 stage 2 (dropped; still reserved) |
| 89,000,000 – 89,999,999 | Run 5 stage 1 confirmation (89.0M) and held-out (89.5M, unused) |
| 90,000,000 – 90,910,000 | runs 3–4 bars and confirmation (also step 0); Astra's rules4 pool benchmark (90M) |
| 95M+ | runs 3–4 held-out (also step 0) |
| 96,092,200 – 96,092,201 | Astra's add-on/CLI parity check |
| 97,000,000 – 97,999,999 | crossplay |
| 22,000,000,000 – 22,599,999,999 | Claude Code, Sept 25 overnight list: kp3 equivalence test (22.0B), brew card-draw model (22.1B, Python), brew goldfish (22.2B), Lucario network games (22.3B), their rollouts (22.4B) and k3 probes (22.5B) |
| 22,600,000,000 – 22,699,999,999 | Claude Code, kt's Dustin-deck A/B (registered Sept 26 in `rl/results/kt_2026-09-26/README.md`; 1,920 games per arm; played Sept 29, `rl/results/kt_tables_2026-09-28/`) |
| 22,700,000,000 – 22,700,079,999 | Claude Code, kt's clause (d) rows: the Dragonair Mega Rayquaza ex list against the eight panel lists (kt amendment 1, Sept 26; 22.7B + panel index × 10,000 + i, i < 500; played Sept 29) |
| 22,800,000,000 – 22,800,099,999 | Claude Code, X Speed census (Sept 27, `rl/results/xspeed_census_2026-09-27/`): 22.8B + 10,000 × deck + 1,000 × opponent (+500 seat 1), `--seed-stream`, 15 games per call |
| 22,801,000,000 – 22,801,319,999 | Claude Code, the Sept 28 engine switch's touched-path check (`rl/results/engine_switch_2026-09-28/touched/`): 22.801B + pairing × 10,000 + i, 32 pairings (decks 07 and 05, the metal-barrier example, a 2-Blue test list, each v the 8 panel lists) |
| 22,900,000,000 – 22,900,081,499 | Claude Code, km's clause (d) Lucario rows (registered Sept 29, `rl/results/trainer_pricing_2026-09-28/REGISTRATION_DRAFT.md`, step 4 (d)): 22,900,000,000 + row × 10,000 + j, j < 1,500, rows 0–8 (the 7 table cells in pairing order, then Rayquaza v Lucario, then Altaria/Greninja v Lucario), Lucario in seat 0 on even j; deals 0–499 of each row are the table's own (72,000,000 and 21,108,000,000 blocks), reused on purpose; (d) plays both arms on them itself |
| 23,000,000,000 – 23,009,999,999 | Claude Code, kta's fresh deals (registered Sept 29, `rl/results/kta_2026-09-29/REGISTRATION.md`, section 3.2 for the sub-blocks; clause (d) at 23,003,000,000 + row × 10,000 + i, i < 2,000) |
| 23,100,000,000 – 23,100,999,999 | Claude Code, the rules engine switch (registered Sept 30, `rl/results/engine_switch_rules_2026-10/PLAN.md` step 8): 23,100,000,000 + pairing × 10,000 + i; pairings 0–31 step 8's carrier games (km3 i < 500, k3 i < 250), 32–35 step 8b's scratch-deck rows, 40–71 sitting 1's step 7c (Dustin's decks 02, 06, 08 and 14 v the 8 panel lists, i < 60; `pairs_7c.tsv`, `seeds_7c.txt`) |
