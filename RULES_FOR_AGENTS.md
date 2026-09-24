# Pokémon TCG Pocket — rules an agent needs (2026-09-15, updated 2026-09-22)

Pocket is the mobile game, not the physical Pokémon TCG. Most of what a model "knows" about
the Pokémon TCG is the physical game and is wrong here. Read this once; look cards up, never
recall them (`python lib/card.py <name or id>` prints exact text from `deckgym-database.json`).

Checked 2026-09-15 against the official Pokémon Support "TCG Pocket Battle Rules FAQ", Bulbapedia's
Pokémon TCG Pocket page and one community how-to-play guide (a Sonnet review agent, six pages).
Lines marked **[verify]** were not found in those pages; nothing in the file was contradicted.
Updated 2026-09-21 from the in-app Tips (About Battle Rules), the official Detailed Battle FAQ, Dustin's
recordings and his statements; opening-hand line updated 2026-09-22 with Dustin's OK. Full sourced detail, open questions and known engine bugs: `rules/`
(start with its README).

## Deck, points, winning

- 20 cards. At most **2 copies of any card name** (all printings of a name share the limit;
  "Pikachu" and "Pikachu ex" are different names). At least one Basic Pokémon.
- No energy cards. The deck declares one or more **energy types**; the **Energy Zone** produces
  one energy per turn, randomly among the declared types. Two types means roughly half your
  energy is the wrong type on a given turn — this is why almost every good deck is mono-type.
- You win at **3 points**. Knock out a normal Pokémon = 1 point, a **Pokémon ex = 2 points**, a
  **Mega Evolution Pokémon ex = 3 points** (the rule box on the card says so; one Mega KO ends
  the game). You also win if the opponent has no Pokémon left in play. In the observed T2 setup, the player at 2 points
  receives the 3rd point while their last Pokémon is Knocked Out in the same attack; the result was a tie. One video
  seat observed; opponent final 2 points inferred from the ex KO. Rules4 implements this narrow case. Both reaching 3
  with Pokémon left is a [COMMUNITY] claim and remains unverified. See `rules/05` #2.
- Battle clock runs out → that player **loses**. Turn limit (30 turns in versus; the on-screen
  counter counts both players' turns) → **tie**.
- There is **no deck-out loss** — an empty deck just means no draw (Bulbapedia).
- Hand limit **10** cards; draws past 10 are skipped and the card stays in the deck.

## Board and turn

- One Active Pokémon and a **Bench of 3** (not 5).
- Setup: 5-card opening hand guaranteed to contain a Basic; coin flip for who goes first. The hand is
  dealt as 5 random cards; if none is a Basic, one of them is swapped for a Basic, so extra Basics are
  **not** favoured (two statistical studies; implemented by `rules1` and retained in active `rules4`, see `rules/09`).
- **The player going first gets no energy from the Energy Zone on their first turn** and
  cannot evolve on it, but **does draw** and may play a Supporter. A **zero-cost attack is allowed** on that first turn (official FAQ: an
  attack with no Energy symbol "can be used on the first turn of the player that goes first"; so
  can any attack whose cost a card effect has paid).
- Every turn, in this order: draw 1 → then any order of: attach the turn's energy to one of
  your Pokémon (once; unattached energy is discarded at end of turn — Bulbapedia and
  community guides), play Basics to the
  Bench, evolve, play Items (no limit), play **one Supporter** per turn, attach Tools (one per
  Pokémon), play a Stadium (one per turn; one in play at a time; can't play one with the same name as the one in play; playing one replaces the one in play, including your opponent's — Dustin, 2026-09-16), use Abilities,
  **retreat once per turn** (discard energy equal to the Retreat Cost) → attack, which ends the
  turn. You may end the turn without attacking. **Mega Evolving does not end the turn.**
- A Pokémon **can't evolve the turn it was put into play**, and no Pokémon evolves on either
  player's first turn. A Pokémon evolves at most once per turn (Rare Candy: Basic straight to
  Stage 2, not on your first turn, not on a Pokémon played this turn).
- **Weakness is a flat +20** damage (×2 instead while Bounded Field is in play, for non-Mega-ex
  attackers). **Never on Benched Pokémon. There is no Resistance** in Pocket.
