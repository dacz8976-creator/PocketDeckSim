# Full-battle visual review draft

**Current status: completed full-battle review accepted by the lead; original archived unchanged in `Reviewed`. Excluded from Ladder Log.**

Source: `20261001_020413000_iOS.MP4`, 326.96 seconds. Reviewer: `sol_auto_evening_020413000`. Model: `gpt-6.1-sol`, reasoning effort `high`. Review date: 2026-10-01 UTC, September 30 America/Chicago. Status: full review accepted by the lead, registered and archived.

The immutable `SOURCE.json` binds the filename, 600860503 bytes and SHA-256 `87fc6d7dd7f19ee01bec07969cf6991f8618315c9747a6ab18233c12436e65d4`. This review preserves that file and the original video. This worker has not changed the global index, event log, media locations, Ladder Log, or original location.

## Scope, mode and result

One complete battle is visible, from loading and setup to the results screen. The opening explicitly identifies an AI opponent. The green checked Auto indicator is visible throughout ordinary play, including the decisive turns. No Auto toggle, pause menu or manual takeover is observed. Owner testimony independently classifies this as an Auto AI game, excluded from the Ladder Log.

Dacz8976 goes second and loses on turn 17 against `Mega Gardevoir ex & Mimikyu ex Deck (Deluxe Pack: Mega)`. The owner earns 2 points by knocking out Wynaut and Meloetta. The opponent earns two successive 2-point awards by knocking out Guzzlord ex and Crobat ex, 4 awarded points in total. The game's three-circle HUD and results screen display 3 opponent points because the display caps at the winning threshold. The final attack is direct damage from Fantasia Force, not poison damage. The final results show 17 turns, owner points 2, opponent HUD points 3, and Damage done 440. The recording ends after this complete result is visible, not during an unresolved battle.

Useful terminal references: `native/t0314.00.jpg` for Crobat HP 0 and surviving benches; `native/t0320.00.jpg` for the terminal award; `native/t0325.00.jpg` for Defeat and challenge; `native/t0326.50.jpg` for the complete results panel.

## Visible cores and card versions

The owner's played core is Guzzlord ex, Zubat/Golbat/Crobat ex, and Gastly/Haunter/Mega Gengar ex, with Darkness Energy. Two Crobat ex copies are played, one through Golbat and the other through Rare Candy. Team Rocket's Weezing ex is drawn on turn 12 but remains in hand. No Team Rocket's Koffing is revealed, so a complete Weezing line must not be inferred. Lusamine remains in hand after its turn-4 draw; two Rare Candy copies become visible, with one used on the second Zubat. The full 20-card deck and unrevealed cards are unknown.

The opponent plays Wynaut, Mimikyu ex, Ralts/Kirlia/Mega Gardevoir ex, Meloetta, Bramblin, Peculiar Plaza, Poké Ball, Diantha and Potion. Psychic Energy is visible. The exact unseen opponent cards and deck counts remain unknown even though the challenge title supplies its advertised core.

Mechanically relevant identities come directly from visible card text:

- Guzzlord ex: 170 HP, Grindcore 30 for two Colorless, with repeated flips until tails and Energy discard for heads; Tyrannical Hole 120 for three Darkness plus one Colorless.
- Wynaut: 30 HP, Stompy Jammer 10 with a zero-Energy cost, increasing the defending Pokémon's attack cost by one Colorless on the next turn.
- Mimikyu ex: 120 HP, Disguise blocks the first attack damage after it comes into play; Claw Slash 70 for two Psychic. Retreat cost two, reduced to zero by Peculiar Plaza.
- Crobat ex: 170 HP, Venomous Slash 70 for one Darkness and inflicts Poison. Its retreat cost is one Colorless, so Peculiar Plaza does not make this Darkness-type Pokémon's retreat free.
- Meloetta: 70 HP, Strange Singing puts a random Psychic Pokémon from the deck into hand at the beginning of the turn if Active. It does not generate Energy. Psyshot costs two Psychic and is not used here.
- Mega Gardevoir ex: Stage 2 evolving directly from Kirlia, 210 HP, Fantasia Force 110 for two Psychic; it takes three Psychic Energy from the Energy Zone and distributes them to Psychic Pokémon. A Mega ex knockout would award three points, but none is knocked out here.
- Mega Gengar ex: Stage 2 evolving directly from Haunter, 210 HP, Labyrinth of Shadows 120 for three Darkness plus one Colorless, with a next-turn restriction on the opponent playing Trainers from hand. This attack is never used here.
- Diantha visibly heals 90 from a Psychic Pokémon with at least two Psychic Energy, then discards two Psychic Energy from that Pokémon. Potion heals 20. Pokémon Center Lady heals 30 and clears Special Conditions.

