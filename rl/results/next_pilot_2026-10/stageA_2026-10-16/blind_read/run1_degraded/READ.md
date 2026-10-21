# Reading T1-T7: km3 vs Dustin

Sources: turns.json, cards.md, PLAN.md, his_list.txt only.

**Limits that apply to every turn**
- cards.md has no entry for any opposing card. That covers Mega Kangaskhan, Mega Pidgeot, Mega Rayquaza, Mega Lucario, Mega Diancie, Indeedee, Drampa, Dedenne and the rest. It also has no entry for the Stadiums Soothing Shore and Peculiar Plaza, or for Giant Cape, Rocky Helmet or Electrical Cord.
- So I can't compute the damage the opponent does next turn. I only use what is visible (HP, attached Energy, this turn's Energy) and my own HP arithmetic. Every verdict that depends on "can they KO X" is flagged.
- Poison's 10 damage per checkup is a standard Pocket rule, not in cards.md. I use it only as a minor term.
- The "Colorless" Energy on Muk (T6) and "[C] cost can be paid by any Energy" are also not stated in cards.md. They are standard rules.
- Board slot 0 is the Active. In his plans `@n` is a board slot and `Attach@0` means the Active.
- Deck count: his list is 20 cards. All 9 of his Pokémon cards are accounted for on board, in hand or in discard at T5 and T6.

| Turn | km3's line | His line | Class | Confidence | Deciding fact |
|---|---|---|---|---|---|
| T1 | Evolve Muk, Glimmet to bench, **Energy on Regigigas** (12/12 seeds) | Same, **Energy on Pawniard** | his line at least as good | medium | Regigigas is the Ilima pull-back wall, and Ilima discards its Energy. Pawniard's Energy is the one that counts toward Kingambit's [DD]. |
| T2 | Ilima, **Kingambit Active**, 2nd Energy on it, Blade 60 on Mega Pidgeot ex (12/12) | Ilima, **Glimmora Active**, Glimmet to bench, Venomous Hit 30 + poison | his line at least as good | medium | The Blade is 60 (0 KOs) and takes no KO. It leaves the only Kingambit stuck Active (2 Energy, retreat 3) in front of a 4-Energy Mega ex. |
| T3 | Candy → Kingambit, Ilima, **Kingambit Active**, Blade 60 on Drampa (12/12) | Same Candy and Ilima, **Glimmora Active**, Venomous Hit 30 + poison | his line at least as good | medium | The Blade does 60 against Drampa's 100 HP and no KO is available. It trades 20 extra damage for the Kingambit, which can't leave the Active spot with 2 Energy against retreat 3. |
| T4 | Ilima, **Pawniard Active**, Slash 30 on Mega Lucario ex (12/12) | Energy on Pawniard (bench), nothing else | his line at least as good | medium | The Active would be a 50-HP Pawniard, the only Pawniard in the deck, facing a 3-Energy Mega Lucario ex. Kingambit is in hand and has no other route in. |
| T5 | Energy on Kingambit, **Helmet on the 10-HP Active Regigigas**, Mesagoza, end (12/12) | **Helmet on Kingambit**, Energy on Muk, end | his line at least as good | medium | The Helmet is a single copy. On Regigigas it is lost when Regigigas is KO'd. On Kingambit it gives -20 for the one Pokémon that must survive. |
| T6 | Helmet and Energy both on the **Active Muk** (12/12) | Helmet and Energy both on the **benched Kingambit** | unclear | low | Whether Muk survives the opponent's next hit. That damage isn't in cards.md. See T6 below. |
| T7 | Energy on the Active Grimer (8/12); Copycat in 8/12 seeds (cut at the first draw); the other 4 end the turn | Energy on Pawniard, no Copycat, end | his line at least as good | high | Copycat with his 4 other cards against an opponent hand of 1 draws 1 card, and shuffles away the only Rare Candy. |

