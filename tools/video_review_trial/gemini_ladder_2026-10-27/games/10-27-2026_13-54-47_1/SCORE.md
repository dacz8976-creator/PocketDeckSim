# Score: Gemini (G) vs Codex (X), game "ScreenRecording_10-27-2026 13-54-47_1"

Frames opened: about 31 of the 120 allowed (t=1, 3, 20, 22, 24, 32, 73, 98, 132, 219, 221, 270, 286, 363, 380, 402, 500, 514, 522, 585, 593, 600, 664, 675, 676, 677). t=678 does not exist.

## Facts both reviews agree on (confirmed by the frames, not repeated below)
- Opponent went first; Dustin chose Hoopa ex (150 HP) active, opponent Electrike (60 HP). Opening hand: Hoopa ex, Protective Poncho, Professor's Research, Deceptive Needle, Rare Candy (t=24, t=32). Energy Zones: opponent Lightning, Dustin Darkness.
- 12 global turns, Dustin 2 - 0, opponent conceded (banner at t=664). Result screen: 12 turns played, 250 damage, "pts gained 1" (t=675, 677).
- Both knockouts (Electrike on turn 4, Oricorio on turn 8), Shadow Bullet / Zzzap / Hyper Ray damage, Rocky Helmet hits, Deceptive Needle chips, Lucky Ice Pop chain (Hoopa 10 to 90) all agree and fit every frame opened (Hoopa 130 at t=219, 110 at t=286, 60 at t=380, 10 at t=500, 90 at t=664).
- The deck screen at t=1 shows the name "New deck 18", Hoopa ex, Mega Sableye ex, 2 Deino, 2 Hydreigon, 2 Poke Ball, Rare Candy. G records the name; X's QR route records the deck another way ("title obscured" in X refers to the t=0 frame). Not graded.

## Disagreement table

| Turn | Item | G says | X says | Frames | Verdict |
|---|---|---|---|---|---|
| 5 (opp) | Opponent's Supporter | Professor's Research at t=270 (draw 2) | Not mentioned. Turn 5 is: bench Oricorio, attach, Zzzap | t_0270 shows Professor's Research being played on the opponent's turn (opponent clock running, "Time limit 77") | G right |
| 7 (opp) | Where the Lightning Energy went | Attached to benched Oricorio at t=402; board shows bench Oricorio 1 Energy, Electrike 0 | Attached to the new benched Electrike around t=380; Electrike 1 Energy | t_0363: Electrike being benched, bench Oricorio no Energy. t_0380 and t_0402: benched Electrike shows a Lightning icon, benched Oricorio shows none (active Oricorio 2) | X right |
| 9 (opp) | Where the Lightning Energy went | Attached to Active Electrike at t=520, then it retreats | Attached to benched Oricorio at t=512-514, then Electrike retreats, discarding its 1 Energy | t_0500: active Electrike 1 Energy. t_0514: benched Oricorio now has a Lightning icon, Electrike still 1. t_0522: Electrike benched with 0 Energy, Oricorio active with 1 | X right |
| 11 (opp) | Energy attachment | Lightning to benched Electrike at t=592 | "No new Energy attachment observed"; counts 4 attachments in total | t_0522 and t_0585 area: Electrike 0 Energy after the turn-9 retreat. t_0593: benched Electrike (40 HP) has a Lightning icon. t_0664: Electrike still has 1 | G right |
| Result screen | Opponent's Card of the Game | Oricorio, on the "Your opponent's cards" screen at t=676 | Says no opponent result-screen selection exists; Oricorio is the analyst's pick (and the independent check told X to delete the contrary statement) | t_0676: "Card of the Game" over Oricorio, vs. ぴかちゅう | G right |

Not counted as disagreements (within tolerance or no real conflict): concession time (G 664, X 665.5-666.5; frame t=664 already shows the banner), opponent promotes Electrike on turn 8 (453 vs 456), turn 3 order of the Lightning attach and Copycat (G: Lightning first, Copycat 220; X is vague "by 225.5"; frame t_0219 shows the Lightning already on bench Oricorio and a 5-card hand, t_0221 a 4-card hand, so G's order is right and X's is not contradicted).

## Errors by review

### G (Gemini): 2 major, 0 minor
1. Major. Turn 7, opponent Energy attachment. G: Lightning to benched Oricorio at t=402. Truth: to benched Electrike, already there by t=380. The turn 7 board-state line (bench Oricorio 1 Energy, Electrike 0) is wrong for the same reason and is not counted again.
2. Major. Turn 9, opponent Energy attachment. G: Lightning to Active Electrike at t=520. Truth: to benched Oricorio by t=514; Electrike's own Energy from turn 7 is what it discards on the retreat. The turn 9 end-of-turn board in G is right (the two errors cancel).

### X (Codex): 2 major, 1 minor
1. Major. Turn 5: leaves out the opponent's Professor's Research play (t=270).
2. Major. Turn 11: says no Energy attachment; the opponent attached Lightning to the benched Electrike (~t=592). X's "four attachments" total (and its repeat in the independent check) is wrong for the same reason; truth is five (Oricorio turns 3, 5, 9; Electrike turns 7, 11).
3. Minor. Result screen: X says the opponent's Card of the Game was an analyst pick with no result-screen selection; the screen at t=676 shows Oricorio as the game's Card of the Game. X's sheet value (Oricorio) is right.

## Opponent sheets (12 fields each, against the frames)

Fields: went_first, global_turns, final_score, end, Energy Zone, Pokemon names, attack names, Trainer names, special_conditions, healed, bench_damage, card of the game.

| Field | Truth | gemini | gemini_cheap | codex |
|---|---|---|---|---|
| went_first | opponent | right | right | right |
| global_turns | 12 | right | right | right |
| final_score | 2-0 Dustin | right | right | right |
| end | opponent concession | right | right | right |
| Energy Zone | Lightning | right | right | right |
| Pokemon names | Electrike, Oricorio, Zeraora (two Electrike, two Oricorio) | right | right | right |
| attack names | Zzzap only | right | right | right |
| Trainer names | Professor's Research, Rocky Helmet, Copycat, Poke Ball, Cyrus, Lucky Ice Pop, Red Card | right | right | right (name set complete; its per-turn list omits the turn 5 Professor's Research entry) |
| special_conditions | none | right | right | right |
| healed | true (Lucky Ice Pop healed Oricorio 60 to 70) | right | right | right |
| bench_damage | false | right | right | right |
| card of the game | Oricorio (t=676) | right | right | right |

Score: gemini 12/12, gemini_cheap 12/12, codex 12/12.
Outside the 12 fields (not scored): the `opponent_energy_attached` lists are wrong in gemini and gemini_cheap (both give turn 7 Oricorio and turn 9 Electrike, the same two errors as G's review; both have turn 11 Electrike right) and in codex (turns 3/5/7/9 right, but it misses turn 11).

## Which record to rely on
For this game, G is the more complete record: it is the only one that has the opponent's turn 5 Professor's Research and the turn 11 Energy on Electrike, it matches the result screen for the opponent's Card of the Game, and it records the deck name. Both reviews agree on every attack, damage number, Knock Out, point, turn order, the ending and the whole of Dustin's play, so the facts that decide the game are equally reliable in either. X is more reliable on where the opponent's Energy went in turns 7 and 9 (G has both targets wrong, which would mislead anyone tracking the opponent's Electrike and Oricorio Energy), but X's own total of four attachments is wrong. Each review has two major slips, all in the opponent's side bookkeeping, and the slips do not overlap, so a player should read G's narrative and take X's Energy targets for turns 7 and 9; the opponent sheets, all three 12/12, are equally safe to use.