No outside catalog was necessary to identify these consequential effects because the source displays their text. This report does not invent set/card numbers or treat alternate Crobat artwork as a different mechanic.

## Full time-coded narrative

Times are source-video seconds. Turn boundaries are rounded phase boundaries; exact native frames have filename timestamps. Overview labels use the extractor's fps midpoint convention.

### 0.00-22.00: loading, opponent and setup

The recording begins with the loading screen, then the versus screen identifies `AI Opponent` and Dacz8976. The coin/turn-order display says Going second. The owner starts Guzzlord ex Active at 170 HP with an empty Bench. The visible remaining opening hand includes Golbat, Professor's Research, Crobat ex and Pokémon Center Lady. The opponent starts Wynaut Active at 30 HP, with Mimikyu ex 120 and Ralts 60 on the Bench. The Disguise explanatory banner is visible. No Energy is attached at setup. The Auto indicator is already checked.

References: `overview/sheet_01.jpg`, `native/t0006.00.jpg`, `native/t0017.00.jpg`, `native/t0021.00.jpg`.

### Turn 1, opponent, about 22.00-33.00

Wynaut uses Stompy Jammer for 10, taking Guzzlord 170 to 160. The next-turn attack-cost increase is displayed. Wynaut has no attached Energy. No setup change or Trainer is observed in this turn.

References: `native/t0025.00.jpg`, `native/t0028.00.jpg`, `native/t0031.00.jpg`, overview frames 8-11.

### Turn 2, owner, about 33.00-54.00

A Poké Ball search and Zubat reveal are visible. The Spin Turn Zubat, 50 HP, is benched on the right. Professor's Research is used, and the ensuing reveals include a second Crobat ex and Gastly. Gastly, 60 HP with Mumble 20, is benched in the middle. One Darkness Energy is attached to Guzzlord. No attack occurs: Grindcore's base cost is two and the Stompy Jammer modifier raises the current requirement to three, while Guzzlord has only one Energy. Guzzlord remains at 160 HP, score 0-0.

References: `overview/sheet_02.jpg`, `native/t0041.00.jpg`, `native/t0042.00.jpg`, `native/t0044.00.jpg`, `native/t0045.00.jpg` through `native/t0054.00.jpg`. The card-transfer animations and later discard pile establish both Poké Ball and Research use; the narration does not require identifying every ordinary draw before its reveal.

### Turn 3, opponent, about 54.00-66.00

Ralts evolves into Kirlia, 80 HP with Double Spin. One Psychic Energy is attached to Mimikyu ex. Meloetta, 70 HP, is benched on the left. Wynaut again uses Stompy Jammer: Guzzlord 160 to 150, with another next-turn cost increase. A phone notification briefly covers the upper screen around 64-71 seconds, but the before/after board and attack banner show the meaningful actions.

References: `native/t0055.00.jpg`, `native/t0057.00.jpg`, `native/t0058.00.jpg`, `native/t0059.00.jpg`, `native/t0060.00.jpg`, overview frames 19-22.

### Turn 4, owner, about 66.00-75.00

Lusamine is drawn and its card text is shown. The right Zubat evolves into Golbat, 80 HP with Bite 30. A second Darkness is attached to Guzzlord. The owner ends without attacking. Guzzlord has two Energy, still below the current three-Energy Grindcore requirement after Stompy Jammer. Lusamine is not played; the opponent has no point yet, so its displayed condition is not met. Gastly remains unevolved, no Tools or additional Bench Pokémon are played, and score remains 0-0.

References: `native/t0072.00.jpg`, `native/t0074.00.jpg`, `native/t0075.00.jpg`, overview frames 23-26.

### Turn 5, opponent, about 75.00-92.00

Wynaut retreats to the Bench and Mimikyu ex becomes Active. Wynaut's printed retreat cost is zero. The opponent uses Poké Ball; the retrieved hidden card is not established and the Bench is already full. A second Psychic is attached to Mimikyu. Claw Slash deals 70, taking Guzzlord from 150 to 80. No poison or burn is inflicted. Disguise remains available for Mimikyu's first received attack damage.

