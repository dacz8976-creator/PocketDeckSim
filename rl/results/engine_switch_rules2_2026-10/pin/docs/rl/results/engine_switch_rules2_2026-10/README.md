# Rules switch 2 (Oct 2026): what it is, how it ran, and the pin

The plan is `PLAN.md` here, and the one-page package Dustin answered is `RELEASE_PACKAGE.md`. This file is the switch's summary. Each step's record is in `STATUS.txt` and `PIN_STATUS.txt`, and step 8c's is in `8c/`.

## What the switch is

The official engine before it was main-8626a35 (`../../engine-2026-10-02/`). The switch adds P, the final engine commit of `claude/coin-prevention-round2`, taken by commit and not by branch head: c7a25df49e0b4acdc61f8b78f2cab599d86f5c76, engine tree 70652fff (`switch2.env`). It makes the engine follow the plain card text (Dustin's Oct 1 rule) in three parts, plus one text fix:
- **Round 2's coin-prevention rules and the card-text fixes.**
  - Wild Swing and six other sites (Wellspring Dance, Tornado Shot, Double Splash and Triple Bombardment, Mischievous Ring, Litter, and Mega Kangaskhan ex's second punch) now flip Meowth's, Togekiss's, Bastiodon's and Hisuian Goodra's coin when their damage lands. Any other attack's queued plain hit flips it too.
  - The coin Abilities and Guts also answer an attack's damage to its own side's Pokémon, and Perish Body flips for an attack's plain queued hit.
  - Will works for a Confused attacker (on the attack's own first coin, after the Confusion coin) and on a block coin ("If tails, that attack doesn't happen"). Victory Star is offered after a block coin's heads and with Will pending.
  - Each Ariados adds 1 to the Retreat Cost, so two add 2.
  - Luxury Coin isn't offered on the opponent's Stadium, and a Fossil can't be played under an Item lock.
- **Fossils are Item cards** at the seven other places that read "Item card" (P3, question 2a).
- **Return damage left by an attack takes Weakness** (P2): the hit back from Cursed Jewel, Spike Armor, Bristling Spikes, Needle Lariat and Shell Trap gets +20 on a weak attacker, or is doubled under Bounded Field unless the holder is a Mega Evolution Pokémon ex. A Tool's or an Ability's return damage stays flat.
- **P1:** Gholdengo's caveat text (no game changes).
- **For the checks:** one revert switch per rule (13 `DECKGYM_*` variables, none set by default), for 8c's revert check. F1 keeps the promotion ahead of a copied second punch whose attacker has left the Active Spot.
- 26 engine files change, 17 source and 9 test files (`allowed_engine_files.tsv`). `engine/src/players/`, `Cargo.lock` and `Cargo.toml` are unchanged. The suite at P: 2,103 passed, 0 failed (fc6307c0).
- Card by card, with the commits: `PLAN.md` sections 0 and 2; `../../../rules/09_engine_repairs_2026-09-22.md`, "Fixed Oct 12".

## Dustin's decisions (Oct 9)

His answers to the release package, verbatim (`PLAN.md`, the Oct 9 status):
- **"1-3 sure."** So, as recommended:
  1. go, "update if everything passes", with the two stricter checks: a game one move longer or shorter is judged like any other, and the revert check is required;
  2. the scope: the three parts plus P1, leaving out the bots' price of a Will-boosted block coin and their Junk Spark count of Fossils;
  3. the new reference games: km3's B2e reference for the 16 two-Ariados rows, and new floor pages after the pin.
- **"Alright it is fine to use the laptop over the weekend"** (question 4).
- A hit back counts as attack damage for the attacker's Heavy Helmet (his recording 20261009_223237000, Oct 9). That stays outside this switch, since he approved the scope without it (`rules/09`, open).

## Sitting 1 (steps 4-7c): passed

Oct 11, 07:17-10:38 UTC; record 7f7581ca (SITTING 1 DONE); 199,400 games.
- **Step 4:** the candidate 08a9b3ae607c904e7df9f6e999d3f830eccc930f, main c4f27f2 plus P c7a25df, kept at `refs/pocketdecksim/rules-switch2-candidate` (not a branch). Its `engine/` is P's tree byte for byte, and exactly the 26 allowed files change.
- **Step 5:** one fresh build from one archive, `cargo build --release --locked`: deckgym 0a9199bc…, legality_scan bf9d7502…, goldfish d8cfb779… (`programs.sha256`).
- **Step 6:** the watch build's legality_scan, 60797708…, with the round-2 counters (evidence only).
- **Step 7:** 151,240 identity games equal to their references on every field: kta3 on its fresh and development deals, km3, k3 and kp3 on scoreboard v3's 45 cells, kog3, kq3, kpr3, and kd3 as a gate.
- **Step 7b:** 28,000 watch games on the table, equal to the plain ones. Every round-2 exact counter read 0, and the three required off-gate counters fired.
- **Step 7c:** Dustin's 7 floor pages (decks 02, 06, 08, 14 and 10, and draft D's root and amended pages) replayed through `floor.py`, every game equal. That includes deck 10's t-weezing row, which could have changed (0 of 240 games differ). Oct 1's 32 watch rows and the 23 new rows named equal were identical, and deck 10 v t-weezing's watch row changed 0 of 60 deals.

## Sitting 2 (steps 8b-10): passed

Oct 11, 10:38-13:14 UTC; record a9890744 (SITTING 2 DONE); 137,090 games.
- **Step 8b**, the early-warning rows, 2,800 games: 89 of 1,040 deals changed. The rows the cloud also played equal the cloud's at P.
- **The trace-load gate:** 0, from the cloud's 8b rows (`trace_load.txt`).
- **Step 8**, the carriers and the Will rows, 54,750 games: 0 of 26,250 deals changed.
- **Step 9**, km3's coverage, 74,500 games: the 58,500 games of the 80 B2e pairings without Ariados, Scizor and the second lists equal `../km_tables_2026-09-30/`'s references. In the 16 two-Ariados pairings, 1,044 of 8,000 deals changed.
- **Step 10:** `deckgym simulate`, goldfish `--coverage` and `run_screen` under km3 equal to their recorded files.

## Step 8c: every changed game accounted for

`8c_RESULT.txt` (result 18e8020e; the record and its tools in `8c/README.md`). The laptop session ran it on Oct 11, 15:03-15:53 UTC, with the tools pinned in `tools_8c.tsv`, and the coordinator audited it the same day (`8c/README.md`, its last section).

| Changed games (steps 8b and 9; steps 7c and 8 had none) | 1,133 |
|---|---:|
| On the board: an exact counter at the first differing move | 511 |
| In look-ahead: both halves, and the revert check gave back the old choice and scores (621 of 621) | 621 |
| Unexplained | 0 |
| Judgment call | 1 |

- The 111 CONDITION 3 games (only an off-gate counter fired) and the one game with no counter at all were each traced. No game had only round 1's or a superset's counters.
- In the 8b rows the cloud also played, the 25 changed games got the same verdicts as in the cloud's own classification.

## The judgment call, and Dustin's word

Step 9, km3, pairing 34 (Whimsicott, a B2e held-out list, v Sceptile), deal 449. On turn 8, from the same position, the old engine's bot plays its Stadium and the new one's plays Professor's Research; the winner and the points are the same. The probe found nothing inside the bot's search, but a hand trace found the cause. In the bot's planning line, Professor's Research draws the deck's second Ariados, which evolves the Benched Spinarak; with Trap Territory counted twice, Grass Knot then Knocks Out the opponent's Active. Turning off only the Trap Territory rule brings back the old choice and every score; turning off any other rule doesn't (`8c/README.md`, `8c/hand_9_34_449/`, `8c_DECISION.md`).

**Dustin's word** (Oct 11, about 16:20 UTC, in the laptop session; verbatim, `8c_DECISION.md` at 980ca8c8): "Yes the hand trace is good"

## The pin (Oct 12)

- **Merge:** P into main as @@MERGE@@ (main-@@MERGE_SHORT@@), a merge commit with parents main and P, made off-tree. Main's `engine/` hadn't changed since the candidate's main c4f27f2, so the merge's `engine/` is P's tree 70652fff, the built candidate's byte for byte (checked by the pin). The merge also brings P's records under `rl/results/`, among them the cloud's files in `../coin_prevention_round2_2026-10-01/` and `../round2_readiness_2026-10-02/`.
- **Programs:** sitting 1's builds, copied to `rl/engine-2026-10-12/` with `SHA256SUMS` and never rebuilt (`programs.sha256`). In the manifest, main-8626a35 moved to the history as superseded. The screen's and the floor's pilot stays km3.
- **Scoreboard v3 re-verified at the new engine, 45 cells.** k3 and kp3 replayed identical on all 45 cells (step 7), so scoreboard v3's files stay this engine's frozen k3 and kp3 tables, with the same hashes.
- **km3's new B2e reference** for pairings 32-39 (h-whimsicott) and 80-87 (deck 12) is step 9's replay, `08a9b3a_cov_b2e_km3.jsonl` here (question 3a; noted in `../km_tables_2026-09-30/READING.md`). The other 80 pairings, Scizor and the second lists keep their references, which step 9 found equal.
- **The documents:** START_HERE, CLAUDE.md, RUN5, `rules/09`, `rules/04`, `rules/02`, the Oct 1 recordings' READOUT and km's reading (`pin/docs/CHANGES.md`).

## After the pin

1. In GitHub Desktop, Fetch origin; if it then offers Pull origin, stop and ask the laptop session first; otherwise Push origin (`pin/README.md`). Tell Sonnet and the cloud sessions the new engine's name (main-@@MERGE_SHORT@@, `rl/engine-2026-10-12/`). km3 stays the working pilot, and no `DECKGYM_*` variable is ever set in a recorded run.
2. Step 15, as `../floor_recheck_rules2_2026-10/PLAN.md` says: the floor's pre-use re-check under km3, then the new pages for deck 12, brews 07 and 09 and draft D. Each new page goes to Dustin beside its old one, and a new failure or judgment call stops and goes to him. Deck 10 needs no new page (step 7c).
3. Then kx3 is rebuilt on the new engine and checked, and the slow report's program is rebuilt, its self-checks replayed, and pinned again (`RELEASE_PACKAGE.md`).

## Left out (for a later round; each needs the full procedure)

- **A hit back as attack damage** for the attacker's own cards: Heavy Helmet (seen), and by their wording Disguise, Guts, Rescue Scarf, Lucky Egg and Rocky Helmet (`rules/09`, the open entry).
- **The bots' pricing**, since `engine/src/players/` is unchanged: a block coin stays 50/50 to them even when Will makes it heads (`value_functions.rs`:1976 and 2011), and their Junk Spark estimate still leaves Fossils out. No list reaches either (`PLAN.md` question 2c; `RELEASE_PACKAGE.md` question 2).
- **Which of the Confusion coin and a block coin comes first:** no card text decides it, and nothing visible depends on it (`rules/04` §9; question 2b).
- **B4b's reprints:** Victini's caveat arm in `card_validation.rs` is still keyed by card id (B3 025, P-B 049), as on Oct 1 (`../engine_switch_rules_2026-10/README.md`, "Next switch backlog").

## Who did what

| Part | Who |
|---|---|
| The package P (round 2, the card-text job and its follow-up, P1, P2, P3, F1, the revert switches), the suite at P, the counters, coin_probe v2, the classifier's fixes, and 8b's early-warning rows | the cloud, on `claude/coin-prevention-round2` |
| The package's second read (Oct 2), equivalence reader two, and 8c's revert-check driver (`tools_8c/revert_8c.py`) | Sonnet |
| Equivalence reader one | the laptop session's Opus subagent |
| The plan, the runners, the builds, sittings 1 and 2, 8c's run, the pin and step 15 | the laptop session |
| Routing, audit and operational decisions | the Fable coordinator session |
| The go, the scope, the reference games, the laptop's nights and the judgment call | Dustin |
