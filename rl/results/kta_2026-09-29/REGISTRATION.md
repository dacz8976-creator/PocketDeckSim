# DRAFT (Sept 29; harmonised with RUN5 and with km's draft, Sept 29; second fix pass, Sept 29; third pass, Sept 29 (review changes)): `kta`, kt's switch 1 alone on kog, registered afresh on fresh deals

**Decision this informs:** whether kog3, the working pilot, is replaced by kta3. kta3 is kog3 plus kt's switch 1 only: the defender's temporary damage cuts and reduction Tools priced in the threat clock. It is read on the 45 cells, by the route the footprint fixes, with clause (d) on Dragonair Mega Rayquaza ex.

**In one line (third pass, Sept 29):** written under the Sept 29 attribution case, where the one pilot lever sits in Rayquaza's nine cells (kta's clause (d) is on Rayquaza, inside it; km's is on Lucario, outside it), and kta's verdict is expected to rest on the fallback, which is why the Jasmine threshold must be right. The review's words for the footprint thresholds: "they're doing the work the accuracy clause can't".

**Written under the attribution of Sept 29, in detail** (`rl/results/error_attribution_2026-09-29/README.md`, with its Check): kta's clause (d) sits on Rayquaza, the archetype whose nine scoreboard cells hold the one pilot lever the attribution found (about a third of kog3's real miss, 22% to 53%, reached by three tested designs), but kta3 moved that group only from τ̂ 20.6 to 19.9 on development deals (real error 14.05 to 13.84 on all 45), so it is not expected to move the 45-cell accuracy much, and its verdict is expected to rest on the fallback: no harm, the coverage decks, (d) and the Jasmine threshold. (Its development ΔMSE interval, −11.0 to −1.4, did not span zero. If the fresh one is also wholly below zero, accuracy passes outright and Jasmine is reported instead; no harm, coverage and (d) gate either way. Section 5.2, "How this route sits inside RUN5's three outcomes".)