References: `native/t0078.00.jpg`, `native/t0079.00.jpg`, `native/t0081.00.jpg`, `native/t0086.00.jpg`, `native/t0090.00.jpg`, overview frames 27-31. The 90 HP number in the attack animation at 90 seconds is an intermediate HP animation, not a final damage value; the settled turn-6 starting value is 80.

### Turn 6, owner, about 92.00-116.00

The other Zubat artwork, 50 HP with Bite 20, is drawn and remains in hand. Golbat evolves into the first Crobat ex, 170 HP. Pokémon Center Lady is played on Guzzlord, healing 30 from 80 to 110. A third Darkness is attached to Guzzlord. Grindcore is used. Mimikyu's Disguise prevents its attack damage, leaving Mimikyu at 120. The Energy-discard flip still occurs: the source clearly shows zero heads and one tails, so Mimikyu keeps both Psychic Energy. No point is awarded.

References: `native/t0099.00.jpg`, `native/t0102.00.jpg`, `native/t0105.00.jpg`, `native/t0106.00.jpg`, `native/t0110.00.jpg`, `native/t0113.60.jpg`, `native/t0114.60.jpg`.

### Turn 7, opponent, about 116.00-133.00

Peculiar Plaza is played, reducing the retreat cost of Psychic-type Pokémon by two. Mimikyu retreats for zero Energy into Wynaut, preserving its two Psychic. A Psychic Energy goes onto Kirlia. Wynaut uses Stompy Jammer, taking Guzzlord 110 to 100 and reapplying the next-turn attack tax. The Plaza stays in play for the rest of the battle.

References: overview frames 40-45, `native/t0123.00.jpg`, `native/t0126.00.jpg`; the Kirlia attachment is visible in the settled following-turn board at `native/t0140.00.jpg` and `native/t0156.00.jpg`.

### Turn 8, owner, about 133.00-151.00

Haunter is drawn and evolves Gastly in the middle Bench slot to 80 HP, with Spin Turn 40. A fourth Darkness is attached to Guzzlord. Despite having four Energy, Tyrannical Hole currently requires five because of Stompy Jammer, so the owner uses Grindcore. It deals 30 and knocks out the 30-HP Wynaut. The source says `No Energy attached`; no Energy-discard coin sequence is shown for this zero-Energy target. The owner earns point 1. The opponent promotes Meloetta at 70 HP. Guzzlord remains at 100 HP with four Darkness.

References: `native/t0137.00.jpg`, `native/t0138.00.jpg`, `native/t0140.00.jpg`, `native/t0142.00.jpg`, `native/t0144.00.jpg` through `native/t0146.00.jpg`, `native/t0152.00.jpg`.

### Turn 9, opponent, about 151.00-162.00

Meloetta is Active at turn start, and Strange Singing activates. A retrieved Psychic Pokémon goes into the opponent's hand without a public identity reveal. Bramblin, 60 HP with Petty Grudge, is then benched into the vacated left slot. A second Psychic is attached to Kirlia. Meloetta has no Energy and makes no attack. Guzzlord remains at 100 HP. Score is 1-0.

References: `native/t0152.00.jpg`, `native/t0156.00.jpg`, `native/t0158.00.jpg`, `native/t0159.00.jpg`, `native/t0161.00.jpg`, `native/t0167.00.jpg`. Bramblin's identity was checked at native resolution, rather than guessed from the small pink Bench card.

### Turn 10, owner, about 162.00-181.00

Rare Candy is drawn but not used. The generated Darkness is attached to benched Crobat ex, giving it one Energy; Guzzlord stays at four. The Stompy Jammer effect has expired because Meloetta did not use it. Guzzlord uses Tyrannical Hole for 120 plus 20 weakness, shown as 140, knocking out Meloetta from 70 HP. The owner earns point 2, leading 2-0. Mimikyu ex is promoted at 120 with two Psychic. The attack's reported 140 includes overkill, rather than implying Meloetta had 140 remaining HP.

References: `native/t0161.00.jpg`, `native/t0165.00.jpg`, `native/t0167.00.jpg`, `native/t0169.00.jpg`, `native/t0170.00.jpg`, overview frames 57-61.

### Turn 11, opponent, about 181.00-211.00

