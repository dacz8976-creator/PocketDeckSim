# SECOND_READ_7.md: the second reader's classification of the seven pending turns (Oct 16)

Written before `FIRST_READ_7.md` was opened. Read from `pause_games_new_2026-10-13/v2/positions_all.json` (the v3 positions), his recorded
move (`his_plan`), the card texts (`lib/card.py`), and his stated plan (`SPEC_AMENDMENT_1.md`: both Glimmora get a turn, Regigigas walls, no
Muk/Pawniard in front, the Blade is "enough to knock out their likely strongest and win"; `DESIGN_NOTE_CASES.md`: sacrifices that raise the
Blade count are deliberate). Classes as in `EXPECTED_KG.md`: **positive** (his move is right or at least as good, km3's is not),
**unclear** (can't tell), **km3 better**. Opponent lists are partly guessed, so every reading is of the board shown.

| # | turn | class | confidence | reason |
|---|---|---|---|---|
| 9 | 210041 t06 | positive | medium-low | Mega Lucario ex (FF ready, 90) knocks out the 40-HP Regigigas or the 60-HP Glimmet either way; Ilima only swaps Regigigas for Glimmet as the victim unless Muk is put in front (his "that is the way you lose"). He lets the Regigigas go and puts the Energy toward Kingambit; the loss also grows the Blade. The cost is a point given up, so not higher. |
| 10 | 203719 t07 | positive | medium-high | Kingambit has one Darkness, so a Blade now is 60 (count 0) against a 180-HP Mega Rayquaza ex. Rare Candy, Ilima for the 10-HP Regigigas, Glimmora promoted and Venomous Hit is his "both Glimmora have a turn" plan; the Kingambit stays safe on the Bench. |
| 11 | 210823 t08 | positive | medium-high | The Blade is 60 against a 210-HP Mega Pidgeot ex at count 0, pointless. Ilima for the 50-HP Regigigas, Glimmora promoted, a new Glimmet and Venomous Hit follow his plan and use the Energy where it attacks. |
| 12 | 010706 t11 | positive | medium | Muk can't reach Sludge Bomb this turn, and the opponent's Mega Diancie ex (4 [P], Brilliant Storm 120+) knocks it out wherever the Helmet is. A Helmet and the Energy on the benched Kingambit prepare it as the next Active at count 2 (Blade 140) with -20 damage. Not higher: the Helmet on the Muk would survive a 120 hit if the opponent does not attach. |
| 13 | 010837 t05 | positive | medium-high | The Regigigas has no Energy and is 3 short of Giga Turbo, and takes Double-Punching Family (120, leaves 30), so an attach there is wasted; the Energy on Pawniard starts its [DD] for Kingambit (in hand) at count 1. Muk evolving and Glimmet placed follow the plan. |
| 14 | 014423 t03 | positive | medium-high | The Active Grimer (70) is doomed: Dedenne ex's Dede-Circuit is 40 per Tool and the opponent holds three (Cord, Rocky Helmet, Small Balloon), 120 at [LL] and a Lightning is attached next turn. An Energy on it is lost; Pawniard is the right target. No Copycat: the opponent's hand is 1, so it draws 1. An `_expo` case, not a Blade one. |
| 15 | 203719 t11 | positive | medium | The Active is a 10-HP Regigigas with no Energy that will fall to anything, so km3's Helmet on it (@0) is wasted; on the Kingambit (retreat 3, -20 per hit, 140 HP) it protects the Pokémon that is promoted after it falls at count 1 (Blade 100 knocks out the 90-HP poisoned Drampa). Not higher: the Energy went to Muk, not to the Kingambit, which I don't understand; the Helmet property alone is the claim. |
