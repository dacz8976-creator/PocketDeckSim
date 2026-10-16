# READ.md — Dustin vs km3, turns T1–T7

Worked only from turns.json, cards.md, PLAN.md and his_list.txt. (A TASK.md also sits in the folder; I did not open it.)

Conventions: `points` is read as [me, opp]. T6 `[1,0]` has Ralts in the opponent's discard, and T1 has my Glimmora KO'd with opp points 0 (a heads on the coin). Bench indices in the plans are positions in the `board` list, and I checked each one against the attack named in the plan. His deck is 20 cards, which I counted from his_list.txt.

| Turn | km3's line (12 seeds) | His line | Class | Conf. | Deciding fact |
|---|---|---|---|---|---|
| T1 | Glimmet, Muk, energy on **Regigigas** (12/12) | Muk, Glimmet, energy on **Pawniard** | his line at least as good | high | 1 energy on Regigigas (needs CCC) attacks nothing and is lost when Ilima pulls it back. On Pawniard it counts toward Kingambit's DD. |
| T2 | Ilima, Kingambit promoted, Regigigas re-placed, energy on Kingambit, Blade 60 (12/12) | Ilima, **Glimmora** promoted, Glimmet placed, energy on Glimmora, Venomous Hit | his line at least as good | high | At 0 KOs the Blade does 60 against a 210-HP Mega Pidgeot. Putting Kingambit Active exposes it to a 100-damage Twister that strips its energy, and Glimmora is the cheaper KO to give up. |
| T3 | Candy to Kingambit, Ilima, **Kingambit** promoted with 2 energy, Blade 60 (12/12) | Same Candy and Ilima, **Glimmora** promoted, Regigigas re-placed, Venomous Hit | his line better | high | Rayquaza (F+L, plus the visible Fire attach) can hit for 150 after a free-ish retreat. That is above Kingambit's 140 and below nothing of his that he wants to lose. |
| T4 | Ilima, **Pawniard promoted Active**, energy, Slash (12/12) | Energy on Pawniard (stays benched), nothing else | his line better | high | Pawniard 50 HP Active dies to Lucario's 90 already loaded. It is the only Pawniard and the list has no Bisharp, so Kingambit would be dead. |
| T5 | Energy on Kingambit, Helmet on **Regigigas (10 HP)**, Mesagoza (12/12) | Helmet on **Kingambit**, energy on Muk | his line at least as good | medium | Regigigas at 10 HP dies to any hit and the Helmet is lost with it. On Kingambit (retreat 3) it turns a 150 Mega Burst into 130, below 140. |
| T6 | Helmet and energy both on **Muk** (Active) (12/12) | Helmet and energy both on **Kingambit** (bench) | his line at least as good | medium | The opp's visible threat is Diancie hitting for 140 and exposing itself at 40 HP, a 3-point win for me. After Muk dies, Regigigas cannot attack, so the only punisher is a Kingambit holding DD. |
| T7 | Mostly energy on **Grimer**, then **Copycat** in 8/12 seeds (4 seeds just attach and end) | Energy on Pawniard only, nothing else | his line better | high | Copycat draws only 1 card (opp hand 1), so I would shuffle away 4 cards, including the one Rare Candy. The energy on Grimer is wasted because Grimer is KO'd. |

## T1
**km3**: all 12 seeds Place Glimmet, evolve Muk, attach to Regigigas (@0). **His line**: the same two plays, but the attach goes to Pawniard (@1).

Both lines have Muk in play, so Regigigas's ability is off. Regigigas needs CCC for Giga Turbo, so with 0 energy now and one attach per turn it cannot attack this turn or next, whichever line. The opponent's visible threat is Mega Kangaskhan with 3 energy (L, M, M) plus the Metal coming, using Double-Punching Family for 80 + 40 = 120. That takes Regigigas to 150 − 120 = 30 in both lines and does not KO it. Nothing on my side dies in either line. The difference is only where the energy sits.

PLAN.md says Regigigas is a wall to be pulled back with Ilima, and Ilima discards attached energy. T2's discard shows two Darkness already lost that way. Energy on Pawniard survives into a Rare Candy evolution, and Kingambit needs DD ("two energies… two turns"). Pawniard is undamaged on the bench, so Cyrus cannot target it. This is a free pre-load with no downside I can find. km3's attach on Regigigas is wasted.

## T2
**km3**: Ilima on Regigigas (50 HP), promote Kingambit (1 D, +1 attach = DD), re-place Regigigas at 150, Overlord's Blade 60. **His line**: Ilima, promote Glimmora (90), place the second Glimmet, attach to Glimmora, Venomous Hit 30 and poison.