Kirlia evolves directly into Mega Gardevoir ex, 210 HP. The regular attachment brings it from two to three Psychic. Mimikyu retreats for free under Peculiar Plaza, keeping its two Psychic, and Mega Gardevoir becomes Active. Fantasia Force hits Guzzlord for 110, knocking it out from 100 HP. The attack's Energy distribution brings Mega Gardevoir from three to five Psychic and Mimikyu from two to three. The opponent earns 2 points, tying the awarded score 2-2. The owner promotes the first Crobat ex, 170 HP with one Darkness. Haunter remains 80 with no Energy. There is no burn or poison on Guzzlord.

References: `native/t0188.00.jpg`, `native/t0192.00.jpg`, `native/t0194.00.jpg`, `native/t0197.00.jpg` through `native/t0200.00.jpg`, overview frames 68-71.

### Turn 12, owner, about 211.00-227.00

Team Rocket's Weezing ex, 140 HP, is drawn. Its Boiler Smog text is shown, but it stays in hand; no Koffing is in play to evolve. The second Zubat, Bite version, is benched on the right at 50 HP. One Darkness is attached to Haunter. Crobat uses Venomous Slash for 90 including weakness: Mega Gardevoir 210 to 120, then ordinary Poison 10 takes it to 110 at the turn boundary. Crobat remains 170. Score stays 2-2.

References: `native/t0213.00.jpg`, `native/t0219.00.jpg`, `native/t0221.00.jpg`, `native/t0222.00.jpg`, `native/t0224.00.jpg`, `native/t0226.00.jpg`. The poison amount is directly corroborated by this state change and subsequent explicit Poison 10 banners.

### Turn 13, opponent, about 227.00-243.00

Diantha is played on poisoned Mega Gardevoir. It heals 90 from 110 to 200 and discards two Psychic, reducing five to three. Healing alone does not clear Poison; the status remains visible. The regular attachment adds one Psychic back, reaching four. Fantasia Force deals 110 to Crobat, 170 to 60, and its distribution leaves Mega Gardevoir with five Psychic and Bramblin with two. Poison 10 then takes Mega Gardevoir from 200 to 190 at the turn boundary. No points are scored.

References: `native/t0229.00.jpg`, `native/t0230.50.jpg`, `native/t0231.00.jpg` through `native/t0236.00.jpg`, `native/t0237.00.jpg`, `native/t0239.00.jpg`, `native/t0240.00.jpg`, `native/t0242.00.jpg`, `native/t0246.00.jpg`.

### Turn 14, owner, about 243.00-268.00

A second Rare Candy is drawn. One Rare Candy evolves the benched Bite Zubat directly into the second Crobat ex, 170 HP. The first Crobat ex, at 60 HP, retreats and pays its one-Energy retreat cost, discarding its Darkness. Peculiar Plaza applies only to Psychic-type Pokémon, so it does not reduce this Crobat's cost. The second Crobat is promoted and gets the regular Darkness attachment. It uses Venomous Slash for 90, reducing Mega Gardevoir 190 to 100. Poison is reapplied and its turn-boundary 10 leaves Mega Gardevoir at 90 HP. The damaged first Crobat remains on the Bench at 60 with no Energy, and Haunter remains 80 with one Darkness. Score stays 2-2.

References: `native/t0246.00.jpg`, `native/t0251.00.jpg`, `native/t0254.00.jpg` through `native/t0258.00.jpg`, `native/t0260.00.jpg`, `native/t0261.00.jpg`, `native/t0263.00.jpg`, `native/t0265.00.jpg`, overview frame 90. The retreat payment and fresh Crobat attachment must not be combined into an extra Energy on the first Crobat.

### Turn 15, opponent, about 268.00-285.00

Potion heals Mega Gardevoir 20, from 90 to 110. The opponent retreats Mega Gardevoir into Mimikyu at no Energy cost under Plaza, retaining Mega's five Psychic. The retreat clears Mega Gardevoir's Poison, explicitly confirmed by the source banner. The regular attachment brings Mimikyu from three to four Psychic. Claw Slash deals 70 to the fresh Crobat, taking it from 170 to 100. Bramblin remains 60 with two Psychic; Mega Gardevoir is benched at 110 and no longer poisoned. No point is scored.

References: `native/t0269.00.jpg`, `native/t0270.00.jpg`, `native/t0271.00.jpg`, `native/t0272.00.jpg`, `native/t0276.00.jpg`, `native/t0277.00.jpg`, `native/t0279.00.jpg`, `native/t0285.00.jpg`, `native/t0287.00.jpg`.

### Turn 16, owner, about 285.00-302.00

