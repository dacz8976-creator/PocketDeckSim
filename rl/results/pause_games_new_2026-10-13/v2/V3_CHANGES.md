# Positions v3 (Oct 14): the fixes for the laptop's review of the 92 positions

Sonnet ("Opus agents progress"), branch `sonnet/positions-v3-2026-10-14`, from main 373b41a6. The review is `REVIEW_POSITIONS_laptop.md` in this folder (three blockers, nine majors, one runner bug, about 38 minors). This note says what was fixed, what changed in the 92 positions and the reads, and what is **not** done.

## Result

- **Every blocker and major of the review is fixed in the converter, the normaliser or the deck reader, with a test written first for each** (the new tests fail on main's code and pass on the new code). `review_fixes_check.txt`: **67 of 67 checks pass** (`scripts/check_review_fixes.py`, run again at the end of `run_all.sh`).
- **52 of the 92 positions changed, 40 are identical** (`v3_position_changes.txt`: every changed field of every changed position, old → new). By field: opponent next Energy 18, his plan 17, opponent Bench cards 22, his board 11, opponent hand count 10, opponent discard 4, notes 27.
- **The converter change alone leaves the 125 Oct 12 positions byte-for-byte as they were** (all 24 games re-converted into a temporary folder with main's converter and with the new one: 0 of 125 differ). The Oct 12 files in the repo were not touched.
- Tests: converter **143** (97 before, 46 new), normaliser **28** (new file `scripts/test_normalize_ledger.py`; 2 of them read the real ledgers when Recording_QA is on the machine: every recorded correction applies to its ledger, and 022530's deck settles Dratini).
- The full chain was run again (`scripts/run_all.sh`: convert, km3 on `pg_pos_F_cond` seeds 1-12, forced replays, older engine, state check, deck check, position cards, tables). `DECKGYM_*` unset; no engine or Rust change.

## The findings and what was done

| review | fix | positions that changed |
|---|---|---|
| **Blocker 1**: 015011's nested Bench `{position, pokemon}` dropped | `instances()` (converter) and `inst()` (normaliser) unwrap the entry, take the outer position when the Pokémon has none, skip `null` | 015011 t01 (Alolan Grimer), t03 (Regigigas, Grimer; the opponent's Tyrogue) |
| **Blocker 2**: 030351's Darkrai B1 154 instead of B2b 040 (HP filter on the Starting-Plains HP) | `cardlib.hp_boost()` reads the +HP of a Stadium or Tool from its database text (Starting Plains: Basic +20, Elegant Cape: Stage 1 +30, Leaf Cape, Giant Cape); a card fits when printed HP + boost is the HP shown (else, when the printed HP is the HP shown although a boost would apply, as a weaker fit); the ledger's "printed N HP" text narrows further. Used for the opponent's cards, his own cards, the cards that left the board and his stack cards | 030351 t09, t11, t13, t15: both Darkrai are B2b 040 |
| **Blocker 3**: 022530's Dratini A3b 051 instead of B4 116 | `deckspec.entry_entity()` reads `semantic entity N` from the strings the file uses; `normalize_ledger.py` builds the list from the packet's QR and snapshot (they AGREE) when the file's own list leaves an entry open and both files exist | 022530 t03-t11 (his Dratini; the deck file `KW261013_022530000.txt` now lists 2 Dratini B4 116) |
| **Major 1**: opponent next Energy fell back to his deck's Energy (18 positions) | `opp_energy_next()`: the zone's circle at the turn start, else the `next` circle on the same row after his turn, else his next row (its this-turn circle or the Energy he attached from the zone), else the only type his zone ever shows in the game; only then the deck's Energy, and a note says so | 010706 all 11 (Psychic), 010003 all 6 (Water / Lightning), 203719 t17 (Lightning) |
| **Major 2**: no Promote step and wrong slots after Ilima | Ilima empties the slot of the Pokémon it returns; `Promote:0@k` (the one named after "promotes", or in the next promotion row, or the only one on the Bench); a Pokémon he benches goes to the first empty slot, as the engine's `Place` does; a promotion that is not told cuts the plan at that step | 203719 t07, 210823 t08, 020824 t11 (the forced replay now runs the whole line in all three) |
| **Major 3**: `stadium_activation` dropped | `nk()` maps it to `ability` (a `UseStadium` step) | 210041 t08, 210823 t02, t04 |
| **Major 4**: Giga Turbo's Energy target | the Turbo Shark block now covers every attack whose text takes an Energy from the zone to a Benched Pokémon; the type comes from the card text ([C] Colorless, [W] Water) | 010706 t09, 230258 t11, 010003 t09 |
| **Major 5, 6, 9** (Codex misreadings settled from frames or the ledger's own numbers) | recorded corrections, see the next section | 210823 (6), 015659 t05-t13, 022530 t03-t11 |
| **Major 7**: Dragon's Blessing's Energy choice | an Ability play that takes an Energy of a named type from the discard gets the step `AttachTypedFromDiscard:<Type>@<slot>` | 022530 t09 (Fighting onto the Active); the same step appears in 030351 t05, t07, t09, t11, t13, t15 (Metal) |
| **Major 8**: "No Basic found" Poké Ball kept as his first move | `NOTHING_FOUND` reads "no basic" | 010706 t15 (the plan now starts with the evolution, and km3 plays all three steps in 12 of 12 seeds) |

## Recorded corrections (frames and the ledger's own numbers)

`scripts/ledger_corrections.json`: each entry has an id, the operation, the reading the ledger has now (`was`, the correction is refused on a ledger that says something else), the note that goes into the notes of the positions it covers (as "ledger corrected from the frames: ..."), and the evidence (the review's table and the frame names). `normalize_ledger.py` applies them to its **copy** of the ledger and writes them into it as `corrections`; the Recording_QA files are never edited. An entry that changes nothing is an error.

| id | what | evidence |
|---|---|---|
| `210823-meowth-left-bench` | the opponent's left-Bench "Alolan Meowth" is a Meowth B2 124 / B2 204 (Carefree Steps, Feelin' Fine, 50 HP) | review: `t0047.00_top.jpg`, `t0085.50_top.jpg` |
| `015659-opponent-hands` | his hand at the opponent's turns 5 / 7 / 9 is 6 / 7 / 6 | review: `t0114.50_top.png`, `t0157.80_top.png`, `t0208.80_top.png` |
| `015659-no-rare-candy-turn-4` | the opponent's turn-4 Rare Candy did not happen (Mega Lucario ex is a Stage 1); the play becomes an evolution, so no Rare Candy is in his discard (t05-t13) | same frames |
| `022530-elegant-cape` | the opponent's Tool is Elegant Cape B3b 065, not Giant Cape | the ledger's HP numbers (Scyther 70, Mega Scizor ex 230); review frames `t0190.00.jpg`, `t0217.00_top.jpg` |
| `010706-opponent-hands`, `203719-opponent-hands`, `225319-opponent-hand` | the opponent hand counts the review's table gives for the frames (010706 t03 / t05 / t07: 6 / 7 / 8; 203719 t07 / t09 / t11 / t13: 4 / 3 / 4 / 4; 225319 t08: 4) | review table |

I did not look at any frame myself; the corrections are the review's. Two frame facts from the review's table are **not** carried: 030351's phantom Fighting on "the second Igglybuff" at t13 and t15 (the ledger has two Igglybuff, each with 1 Fighting, and the review does not say which one: it needs the frames), and 015659's unlogged hand changes in turns 10-12 (the left-out t11 stays out, as the review accepts it as open).

## What changes for the earlier reads

- **km3, free run** (`km3_TABLES.md`, `POSITION_TABLE.md`, `km3_summary.json`): positions where it agrees with his first move / differs / splits 55 / 28 / 5 → **57 / 26 / 5**; same plan in at least 10 of 12 seeds 29 → 31. The 52 changed positions' runs are in `runs_km3/`; the 40 others are identical. Readings that moved: 015011 t01 (km3 plays the Poké Ball in **11 of 12** seeds; it was 8, judged on a board without the Bench), 015011 t03 (it starts with Heavy Helmet in 12 of 12), 010706 t15 (km3 now plays his whole line), 210823 t02 (Copycat 8, Research 4; Mesagoza is gone), 210823 t04 (modal plan now includes the Alolan Muk evolution), 022530 t01 (the deck changed: the first-move spread moved).
- **Forced replays** (`runs_forced/`): 210823 t08 no longer counts among the positions where "km3 plays every step" (it parts at the promotion); 010706 t15 now does. The count of positions where km3 plays all of his line is 37 before and after (one out, one in); positions that deviate at some step: 51 before and after. 203719 t07, 210823 t08 and 020824 t11 are replayed to the last step. 210823 t04's step comparison is aligned (the Mesagoza flip is its own step).
- **The kx3 position study, part 2** (`../../pause_positions_kx3_2026-10/READING.md`): **203719 t17** now has the opponent's next Energy Lightning (it was Darkness) and **015659 t05** the opponent's hand 6 with no Rare Candy in his discard; both need their runs repeated. The other six positions there (010837 t03, t09, t11; 014423 t07; 210041 t06; 020824 t11's first move) are identical to what they were. I did not repeat any kx3 run.
- **`PAUSE_GAMES_2026-10-13_READ_v2_sonnet.md`** is left as it was (it is the record of v2). Its statements about 210823 t08 ("Giga Turbo", "km3 plays every step"), 203719 t07 and 020824 t11 (the converter slips) are superseded by `POSITION_TABLE.md` of this folder.

## Not done (and who)

- **The Starting Plains HP in `pg_pos.rs` (030351 t11, t13, t15): the Opus cloud's.** The positions are right; the runner gives his damaged Basics +20 HP at the first action. km3's reads of those three positions stay untrustworthy until it is fixed. `check_state_dump.py` still does not compare HP.
- **The typed label of the Energy choice: one line in `rl/strength/src/main.rs` `label()`** (Rust, so not mine). It names every `AttachTypedFromDiscard` choice without its type. The converter now writes the step as `AttachTypedFromDiscard:<Type>@<in_play_idx>` (for example `AttachTypedFromDiscard:Fighting@0`), which is what a label `format!("AttachTypedFromDiscard:{:?}@{}", energy_type, in_play_idx)` would give. Until then `forced_runs.py` cuts the line at that step when the discard holds several types (022530 t09: Frenzied Blade is not replayed; the cut and its reason are in `runs_forced/forced_summary.json`) and drops the step when the engine took the only type by itself (030351 t05, t15).
- **Not touched, minors of the review**: Energy discarded with a Pokémon Ilima returns; the Rainbow Cave / Shuckle ex / Fragrant Forest discard entries; the checkup restore giving Druddigon 2 Metal where the text says 3; the opponent printings that are flagged, not stated (Pidgey in 210823, Ralts and Kirlia in 010706, Combee, Varoom, 203719's Dratini); `his_plan_ended` false where the turn ended in a prompt response; opponent names and results missing in `games_meta.json`; his Glimmora in 014423. 015659's t10-t12 hand question stays open.
- The forced replay picks the first empty Bench slot for a `Place` step, km3 often another one (020824 t11: 1 against 3), which shows as a disagreement at that step although the slot is not a choice of strategy. Unchanged from v2.

## Files

`positions_all.json`, `decks/`, `games_meta.json`, `position_list.*`, `report_convert.json`, `deck_from_qr_check.txt`, `runs_km3/`, `runs_forced/`, `km3_summary.json`, `km3_TABLES.md`, `report_out.txt`, `position_cards.txt`, `POSITION_TABLE.md` (regenerated; `engine_comparison.txt`, `state_dump_check.txt` and `deck_assumption_check.txt` come out identical); new: `V3_CHANGES.md`, `v3_position_changes.txt`, `review_fixes_check.txt`; scripts: `normalize_ledger.py` (rewritten as functions, same output on every packet except the ones above), `ledger_corrections.json`, `test_normalize_ledger.py`, `check_review_fixes.py`, `compare_positions.py`, `forced_runs.py` (typed step), `make_table.py` (the readings of the changed positions), `run_all.sh`. The converter, deck reader and card library are in `../../pause_games_new_2026-10-12/harness/` (`ledger_to_positions.py`, `deckspec.py`, `cardlib.py`, `test_ledger_to_positions.py`).

```
cd rl/results/pause_games_new_2026-10-12/harness && python3 -B -m unittest test_ledger_to_positions     # 143
cd rl/results/pause_games_new_2026-10-13/v2/scripts && python3 -B -m unittest test_normalize_ledger     # 28
bash rl/results/pause_games_new_2026-10-13/v2/scripts/run_all.sh                                          # regenerates everything, ends with the 67 checks
```