**Status: a draft, not a registration. No code, no game.** Nothing here is registered until this text is committed as the registration, with Dustin's word on it (kt's registration says the same of itself). Once committed, any change to it is a dated amendment made before any fresh game (kt's rule for itself). After that come the build and its identity (the build exists: ec7e1a8, reused as-is, section 4), then the tables. Choices the drafter made that no rule or ruling fixed are marked **[proposed]**. The overnight delegation to Fable (Sept 28-29) does not cover his registration gate. The text was harmonised with RUN5 and with km's draft on Sept 29; every change is listed at the end ("Harmonised with RUN5 (Sept 29)"). A second fix pass the same day applied an independent checker's points; its changes are listed in section 13 ("Second fix pass, Sept 29"). A third pass the same day applied the changes from a review Dustin forwarded; they await his word like the rest of the text, and every change is listed in section 14 ("Third pass, Sept 29 (review changes)"), which governs where an older note says otherwise.

**Needs Dustin's word (the one list; the reasons are in section 10):**
1. **This text as kta's registration:** the gate (section 6), the development-data declaration (3.1), the fresh seed blocks (3.2).
2. **The Jasmine threshold:** at least 20% of offered turns on deck 07, gating only when the ΔMSE interval spans zero (5.5; 10, b). With it, **the guard** (third pass, worded as km's): if kog3's own Jasmine rate on the same fresh deals already reaches 20%, the footprint test counts as not passed in the fallback.
3. **Clause (d)'s size: 2,000 deals per row** on the census Rayquaza list's 8 rows, both arms, all on fresh seeds in kta's own block (third pass, Sept 29; the same size, reason and convention as km's D2), read once. RUN5 records his Sept 29 decision as kta "with the same clause (d) gate as before", and the earlier test was 500 per row; this text keeps the same deck, list, rows and statistic, and the size change is his to confirm (5.2 (d); 10, a).
4. **The other marked choices:** mixed rows only where games differ (10, c; km's draft now does the same, so the two drafts agree); the Vespiquen trace (e); the wiring gap (f); the drafter's reading of the three outcomes on the reserve route, with the near-zero rule at both ΔMSE edges (g); the smaller [proposed] items (i).
5. **The build and its identity:** ec7e1a8's kta3 reused as-is, with section 4's checks and no cloud round.
6. **The tables:** the start of any game, and its place in the laptop's queue (10, h).

**Seeds:** all fresh, in one reserved block, **23,000,000,000 - 23,009,999,999** (sub-blocks in 3.2). Nothing else uses it. START_HERE's seed table ends at 22,801,319,999. The only larger game-seed block in the tree or on the branches (checked Sept 29) is km's proposed clause (d) block, 22,900,000,000 - 22,900,081,499, in its draft (`trainer_pricing_2026-09-28/REGISTRATION_DRAFT.md`). This block doesn't touch it. The one other large number, 26,092,500,001 (`docs/REVIEW_2026-09-24_direction.md`, the Limitless split's random seed), isn't a game block.

**Sources.** kt's registration, amendment 2 over the original text (`git show origin/claude/pensive-ptolemy-spwc0b:rl/results/kt_2026-09-26/README.md`; amendment 3 is withdrawn). That file is pinned here at commit b878047 (blob 1512325), the last commit touching it on that branch. Main's copy of the same path (blob cac0e86) is an older text ("RE-ISSUED ON KOG", 966d75d, Sept 28 02:47 UTC), not the amendment 2 the reading was coded from (`kt_tables_2026-09-28/README.md`), and is not the source. The reading: `rl/results/kt_tables_2026-09-28/` (`READING.md`, `READING_numbers.txt`, `ec7e1a8_ab_table.txt`, `footprint.txt`, `STATUS.txt`). The rules: `rl/RUN5.md`, "The frame a candidate is read in" and "Where things stand" (kt bullet). The build note: `rl/results/kt_2026-09-26/BUILD.md` on the cloud branch (commit a412873; main's copy is older and has no ec7e1a8 section), section "The build on kog (ec7e1a8, Sept 28)". The cloud's cross-check: `rl/results/kt_kog_2026-09-28/` on the cloud branch (commit 816fd9c; not on main). The seed table: `START_HERE.md`.

---

## 1. In plain words

**What kta is.** kta3 = kog3 with kt's **switch 1** and nothing else. Switch 1 puts the defender's temporary damage cuts, and the reduction Tools that act as cuts, into the threat clock, for both sides. The cards it reads:
- Jasmine: "During your opponent's next turn, all of your Steelix and Skarmory ex take -50 damage from attacks from your opponent's Pokémon." (`card.py`)
- Metal Core Barrier, Steel Apron, Heavy Helmet;
- Cheren and Blue;
- self-cutting attacks: Gouging Fire's Scorching Interruption (-30 next turn) and Frigibax's Stiffen (-20 next turn).

Switches 2 and 3 are off. The flat +10 for a Tool on the Active stays. Only `kta3` is registered.

**Why it exists** (Dustin, Sept 29 morning, recorded in `RUN5.md`, kt bullet): **"kta alone, kog stays."** And: **"The +8.5 on your Skarmory deck is real simulator evidence and it should be in the registration as the reason the candidate exists; it isn't the gate."** RUN5 also records, without quotation marks, that kta is registered as switch 1 alone on kog with the same clause (d) gate as before (Rayquaza per the registration, Skarmory as the motivating deck, Suicune reported). The evidence, all from the kt reading, all development data:
- **The Skarmory A/B.** Dustin's deck 07 (`decks/dustin/07-skarmory-stall.txt`: 2 Skarmory ex, 2 Jasmine, 2 Metal Core Barrier, 1 Steel Apron) against the eight panel lists, 1,920 games per arm, paired by deal, kog3 on the panel in both arms:
  - kog3 47.4%, kta3 55.9%: **+8.5 points, 95% interval +6.7 to +10.4**.
  - Jasmine played on **0.4%** of the turns she was offered under kog3 (36 of 8,597) and **30.2%** under kta3 (1,711 of 5,669).
  - The other four decks: 05 +1.8 (+0.9 to +2.6); 03 +0.7 (-0.7 to +2.1); 11 +0.1; 01 -0.2 (-1.2 to +0.8). All five together +2.2 (+1.6 to +2.7).
- **The footprint.** On the 45 cells kta3 changes 559 of 22,500 games (**2.48%**), all in the 17 cells whose lists carry a switch-1 card. The 45-cell table barely sees it because, of its ten lists, only two carry such cards: Suicune's (Stiffen) and Rayquaza's (Gouging Fire). Deck 07 carries several switch-1 cards (Jasmine, Metal Core Barrier, Steel Apron), and 83.5% of its A/B games differ.
- **The reserve route, read once, passed every clause on the development deals:**
  - τ̂ margin +0.21 (90% interval +0.06 to +0.31), real error 14.0 to 13.8, no veto counted;
  - no deck's own side worse beyond noise;
  - Rayquaza's clause (d): **+1.00 ± 0.39**, 52 games better and 12 worse;
  - no coverage harm, though most coverage rows barely changed. Mixed-row games (kta3 on the held deck only) that differ from kog3's: B2e 28 of 48,000, Scizor 980 of 4,000. With kta3 on both sides: B2e 325 of 48,000 (all in the 12 pairings of section 2), Scizor 1,225 of 4,000.
- **Why it can't be adopted from that reading.** kt's registration fixed the outcome before any game: "kt3 fails: nothing adopted ... the next candidate is registered afresh." kt3 failed the ordinary rule, so kta3's pass adopted nothing. Dustin's word is that this registration is that fresh one. It doesn't reopen kt's "not adopted": kt3, ktb3 and ktc3 are not run again.

**What this registration adds to kt's:**
- fresh simulator deals for everything a verdict rests on (section 3);
- Dustin's Sept 29 rules: the three-outcome accuracy reading, the detectable size printed, the held-out direction, and two columns (which condition carried the verdict; (d) per cell beside the pooled number);
- kta3 alone, with kog3 as the only comparator;
- a fresh replication of the Skarmory A/B, reported. Only its Jasmine rate can gate, and only in the fallback (5.5, 5.6).

**What it does not change:** switch 1's spec, the reserve route's clauses, clause (d)'s deck, list and statistic, the coverage tests, and clause (d) as one test with no second chance (kt amendment 1: "so there are not two chances to pass").

**Read once.** Everything is read once, with no doubling, rerun or second block (km's draft says the same; kt's text said it only for (d)). RUN5's "doubling deals to 2,000 when undecided" doesn't apply here: it sits in "Variants and process" beside the τ̂ margin E = 3 comparison between variants, and it is not part of the reserve route, the three-outcome accuracy rule or clause (d). Clause (d)'s size is fixed before play: 2,000 deals per row, written now (third pass), not a doubling after an undecided result (5.2 (d)).

---

## 2. The candidate

- `kta<N>` = `kog<N>` with switch 1 only (`EvalFeatures::KTA` at ec7e1a8, on `EvalFeatures::KOG`). kog = kp + koa's opening switch A + kpg's discard credit F. Switches 2 and 3, R, kph's A and B, kq's and kd's features are off.
- **The spec is kt's registration's SWITCH 1 section, unchanged.** In short: `temporary_defender_reduction(state, victim, threat, turn)` sums the turn effects and card effects that cut damage on the turn the clock puts the threat's first hit, plus Metal Core Barrier's cut when that turn is the holder's opponent's next turn. Permanent cuts (Steel Apron, Heavy Helmet) come from `persistent_defender_damage`. The first hit is `max(0, damage - temporary - permanent)`, later hits `max(0, damage - permanent)`. Timing is the clock's own. The clock counts whole turns, so a cut that doesn't change the number of hits is worth 0. Where the victim is Weak the clock under-counts the cut.
- **A spec change after any reading is a new code.**
- **Where switch 1 reaches on the 45 cells** (read from the lists, kt amendment 2 item 3): 17 of 45. Suicune's list carries one Frigibax P-B 037 (Stiffen): its 7 table cells and 2 new cells. The scoreboard's Rayquaza list carries 2 Gouging Fire B3a 054: its 9 cells. Rayquaza v Suicune is in both, so 9 + 9 - 1 = 17. It matched the measured 17 cells with a changed game. No other panel list, and not Mega Altaria ex Greninja's, carries a switch-1 card.
- **Coverage reach:** Scizor's list carries 2 Metal Core Barrier B2 148 (its 8 rows). Through the panel's Suicune, switch 1 also reaches B2e pairings 4, 12, 20, 28, 36, 44 (held-out) and 52 to 92 in steps of 8 (Dustin's), and the second lists' rows against Suicune (v-lucario_2's row 19, v-weezing_2's row 26, l-charizardy's row 44). No B2e list or second list carries a switch-1 card of its own.
- **Predictions never choose the route.** The measured footprint does (section 5.1).

---

## 3. Development data, and what "fresh" means

### 3.1 Declared development data for kta (RUN5, "Development data, stated with each reading")

Everything read Sept 28-29 for kt is development data for kta. Nothing in it is pooled with a fresh file, and none of it is evidence for the verdict:
- the four 45-cell tables (kt3, kta3, ktb3, ktc3) at their deals (72,000,000 + pairing × 10,000 + i for the 28; 21,108,000,000 + pairing × 10,000 + i for pairings 8-24), and kog3's `table_kog3` and `new17_kog3`, with their mixed rows (the cloud's copies of the four tables in `kt_kog_2026-09-28/`, on the cloud branch, are the same games);
- clause (d)'s block, **22,700,000,000 - 22,700,079,999**: kog3, kta3 and kt3 on the Rayquaza list;
- B2e (21,106,000,000 block), the Scizor row (21,108,000,000, pairings 0-7) and the four second lists, for kog3, kta3 and kt3;
- the Dustin-deck A/B, **22,600,000,000 block**, decks 07, 05, 11, 01, 03, arms kog3, kt3, kta3;
- the Rayquaza traces (21,108,900,000+, 200 games) and the readout counters (first 100 deals of the 28 table pairings, kog3, kt3, kta3, ktb3, ktc3);
- the reading itself: `READING.md`, `READING_numbers.txt`, the score45 pages, the second reader's files, and Dustin's rulings on them;
- the carrier census (the Rayquaza archetype's real Limitless cells, pooled 46.3 ± 4.8 over 606 matches, and its list);
- **the earlier data kt was designed from (Sept 25-26, all kp3 games).** kt's amendment 2 (item 5 and "What kt games exist") names the Tool census, the Trainer audit and the smokes as development data; the Skarmory causal test is added here:
  - the Skarmory Tool/Jasmine causal test on deck 07 (`skarmory_tool_jasmine_2026-09-25/`, block 21,102,000,000 - 21,102,999,999: Jasmine 1.8% to 82.4% of turns under a flat +10, and the skeptic's +5.7 points on a fresh paired 1,920-game block);
  - the Tool census (`tool_turn_effect_census_2026-09-25/`, the first 100 deals of the 28 table pairings) and the Trainer audit (`trainer_audit_2026-09-25/`, block 21,104,000,000 - 21,104,999,999);
  - the 43cef0b smokes (40 deals of the 28 pairings on the kp-based codes).

kta3 was also **chosen** from four codes after their tables were seen. Its development point estimates (+1.00, +0.21, +8.5) are therefore likely a little high. Fresh deals remove that on the simulator side.

### 3.2 The fresh deals

Every group keeps its development group's shape: same lists, same pairing numbers, same seat rule (even i puts the first-named deck in seat 0), i < 500 unless noted. Only the seed base moves, and clause (d)'s deal count (i < 2,000, third pass).

| Group | Development deals | **Fresh deals** | Range |
|---|---|---|---|
| The 28 table cells | 72,000,000 + pairing × 10,000 + i | **23,000,000,000** + pairing × 10,000 + i | 23,000,000,000 - 23,000,279,999 |
| Scizor rows (pairings 0-7) and the 17 new cells (pairings 8-24 of `new_decks.tsv`) | 21,108,000,000 + pairing × 10,000 + i | **23,001,000,000** + pairing × 10,000 + i | 23,001,000,000 - 23,001,249,999 |
| B2e, 96 pairings | 21,106,000,000 + pairing × 10,000 + i | **23,002,000,000** + pairing × 10,000 + i | 23,002,000,000 - 23,002,959,999 |
| Clause (d): Rayquaza list v the 8 panel lists (panel index 0-7, altaria to weezing) | 22,700,000,000 + index × 10,000 + i, i < 500 | **23,003,000,000** + index × 10,000 + i, **i < 2,000** | reserved 23,003,000,000 - 23,003,079,999; used 23,003,000,000 - 23,003,071,999 |
| Dustin-deck A/B | 22,600,000,000 + 10,000 × deck + 1,000 × opponent (+500 seat 1) + i, i < 120 | **23,004,000,000** + the same | 23,004,000,000 - 23,004,999,999 |
| Rayquaza traces (`--seed-stream`, 200 games each) | 21,108,900,000+ | **23,005,000,000** (v Lucario), **23,005,001,000** (v Vespiquen) | 23,005,000,000 - 23,005,001,199 |

- **The second lists** use their main lists' deals, as in kt: Lucario's, Suicune's and Weezing's at table pairings on the fresh 23,000,000,000 base; Charizard Y's on B2e pairings 40-47 on the fresh 23,002,000,000 base.
- **Clause (d)'s 2,000 deals per row** (third pass, Sept 29) are all fresh and all in its own sub-block: row `index` uses 23,003,000,000 + index × 10,000 + i, i = 0 to 1,999, so the last seed is 23,003,071,999 (7 × 10,000 + 1,999). Each row has 10,000 seeds of room, so 2,000 fit, and the sub-block ends at 23,003,079,999, below the A/B's 23,004,000,000 and above the 45 cells' and coverage sub-blocks (checked by script: no two sub-blocks overlap, and all sit inside 23,000,000,000 - 23,009,999,999). No new block. The fresh `--pairs` file for (d) (a copy of `kt_tables_2026-09-28/d_rayquaza.tsv`) gets `seed_first` = 23,003,000,000 + index × 10,000 (which the scan asserts) and `seed_last` = that + 1,999. `legality_scan --pairs` takes `--games` up to 10,000, one row's sub-block (its header, lines 32-33, the same at 233bced), so `--games 2000` needs no tool change.
- **kog3's baselines are re-run** on every fresh group, by the same binary. No development file serves as a baseline.
- The registration commit writes one row into START_HERE's seed table: "23,000,000,000 - 23,009,999,999 | Claude Code, kta's fresh deals (rl/results/kta_2026-09-29/REGISTRATION.md)".
- **Tool limit:** `legality_scan --decks` has the table's base 72,000,000 fixed and refuses `--seed-base`. Only `--pairs` takes a new base. So the 28 table cells are played from a `--pairs` file of the same 28 pairings (alphabetical order, same decks). Every `--pairs` file for a fresh base has its `seed_first` column rewritten to match (the scan asserts this). Section 4 proves the new files reproduce the old games.

### 3.3 What "fresh" does and doesn't mean for accuracy

- **Fresh:** the simulator's deals, for every game a verdict rests on.
- **Not fresh: the Limitless side.** The 45 cells' real results are the same 59 development-half events (`scoreboard_v3_2026-09-27/limitless_45_dev_events.json`) that scored kog3 at 14.0 and kta3 at 13.8. The Sept 25 holdout is spent. The only new real data is the post-freeze pull (5.7).
- **So the τ̂ margin (kog3 minus kta3) on fresh deals is a no-harm test on fresh simulator deals.** It can show that the earlier +0.21 was not a lucky draw of deals, and that no harm appears. It cannot be new evidence that kta plays closer to the real game, because the real figures are the ones the candidate was chosen against. RUN5, "Accuracy judges only what it can detect".
- **Written now, from that:**
  1. Clause (b) reads the margin as **no harm only**: its 90% lower bound at -1.0 or above. A positive margin is reported as "replicates on the simulator side", never credited as accuracy.
  2. ΔMSE is printed with the three-outcome label of RUN5 and its detectable size (5.4). On either route, wholly above zero fails kta3 with no fallback, and spanning zero sends it to the fallback, where the Jasmine threshold gates as well. Wholly below zero passes the accuracy clause and is reported as "demonstrated on the simulator side; the real side is development data". It replaces none of the other tests.
  3. Accuracy confirmation is the post-freeze pull, and only there.

---

## 4. Build and identity

**The build exists and is reused as-is. No new build. No cloud round.**
- **Commit ec7e1a867bdaae2b0b4a3d2730e36dfffb611900** = the official engine 233bced (`rl/engine-2026-09-28/`, main 9b4df9b) plus kt's presets redefined on kog. `git diff 233bced ec7e1a8 -- engine/` touches `engine/src/players/mod.rs` and `engine/src/players/value_functions.rs` only.
- **The programs**, in the laptop's WSL, `/home/dacz8976/engine-kt-ec7e1a8/engine/target/release/`. `STATUS.txt` records all three hashes. All three were re-hashed on the disk on Sept 29 (the first two by the drafter, all three again by the independent check) and match (the runner checks them again before use):
  - `deckgym` sha256 `407976366fa2104ee1f2663c94fe31b1c503466defe9d6154b7e60659cb0991c`
  - `examples/legality_scan` sha256 `924751ba0926993eaee87ecc8fb8301ffd0b7eee8490bfb3369427794328f938`
  - `tool_census` (built in the same tree) sha256 `d9799c96015f74b952889a7f7d9820bbc12d5d97e4d267ad8acc2b63cdcc720b`
- **The official program must never play kta.** It answers `kta3` with the old kp-based preset (kt's BUILD.md, "The code names"). Every kta game is played by these programs. Each output file name starts `ec7e1a8_fresh_`. A runner that finds any other hash stops. The hashes are checked before the first game and after the last, and printed in the reading.

**What the existing identity work licenses.** All of it was done at this same binary file, so none of it is repeated:
- 13 replays, all equal game for game on moves, decisions, openings, winner, points and seed (`identity_check.txt`; `STATUS.txt`, Sept 29 02:49 UTC): k3 and kp3 against the official references (14,000 each), kog3 against `table_kog3` (14,000) and `new17_kog3` (8,500), kq3 (14,000), kd3 and kpr3 (1,120 each), kog3 against the coverage baselines at i < 40 (B2e 3,840; Scizor 320; the four second lists 280, 280, 280, 320). So the shared player code is unchanged and kog3 at this binary **is** kog3.
- The cloud built ec7e1a8 on its own machine (different hashes). Its kta3 table files match the laptop's game for game: 14,000 of 14,000 on the 28 cells and 8,500 of 8,500 on the 17 (`kt_kog_2026-09-28/README.md`, "Where it ended"; the four kt codes together, 90,000 of 90,000). So the code's games don't depend on the build machine.
- Tests at the commit: the 14 kt tests pass, including `the_codes_are_kog_plus_their_switches` (kta's preset with its switch off is `KOG` exactly) and the value test (kta equals kog's value wherever nothing switch 1 reads is on the board, and after setup equals switch 1 on kp plus F). The full suite: 1,977 passed.

**The one gap, stated plainly.** The build note records that the step from the parsed code `kta3` to its value function was checked by reading, not by a test. A test would be a code change and a new commit, so a new build. This registration doesn't make it. It closes the gap by behaviour instead:
- kta3's changed games sit only in the 17 cells whose lists carry a switch-1 card (development: 17 of 45 cells, the same 17). If `kta3` were wired to a function with switch 2 or 3 on, it would change games in cells with no switch-1 card, as ktb3 (every cell, 65.39% of games) and ktc3 (Blaziken's cells, 5.84%) did.
- kta3 differs measurably from kt3 (Barrier on a qualifying holder 79% against kt3's 97%; deck 07 moves differ 83.5% against 95.3%).
- **Written now as an integrity line:** on the fresh deals, any changed game in a cell or coverage pairing whose two lists carry no switch-1 card (the reach lists of section 2) holds the reading (status PENDING, never a registered fail) until it is explained. On the development games there was none: all 559 changed table games sit in the 17 cells, and all 325 changed B2e games in the 12 pairings.
- Whether to close the gap with a test as well is Dustin's (section 10, f).

**Identity checks new to this registration** (before any fresh game; none needs a reference to a fresh deal):
1. **The programs' sha256** equal the three above.
2. **The runner and the pairs files reproduce the old games.** The fresh runner, run once with the *development* seed bases, i < 20 of every group, for kog3 and kta3, must equal kt's files game for game (moves, decisions, openings, winner, points, seed). All are in `rl/results/kt_tables_2026-09-28/`. Not all are committed (git, Sept 29): the `ec7e1a8_id_*` files are on the laptop's disk only. `ec7e1a8_id_kog3_500` and `_new17` have the same sha256 as the committed `kog_composition_2026-09-27/table_kog3.jsonl` and `new17_kog3.jsonl`; the i < 40 coverage identity files have no committed copy of their own.
   - the 28 table cells and 17 new cells: kog3 against `ec7e1a8_id_kog3_500` and `ec7e1a8_id_kog3_new17`; kta3 against `ec7e1a8_kta3_table` and `ec7e1a8_kta3_new17`;
   - Scizor, B2e and the four second lists: kog3 against `ec7e1a8_id_kog3_scz40`, `_b2e40` and `_var_*40` (the i < 40 identity files); kta3 against `ec7e1a8_scizor_kta3`, `ec7e1a8_b2e_kta3` and `ec7e1a8_var_*_kta3`;
   - clause (d): `ec7e1a8_d_kog3` and `ec7e1a8_d_kta3`.

   7,440 games. If they are equal, the only things that differ in the fresh run are the seed bases and the pairs files' `seed_first` column. **[proposed]** (i < 20 rather than kt's i < 40, to halve its time: kog3's i < 40 coverage identity alone took 854 s at this binary, B2e's 3,840 games in 642 s (`STATUS.txt`), so i < 40 with two codes would take about twice as long as i < 20's 15 to 25 minutes; section 8, row 1.)
3. **The A/B tool:** deck 07's first matchup (240 games per arm, kog3 and kta3), re-played at the development block, equals kt's `ec7e1a8_ab_d07_*` games (on the laptop's disk, not committed as of Sept 29; `ec7e1a8_ab_table.txt` is). 480 games. **[proposed]** (The fresh copy of `kt_ab_play.py` takes its block as an option, default 23,004,000,000, so this check runs the same code at 22,600,000,000. Its gate is in 5.6.)
4. **Timing (gates, as in kt):** kta3's 40-deal run (28 table pairings, 1,120 games) within 1.25 × kog3's. Both arms run fresh. Wall time gates; user+sys CPU seconds are recorded beside. If the first pair is over, both arms are rerun once and the second pair decides (kt amendment 2, item 7, and `kt_tables_2026-09-28/README.md`, "The timing check in `run_kt.sh`"). kt3's 0.91 doesn't cover kta3, since no kta3 timing exists. km's draft uses the same rule.
5. **Every scan page free of RULE findings** (as in kt's run). A RULE finding stops the reading.
6. **The counter tool.** `tool_census.rs` has the base 72,000,000 hard-coded. To count Stiffen on fresh deals it needs a `--seed-base` option (a tool change, its own sha256, checked by the census's own fingerprint test against the fresh table file). **[proposed]** If Dustin doesn't want the tool change, Stiffen's counter stays on the development deals (kog3 58 of 127 offered turns, kta3 84 of 152) and is labelled development-only. It gates nothing either way.
7. **If the program file is missing or its hash differs,** rebuild ec7e1a8 with `git archive` as `run_kt.sh` did, then: kog3 equals `table_kog3` and `new17_kog3` (22,500 games) and kta3 equals `ec7e1a8_kta3_table` and `_new17` (22,500 games), game for game, before anything else runs.

**A check that fails stops the run before any table game, and the failure is written down** (`run_kt.sh` did the same for identity and timing: `READING_numbers.txt` 1b). Nothing is read until it is explained.

**Pinning.** Adoption doesn't put kta into the official engine. If kta is adopted, an engine switch (RUN5's procedure) must carry these presets before the screen or the floor use it, and must settle the name clash with the official program's kp-based `kta3`. That is after the verdict and not part of this registration.

---

## 5. The reading

The reading code is `read_kta.py`: `read_kt.py` (committed b33a96c, run unchanged on kt) with the fresh files, kta3 only, the columns below, and the gating of 5.2 to 5.5, which `read_kt.py` does not have (the ΔMSE label read and gating on both routes, (d) gating on both routes, the Jasmine threshold in the fallback only). Its readings N1-N13 (`READING_numbers.txt`, "NOTES") are **adopted as registered**, except where RUN5's Sept 29 rules replace them: N6's "at 15% or more (d) is reported and gates nothing", and N11's "the other route's numbers" not read (with N1's "the CHOSEN route's tests only"), give way to 5.2 to 5.4, where the ΔMSE and its label are read on both routes and (d) gates on both. The rest stand: the 45-cell block gates; the match-level interval gates with the by-event one beside; clause (b)'s "no veto" is the 45-cell v2 vetoes through mixed rows plus the B2e held-out veto; own-side harm alone is a veto; a τ̂ bound within 0.10 of -1.0, or a ΔMSE bound within 5% of the interval's width of 0 at either edge (N9, extended to the lower edge: 5.4, "Near-zero bounds"), is PENDING until the same games are re-bootstrapped at `--reps 20000` (arithmetic, not new games), and that run decides; the zero-footprint integrity check holds the verdict and never fails it. It is written and reviewed before any fresh result is read except the footprint, tested with stand-in scenarios as `test_read_kt.sh` does, and committed. Everything is read once.

### 5.1 Footprint first, committed alone

- kta3 on both sides of the 45 cells against kog3 on the fresh deals, paired by (a, b, i), on the `moves` field. Share of the 22,500 paired games that differ.
- **Under 15%: the reserve route (5.2). 15% or more: the ordinary rule (5.3).**
- **Predicted, not chosen:** about 2.5% (development 559 of 22,500 = 2.48%), all in the 17 cells of section 2. The prediction never picks the route.
- **If it lands at 15% or more,** first, nothing else is read until the program hashes, the pairs files and the integrity line are checked: development was 2.48%, so a footprint six times larger points at a wiring or identity fault before it points at the route. If those are clean, the ordinary rule applies as written in 5.3.

### 5.2 The reserve route (footprint under 15%)

RUN5, "Reserve route for a change the table can barely see", and kt's FOOTPRINT AND ROUTES, with kog3 the only comparator.

**How this route sits inside RUN5's three outcomes** (RUN5, "Accuracy judges only what it can detect"). The ΔMSE on the 45 cells (kta3 minus kog3, 5.4) is read on this route too, and its label decides which tests gate:
1. **Wholly above zero:** kta3 fails on accuracy, with no fallback, whatever (b) to (d) say.
2. **Spanning zero ("inconclusive at this size"):** the fallback. Its four tests are this route's own: **no harm** is (b) and (c); **the coverage decks** are 5.5's coverage tests; **the pre-named decks** are (d); **the behavioural footprint** is the Jasmine threshold (5.5), which gates here and only here.
3. **Wholly below zero:** the accuracy clause passes. (b), (c), the coverage tests and (d) still gate, as the route requires. The Jasmine rate is reported with its threshold beside and gates nothing.

So (b), (c), coverage and (d) gate on every outcome that doesn't fail on accuracy. The one difference between outcomes 2 and 3 is whether the Jasmine threshold gates. km's draft reads its reserve route the same way.

- **(a)** the footprint of 5.1.
- **(b) no harm:** the τ̂ margin (kog3 minus kta3), match-level 90% interval's lower bound at -1.0 or above, and no rule-v2 veto counts, including the B2e held-out veto (own-side harm in the mixed rows). Rule v2 is kt's (FOOTPRINT AND ROUTES): a cell's miss grows by more than 6, or a deck's gap by more than 2; it counts only when the mixed rows against kog3 on the same deals show kta3's own side worse beyond the row's paired noise, and never on a cell with a Limitless band over 15.0. The held-out veto is read as `read_kt.py` N4 reads it. The by-event interval is printed beside. Read as in 3.3: no harm only.
- **(c) mixed rows:** the pairings of the 45 cells where kta3's fresh footprint isn't zero (expected 17), both directions (kta3 on the first-named deck only, then the second-named only, against kog3 on both), 500 deals, paired by deal. No meta deck's own side is worse beyond paired noise, pooled per deck over its cells (the whole 95% interval below zero is harm). The other cells (expected 28) are covered by the integrity line and an i < 40 sample of both mixed directions (2,240 games) **[proposed]**.
- **(d) the gain, one exact test, fixed now:**
  - **The deck:** the census Dragonair Mega Rayquaza ex list, `rl/results/kt_carrier_census_2026-09-26/decks/c-dragonair_mega_rayquaza_ex.txt` (Gouging Fire in 135 of 143 Limitless lists, 132 of them with two copies). It is a Limitless top-30 archetype, carries the relevant cards, and is not Dustin's deck (his files are `decks/dustin/` and the brews built with him; the archetype match with his deck 11 doesn't change that, per his Sept 26 ruling).
  - **The rows:** the eight panel lists (`decks/research/<name>.txt`), 8 × 2,000 deals per arm (16,000 games per arm, 32,000 in all; third pass), all on the fresh sub-block of 3.2. One arm has kta3 on the Rayquaza list, the other kog3. **kog3 plays the panel list in both arms.** Even i puts the Rayquaza list in seat 0.
  - **The statistic:** Rayquaza's own-side score per game (`first_deck_score`, Rayquaza's side whichever seat), the equal-weight mean over the 8 rows of the per-row mean difference (kta3 minus kog3), in points. Half-width 1.96 × sqrt(Σ per-row variance of the mean difference) / 8 (the variation check's, as `read_kt.py` N6).
  - **It passes if the mean minus the half-width is above zero.** Read once: no doubling, no rerun, no second block.
  - **The open confirmation** of kt's amendment 1 (Rayquaza as the one clause (d) test, Suicune reported) is given: by the laptop (`kt_tables_2026-09-28/README.md`), by Dustin about 7 pm Central Sept 28 ("Rayquaza, as registered", recorded in RUN5, "kt's clause (d) gates on Rayquaza, as registered"), and again Sept 29 (RUN5, kt bullet). His word on this text confirms it for kta.
  - **The scoreboard's Rayquaza list** (2 Trainers and the Dratini card differ) is a different list. Its 9 cells are read under (c) for no harm, and never as a second chance at (d).
  - **Required on both routes** (RUN5: "Clause (d)'s gain stays required in both routes". RUN5's two routes there are the normal accuracy route and the fallback; either can occur on either footprint route, so (d) gates on the reserve route and the ordinary rule alike). The same test, at the same size, is read on the ordinary route (5.3).
  - **Size: 2,000 deals per row, both arms, fixed now** (third pass, Sept 29, the same size, reason and convention as km's D2). (d) is paired and simulator-only, so its noise is all simulator noise, and more deals cut it; the scoreboard cells are the opposite case. The reason is recorded as the review gave it: "The two registrations should not carry different deal counts for the same clause with the same purpose." RUN5 records his Sept 29 decision as kta "with the same clause (d) gate as before" (then 500 per row); the deck, list, rows and statistic are unchanged, and the size is his to confirm (10, a).
  - **Power at 2,000.** Development half-width ±0.39 at 500 deals, so sd 0.199 there. The pooled interval halves as the deals quadruple, so at 2,000 the sd is about 0.10 and the **half-width about ±0.195 points** (MDE50 about 0.20, MDE80 about 0.28). If the fresh sd is like that, a true gain clears the test with these chances (a model estimate, normal approximation): 0.2 points 52%, 0.3 points 85%, 0.4 points 98%, 0.5 points 99.9%, 0.6 points or more about 100%. For comparison, at the earlier 500 deals (no route uses it now): 0.3 points 33%, 0.4 points 52%, 0.5 points 71%, 0.6 points 85%, 0.8 points 98%, 1.0 points 99.9%. Development's +1.00 was carried about half by one row (Vespiquen +3.8); without it the gain was about +0.6.
- **(e)** adoption for the screen and the table together.
- **Route's closure sentence:** the census found a usable archetype (Rayquaza), so the route is open. It is not loosened after the numbers are seen.

### 5.3 The ordinary rule (footprint 15% or more; not expected)

RUN5's three-outcome accuracy rule, with ΔMSE = kta3 minus kog3 on the 45 cells. Mixed rows are then needed on all 45 cells (about 28,000 more games than 5.2's set).
1. **ΔMSE wholly below zero:** accuracy passes. The rule-v2 vetoes, the coverage tests of 5.5 and clause (d) still hold. (d) is run and required, the same test at the same size as 5.2 (d): RUN5 says clause (d)'s gain "stays required in both routes". kt's amendment 2 had said (d) gates nothing at 15% or more. The later rule holds. The behavioural footprint (Jasmine) is diagnostic here, reported with its threshold beside. Confirmation is the ordinary one: post-freeze τ̂ margin at least half the margin this reading measures (the fresh-deal margin against the development Limitless half), its own 90% interval above zero.
2. **Wholly above zero:** fails on accuracy, no fallback.
3. **Spanning zero:** "inconclusive at this size". Only this case goes to the fallback, and the verdict rests on four tests, all required:
   - **no harm:** the τ̂ margin (kog3 minus kta3) has its 90% lower bound at −1.0 or above, and no rule-v2 veto counts through the mixed rows (including B2e's held-out veto);
   - **the coverage decks:** 5.5's own-side tests on B2e's held-out decks, the Scizor row and the four second lists;
   - **the pre-named deck:** clause (d) on Rayquaza, as in 5.2 (d);
   - **the behavioural footprint:** the Jasmine threshold of 5.5.
   Passing all four: adopted, "unconfirmed". Confirmation is the no-harm re-check of 5.7. Failing any: not adopted, named by the test failed, never as an accuracy negative.

### 5.4 Accuracy: printed, labelled, sized (both routes)

- ΔMSE (kta3 minus kog3, 95% interval, match-level, with the by-event interval beside), the **three-outcome label**, the interval's own **sd, MDE50 (1.96 sd) and MDE80 (2.80 sd)**, each also as real error. The τ̂ margin with its sd and the smallest harm its bound can see (about -0.9: (b) fails half the time only if the true margin is near -0.9 or worse, so (b) is a guard, not a measurement).
- Development, for scale (not evidence): ΔMSE -5.9 (95% -11.0 to -1.4), τ̂ margin +0.21 (90% +0.06 to +0.31). That interval is wholly below zero, so under this rule the development reading would have been outcome 1, with Jasmine reported rather than gated. **score45's own page for kta3 prints "ADOPTION RULE (v2): adopt". That is the ordinary rule's view of a code on the reserve route. It isn't read here and must not be quoted as an adoption.**
- **The label gates the same way on both routes:** wholly above zero fails kta3 on accuracy, whatever else passes, with no fallback (RUN5, outcome 2); spanning zero is "inconclusive at this size", never a negative, and sends kta3 to the fallback, where the Jasmine threshold gates beside no harm, coverage and (d); wholly below zero passes the accuracy clause, and on the reserve route it is reported as "demonstrated on the simulator side; the real side is development data" (3.3) and replaces no clause. How the reserve route's clauses sit in that reading is in 5.2.
- **Near-zero bounds, both edges** (`read_kt.py`'s N9, extended; second fix pass, Sept 29). The bounds are bootstrap percentiles with Monte-Carlo error (score.py's seeds are fixed, so a bound moves with `--reps`). N9 makes a bound within that error of its line PENDING below `--reps 20000`, and the 20,000-rep rerun decides. Here that covers both edges of the ΔMSE interval and the τ̂ bound:
  - a ΔMSE **upper** bound within 5% of the interval's width of 0 (N9 as written): it decides whether RUN5's outcome 1 (wholly below zero, accuracy passes) applies;
  - a ΔMSE **lower** bound within 5% of the interval's width of 0 (new here): it decides whether RUN5's outcome 2 (wholly above zero, fails with no fallback) applies;
  - the τ̂ margin's 90% lower bound within 0.10 of −1.0 (N9 as written; one printed as −1.00 is read at more digits).
  Each is PENDING below `--reps 20000`. The same games are re-bootstrapped at `--reps 20000` (arithmetic, not new games), and that run decides the label or the clause. The verdict waits for it. Fixed now, before any fresh result, so the rerun is a rule and not a choice.
- kog3's own real error on the fresh deals is printed beside (a free replication of 14.0).

### 5.5 Coverage, the behavioural footprint, and what is reported

**Coverage** (RUN5, "How coverage rows count"; kt amendment 2 item 4). Read whatever the 45-cell result, both routes. A veto blocks the takeover. A gain is reported, not credited. For each: kog3 and kta3 on both sides, then own-side mixed rows (kta3 on that deck, kog3 on the other, against kog3 on both, paired by deal), on the pairings where kta3's games differ from kog3's **[proposed; a zero-footprint pairing has an own side of exactly +0.00 ± 0.00 by construction, so it cannot veto (the last bullet below says why); the full alternative is in section 10, c]**:
- **B2e held-out archetypes, pairings 0-47** (`rl/results/b2e_card_check_2026-09-26/b2e_pairings.tsv`): own-side harm, whole 95% interval below zero, is a veto. Dustin's files (48-95) are reported beside, never counted.
- **The Scizor row** (pairings 0-7 of `new_decks.tsv`): own side pooled over its 8 rows, whole interval below zero is harm. Its accuracy is reported (Scizor's real figure 32.2 ± 10.2).
- **The four second lists** (`v-lucario_2`, `v-suicune_2`, `v-weezing_2`, `l-charizardy`): the same own-side test. Accuracy reported.
- The reading prints, for every no-harm test, **how many games changed** behind it, the number of own-side tests with any changed game, and the chance a harmless candidate trips at least one (1 - 0.975^n).
- **Why the differing pairings are enough** (second fix pass, Sept 29): where kta3's both-sides games equal kog3's on every deal of a pairing, its mixed-row games there equal kog3's as well (a pilot's choice is a function of the position; `read_kt.py`'s integrity line checked this on kt's data, where every mixed-row game in kta3's 28 zero-footprint cells equalled kog3's, `READING_numbers.txt`), so running only the differing pairings gives the same result as running every row. The choice is still Dustin's (section 10, c).

**The behavioural footprint** (RUN5: "diagnostic in the normal route and gating only in the fallback", and there only with a threshold written before the games):
- **The threshold: Jasmine on deck 07.** In the fresh A/B (5.6), kta3 plays Jasmine on **at least 20% of the turns she is offered.** Denominator: turns on which Jasmine was a legal play, as the census defines it. The rate is pooled over deck 07's 1,920 kta3 games (turns played added up over turns offered added up, as in the development figures), a point value with no interval. Development: kog3 0.4% (36 of 8,597), kta3 30.2% (1,711 of 5,669). **[For Dustin's word: 20% is two-thirds of kta3's development rate and about 48 times kog3's (36 of 8,597 is 0.42%).]** kt's registration also predicted a rate "well below the flat +10's 82%" (the flat +10 took it to 82.4%); that is reported, not gated.
- **The guard** (third pass, Sept 29; worded to match km's step 3, since the footprint gates are symmetric across the two drafts). kog3's own Jasmine rate is read on the same fresh deals (deck 07's 1,920 kog3-arm games of the fresh A/B, pooled the same way). **If kog3's own rate on the same fresh deals already reaches 20%,** the line cannot show the mechanism and reads "not shown at this size". **In the fallback this counts as the footprint test not passed:** the mechanism can't be shown on those deals, so kta3 reaching the threshold there is not evidence of it. kta is then not adopted, recorded as "mechanism not shown at this size", never as an accuracy negative. Outside the fallback it is reported. This stops the baseline meeting the threshold (development: kog3 0.4%, so it is not expected to bite). **[For Dustin's word, with the threshold.]**
- **When it gates:** only when the ΔMSE interval spans zero (the fallback), on either route (5.2, 5.3). When the interval is wholly below zero it is diagnostic: printed with the threshold beside, gating nothing. When the interval is wholly above zero kta3 has already failed. (The earlier draft gated it on the reserve route whichever way ΔMSE read. That is withdrawn: RUN5 says footprint counts gate only in the fallback.)
- **Reported, with predictions written now** (a wrong-direction move beyond its interval is "a finding to write down, not a gate that fired"):
  - Stiffen played per offered turn rises (development kog3 45.7% (58 of 127), kta3 55.3% (84 of 152); the interval will be wide, about ±12 points at this size, so a miss reads "not shown at this size").
  - Metal Core Barrier on a qualifying holder is unchanged (development 80% against 79%; kt3, which also has switches 2 and 3, moved it to 97%).
  - Steel Apron and Heavy Helmet play rates: reported. Development: Apron 70.8% to 84.7%, Helmet 86.6% to 90.2% (deck 01), 68.7% to 73.4% (deck 03).
  - **Scorching Interruption: no prediction.** The one development trace (Rayquaza v Lucario, 200 games) showed no visible change: offered 220 and used 151 under kta3, offered 223 and used 150 under kog3, wins 60 and 59. Half of (d)'s development gain came from the Vespiquen row, which that trace didn't cover. So the fresh traces are Rayquaza v Lucario and **Rayquaza v Vespiquen** (200 games each, one arm with kta3 on the Rayquaza side and one with kog3, kog3 on the other side, Rayquaza in seat 0, the same seeds in both arms), and the reading tallies, over the traces' changed games, the kind of the first decision that differs. The Rayquaza list is the census list of (d), `c-dragonair_mega_rayquaza_ex.txt` (the development Lucario trace used the scoreboard's list, `g-dragonair_mega_rayquaza.txt`, so the fresh one is not a like-for-like replay). **[proposed; reported, gates nothing.]** Its job is to say what kta does for Rayquaza, which the development numbers don't show.

**Reported beside, gating nothing** (Dustin, Sept 28 and 29):
- **Suicune:** its nine rows (7 table + Rayquaza v Suicune + Altaria/Greninja v Suicune): own side in the mixed rows (development -0.00 ± 0.25 over 4,500 deals; the table's seven +0.06 ± 0.30) and its real cells before and after. The same direction as Rayquaza is supporting evidence. The other direction is "a finding to write down, not a gate that fired." That is about Suicune as a second (d) test. Suicune is also one of the meta decks read under (c), pooled over its nine cells: own side worse beyond paired noise there is (c) harm, as for every meta deck (`read_kt.py` N7).
- **Rayquaza's real cells:** the scoreboard list's nine cells and the census list's cells against the eight, before and after (census pooled 46.3 ± 4.8 over 606 matches). Not gated.
- **The held-out direction** (RUN5, Sept 29), gating nothing: how B2e's held-out archetypes (pairings 0-47) moved. How many moved closer to their Limitless figure, how many further, and the mean change in miss. Development, kta3: all six within 0.1 point (further by +0.0, -0.1, +0.0, -0.1, +0.0, +0.0 for Charizard Y Entei, Garchomp, Hoopa/Absol, Manectric, Raticate, Whimsicott, in the reading's order).
- **Hydreigon's deck gap** (development 7.3 to 7.1) and the other deck averages.

### 5.6 The Dustin-deck A/B, fresh, reported, gates nothing except through 5.5's Jasmine line (which gates only in the fallback)

- **The reason the candidate exists, replicated on fresh deals.** Decks 07, 05, 11, 01, 03 against the eight panel lists, 240 games per matchup, 1,920 per deck and arm, kog3 and kta3 on the deck's seat, **kog3 on the opponent's seat in both arms**, paired by seed, with McNemar beside. The A/B tool is kt's (`kt_ab_play.py`, `read_kt_ab.py`, run by a copy of `run_kt_ab.sh`) with the block at 23,004,000,000 and the kt3 arm dropped.
- **The fresh A/B must pass `kt_ab_play.py`'s gate.** `kta3` starts with "kt", so the tool refuses to play it unless its gate file exists (`kt_ab_play.py` line 108). The gate file is the existing `rl/results/kt_tables_2026-09-28/GATE_koh_b2e_read` (its text: koh's B2e rows read and committed at 0497f47, 2026-09-29T02:45:30Z). How: the copy keeps the check unchanged and is given that file's full path with `--gate`, as `run_kt_ab.sh` does (its line 23 and 59). The tool's default gate path is its own folder, where no gate file exists, so without `--gate` the copy refuses. No new gate file is written and the file is not moved. The gate's reason still holds: kt's base would change if koh were adopted, and koh stays not adopted (RUN5, "Where things stand"). The copy of `run_kt_ab.sh` also keeps its identity check, pointed at kta's own record: no A/B game until section 4's checks are recorded as passed in the kta tables folder's `STATUS.txt` (kt's runner checks for "KT PART A DONE" the same way).
- Printed: deck win rates; the paired difference; Jasmine offered and played; Metal Core Barrier, Steel Apron and Heavy Helmet placement (qualifying holder or not).
- **It isn't the gate** (Dustin, RUN5, kt bullet: "The +8.5 on your Skarmory deck is real simulator evidence and it should be in the registration as the reason the candidate exists; it isn't the gate."). If deck 07's fresh interval isn't above zero, the reading says plainly that the reason the candidate exists did not replicate. That non-replication is reported and gates nothing: adoption rests on section 6's tests (Rayquaza's gain, no harm, coverage, and Jasmine only in the fallback), which is stated beside the verdict. This is settled by his word and is not an open question (second fix pass, Sept 29).
- A Dustin deck hurt beyond noise is a finding to write down, not a veto (his files are reported, not counted, RUN5, "Nothing is excluded from testing because it matches Dustin's decks").

### 5.7 Confirmation (RUN5, "When post-freeze data is read")

- **Joining the list.** If kta is adopted before the post-freeze read, it joins that pull's list by a commit to `rl/results/postfreeze_2026-09-27/README.md` before the data is opened. Otherwise it waits for the next pull (rolling freeze).
- **The check** (a no-harm re-check, "as for a no-harm fix"): the τ̂ margin (kog3 minus kta3) on post-freeze events alone, 90% lower bound at -1.0 or above, and no veto. Rayquaza's and Suicune's post-freeze real cells reported with their sizes. The read is once, at 804 panel matches and 303 on the new cells (about mid-October), or at the last pull before Mega Garchomp ex, with the size printed beside.
- **Lapse clause (kt item 6):** kta carries kog's A and F. If kog's row (or kpg's or koa's that it inherits) has not passed by the pull at which kta's check passes, kta is not confirmed yet. kta's passed check stands and is not read again. It is confirmed at the first later pull at which those rows pass. A check that failed is read again at the next pull, on the events after it.
- **A failed check reads "not confirmed at this size"**, never "no better". Until confirmed, an adopted kta is the working pilot, "unconfirmed".
- Events up to B4b's release are B4a-meta events. B4b (releasing 8 pm Central Sept 29, expected reprint-only) is a separate matter and doesn't enter any kta game. If it isn't reprint-only and the window closes, that is a decision for Dustin (RUN5, "B4b and the size rule").

### 5.8 Which condition carried the verdict (Dustin's column, not a rule)

The reading prints a table with one line per condition, its result, and the number of changed games behind it, in the form of `READING.md`:

| Condition | What it fixes or tests | Expected to say |
|---|---|---|
| (a) footprint under 15% | the route | fixes the route |
| ΔMSE label (5.4) | wholly above zero fails; spanning zero sends to the fallback | whether the Jasmine threshold gates |
| (b) no harm on the 45 cells | τ̂ lower bound, vetoes | little: with about 2.5% of games changed, no harm is nearly automatic |
| (c) no meta deck worse | mixed rows, 17 cells | little, for the same reason |
| coverage | B2e, Scizor, second lists | little, except Scizor (980 of 4,000 mixed-row games differed) |
| **(d) the gain on Rayquaza** | pre-named deck | **informative** |
| **Jasmine on deck 07** | the mechanism (gates only in the fallback) | **informative** |

"No harm with almost no changed games" is the reserve route working as designed. It says little. The informative parts are the gain on the pre-named deck and the mechanism.

### 5.9 (d) per cell, beside the pooled number (Dustin's column, not a rule)

Printed: the eight rows (kog3 to kta3, change ± 95%), the pooled figure, and **each row's share of the pooled sum**, so a gain that is really one cell shows as one cell. Development: Vespiquen +3.8 ± 2.0 carried about half of the pooled +1.00; the other seven rows were +0.0 to +1.4, all zero or positive. If one row supplies more than half of a passing pooled gain, the reading says so beside the verdict. It gates nothing.

---

## 6. Outcomes fixed now

**Adopted** (as the working pilot, "unconfirmed"), only if all of these hold:
1. identity: section 4's checks pass (timing included), every scan page free of RULE findings, the integrity line clean;
2. (a): footprint under 15%. Otherwise 5.3 applies, with the same tests in the ordinary rule's form;
3. ΔMSE not wholly above zero (RUN5's outcome 2: that fails, with no fallback). A bound near 0 at either edge is PENDING until the 20,000-rep rerun decides (5.4, "Near-zero bounds");
4. (b): τ̂ margin lower bound at -1.0 or above, no veto counts (including B2e's held-out veto);
5. (c): no meta deck's own side worse beyond paired noise;
6. **(d): Rayquaza's pooled own-side gain with the whole 95% interval above zero** (on both routes);
7. coverage: no own-side harm on the B2e held-out decks, the Scizor row or the four second lists;
8. **only if the ΔMSE interval spans zero (the fallback):** the Jasmine threshold of 5.5, with its guard (kog3's own rate on the same fresh deals at 20% or more counts as not passed). Otherwise it is reported and gates nothing;
9. and (e) for the screen and the table together.

**Not adopted** if any that applies fails. kog stays the working pilot. The reading names the test that failed (harm, coverage, gain, mechanism, or accuracy-worsening). It never records an accuracy negative for a result that is only inconclusive.
- **(d) failing** reads "gain not shown at this size on Rayquaza", with the interval and the detectable size printed. It is not read as evidence that switch 1 does nothing. The Skarmory A/B stays a simulator finding about that deck. This registration doesn't create an override route. Any override is Dustin's, recorded as such, as with kp3.
- **A veto or harm** on any coverage row blocks the takeover. A gain there is reported, not credited.

**Unchanged by this registration:** kt3's "not adopted, as registered" stands. kt3, ktb3 and ktc3 are not run. A spec change after any reading is a new code. This registration offers no second fresh round on the same spec.

**If adopted:** it goes on the post-freeze list (5.7), and an engine switch is needed before the screen or the floor use it (section 4, "Pinning").

---

## 7. What would show it wrong (stated before any game)

Each item says whether it gates.
1. **The footprint is far from 2.5%** (gates the route; 5.1). Investigated as a wiring or identity fault first.
2. **A changed game in a cell or coverage pairing whose lists carry no switch-1 card** (holds the reading). kta3 would be doing more than switch 1.
3. **(d) fails:** Rayquaza's gain doesn't clear zero at this size (gates). The development +1.00 comes from a code picked after the tables were seen, and one row carried about half of it. A smaller gain is expected on fresh deals, and (d)'s detectable size decides how much can be said.
4. **Jasmine doesn't reach the threshold, or kog3's own rate on the same fresh deals already reaches it (the guard)** (gates only when the ΔMSE interval spans zero; otherwise reported). Then the Skarmory result did not come from the mechanism the registration names, or the deals can't show it.
5. **Own-side harm** anywhere in (c) or coverage (gates). About n tests can each trip by chance, and the reading prints n and the chance.
6. **ΔMSE wholly above zero** (gates, on either route, with no fallback).
7. **Deck 07's fresh A/B interval not above zero** (reported; gates nothing, as Dustin settled: 5.6). The reason the candidate exists is then not confirmed.
8. **A Dustin deck hurt** in the fresh A/B (reported; a finding).
9. **Stiffen falls, or Barrier on a qualifying holder moves** (reported). Unpredicted interactions.
10. **The one thing no number here can show:** that kta plays closer to the real game. That waits for the post-freeze pull (5.7).

---

## 8. Compute plan

Laptop, WSL, `RAYON_NUM_THREADS=12`, `nice -n 10`, one runner at a time. Rates are Sept 28-29's measured ones on this shared laptop (7.6 games a second on the 45-cell tables, 10 to 21 on the smaller sets, B2e about 17). kt's readout counters finished at 14:19 UTC Sept 29 (`STATUS.txt`, "KT COUNTERS DONE"), and no game process was running when the checker looked at 14:27 UTC. B4b's release (8 pm Central Sept 29) may bring its own laptop work: the upstream check at 9:07 pm and 9:03 am, and the refresh's replays of the k3, kp3 and kog3 tables (RUN5 A5). Where kta sits relative to those and to km's jobs is Dustin's.

| # | Run | Games | Reference time |
|---|---|---:|---:|
| 1 | Runner identity (development bases, i < 20, kog3 and kta3) and the A/B tool check | 7,920 | ~15-25 min |
| 2 | Timing, kog3 and kta3, 40 deals × 28 pairings | 2,240 | ~6 min |
| 3 | kog3 and kta3 on the 45 cells (22,500 each) | 45,000 | ~87 min |
| | **Footprint read and committed alone** | | |
| 4 | Mixed rows, the ~17 cells with a changed game, both directions (17,000), and the integrity sample on the other 28 cells (2,240) | 19,240 | ~19 min |
| 5 | Clause (d): 8 rows × 2 arms (kog3 and kta3 on the Rayquaza side, kog3 on the panel) × 2,000 deals | 32,000 | ~43 min |
| 6 | The A/B: 5 decks × 1,920 × 2 arms | 19,200 | ~38 min |
| 7 | Rayquaza traces, v Lucario and v Vespiquen, 2 arms | 800 | ~1 min |
| 8 | Census counters, kog3 and kta3, first 100 deals × 28 pairings (needs the tool option, 4.6) | 5,600 | ~6 min |
| 9 | Scizor: both sides, kog3 and kta3, and the two mixed directions | 16,000 | ~17 min |
| 10 | Second lists (29 rows): kog3 and kta3 both sides, mixed rows (upper bound) | 43,500 | ~44 min |
| 11 | B2e (96 pairings): kog3 and kta3 both sides (48,000 each) | 96,000 | ~96 min |
| 12 | B2e mixed rows on the pairings with a changed game (about 12 expected) | ~6,000 | ~6 min |
| | **Total** | **~293,500** | **~6.3-6.5 hours** |

- **Row 1's time** (corrected at the second fix pass, Sept 29; it said ~11 minutes). kog3's i < 40 coverage identity at this binary took 854 s for 5,320 games (B2e's 3,840 games in 642 s: short per-pairing runs go at about 6 games a second, `STATUS.txt`). At i < 20 with two codes the coverage part is the same 5,320 games in twice as many runs; the 45 cells and (d) add 2,120 games and the A/B check 480. So about 15 to 25 minutes.
- **Row 5's time** (third pass, Sept 29): kt's development (d) ran 4,000 games per arm in 316 s (kog3) and 323 s (kta3) at this binary (`STATUS.txt`), 12.5 games a second, so 32,000 games take about 43 minutes. That is 24,000 games and about 32 minutes more than the 500-deal row it replaces (8,000 games, ~11 min). The total went from about 269,500 games and 5.8 to 5.9 hours to about 293,500 games and 6.3 to 6.5 hours.
- **With the upper bounds** (mixed rows on all 45 cells as kt ran them, and on all 96 B2e pairings): about 361,500 games, about 7.4 to 7.6 hours.
- **If the timing pair is over and rerun once** (4.4): +2,240 games, about +6 minutes.
- **One overnight session.** Overnight and at home the laptop runs anything (his quiet-hours note). Run 3's footprint is read and committed before runs 4 to 12 are read, but the runner doesn't stop for it, as kt's didn't.
- **Cloud: none.** No build is needed. A cloud round would be needed only if Dustin asks for the wiring test (4, "The one gap"), which is a code change and a new commit with its own identity replays. (d)'s 2,000 deals per row run on the laptop, like every kta game (section 4 names the laptop's programs only). The cloud's own build of ec7e1a8 has other hashes (`BUILD.md`: deckgym 158b0564…, legality_scan e19703b1…), so a cloud run would first need section 4 amended to name them. Its games matched the laptop's on 90,000 of 90,000 (`kt_kog_2026-09-28/README.md`).

---

## 9. Who does what, and in what order

- **Dustin:** his word on the text, the build and identity, and the tables (three gates, in that order). Every open choice in section 10.
- **Laptop session (Claude Code):**
  1. the fresh pairs files, the runner (`run_kta.sh`, from kt's `run_kt.sh`), the A/B scripts with the new block, the reading code `read_kta.py` and its stand-in tests, one independent review of the diff against `read_kt.py` and this text;
  2. the section 4 checks;
  3. all games, from the ec7e1a8 programs with their hashes recorded, output in `rl/results/kta_tables_<date of the first table>/`;
  4. the footprint, committed alone, then the reading.
- **Second reader** (RUN5's tier 1: any pilot adopted or played by Dustin gets one): an independent Sonnet agent with its own code, comparing only after computing, plus an outcome audit against this text, as kt had. Run whichever way the verdict goes **[proposed]**.
- **Cloud:** nothing, unless Dustin asks for the wiring test.
- **Fable:** reviews on request only.
- **One owner per file:** this registration text is a draft written by the kta-writer agent and committed by the parent session. The tables folder is the laptop's.

---

## 10. Needs Dustin's word

The gates in the top block ("Needs Dustin's word"), and these choices, with the drafter's lean where there is one:
- **a. Clause (d)'s deal count: 2,000 per row** (third pass, Sept 29, from the review he forwarded; it replaces the draft's earlier 500 per row and removes the "2,000 as an option only" line). The reason is km's D2 (RUN5): clause (d) is paired and simulator-only, so its noise is all simulator noise, and quadrupling the deals halves it; RUN5's Sept 29 rule lets a registration fix more deals in such cells before the tables ("cheaply, and only there"). And, as the review put it: "The two registrations should not carry different deal counts for the same clause with the same purpose." All 2,000 deals per row are fresh, in kta's own (d) sub-block (3.2), both arms: 32,000 games, about 43 minutes (24,000 games and about 32 minutes more than at 500). It is read once, with no doubling. What needs his word: RUN5 records his Sept 29 decision as kta "with the same clause (d) gate as before", and the earlier test was 500 per row, so this reads "the same gate" as the same deck, list, rows and statistic, at a new size. (Section 5.2 (d) has the chances of clearing at 2,000, with the 500-deal figures beside for comparison.)
- **b. The Jasmine threshold: at least 20% of offered turns on deck 07,** from the development figures (kog3 0.4%, kta3 30.2%); 20% is two-thirds of kta3's rate, between the two rates and above their midpoint (15.3%). It stays at 20% (third pass). It gates only when the ΔMSE interval spans zero (the fallback), on either route, and is diagnostic otherwise, as RUN5 says. (The earlier draft gated it on the reserve route whichever way ΔMSE read. That is withdrawn.) **With it, the guard** (third pass, worded as km's): if kog3's own Jasmine rate on the same fresh deals already reaches 20%, the footprint test counts as not passed in the fallback (5.5). The number and the guard are his to set.
- **c. Mixed rows only on pairings where kta3's games differ from kog3's,** for the 45 cells (kt's amendment 2 rule) and, by the same argument, for coverage. RUN5's record of his Sept 28 ruling says coverage rows get mixed rows "every time" (his own words: "coverage rows count for the mixed-row veto and are reported for accuracy"). The drafted design does read every coverage row, and drops only rows that cannot differ (5.5, last coverage bullet, says why the two give the same result for less compute). The full alternative (all 96 B2e mixed rows, all 45 cells) adds about 68,000 games and about 66 minutes. km's draft now does the same (third pass, Sept 29), so the two drafts no longer differ here; the reading of "every time" is still his to confirm.
- **d. Removed at the second fix pass (Sept 29): not an open question.** It asked whether a fresh Skarmory A/B that doesn't replicate should gate. Dustin had already settled it (RUN5, kt bullet: "... it isn't the gate"): non-replication is reported and gates nothing (5.6). The letter is kept so the other letters' references stay right.
- **e. The Rayquaza v Vespiquen trace and first-divergence tally,** reported only. It answers what kta does for Rayquaza, which the development numbers leave open.
- **f. The wiring gap** (4): accept the behavioural closure (the integrity line, the differences from kt3), or ask for a test and a new commit (a cloud round). **Lean: accept.**
- **g. The operational reading of RUN5's three outcomes for a reserve-route candidate** (5.2, "How this route sits inside RUN5's three outcomes"; 5.4; 5.5; 6): wholly above zero fails with no fallback; spanning zero is the fallback, whose no-harm, coverage and (d) tests are the route's own, with the Jasmine threshold added; wholly below zero passes accuracy and leaves the route's tests gating. km's draft reads its reserve route the same way. With it goes the near-zero rule at both ΔMSE edges (5.4, "Near-zero bounds"): `read_kt.py`'s N9 covered the upper bound; the lower bound near 0, which decides outcome 2, is added the same way, in both drafts. It is the drafters' reading, and his to correct.
- **h. The queue:** where kta's games go relative to km's jobs and B4b's refresh (kt's counters are done).
- **i. The smaller [proposed] items,** each cheap and easy to drop: the i < 20 runner replay (4.2), the A/B tool check and the block option it needs (4.3), the census tool's `--seed-base` option (4.6), the i < 40 integrity sample (5.2 c), and the second reader (9).

---

## 11. What was run to write this draft

Read-only work only: files read, `git show` of the kt registration and build note from the cloud branch, `git grep` of every branch for seed numbers, `sha256sum` of `deckgym` and `legality_scan` (they match `STATUS.txt`), and `card.py` for the cards quoted. **No game, no build, no engine run.** The chances in 5.2 are arithmetic from the development half-width (normal approximation), not simulations. The compute table's times are Sept 28-29's measured ones from `STATUS.txt`.

An independent check (Sept 29, read-only) then re-hashed all three programs, re-added the compute table, compared the coverage changed-game counts with the committed game files (`moves` field, kta3 against kog3's baselines), and read `legality_scan.rs`, `tool_census.rs`, `kt_ab_play.py` and `read_kt.py` for the seed and tool claims. It played no game. Its fixes are in the text above and are listed in the parent session's report.

---

## 12. Harmonised with RUN5 (Sept 29)

Edited on Sept 29 so that this draft and km's (`rl/results/trainer_pricing_2026-09-28/REGISTRATION_DRAFT.md`) read RUN5's "The frame a candidate is read in" the same way: "Accuracy judges only what it can detect", "Clause (d)'s gain stays required in both routes", "The held-out direction, reported beside every verdict", "How coverage rows count", and Dustin's Sept 29 decisions under kt in "Where things stand". Read against RUN5 as it stands on Sept 29, `rl/results/error_attribution_2026-09-29/README.md` (with its Check), `rl/results/eval_power_2026-09-29/README.md`, and `kt_tables_2026-09-28/` (`kt_ab_play.py`, `run_kt_ab.sh`, `README.md`, the gate file). Read-only: no game, no build, no engine run. Still a draft.

Changes:
1. **Title and top.** The title says "harmonised". A line "Written under the attribution of Sept 29" was added, with its one caveat: kta3's development ΔMSE interval (−11.0 to −1.4) did not span zero. The three-item "Dustin's word is needed" list became one six-item "Needs Dustin's word" block, pointing to section 10. The Status block points here.
2. **The three outcomes, the same on both routes** (3.3 item 2; 5.2, new paragraph "How this route sits inside RUN5's three outcomes"; 5.3 outcome 3; 5.4; section 6; section 7 item 6). Wholly above zero fails with no fallback on either route. Spanning zero is the only way into the fallback. On the reserve route the fallback's no-harm, coverage and pre-named-deck tests are the route's own (b)+(c), coverage and (d). On the ordinary route the fallback's four tests are written out. Wholly below zero passes accuracy and leaves every other test gating. Before this, 3.3 and 5.4 said the label changed the verdict only when wholly above zero.
3. **The Jasmine threshold gates only in the fallback** (1; 5.5; 5.6 heading; 5.8; section 6, item 8; section 7 item 4; 10 b). The wording that gated it on the reserve route "whichever way ΔMSE reads" is removed. The number stays 20% of offered turns on deck 07, from the development figures (kog3 0.4%, kta3 30.2%), marked for his word. 5.4 notes that the development reading would have been outcome 1, with Jasmine reported.
4. **Clause (d)** (5.2 (d); 5.3 outcome 1; section 6 item 6; section 8; 10 a). Required on both routes, the same test at the same size. 500 deals per row, "as before" (RUN5's record of his Sept 29 decision), read once, no doubling. 2,000 per row is listed as an option for his word only. The draft's earlier "Lean: 2,000" is withdrawn.
5. **Read once, and RUN5's doubling line** (section 1). "Doubling deals to 2,000 when undecided" belongs to the τ̂ margin E = 3 comparison in "Variants and process" and doesn't apply here. "Read once" is now the text's rule, not a [proposed] item, and is removed from 10 i.
6. **The fresh A/B's gate** (5.6, new bullet; 4.3). `kt_ab_play.py` refuses a kt code without its gate file. The copy is run with `--gate` naming the existing `kt_tables_2026-09-28/GATE_koh_b2e_read`, as `run_kt_ab.sh` does, with the check left in place, and with the runner's identity check pointed at kta's own record. The copy takes its block as an option, so check 4.3 runs the same code at the development block ([proposed]).
7. **Timing** (4.4; section 6 item 1; section 8). Wall time gates at 1.25 × kog3, both arms fresh, rerun once if over, user+sys CPU recorded beside, as in kt and as km's draft now says. It is no longer a [proposed] item (removed from 10 i). The compute plan adds the rerun's cost.
8. **Coverage** (10 c). A sentence says km's draft runs mixed rows on every coverage row, so the two drafts differ there until he picks one. The design itself is unchanged.
9. **Section 10.** The intro, a, b, c, g and i were rewritten as above.

Not changed: switch 1's spec, the seeds, the build and identity (apart from 4.3's block option and 4.4's wording), (b), (c), the coverage rows, the held-out direction column, the traces, the confirmation and the compute plan's main rows.

**Fixed at the harmonisation check (Sept 29, a checker other than the editor; read-only, no game):**
1. Top line: "If the fresh one doesn't either" now reads "is also wholly below zero" (an interval wholly above zero also doesn't span zero, and that fails).
2. Section 5's first paragraph: `read_kt.py` gates ΔMSE on the ordinary route only and (d) on the reserve route only (its N6 and N11), so "N1-N13 adopted as registered" contradicted 5.2 to 5.4. N6 and N11 (and N1's chosen-route-only comparison) now give way to 5.2 to 5.4, and `read_kta.py` is said to add that gating.
3. 5.2 (d): RUN5's "both routes" in "Clause (d)'s gain stays required in both routes" means the normal accuracy route and the fallback. Said so; the outcome is unchanged.
4. 10 c: "every time" is RUN5's record of the ruling, not his quoted words. His words are quoted beside it.
5. 5.5: "50 times kog3's" is about 48 times (0.42%).
6. 4.2 and 4.3 called the reference files "committed". The `ec7e1a8_id_*` and `ec7e1a8_ab_*` game files are on the laptop's disk only (git status, Sept 29). The text now says so and names the committed twins of the two table files.

---

## 13. Second fix pass, Sept 29

An independent checker left seven points on this draft and km's after the harmonisation. Four touch this draft (numbered as the checker numbered them; points 2, 3 and 7 are km's only). Applied as given, read against `read_kt.py` (N9, `tau_gate`, `dmse_gate` and the clause (c) integrity line), `READING_numbers.txt`, `kt_tables_2026-09-28/STATUS.txt` and RUN5. Read-only: no game, no build, no engine run. Still a draft, and the top block still lists what needs Dustin's word.

1. **Near-zero bounds, both edges** (section 5's first paragraph; 5.4, new bullet "Near-zero bounds"; section 6 item 3; 10 g). The draft adopted N9 for the τ̂ bound only. N9 (a bound within Monte-Carlo error of its line is PENDING below `--reps 20000`, and the 20,000-rep rerun decides) now also covers both edges of the ΔMSE interval: the upper bound within 5% of the interval's width of 0 decides RUN5's outcome 1, as N9 had it, and the **lower** bound within 5% of the width of 0 decides outcome 2 (fail, no fallback), which N9 didn't cover because `read_kt.py` had no outcome 2. km's draft now has the same rule.
4. **Coverage mixed rows** (5.5, new last coverage bullet; 10 c, a pointer). One sentence: where kta3's both-sides games equal kog3's on every deal of a pairing, its mixed-row games there equal kog3's as well (a pilot's choice is a function of the position; `read_kt.py`'s integrity line checked this on kt's data), so running only the differing pairings gives the same result as running every row. The choice stays in 10 c for Dustin's word.
5. **Row 1's time** (section 8 row 1, the total and the upper-bound line; the reason in 4.2). Row 1 said ~11 minutes. kog3's i < 40 coverage identity took 854 s at this binary (B2e's 3,840 games in 642 s), so at i < 20 with two codes it is about 15 to 25 minutes. The total is now about 5.8 to 5.9 hours (was 5.7), and the upper bounds about 7 hours (was 6.8). 4.2's reason for i < 20 was "to keep it near ten minutes"; it is now "to halve its time" (i < 40 with two codes would take about twice as long).
6. **The fresh Skarmory A/B is not an open question** (the top block, item 4; 5.6; section 7 item 7; 10 d). Dustin settled it (RUN5, kt bullet: "... it should be in the registration as the reason the candidate exists; it isn't the gate"). 10 d is removed as a question and left as a one-line stub, so the letters e to i keep their references. 5.6 and section 7 say non-replication is reported and gates nothing.

Not changed: the gate, the seeds, the build and identity scope, (b), (c), (d) and its size, coverage, the Jasmine threshold, and every game count.

---

## 14. Third pass, Sept 29 (review changes)

Dustin forwarded a review of this draft and km's. Its changes are applied here as given; the texts await his word. Read against km's draft, `kt_tables_2026-09-28/STATUS.txt` (the (d) timings), `d_rayquaza.tsv`, `engine/examples/legality_scan.rs` (the `--games` cap, the same at 233bced) and RUN5. Every count, seed range and time in this pass was re-added by a script (`fix8/check.sh` in the session's scratch folder, modelled on the last pass's): no game, no build, no engine run. Still a draft. **This note governs where an older note (sections 12 and 13) says otherwise.** Numbered as the review numbered its changes; changes 3 and 4 are km's, except that change 3 also removes the "the two drafts differ" item here.

1. **The Jasmine guard** (the top block, item 2; 5.5, new bullet "The guard"; section 6 item 8; section 7 item 4; 10 b). The threshold stays at 20% of offered turns on deck 07. Added, worded to match km's: if kog3's own Jasmine rate on the same fresh deals (deck 07's kog3-arm games of the fresh A/B) already reaches 20%, the line reads "not shown at this size", and in the fallback that counts as the footprint test not passed. Reason: the footprint gates are symmetric across the two drafts, and this stops the baseline meeting a threshold. 10 b now also says where 20% sits: between kog3's 0.4% and kta3's 30.2%, above their midpoint (15.3%), at two-thirds of kta3's rate.
2. **Clause (d) at 2,000 deals per row** (the top block, item 3; section 1, "Read once"; 3.2, the group line, the (d) row of the table and the bullet that replaces "Reserved, not used unless Dustin says so"; 5.2 (d), the rows, the size and a new power bullet; section 8, row 5, the total, a new row-5 note, the upper-bound line and the cloud line; 10 a). On the census Rayquaza list's 8 rows, both arms (kta3 and kog3 on the Rayquaza side, kog3 on the panel), all 2,000 deals on fresh seeds in kta's own block: 23,003,000,000 + index × 10,000 + i, i < 2,000, seeds 23,003,000,000 - 23,003,071,999, inside the (d) sub-block 23,003,000,000 - 23,003,079,999, which overlaps none of kta's other sub-blocks (checked by script) and needs no new block and no tool change (`--pairs` takes `--games` up to 10,000). Power: half-width about ±0.195 points at 2,000 (sd about 0.10); a true gain of 0.3 points clears 85% of the time, 0.4 points 98%, 0.5 points 99.9% (500-deal figures kept beside for comparison). Compute: 8 × 2 × 2,000 = 32,000 games for (d), about 43 minutes at kt's measured 12.5 games a second. Removed: the 500-deal choice and "2,000 as an option only". The reason, recorded: km's D2 reason (paired and simulator-only, so more deals cut its noise), and "The two registrations should not carry different deal counts for the same clause with the same purpose." "Read once" is unchanged: the size is fixed before play, not a doubling.
3. **Coverage mixed rows** (the top block, item 4; 10 c). km's draft now runs coverage mixed rows only where the candidate's both-sides games differ from kog3's, as this draft does. The "km's draft runs them on every coverage row, so the two drafts differ" wording is removed from both places. The choice itself (RUN5's record says "every time") stays in 10 c for his word.
5. **The attribution case, in one line** (the top). A new line says this text was written under the Sept 29 attribution (the pilot lever sits in Rayquaza's nine cells; kta's (d) is on Rayquaza, km's on Lucario, outside it), that the verdict is expected to rest on the fallback, and why the Jasmine threshold must therefore be right, in the review's words: "they're doing the work the accuracy clause can't". The detailed paragraph that follows is unchanged apart from its heading.

**New totals (section 8):** about 293,500 games and 6.3 to 6.5 hours (was about 269,500 and 5.8 to 5.9); with the upper bounds about 361,500 games and 7.4 to 7.6 hours (was about 337,000 and 7). The (d) row: 32,000 games, about 43 minutes (was 8,000, about 11).

**Still needs Dustin's word from this pass:** the (d) size change against RUN5's "the same clause (d) gate as before"; the Jasmine guard; and, as before, 20% itself and the reading of "every time" for coverage mixed rows.

Not changed: switch 1's spec, the build and identity (including identity check 2's i < 20 replay of the development (d) files), (b), (c), the coverage rows, the Jasmine threshold's number, the A/B, the traces, the confirmation, every other sub-block and every other row of the compute plan.