Mega Gengar ex is drawn and evolves Haunter directly to 210 HP. It inherits Haunter's one Darkness and receives the turn's attachment, reaching two. It stays on the Bench; Labyrinth of Shadows needs four Energy and cannot be used with this visible state. The 100-HP Active Crobat stays Active and uses Venomous Slash on Mimikyu. Disguise does not trigger again after Mimikyu's earlier blocked Grindcore or after its retreats. The attack deals 90 with weakness: Mimikyu 120 to 30, then Poison 10 leaves it at 20. Both sides remain at 2 awarded points.

References: `native/t0285.00.jpg`, `native/t0287.00.jpg`, `native/t0290.00.jpg`, `native/t0291.00.jpg`, `native/t0293.00.jpg`, `native/t0296.00.jpg`, `native/t0297.00.jpg`, `native/t0299.00.jpg`, overview frame 101.

### Turn 17, opponent and terminal, about 302.00-326.96

The opponent retreats 20-HP Mimikyu to the Bench for free under Peculiar Plaza and promotes Mega Gardevoir at 110 HP. The source confirms Mimikyu recovers from Poison upon retreat. Psychic Energy movement occurs around the final attack, but a separate regular turn-17 attachment is not established by the inspected evidence. The settled pre-attack board has Mega Gardevoir five, Bramblin two and Mimikyu four; afterward it has six, four and four, a net increase of three consistent with Fantasia Force. No additional ordinary attachment or rules discrepancy is inferred. Mega Gardevoir uses Fantasia Force for 110 on the 100-HP Crobat, which reaches 0 and is discarded. The opponent receives `+2 points!`, crossing the 3-point win threshold from two awarded points to four, and the HUD fills its third circle. The surviving owner Bench is Mega Gengar ex 210 with two Darkness and the first Crobat ex 60 with no Energy. The opponent retains Mega Gardevoir 110, Bramblin 60 and Mimikyu 20. Defeat follows, with the challenge title and final stats visible through the end.

References: `native/t0306.00.jpg`, `native/t0309.00.jpg`, `native/t0311.00.jpg`, `native/t0312.00.jpg`, `native/t0314.00.jpg`, `native/t0315.00.jpg`, `native/t0315.50.jpg`, `native/t0316.00.jpg`, `native/t0316.50.jpg`, `native/t0320.00.jpg`, `native/t0325.00.jpg`, `native/t0326.50.jpg`.

## Reconciled HP, points and Energy

Guzzlord's HP path is 170, 160, 150, 80, healed to 110, 100, then 0 from Fantasia Force. The first Crobat stays 170 until Fantasia Force takes it to 60, then retreats and survives on the Bench. The second Crobat starts 170, takes Claw Slash to 100, then final Fantasia Force to 0. Gastly/Haunter/Mega Gengar take no damage. The opponent's Wynaut is 30 to 0; Meloetta 70 to 0; Mega Gardevoir is 210 to 120 to 110, healed to 200, poison to 190, hit to 100 and poison to 90, Potion to 110, then stays benched/Active at 110. Mimikyu stays 120 after Disguise, later becomes 30 and then 20 after poison, and survives at 20 on the Bench.

| Owner turn | Regular Darkness destination | Settled count after attachment |
|---|---|---|
| 2 | Guzzlord ex | 1 |
| 4 | Guzzlord ex | 2 |
| 6 | Guzzlord ex | 3 |
| 8 | Guzzlord ex | 4 |
| 10 | First Crobat ex | 1 |
| 12 | Haunter | 1 |
| 14 | Second Crobat ex | 1; first Crobat pays away its previous 1 on retreat |
| 16 | Mega Gengar ex | 2, including the inherited Haunter Energy |

Opponent development is Mimikyu 1 on turn 3 and 2 on turn 5; Kirlia 1 on turn 7 and 2 on turn 9; Mega Gardevoir 3 from the regular turn-11 attachment. The first Fantasia Force leaves Mega at 5 and Mimikyu at 3. Diantha on turn 13 removes two from Mega, then the regular attachment reaches 4; the next Fantasia leaves Mega 5 and Bramblin 2. The turn-15 regular attachment reaches Mimikyu 4. Psychic retreats preserve Energy under Plaza. The terminal frames visibly show Mega 6, Bramblin 4 and Mimikyu 4; a separate turn-17 regular attachment is not established. The net increase from the settled pre-attack board is three, consistent with Fantasia Force, and does not establish a rule defect.

