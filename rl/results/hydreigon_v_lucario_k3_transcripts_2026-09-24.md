# k3 vs k3: Hydreigon v Lucario, five games Hydreigon lost (2026-09-24)

For Dustin to read. In the Limitless check, the simulator has Hydreigon (Hydreigon / Mega Absol ex) winning **30.2%** of 1,000 k3 vs k3 games against Lucario; real B4a results have it at **54.4%** (149 matches, ±8). Stronger search (k2 → k4, the lead's run) doesn't move it. So the question for these games is: **is the engine getting a card or rule wrong, or is k3 playing one side badly?**

**How the games were picked:** the first five Hydreigon losses by seed number from the table's own games (seeds 72,130,000–72,130,999), not hand-picked. Two have Hydreigon in seat 0, three in seat 1; the engine's coin decides who goes first. Each game was replayed move by move from the recorded game; all five reproduce the table's result exactly (winner, points, turns).

**How to read it:**
- Both real hands are shown at the start of every turn. k3 only sees its own hand plus public information; the hands are shown so you can judge its choices.
- "Draws X" is the card drawn at the start of the turn.
- "[forced]" means that was the only legal move, played automatically.
- "What changed" lists HP, status, knockout and point changes from the moves just above it. If the step included the end of the turn, end-of-turn effects are included (for example, Deceptive Needle's 10 damage).
- Board: Active first, then Bench; energy in brackets; tools after "+".

**Decklists** (the Sept 8 study lists, the ones in the table):
- *Hydreigon (Darkness):* 2 Deino, 2 Hydreigon, 1 Bombirdier, 1 Mega Absol ex, 2 Professor's Research, 2 Copycat, 1 Cyrus, 1 Sabrina, 2 Poké Ball, 2 Rare Candy, 2 Lucky Ice Pop, 2 Deceptive Needle.
- *Lucario (Fighting):* 2 Riolu, 2 Mega Lucario ex, 1 Lucario, 1 Bonsly, 1 Hitmonlee, 2 Professor's Research, 2 Copycat, 1 Korrina, 1 Pokémon Center Lady, 1 Cyrus, 2 Poké Ball, 1 Field Blower, 1 X Speed, 1 Protective Poncho, 1 Arena of Antiquity.

**Card text as the engine has it** (from the engine's own card data, for the cards that appear in these games; compare against the real cards if something looks off):

- **Bombirdier** (B3 115), stage 0, 70 HP, weak Lightning, retreat 1. Ability *Villainous Delivery*: As long as this Pokémon is on your Bench, your Active [D] Pokémon's Retreat Cost is 1 less. Attack *Dark Cutter* [D] 30.
- **Bonsly** (B3 078), stage 0, 30 HP, weak -, retreat 0. Attack *Teary Attack* [free] 10: During your opponent's next turn, attacks used by the Defending Pokémon do -30 damage.
- **Deino** (B1 155), stage 0, 60 HP, weak Grass, retreat 1. Attack *Headbutt* [D] 20.
- **Hitmonlee** (A1 154), stage 0, 80 HP, weak Psychic, retreat 1. Attack *Stretch Kick* [F] 0: This attack does 30 damage to 1 of your opponent's Benched Pokémon.
- **Hydreigon** (B1 157), stage 2 from Zweilous, 150 HP, weak Grass, retreat 2. Ability *Roar in Unison*: Once during your turn, you may take 2 [D] Energy from your Energy Zone and attach it to this Pokémon. If you do, do 30 damage to this Pokémon. Attack *Hyper Ray* [DDD] 130: Discard all Energy from this Pokémon.
- **Lucario** (A2 092), stage 1 from Riolu, 100 HP, weak Psychic, retreat 2. Ability *Fighting Coach*: Attacks used by your [F] Pokémon do +20 damage to your opponent's Active Pokémon. Attack *Submarine Blow* [FF] 40.
- **Mega Absol ex** (B1 151), stage 0, 170 HP, weak Grass, retreat 1. Attack *Darkness Claw* [DD] 80: Your opponent reveals their hand. Choose a Supporter card you find there and discard it.
- **Mega Lucario ex** (B3 081), stage 1 from Riolu, 190 HP, weak Psychic, retreat 1. Attack *Fighting Pulse* [FF] 90: If this Pokémon has at least 1 extra [F] Energy attached, this attack does 50 more damage.
- **Riolu** (B3 079), stage 0, 60 HP, weak Psychic, retreat 1. Attack *Fighting Fist* [F] 10: If your opponent's Active Pokémon is a Pokémon ex, this attack does 30 more damage.
- **Arena of Antiquity** (B3 154), Stadium: Attacks used by each [F] Pokémon in play (both yours and your opponent's) do +20 damage to the opponent's Active Pokémon ex.
- **Copycat** (B1 225), Supporter: Shuffle your hand into your deck. Draw a card for each card in your opponent's hand.
- **Cyrus** (A2 150), Supporter: Switch in 1 of your opponent's Benched Pokémon that has damage on it to the Active Spot.
- **Deceptive Needle** (B4 148), Tool: At the end of your turn, if the [D] Pokémon this card is attached to is in the Active Spot, do 10 damage to your opponent's Active Pokémon.
- **Field Blower** (B3 147), Item: Discard a Pokémon Tool card from a Pokémon (yours or your opponent's), or discard a Stadium card in play.
- **Korrina** (B3 149), Supporter: During this turn, attacks used by your [F] Pokémon do +30 damage to your opponent's Active Pokémon ex.
- **Lucky Ice Pop** (B2 145), Item: Heal 20 damage from your Active Pokémon. If you healed any damage in this way, flip a coin. If heads, put this Lucky Ice Pop into your hand instead of the discard pile.
- **Poké Ball** (P-A 005), Item: Put a random Basic Pokémon from your deck into your hand.
- **Pokémon Center Lady** (A2b 070), Supporter: Heal 30 damage from 1 of your Pokémon, and it recovers from all Special Conditions.
- **Professor's Research** (P-A 007), Supporter: Draw 2 cards.
- **Protective Poncho** (B2 147), Tool: As long as the Pokémon this card is attached to is on your Bench, prevent all damage done to that Pokémon by your opponent's attacks and Abilities.
- **Rare Candy** (A3 144), Item: Choose 1 of your Basic Pokémon in play. If you have a Stage 2 card in your hand that evolves from that Pokémon, put that card onto the Basic Pokémon to evolve it, skipping the Stage 1. You can't use this card during your first turn or on a Basic Pokémon that was put into play this turn.
- **Sabrina** (A1 225), Supporter: Switch out your opponent's Active Pokémon to the Bench. (Your opponent chooses the new Active Pokémon.)

---

## Game 1: seed 72130002. Lucario goes first. Lucario wins 5–0 on turn 13.

**Setup** (points: Hydreigon 0, Lucario 0)
- Hydreigon hand: Sabrina, Poké Ball, Cyrus, Mega Absol ex, Hydreigon
- Lucario hand: Professor's Research, Mega Lucario ex, Protective Poncho, Riolu, Hitmonlee
- Moves:
  - Lucario puts Hitmonlee into play (Active)
  - Lucario puts Riolu into play (Bench)
  - Lucario ends the turn [forced]
  - Hydreigon puts Mega Absol ex into play (Active) [forced]
  - Hydreigon ends the turn [forced]

**Turn 1 — Lucario** (points: Hydreigon 0, Lucario 0)
- Hydreigon hand: Sabrina, Poké Ball, Cyrus, Hydreigon
- Lucario hand: Professor's Research, Mega Lucario ex, Protective Poncho, Poké Ball
- Hydreigon board: Active Mega Absol ex 170/170 HP; Bench: empty
- Lucario board: Active Hitmonlee 80/80 HP; Bench: Riolu 60/60 HP
- Lucario's Energy this turn: none (next: Fighting)
- Moves:
  - Lucario draws Poké Ball
  - Lucario plays Poké Ball
  - Lucario plays Professor's Research
  - Lucario plays Poké Ball
  - Lucario plays Protective Poncho
  - Lucario attaches Protective Poncho to Hitmonlee (Active)
  - Lucario puts Riolu into play (Bench)
  - Lucario ends the turn

**Turn 2 — Hydreigon** (points: Hydreigon 0, Lucario 0)
- Hydreigon hand: Sabrina, Poké Ball, Cyrus, Hydreigon, Deino
- Lucario hand: Bonsly, Mega Lucario ex, Mega Lucario ex
- Hydreigon board: Active Mega Absol ex 170/170 HP; Bench: empty
- Lucario board: Active Hitmonlee 80/80 HP +Protective Poncho; Bench: Riolu 60/60 HP; Riolu 60/60 HP
- Hydreigon's Energy this turn: Darkness (next: Darkness)
- Moves:
  - Hydreigon draws Deino
  - Hydreigon plays Poké Ball
  - Hydreigon puts Deino into play (Bench)
  - Hydreigon puts Deino into play (Bench)
  - Hydreigon plays Sabrina
  - Lucario chooses Riolu (Bench) to become Active
  - Hydreigon attaches 1 Darkness Energy to Mega Absol ex (Active) (turn's Energy)
  - Hydreigon ends the turn

**Turn 3 — Lucario** (points: Hydreigon 0, Lucario 0)
- Hydreigon hand: Cyrus, Hydreigon
- Lucario hand: Bonsly, Mega Lucario ex, Mega Lucario ex, Lucario
- Hydreigon board: Active Mega Absol ex 170/170 HP [Darkness]; Bench: Deino 60/60 HP; Deino 60/60 HP
- Lucario board: Active Riolu 60/60 HP; Bench: Riolu 60/60 HP; Hitmonlee 80/80 HP +Protective Poncho
- Lucario's Energy this turn: Fighting (next: Fighting)
- Moves:
  - Lucario draws Lucario
  - Lucario evolves Riolu (Bench) into Mega Lucario ex
  - Lucario evolves Riolu (Active) into Mega Lucario ex
  - Lucario attaches 1 Fighting Energy to Mega Lucario ex (Active) (turn's Energy)
  - Lucario ends the turn

**Turn 4 — Hydreigon** (points: Hydreigon 0, Lucario 0)
- Hydreigon hand: Cyrus, Hydreigon, Rare Candy
- Lucario hand: Bonsly, Lucario
- Hydreigon board: Active Mega Absol ex 170/170 HP [Darkness]; Bench: Deino 60/60 HP; Deino 60/60 HP
- Lucario board: Active Mega Lucario ex 190/190 HP [Fighting]; Bench: Mega Lucario ex 190/190 HP; Hitmonlee 80/80 HP +Protective Poncho
- Hydreigon's Energy this turn: Darkness (next: Darkness)
- Moves:
  - Hydreigon draws Rare Candy
  - Hydreigon plays Rare Candy
  - Hydreigon evolves Deino (Bench) into Hydreigon
  - Hydreigon uses the Ability of Hydreigon (Bench)
    - what changed: Hydreigon's Hydreigon 150 → 120 HP
  - Hydreigon retreats Active, bringing up Hydreigon (Bench)
  - Hydreigon attaches 1 Darkness Energy to Hydreigon (Active) (turn's Energy)
  - Hydreigon ends the turn

**Turn 5 — Lucario** (points: Hydreigon 0, Lucario 0)
- Hydreigon hand: Cyrus
- Lucario hand: Bonsly, Lucario, X Speed
- Hydreigon board: Active Hydreigon 120/150 HP [Darkness, Darkness, Darkness]; Bench: Deino 60/60 HP; Mega Absol ex 170/170 HP
- Lucario board: Active Mega Lucario ex 190/190 HP [Fighting]; Bench: Mega Lucario ex 190/190 HP; Hitmonlee 80/80 HP +Protective Poncho
- Lucario's Energy this turn: Fighting (next: Fighting)
- Moves:
  - Lucario draws X Speed
  - Lucario puts Bonsly into play (Bench)
  - Lucario attaches 1 Fighting Energy to Mega Lucario ex (Active) (turn's Energy)
  - Lucario attacks with Fighting Pulse (90 base; If this Pokémon has at least 1 extra [F] Energy attached, this attack does 50 more damage.)
  - Lucario ends the turn [forced]
    - what changed: Hydreigon's Hydreigon 120 → 30 HP

**Turn 6 — Hydreigon** (points: Hydreigon 0, Lucario 0)
- Hydreigon hand: Cyrus, Hydreigon
- Lucario hand: X Speed, Lucario
- Hydreigon board: Active Hydreigon 30/150 HP [Darkness, Darkness, Darkness]; Bench: Deino 60/60 HP; Mega Absol ex 170/170 HP
- Lucario board: Active Mega Lucario ex 190/190 HP [Fighting, Fighting]; Bench: Bonsly 30/30 HP; Mega Lucario ex 190/190 HP; Hitmonlee 80/80 HP +Protective Poncho
- Hydreigon's Energy this turn: Darkness (next: Darkness)
- Moves:
  - Hydreigon draws Hydreigon
  - Hydreigon attaches 1 Darkness Energy to Mega Absol ex (Bench) (turn's Energy)
  - Hydreigon ends the turn

**Turn 7 — Lucario** (points: Hydreigon 0, Lucario 0)
- Hydreigon hand: Cyrus, Hydreigon
- Lucario hand: X Speed, Lucario, Copycat
- Hydreigon board: Active Hydreigon 30/150 HP [Darkness, Darkness, Darkness]; Bench: Deino 60/60 HP; Mega Absol ex 170/170 HP [Darkness]
- Lucario board: Active Mega Lucario ex 190/190 HP [Fighting, Fighting]; Bench: Bonsly 30/30 HP; Mega Lucario ex 190/190 HP; Hitmonlee 80/80 HP +Protective Poncho
- Lucario's Energy this turn: Fighting (next: Fighting)
- Moves:
  - Lucario draws Copycat
  - Lucario attaches 1 Fighting Energy to Mega Lucario ex (Bench) (turn's Energy)
  - Lucario attacks with Fighting Pulse (90 base; If this Pokémon has at least 1 extra [F] Energy attached, this attack does 50 more damage.)
    - what changed: Hydreigon's Hydreigon knocked out; Lucario points 0 → 1
  - Hydreigon promotes Mega Absol ex (Bench) to Active
  - Lucario ends the turn [forced]

**Turn 8 — Hydreigon** (points: Hydreigon 0, Lucario 1)
- Hydreigon hand: Cyrus, Hydreigon, Professor's Research
- Lucario hand: X Speed, Lucario, Copycat
- Hydreigon board: Active Mega Absol ex 170/170 HP [Darkness]; Bench: Deino 60/60 HP
- Lucario board: Active Mega Lucario ex 190/190 HP [Fighting, Fighting]; Bench: Bonsly 30/30 HP; Mega Lucario ex 190/190 HP [Fighting]; Hitmonlee 80/80 HP +Protective Poncho
- Hydreigon's Energy this turn: Darkness (next: Darkness)
- Moves:
  - Hydreigon draws Professor's Research
  - Hydreigon plays Professor's Research
  - Hydreigon plays Rare Candy
  - Hydreigon evolves Deino (Bench) into Hydreigon [forced]
  - Hydreigon uses the Ability of Hydreigon (Bench)
    - what changed: Hydreigon's Hydreigon 150 → 120 HP
  - Hydreigon retreats Active, bringing up Hydreigon (Bench)
  - Hydreigon plays Deceptive Needle
  - Hydreigon attaches Deceptive Needle to Hydreigon (Active)
  - Hydreigon attaches 1 Darkness Energy to Hydreigon (Active) (turn's Energy)
  - Hydreigon ends the turn
    - what changed: Lucario's Mega Lucario ex 190 → 180 HP

**Turn 9 — Lucario** (points: Hydreigon 0, Lucario 1)
- Hydreigon hand: Cyrus
- Lucario hand: X Speed, Lucario, Copycat, Pokémon Center Lady
- Hydreigon board: Active Hydreigon 120/150 HP [Darkness, Darkness, Darkness] +Deceptive Needle; Bench: Mega Absol ex 170/170 HP
- Lucario board: Active Mega Lucario ex 180/190 HP [Fighting, Fighting]; Bench: Bonsly 30/30 HP; Mega Lucario ex 190/190 HP [Fighting]; Hitmonlee 80/80 HP +Protective Poncho
- Lucario's Energy this turn: Fighting (next: Fighting)
- Moves:
  - Lucario draws Pokémon Center Lady
  - Lucario attaches 1 Fighting Energy to Mega Lucario ex (Active) (turn's Energy)
  - Lucario plays Pokémon Center Lady
  - Lucario heals 30 from Mega Lucario ex (Active) and cures status [forced]
    - what changed: Lucario's Mega Lucario ex 180 → 190 HP
  - Lucario attacks with Fighting Pulse (90 base; If this Pokémon has at least 1 extra [F] Energy attached, this attack does 50 more damage.)
  - Hydreigon promotes Mega Absol ex (Bench) to Active [forced]
  - Lucario ends the turn [forced]
    - what changed: Hydreigon's Hydreigon knocked out; Lucario points 1 → 2

**Turn 10 — Hydreigon** (points: Hydreigon 0, Lucario 2)
- Hydreigon hand: Cyrus, Professor's Research
- Lucario hand: X Speed, Lucario, Copycat
- Hydreigon board: Active Mega Absol ex 170/170 HP; Bench: empty
- Lucario board: Active Mega Lucario ex 190/190 HP [Fighting, Fighting, Fighting]; Bench: Bonsly 30/30 HP; Mega Lucario ex 190/190 HP [Fighting]; Hitmonlee 80/80 HP +Protective Poncho
- Hydreigon's Energy this turn: Darkness (next: Darkness)
- Moves:
  - Hydreigon draws Professor's Research
  - Hydreigon plays Professor's Research
  - Hydreigon plays Deceptive Needle
  - Hydreigon attaches Deceptive Needle to Mega Absol ex (Active) [forced]
  - Hydreigon attaches 1 Darkness Energy to Mega Absol ex (Active) (turn's Energy)
  - Hydreigon ends the turn [forced]
    - what changed: Lucario's Mega Lucario ex 190 → 180 HP

**Turn 11 — Lucario** (points: Hydreigon 0, Lucario 2)
- Hydreigon hand: Cyrus, Copycat
- Lucario hand: X Speed, Lucario, Copycat, Field Blower
- Hydreigon board: Active Mega Absol ex 170/170 HP [Darkness] +Deceptive Needle; Bench: empty
- Lucario board: Active Mega Lucario ex 180/190 HP [Fighting, Fighting, Fighting]; Bench: Bonsly 30/30 HP; Mega Lucario ex 190/190 HP [Fighting]; Hitmonlee 80/80 HP +Protective Poncho
- Lucario's Energy this turn: Fighting (next: Fighting)
- Moves:
  - Lucario draws Field Blower
  - Lucario attaches 1 Fighting Energy to Mega Lucario ex (Bench) (turn's Energy)
  - Lucario plays Field Blower
  - Lucario discards a Tool from Mega Absol ex (Active)
  - Lucario attacks with Fighting Pulse (90 base; If this Pokémon has at least 1 extra [F] Energy attached, this attack does 50 more damage.)
  - Lucario ends the turn [forced]
    - what changed: Hydreigon's Mega Absol ex 170 → 30 HP

**Turn 12 — Hydreigon** (points: Hydreigon 0, Lucario 2)
- Hydreigon hand: Cyrus, Copycat, Lucky Ice Pop
- Lucario hand: X Speed, Lucario, Copycat
- Hydreigon board: Active Mega Absol ex 30/170 HP [Darkness]; Bench: empty
- Lucario board: Active Mega Lucario ex 180/190 HP [Fighting, Fighting, Fighting]; Bench: Bonsly 30/30 HP; Mega Lucario ex 190/190 HP [Fighting, Fighting]; Hitmonlee 80/80 HP +Protective Poncho
- Hydreigon's Energy this turn: Darkness (next: Darkness)
- Moves:
  - Hydreigon draws Lucky Ice Pop
  - Hydreigon plays Lucky Ice Pop
    - what changed: Hydreigon's Mega Absol ex 30 → 50 HP
  - Hydreigon attaches 1 Darkness Energy to Mega Absol ex (Active) (turn's Energy)
  - Hydreigon plays Copycat
  - Hydreigon plays Lucky Ice Pop
    - what changed: Hydreigon's Mega Absol ex 50 → 70 HP
  - Hydreigon puts Bombirdier into play (Bench)
  - Hydreigon attacks with Darkness Claw (80 base; Your opponent reveals their hand. Choose a Supporter card you find there and discard it.)
  - Hydreigon discards opponent's Copycat from their hand [forced]
  - Hydreigon ends the turn [forced]
    - what changed: Lucario's Mega Lucario ex 180 → 100 HP

**Turn 13 — Lucario** (points: Hydreigon 0, Lucario 2)
- Hydreigon hand: Cyrus
- Lucario hand: X Speed, Lucario, Cyrus
- Hydreigon board: Active Mega Absol ex 70/170 HP [Darkness, Darkness]; Bench: Bombirdier 70/70 HP
- Lucario board: Active Mega Lucario ex 100/190 HP [Fighting, Fighting, Fighting]; Bench: Bonsly 30/30 HP; Mega Lucario ex 190/190 HP [Fighting, Fighting]; Hitmonlee 80/80 HP +Protective Poncho
- Lucario's Energy this turn: Fighting (next: Fighting)
- Moves:
  - Lucario draws Cyrus
  - Lucario attacks with Fighting Pulse (90 base; If this Pokémon has at least 1 extra [F] Energy attached, this attack does 50 more damage.)
    - what changed: Hydreigon's Mega Absol ex knocked out; Lucario points 2 → 5

**Game over:** Lucario 5, Hydreigon 0, after turn 13.

---

## Game 2: seed 72130003. Lucario goes first. Lucario wins 4–2 on turn 9.

**Setup** (points: Lucario 0, Hydreigon 0)
- Lucario hand: Professor's Research, Riolu, Poké Ball, Bonsly, Field Blower
- Hydreigon hand: Lucky Ice Pop, Deino, Professor's Research, Rare Candy, Copycat
- Moves:
  - Lucario puts Bonsly into play (Active)
  - Lucario puts Riolu into play (Bench)
  - Lucario ends the turn [forced]
  - Hydreigon puts Deino into play (Active) [forced]
  - Hydreigon ends the turn [forced]

**Turn 1 — Lucario** (points: Lucario 0, Hydreigon 0)
- Lucario hand: Professor's Research, Field Blower, Poké Ball, Copycat
- Hydreigon hand: Lucky Ice Pop, Copycat, Professor's Research, Rare Candy
- Lucario board: Active Bonsly 30/30 HP; Bench: Riolu 60/60 HP
- Hydreigon board: Active Deino 60/60 HP; Bench: empty
- Lucario's Energy this turn: none (next: Fighting)
- Moves:
  - Lucario draws Copycat
  - Lucario plays Poké Ball
  - Lucario plays Professor's Research
  - Lucario plays Poké Ball
  - Lucario puts Riolu into play (Bench)
  - Lucario puts Hitmonlee into play (Bench)
  - Lucario attacks with Teary Attack (10 base; During your opponent's next turn, attacks used by the Defending Pokémon do -30 damage.)
  - Lucario ends the turn [forced]
    - what changed: Hydreigon's Deino 60 → 50 HP

**Turn 2 — Hydreigon** (points: Lucario 0, Hydreigon 0)
- Lucario hand: Mega Lucario ex, Field Blower, Copycat
- Hydreigon hand: Lucky Ice Pop, Copycat, Professor's Research, Rare Candy, Copycat
- Lucario board: Active Bonsly 30/30 HP; Bench: Hitmonlee 80/80 HP; Riolu 60/60 HP; Riolu 60/60 HP
- Hydreigon board: Active Deino 50/60 HP; Bench: empty
- Hydreigon's Energy this turn: Darkness (next: Darkness)
- Moves:
  - Hydreigon draws Copycat
  - Hydreigon plays Professor's Research
  - Hydreigon plays Lucky Ice Pop
    - what changed: Hydreigon's Deino 50 → 60 HP
  - Hydreigon puts Mega Absol ex into play (Bench)
  - Hydreigon plays Deceptive Needle
  - Hydreigon attaches Deceptive Needle to Deino (Active)
  - Hydreigon attaches 1 Darkness Energy to Mega Absol ex (Bench) (turn's Energy)
  - Hydreigon ends the turn [forced]
    - what changed: Lucario's Bonsly 30 → 20 HP

**Turn 3 — Lucario** (points: Lucario 0, Hydreigon 0)
- Lucario hand: Mega Lucario ex, Field Blower, Copycat, Lucario
- Hydreigon hand: Rare Candy, Copycat, Copycat
- Lucario board: Active Bonsly 20/30 HP; Bench: Hitmonlee 80/80 HP; Riolu 60/60 HP; Riolu 60/60 HP
- Hydreigon board: Active Deino 60/60 HP +Deceptive Needle; Bench: Mega Absol ex 170/170 HP [Darkness]
- Lucario's Energy this turn: Fighting (next: Fighting)
- Moves:
  - Lucario draws Lucario
  - Lucario evolves Riolu (Bench) into Mega Lucario ex
  - Lucario evolves Riolu (Bench) into Lucario
  - Lucario attaches 1 Fighting Energy to Hitmonlee (Bench) (turn's Energy)
  - Lucario retreats Active, bringing up Hitmonlee (Bench)
  - Lucario attacks with Stretch Kick (0 base; This attack does 30 damage to 1 of your opponent's Benched Pokémon.)
  - Lucario puts damage: 30 to Mega Absol ex (Bench) [forced]
  - Lucario ends the turn [forced]
    - what changed: Hydreigon's Mega Absol ex 170 → 140 HP

**Turn 4 — Hydreigon** (points: Lucario 0, Hydreigon 0)
- Lucario hand: Copycat, Field Blower
- Hydreigon hand: Rare Candy, Copycat, Copycat, Hydreigon
- Lucario board: Active Hitmonlee 80/80 HP [Fighting]; Bench: Bonsly 20/30 HP; Lucario 100/100 HP; Mega Lucario ex 190/190 HP
- Hydreigon board: Active Deino 60/60 HP +Deceptive Needle; Bench: Mega Absol ex 140/170 HP [Darkness]
- Hydreigon's Energy this turn: Darkness (next: Darkness)
- Moves:
  - Hydreigon draws Hydreigon
  - Hydreigon plays Rare Candy
  - Hydreigon evolves Deino (Active) into Hydreigon [forced]
  - Hydreigon uses the Ability of Hydreigon (Active)
    - what changed: Hydreigon's Hydreigon 150 → 120 HP
  - Hydreigon attaches 1 Darkness Energy to Hydreigon (Active) (turn's Energy)
  - Hydreigon attacks with Hyper Ray (130 base; Discard all Energy from this Pokémon.)
    - what changed: Lucario's Hitmonlee knocked out; Hydreigon points 0 → 1
  - Lucario promotes Bonsly (Bench) to Active
  - Hydreigon ends the turn [forced]

**Turn 5 — Lucario** (points: Lucario 0, Hydreigon 1)
- Lucario hand: Copycat, Field Blower, X Speed
- Hydreigon hand: Copycat, Copycat
- Lucario board: Active Bonsly 10/30 HP; Bench: Lucario 100/100 HP; Mega Lucario ex 190/190 HP
- Hydreigon board: Active Hydreigon 120/150 HP +Deceptive Needle; Bench: Mega Absol ex 140/170 HP [Darkness]
- Lucario's Energy this turn: Fighting (next: Fighting)
- Moves:
  - Lucario draws X Speed
  - Lucario attaches 1 Fighting Energy to Mega Lucario ex (Bench) (turn's Energy)
  - Lucario plays Field Blower
  - Lucario discards a Tool from Hydreigon (Active) [forced]
  - Lucario attacks with Teary Attack (10 base; During your opponent's next turn, attacks used by the Defending Pokémon do -30 damage.)
  - Lucario ends the turn [forced]
    - what changed: Hydreigon's Hydreigon 120 → 90 HP

**Turn 6 — Hydreigon** (points: Lucario 0, Hydreigon 1)
- Lucario hand: Copycat, X Speed
- Hydreigon hand: Copycat, Copycat, Hydreigon
- Lucario board: Active Bonsly 10/30 HP; Bench: Lucario 100/100 HP; Mega Lucario ex 190/190 HP [Fighting]
- Hydreigon board: Active Hydreigon 90/150 HP; Bench: Mega Absol ex 140/170 HP [Darkness]
- Hydreigon's Energy this turn: Darkness (next: Darkness)
- Moves:
  - Hydreigon draws Hydreigon
  - Hydreigon uses the Ability of Hydreigon (Active)
    - what changed: Hydreigon's Hydreigon 90 → 60 HP
  - Hydreigon attaches 1 Darkness Energy to Hydreigon (Active) (turn's Energy)
  - Hydreigon attacks with Hyper Ray (130 base; Discard all Energy from this Pokémon.)
    - what changed: Lucario's Bonsly knocked out; Hydreigon points 1 → 2
  - Lucario promotes Mega Lucario ex (Bench) to Active
  - Hydreigon ends the turn [forced]

**Turn 7 — Lucario** (points: Lucario 0, Hydreigon 2)
- Lucario hand: Copycat, X Speed, Mega Lucario ex
- Hydreigon hand: Copycat, Copycat, Hydreigon
- Lucario board: Active Mega Lucario ex 190/190 HP [Fighting]; Bench: Lucario 100/100 HP
- Hydreigon board: Active Hydreigon 60/150 HP; Bench: Mega Absol ex 140/170 HP [Darkness]
- Lucario's Energy this turn: Fighting (next: Fighting)
- Moves:
  - Lucario draws Mega Lucario ex
  - Lucario attaches 1 Fighting Energy to Mega Lucario ex (Active) (turn's Energy)
  - Lucario attacks with Fighting Pulse (90 base; If this Pokémon has at least 1 extra [F] Energy attached, this attack does 50 more damage.)
  - Hydreigon promotes Mega Absol ex (Bench) to Active [forced]
  - Lucario ends the turn [forced]
    - what changed: Lucario points 0 → 1; Hydreigon's Hydreigon knocked out

**Turn 8 — Hydreigon** (points: Lucario 1, Hydreigon 2)
- Lucario hand: Copycat, X Speed, Mega Lucario ex
- Hydreigon hand: Copycat, Copycat, Hydreigon, Poké Ball
- Lucario board: Active Mega Lucario ex 190/190 HP [Fighting, Fighting]; Bench: Lucario 100/100 HP
- Hydreigon board: Active Mega Absol ex 140/170 HP [Darkness]; Bench: empty
- Hydreigon's Energy this turn: Darkness (next: Darkness)
- Moves:
  - Hydreigon draws Poké Ball
  - Hydreigon plays Poké Ball
  - Hydreigon puts Bombirdier into play (Bench)
  - Hydreigon attaches 1 Darkness Energy to Mega Absol ex (Active) (turn's Energy)
  - Hydreigon plays Copycat
  - Hydreigon plays Lucky Ice Pop
    - what changed: Hydreigon's Mega Absol ex 140 → 160 HP
  - Hydreigon attacks with Darkness Claw (80 base; Your opponent reveals their hand. Choose a Supporter card you find there and discard it.)
  - Hydreigon discards opponent's Copycat from their hand [forced]
  - Hydreigon ends the turn [forced]
    - what changed: Lucario's Mega Lucario ex 190 → 110 HP

**Turn 9 — Lucario** (points: Lucario 1, Hydreigon 2)
- Lucario hand: Mega Lucario ex, X Speed, Pokémon Center Lady
- Hydreigon hand: Hydreigon, Professor's Research
- Lucario board: Active Mega Lucario ex 110/190 HP [Fighting, Fighting]; Bench: Lucario 100/100 HP
- Hydreigon board: Active Mega Absol ex 160/170 HP [Darkness, Darkness]; Bench: Bombirdier 70/70 HP
- Lucario's Energy this turn: Fighting (next: Fighting)
- Moves:
  - Lucario draws Pokémon Center Lady
  - Lucario attaches 1 Fighting Energy to Mega Lucario ex (Active) (turn's Energy)
  - Lucario attacks with Fighting Pulse (90 base; If this Pokémon has at least 1 extra [F] Energy attached, this attack does 50 more damage.)
    - what changed: Lucario points 1 → 4; Hydreigon's Mega Absol ex knocked out

**Game over:** Lucario 4, Hydreigon 2, after turn 9.

---

## Game 3: seed 72130005. Hydreigon goes first. Lucario wins 5–0 on turn 8.

**Turn 1 — Hydreigon** (points: Lucario 0, Hydreigon 0)
- Lucario hand: Arena of Antiquity, Copycat, Mega Lucario ex, Professor's Research
- Hydreigon hand: Professor's Research, Poké Ball, Lucky Ice Pop, Professor's Research, Poké Ball
- Lucario board: Active Riolu 60/60 HP; Bench: empty
- Hydreigon board: Active Mega Absol ex 170/170 HP; Bench: empty
- Hydreigon's Energy this turn: none (next: Darkness)
- Moves:
  - Hydreigon plays Poké Ball
  - Hydreigon plays Poké Ball
  - Hydreigon puts Bombirdier into play (Bench)
  - Hydreigon retreats Active, bringing up Bombirdier (Bench)
  - Hydreigon plays Professor's Research
  - Hydreigon puts Deino into play (Bench)
  - Hydreigon ends the turn [forced]

**Turn 2 — Lucario** (points: Lucario 0, Hydreigon 0)
- Lucario hand: Arena of Antiquity, Copycat, Mega Lucario ex, Professor's Research, Cyrus
- Hydreigon hand: Professor's Research, Hydreigon, Lucky Ice Pop, Cyrus
- Lucario board: Active Riolu 60/60 HP; Bench: empty
- Hydreigon board: Active Bombirdier 70/70 HP; Bench: Deino 60/60 HP; Mega Absol ex 170/170 HP
- Lucario's Energy this turn: Fighting (next: Fighting)
- Moves:
  - Lucario draws Cyrus
  - Lucario plays Professor's Research
  - Lucario attaches 1 Fighting Energy to Riolu (Active) (turn's Energy)
  - Lucario attacks with Fighting Fist (10 base; If your opponent's Active Pokémon is a Pokémon ex, this attack does 30 more damage.)
  - Lucario ends the turn [forced]
    - what changed: Hydreigon's Bombirdier 70 → 60 HP

**Turn 3 — Hydreigon** (points: Lucario 0, Hydreigon 0)
- Lucario hand: Arena of Antiquity, Copycat, Mega Lucario ex, Cyrus, Professor's Research, Field Blower
- Hydreigon hand: Professor's Research, Hydreigon, Lucky Ice Pop, Cyrus, Copycat
- Lucario board: Active Riolu 60/60 HP [Fighting]; Bench: empty
- Hydreigon board: Active Bombirdier 60/70 HP; Bench: Deino 60/60 HP; Mega Absol ex 170/170 HP
- Hydreigon's Energy this turn: Darkness (next: Darkness)
- Moves:
  - Hydreigon draws Copycat
  - Hydreigon plays Lucky Ice Pop
    - what changed: Hydreigon's Bombirdier 60 → 70 HP
  - Hydreigon plays Professor's Research
  - Hydreigon plays Rare Candy
  - Hydreigon evolves Deino (Bench) into Hydreigon
  - Hydreigon attaches 1 Darkness Energy to Bombirdier (Active) (turn's Energy)
  - Hydreigon attacks with Dark Cutter (30 base; no text)
  - Hydreigon ends the turn [forced]
    - what changed: Lucario's Riolu 60 → 30 HP

**Turn 4 — Lucario** (points: Lucario 0, Hydreigon 0)
- Lucario hand: Arena of Antiquity, Copycat, Mega Lucario ex, Cyrus, Professor's Research, Field Blower, Lucario
- Hydreigon hand: Lucky Ice Pop, Hydreigon, Copycat, Cyrus
- Lucario board: Active Riolu 30/60 HP [Fighting]; Bench: empty
- Hydreigon board: Active Bombirdier 70/70 HP [Darkness]; Bench: Hydreigon 150/150 HP; Mega Absol ex 170/170 HP
- Lucario's Energy this turn: Fighting (next: Fighting)
- Moves:
  - Lucario draws Lucario
  - Lucario evolves Riolu (Active) into Mega Lucario ex
  - Lucario plays Professor's Research
  - Lucario plays Poké Ball
  - Lucario puts Riolu into play (Bench)
  - Lucario attaches 1 Fighting Energy to Mega Lucario ex (Active) (turn's Energy)
  - Lucario attacks with Fighting Pulse (90 base; If this Pokémon has at least 1 extra [F] Energy attached, this attack does 50 more damage.)
    - what changed: Lucario points 0 → 1; Hydreigon's Bombirdier knocked out
  - Hydreigon promotes Hydreigon (Bench) to Active
  - Lucario ends the turn [forced]

**Turn 5 — Hydreigon** (points: Lucario 1, Hydreigon 0)
- Lucario hand: Arena of Antiquity, Copycat, Lucario, Cyrus, Field Blower, Copycat
- Hydreigon hand: Lucky Ice Pop, Hydreigon, Copycat, Cyrus, Deceptive Needle
- Lucario board: Active Mega Lucario ex 160/190 HP [Fighting, Fighting]; Bench: Riolu 60/60 HP
- Hydreigon board: Active Hydreigon 150/150 HP; Bench: Mega Absol ex 170/170 HP
- Hydreigon's Energy this turn: Darkness (next: Darkness)
- Moves:
  - Hydreigon draws Deceptive Needle
  - Hydreigon uses the Ability of Hydreigon (Active)
    - what changed: Hydreigon's Hydreigon 150 → 120 HP
  - Hydreigon plays Lucky Ice Pop
    - what changed: Hydreigon's Hydreigon 120 → 140 HP
  - Hydreigon plays Deceptive Needle
  - Hydreigon attaches Deceptive Needle to Hydreigon (Active)
  - Hydreigon attaches 1 Darkness Energy to Hydreigon (Active) (turn's Energy)
  - Hydreigon ends the turn
    - what changed: Lucario's Mega Lucario ex 160 → 150 HP

**Turn 6 — Lucario** (points: Lucario 1, Hydreigon 0)
- Lucario hand: Arena of Antiquity, Copycat, Lucario, Cyrus, Field Blower, Copycat, Pokémon Center Lady
- Hydreigon hand: Cyrus, Hydreigon, Copycat
- Lucario board: Active Mega Lucario ex 150/190 HP [Fighting, Fighting]; Bench: Riolu 60/60 HP
- Hydreigon board: Active Hydreigon 140/150 HP [Darkness, Darkness, Darkness] +Deceptive Needle; Bench: Mega Absol ex 170/170 HP
- Lucario's Energy this turn: Fighting (next: Fighting)
- Moves:
  - Lucario draws Pokémon Center Lady
  - Lucario evolves Riolu (Bench) into Lucario
  - Lucario attaches 1 Fighting Energy to Mega Lucario ex (Active) (turn's Energy)
  - Lucario plays Pokémon Center Lady
  - Lucario heals 30 from Mega Lucario ex (Active) and cures status [forced]
    - what changed: Lucario's Mega Lucario ex 150 → 180 HP
  - Lucario attacks with Fighting Pulse (90 base; If this Pokémon has at least 1 extra [F] Energy attached, this attack does 50 more damage.)
  - Hydreigon promotes Mega Absol ex (Bench) to Active [forced]
  - Lucario ends the turn [forced]
    - what changed: Lucario points 1 → 2; Hydreigon's Hydreigon knocked out

**Turn 7 — Hydreigon** (points: Lucario 2, Hydreigon 0)
- Lucario hand: Arena of Antiquity, Copycat, Copycat, Cyrus, Field Blower
- Hydreigon hand: Cyrus, Hydreigon, Copycat, Rare Candy
- Lucario board: Active Mega Lucario ex 180/190 HP [Fighting, Fighting, Fighting]; Bench: Lucario 100/100 HP
- Hydreigon board: Active Mega Absol ex 170/170 HP; Bench: empty
- Hydreigon's Energy this turn: Darkness (next: Darkness)
- Moves:
  - Hydreigon draws Rare Candy
  - Hydreigon attaches 1 Darkness Energy to Mega Absol ex (Active) (turn's Energy)
  - Hydreigon plays Copycat
  - Hydreigon plays Deceptive Needle
  - Hydreigon attaches Deceptive Needle to Mega Absol ex (Active) [forced]
  - Hydreigon puts Deino into play (Bench)
  - Hydreigon ends the turn
    - what changed: Lucario's Mega Lucario ex 180 → 170 HP

**Turn 8 — Lucario** (points: Lucario 2, Hydreigon 0)
- Lucario hand: Arena of Antiquity, Copycat, Copycat, Cyrus, Field Blower, Poké Ball
- Hydreigon hand: Rare Candy, Cyrus, Lucky Ice Pop
- Lucario board: Active Mega Lucario ex 170/190 HP [Fighting, Fighting, Fighting]; Bench: Lucario 100/100 HP
- Hydreigon board: Active Mega Absol ex 170/170 HP [Darkness] +Deceptive Needle; Bench: Deino 60/60 HP
- Lucario's Energy this turn: Fighting (next: Fighting)
- Moves:
  - Lucario draws Poké Ball
  - Lucario plays Arena of Antiquity
  - Lucario attacks with Fighting Pulse (90 base; If this Pokémon has at least 1 extra [F] Energy attached, this attack does 50 more damage.)
    - what changed: Lucario points 2 → 5; Hydreigon's Mega Absol ex knocked out

**Game over:** Lucario 5, Hydreigon 0, after turn 8.

---

## Game 4: seed 72130007. Hydreigon goes first. Lucario wins 4–0 on turn 6.

**Turn 1 — Hydreigon** (points: Lucario 0, Hydreigon 0)
- Lucario hand: Mega Lucario ex, Field Blower, Arena of Antiquity, Korrina
- Hydreigon hand: Hydreigon, Rare Candy, Deceptive Needle, Poké Ball, Sabrina
- Lucario board: Active Riolu 60/60 HP; Bench: empty
- Hydreigon board: Active Bombirdier 70/70 HP; Bench: empty
- Hydreigon's Energy this turn: none (next: Darkness)
- Moves:
  - Hydreigon plays Poké Ball
  - Hydreigon plays Deceptive Needle
  - Hydreigon attaches Deceptive Needle to Bombirdier (Active) [forced]
  - Hydreigon puts Mega Absol ex into play (Bench)
  - Hydreigon ends the turn [forced]
    - what changed: Lucario's Riolu 60 → 50 HP

**Turn 2 — Lucario** (points: Lucario 0, Hydreigon 0)
- Lucario hand: Mega Lucario ex, Field Blower, Arena of Antiquity, Korrina, Cyrus
- Hydreigon hand: Hydreigon, Rare Candy, Sabrina
- Lucario board: Active Riolu 50/60 HP; Bench: empty
- Hydreigon board: Active Bombirdier 70/70 HP +Deceptive Needle; Bench: Mega Absol ex 170/170 HP
- Lucario's Energy this turn: Fighting (next: Fighting)
- Moves:
  - Lucario draws Cyrus
  - Lucario attaches 1 Fighting Energy to Riolu (Active) (turn's Energy)
  - Lucario plays Field Blower
  - Lucario discards a Tool from Bombirdier (Active) [forced]
  - Lucario attacks with Fighting Fist (10 base; If your opponent's Active Pokémon is a Pokémon ex, this attack does 30 more damage.)
  - Lucario ends the turn [forced]
    - what changed: Hydreigon's Bombirdier 70 → 60 HP

**Turn 3 — Hydreigon** (points: Lucario 0, Hydreigon 0)
- Lucario hand: Mega Lucario ex, Cyrus, Arena of Antiquity, Korrina
- Hydreigon hand: Hydreigon, Rare Candy, Sabrina, Copycat
- Lucario board: Active Riolu 50/60 HP [Fighting]; Bench: empty
- Hydreigon board: Active Bombirdier 60/70 HP; Bench: Mega Absol ex 170/170 HP
- Hydreigon's Energy this turn: Darkness (next: Darkness)
- Moves:
  - Hydreigon draws Copycat
  - Hydreigon attaches 1 Darkness Energy to Bombirdier (Active) (turn's Energy)
  - Hydreigon attacks with Dark Cutter (30 base; no text)
  - Hydreigon ends the turn [forced]
    - what changed: Lucario's Riolu 50 → 20 HP

**Turn 4 — Lucario** (points: Lucario 0, Hydreigon 0)
- Lucario hand: Mega Lucario ex, Cyrus, Arena of Antiquity, Korrina, Lucario
- Hydreigon hand: Hydreigon, Rare Candy, Sabrina, Copycat
- Lucario board: Active Riolu 20/60 HP [Fighting]; Bench: empty
- Hydreigon board: Active Bombirdier 60/70 HP [Darkness]; Bench: Mega Absol ex 170/170 HP
- Lucario's Energy this turn: Fighting (next: Fighting)
- Moves:
  - Lucario draws Lucario
  - Lucario evolves Riolu (Active) into Mega Lucario ex
  - Lucario attaches 1 Fighting Energy to Mega Lucario ex (Active) (turn's Energy)
  - Lucario attacks with Fighting Pulse (90 base; If this Pokémon has at least 1 extra [F] Energy attached, this attack does 50 more damage.)
  - Hydreigon promotes Mega Absol ex (Bench) to Active [forced]
  - Lucario ends the turn [forced]
    - what changed: Lucario points 0 → 1; Hydreigon's Bombirdier knocked out

**Turn 5 — Hydreigon** (points: Lucario 1, Hydreigon 0)
- Lucario hand: Lucario, Cyrus, Arena of Antiquity, Korrina
- Hydreigon hand: Hydreigon, Rare Candy, Sabrina, Copycat, Lucky Ice Pop
- Lucario board: Active Mega Lucario ex 150/190 HP [Fighting, Fighting]; Bench: empty
- Hydreigon board: Active Mega Absol ex 170/170 HP; Bench: empty
- Hydreigon's Energy this turn: Darkness (next: Darkness)
- Moves:
  - Hydreigon draws Lucky Ice Pop
  - Hydreigon attaches 1 Darkness Energy to Mega Absol ex (Active) (turn's Energy)
  - Hydreigon plays Copycat
  - Hydreigon ends the turn [forced]

**Turn 6 — Lucario** (points: Lucario 1, Hydreigon 0)
- Lucario hand: Lucario, Cyrus, Arena of Antiquity, Korrina, Professor's Research
- Hydreigon hand: Rare Candy, Cyrus, Hydreigon, Professor's Research
- Lucario board: Active Mega Lucario ex 150/190 HP [Fighting, Fighting]; Bench: empty
- Hydreigon board: Active Mega Absol ex 170/170 HP [Darkness]; Bench: empty
- Lucario's Energy this turn: Fighting (next: Fighting)
- Moves:
  - Lucario draws Professor's Research
  - Lucario plays Korrina
  - Lucario attaches 1 Fighting Energy to Mega Lucario ex (Active) (turn's Energy)
  - Lucario attacks with Fighting Pulse (90 base; If this Pokémon has at least 1 extra [F] Energy attached, this attack does 50 more damage.)
    - what changed: Lucario points 1 → 4; Hydreigon's Mega Absol ex knocked out

**Game over:** Lucario 4, Hydreigon 0, after turn 6.

---

## Game 5: seed 72130008. Lucario goes first. Lucario wins 4–1 on turn 9.

**Setup** (points: Hydreigon 0, Lucario 0)
- Hydreigon hand: Poké Ball, Deino, Deceptive Needle, Bombirdier, Mega Absol ex
- Lucario hand: Field Blower, Poké Ball, Lucario, Professor's Research
- Moves:
  - Hydreigon puts Bombirdier into play (Active)
  - Hydreigon puts Deino into play (Bench)
  - Hydreigon puts Mega Absol ex into play (Bench)
  - Hydreigon ends the turn [forced]

**Turn 1 — Lucario** (points: Hydreigon 0, Lucario 0)
- Hydreigon hand: Poké Ball, Deceptive Needle
- Lucario hand: Field Blower, Poké Ball, Lucario, Professor's Research, Mega Lucario ex
- Hydreigon board: Active Bombirdier 70/70 HP; Bench: Mega Absol ex 170/170 HP; Deino 60/60 HP
- Lucario board: Active Bonsly 30/30 HP; Bench: empty
- Lucario's Energy this turn: none (next: Fighting)
- Moves:
  - Lucario draws Mega Lucario ex
  - Lucario plays Poké Ball
  - Lucario plays Professor's Research
  - Lucario puts Hitmonlee into play (Bench)
  - Lucario attacks with Teary Attack (10 base; During your opponent's next turn, attacks used by the Defending Pokémon do -30 damage.)
  - Lucario ends the turn [forced]
    - what changed: Hydreigon's Bombirdier 70 → 60 HP

**Turn 2 — Hydreigon** (points: Hydreigon 0, Lucario 0)
- Hydreigon hand: Poké Ball, Deceptive Needle, Hydreigon
- Lucario hand: Field Blower, Mega Lucario ex, Lucario, Professor's Research, Copycat
- Hydreigon board: Active Bombirdier 60/70 HP; Bench: Mega Absol ex 170/170 HP; Deino 60/60 HP
- Lucario board: Active Bonsly 30/30 HP; Bench: Hitmonlee 80/80 HP
- Hydreigon's Energy this turn: Darkness (next: Darkness)
- Moves:
  - Hydreigon draws Hydreigon
  - Hydreigon plays Poké Ball
  - Hydreigon puts Deino into play (Bench)
  - Hydreigon plays Deceptive Needle
  - Hydreigon attaches Deceptive Needle to Bombirdier (Active)
  - Hydreigon attaches 1 Darkness Energy to Bombirdier (Active) (turn's Energy)
  - Hydreigon attacks with Dark Cutter (30 base; no text)
  - Hydreigon ends the turn [forced]
    - what changed: Lucario's Bonsly 30 → 20 HP

**Turn 3 — Lucario** (points: Hydreigon 0, Lucario 0)
- Hydreigon hand: Hydreigon
- Lucario hand: Field Blower, Mega Lucario ex, Lucario, Professor's Research, Copycat, Mega Lucario ex
- Hydreigon board: Active Bombirdier 60/70 HP [Darkness] +Deceptive Needle; Bench: Deino 60/60 HP; Mega Absol ex 170/170 HP; Deino 60/60 HP
- Lucario board: Active Bonsly 20/30 HP; Bench: Hitmonlee 80/80 HP
- Lucario's Energy this turn: Fighting (next: Fighting)
- Moves:
  - Lucario draws Mega Lucario ex
  - Lucario retreats Active, bringing up Hitmonlee (Bench)
  - Lucario attaches 1 Fighting Energy to Hitmonlee (Active) (turn's Energy)
  - Lucario plays Professor's Research
  - Lucario puts Riolu into play (Bench)
  - Lucario attacks with Stretch Kick (0 base; This attack does 30 damage to 1 of your opponent's Benched Pokémon.)
  - Lucario puts damage: 30 to Mega Absol ex (Bench)
  - Lucario ends the turn [forced]
    - what changed: Hydreigon's Mega Absol ex 170 → 140 HP

**Turn 4 — Hydreigon** (points: Hydreigon 0, Lucario 0)
- Hydreigon hand: Hydreigon, Deceptive Needle
- Lucario hand: Field Blower, Mega Lucario ex, Lucario, Mega Lucario ex, Copycat, Cyrus
- Hydreigon board: Active Bombirdier 60/70 HP [Darkness] +Deceptive Needle; Bench: Deino 60/60 HP; Mega Absol ex 140/170 HP; Deino 60/60 HP
- Lucario board: Active Hitmonlee 80/80 HP [Fighting]; Bench: Riolu 60/60 HP; Bonsly 20/30 HP
- Hydreigon's Energy this turn: Darkness (next: Darkness)
- Moves:
  - Hydreigon draws Deceptive Needle
  - Hydreigon attaches 1 Darkness Energy to Mega Absol ex (Bench) (turn's Energy)
  - Hydreigon attacks with Dark Cutter (30 base; no text)
  - Hydreigon ends the turn [forced]
    - what changed: Lucario's Hitmonlee 80 → 40 HP

**Turn 5 — Lucario** (points: Hydreigon 0, Lucario 0)
- Hydreigon hand: Hydreigon, Deceptive Needle
- Lucario hand: Field Blower, Mega Lucario ex, Lucario, Mega Lucario ex, Copycat, Cyrus, Pokémon Center Lady
- Hydreigon board: Active Bombirdier 60/70 HP [Darkness] +Deceptive Needle; Bench: Deino 60/60 HP; Mega Absol ex 140/170 HP [Darkness]; Deino 60/60 HP
- Lucario board: Active Hitmonlee 40/80 HP [Fighting]; Bench: Riolu 60/60 HP; Bonsly 20/30 HP
- Lucario's Energy this turn: Fighting (next: Fighting)
- Moves:
  - Lucario draws Pokémon Center Lady
  - Lucario plays Cyrus
  - Lucario chooses Mega Absol ex (Bench) to become Active [forced]
  - Lucario evolves Riolu (Bench) into Mega Lucario ex
  - Lucario attaches 1 Fighting Energy to Mega Lucario ex (Bench) (turn's Energy)
  - Lucario attacks with Stretch Kick (0 base; This attack does 30 damage to 1 of your opponent's Benched Pokémon.)
  - Lucario puts damage: 30 to Bombirdier (Bench)
  - Lucario ends the turn [forced]
    - what changed: Hydreigon's Bombirdier 60 → 30 HP

**Turn 6 — Hydreigon** (points: Hydreigon 0, Lucario 0)
- Hydreigon hand: Hydreigon, Deceptive Needle, Professor's Research
- Lucario hand: Field Blower, Pokémon Center Lady, Lucario, Mega Lucario ex, Copycat
- Hydreigon board: Active Mega Absol ex 140/170 HP [Darkness]; Bench: Deino 60/60 HP; Bombirdier 30/70 HP [Darkness] +Deceptive Needle; Deino 60/60 HP
- Lucario board: Active Hitmonlee 40/80 HP [Fighting]; Bench: Mega Lucario ex 190/190 HP [Fighting]; Bonsly 20/30 HP
- Hydreigon's Energy this turn: Darkness (next: Darkness)
- Moves:
  - Hydreigon draws Professor's Research
  - Hydreigon retreats Active, bringing up Bombirdier (Bench)
  - Hydreigon plays Professor's Research
  - Hydreigon plays Lucky Ice Pop
    - what changed: Hydreigon's Bombirdier 30 → 50 HP
  - Hydreigon attaches 1 Darkness Energy to Mega Absol ex (Bench) (turn's Energy)
  - Hydreigon attacks with Dark Cutter (30 base; no text)
  - Hydreigon ends the turn [forced]
    - what changed: Hydreigon points 0 → 1; Lucario's Hitmonlee knocked out

**Turn 7 — Lucario** (points: Hydreigon 1, Lucario 0)
- Hydreigon hand: Hydreigon, Deceptive Needle, Copycat
- Lucario hand: Field Blower, Pokémon Center Lady, Lucario, Mega Lucario ex, Copycat, X Speed
- Hydreigon board: Active Bombirdier 50/70 HP [Darkness] +Deceptive Needle; Bench: Deino 60/60 HP; Mega Absol ex 140/170 HP [Darkness, Darkness]; Deino 60/60 HP
- Lucario board: Active none; Bench: Mega Lucario ex 190/190 HP [Fighting]; Bonsly 20/30 HP
- Lucario's Energy this turn: Fighting (next: Fighting)
- Moves:
  - Lucario draws X Speed
  - Lucario promotes Mega Lucario ex (Bench) to Active
  - Lucario attaches 1 Fighting Energy to Mega Lucario ex (Active) (turn's Energy)
  - Lucario plays Pokémon Center Lady
  - Lucario heals 30 from Bonsly (Bench) and cures status [forced]
    - what changed: Lucario's Bonsly 20 → 30 HP
  - Lucario attacks with Fighting Pulse (90 base; If this Pokémon has at least 1 extra [F] Energy attached, this attack does 50 more damage.)
    - what changed: Hydreigon's Bombirdier knocked out; Lucario points 0 → 1
  - Hydreigon promotes Mega Absol ex (Bench) to Active
  - Lucario ends the turn [forced]

**Turn 8 — Hydreigon** (points: Hydreigon 1, Lucario 1)
- Hydreigon hand: Hydreigon, Deceptive Needle, Copycat, Hydreigon
- Lucario hand: Field Blower, X Speed, Lucario, Mega Lucario ex, Copycat
- Hydreigon board: Active Mega Absol ex 140/170 HP [Darkness, Darkness]; Bench: Deino 60/60 HP; Deino 60/60 HP
- Lucario board: Active Mega Lucario ex 190/190 HP [Fighting, Fighting]; Bench: Bonsly 30/30 HP
- Hydreigon's Energy this turn: Darkness (next: Darkness)
- Moves:
  - Hydreigon draws Hydreigon
  - Hydreigon plays Deceptive Needle
  - Hydreigon attaches Deceptive Needle to Mega Absol ex (Active)
  - Hydreigon attaches 1 Darkness Energy to Deino (Bench) (turn's Energy)
  - Hydreigon ends the turn
    - what changed: Lucario's Mega Lucario ex 190 → 180 HP

**Turn 9 — Lucario** (points: Hydreigon 1, Lucario 1)
- Hydreigon hand: Hydreigon, Hydreigon, Copycat
- Lucario hand: Field Blower, X Speed, Lucario, Mega Lucario ex, Copycat, Riolu
- Hydreigon board: Active Mega Absol ex 140/170 HP [Darkness, Darkness] +Deceptive Needle; Bench: Deino 60/60 HP; Deino 60/60 HP [Darkness]
- Lucario board: Active Mega Lucario ex 180/190 HP [Fighting, Fighting]; Bench: Bonsly 30/30 HP
- Lucario's Energy this turn: Fighting (next: Fighting)
- Moves:
  - Lucario draws Riolu
  - Lucario attaches 1 Fighting Energy to Mega Lucario ex (Active) (turn's Energy)
  - Lucario attacks with Fighting Pulse (90 base; If this Pokémon has at least 1 extra [F] Energy attached, this attack does 50 more damage.)
    - what changed: Hydreigon's Mega Absol ex knocked out; Lucario points 1 → 4

**Game over:** Lucario 4, Hydreigon 1, after turn 9.
---

## Added 2026-09-24: how k3 uses Hyper Ray and Roar in Unison across all 1,000 table games

Counted by replaying every Hydreigon v Lucario game from the table (seeds 72,130,000–72,130,999) and checking the legal moves at each of Hydreigon's decisions. The replays reproduce the table (Hydreigon wins 302 of 1,000).

**The engine's card matches the real card.** The engine's text for Roar in Unison and Hyper Ray is word for word the Limitless card text (Hydreigon, B1 157). In play, all 1,251 uses of Roar in Unison did exactly what the text says: 2 Darkness Energy onto that Hydreigon, 30 damage to it, never twice by the same Hydreigon in a turn, and never using up the turn's normal Energy. No rules error found here.

**k3 fires Hyper Ray only when it knocks out the Active Pokémon.** Hyper Ray was available on 1,203 of Hydreigon's turns.

| Lucario's Active Pokémon | k3 used Hyper Ray | k3 ended the turn without it |
|---|---:|---:|
| 130 HP or less (Hyper Ray knocks it out) | 732 (99%) | 8 |
| more than 130 HP (almost always a healthy Mega Lucario ex, 190 HP) | 12 (3%) | 434 |

On the other 17 turns, Hyper Ray was available earlier in the turn but not at the end (for example, after a retreat), and it wasn't used.

- In 343 of those 442 passes, Hydreigon itself had more than 60 HP, so it could have refilled with Roar in Unison the next turn. The passes aren't about protecting a Hydreigon too weak to use its ability.
- k3 does use the refill. On the Hydreigon turn right after a Hyper Ray, it used Roar in Unison 370 times out of 375 where it was usable (99%). Overall it used Roar in Unison on 83% of the turns it was usable without knocking Hydreigon out.
- The two-turn line a person would play against Mega Lucario ex (Hyper Ray for 130, refill, Hyper Ray again for the knockout and 3 points) is exactly the one k3 skips.
- Association only, not a measured effect: in the 338 games with at least one such pass, Hydreigon won 11.8%; in the other 662 it won 39.6%. Those games also tend to be the ones where a healthy Mega Lucario ex is already in front of Hydreigon, so the gap isn't all caused by the pass.


---

Regenerate any of these: rules4 add-on 0.7.2 (module SHA-256 0fee43ce…), the two Sept 8 lists (fingerprints in `limitless_check_2026-09-23.md`), `engine_play`/`RawEnv.reset` with players k3,k3 on the seed above, Hydreigon in the seat stated.
