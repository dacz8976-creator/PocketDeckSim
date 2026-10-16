# EXPECTED_KG.md: what ky3 item 7's pilot test expects, written before any run (Oct 16)

`KINGAMBIT_ITEM7.md` section 3, item 4 of section 4. Committed before any arm is run. It fixes: the case list, each case's property and
baseline for each arm family, its class under gate 0's rule, the 18-turn firing list, the predictions, and the seed block. Nothing here was
measured by a new run; every baseline is read from committed files, and the ones that don't exist yet say so.

**Positions** are the v3 positions (`pause_games_new_2026-10-13/v2/`, `positions_all.json`), never the v1 ones: 78 turns in the 12 games with
a Kingambit deck (010706, 203719, 210041, 210823, 225319, 230258, 010003, 010837, 014423, 015011, 015659, 020824; 022530 and 030351 are
Haxorus decks and are left out). Pause-game decks: `v2/decks/`. His played list is `73dfed58d1d6`; the 12 games' deck files carry it, read by path.

## 1. Seeds

- **Part (a), the turns:** the position runner's own seeds 1-12, as in every earlier position study, so a switch and its baseline play the same
  deals and km3's re-run must equal `v2/runs_km3/` turn for turn. These are small integers, not game seeds, and none of the tables below uses them.
- **Part (b), self-play: a new block, 25,000,000,000 - 25,099,999,999.** Per list under test X (0 = his played list, 1 = `decks/dustin/01-muk-glimmora-kingambit-regigigas.txt`,
  the historical km3 row), opponent o (1-8, the eight floor lists `decks/screen/opponents/t-*.txt` in file order), seat S (the list under test in
  seat 0 or 1) and deal i: **seed = 25,000,000,000 + X x 10,000,000 + o x 1,000,000 + S x 500,000 + i**, i < 500 (the fast plan needs i < 125).
  The slow arms use i < 10 per list and seat (stage 1 i < 5, stage 2 i = 5-9). The Blade-aware opponent arm replays the X = 0 deals. Smokes:
  25,090,000,000 and up. Every arm of one deal uses the same seed, so arms pair.
- **Checked against** (a) `START_HERE.md`'s seed table: its highest row is 24,601,000,000 - 24,699,999,999 (the slow-report slots); its rule is
  "new blocks go above the last one used". (b) Claude Code's earlier diagnostics: the table's 20,000,000,000+ row and the rows listed under it,
  all of which end at 24,699,999,999. (c) A search of `origin/main`, `origin/sonnet/ky3-pilot` and `origin/sonnet/ky3-blade` (md, py, sh, rs files) for any number of 25,000,000,000 or more: the only hits are 26,092,500,001 and 26,092,500,002, the Sept 25 Limitless event split's
  Python seeds. They are outside this block and are not game seeds. No file uses 25.0B-25.099B.
- **`START_HERE.md` is not edited here** (it is a shared instruction page). The coordinator adds the row: 25,000,000,000 - 25,099,999,999,
  "ky3 item 7 self-play (Kingambit pilot test), formula above".

## 2. Classes: the rule and the families

Gate 0's rule: **a case is a positive only if the family's baseline meets the property in 8 or fewer of 12 seeds; otherwise it is a keep
check.** Positives pass at 10 or more of 12 and at least 4 above baseline. Arm families:

- **km family** (km3, kmb3, kmbc3, kmbd3). Baseline: km3's 12 committed free runs (`v2/runs_km3/out_*.jsonl`), the plan up to its cut. The branch
  re-run of km3 must reproduce them. Counts below are from those files.
- **slow family** (F = frozen kx3, C = the candidate, and ky3 with no switch, which is what ky3_blade_count is compared with). Baselines exist
  only for the eight positions of the kx3 position study (`pause_positions_kx3_2026-10/workers/P8/` and `P8_v3/`, seeds 1-12). **ky3 with no
  switch has not been run on any of them: its baseline is "gate 0, not yet measured", and its class is decided there.** Where F or C is known the
  table gives it as a guide; it does not replace gate 0.

Plans are cut at the first draw card or the end of the turn. A property that is "no X" is met by a plan that is cut before X could appear; the
cut count is given where it matters (010837 t03).

## 3. The cases

`count` is his own knock-out count at the start of the turn (`me.knockouts` in the position). Baselines are "turns met / 12 seeds".

### 3a. The 15 plan turns (his plan, section 3 of the brief)