- **Damage order** (official FAQ; confirmed in Dustin's Skarmory game: 60 into Metal Core Barrier
  under Bounded Field did 60×2−50 = 70): the attack's damage → the attacker's own boosts and
  debuffs → Weakness → the defender's reductions (Tools, "takes −X"), never below 0. An attack that
  does 0 on its own gets no Weakness. The damage order was repaired in rules1 and remains fixed
  in active rules4. Whether Weakness applies after an attacker-side debuff reduces damage to 0
  remains open (`rules/05` #11).
- **Bench damage:** a boost reaches Benched targets only if its text says "your opponent's
  Pokémon", not "…Active Pokémon".
- **Knock Outs during your turn** (Ability damage, removing a Tool or Stadium HP bonus) count at
  once: points immediately (game over on the 3rd), the owner promotes if it was Active, and your
  turn goes on — you can still attack (Dustin). After a **double Knock Out** the attacker promotes
  first (Dustin + a recording).
- **End of turn:** the attack resolves completely (damage, its effects, Rocky Helmet-style
  retaliation, Knock Outs) → "at the end of the turn" effects, turn player's first → Pokémon
  Checkup → Knock Outs from the Checkup.
- **Effects of attacks on a Pokémon end when it goes to the Bench or evolves** (in-app Tips).
- **When a card can be played** (Dustin's rule): it's blocked only when what you can see (hand,
  board, discard piles, whether the deck is empty) shows it can't work; if it depends on what's
  left in the deck, it's allowed (Poké Ball with no Basics left, Cabbie with no Stadium left).
  Anything that draws is blocked on an empty deck, except Copycat. Since v1.7.0 Gladion, Clemont
  and Team Galactic Grunt can be played even when their named cards are visibly all gone (seen in
  play for Gladion; Clemont and Grunt rest on one Japanese source). A Supporter
  played for nothing still counts as "a Supporter played this turn" (seen in play with Gladion).
- **Hidden information:** cards going from a deck into a hand are hidden from the opponent (card
  backs and the count only); cards taken into a hand from the discard or from play are known.
- Damage from Abilities and Special Conditions is not "damage from an attack": effects that
  reduce or prevent attack damage (Shuckle ex's Solid Shell, Oricorio's Safeguard, "-20 from
  attacks" Tools) do nothing against poison ticks, ability pings or Rocky Helmet (official:
  Mimikyu ex FAQ).

## Special Conditions (the part the engine got wrong for six months)

Checked at every **Pokémon Checkup**, which happens after each player's turn and is not part of
either player's turn. Everything below is confirmed word for word by the in-app Tips (About Battle
Rules, 2026-09-21). If both players have conditions, the player whose turn just ended goes first;
on one Pokémon the order is Poison → Burn → Sleep → Paralysis; Knock Outs happen at the end.

- **Poisoned**: 10 damage at every Checkup (both players' turns) until cured. Cards can raise
  the amount (Nihilego +10; Toxapex B3b's Severe Poison sets it to 40).
- **Burned**: 20 damage at every Checkup, then flip: heads cures it.
- **Asleep**: can't attack or retreat. At every Checkup flip: heads wakes it (so a Pokémon put
  to Sleep flips at the very next Checkup and can wake before its own turn).
- **Paralyzed**: can't attack or retreat. Cured at the Checkup **after the affected player's
  next turn** — so it always costs the victim exactly one turn.
- **Confused**: flip when it attacks; **tails = the attack does nothing**. No self-damage
  (that's the physical TCG).
- Asleep, Paralyzed and Confused **replace each other** (only one at a time). Poison and Burn
  stack with anything.
- Retreating, being switched out, or evolving **removes all Special Conditions**. Benched
  Pokémon can't have conditions.
- Some Pokémon are immune (Arceus ex's Fabled Luster; Comfey's Flower Shield for your Psychic
  energy holders). Immunity means the condition is never applied, so nothing to cure.

## Words on cards that trip models up

- "**Team Rocket's** X" is a different card from X (it's in the name; Team Rocket's Researcher
  only finds cards with "Team Rocket" in the name).
- **Mega Evolution ex** cards take the named Pokémon's place in its line: they evolve from its
  pre-evolution (Mega Lucario ex from Riolu, Mega Blaziken ex from Combusken, Mega Altaria ex from
  Swablu) or are Basic (Mega Absol ex) — check the card. They give 3 points when knocked out.
- "**Once during your turn**" abilities are once per turn per Pokémon (two copies = two uses).
- "**This attack does X more damage**" adds before Weakness. Coin-flip attacks use one coin
  per stated flip; "flip until tails" is unbounded.
- An **ex** in the name doubles the points the opponent gets, nothing else.

## What an agent should do with this

Never state a card's HP, cost, weakness, or text from memory — run the lookup. Never assume a
physical-TCG rule applies. When Dustin states a rule, he's right and this file is wrong — fix
the file. When the engine and this file disagree, this file wins and the engine has a bug.

Sources used for the check: support.pokemon.com Battle Rules FAQ (article 38906248102292),
bulbapedia.bulbagarden.net/wiki/Pokémon_Trading_Card_Game_Pocket, pokemon-zone.com how-to-play.
Rare Candy's restrictions are printed on the card itself (`python lib/card.py "Rare Candy"`).
2026-09-21 update: in-app Tips › About Battle Rules (Dustin's screenshots), the official Detailed
Battle FAQ, Dustin's battle recordings and statements — all traced in `rules/06_sources.md`.