## T1
- **km3:** Glimmet to bench slot 3, Muk onto Grimer, Darkness onto the Active Regigigas, end turn. It's identical in all 12 seeds.
- **He:** The same two plays, but the Darkness goes to Pawniard (slot 1).
- **Board after either line:** Regigigas 150 Active, Pawniard 50, Muk 110, Glimmet 60. Hand: Kingambit only.
- **Differences:** The Rare Candy isn't in hand, so Kingambit can't come this turn.
  - If he attaches to Pawniard, it has 1 of Kingambit's 2 Energy. One more attach next turn makes it Candy-ready on that same turn if he draws the Candy.
  - If km3 attaches to Regigigas, Pawniard has 0 and is a turn behind.
- **Regigigas Energy is fragile.** Regigigas is the Active wall, and his own plan is to pull it back with Ilima. Ilima returns the Pokémon to hand, so its Energy is discarded. That is exactly what the T2 board shows (2 Darkness in discard_energy).
- **Regigigas needs 3 Energy for Giga Turbo.** With 1 now it has no attack for two more turns, and the Muk evolution is the same in both lines.
- **Opponent next turn:** Mega Kangaskhan ex 180 with Lightning, Metal, Metal, plus Metal next turn = 4 Energy. Its damage isn't in cards.md. Regigigas at 150 is the Active either way and takes the same hit. Pawniard's exposure on the bench is the same whether it holds Energy or not.
- **Verdict:** his line is at least as good. Medium, because the opposing attack values are unknown.

## T2
- **km3:** Ilima, Regigigas (50 HP) to hand, Kingambit promoted, Regigigas re-placed on the bench at full HP, Darkness onto Kingambit, Overlord's Blade.
- **He:** Ilima, Glimmora (90) promoted, the second Glimmet placed on the bench, Darkness onto Glimmora, Venomous Hit. Regigigas stays in hand.
- **Damage.** Mega Pidgeot ex is 210.
  - km3: Blade is 60 + 40×0 = 60, so Pidgeot is at 150.
  - His: 30, so Pidgeot is at 180, and poison takes it to 170 at checkup.
  - Neither is a KO. Overlord's Blade needs 60 + 40k ≥ 210, which is k = 4, and I have 0 KOs.
- **Opponent next turn:** Active Mega Pidgeot ex 210 with Darkness, Darkness, Colorless, plus Darkness next turn = 4 Energy. A second Mega Pidgeot ex 210 is on the bench. Their damage isn't in cards.md.
- **What km3 exposes.**
  - Kingambit (140, no Helmet) is Active with 2 Energy against retreat 3, so it can't leave. It is the only Kingambit and the deck's win condition.
  - A Mega ex KO is 3 points on its own. The only way I win this board is a Pidgeot KO, which needs 4 prior KOs for the Blade (or chip + Blade), so Kingambit is nowhere near a win yet.
- **What his line exposes.** The sacrificed piece is Glimmora, which gives up 1 point only on tails (expected 0.5 points, per PLAN). A Glimmora KO raises the Blade to 60 + 40 = 100 for a Kingambit that stays safe on the bench.
- **What his line keeps.**
  - The 2nd Glimmet is on the bench and the 2nd Glimmora is in hand, so he evolves next turn ("both Glimmora get a turn").
  - Regigigas is back at 150 in hand (it was 50).
- **What km3 loses.** It leaves a Glimmet and a Glimmora in hand with no board spot for the Glimmet.
- **Verdict:** his line is at least as good. Medium, because the exact damage that would KO Kingambit is unknown.

## T3
- **km3:** Candy, Kingambit; Ilima, Regigigas (10 HP) to hand; Kingambit Active; Regigigas to the bench; Darkness onto Kingambit; Mesagoza; Blade.
- **He:** The same Candy and Ilima (Mesagoza earlier), Glimmora Active, Regigigas to the bench, Darkness onto Glimmora, Venomous Hit.
- **Damage on Drampa (100):**
  - km3: 60 + 40×0 = 60, so Drampa is at 40.
  - His: 30, so Drampa is at 70, then 60 after poison.
  - Nothing is KO'd. There is no target at or under 60, since Dratini is hidden under Dragonair.
