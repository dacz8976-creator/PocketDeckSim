# START HERE — PocketDeckSim (from Pocket Deck Lab, 2026-09-24)

Read this before anything else in the folder. It is the only summary that is current. If another
file disagrees with it, the other file is history.

> This is Pocket Deck Lab's START_HERE.md as of Sept 24, 2026 (Dustin's laptop), with paths translated to
> this repo. Deck building stays in Pocket Deck Lab; the simulator and bot work lives here. Anything marked
> *(Pocket Deck Lab only)* wasn't copied. The last section (what's running, seed ranges) is added for this repo.

## What this project is for

Find 20-card Pokémon TCG Pocket decks that are creative **and** win — off-meta, catch people off
guard, built around what Dustin enjoys playing (Arceus/Crobat, Xatu, poison, weird pairings). Not
"the optimized deck that wins 0.1% more often." The output that counts is a deck Dustin plays on
the ladder and wins with.

## What is true right now

- **The engine is `0.1.0-pdl.rules4`** (September 22). It retains the earlier rules repairs,
  player-selected Energy discards and corrected Cubone/Clefable/Bonsly effects, and fixes the
  T2 last-Pokemon/third-point result to a tie. `project_manifest.json` names the verified executable (`rl/addon-0.7.2/deckgym`, copied from
  Pocket Deck Lab on Sept 24 with its hash unchanged; identities: `rl/addon-0.7.2/release-identity.json`).
  Verification: 1,826 engine tests, 44 accepted-review segments and four k3 smoke games.
  See the [rules4 repair and evidence limits](rl/addon-0.7.2/rules4-repair-README.md)
  and earlier rules3 repairs (`Boss Folder/rules3-repairs-2026-09-22/README.md`, *Pocket Deck Lab only*).
  The RL add-on is now **0.7.2** on rules4. Its chosen-pair replay, hidden-card, forecast and
  choice-encoding checks passed, and all 47,800 benchmark games are complete and validated. See the
  [current add-on recheck](rl/results/astra-review/rules4-addon-recheck-2026-09-22/README.md).
  Historical binaries, results and training environments are preserved. Any new run must identify
  the add-on explicitly and have a fresh result identity. Run 5's step 0 and stage 1 finished Sept 23;
  its stage 2 is dropped. Results and the plan after it: `rl/RUN5.md`.
- **Every deck ranking produced before 2026-09-10 is void.** All of them (meta4–meta9, the
  Zoroark work, the Sept 8 eval18 panel) ran on an engine where Asleep/Paralyzed Pokémon could
  still attack and retreat. Don't re-run them; don't cite them.
- **What the simulator is good for (measured Sept 23).** Against 25,143 real B4a matches, k3 vs k3
  on rules4 calls the favorite right in 23 of 28 top-deck matchups (15 of 16 clearly one-sided ones).
  Its typical miss is about 9 points, with some 20–30-point misses: it underrates Altaria and Vespiquen
  and overrates Sceptile (being checked). It hasn't been shown to rank decks, and brews can't be checked
  this way; the ladder still judges those. Details:
  `rl/results/limitless_check_2026-09-23.md`. Card A vs card B in
  the same shell still needs paired seeds and ≥1,000 games; differences under 5 points are noise.
- **What "competitive" means is read off Limitless**, not simulated. Snapshot and top-30 table:
  `decks/classifier/limitless_2026-09-10.json`. Refresh roughly monthly or when a set drops.

## The loop

Deck building has its own folder and rules: **`decks/README.md`** (*Pocket Deck Lab only*; kept separate from the bot/RL
work). In short: draft in `decks/brews/` → QR + Ladder Log → Dustin plays 10–15 games → keep, adjust or
retire. Brew screening and its cutoffs wait until the engine is trustworthy and realistic (Dustin, Sept 24); the quick bot screen (`decks/screen/`) is on hold until then.

## Before you do anything

