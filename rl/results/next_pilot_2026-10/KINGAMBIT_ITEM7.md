# ky3 item 7: the Kingambit pilot (`_blade`, `_count`, the pilot test)

**Audited and approved by Fable, Oct 15.** This is ky3 item 7, after `EXPECTED.md`. Fable launches it; the driver running items 1-6 does not.
- **Where it runs:** the same build clone and target dir (`sonnet/ky3-pilot`, `CARGO_TARGET_DIR=/home/dacz8976/ky3-target`), as an incremental compile.
- **When:** only once C: has 15 GB free. If the compaction window slips, item 7 waits.
- **The pilot test** (section 3) is written before any run, on the list he actually plays (73dfed58d1d6), read by path.
- **Stage A** runs detached on the laptop and costs under $1. The slow confirm goes to Managed Agents.

The item includes its two needs:
- the PL2 logger, with the Blade count at own turns 6 and 8;
- print-only score dumps for F and C at 203719 t17 and 010837 t03.

Read it alongside `DESIGN_NOTE.md` sections 2 and 5 ("The Kingambit challenge") and `DESIGN_NOTE_CASES.md`.

Line numbers refer to origin/main 70319c3d. These files are the same blobs on 9a0bc5ac: value_functions.rs, expectiminimax_player.rs, apply_action_helpers.rs, apply_attack_action.rs, state/mod.rs and observation.rs. The play-out files exist only on 9a0bc5ac.

## 0. Short answer

- **A km-class bot can never decline a knockout.** A point is worth 10,000 in km's score and a turn of clock only 100. So "carry out the plan" (sacrifices and delays included) is for ky3's play-outs to pass, not for the pricing. `_blade` and `_count` make the fast codes value the plan; they can't make them pass up a point.
- **Every gain here is measured against km3 opponents that walk into the Blade.** The honest comparison is the Blade-aware opponent arm from the Kingambit diagnosis (`../pause_positions_kx3_2026-10/KINGAMBIT_PASS_cloud.md`, the gate) once it exists. Until then, every result says which opponent it was measured against.
- **`_blade` (the Blade priced at the current count) is the correct reading of the card and the base for `_count`. It will change almost no km move:**
  - 7 of his 15 plan turns are at count 0, where it changes nothing.
  - Of the other 8, the Blade can become the clock's threat in some reachable board on only 4: 203719 t17 and 010837 t07, t09, t11. On the rest, either a ready Regigigas (Giga Turbo 100, the same as the Blade at count 1) wins the pick, or Pawniard's Kingambit form is charged 2 evolution steps.
  - On all 78 turns it can reach the threat on at most 18.
  - At 010837 t09 and t11 a stronger version on both seats already changed nothing (KINGAMBIT_PASS_cloud.md:88-95).
- **Why pricing can't do it:**
  - No term in km's score reads the count (778-793).
  - km never searches the opponent's turn, which is when fodder falls.
  - A point is worth 10,000 and a turn of clock 100 (47, 56).
- **The play-out bots already do part of the job:**
  - On 80 deck-01 deals, F wins 35, C 38 and km3 12.
  - F and C reach count 2 or more before the first Blade more often.
  - They protect Pawniard no better than km3: 13-15 of about 72 games lose it before it evolves.
  - They are hundreds of times slower, and their play-outs continue with km3.
- **The path:**
  1. `_blade`, then `_count`. `_count` includes an expected-points rule for Pokémon that can deny points, measured separately with a diagnostic code.
  2. Fast codes kmb, kmbc and kmbd screen. The slow ky3_blade_count confirms the best few. ky3_blade gets slow runs only if stage A earns them.
  3. One pilot test, written before any run, on the list he actually plays.

## 1. `_blade`

