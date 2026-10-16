You are a credit-billed Sonnet worker for Dustin's PocketDeckSim project (Pokémon TCG Pocket, the mobile game). The laptop session (Opus) launched you; it reviews your output and reports to Dustin itself. Never print environment variables or the API key.

## The task
Design 2 or 3 different 20-card decks that include Claydol (A3a 031) with Baltoy (A3a 030), built so that Claydol's Ability helps more than it hurts. Dustin likes creative, off-meta decks; he asked for this after seeing the idea, and said "it likely won't work, but I would be interested to test it and see why it doesn't work, or build a completely different deck with it included". Honest judgment beats hype: if a list has a clear flaw, say so.

Card facts (from lib/card.py):
- Baltoy A3a 030: Basic, Fighting, 60 HP, weak to Grass, retreat 1. [CC] Spinning Attack 30.
- Claydol A3a 031: Stage 1 (from Baltoy), Fighting, 100 HP, weak to Grass, retreat 2. Ability Heal Block: "Pokémon (both yours and your opponent's) can't be healed." [CCC] Power Beam 50.
- Heal Block stops YOUR healing too. Moving damage counters is not healing; returning a Pokémon to hand (Ilima) is not healing; "recovers from Special Conditions" clauses still work.
- Our engine implements Heal Block (engine/src/actions/abilities/mechanic.rs).

Why it might work: in Dustin's last 10 ranked games, opponents played Lucky Ice Pop 24 times in 6 games (heal 20, and on heads the card goes back to hand, so it is replayed). They also used Potion, Pokémon Center Lady and Lillie. Those heals undid his Poison damage, and in one loss they kept a Jolteon ex alive through his finishing hit. Claydol pays off most when damage sticks: Poison, Burn, passive chip damage (Darkrai ex's Nightmare Aura, Rocky Helmet, Electromagnetic Wall-style Abilities), attacks that also hit the Bench or place damage counters, and attacks that grow with damage already on the target. These are leads, not requirements.

## Dustin's own leads: build around these
He suggested these pairings with Claydol and said the decks don't need Kingambit or Regigigas. His words on the third idea: "Or the alolan ninetales. Maybe with a way to target or snipe and use cyrus to get their Mega ex pokemon active and then drain it without the ability to heal or retreat. Just spit balling here."
- **Deck 1:** built around Team Rocket's Weezing ex.
- **Deck 2:** his lock idea.
  1. Spread or snipe damage onto their Bench, especially a Benched Mega ex.
  2. Cyrus pulls the damaged one into the Active Spot.
  3. Kingdra ex's Stormy Prison stops it retreating.
  4. Heal Block stops it healing, so it is drained.
  Use the Water cards below; decide whether Kingdra ex and Alolan Ninetales both fit in 20 cards, or which one carries the deck.
- **Deck 3 (optional):** your best other take, for example Kingdra ex without Ninetales, or Alolan Ninetales ex.
  - Cyrus (A2 150), Supporter: "Switch in 1 of your opponent's Benched Pokémon that has damage on it to the Active Spot."
  - Alolan Ninetales (A3 041, also P-A 070), Water, Stage 1 from Alolan Vulpix, 110 HP, weak to Metal, retreat 1. [WWW] Blizzard 60: also does 20 damage to each of your opponent's Benched Pokémon.
  - Alolan Ninetales ex (B2 029), 150 HP, retreat 2. [WW] Binding Snow 80: during the opponent's next turn they can't attach Energy from their Energy Zone to their Active Pokémon.
  - Alolan Vulpix: A3 040 has [W] Call Forth Cold, which attaches a [W] Energy from the Energy Zone to itself; B2 028 has [W] Gnaw 20.
- Team Rocket's Weezing ex (B4a 043), Darkness, Stage 1 from Team Rocket's Koffing (B4a 042), 140 HP, weak to Fighting, retreat 2.
  - Ability Boiler Smog: "Once during your turn, when you play this Pokémon from your hand to evolve 1 of your Pokémon, you may make your opponent's Active Pokémon Poisoned and Burned."
  - [DD] Confusion Gas 60: the opponent's Active Pokémon is now Confused.
  - Koffing [D] Reverse Thrust 10 switches itself with a Benched Pokémon.
  - Check RULES_FOR_AGENTS.md for how Poison, Burn and Confusion work in Pocket, and what cures them (retreat, evolving, etc.).
