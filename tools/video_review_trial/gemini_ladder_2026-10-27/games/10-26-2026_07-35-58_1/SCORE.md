# Score: Dustin (Dacz8976) vs こたどん, 10-26-2026 07-35-58_1

Review G = Gemini (`gemini/`). Review X = Codex (`codex/REVIEW.md` as amended by its correction notes; its native mm:ss times were converted to video seconds, e.g. 584.50 s is `t_0584`/`t_0585`).
About 45 frames were opened (limit 120).

## Facts both reviews agree on and the frames support

- Dustin went first. His opening hand: Poké Ball, Team Rocket's Koffing (x2, one gold), Seadra, Kingdra ex (`t_0025`).
- Dustin's Energy Zone is Water. The opponent's is Lightning and Water (Lightning seen `t_0024`, Water seen `t_0123`).
- The opponent opens with Oricorio and its Ability Safeguard (`t_0036`).
- Boiler Smog on turns 3 and 9.
- Seadra's Water Arrow for 50, then Poison and Burn, Knock Out the first Oricorio at the end of turn 9. Score 1-0.
- Zzzap hits on turns 8, 10, 12, 14 and 16. The turn-10 Zzzap knocks out Seadra. Score 1-1 (the opponent's point marker is visible at `t_0491`).
- Water Shuriken hits Dustin's Pokémon on turns 10, 12, 14 and 16. Soothing Shore heals on both sides.
- Dustin concedes on turn 18 (`t_0584` confirm dialog, `t_0587` Defeat).
- Result screen (`t_0594`, `t_0596`, `t_0597`): went first, 18 turns, 1 point each, damage done 50. Card of the Game is Seadra for Dustin and Oricorio for the opponent. Master Ball Rank, 999 pts, 0 lost.
- Seven or eight sub-turn details (HP values, Shore heals, Copycat and Research draws) match in the two reviews wherever I spot-checked them (`t_0462`, `t_0466`, `t_0491`, `t_0578`).

## Disagreement table

| Turn | Item | G says | X says | Frames | Verdict |
|---|---|---|---|---|---|
| 2 (opp) | Trainers played | Poké Ball, then **Professor's Research** (t=64-66), bench Oricorio and Froakie, L to Active | Poké Ball only; "No opponent Research ... is established" | `t_0064` (discard top is Poké Ball), `t_0070` (discard top is Professor's Research, hand and deck changed) | G right |
| 4 (opp) | Energy attachment | Lightning to the new Active Oricorio (70 HP), t=124 | No new Energy attachment ("Water offered, not attached") | `t_0123` (new Active has no Energy, Zone shows Lightning), `t_0125` and `t_0127` (Lightning icon on the Active Oricorio, Zone empty) | G right |
| 12 (opp) | Order inside the turn | Water Shuriken (t=458-462) then Lightning to Greninja (t=463-465) | Lightning to Greninja, then Water Shuriken | `t_0457` (no L on Greninja), `t_0462` (Weezing already 70, Greninja has no L), `t_0466` (L now on Greninja) | G right (order only; not counted as an error, X's ledger is labelled approximate) |
| 14 (opp) | Where the Lightning goes | Benched Greninja (now 2 L) | Froakie | `t_0491` (Greninja 1 L, Froakie none), `t_0497` (Greninja still 1 L, Froakie has L) | X right |
| 18 (opp) | Second Greninja | Opponent plays **Rare Candy** (t=581-582), then Froakie becomes Greninja (584-586) | A second Greninja appears; "enabling mechanism not established; no Rare Candy is inferred" | `t_0581` (enlarged Rare Candy card, opponent's clock running, Dustin's clock frozen), `t_0582` (card gone), `t_0584` (Greninja card played behind the concede dialog), `t_0586` (two Greninja) | G right |
| 18 (opp) | Energy on the second Greninja | 0 Energy | Preserves Froakie's Lightning | `t_0578` (Froakie has L), `t_0586` (right-hand Greninja has L) | X right |

No "both wrong" and no "unsettled" items.

## Claims only one review makes that the frames contradict

- G only: Greninja has "2 L" on turn 14 and later board states. It has 1 L and 1 W (`t_0578`).
- G only: the second Greninja has 0 Energy (see the table).
- X only: none found. X leaves things out; it does not invent them. (Its "No new Energy attachment" on turn 4 and its "no Rare Candy" are the omissions above.)

## Errors and grades

**Review G (Gemini)**
- Major 1: Turn 14, a Lightning Energy said to go to Greninja; it went to Froakie (`t_0491`, `t_0497`). The wrong Greninja Energy counts in the turn 14, 16 and 18 board-state lines come from this one error, not counted again.
- Minor 1: Turn 18 board state, second Greninja shown with 0 Energy; it has the Lightning that Froakie carried (`t_0586`).

**Review X (Codex)**
- Major 1: Turn 2, Professor's Research play missing (`t_0064`, `t_0070`).
- Major 2: Turn 4, Lightning attachment to the new Active Oricorio missing (`t_0123`, `t_0125`).
- Major 3: Turn 18, Rare Candy play missing and the second Greninja's cause called unknown (`t_0581`, `t_0582`).
- Minor 0.

Timestamps: no gap over 3 s was found in either review (G's 581-587 and X's 584.5 and 587.5 both match frames).

## Opponent sheets (12 fields)

Truth: went_first Dustin; 18 turns; final 1-1; end concession by Dustin; Energy Zone Lightning and Water; Pokémon Oricorio, Froakie, Frogadier, Greninja; attack Zzzap (Water Shuriken and Safeguard are Abilities); Trainers Poké Ball, Professor's Research, Soothing Shore, Copycat, Rare Candy; special_conditions none (the Poison and Burn came from Dustin's Boiler Smog); healed true; bench_damage true; card of the game Oricorio.

| Field | gemini | gemini_cheap | codex |
|---|---|---|---|
| went_first | right | right | right |
| global_turns | right | right | right |
| final_score | right | right | right |
| end | right | right | right |
| Energy Zone type(s) | right | right | right |
| Pokémon names | right | right | right |
| attack names | right | right | right |
| Trainer names | right | right | **wrong** (no Professor's Research, no Rare Candy) |
| special_conditions | right | right | right |
| healed | right | right | right |
| bench_damage | right | right | right |
| card of the game | right | right | right |
| **Right / checked** | **12 / 12** | **12 / 12** | **11 / 12** |

Outside the 12 fields: gemini's `opponent_energy_attached` has the same turn-14 target error as G's review; gemini_cheap's attachment list is scrambled (it lists Water on turn 4 and turn 8 and misses turns 14 and 16); codex's attachment list lacks turn 4. None of these are among the 12 scored fields.

## Which record to rely on

Review G is the one to rely on for this game. It has the complete card-by-card turn record: it is the only one to log the opponent's Professor's Research (turn 2), the turn-4 Lightning attachment and the turn-18 Rare Candy, and its sheets match all 12 sheet fields. Its faults are one wrong Energy target (turn 14, Lightning to Greninja instead of Froakie, which makes its later Greninja Energy counts wrong) and one small board-state slip on the second Greninja. Review X has the right Energy target for turn 14 and the right Energy on the second Greninja, but it left out three opponent plays (two Trainers and one Energy attachment), so its Trainer list and its turn-4 and turn-18 pictures are wrong. Both agree on every attack, damage number, Knock Out, point, the 1-1 score and the concession. A player should take the turn-by-turn play from G and double-check the Energy on the Greninja line against X.
