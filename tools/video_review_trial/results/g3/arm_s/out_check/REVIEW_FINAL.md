# Review: Dustin (Dacz8976) vs Zavs65, ranked match (checked)

**Header**
- Deck / QR: A "Share With 2D Pattern Code" QR dialog is shown at t=0. The deck name is not readable. The ranked screen shows "Master Ball Rank", 970 pts.
- Went first: the opponent. The coin lands on "Going second" at t≈21, and "You are going second" shows at t=24.
- Final score: Dustin 0, opponent 2. The opponent's points came at t≈142-143 (Magikarp KO) and t≈213-215 (Feebas KO). [checked: corrected]
- End: Dustin conceded during opponent global turn 15 (menu → "Concede" at t≈498, "Are you sure you want to concede?" → Concede at t≈499). The "Defeat" screen follows at t≈500-502. This is `concede_dustin`. [checked: corrected]
- Global turns: 15 (the last was the opponent's, in progress at the concession).
- Result-screen statistics: not shown in the frames. The screen only reads "Defeat".
- Confidence: every attack, HP change, KO, point and Energy attachment below was checked against the frames. Two opponent card identities are still unread (the turn-7 Tool and a face-down card at t≈302-303). [checked: corrected]

**Opening**
- Dustin's opening hand (t=24): Magikarp, Cabbie, Copycat, Poké Ball, Mega Gyarados ex.
- Dustin's Active is Magikarp (30 HP), placed at t≈25-27. No Bench at the start.
- Dustin's Energy Zone: Water.
- Opponent's Active: Furfrou (70 HP), with the Fur Coat Ability ("This Pokémon takes −20 damage from attacks"). The opponent has no Bench at setup (t=40 shows three empty Bench slots). [checked: corrected]
- Opponent's Energy Zone: Lightning.

**Global 1: opponent, t≈34-60**
- The opponent plays Poké Ball (t≈37) and a second Poké Ball (t≈42). They put Eevee (60, shown at t≈43) and Oricorio (70, shown at t≈46) into the hand. [checked: corrected]
- The opponent benches Eevee (60 HP) and Oricorio (70 HP), both by t≈44-48. Oricorio's Ability is Safeguard: it prevents all damage done to Oricorio by attacks from the opponent's Pokémon ex. [checked: corrected]
- The opponent plays Protective Poncho (a Tool) at t≈56. It goes on Eevee (Tool icon on Eevee, t=59). [checked: corrected]
- No attack. No Energy is attached (the opponent went first, and no Energy shows on any opponent Pokémon at t=59). [checked: corrected]
- Board: opponent Active Furfrou 70; Bench Oricorio 70, Eevee 60 (Protective Poncho). Dustin Active Magikarp 30.

**Global 2: Dustin, t≈61-118**
- Draw at t≈61-62: Mega Sharpedo ex. The hand at t=63 is Cabbie, Copycat, Poké Ball, Mega Gyarados ex, Mega Sharpedo ex.
- t≈69-75: Poké Ball (t≈70) gets Feebas (30 HP, card shown at t≈72), and Feebas is benched at t≈75. [checked: corrected]
- t≈97-106: Cabbie (t≈97) fetches the Stadium Soothing Shore (shown at t≈99). Soothing Shore is played at t≈105-106. Its text: at the end of each player's turn, that player heals 20 damage from each of their Pokémon that has any Water Energy attached. [checked: corrected]
- Energy: 1 Water from the Energy Zone to Magikarp at t≈107-108. [checked: corrected]
- t≈108-117: Magikarp attacks with Expert Splasher (10, +20 if both coins are heads). The result is **2 tails, 0 heads** (counter at t=113). That is 10 damage, cut to 0 by Fur Coat (−20). Furfrou stays at 70 (t≈117-119). [checked: corrected]
- Soothing Shore heals nothing (Magikarp is undamaged).
- Board: Dustin Active Magikarp 30 (1 Water); Bench Feebas 30. Opponent unchanged.

**Global 3: opponent, t≈119-147**
- The opponent attaches Lightning Energy from the Energy Zone to Furfrou (t≈126-127).
- Furfrou attacks with Double Headbutt (flip 2 coins, 30 per heads). The result is 1 heads, 1 tails (t≈134-135), so 30 damage. Magikarp 30 → 0 is Knocked Out at t≈138-140. [checked: corrected]
- Point: +1 for the opponent at t≈142-143. Score 0-1. [checked: corrected]
- Dustin promotes Feebas (30 HP) to Active at t≈145-147. [checked: corrected]

**Global 4: Dustin, t≈148-187**
- Draw: Mega Sharpedo ex (alternate-art card shown at t≈150). [checked: corrected]
- Copycat is played at t≈164-165 (shuffle the hand into the deck, then draw a card for each card in the opponent's hand). The new hand is shown at t≈170-174: Elegant Cape, Irida, Copycat, Carvanha, Mega Sharpedo ex. **Irida is not played this turn** (it is still in hand at t=200). [checked: corrected]
- Carvanha (50 HP) is benched at t≈176-177.
- Elegant Cape (a Tool: a Stage 1 Pokémon gets +30 HP) is attached to the Benched Carvanha at t≈181-183 ("Please choose a Pokémon to attach the Pokémon Tool to"). [checked: corrected]
- Energy: 1 Water from the Energy Zone to the Benched Carvanha at t≈184-185 (Water icon on Carvanha, t=200). [checked: corrected]
- No attack. Soothing Shore heals nothing (no damage on Dustin's side).
- Board: Dustin Active Feebas 30; Bench Carvanha 50 (Elegant Cape, 1 Water). Opponent Active Furfrou 70 (1 Lightning); Bench Oricorio 70, Eevee 60 (Poncho). Score 0-1. [checked: corrected]

**Global 5: opponent, t≈188-229**
- The opponent attaches Lightning Energy from the Energy Zone to the Benched Oricorio (t≈197-199; Lightning icon on Oricorio at t=200). [checked: corrected]
- Furfrou attacks with Double Headbutt. 1 heads (t≈204-205), so 30 damage. Feebas 30 → 0 is Knocked Out at t≈208-210. [checked: corrected]
- Point: +1 for the opponent at t≈213-215. Score 0-2.
- Dustin promotes Carvanha (50 HP) at t≈216-228 ("Please choose a Pokémon to switch in").

**Global 6: Dustin, t≈229-270**
- Draw: Mega Gyarados ex (shown at t≈231). [checked: corrected]
- Dustin evolves the Active Carvanha into Mega Sharpedo ex at t≈235-238 (190 HP, plus 30 from Elegant Cape = 220; "Stage 1 Pokémon get +30 HP", t≈240). [checked: corrected]
- Copycat is played at t≈241-243. **Wallace is not played this turn.** The Wallace cards at t≈246-249 are the new hand being shown. [checked: corrected]
- A second Carvanha (50 HP) is benched at t≈252-255. [checked: corrected]
- Energy: 1 Water from the Energy Zone to the Active Mega Sharpedo ex at t≈258 (2 Water now). [checked: corrected]
- A second Elegant Cape is attached to the Benched Carvanha at t≈261 (Tool icon on the Benched Carvanha, t=288). [checked: corrected]
- Mega Sharpedo ex attacks with Turbo Shark (70; take a Water Energy from the Energy Zone and attach it to 1 Benched Water Pokémon) at t≈264-266. The damage popup reads "50" (70 − 20 Fur Coat). Furfrou 70 → 20 at t≈268. Turbo Shark's Water goes to the Benched Carvanha (Water icon on it at t=288/300). [checked: corrected]
- Board at t=270: Dustin Active Mega Sharpedo ex 220 (Elegant Cape, 2 Water); Bench Carvanha 50 (Elegant Cape, 1 Water). Opponent Active Furfrou 20 (1 Lightning); Bench Oricorio 70 (1 Lightning), Eevee 60 (Poncho). Score 0-2. [checked: corrected]

**Global 7: opponent, t≈271-318**
- Eevee evolves into Sylveon ex (100 HP, Ability Soothing Ribbon) at t≈276-278. Soothing Ribbon is used at t≈282. Furfrou heals 30, 20 → 50 (popup "30", t≈284-285). [checked: corrected]
- Furfrou retreats. Oricorio (70) becomes Active at t≈288-290. Furfrou's Lightning is discarded (no Energy on Furfrou at t=288). [checked: corrected]
- The opponent attaches Lightning Energy from the Energy Zone to Oricorio at t≈291 (2 Lightning, t=294). [checked: corrected]
- A Pokémon Tool (name not readable) goes on Oricorio at t≈297-299. "+20 HP" shows at t≈300-301, and Oricorio goes 70 → 90. [checked: corrected]
- A face-down card animation at t≈302-303 is not identified. Shinx (60 HP) is benched by t≈308. [checked: corrected]
- Oricorio uses Zzzap (50). Mega Sharpedo ex has Lightning Weakness (+20), so it takes 70: 220 → 150 at t≈315-317. [checked: corrected]
- Board: Opponent Active Oricorio 90 (Tool, 2 Lightning); Bench Furfrou 50, Sylveon ex 100, Shinx 60. Dustin Active Mega Sharpedo ex 150 (2 Water); Bench Carvanha 50 (Cape, 1 Water). [checked: corrected]

**Global 8: Dustin, t≈318-349**
- Draw: Lisia (shown at t≈321). **Lisia is not played this turn.** It stays in hand (t=371). [checked: corrected]
- Wallace is played at t≈327-330. It evolves the Benched Carvanha into a second Mega Sharpedo ex (t≈331-335, 220 HP with Elegant Cape; "Stage 1 Pokémon get +30 HP"). [checked: corrected]
- Energy: 1 Water from the Energy Zone to the Benched Mega Sharpedo ex at t≈337. [checked: corrected]
- The Active Mega Sharpedo ex (150) retreats at t≈338. The Bench Mega Sharpedo ex (220) becomes Active at t≈340-341. [checked: corrected]
- No attack. "End your turn? An attack can be used" at t≈345; OK.
- Soothing Shore at t≈346-348: the Benched Mega Sharpedo ex heals 150 → 170. The Active stays at 220 (undamaged). [checked: corrected]
- Board: Dustin Active Mega Sharpedo ex 220 (Cape, 2 Water); Bench Mega Sharpedo ex 170 (Cape, 2 Water). Opponent unchanged. Score 0-2. [checked: corrected]

**Global 9: opponent, t≈350-371**
- The opponent attaches Lightning Energy from the Energy Zone to the Benched Shinx (t≈360-361; Lightning icon on Shinx at t=371). [checked: corrected]
- Sylveon ex's Soothing Ribbon is used at t≈356-358. Furfrou heals 50 → 70. [checked: corrected]
- Oricorio uses Zzzap (50 + 20 Weakness = 70) at t≈365-369. The Active Mega Sharpedo ex goes 220 → 150 (t≈369-370). [checked: corrected]
- Board: Opponent Active Oricorio 90 (2 Lightning); Bench Furfrou 70, Sylveon ex 100, Shinx 60 (1 Lightning). Dustin Active Mega Sharpedo ex 150; Bench Mega Sharpedo ex 170. [checked: corrected]

**Global 10: Dustin, t≈372-394**
- Draw: Milotic ex (shown at t≈374).
- Lisia is played at t≈376-377. "There are no cards in the deck that can be the target of the effect" shows at t≈379-380. [checked: corrected]
- Energy: 1 Water from the Energy Zone to the Active Mega Sharpedo ex (150) at t≈382. [checked: corrected]
- The Active retreats at t≈383. The Benched Mega Sharpedo ex (170) becomes Active at t≈385-386. [checked: corrected]
- No attack ("An attack can be used" prompt at t≈390, OK).
- Soothing Shore at t≈392-394: Active 170 → 190, Bench 150 → 170. [checked: corrected]
- Board: Dustin Active Mega Sharpedo ex 190 (Cape, 2 Water); Bench Mega Sharpedo ex 170 (Cape, 3 Water). [checked: corrected]

**Global 11: opponent, t≈395-411**
- The opponent attaches Lightning Energy from the Energy Zone to the Benched Shinx (2 Lightning on Shinx at t=412). [checked: corrected]
- Oricorio attacks with Zzzap. Dustin's Active takes 70 (Weakness), 190 → 120 at t≈408-411. [checked: corrected]
- Board: Dustin Active Mega Sharpedo ex 120; Bench Mega Sharpedo ex 170. Opponent Active Oricorio 90; Bench Furfrou 70, Sylveon ex 100, Shinx 60 (2 Lightning). [checked: corrected]

**Global 12: Dustin, t≈412-448**
- Draw: not identified (the hand stays Wallace, Mega Gyarados ex, Soothing Shore, Milotic ex, Irida; Irida is shown at t≈414). [checked: corrected]
- Irida is played at t≈429. It heals 40 from each Water Pokémon with Energy: Active 120 → 160 and Bench 170 → 210 (t≈432-434). [checked: corrected]
- Energy: 1 Water from the Energy Zone to the Active (160) at t≈436. [checked: corrected]
- The Active retreats at t≈437-438 ("Please choose a Pokémon to switch in"). The Bench Mega Sharpedo ex (210) becomes Active at t≈440-441. [checked: corrected]
- No attack ("An attack can be used", t≈444).
- Soothing Shore at t≈445-448: Active 210 → 220 (capped at max), Bench 160 → 180. [checked: corrected]
- Board: Dustin Active Mega Sharpedo ex 220 (Cape, 3 Water); Bench Mega Sharpedo ex 180 (Cape, 3 Water). [checked: corrected]

**Global 13: opponent, t≈449-474**
- Rare Candy is played at t≈454. The Benched Shinx evolves into Luxray (Stage 2, 130 HP) at t≈456-458. [checked: corrected]
- Oricorio retreats (1 Lightning discarded; 1 left on Oricorio at t=465). Luxray becomes Active at t≈460. [checked: corrected]
- The opponent attaches Lightning Energy from the Energy Zone to Luxray at t≈461 (3 Lightning, t=465). [checked: corrected]
- Luxray uses Volt Bolt (discard all Lightning Energy from this Pokémon; 120 damage to 1 of the opponent's Pokémon) on the Active, at t≈471-473. The popup reads "Weakness 140": 220 → 80. [checked: corrected]
- Board: Dustin Active Mega Sharpedo ex 80; Bench Mega Sharpedo ex 180. Opponent Active Luxray 130 (no Energy); Bench Furfrou 70, Sylveon ex 100, Oricorio 90 (Tool, 1 Lightning). [checked: corrected]

**Global 14: Dustin, t≈475-489**
- "No cards left in deck; unable to draw cards" at t≈476-477. No draw.
- No Energy is attached from the Energy Zone ("End your turn? Energy can be attached" prompt at t≈479). [checked: corrected]
- Mega Sharpedo ex attacks with Turbo Shark at t≈480-481: 70 damage, Luxray 130 → 60. Turbo Shark's Water goes to the Benched Mega Sharpedo ex (4 Water at t=495). [checked: corrected]
- Soothing Shore at t≈486-488: Active 80 → 100, Bench 180 → 200.
- Board: Dustin Active Mega Sharpedo ex 100 (Cape, 3 Water); Bench Mega Sharpedo ex 200 (Cape, 4 Water). Opponent Active Luxray 60. [checked: corrected]

**Global 15: opponent, t≈490-500**
- The opponent plays Volkner at t≈495-497 (Volkner is on top of the discard pile at t=498). Luxray goes from no Energy (t=497) to 2 Lightning (t=498). The Energy Zone Lightning is still unattached. [checked: corrected]
- At t≈498 Dustin opens the menu and concedes (t≈499). "Defeat" follows at t≈500-502. [checked: corrected]
- Final board at t=498: Dustin Active Mega Sharpedo ex 100 (Elegant Cape, 3 Water); Bench Mega Sharpedo ex 200 (Elegant Cape, 4 Water). Opponent Active Luxray 60 (2 Lightning); Bench Furfrou 70, Sylveon ex 100, Oricorio 90 (Tool, 1 Lightning). Score 0-2. [checked: corrected]

**Hand at the start of Dustin's turns**
- Turn 2 (t=63): Cabbie, Copycat, Poké Ball, Mega Gyarados ex, Mega Sharpedo ex.
- Turn 4 (t≈150): Copycat, Mega Gyarados ex, Mega Sharpedo ex, Mega Sharpedo ex (draw). [checked: corrected]
- Turn 6 (t≈231): Irida, Copycat, Mega Sharpedo ex, Mega Gyarados ex (draw). [checked: corrected]
- Turn 8 (t≈321): Wallace, Wallace, Mega Gyarados ex, Soothing Shore, Lisia (draw). [checked: corrected]
- Turn 10 (t≈374): Wallace, Mega Gyarados ex, Soothing Shore, Lisia, Milotic ex (draw). [checked: corrected]
- Turn 14 (t≈476): Wallace, Mega Gyarados ex, Soothing Shore, Milotic ex (no draw; deck empty). [checked: corrected]