The owner receives +1 on turn 8 and +1 on turn 10. The opponent receives +2 on turn 11 and +2 on turn 17. The final results Damage done 440 matches the visible direct attack damage count 30 + 140 + 90 + 90 + 90 = 440, including Meloetta overkill and excluding blocked Grindcore damage and poison ticks. It is not evidence that actual HP removed totals 440.

No Pokémon Tool is visibly played. Peculiar Plaza is the only observed Stadium, with no replacement. Poison is the only observed Special Condition, always from Crobat's attacks; it never causes a knockout. No burn, sleep, paralysis or confusion is inflicted in this battle. Team Rocket's Weezing's burn/poison/confusion text is displayed on a draw but its effects never activate.

## Strategic and mechanical observations

These are source-grounded observations with conditional interpretations, not a reconstructed optimal policy or simulator diagnosis.

1. Wynaut's early tax materially delays Guzzlord. The turn-2 and turn-4 pass are consistent with insufficient Energy under Stompy Jammer. On turn 8, Guzzlord has four Energy but the tax still prevents Tyrannical Hole, making the smaller Grindcore the available knockout attack. This is a useful attack-cost interaction to check against an engine, but source agreement alone does not prove engine correctness.
2. Mimikyu's one-time Disguise blocks Grindcore damage while the Energy-discard coin procedure still runs. The observed first flip is tails, so it does not show whether a heads outcome would remove Energy despite Disguise. The later Crobat hit proves the previously used Disguise is not reset by retreat and re-entry into the Active Spot.
3. Peculiar Plaza enables the opponent to cycle Mimikyu, Wynaut and Mega Gardevoir without sacrificing Psychic Energy. Retreat also clears poison. Diantha and Potion buy Mega Gardevoir enough HP to continue this cycle. Healing does not itself clear poison: Mega remains poisoned after Diantha and Potion, then recovers when it retreats.
4. The owner develops a second Crobat and retreats the 60-HP first one on turn 14. This preserves the first copy and supplies a fresh 170-HP attacker, paying one Darkness as required. That defensive exchange buys an additional owner attack before the terminal turn.
5. The consequential turn-16 vulnerability is visible before the loss: Active Crobat has 100 HP, the opponent's benched Mega Gardevoir has 110 HP and enough Psychic to attack, and Plaza makes the opponent's switch free. Hitting Mimikyu leaves it at 20 and poisoned, but the opponent can clear poison by retreating, then take the final knockout. A conditional alternative is to retreat Crobat into the undamaged 210-HP Mega Gengar to absorb one Fantasia Force hit and gain another draw/attachment opportunity. This would cost Crobat its one Darkness and forego its attack, and Mega Gengar at two Energy cannot retaliate that turn. The hidden next draw and later opponent choices are unknown, so this is a survival line to investigate, not a proven winning line.
6. Mega Gengar's late development is incomplete at the end: two attached Darkness versus its four-Energy attack cost. Its Trainer-lock text is not exercised. The unplayed Weezing ex and Lusamine are visible hand constraints, but the footage cannot establish a full-deck consistency verdict. Before the opponent earns points, Lusamine's condition is unmet; after Guzzlord is knocked out, no Ultra Beast remains in play as a target.

## Explicit limits and lead check

The entire available battle and all 17 turns have been visually covered using the overview plus targeted native frames. Full hidden deck lists, all hidden opponent draws, exact cosmetic card numbers, and whether a separate regular turn-17 Energy attachment occurs remain unknown. The last uncertainty does not alter the attack's legality, direct knockout, award or Defeat result. The results panel is completely visible at 326.50 seconds.

Independent lead checks should span setup at 6/17/25 seconds; ordinary development at 42-60 and 72-90; the 113.60-second coin; the 140-146-second Wynaut knockout and no-Energy banner; the 167-200-second two-point exchanges; Diantha at 230.50-242; Rare Candy and paid Crobat retreat at 254-265; and the final 290-326.50-second chain. Check `COVERAGE.md`, `UNCERTAINTIES.json` and `SUMMARY.json` together before acceptance. Independent acceptance, global completion registration and matching-hash archival are complete; storage state is recorded separately in CLOUD_STORAGE.


## Lead completion

Accepted as a completed full-battle review after the source checks documented in `LEAD_ACCEPTANCE.json`. The unchanged original is archived in `Reviewed`; matching before/after SHA-256 is recorded in `MOVE_RECEIPT.20261001_020413000_iOS.MP4.json`. No Ladder Log entry was created.