**The change:**
- A new flag `blade_count` in `EvalFeatures` (351-390). It is false in every existing constant.
- It is read in one place, the damage closure of `kt_clock_stadium` (1754-1760). With the flag on, for an attack whose effect maps (EFFECT_MECHANIC_MAP) to `ExtraDamagePerOwnKnockoutThisGame { damage_per_ko }`, the closure returns the estimate plus `damage_per_ko × state.count_own_knockouts_this_game(owner)`. `owner` is the threat's owner (1753). Every other attack is unchanged.
- The `_ => fixed` arm at 2519 stays as it is, because every tier shares it.
- The switch reaches:
  - the threat pick (1761-1762, including evolution forms at 1350-1366);
  - both clocks (1912-1913).
- It does not reach the online yardstick (3055-3069), which only chooses among one card's attacks.

**Exposure:**
- Only Kingambit B3a 043 has this text.
- It appears in decks/dustin/01 and in his played list (the QR-verified rl/results/pause_games_new_2026-10-13/v2/decks/).
- No panel, pool or gauntlet list has it.

**Where it acts in ky3:**
- km's proposal (playout_player.rs:546, 1000).
- His seat in the play-outs. Lines 946-948 give both seats `PlayerCode::KM` today, so this needs a code per seat, as `_punch` does.
- The cap's ranking (1104), only if `_punch` rewires that call.
- The play-out opponent seat stays plain km3. In a Kingambit mirror both seats would need `_blade` (none is tested).

**Fast code `kmb<N>`:** a new `PlayerCode::KMB`, with a value function using `EvalFeatures::KMB`.
- It is parsed before `km<N>`, which would reject "kmb3" (mod.rs:290-296).
- `kmbc` and `kmbd` are parsed before `kmb`.
- Parse tests show km3 still parses to `KM{3}`.

**Unit tests (each shown failing first):**
1. **Estimate:** 60, 100, 140, 180 at counts 0-3 with the flag; 60 at every count without it.
2. **Whose count:** the opponent at 3 and the owner at 0 gives 60; the owner at 3 and the opponent at 0 gives 180.
3. **The threat pick:**
   - Ready Kingambit (DD) and ready Alolan Muk (DCC): Muk at count 0, Kingambit at counts 1-3.
   - Add a ready Regigigas in an earlier slot: Regigigas at count 0; Regigigas at count 1 too, because the pick keeps the first of a tie; Kingambit at counts 2-3.
   - Without the flag, Kingambit is never picked.
4. **Evolution form:** Pawniard in play, Kingambit in hand, count 2: the form reads 140 and its steps stay 2.
5. **The clock:** his only Pokémon is a ready Kingambit; the opponent has only an Active 180-HP Mega ex (3 points), with no Tool, Stadium or damage cut. `theirs` totals 3, 2, 2, 1 at counts 0-3 with the flag, and 3 without it.
6. **Mirror:** an opposing Kingambit is read at the opponent's count in his `mine` clock.
7. **Identity:**
   - With count 0 on both sides, every value is bit-equal, including deck-01 states.
   - A property test on recorded panel states.
   - km3 keeps `81b572198c04d5d1`, and kmb3 prints the same.
   - ky3_blade prints ky3-with-no-switch's digest (ky3's gate 2 pins that to F's `31d638dbc818b0fa`, which was measured before rules switch 2, so gate 2 must hold first).
8. **Replay:**
   - On the branch build, generate km3's 80 deck-01 deals. The logged Oct 3 games ran before rules switch 2.
   - Then run kmb3 on the same deals. Each game must match until the first deck-01 decision where a Blade candidate at count 1 or more is reachable.
   - Log the first difference and its count, as a firing count.

**Expected:** kmb3 changes km's move on none of the 15 plan turns. The 18 turns where it can fire are listed in EXPECTED_KG.md.

## 2. Pricing alone, or a plan-value term

**Pricing explains none of the 15 plan turns.**
- At 010706 t11, Regigigas has DDD and is ready at 100, and Kingambit can't be ready this turn.
- Not valuing the plan explains 13 of the 15. The other two (014423 t03, t07) may also come from Dede-Circuit being priced at its printed 40.

**So the plan value has to be a term in clock turns.** Declining a knockout can only come from ky3's play-outs.