- **Opponent next turn:**
  - Drampa 100 with Lightning (+Fire next turn = 2 Energy).
  - Drampa 100.
  - Mega Rayquaza ex 180 with Fire, Lightning (+Fire = 3 Energy).
  - Dragonair 80.
  - Rayquaza's damage isn't in cards.md.
- **What km3 does.** Putting Kingambit (140) Active with 2 Energy, with retreat 3 and no Helmet, exposes the Kingambit to Rayquaza and Drampa. The 20 extra damage doesn't change a KO.
- **What his line keeps.** Kingambit sits on the bench with 1 Energy, one attach from attacking once it is promoted. Mega Rayquaza ex is 180 HP and is a 3-point KO, and Blade = 60 + 40k ≥ 180 at k = 3. That is exactly the "3 KOs → 180" line in PLAN.
- **Mesagoza.** It is used in both lines. In his line it is used before Ilima. The only Pokémon still in his deck is the second Glimmora, so it is a coin flip at best.
- **Verdict:** his line is at least as good. Medium, because Rayquaza's damage is unknown.

## T4
- **km3:** Ilima, Regigigas (40) to hand, **Pawniard promoted to Active**, Regigigas placed on the bench at 150, Darkness onto Pawniard, Slash.
- **He:** Darkness onto the benched Pawniard and end. Regigigas stays Active at 40 HP and Ilima stays in hand.
- **Damage.** Slash is 30 on Mega Lucario ex (190), leaving it at 160. That is no KO and not a threat.
- **Opponent next turn:** Mega Lucario ex 190 with Fighting, Fighting (+Fighting next turn = 3 Energy). Hitmonchan ex 130, Riolu 70 and Tyrogue 30 are on the bench. Lucario's damage isn't in cards.md.
- **What km3 does.** With Pawniard Active at 50 HP, a 3-Energy Mega ex will KO it.
  - Pawniard is the only Pawniard in the deck and the only way to play Kingambit. Kingambit is already in hand, and the T4 board has no other Pawniard, so the win condition would be dead.
  - The opponent gets 1 point either way.
- **What his line does.** The Regigigas at 40 is weak to Fighting (cards.md), so any Lucario hit of 20 or more KOs it. His line gives that point away on the piece he cares about least, and the Blade goes to 60 + 40 = 100.
  - Cost: he loses the only Regigigas, and Ilima is dead afterwards because Regigigas is the only [C] Pokémon.
- **What neither line tried.** Ilima, then promote Glimmet (60) or Muk (110), and re-place Regigigas at 150. That could beat both lines. I can't classify it because neither side played it.
- **Verdict:** his line is at least as good. Medium, because Lucario's damage is unknown.

## T5
- **km3:** Darkness onto Kingambit (now 2), Helmet onto Regigigas (Active, 10 HP, retreat 4), Mesagoza, end.
- **He:** Helmet onto Kingambit (slot 3), Darkness onto Muk (slot 1, now 2), end.
- **Opponent next turn:** Drampa 90 poisoned with Lightning (+Lightning next turn = 2 Energy), Drampa 100 with Fire, Fire, Mega Rayquaza ex 180 with Fire, Lightning (+Lightning = 3 Energy), Dragonair 80. Damage values aren't in cards.md.
- **Regigigas.**
  - It has 10 HP, no Energy and retreat 4, so it can't retreat. With the Helmet it takes -20 and survives only if the raw damage is under 30.
  - If it is KO'd, the Helmet goes with it. The deck has only 1 Helmet.
  - If it is KO'd (opponent +1 point), the Blade goes to 60 + 40 = 100. That kills Drampa at 80 or 100 and Dragonair at 80.
- **Kingambit.** In his line it is the Pokémon promoted after Regigigas goes down. It is 140 HP with -20 per hit, and it has 1 Energy, so one attach next turn makes the 2 it needs.
  - km3's early Energy on it only saves a future attach.
  - His Muk attach isn't explained by his plan. It costs nothing because Kingambit still reaches 2 next turn. At worst it is a tempo loss.