Read `RULES_FOR_AGENTS.md` (one page: Pocket's rules, where they differ from the physical TCG).
Never state a card's text from memory — `python lib/card.py "<name or id>"` prints it.
When your session ends, add one dated line to `LOG.md` (*Pocket Deck Lab only*) in plain words: who you are, what changed.

## Where things are

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

## Running now, and seed ranges already used (added for this repo, Sept 24; refreshed Sept 25 morning)

**The current plan** is "The plan, revised Sept 25 (approved by Dustin)" at the end of `rl/RUN5.md`. It supersedes
the Sept 24 plan. The full record and every number behind it is section 8 of `docs/REVIEW_2026-09-24_direction.md`;
the per-candidate table readings are indexed in `rl/results/table_readings_2026-09-24/README.md`.

**Finished**
- **The Hydreigon network run** (Sept 24–25, `runs/diag-hydreigon-lucario`): +40.8 over k3, two k3 blind spots
  found (Darkness Claw pricing, the Hyper Ray chip). Reading: `rl/results/hydreigon_network_readout/READING.md`;
  summary in section 8. It was the last run of that family; run 6 is B7 in the plan and not now.
- **Scoreboard v2** (the 28 cells rebuilt from the development half's pairings; holdout reserved):
  `rl/results/scoreboard_v2_2026-09-25/`.
- **Brew pilot checks** (k3 against kp3 on Dustin's decks): `rl/results/brew_pilot_check_2026-09-25/`.
- **Earlier:** the deeper-search table (k4–k6 don't help, Sept 24), the option B and kp3 table readings, the
  discard-attack census.

**Running or next** (in the plan's order): the A2 screen re-run with kp3 on both sides (a diagnostic on the scratch
add-on, for Dustin's decision on the screen hold; the screen's own switch to kp3 needs a new engine build, see RUN5's
A2 line); kd (the defender's Weakness and reductions in the clock) built in the cloud, read against kp3 on v2; kpr
after it. The quick bot screen stays on hold until Dustin lifts it.

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
| 19,000,000,000 – 19,800,000,000 blocks | Opus's cloud practice test of the Hydreigon settings (program test only) |
| 20,000,000,000+ | Claude Code diagnostics (Caterpie counterplay from 20.0B); 21,000,000,000 – 21,001,999,999: Hydreigon pair checks and readout smoke tests (Sept 24); 21,002,000,000+: the laptop's A1 build (branch `laptop/engine-first-2026-09-24`); 21,020,000,000 + pairing × 100,000 + i, i < 200: discard-attack census (Sept 25); 21,030,000,000 – 21,032,079,999: Raticate brew pilot check; 21,050,000,000 – 21,064,079,999: all-15-decks pilot check (Sept 25); 21,070,000,000 – 21,093,079,999: A2 screen re-run with kp3 (Sept 25); 22,000,000,000 – 22,500,000,000: the cloud's Sept 24–25 diagnostics; new blocks go above the last one used |
| 1M, 2M, 8M, 9M | step-3 checks |
| 5M, 6M | v2.2 checks (Astra's rules4 recheck also 6M) |
| 18M, 18.5M, 18.9M, 28.5M | step-1 checks (18M, 18.5M); Astra's interface checks (18.5M, 28.5M) and mirror benchmark (18.9M) |
| 20M, 21M, 22M, 30M | run 1 (k3, random, previous checkpoints, confirmation) |
| 40M, 41M, 43M | matchup tests; knockout audit v2 (43M) |
| 50M | k3 screen; speed tests; Astra's screen benchmark |
| 60M, 61M, 62M, 70M | run 2 (k3, random, previous checkpoints, confirmation); speed tests (60M); step-3 checks (70M) |
| 72,000,000 – 72,279,999 | Limitless check k3 table (72,000,000 + pairing × 10,000 + game), deeper-search tables k4–k6, the d3/p3/y3 probes, list-refresh variant games, Hydreigon transcripts, option B first look and option B table (Sept 24, i < 500) |
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
