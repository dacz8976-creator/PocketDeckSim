# Engine candidate, Oct 20, 2026: the self-checks, old v new

**This is a CANDIDATE. It is not adopted.**
- main, START_HERE, the pin documents, `project_manifest.json`, `current_engine.py`, `rl/engine-2026-10-12/` and the frozen AI judge (frozen-4, engine 70652fff) are untouched.
- Adoption follows Astra's review and Dustin's yes.
- No API spend.

The list of changes and the results each was expected to change was written BEFORE any build: `PLAN.md`, the first commit on this branch (b27e776b, 02:05Z; the build started 02:09Z). The verification found two errors in that list; they are named under "What PLAN got wrong" and were checked with extra runs.

## What was built
**The candidate:** branch `laptop/engine-candidate-2026-10-20`.
- The programs were built from d9d2e704, engine tree 12e23abd.
- The ported tests came in ccb1d3b5 (engine/tests only). So the branch tip's engine tree is 300030ce, not the built tree: the only difference is `engine/tests/` (3 files changed, 7 added).
- An adoption must either pin d9d2e704's tree or state that tests-only exception. The last pin required main's engine/ to be byte-identical to the built tree.

| Commit | Change | Group if it moves a game |
|---|---|---|
| 501fc1dd | the Growl-to-0 rule (cherry-picked from claude/growl-zero-no-weakness b887a9f8; same patch, same engine tree) | (a) rule fix |
| 9c51453b | upstream #385: on-play "from your hand onto your Bench" Abilities only on the owner's turn | (b) upstream |
| 75343578 | upstream #390: random multi-hit damage grouped by hit counts, in a fixed order | (b) upstream |
| 42d2dd8e | upstream #401, Fossil part: DiscardFossil offered once | (b) upstream |
| 764f7459 | upstream #344, narrow: Dragon/Colorless Energy zones invalid; named panic | (b) upstream |
| d9d2e704 | engine/UPSTREAM.md refresh (doc) | none |
| ccb1d3b5 | ported tests (#385 plus a Team Rocket's Boss case, #401, #344, #383, #346, #347, #348) | none |

**Build:** one `git archive` of d9d2e704 (engine and decks) into a fresh folder with an empty target directory: `cargo build --release --locked`, plus `--example legality_scan` and `--example goldfish`. Settings were CARGO_BUILD_JOBS 2, nice 19 and ionice -c3, and it took 527 s.

**The tested programs** are in `programs/`. They are the bytes the candidate side of every check ran (the floor pages' coverage half aside, see below), copied at 02:18Z before the test suite and never rebuilt.
- deckgym 245e11e8cf939da7ba12a50fbb18630c67b1fb2231a692dd0c259c4a01556745
- legality_scan bce5654bb51b8b8bc201fba353267c575c168291959c32de6ee1365ecf7db8e9
- goldfish f53e948997326174103d917642cde78edb788098a7e8a5faf702096c91390e35

The later `cargo test --features test-utils` runs rebuilt the build folder's `target/release`. Only `programs/` holds the tested bytes; the original build outputs also survive in that target under their hashed names.

**The strength harness for the self-checks** (`rl/strength/build.sh`, own build and target folders; the slow report's pinned program was not touched):
- km3 build: 04fadd96870e4a7876a8eebc3f86721d42bfab62ed8e4906cb0986228948680f
- kx3 build: the candidate with laptop/kx3-on-rules2's kx3 files laid over it, six files: five added (playout_player.rs, playout_pool.rs, an example, two tests) and players/mod.rs modified. Hash 068c993a3251a4d02f5aa7cbbee65bb2c3116ffeb548ddad9f641501af2cd725.
- **Deviation from PLAN:** both strength builds ran at 8 cargo jobs, at nice 19 without ionice. `build.sh` sets CARGO_BUILD_JOBS from STRENGTH_JOBS (default 8), which overrode the drivers' setting. PLAN said 2 jobs and ionice. Both builds were inside the night window, one cargo at a time.
- The build records (`*.build.json`) are in `programs/`. The strength binaries and U's and V's legality_scan stay on the laptop. Their hashes and the U and V refs and engine trees are in `programs/other_programs.sha256`; its paths are relative to the laptop's `pincand_work/programs`.

**The old pin is intact:**
- `rl/engine-2026-10-12/` is unchanged.
- Its three programs pass `sha256sum -c SHA256SUMS`.
- They were run from a copy and still reproduce their own records (below).

## Results
**The engine test suite** (`cargo test --release --features test-utils --locked --no-fail-fast`, a test-utils build, not the shipped bytes):
- 2,108 passed and 0 failed at d9d2e704. That fits 2,106 for the Growl branch (inferred: 2,108 minus #390's 2 tests) plus #390's 2 unit tests. The Growl branch itself recorded only "417 lib tests and every integration test pass".
- 2,125 passed and 0 failed with the ported tests (the working-tree files, byte-equal to ccb1d3b5's).

**Self-check digests:**

| Check | Old | New | |
|---|---|---|---|
| km3 self-check (12 games, t-altaria v t-suicune) | 81b572198c04d5d1 (slow-report pin 76df495b, re-run tonight) | 81b572198c04d5d1 | same |
| kx3 poolmeta self-check | 31d638dbc818b0fa (recorded on 76df495b) | 31d638dbc818b0fa | same; PLAN listed it under "Possible" |

**How each kind of run is compared** (the depth differs):
- **legality_scan rows:** every field the reference records (18 to 21 depending on the table, always including the move and decision hashes), with `switch_check.py same`. A game that plays differently anywhere differs here.
- **Floor pages:** 14 per-game summary fields, no moves or decisions (`sitting1_check.py floor`).
- **The CLI:** the whole output except the "Ran ..." timing line (the win, draw and averages lines included). **run_screen:** its 20 summary lines. **goldfish:** the page and the coverage file.
- The CLI and goldfish runs keep their result in `summary.tsv`; they have a `.cmd` but no `.cmp`.
- So for the 18,480 floor, CLI and screen games, "same" means the same outcomes and summaries, not the same play. The change count below is a lower bound for them.
- legality_scan ran with RAYON_NUM_THREADS 8. Games are matched by (pairing, i). The .run records don't name the references' thread count; every identical replay supports the invariance.

**Replays of the old pin's recorded games:**
- The references are `rl/results/engine_switch_rules2_2026-10/08a9b3a_*` plus the `floor_7c/` pages. Each replayed reference was played by the pinned programs (every replayed .run names legality_scan bf9d7502, deckgym 0a9199bc or goldfish d8cfb779). The floor pages' coverage was recorded by the Oct 2 goldfish.
- The inputs (decks, pairs files) equal the recorded ones: 34/35, the manifest aside, 65/65 and 16/16.
- The floor pages run floor.py, which takes the manifest's goldfish for the coverage. So the candidate's floor rows test the candidate deckgym with the OLD goldfish. The candidate goldfish is tested by step 10's goldfish row.

| Run | Games | Old | New |
|---|---|---|---|
| step 10: CLI k3, kp3, kog3, kta3, km3 (240 each) | 1,200 | re-run: same | same |
| step 10: goldfish --coverage | - | re-run: same | same |
| step 10: run_screen, brews 06 and 06b | 3,840 | re-run: same | same |
| floor pages 02, 06, 08, 10, 14 (Dustin's decks) and draft D root and amended; every page has a t-lucario row (Bonsly) | 13,440 | recorded | same (14 summary fields; D pages with the pre-set B3 025 caveat allowance) |
| research table, 28 cells: k3, kp3, km3 (14,000 each) | 42,000 | recorded | same |
| research table: kog3, kq3, kta3 dev, kta3 fresh (14,000 each) | 56,000 | recorded | same |
| research table: kd3, kpr3 (1,120 each) | 2,240 | kd3 re-run: same | same |
| km3 coverage: the second lists v-lucario_2 (Bonsly), v-suicune_2, v-weezing_2, l-charizardy; Scizor | 18,500 | recorded | same |
| km3 coverage: B2e, 96 pairings | 48,000 | recorded | same |
| step 8 and 8b rows (the carriers incl. togekiss_meowth with Togepi A4 078 and t-lucario pairings; the Will rows; 8b cloud and new2) | 27,290 | recorded | **1 game differs** (km3 carriers, pairing 11); the rest same |
| **17 new cells: k3, kp3, kog3, km3, kta3 dev, kta3 fresh (8,500 each)** | 51,000 | recorded | **37 games differ, all in pairing 21** |

**Rows the old pin never recorded, played tonight by both the old pinned program and the candidate:**

| Run | Games each | New v old |
|---|---|---|
| step 7c km3 floor rows (pairs_7c, 32 pairings x 60; 4 v t-lucario) | 1,920 | same |
| step 7c2 km3 floor rows (pairs_7c2, 24 x 60; 3 v t-lucario) | 1,440 | same |
| c-dragonair_mega_rayquaza_ex (Skull Fossil, #401's reach) v the 8 research decks, on the kt clause-(d) deals (`kta_tables_2026-09-29/pairs/dev_d_rayquaza.tsv`, equal to `kt_tables_2026-09-28/d_rayquaza.tsv`; seed base 22,700,000,000, 500 a pairing), one bot on both seats: km3, kta3, k3 (4,000 each) | 12,000 | **km3 629, kta3 621, k3 10 games differ** |

## Every changed game, sorted
**The changed games:**
- **In the old pin's recorded tables: 38.** That is 37 in the 17 new cells (all pairing 21) and 1 in step 8's km3 carrier rows (pairing 11).
- **In the Rayquaza rows** (old v new, both played tonight): **1,260**, all from #401.

The new17 changes:

| Bot | Changed games (pairing 21, deals) |
|---|---|
| k3 | 8 (102, 157, 219, 224, 265, 330, 345, 465) |
| kp3, kog3, km3, kta3 dev | 7 each (102, 157, 206, 219, 265, 345, 465) |
| kta3 fresh (other deals) | 1 (329) |

- **The cell:** g-mega_altaria_greninja v t-hydreigon, new17 pairing 21.
- **The winner flips in 1 game** (k3, deal 102). The others change other fields: moves and decisions always, and sometimes points, turns, abilities or hyper_ray.
- **Pairing 22,** the same deck against t-weezing, changed in none.
- **The plan predicted this cell.** PLAN.md listed it under "Possible: new17 pairings 21 and 22 ... for k3, kp3 and km3". kog3 and kta3 weren't named because their runs were in the optional set.

**The mechanism** (by reading the cards):
- g-mega_altaria_greninja holds Bonsly B3 078. Its Teary Attack reads "During your opponent's next turn, attacks used by the Defending Pokémon do -30 damage."
- It also holds Oricorio B4 078, a Psychic Pokémon weak to Darkness. t-hydreigon's Deino (Headbutt 20) and Bombirdier (Dark Cutter 30) attack into it.
- Under the old pin such an attack did 0 + 20 Weakness. Under the Growl rule it does 0. This is exactly the case 501fc1dd changes.

**The step 8 carrier change:**
- km3, pairing 11 (carriers/alternates/togekiss_meowth.txt v t-lucario), deal 484.
- Points and turns differ; the winner is the same.
- Both decks hold a cut card: Togepi A4 078 and Bonsly B3 078.
- On U (no Growl) that pairing equals the old pin (500 of 500).

**Sorted:**
- **(a) expected from a named rule fix: 38.** All 37 new17 changes and the step 8 carrier change.
  - **Method change, stated:** PLAN's own test for (a) was "the first difference has a cut card in play". It could not be applied: the game records hold only hashes of the moves, so there is no first difference to read without a trace. The cause was settled two other ways.
  - **Deck reach** (`games/classify.tsv`): of the candidate's changes, only the Growl rule's cards are in either deck of pairing 21 or of the carrier pairing 11. The verifiers' independent scans found no card that #385, #390, #401 or #344 acts on in those decks; the scans are not in the package. They covered the 58 deck files the replayed runs used, step 8 included. Among project lists, Fossils appear only in the Rayquaza list (below). The engine's own example deck `engine/example_decks/donphan.txt` holds Old Amber.
  - **The build without the Growl commit.** U is the candidate with only 501fc1dd reverted (local ref refs/pocketdecksim/engine-candidate-2026-10-20-U, 239b70a0; legality_scan a1493ce8). On U, pairings 21-22 were replayed for k3, kp3 and km3 (04:25Z, 3,000 games), then pairing 21 for all six changed runs (08:22Z, 3,000 games), then step 8's carrier pairing 11 for km3 (10:30Z, 500 games), all with the recorded commands. All 6,500 equal the old pin's games on every field, and U differs from the candidate on exactly the 38 changed deals.
  - **What U shows:** the Growl commit is necessary for these changes, given the other four. A build of the old pin plus Growl alone wasn't run. An interaction is ruled out by reading the code: none of the four upstream paths can fire for these decks (no Fossil, no random multi-hit, no on-play Bench Ability, legal Energy).
  - U doesn't show whether the rule fired in the game as played or only inside the bots' look-ahead.
- **(b) from an upstream change: 1,260,** every Rayquaza change (km3 629, kta3 621, k3 10). **#401 causes them, but PLAN did NOT predict them** (it said no list holds a Fossil).
  - **Proof.** V is the candidate with only 42d2dd8e (#401) reverted: local ref refs/pocketdecksim/engine-candidate-2026-10-20-V, 2e75429f; legality_scan 046460ab. V equals the old pin on all 4,000 Rayquaza games for each bot. U (no Growl) equals the candidate on pairing 3, the one Rayquaza pairing a cut card reaches (research/lucario holds Bonsly). V equals the old pin there too.
  - This sort used V, the #401 counterpart of U. U was run only on pairing 3.
  - **What changed in play.** #401 removes a duplicate DiscardFossil from the actions the bots search, so their choices and random paths differ from that point on.
  - **Winner flips:** 157 for km3 and 148 for kta3 (of 4,000 each), 3 for k3.
  - **The Rayquaza deck's average score barely moves** (paired, same deals):
    - km3: 0.2915 to 0.2938 (+0.0022, se 0.0031);
    - kta3: 0.2928 to 0.2938 (+0.0010, se 0.0030);
    - k3: 0.2990 to 0.2988 (-0.0003, se 0.0004).
  - So the play paths change, but the deck's result level doesn't.
  - **What was not measured.** Tonight's rows play the kt clause-(d) deals with one bot on both seats. The RECORDED clause-(d) tables were not replayed: kog3; kta3 v kog3; kt3 v kog3; and kta fresh kog3 and kta3 v kog3. All of them were recorded on engine ec7e1a8, not the old pin, and their change is not measured. km3 and k3 have no clause-(d) table.
- **(c) unexplained: 0.**

## What PLAN got wrong (found by the verification, checked with extra runs)
1. **Fossils.** PLAN said "None: no Fossil in any list" for #401. In fact `rl/results/kt_carrier_census_2026-09-26/decks/c-dragonair_mega_rayquaza_ex.txt` holds Skull Fossil, and the kt/kta d_rayquaza tables use it. Switch 2's PLAN had already named it. Played old v new tonight, 1,260 of 12,000 games differ, all caused by #401: group (b), not predicted.
2. **Togepi.** PLAN said Togepi A4 078 is only in a pause-game list. It is also in the carrier list `carriers/alternates/togekiss_meowth.txt`, used by step 8's carrier pairings 8-15. Those rows were replayed tonight: 1 km3 game differs (pairing 11, against t-lucario), and U shows it's the Growl rule, group (a).
3. **Small overstatements:** "decks 14 and 10" meet t-lucario: every floor page does. Koraidon ex has no on-bench Ability arm in this fork, so #385's guard reaches Miraidon ex, Roaring Moon and Poltchageist.

## Open points for the reviewer
- **The Growl rule's "+X" choice: recorded Oct 20 (this note added that evening).** When the attacker's side cuts an attack to 0, a defender-side "+X damage" is skipped too, as the candidate does. Shot List row `cut-to-zero-plus-x`, `Battle Logs/Recording_QA/LUXRAY_ESPATHRA_RETRY_2026-10-20/`, clip02 `ScreenRecording_10-20-2026 17-54-38_1.mp4`; Codex review, independent PASS, lead acceptance: Luxray (Intimidating Fang) carrying Espathra's Lumina Crash (+50 from attacks) took 0 from Flittle's Flop (20): preview 0 at 04:01.5, damage 0 at 04:09.5, Luxray still 100 at 04:10.5. The control: Slurpuff's Draining Kiss (50) did 80 to the same marked Luxray at 05:13.5 (50 − 20 + 50). Limits (Codex): these cards and conditions only; both tests changed the attacker before the hit (a retreat; a Knock Out and promotion); Peculiar Plaza was in play (it changes retreat only). Tests pin both cases (`hooks/core.rs`, in the final candidate).
- **#385:** a rules repair. Adoption needs Dustin's yes on it as a rule. Its tests cover Miraidon ex and Roaring Moon, including the Team Rocket's Boss case. Poltchageist's newly gated heal offer has no test (added Oct 20 evening: 6726f83f).
- **#390's unit tests** compare sorted outcomes, so they don't assert the fixed order, and one test has a 1-second time limit. The determinism claim rests on the BTreeMap in the code.
- **#344:** two tracked deck files without an "Energy:" line now derive Colorless or Dragon Energy and become invalid: `rl/results/limitless_skill_model_2026-09-25/decklists/garchomp.txt` and `raticate_ninetales.txt` (research artifacts). Also, the CLI preflight's message for the new rejection is the generic "failed full-deck validation".
- **#401 changes how Fossil decks play.** On the kt clause-(d) deals, #401 changes 15.7% of km3's games, 15.5% of kta3's and 0.25% of k3's, with no measurable change in the deck's score. The recorded clause-(d) tables (kog3, kta3 v kog3, kt3 v kog3; kta fresh) would very likely change too, but that wasn't measured. They were recorded on ec7e1a8, so they would need new references after an adoption, and that is Dustin's decision too. #401 is a plain bug fix (the Fossil discard was offered twice). Keeping the old behaviour would mean leaving it out of the pin.
- **Re-baselining.** Adopting means pairing 21's references change for k3, kp3, kog3, km3 and kta3 (dev and fresh). Step 8's carrier reference changes in one km3 game.
  - Those cells are inside scoreboard v3's frozen 45 cells for k3 and kp3. Scoreboard v3's development real-error readings use them (RUN5).
  - The closer precedent is switch 2's PLAN question 3a: rule-driven new references accepted, as for B2e. Its section 3 lists what follows: every pilot's baselines are re-registered, and kta3's status and km3's thresholds go back to Dustin. That is Dustin's decision.
- **The kx3 digest** is unchanged on the candidate, but kx3 itself is not on the official tree. A re-pin of the slow-report program follows an adoption.

## Not checked here
- **The watch rows:** the step 7b watch tables, and the 7c, 7c2, 8 and 9 watch rows. They were played by the watch build (counters for round 2), which has no counterpart for these changes. 7c and 7c2 were played old v new instead.
- **The floor re-check pages** in `rl/results/floor_recheck_rules2_2026-10/`: deck 12, the draft D pages (incl. D victini-passive), brews 07 and 09, 07-skarmory, brew-05b, brews 06 and 06b, the control pages, and the Part A re-check. Each was made on `rl/engine-2026-10-12/deckgym` and has a t-lucario row, which the Growl rule can reach.
  - The ladder predictions in `rl/results/ladder_validation/predictions/` are built from those pages. Their make_predictions.py requires the old engine key, so they too follow an adoption.
- **The kx3 replays** in `rl/results/kx3_on_rules2_2026-10/`: kx3's pool holds t-lucario and research/lucario. Only the kx3 self-check digest was run.
- **The recorded kt/kta clause-(d) tables** (see (b) above).
- **The AI judge's lister and baseline:** they stay on 70652fff by design (frozen-4).
- **The slow-report program** (`slow_report_pin.json`): re-pinned only at adoption.
- **Old-side game-level re-runs:**
  - kd3's 1,120 games;
  - U's 6,500 games equal to the old pin (plus 1,500 Rayquaza pairing-3 games equal to the candidate);
  - V's 12,000 games equal to the old pin;
  - tonight's 7c, 7c2 and Rayquaza old-pin plays (15,360).
- **Everything else relies on the recorded references,** whose programs (by sha) and inputs (by hash) were checked.

## Time used
All of it was laptop time at night, inside Dustin's 02:00-13:00Z window, Oct 20, from 02:09Z to 10:59Z (8 h 50 min of wall time). Nothing had to be frozen at the 12:55Z stop.
- builds: candidate 527 s; km3 strength 4.5 min and kx3 strength 7 min (8 jobs, see above); U 453 s;
- suites: 785 s and 318 s;
- self-checks: km3 about 6 s each; kx3 5,141 s;
- replays (`games/summary.tsv`; several overlapped the kx3 self-check):
  - main pass: candidate 35 runs, 236,220 games, 20,226 s of run time; old pin 8 runs, 6,160 games, 452 s;
  - U, main pass: 6,000 games, about 9 min;
  - the extra runs after the verification (08:49-10:59Z):
    - step 8 and 8b: 27,290 games;
    - 7c and 7c2, old and new: 6,720;
    - Rayquaza, old and new: 24,000;
    - U on pairing 11 and the Rayquaza pairing 3: 2,000;
    - V: a 270 s build and 12,000 games.

The meter: one Claude session plus subagents. Read-only: the scoping readers and two verification rounds. The test porter wrote the test files, which I compiled and committed. No API credits.

## Files here
- `PLAN.md`: the list, written first.
- `RESULT.md`: this file.
- `programs/`: the tested programs, SHA256SUMS, the strength build records and `other_programs.sha256` (strength, kx3 strength, U's and V's legality_scan, their refs and engine trees).
- `tests_and_builds.txt` and `selfchecks.txt`.
- `driver.log` and `window_keeper.log`: the night's log and the keeper's freeze and thaw record.
- `games/`:
  - `summary.tsv`: one line per replay; side old, new or oldnew;
  - `classify.tsv`: deck reach of the changed deals;
  - `u/`: U's comparisons (`verify.tsv`, `.cmp`) and game files;
  - `v/`: V's Rayquaza game files and comparisons, U's Rayquaza pairing-3 files, and `dray_pairings.txt`;
  - `new/`, `old/`, `oldnew/`: each run's `.cmd` (the exact command), its `.cmp` (the checker's output; the CLI and goldfish runs have none) and `*.diff.tsv` (every differing deal with its fields);
  - in `new/`, the candidate's game files for the seven changed runs: the six new17 runs and step 8's km3 carrier run, the would-be new references;
  - `oldnew/`: both sides' game files for the 7c, 7c2 and Rayquaza rows;
  - `outputs.sha256`: the hash of every game output tonight, including about 66 MB of files not in the package (they stay in the laptop's `pincand_work/games`).
- `tools/`: as run:
  - replay.py, oldnew.py, classify.py, u_verify.py, the drivers and the night keeper;
  - after_more.sh (the U run on carrier pairing 11) and vfix.sh (V's comparisons, re-run with the right expected count after driver_v.sh's first check passed --expect 4000 instead of 3,500);
  - bpatch.py, the byte-exact patch tool that made the code commits (it keeps each file's CRLF or LF endings).
  - classify.py's card triggers are narrower than the engine's: it misses 7 random-target printings, Old Amber, and decks without an Energy line. The independent scan above didn't rely on it. Fix it before reuse.
