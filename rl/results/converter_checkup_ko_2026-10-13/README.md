# Converter: a Pokémon of his knocked out by the checkup after his turn ended

Job from Fable (delegator), from the laptop's note on the v2 read of the Oct 13 games. Sonnet session "Opus agents progress", Oct 13. Branch `sonnet/converter-checkup-ko` (from main feddbce6). Changes: `../pause_games_new_2026-10-12/harness/ledger_to_positions.py` (a new `checkup_knockouts()` and a few changed lines in `convert_game`) and `test_ledger_to_positions.py` (12 new tests, 97 in all, all pass). This folder is the record. No hold file, no other harness file, nothing in `v2/`.

## The problem

When the checkup after his turn knocks out his Active (Poison, Burn, Bad Dreams on a Sleeping Pokémon), the ledger logs the knock-out and his promotion at the end of his own row, and that row's `board_after` is already past the knock-out. The converter finds the Pokémon the opponent's turn knocked out by comparing the end of one of his rows with the start of his next, so it never saw this one: the Pokémon, what was under it, its Tool and its Energy were missing from his discard, and `me.knockouts` stayed 0. In game 20261013_030351000 (Dragonair at turn 5, Druddigon at turn 13) the position of turn 15 showed 4 cards too few and the runner refused it: `deck count: the position says 0, the list minus seen cards leaves 4`. My v2 read worked around it in its own `normalize_ledger.py` (put the Pokémon back into `board_after` in a copy of the ledger); this ports the case into the converter.

## The rule (`checkup_knockouts(row)`)

A Pokémon of his is one when all four hold, for one of his rows:

1. a promotion / replacement play comes after the row's last turn-ending play (an `end_turn`, or an attack);
2. it was on his board at the start of the row and is gone at its end (by instance id; without ids, the Active, when fewer of its name are left);
3. it did not evolve in the row (an evolved Pokémon is a new instance: an evolution play names its id; an Ability or an attack of the Pokémon does not count as an evolution);
4. the row's automatic events or the promotion's text say it was knocked out / left the board / was discarded, and say nothing of it going back to his hand or deck (a bounce, such as Ilima, also ends in a promotion).

Exactly one Pokémon must fit; with two, none is taken and the position's notes say so. Its Energy is what it had at the start plus what the row attached to it (the plays' `energy.destination`), unless the clause of the ledger's text that says it left the board gives a count (then that count, and a note says so; the clause only, since the next one often gives the promoted Pokémon's Energy: `... 3 Metal are discarded. Owner promotes second Haxorus 150 HP with 1 Fighting.`). Its Tool is the one it had, or one the row attached. It then goes through the same path as a Pokémon the opponent knocked out: `disc` (the Pokémon, the cards under it, its Tool), `disc_energy`, `me.knockouts`; the note reads `knocked out at the checkup after his turn ended: X`. It does not set the flag that Mach Stealth reads (that is the opponent's attack), and the Energy-moved-by-the-opponent adjustment does not apply to it.

Across the 50 game folders in Recording_QA (233 rows of his) this fits exactly two rows: 030351 turns 5 and 13. Three other rows have a Pokémon gone at the end of his row (two of Accelgor's Deck and Cover, which shuffles the Pokémon and what is on it into his deck and promotes another, and one Ilima bounce of a Regigigas); none has a promotion *play* after the last turn-ending play (the promotion is in the attack's text), so none is taken, and if a ledger did log one the text ("return to deck", "shuffles") would still keep it out (test). A Pokémon of his knocked out by its own attack's recoil would have the same shape (attack, then promotion, with the knock-out in the text) and is covered by the same rule; none occurs in the 50 games.

## What changes (`scripts/compare_old_new.sh`, output in `compare_output.txt`, details in `before_after.json`)

The converter of main against this branch's, on the same ledgers: the 28 older games as they are (125 positions) and the 14 games of Oct 12-13 (92 positions) through v2's normaliser, in two forms.

| ledgers | result |
|---|---|
| as the v2 read used them (the normaliser's restore step on) | **0 of 217 positions differ.** The positions in `v2/` stay as they are; the restore step is now redundant and harmless |
| without the restore step | **5 of 217 differ**, all of 030351 (turns 7, 9, 11, 13, 15), and only in `me.discard`, `me.discard_energy`, `me.knockouts` and (turns 7 and 15) `notes`. The other 212 positions, including all 125 of the older games, are identical |

In the 5 positions: Dragonair B4 117 and the Dratini B4 116 under it and 2 Metal enter the discard from turn 7 (and `knockouts` is 1); Druddigon A1a 056 with its Rocky Helmet and 3 Metal enter from turn 15 (`knockouts` 2).

Against the v2 restore (`new converter, restore on v off`): 2 positions differ, only in wording of the note (`between turns` v `at the checkup after his turn ended`) and, at turn 15, one more Metal in `discard_energy` (7 instead of 6): the restore took Druddigon's 2 Metal from the start of the turn, the port adds the third that Dragon's Blessing attached to it during the turn, which the ledger's text confirms (`3 Metal are discarded`).

## In the runner (`pg_pos_F_cond`, sha256 5c4859949a88a28b, km3 seeds 1-12, nice 19)

The 8 positions of 030351 from the new converter on the ledgers without the restore step load with no problems, 030351 turn 15 included (the old converter on the same ledger: `deck count: the position says 0, the list minus seen cards leaves 4`), and km3's plans are identical to the v2 runs in all 8 positions x 12 seeds.

## Open (not part of this job; the position format is unchanged)

- `discard_energy` only goes up (retreat payments, knock-outs). An Ability that attaches Energy from the discard (Dragonair's Dragon's Blessing in 030351) does not take it out again, and Energy a Stadium discards from the zone (Rainbow Cave) is not added. For 030351 the position's `discard_energy` is therefore not the real pile.
- A Tool that the knocked-out Pokémon received in its last row is read from the row's plays; an unusual wording of that play would be missed (the count of cards shown would be one short).
- If the ledger gives no instance ids the rule falls back on names and the Active; I have no such ledger with a checkup knock-out, so that path is tested only with made-up rows.

## Files

`README.md` (this), `compare_output.txt`, `before_after.json`, `scripts/` (`compare_old_new.sh`, `cmp_pos.py`, `before_after.py`). Tests: `cd rl/results/pause_games_new_2026-10-12/harness && python3 -B -m unittest -v test_ledger_to_positions.CheckupKnockouts` (12) or the whole module (97).
