# Raticate and Manectric list card check (Sept 26, morning)

**Why:** B2e found two archetype lists far above their real Limitless results (`../b2e_rows_2026-09-26/READING.md`):
- **Team Rocket's Raticate ex / Alolan Ninetales ex:** 57.5% under kp3 against 41.2% real. Under k3 it scores 41.1%. The mixed rows show kp3's own piloting of Raticate carries the rise (+19.8 ± 1.6; `../b2e_mixed_2026-09-26/`).
- **Mega Manectric ex / Heliolisk:** about 64% under both pilots against 49% real.

A card or rules implementation that is too strong would explain either, so every card in both lists was checked against the engine. The method is the Altaria check's (`../altaria_card_check_2026-09-26/`):
- code reading only;
- every clause of each card's `lib/card.py` text;
- its code path, tests and Dustin's recordings;
- three independent skeptics on every finding that wasn't clean.

**Scope:**
- five checkers: the Raticate list, Raticate ex itself, the Manectric list, the Manectric Pokémon, and both lists' interactions with the eight panel decks;
- 15 skeptic reads.

Full output: `card_check.json`.

**Result: no card in either list does more in the engine than its text allows.** So card implementation does not explain either gap.
- **Thieving Incisors** matches the card, traced end to end and backed by footage:
  - it moves exactly one random Energy from the opponent's Active to Raticate ex and keeps the Energy's type;
  - it is optional;
  - it fires once per evolve-from-hand;
  - the turn's attach is untouched.
- **What explains Raticate's +16 under kp3** is kp3 using an ability k3 leaves unpriced. That's a piloting difference, not a rule.
  - What's left: real players get less from Raticate than kp3 does, or the panel decks' bots don't play around it: they keep powering an Active that Raticate can strip, and the mixed rows show kp3 on the opponents takes back only 4 points.
  - Either way, kp3's screen will read Dustin's Raticate decks (13, 14, 15) as stronger than the ladder will. Treat their screen numbers with that warning until it is explained.
- **Manectric's +15 under both pilots** is not a card bug either. The candidates are how both pilots play against it, the list, or the population.

**Engine deviations found along the way.** None makes either list stronger. They go to the cloud's repair list via Dustin, each as its own commit with its own replay.
1. **Clemont's Backpack applies to non-attack damage and to your own Pokémon.**
   - The card: "During this turn, attacks used by your Magneton or Heliolisk do +20 damage to your opponent's Pokémon."
   - The engine: the Backpack branch skips the attack-only gate and never checks the target's side (`hooks/core.rs` 1069-1087).
   - The result: a Poisoned or Burned Active Heliolisk (or Magneton) takes +20 at the Checkup per Backpack played that turn.
   - Upheld 3 to 0. It hurts the Manectric side, so it can't explain the overrating. It can arise in B2e's Manectric games.
2. **Roar in Unison is offered while Binding Snow's lock is on.** Using it does nothing but spend the once-per-turn Ability. Ice Maker is correctly gated. Minor; it can only hurt the Hydreigon player who picks it. Upheld as a move-generation difference (`move_generation_abilities.rs` 120 against 366).
3. **Clemont played from a 10-card hand can reach 11 cards.** Deck searches have no hand-size cap; draws stop at 10 (`state/mod.rs` 833-842 against 811-818). Negligible.
4. **Promotion after an end-of-turn knockout comes after the next draw.** Already confirmed on footage (`../altaria_card_check_2026-09-26/`, deviation 3). In these pairings it helps only the held decks, and equally under k3 and kp3.

**Open in Pocket, left as they are:**
- **Binding Snow's lock:** it follows the player, not the Pokémon hit, and the wording supports that.
- **Thieving Incisors after Ilima returns Raticate ex:** a fresh Pokémon, so it can fire again (rules/05 #25; only decks 13 and 15 run Ilima).
- **Poké Ball and Clemont random picks:** per copy.
- **Copycat corners.**