The opponent's Active Mega Pidgeot ex (210, D D C) has Giant Twister (CCC): 100 damage, with 3 coin flips that each discard a random energy from my Active. If all three are tails it does nothing, which is a 1/8 chance.

km3's line: Blade 60 takes Pidgeot to 210 − 60 = 150, and the return hit leaves Kingambit at 140 − 100 = 40. Its 2 energy is stripped in 4/8 of the cases: with 2 heads or more it loses both, with 1 head it loses one, and with 0 heads nothing happens. Kingambit has retreat 3 and no spare energy, so it is stuck Active and dies next turn (40 < 100; two Ice Pops only reach 80). Even a Blade that fully works would need 4 KOs to reach 60 + 40×4 = 220 ≥ 210. At 0 KOs it is nowhere near.

His line: Pidgeot goes 210 − 30 = 180, and about −10 per poison checkup (a rule not in cards.md). Glimmora (90 < 100) dies to Twister, giving the opponent 0.5 points on average (the Shattering Crystal coin). The KO count goes to 1, so the Blade becomes 100, and I choose the new Active, so I can bring in Muk or Glimmet rather than Kingambit. Kingambit stays safe with 1 energy and Regigigas is held back at full HP. Damage is roughly equal (about 60 for km3, about 50 for his), but km3 puts the win condition on the line and he puts the Glimmora, which PLAN.md says averages 0.5 points.

## T3
**km3**: Rare Candy to Kingambit (from Pawniard, 1 D), Ilima on Regigigas (10 HP), promote **Kingambit**, re-place Regigigas, attach (DD), stadium, Blade 60. **His line**: the same Candy and Ilima, stadium, but promote **Glimmora**, re-place Regigigas, attach to Glimmora, Venomous Hit.

The opponent's Active is Drampa (100, 1 L) with Power Blast (CC): 70. The bench holds Mega Rayquaza ex (F + L, 180) with Mega Burst (RL): it discards all R/L and deals 50 per energy discarded. Its energy next turn is Fire. Drampa has retreat 1, so the opponent can retreat it (discarding its L), attach Fire to Rayquaza (F, L, F = 3 energy) and use Mega Burst for 3 × 50 = 150. That is all visible and needs nothing from the opponent's hand.

km3's Active Kingambit has HP 140, and 150 ≥ 140, so Kingambit is KO'd (opp +1 point, and the Kingambit line is gone) for a Blade of 60 on Drampa (100 → 40, no KO). Even without the Rayquaza line, Kingambit sits Active with retreat 3.

His line: Glimmora (90) is Active with 1 energy and does 30 + poison to Drampa (100 → 70, then −10 per checkup). It dies to Mega Burst (150 ≥ 90) or takes 70 from Drampa (90 − 70 = 20). If it dies, the opponent gets 0.5 points on average, my KO count goes to 1 and the Blade is 100. Kingambit sits benched, undamaged (so no Cyrus target), with 1 energy. The Regigigas and Ilima parts are the same in both lines (both save the 10-HP Regigigas).

## T4
**km3**: Ilima on Regigigas (40 HP), promote **Pawniard** (50 HP), re-place Regigigas, attach to Pawniard, Slash 30. **His line**: attach to Pawniard (benched), nothing else.

The opponent's Active is Mega Lucario ex (190, F F) with Fighting Pulse (FF): 90, or 140 with an extra Fighting attach (Fighting is the energy next turn). The Active Pawniard has 50 HP, so 90 ≥ 50 and it dies. Hitmonchan ex is on the bench and would need a retreat. Weakness does not matter here: 90 > 50 even without it. Pawniard is the only Pawniard in his list and the list has no Bisharp, so losing it ends Kingambit entirely. In exchange km3 deals 30 (Lucario 190 → 160) and saves Regigigas. Regigigas's HP is 40, and it takes at least 90 from Lucario, so either way I lose a card to a 1-point KO.

