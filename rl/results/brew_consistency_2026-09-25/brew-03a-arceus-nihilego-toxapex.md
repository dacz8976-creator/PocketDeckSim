# Brew 03a: Arceus / Nihilego / Toxapex

List: `decks/brews/brew-03a-arceus-nihilego-toxapex.txt`. Main attackers: Toxapex, Arceus ex. Combo: Nihilego, Toxapex in play by your turn 3.
Ladder Log: 1-3.

## What the cards allow (20,000 shuffles, no opponent)

The card-draw model plays solitaire: draws, plays its draw and search cards, puts Basics down, evolves, and gives each turn's energy to the Pokémon closest to attacking. It shows what the list can do, not what a player or bot will do.

| | going first | going second |
|---|---|---|
| Opening hand with one Basic | 52% | 52% |
| A main attacker could attack by your turn 2 | 0% | 44% |
| A main attacker could attack by your turn 3 | 57% | 92% |
| A main attacker could attack by your turn 4 | 97% | 96% |
| Stage 2 in play by your turn 3 | n/a | n/a |
| Combo in play by your turn 3 | 53% | 52% |
| Stuck cards in hand, end of turns 1-4 | 1.2, 0.6, 0.5, 0.5 | 1.2, 0.6, 0.5, 0.5 |

When the opening hand has one Basic, it is: Arceus ex (17% of all games), Nihilego (17% of all games), Mareanie (17% of all games).

**Chance each card has been in your hand by the end of your turn 1 / 2 / 3 / 4** (going second; going first is the same card count, a turn earlier in the game). "With search" plays the list's draw and search cards; "draws only" is the exact odds from drawing alone, ignoring the rule that the opening hand always has a Basic.

| card | with search | draws only |
|---|---|---|
| Arceus ex | 75% / 83% / 88% / 93% | 52% / 59% / 65% / 71% |
| Nihilego | 75% / 83% / 88% / 92% | 52% / 59% / 65% / 71% |
| Toxapex | 59% / 69% / 76% / 83% | 52% / 59% / 65% / 71% |
| Cyrus | 35% / 43% / 50% / 57% | 30% / 35% / 40% / 45% |
| Giant Cape | 35% / 44% / 50% / 57% | 30% / 35% / 40% / 45% |
| Mareanie | 75% / 83% / 88% / 93% | 52% / 59% / 65% / 71% |
| Poison Barb | 35% / 43% / 50% / 57% | 30% / 35% / 40% / 45% |
| Poké Ball | 59% / 68% / 75% / 81% | 52% / 59% / 65% / 71% |
| Team Rocket's Goo-zooka | 59% / 69% / 76% / 83% | 52% / 59% / 65% / 71% |

## What the bot does with it (k3 piloting, 400 games against each opponent bot)

k3 plays the list against the 8 table decks, 50 deals each, once against a bot that only ends its turn ('et': pure goldfish) and once against one that attaches and attacks ('aa': points given up before the list's first real attack). "Could" means a main attacker was in the Active Spot with an attack available; "did" means k3 used it.

**Bot numbers untrusted for this list**: some of its cards hit a path k3 prices badly (see the last section).

| | vs et, first | vs et, second | vs aa, first | vs aa, second |
|---|---|---|---|---|
| games | 197 | 203 | 197 | 203 |
| main attacker could / did attack by turn 2 | 0% / 0% | 12% / 12% | 0% / 0% | 8% / 8% |
| main attacker could / did attack by turn 3 | 9% / 9% | 56% / 56% | 7% / 7% | 45% / 45% |
| main attacker could / did attack by turn 4 | 52% / 52% | 62% / 62% | 32% / 32% | 52% / 52% |
| never attacked with a main attacker | 37% | 36% | 55% | 47% |
| points given up before the first main attack (average; share of games with any) | 0.00; 0% | 0.00; 0% | 0.47; 29% | 0.06; 5% |
| Stage 2 in play by turn 3 | 0% | 0% | 0% | 0% |
| dead cards at the end of turns 2-4 (average) | 1.5 | 1.4 | 1.4 | 1.4 |
| won (a sanity check, not a strength rating) | 100% | 100% | 92% | 99% |

Games that crashed (a card the engine can't play): 0.
Dead cards: cards in hand that no offered move could use when the list attacked or ended its turn (a Supporter held because one was already played that turn doesn't count).

## Where the bot is blind on this list

- **Mareanie** (B3b 046): Venoshock: ExtraDamageIfDefenderStatus estimated at printed damage: k3's damage estimate uses the printed damage.
- **Poison Barb** (A3 146): its effect pays off during the opponent's turn, which k3 doesn't search (its clock counts HP and the opponent's best damage, not effects like this).
- **Rocky Helmet** (A4b 322): its effect pays off during the opponent's turn, which k3 doesn't search (its clock counts HP and the opponent's best damage, not effects like this).
- **Team Rocket's Goo-zooka** (B4a 068): its effect pays off during the opponent's turn, which k3 doesn't search (its clock counts HP and the opponent's best damage, not effects like this).
- **Toxapex** (B3b 047): Severe Poison: InflictPoisonWithCustomCheckupDamage estimated at printed damage: k3's damage estimate uses the printed damage.

Engine commit 86e6154; goldfish seeds 22,200,000,000 + opponent x 10,000 + i (i < 50); card-draw model seed 22,100,000,000.