**`_count`** implies `_blade`. Codes: `kmbc<N>` and `ky3_blade_count`. Diagnostic: `kmbd<N>` (`_blade` plus part 1 only). With the flag on, in `kt_clocks` (1902-1918):

1. **Expected points.**
   - A victim whose live ability is `CoinFlipToDenyKnockoutPoints` counts half its knockout points. "Live" means read by `get_in_play_ability_mechanic`, as the engine does at apply_action_helpers.rs:878-879, so suppression counts.
   - The loop runs until 3 expected points.
   - This covers Glimmora and Dusknoir, his "Pokémon that don't give up points". Alolan Muk silences only Basic Pokémon.
2. **The schedule.**
   - It is taken from the other side's clock computed with `_blade` only, never with its own projection.
   - It uses the same threat and the same hits per victim.
   - The Active falls first, then the Bench in kp's order, with every Blade holder last. Holders are Kingambit, plus Pawniard or Bisharp when a Kingambit is in that side's hand or deck.
   - That clock's own total uses the same order.
   - With no holder in play, the order is kp's.
   - Gusts and Bench damage are ignored. This is a stated limit: at 225319 his Pawniard fell to Bench damage.
3. **The projection.**
   - Hit k is priced at the count now, plus this side's Pokémon knocked out in the schedule on the other side's turns before hit k.
   - Turn order comes from `state.current_player`. If this side is to move and hasn't attacked (km's own-turn leaves, expectiminimax_player.rs:833-905), its turn j comes first; otherwise the other side's does.
   - Knockouts after the other side reaches 3 expected points don't count.
4. **The guard.** If the schedule reaches this side's last holder before the Blade line finishes, there is no Blade credit, and the usual threat is used.
5. **The pick.** A Blade candidate replaces the usual threat when its projected total is smaller. The switch reads the mechanic, never a card name.

**Identity:**
- Bit-equal wherever no Blade candidate is reachable in the clock and no denial holder is in play. That covers every panel, pool and gauntlet list and decks 12 and 13-A.
- Digests: kmbc3 and kmbd3 must print km3's; ky3_blade_count must print ky3's.

**Unit tests (each shown failing first):**
1. **Projection, opponent to move:**
   - Count 2. A ready Kingambit on the Bench. His Active Glimmora is knocked out in one hit by their ready attacker. Their only Pokémon is an Active 180-HP Mega ex.
   - `_blade` alone needs 2 hits; `_count` needs 1.
2. **Projection, own turn:** the same board with him to move and no attack yet: still 2 hits.
3. **Guard:** Kingambit Active and knocked out first: no credit, and the clock falls back to the next threat.
4. **Their win:** their winning knockout adds nothing to his count.
5. **Expected points:** victims Glimmora, Glimmora, Grimer and a fourth Pokémon. Today's 3 points become 2, and `mine` gets longer.
6. **Suppressed denial:** a Glimmora whose ability is suppressed counts a full point.
7. **Pick:**
   - Pawniard (1 Dark) on the Bench, Kingambit in hand, count 2, usual threat Hang Down 20 (missing 1), against a 180-HP opponent: the form is picked.
   - With Pawniard as the Active about to fall, it is not.
8. **Saturation:** once the Blade knocks out every victim in one hit, another fodder knockout changes `theirs` by 0.
9. **Wrong side:** the opponent's own losses never raise his count.
10. **Mirror:** with both sides holding a Blade, each projection uses the other side's `_blade`-only clock, with no circular dependency.
11. **Two holders:** with two Pawniard, the guard fires only at the last one.
12. **Firing log** (this replaces the old bound test):
    - Every decision on recorded deck-01 states where kmbc3's move differs from kmb3's, with the change in the clock term.
    - Every knockout km3 took that kmbc3 drops is read by hand (0 expected).
13. **Identity:** the property test and the digests.