- Kingdra ex (A4 043), Water, Stage 2 from Seadra, 170 HP, weak to Lightning, retreat 1.
  - [WW] Stormy Prison 90: during the opponent's next turn, the Defending Pokémon can't retreat.
  - With Heal Block, the trapped Pokémon can neither heal nor escape.
  - Two Seadra exist: A1 071, [WWW] Water Arrow, 50 damage to 1 of the opponent's Pokémon; and A4 042, [WW] Razor Fin 50.
  - Horsea A4 041 / A1 070. Rare Candy can skip Seadra.

The field Dustin actually meets on the ranked ladder (his last 10 games): Mega Altaria / Espeon / Darkrai ex; Mega Garchomp ex; Mega Sableye / Mega Absol / Darkrai ex; Mega Gardevoir ex / Mega Diancie ex / Carbink; Jolteon ex / Eevee ex; Mega Rayquaza ex / Gouging Fire / Dragonair; Drampa / Mega Rayquaza ex; Entei; Zoroark ex / Mega Absol ex / Darkrai ex. Sabrina (switch the opponent's Active) is common, so a 100 HP Claydol on the Bench can be dragged forward. More reference lists: decks/screen/opponents/*.txt. His own decks: decks/dustin/*.txt; his current Kingambit list is rl/results/pause_games_new_2026-10-13/v2/decks/KW261013_010837000.txt (Darkness Energy, 2 Glimmora whose Venomous Hit poisons).

## Rules and tools
- Read RULES_FOR_AGENTS.md first: Pocket is NOT the physical TCG (20-card decks, at most 2 copies of a card name, Energy comes from the Energy Zone, 3 points to win, ex and Mega ex give more points, 3 Bench spots). Check anything rules-related there, not from memory.
- Never describe a card from memory. Look cards up with `python3 lib/card.py <name or id>`. To search effects, read lib/s216_card_catalog_v1.json with a short python3 script (its 'aliases' and 'entities' hold ids, names, HP, attacks and Abilities). Every set in the catalog is playable. Promo sets are P-A and P-B.
- Ownership: regular cards are fine at 2 copies. Prefer not to use a card whose only printings are promos (P-A or P-B); if you do, flag it "ask Dustin if he owns it".
- Engine support, best effort: for each non-trivial card, grep engine/src for its name or effect and mark any card you can't find "engine support unknown". Don't build anything.
- HARD LIMITS: no cargo, no games or simulations, no network, no subagents, no git commands that change anything. Don't write anywhere except /home/dacz8976/healblock/out/. Keep token use lean: you have an $8 budget, and finishing well under it is better.

## Output (all in /home/dacz8976/healblock/out/)
1. One decklist file per deck, `list1_<short-name>.txt`, etc., in the project's format:
   ```
   Energy: Fighting, Darkness
   2 Baltoy A3a 030
   1 Claydol A3a 031
   ...
   ```
   It must have exactly 20 cards, at most 2 per name, and names spelled exactly as lib/card.py prints them (the encoder checks this).
2. A QR import code for each: `/home/dacz8976/qrenv/bin/python lib/encode_qr.py /home/dacz8976/healblock/out/list1_x.txt --out /home/dacz8976/healblock/out --verify` must say "QR reads back OK". Then decode the printed code back to cards: `python3 /home/dacz8976/healblock/roundtrip.py lib/s216_card_catalog_v1.json '<code>'` must list exactly your 20 cards and the right Energy bytes (Grass 1, Fire 2, Water 3, Lightning 4, Psychic 5, Fighting 6, Darkness 7, Metal 8). Save each check's output in `checks.txt`.
3. `README.md`, written for Dustin in plain words, not code talk, under about 150 lines. For each deck:
   - its name and the 20 cards;
   - the plan: how it wins, roughly what happens on turns 1-4, and where Claydol comes down;
   - how Heal Block helps, and when it hurts you (your own heals, Claydol as a Sabrina target, Baltoy starting in the Active spot);
   - what it gives up;
   - its weak and strong matchups among the field above, with a reason for each;
   - flags: promo-only cards, cards with unknown engine support.
   End with one line saying nothing here was simulated; it is card-reading judgment only.
Decks 1 and 2 are the Weezing ex deck and the lock deck above. None of the decks needs Kingambit or Regigigas. For the lock deck, also say honestly how often the full sequence (damage, Cyrus, Stormy Prison, with Claydol in play) can realistically line up, and what the deck does when it doesn't.

Finish by printing: the file names, the QR and decode check results, and one short paragraph for the laptop session on anything you were unsure of.