| # | turn | count | group | property (his move) | km3 | F | C | km class | slow class | prediction |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 010837 t03 | 0 | reviewed, his ruling | no Slash this turn (Pawniard retreats instead of knocking out the Pichu) | 10/12 (10 plans are cut at the Copycat draw; Slash in 2) | 12/12 (7 cut) | 12/12 (9 cut) | **keep check** by the rule (10 > 8). Declined knock-out: reported, not counted | not run (C/F: keep) | none of kmb3/kmbc3/kmbd3 changes it |
| 2 | 203719 t17 | 1 | reviewed, his ruling | no Overlord's Blade (the exact-100 knock-out on Drampa is declined, Glimmora falls to grow the Blade) | 0/12 (Blade 12/12) | 11/12 (v3) | 12/12 (v3) | **positive**. Declined knock-out: reported, not counted | F, C: keep checks; ky3: gate 0 | not changed by any fast code |
| 3 | 010837 t07 | 1 | reviewed, study | the turn's Energy goes on the Glimmet (@2), not the Kingambit | 0/12 (Kingambit @1, 12/12) | n/m | n/m | **positive** | gate 0 | kmb3 no; kmbc3 perhaps no |
| 4 | 225319 t06 | 1 | reviewed, study | no Slash: Pawniard takes the Energy and retreats | 0/12 (Slash 12/12) | n/m | n/m | **positive** | gate 0 | kmb3 no; kmbc3 perhaps |
| 5 | 014423 t07 | 1 | reviewed, study v2, confounded | the Energy goes to the benched Pawniard (@1), not the Active Regigigas | 0/12 (@0 12/12) | 0/12 (6 end turn) | 0/12 | **positive** | F, C: positive | `_expo` case: no change from any code here |
| 6 | 015659 t05 | 0 | reviewed, study v2, confounded | the Energy goes on the newly placed Pawniard (@3) | 0/12 | 0/12 (v3) | 1/12 (v3) | **positive** | F, C: positive | `_expo` case: no change from any code here |
| 7 | 010837 t09 | 2 | reviewed, the cloud's diagnosis | no Blade: Hang Down after Pops (the Blade is 140, the Kangaskhan 180) | 0/12 | 0/12 | 11/12 | **positive**, counted in fast arms | F: positive; C: keep check | kmbc3 perhaps; kmb3 no |
| 8 | 010837 t11 | 2 | reviewed, the cloud's diagnosis | no Blade: Hang Down, the Pichu knock-out declined | 0/12 | 0/12 | 12/12 | **positive**. Declined knock-out: reported, not counted | F: positive; C: keep check | not changed by any fast code |
| 9 | 210041 t06 | 0 | second reader: agree (counts) | no Ilima this turn; the Energy goes on the benched Pawniard | 0/12 (Ilima 12/12) | 0/12 | 0/12 | **positive** | F, C: positive | **kmbc3 changes it**; kmb3 no |
| 10 | 203719 t07 | 0 | second reader: agree (counts) | no Blade (Glimmora promoted, Kingambit stays out) | 0/12 | n/m | n/m | **positive** | gate 0 | **kmbc3 changes it**; kmb3 no |
| 11 | 210823 t08 | 0 | second reader: agree (counts) | no Blade (Glimmora promoted) | 0/12 | n/m | n/m | **positive** | gate 0 | kmbc3 perhaps; kmb3 no |
| 12 | 010706 t11 | 1 | second reader: agree (counts) | Heavy Helmet on the Kingambit (@1) | 0/12 (Muk @0 12/12) | n/m | n/m | **positive** | gate 0 | no change from any code here (the Helmet is not priced by the Blade) |
| 13 | 010837 t05 | 1 | second reader: agree (counts) | the Energy goes on the benched Pawniard (@1) | 0/12 (Regigigas @0 12/12) | n/m | n/m | **positive** | gate 0 | no change expected |
| 14 | 014423 t03 | 0 | second reader: agree (counts) | the Energy goes on the benched Pawniard (@1) | 1/12 (@0 in 8; 2 plans are cut before an attach) | n/m | n/m | **positive** | gate 0 | `_expo` case: no change from any code here |
| 15 | 203719 t11 | 0 | second reader: agree (counts) | Heavy Helmet on the Kingambit (@3) | 0/12 (Helmet @0 12/12) | n/m | n/m | **positive** | gate 0 | no change expected |

"n/m" = not measured (F and C ran only the eight kx3-study positions). Seven of the 15 are at count 0 (cases 1, 6, 9, 10, 11, 14, 15).