**What can and can't happen ("always sacrifice"):**
- In km, `_count` can change only choices where km3's margin is smaller than the clock shift: who stands in front, where Energy and the Helmet go, promotions.
- It credits only knockouts the opponent's clock would make, and charges each one its expected points.
- Passing a knockout can only come from ky3's play-outs, which must clear their bar: 2 standard errors, or 3 under `_zs3` when km's move is the knockout.

**Not in this path:**
- **`_expo`:** Energy on an Active about to fall still earns the online score at ×500 (+167), against `_count`'s 100 for a turn saved.
- **Two pricing gaps:** Seal of Antiquity and Dede-Circuit.
- **Piece 2, a careful opponent:** measured by stage B0 and the kmb3-opponent arm, not built as a km3 change. This departs from the Kingambit challenge's "add piece 2", so Fable should confirm it.

## 3. The pilot test

**Amendment (Oct 15, after Dustin corrected the plan; see `../../setup_tester/SPEC_AMENDMENT_1.md`).** The plan lines are P2-P5
from that amendment, on his played list:
- P2: both Glimmora had their turn. In a bot game that means each attacked at least once.
- P3: Muk or Pawniard was Active.
- P4: Kingambit ready at the winning moment, in two columns, "knocks out their strongest" and "wins outright".
- P5: the plan was reached before the opponent's third point.

His plan is the reference:
- Regigigas leads as the wall, with Ilima to pull it back.
- Both Glimmora get a turn.
- Muk and Pawniard are never Active.
- Pawniard is benched after the first knockout of his Pokémon and takes two turns to get [DD] and evolve.
- The Blade target is their strongest Pokémon, when knocking it out wins.

Speed ("Kingambit by own turn N") is descriptive only.

Commit `EXPECTED_KG.md` before any run. For each case it records:
- the property and its baseline count for each arm family;
- its class under gate 0's rule: a positive only if that family's baseline meets the property in 8 or fewer of 12 seeds, otherwise a keep check.

**Predictions:**
- kmb3 changes km's move on none of the 15 plan turns.
- kmbc3 changes 210041 t06 and 203719 t07, and perhaps 225319 t06, 210823 t08 and 010837 t09.
- kmbc3 leaves most of the "feed the future" turns unchanged.
- kmbc3 cannot change the three declined knockouts.
- kmbd3 alone moves few or none of the 78 turns.

**Arms:**
- **Fast:**
  - km3, re-run on the branch build; it must match v2/runs_km3;
  - kmb3, kmbc3, kmbd3.
  - All 78 turns, 12 seeds.
- **Slow:** ky3 and ky3_blade_count on 25 turns. ky3_blade only if kmb3 moves a plan turn.
- **Worlds:** ky3_infer and ky3_infer_blade_count on 010837 t03, t09, t11 and 203719 t17. If Fable keeps `_infer` off, those turns are "not exercised".
- **Score dump:** on, print-only.
- **Optional B':** the plan continuation (playout_plan.rs), with his line scripted for 2 turns at the 15 plan turns. It shows whether his line wins once played out.

### (a) His turns

**Positions:** the v3 positions in the v2/ folder, never the v1 positions.

**The 25 slow turns:**
- the 15 plan turns;
- the 6 keep checks;
- 010706 t15, 203719 t13, 210041 t10 and 230258 t13.

020824 t03 and 225319 t04 are report-only, fast arms only.

