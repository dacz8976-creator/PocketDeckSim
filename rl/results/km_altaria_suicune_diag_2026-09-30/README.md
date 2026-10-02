Decision this informs: none. A bounded diagnosis the laptop asked for (via Dustin, Sept 30): which decisions changed behind Suicune's gain in km's Altaria v Suicune cell. Nothing gates on it and nothing is re-read. km was adopted "unconfirmed" on Sept 30 (main 9dda21a, `../km_tables_2026-09-30/READING.md`, line 87).

Seeds: the table's deals only, table pairing 4 (Altaria v Suicune): 72,000,000 + 40,000 + i; even i puts Altaria in seat 0. No new seed block and no new table game: the trace replays 40 of kta3's committed games.

# Altaria v Suicune under km3: what changed behind Suicune's gain

## In plain words

- **Suicune's gain comes from one habit.** When Altaria's Training Area is in play with a Stage 1 Pokémon in Altaria's Active Spot, km3 on Suicune's side removes Training Area. In the 28 deals that swing to Suicune, that Active was Mega Altaria ex in 22 and Espeon in 5. km3 removes it:
  - either by playing its own Stadium, Soothing Shore, which replaces it;
  - or by playing Field Blower on it.
- kta3 doesn't do this. In the 28 deals that swing to Suicune, this is the first decision that changed in every one: 14 Soothing Shore and 14 Field Blower, and every Field Blower was aimed at the Stadium.
- **Why km3 does it: Suicune's own pricing of Altaria's Stage 1 bonus.**
  - Mega Altaria ex is a Stage 1 Pokémon, so Training Area adds +10 to its attack against Suicune's Active.
  - Its Mega Harmony does 40, plus 30 for each of Altaria's Benched Pokémon. With three on the Bench that is 130: two hits on a 140-HP Suicune ex or Baxcalibur. With Training Area's +10 it is 140: one hit.
  - km3's clock counts that bonus and kta3's doesn't. In 21 of the 28 deals, at the changed decision, km3's clock says Altaria knocks out Suicune's Active in 1 turn where kta3's says 2. The three-on-the-Bench reading comes from these clocks: 2 hits and 1 hit on 140 HP mean exactly 130 damage.
  - In 5 more, km3's clock is 1 or 2 turns shorter (4 of them with Espeon Active, 1 with Mega Altaria ex).
  - In 2 (Igglybuff and Espeon Active), no clock changes at that decision itself. There the difference comes from positions further down km3's search.
  - Removing Training Area gives back the turn.
  - In 38 of the 40 traced decisions, the only clock N2 changed was Suicune's survival clock (how soon Altaria wins). Suicune's own attack clock never changed: its list has no Stage 1 Pokémon (Frigibax, Suicune ex and Chien-Pao ex are Basic; Baxcalibur, reached by Rare Candy, is Stage 2).
- **None of Suicune's first changes is an attack choice or a retreat.** Where kta3 attacked (7 deals) or attached Energy (10 deals), km3 first removed Training Area.
- **Altaria's side, for context.** With km3 on Altaria only, the first change in 17 of 21 deals is Altaria playing Training Area where kta3 didn't, sometimes over Soothing Shore. That is the M2 mechanism, and in the mixed rows it neither gains nor loses (−0.6 ± 1.8).

## Method

1. **From the records alone.** The committed game files hold one move fingerprint per game, not the moves. In the cell's 500 deals, km3 on Suicune alone (the mixed row `1f6319e_mixed_table_km3_second.jsonl`, kta3 on Altaria) changes the moves of 91 games against kta3 on both sides (`../kt_tables_2026-09-28/ec7e1a8_kta3_table.jsonl`):
   - 28 swing to Suicune and 3 to Altaria, a net 25 games, which is the 5.0-point gain;
   - 60 keep their result.
   - For comparison, km3 on Altaria alone changes 188 games, and km3 on both changes 227.