His line: Regigigas stays Active and dies to Lucario (40 ≤ 90): the opponent gets 1 point, I get KO count 1 (Blade 100), and Pawniard is untouched on the bench with 1 energy, a Cyrus-safe target since undamaged. That matches "protecting pawniard is what I favor" and "Ideally pawniard hits the bench after one pokemon has been ko'ed." He leaves Ilima in hand rather than burning it to swap one dying card for another (Ilima + Glimmet Active would also be KO'd for the same 1 point).

## T5
**km3**: Darkness to Kingambit (now 2), Heavy Helmet on **Regigigas** (10 HP, Active), use Mesagoza, end. **His line**: Helmet on **Kingambit**, Darkness to Muk (2).

Nobody attacks in either line: Regigigas has no energy and the others are on the bench. The opponent's Drampa (90, L, poisoned) has L + the L coming = CC for Power Blast 70, which KOs Regigigas (10 HP) even through a Helmet (70 − 20 = 50 ≥ 10). So km3's Helmet is lost with Regigigas. On Kingambit (retreat 3, so the Helmet applies) it cuts every hit by 20. Rayquaza's Mega Burst with F, L plus one more R/L energy is 150, which is 150 − 20 = 130 < 140. Without the Helmet it is 150 ≥ 140. That is the "protecting Kingambit" margin, and it holds only when the energy next turn is R or L (unknown; the one after is not shown).

The energy placement is roughly a wash: Kingambit has 1 D, attaches one next turn and has the DD it needs for a Blade of 60 + 40 = 100 once Regigigas is KO'd and Kingambit is promoted. Mesagoza is a no-op here: all 9 Pokémon in his list are on the board or in his hand, so the deck has none left to find.

## T6
**km3**: Heavy Helmet and the Darkness both on **Muk** (Active), end. **His line**: both on **Kingambit** (bench, 140, no energy before).

The opponent's Mega Diancie ex is on the bench at **40 HP** with 4 Psychic and a Giant Cape. Peculiar Plaza makes Psychic retreat costs 2 less, so Indeedee (retreat 1) swaps out for free. Brilliant Storm (CCC) does 40 + 20 per Psychic energy on all their Pokémon: 4 + the Psychic coming = 5, so 40 + 100 = 140. That KOs Muk (110): even with km3's Helmet it is 140 − 20 = 120 ≥ 110. So Muk dies in both lines and the opponent goes to 1 point (my KO count 2, Blade 60 + 80 = 140).

Then Diancie is Active at 40 HP, and a KO of a Mega ex is 3 points (1 + 3 ≥ 3), which is a win. The punisher has to be Kingambit with DD. In his line it has D (this turn) + the attach next turn = DD, with the Helmet. In km3's line it has 0 energy, one attach gives only 1 D, and Muk's Colorless energy is gone with Muk. Regigigas (DDD on the bench) cannot do it: its Seal needs Muk alive to be switched off, and Muk would be the one KO'd. Indeedee's heal is also off while Muk lives (Indeedee is Basic), so Diancie stays at 40 up to the attack.

The verdict is medium because it relies on the opponent actually attacking with Diancie; if it does not, the lines differ little (his is no worse).

## T7
**km3**: in 4 seeds (2, 4, 7, 10) attach to Grimer and end turn. In 8 seeds it goes on to play Copycat (seed 1 attaches to Pawniard, seed 9 to Regigigas, 3/5/8/12 to Grimer, 6 and 11 play Copycat first). Those plans are cut at the first draw, so the final board is unknown. **His line**: attach to Pawniard, nothing else.

My hand is Copycat, Glimmora ×2, Rare Candy, Ice Pop. The opponent has **1** card in hand, so Copycat shuffles my other 4 cards into the deck and draws 1. His deck is 20 cards, so the deck is about 10 now, which makes it 14 after the shuffle. A draw for Kingambit goes from 1/10 to 1/14, and I lose the single Rare Candy and both Glimmora (PLAN.md: "You want both glimmora to have a turn"; "If I have one card that I really need, I don't use copycat"). In the hand as it stands, Glimmora ×2 and Ice Pop do nothing now (no Glimmet in play, no damage) and Rare Candy needs Kingambit, so there is some argument for refreshing, but it is a 4-for-1 trade and he is right to decline.

The opponent's threat: Dedenne ex Active has 1 L and gets the L coming, so LL. Dede-Circuit is 40 per Tool on all their Pokémon: Electrical Cord, Rocky Helmet, Small Balloon = 3 tools, so 3 × 40 = 120, which is above Grimer's 70. The Active Grimer cannot retreat (retreat 2 against at most 1 energy), so it dies in every line. That gives the opponent 1 point and me a Blade of 100, and any energy on Grimer is wasted. In his line the energy on Pawniard (bench, undamaged) is preserved.

## Data notes
- cards.md does not state weakness (+20), poison damage (10 per checkup), or that a Colorless energy cannot pay a [D] cost. I used the standard values. No verdict depends on any of them, but T2's poison figures, T6's Colorless energy on Muk and T4's side arithmetic use them.
- Energy names map to cost letters as Fire → [R], Lightning → [L], Psychic → [P]. T3's Rayquaza numbers use that, and Rayquaza's cost RL is met by the Fire and Lightning shown.
- T7's board looks like a lot for the opponent to have played by game turn 3 (4 Pokémon, 3 tools, 2 energy). The file marks every position `approximate`, and the verdict does not depend on it.
- T5 and T6 both show turn_count 11 and his_turn 6. This is consistent with him being first player, so I treated it as a coincidence rather than an error.