**The seven former "pending second reader" cases** are 9-15. The first reading is `FIRST_READ_7.md` (all seven: upheld; confidence from
medium-high to low-medium; case 14 is high but is an `_expo` case, not a Blade one). The second reading, `SECOND_READ_7.md`, was written
before the first was opened (Sonnet worker, Oct 16). Per turn, the class is the same in both, **agree, all seven count** (none is
"unclear" or "km3 better", so the counted list and kmbc3's denominator are 12):

| case | turn | first reader | second reader | result |
|---|---|---|---|---|
| 9 | 210041 t06 | upheld, medium | positive, medium-low | agree (counts) |
| 10 | 203719 t07 | upheld, medium | positive, medium-high | agree (counts) |
| 11 | 210823 t08 | upheld, medium | positive, medium-high | agree (counts) |
| 12 | 010706 t11 | upheld, medium-high | positive, medium | agree (counts) |
| 13 | 010837 t05 | upheld, low-medium | positive, medium-high | agree (counts) |
| 14 | 014423 t03 | upheld, high (`_expo`) | positive, medium-high (`_expo`) | agree (counts) |
| 15 | 203719 t11 | upheld, medium-high | positive, medium | agree (counts) |

The classes agree; some reasons differ, for the laptop's review. Neither reading changes a class:
- Case 9: the first reader has km3 promoting the Pawniard after Ilima and losing it; the second reader did not consider that and reads Glimmet
  or Muk as the victim (Muk in front being what Dustin says loses). Both end at "the Regigigas is the cheaper loss".
- Case 15: the first reader reads the Energy as going on the Glimmora ("@1"); the second reader reads "@1" as board index 1, the Muk (the
  same convention gives the Kingambit for "@1" in 010706 t11). Both rest the case on the Helmet alone, which is the property.
- Case 12: the Peculiar Plaza/Helmet-does-not-save-Muk reading is the first reader's; the second reader reached the same Muk fall from
  Mega Diancie ex's Brilliant Storm and did not use the Stadium.

**Case 1 and the rule.** Dustin ruled this pass deliberate, so it was listed as a reviewed positive. By gate 0's rule as written it is a keep
check for the km family: km3 does not Slash in 10 of 12, only because 10 of its plans are cut at Copycat before the choice (his own line puts
Copycat after the retreat). Read as "Retreat:1 appears before the cut" the baseline is 0/12. I kept the "no Slash" property because it is the
decision the ruling was about; the verdict rule counts case 1 as a known limit in the fast arms either way, so no pass or fail turns on it.

### 3b. Keep checks (the baseline already passes; no arm may lower it)

| turn | count | property | km3 | slow |
|---|---|---|---|---|
| 010706 t05 | 0 | Rare Candy, then Evolve:Kingambit | 12/12 | gate 0 |
| 210823 t06 | 0 | Rare Candy, then Evolve:Kingambit | 12/12 | gate 0 |
| 230258 t09 | 1 | Rare Candy, then Evolve:Kingambit | 12/12 | gate 0 |
| 010706 t21 | 3 | Overlord's Blade attack (the winning knock-out) | 12/12 | gate 0 |
| 010837 t13 | 3 | Overlord's Blade attack | 12/12 | gate 0 |
| 010837 t15 | 3 | Overlord's Blade attack | 12/12 | gate 0 |

### 3c. The four other slow turns, and the two report-only turns

The four are in the slow set because the Blade is reachable there but km3 already plays his whole line, so they are keep checks:

| turn | count | property (his line) | km3 |
|---|---|---|---|
| 010706 t15 | 1 | Evolve:Glimmora, Attach, Sludge Bomb | 12/12 |
| 203719 t13 | 1 | Place:Glimmet, Attach@2, Venomous Hit | 12/12 |
| 210041 t10 | 2 | Evolve:Glimmora, Attach@0, Venomous Hit | 12/12 |
| 230258 t13 | 2 | Attach@0, Venomous Hit | 12/12 |

**Report-only, fast arms only:** 020824 t03 (count 0; his first step Evolve:Glimmora, km3 benches Pawniard first, 0/12) and 225319 t04
(count 0; his first step Heavy Helmet, km3 starts with Mesagoza, 0/12). No class.

### 3d. Right to pass, identity

Every correct pass an arm's baseline makes must still be made in every seed. Game 3 T4 and deck 13-A G5 T4 are held by identity (no Kingambit
and no denial holder in their lists). Part (a) also counts, over **all 78 turns**, the turns where an arm's first move or plan differs from
km3's: baseline 0 by definition, and every change is read by hand.

## 4. The 18 turns where kmb3 can fire