2. **The trace, 40 games** (the laptop's cap).
   - **Which deals:** all 31 whose result changed, and the first 9 of the 60 that kept their result.
   - **What it replays:** `km_diag_trace` replays kta3 on both sides, deal by deal, exactly as the table played it.
   - **What it asks:** at every decision of each seat it also asks km3 what it would choose there. km3 gets the same observation, the same offered moves and the same search seed (`Game::randomness().decision`, as `Game::play_tick` seeds each decision).
   - **Why that gives the first change:** until km3's answer differs from kta3's, a game with km3 on that seat is move for move the kta3 game. So the first differing answer is the first differing decision of the km3 game. Asking both seats at once gives it for km3 on Suicune only, on Altaria only, and on both (the earlier of the two).
   - **Program and build:** built as an example in a scratch copy of build B's `engine/` (1f6319e), with one scratch-only helper appended to `value_functions.rs` (`km_diag_clocks.rs`) so it can print kta's and km's clocks. B itself is unchanged. sha256s are in `sha256.txt`; the program is `6de23905…`.
   - **Field Blower's target:** where km3's first different move is Field Blower, the trace also applies that move to a copy of the game and asks km3 for its next choice there. Here that was the only move offered each time: discard the Stadium.
   - **Two runs:** the trace ran twice on the same 40 deals. The first run found the decisions, and the second added the Tools in play and Field Blower's target. The committed rows are the second run's.
3. **Checked against the records** (`classify.py`, whose first lines are these checks; all 40 of 40):
   - every replay's move fingerprint equals kta3's committed game;
   - Suicune has a first differing decision exactly where the km3-on-Suicune record's moves differ;
   - Altaria has one exactly where the km3-on-Altaria record's differ;
   - one of them has one exactly where the km3-on-both record's differ.

## Counts (the 40 traced deals; `classify_output.txt`)

**Suicune's first differing decision** (km3 on Suicune, kta3 on Altaria), by kind and by how the deal's result changed:

| kind | to Suicune (28) | to Altaria (3) | same result (9 of 60) | all 40 |
|---|---:|---:|---:|---:|
| Stadium play (Soothing Shore, replacing Training Area) | 14 | 0 | 3 | 17 |
| Field Blower (on the Stadium: Training Area) | 14 | 1 | 1 | 16 |
| attack choice | 0 | 0 | 0 | 0 |
| retreat or promotion | 0 | 1 | 1 | 2 |
| other (Energy, a Tool, a Trainer) | 0 | 1 | 4 | 5 |

- **Training Area was in play at all 40 decisions.**
- **Which of Suicune's clocks N2 changed there:** its survival clock only ("how soon Altaria wins", Altaria's Stage 1 attacker's bonus) in 38; neither in 2; its own attack clock in none.
- **What kta3 did instead** at the 33 Stadium and Field Blower decisions:
  - attached Energy: 10;
  - attacked: 7 (Crystal Waltz or Buster Tail; km3 plays Field Blower first);
  - played a Trainer: 11 (one of them the Tool Giant Cape);
  - used an Ability: 1;
  - benched a Basic: 4.
- **km3 on both sides, the same 40 deals:** Altaria's change comes first in 20 and Suicune's in 1; in 19 only Suicune's side changes.

## Examples

1. **Soothing Shore instead of attaching Energy** (i = 38, seed 72,040,038, turn 8).
   - The board: Suicune ex (140 HP left) in Suicune's Active Spot, Mega Altaria ex (190) in Altaria's, Training Area in play.
   - kta3 attaches its Water Energy to the Bench.
   - km3 plays Soothing Shore, which replaces Training Area.
   - Suicune's survival clock: kta 2 turns, km 1. Its attack clock is 2 under both.
2. **Field Blower before attacking** (i = 122, seed 72,040,122, turn 8).
   - The same Actives, with Training Area in play.
   - kta3 attacks with Crystal Waltz.
   - km3 first plays Field Blower, whose only offered target is the Stadium, so Training Area is discarded.
   - Suicune's survival clock: kta 2, km 1.
3. **Baxcalibur clears the Stadium before Buster Tail** (i = 253, seed 72,040,253, turn 7).
   - Baxcalibur (Stage 2, 140 HP) is Suicune's Active, facing Mega Altaria ex under Training Area.
   - kta3 attacks with Buster Tail (90).
   - km3 plays Field Blower on Training Area first.
   - Suicune's survival clock: kta 2, km 1. Its attack clock is 3 under both. Baxcalibur is Stage 2, so Training Area gives it nothing.

## Limits

- **Coverage:** 40 of the 91 changed deals were traced: all 31 whose result changed, but only 9 of the 60 that kept their result. The kinds of first change in the other 51 were not traced.
- **What is counted is only the first differing decision.** Later decisions in the km3 games (for example the attack after the Field Blower) are not compared.
- **Field Blower's target is km3's pick on a copy of the game,** not a replay of the km3 game. Here it was the only move offered.

## Files

- `km_diag_trace.rs` and `km_diag_clocks.rs`: the trace program, and the scratch-only helper appended to B's `value_functions.rs` in the copy that builds it.
- `trace_rows.jsonl`: one row per traced deal. It gives the replay's move fingerprint and each seat's first differing decision:
  - kta3's move and km3's move;
  - the turn;
  - the Stadium in play;
  - both Actives;
  - the Tools in play;
  - kta's and km's clocks;
  - Field Blower's target;
  - the 8 moves before it.
- `classify.py`: the checks against the records, and the counts. `classify_output.txt` is its output.
- `sha256.txt`: the sources, the rows and the program.