**Positives (each needs his move upheld by him or by two readers):**
- **Reviewed:**
  - 010837 t03 (his ruling);
  - 203719 t17 (his ruling);
  - 010837 t07 and 225319 t06 (the study);
  - 014423 t07 and 015659 t05 (study v2, confounded);
  - 010837 t09 and t11 (the cloud's diagnosis). These are classified per family: for the `_infer` pair they are likely keep checks.
- **Need a second reader before they count:** 210041 t06, 203719 t07, 210823 t08, 010706 t11, 010837 t05, 014423 t03, 203719 t11.

**Keep checks:**
- His Rare Candy evolutions: 010706 t05, 210823 t06, 230258 t09.
- His knockouts: 010706 t21, 010837 t13, 010837 t15.
- No seed may lose what the baseline had.

**Right to pass:**
- Every correct pass an arm's baseline makes must still be made in every seed.
- Game 3 T4 and deck 13-A G5 T4 are held by identity: their lists have no Kingambit or denial holder.

**Rules:**
- A positive passes at 10 or more of 12 seeds and at least 4 above its baseline.
- **Fast arms:**
  - The 3 declined knockouts (010837 t03, 203719 t17, 010837 t11) are a known limit, reported but not counted. 010837 t09 counts.
  - kmbc3 passes (a) if it passes at least half of its counted positives and loses nothing.
- **Slow arms:** every counted positive applies.

### (b) Self-play

**Deals:**
- His played list (pause-game QR list, read by path) against the 8 floor lists, both seats.
- decks/dustin/01 only as a historical km3 row.
- Seeds: a new block at 20,000,000,000 or above not used by earlier diagnostics, recorded in EXPECTED_KG.md.

**Arms:**
- Fast: 2,000 games each (125 per list and seat) for km3, kmb3, kmbc3, kmbd3.
- Slow: 160 games (the first 10 per list and seat), in two stages of 80, for ky3 and ky3_blade_count.
- The opponent is plain km3, except in the next arm.
- **Blade-aware opponent arm:** kmbc3 and km3 against the panel piloted by kmb3. It is part of the verdict.

**Pairing:**
- Per deal: the mean difference ± 1.96 × sd / √n, seats separately.
- The deals where the two arms didn't go first together (0 expected).
- Slow-pilot games against total games.

**Tooling:**
- A new logger reads `own_knockouts_this_game` through serde JSON (pg_pos.rs:404) and indexes it by deck 01's seat.
- It records: both boards, hand names, the full list of legal moves, knockout events with their cause and the Glimmora coin, and switches with who chose them.
- analyze_kg.py is self-tested on made-up games: deck 01 in seat 1, a denied knockout, an Ilima return, a gust.

**Measures** (scale figures from the 80 deck-01 deals, km3 / F / C):

| | measure | km3 / F / C |
|---|---|---|
| **PL1 (primary)** | per deal: Pawniard reached play and was never knocked out before evolving | 58/80, 57/80, 59/80 |
| **PL2 (primary)** | per deal: the first Blade comes at count 2 or more and knocks out | at most 14/80, 21/80, 28/80 (knockout share to be measured) |
| secondary | count at the first Blade (mean) | 2.0, 2.2, 2.2 |
| secondary | first Blade by own turn 6 and by own turn 8 | to be measured |
| secondary | Dark Energy on Pawniard before it evolves | 5/45, 18/42, 22/42 |
| secondary | fodder share of own knockouts before the first Blade; Glimmora denials | to be measured |
| secondary | plan passes | to be measured |
| secondary | win rate | 12/80, 35/80, 38/80 |

**Guards:**
- **G1:**
  - Fast: the 95% lower bound of (switch − baseline) is above −5 points.
  - Slow: fails only if the 95% upper bound is below 0.
  - Detectable effects are about ±2-3 points fast and ±8-10 slow.
- **G2:** neither of these rises:
  - the opponent's points at the first Blade, on deals where both arms Blade;
  - the share of deals where the opponent reaches 2 points before any Blade.
- **G3:** losses after a plan pass don't rise.
- **G4:** Kingambit made Active at count 1 or less without a knockout, then knocked out the next turn, doesn't rise (km3: 9 of 14 count-1 promotions).
- **G5:** Kingambit with DD on the Bench for 2 or more own turns in a lost game doesn't rise (km3 about 0; its 13 games ending with Kingambit on the Bench had it uncharged).
- **G6 (report only):** Pawniard knocked out on the Bench.

**Verdicts:**
- **"Pilots Kingambit better, against bot opponents":** all of these hold:
  - PL1 and PL2 both rise with the paired 95% interval above 0;
  - no guard fails;
  - part (a) passes;
  - the rise keeps its sign against the Blade-aware opponent arm.
- **Does not count:**
  - a higher win rate with PL1 and PL2 flat (F − km3 is +20.4 ± 5.8 pooled over the development decks);
  - PL2 up while G2 or G3 fails;
  - PL1 up through G5;
  - any lost keep check or correct pass;
  - positives counted before their review.
- **Fit to screen:**
  - kmbc3 passes (a) and (b) against km3;
  - its PL1 and PL2 differences have the same sign as ky3_blade_count's;
  - stage D's rank check agrees.

## 4. Build and cost

**Branch:** `sonnet/ky3-blade`, cut from sonnet/ky3-pilot after item 1 (or after `_punch`). One commit per item, tests first, each shown failing:
1. `_blade`, kmb, the `_blade` suffix, and tests 1-8.
2. `_count`, kmbc, kmbd, the `_count` suffix, and its tests 1-13.
3. The logger and analyze_kg.py, with self-tests.
4. EXPECTED_KG.md, including the second reader's verdicts.

**Then STOP.** The laptop reviews the diffs and Fable audits that review. The ky3 brief's rules apply:
- no `DECKGYM_*`;
- no change to strength main.rs or the slow-report pin;
- km3's digest unchanged;
- push only to the branch;
- no frames or videos.

**Build effort:** about 2.5-3.5 days of Sonnet work and $30-70 in API credits.

**Runs:**

| stage | what | sandbox-hours |
|---|---|---|
| A | km3 re-run plus 3 fast arms on 78 turns; 6 × 2,000 games | 3-4 (under an hour on the laptop) |
| B0 | the continuation gate at 010837 t09 and t11 | 2-5 (estimate) |
| B | 18 new ky3 runs, 25 ky3_blade_count runs, 8 `_infer` runs, self-checks at 2.2 each | 14-30 |
| B' (optional) | the plan continuation | 3-7 |
| C | 2 slow arms × 160 games | 38-50 |
| D (Dustin's word) | rank check: 3 variants × 160 slow games, plus fast games | 57-75 |
| setup | | about 3 per worker |

- **Total:** about 60-95 sandbox-hours ($5-9) without D, or 120-170 ($11-15) with D.
- **Staging:** each stage runs only if the one before passes. Stage A answers within hours whether kmbc3 moves toward his plan.

## 5. What this unlocks

**Speed:** km3 plays about 6 deck-01 games a second on the laptop (1,920 in 312 seconds). Assume kmbc3 takes 1.2-1.5 times as long until stage A measures it.

**The screen, only after a pilot passes, including D:**
1. **First look:** 320 games per variant against his played list, about ±6-8 points. That is roughly 1,000-1,400 variants a day on the laptop. Cloud cost is unmeasured.
2. **Second look:** the top 30 at 2,000 games each on fresh deals, about ±3 points.
3. **Confirmation:** the top 3-5 with ky3_blade_count at 160 deals, about 19-25 sandbox-hours each.

**Limits:**
- The opponents are 8 public lists played by km3, which walks into the Blade.
- Mega Rayquaza, Dedenne, Mega Pidgeot, Starmie, Gardevoir/Diancie and Falinks are missing.
- Under 5 points is noise.
- Variants come from cards he owns or can get; denial-holder variants such as Dusknoir are covered by the mechanic.
- Making kmbc3 the screener is Dustin's decision.
- Until a pilot passes, deck-01 bot scores stay labelled "the bot can't carry out this deck's plan".

## Flags

- **Rare Candy:** Pawniard's Kingambit form is charged 2 steps (1354, 1361).
- **010837 t03:** km3 Slashes in 2 of 12 seeds (the runs), not 4.
- **Deck lists:** the 80 self-play games used decks/dustin/01, not his played list.
- **G5's baseline is corrected.**
- **Not yet answered:** PL2's knockout share and the turn-6 and turn-8 Blade counts need the logger. F's and C's causes at 203719 t17 and 010837 t03 need the score dump.

---