**Rule used (mine, written from the code at `value_functions.rs` `threat_candidates` and `evolution_targets`).** A turn is listed when
(i) his count is 1 or more (at count 0 the Blade is 60, its printed value, so `_blade` is bit-equal), and (ii) in some board km can reach
in his own turn (one Energy attach to any Pokémon, a Rare Candy evolution when Rare Candy and Kingambit are both in hand, a different Active),
the Blade, priced at the count, becomes the clock's threat: the first attack with the fewest missing Energy, then the most damage, ties kept
by slot. Forms are read from his deck and hand, so a Pawniard with Kingambit still in either counts, charged 2 evolution steps. A ready
Regigigas (Giga Turbo 100) wins a tie with the Blade at count 1 unless the Kingambit sits in an earlier slot.

**The 17 turns this rule finds** (count in brackets; * = also one of the 25 slow turns):

| game | turns |
|---|---|
| 010706 | t13 (1), t15* (1), t17 (2), t19 (2), t21* (3) |
| 203719 | t13* (1), t15 (1), t17* (1) |
| 210823 | t10 (1), t12 (1) |
| 230258 | t11 (1), t13* (2) |
| 010837 | t07* (1, via Rare Candy), t09* (2), t11* (2), t13* (3), t15* (3) |

Of the plan turns only 203719 t17 and 010837 t07, t09 and t11 appear, which is what the brief says (4 of the 8 plan turns with a count). The
other four (225319 t06, 014423 t07, 010837 t05, 010706 t11) are where Pawniard's form pays 2 steps or a ready Regigigas wins.

**Count: 17, not 18.** The brief says "at most 18". I could not reproduce the eighteenth with this rule. Near misses that a looser reading of
"reachable" might add: 010706 t09 (Regigigas [DD] Active, Kingambit empty; Giga Turbo and Blade tie at 100 only if the attach goes to
Regigigas), 010706 t11 (Kingambit empty, Regigigas [DDD] ready), 230258 t09 (Rare Candy and Kingambit in hand, but Pawniard has no Energy and
Glimmora is already ready), 225319 t06 and 014423 t07 (form charged 2 steps). **The firing count of unit test 8 is what settles the list**: it
logs every deck-01 decision where a Blade candidate at count 1 or more is reachable, and this table is replaced by that count, with the
difference stated, when it runs. The prediction below does not depend on whether the list is 17 or 18.

## 5. Predictions (from the brief, recorded before any run)

- **kmb3** changes km's move on **none** of the 15 plan turns. Its firing count over the 78 turns is at most the 17-18 above.
- **kmbc3** changes **210041 t06 and 203719 t07**, and perhaps 225319 t06, 210823 t08 and 010837 t09.
- kmbc3 leaves most of the "feed the future" turns unchanged (cases 3, 5, 6, 12, 13, 14, 15).
- kmbc3 **cannot change the three declined knock-outs** (010837 t03, 203719 t17, 010837 t11): reported, not counted.
- **kmbd3** alone moves few or none of the 78 turns.
- Cases 5, 6 and 14 are `_expo` cases (the Energy goes on a doomed Active); a failure there is not a failure of `_blade` or `_count`.
- Fast-arm pass for kmbc3: it passes (a) if it passes at least half of its counted positives and loses nothing. Counted positives today are
  cases 3, 4, 5, 6, 7 (case 7 = 010837 t09) and the pending cases 9-15 **only once each has its second reader**; cases 1, 2 and 8 are not counted.
  With the pending seven undecided the counted list is at most 12, and "half" is read on the list that stands when the arm is scored.

## 6. Arms and what each one is compared with (copied from the brief, not changed)

- **Fast:** km3 (re-run on the branch build, must equal `v2/runs_km3`), kmb3, kmbc3, kmbd3; all 78 turns, seeds 1-12.
- **Slow:** ky3 and ky3_blade_count on the 25 turns above (15 + 6 + 4); ky3_blade only if kmb3 moves a plan turn.
- **Worlds:** ky3_infer and ky3_infer_blade_count on 010837 t03, t09, t11 and 203719 t17; if `_infer` stays off, "not exercised".
- Part (b) self-play: his played list against the eight floor lists, both seats, 2,000 games per fast arm, 160 per slow arm in two stages of
  80, plus the Blade-aware opponent arm; measures PL1, PL2 and guards G1-G6 as in the brief.

## 7. Limits stated now

- All km baselines are from `runs_km3` on the Oct 14 build (v3 positions). The branch's km3 re-run replaces them if it differs, and any
  difference is reported before an arm is read.
- F and C baselines are on eight positions only, and only 203719 t17 and 015659 t05 use the v3 runs (the other six positions are identical
  in v3 per the study's own note).
- The 17-turn list rests on a hand rule over the position records, not on engine output; see section 4.
- Cases 9-15 now carry two readers (`FIRST_READ_7.md`, `SECOND_READ_7.md`), agreeing on all seven. Neither reader saw a frame or the opponent's hidden hand.