- **Mesagoza.** All 9 Pokémon are already on board, in hand or under evolutions, so the deck has none left. Using the Stadium does nothing in km3's line, and skipping it loses nothing.
- **Verdict:** his line is at least as good. Medium. The only way km3 is better is if Regigigas survives a sub-30 hit.

## T6
- **Position.** Points are 1-0 to me, with 1 KO of mine counted, so the Blade is 60 + 40 = 100 now.
- **He needs 2 more points.** An ex KO would win: Indeedee ex 130 is 2 points, and Mega Diancie ex 40 HP (benched, 4 Psychic Energy) is 3 points.
- **Neither line attacks this turn.** Muk has Colorless, and with the attach it holds 2 of the 3 Energy that Sludge Bomb [DCC] needs. Regigigas can't attack from the bench. Ilima has no damaged [C] target.
- **km3:** Helmet and Darkness onto the Active Muk, so Muk is 110 with -20 and holds Colorless + Darkness. Kingambit stays on 0 Energy.
  - **If Muk survives:** next turn it attaches again, giving 3 Energy, and Sludge Bomb does 70. That kills a Diancie at 40 outright (the win). It leaves Indeedee at 60 on the first hit.
  - **If Muk is KO'd:** Kingambit has 0 Energy and one attach makes 1, so it can't attack. Regigigas can't attack either, because Muk's ability only lets it attack while Muk is in play (Seal of Antiquity is switched off by Muk, per PLAN).
- **He:** Helmet and Darkness onto the benched Kingambit. Muk (110, 1 Colorless) stays Active with no Helmet.
  - **If Muk is KO'd:** the opponent gets 1 point, the Blade becomes 60 + 40×2 = 140, and Kingambit (140 HP, -20, 1 Energy) is promoted. After one attach it has 2 Energy and the 140 Blade KOs Indeedee (130) or Diancie (40). That is a win.
  - **If Muk survives:** nothing in his line can hit next turn (Muk would reach 2 Energy, Kingambit is benched, and Muk can't retreat for 3). He is a turn or two slower than km3.
- **The turn splits on one number.** The line that is better depends on whether the opponent's hit KOs Muk (his line wins on the spot) or leaves it alive (km3's line wins). Indeedee has 0 Energy (1 after attach). The Diancie ex would have to be promoted first, and then its damage against 110 HP (130 with the Helmet) isn't in cards.md.
- **Verdict:** unclear, low confidence. It is a real trade-off, not a case where one line dominates.

## T7
- **km3:** Eight seeds play Copycat (1, 3, 5, 6, 8, 9, 11, 12), cut at the first draw. The other four (2, 4, 7, 10) attach and end. Attach is usually to the Active Grimer (slot 0); seed 1 uses Pawniard, seed 9 uses Regigigas. Because the Copycat plans are cut, I can't see what km3 does after the draw.
- **He:** Darkness onto Pawniard (slot 1), end turn. No Copycat.
- **Copycat arithmetic.**
  - His hand is 5: Copycat, Glimmora, Glimmora, Rare Candy, Lucky Ice Pop.
  - After playing Copycat, 4 cards are shuffled into the deck, and he draws 1 (opponent hand = 1). That is a net loss of 3 cards.
  - The deck would then hold 14 cards. The only Kingambit is 1 of those 14, and if he drew it the Rare Candy would be shuffled away.
  - PLAN says he skips Copycat when he holds a card he really needs, and uses it when he has 2 cards and the opponent 8. Here it is 4 cards against 1.
- **Attach.** The Active Grimer (70 HP, can't evolve: no Muk in hand) is the likely sacrifice, so its Energy would be wasted. Pawniard gets 1 of the 2 Energy needed for Kingambit ("two turns"). This is a judgement and I'd call it his line's smaller edge.
- **Opponent next turn:** Dedenne ex 120 Active (Lightning, Electrical Cord), Emolga 70, Dedenne ex 120 (Rocky Helmet), Zeraora 90 (Lightning, Small Balloon). The opponent hand is 1 card, so no hidden-card hazard. Damage isn't in cards.md.
- **Verdict:** his line is at least as good. High, on the Copycat arithmetic.
