# Brew 06b: Pyukumuku / Silvally / TR Scyther (Grass)

List: `decks/brews/brew-06b-pyukumuku-silvally-scyther-grass.txt`. Main attackers: Silvally, Team Rocket's Scyther. Combo: Pyukumuku, Silvally in play by your turn 3.
Ladder Log: 0-3.

**List check:** Pyukumuku's Sprinkle Water [W] can't be paid with Grass Energy.

## What the cards allow (20,000 shuffles, no opponent)

The card-draw model plays solitaire: draws, plays its draw and search cards, puts Basics down, evolves, and gives each turn's energy to the Pokémon closest to attacking. It shows what the list can do, not what a player or bot will do.

| | going first | going second |
|---|---|---|
| Opening hand with one Basic | 41% | 41% |
| A main attacker could attack by your turn 2 | 0% | 73% |
| A main attacker could attack by your turn 3 | 82% | 96% |
| A main attacker could attack by your turn 4 | 99% | 99% |
| Stage 2 in play by your turn 3 | n/a | n/a |
| Combo in play by your turn 3 | 59% | 59% |
| Stuck cards in hand, end of turns 1-4 | 2.3, 1.7, 1.5, 1.4 | 2.3, 1.7, 1.5, 1.4 |

When the opening hand has one Basic, it is: Team Rocket's Scyther (12% of all games), Pyukumuku (12% of all games), Type: Null (11% of all games), Teal Mask Ogerpon ex (6% of all games).

**Chance each card has been in your hand by the end of your turn 1 / 2 / 3 / 4** (going second; going first is the same card count, a turn earlier in the game). "With search" plays the list's draw and search cards; "draws only" is the exact odds from drawing alone, ignoring the rule that the opening hand always has a Basic.

| card | with search | draws only |
|---|---|---|
| Pyukumuku | 77% / 88% / 95% / 98% | 52% / 59% / 65% / 71% |
| Silvally | 68% / 85% / 94% / 98% | 52% / 59% / 65% / 71% |
| Team Rocket's Scyther | 77% / 89% / 95% / 98% | 52% / 59% / 65% / 71% |
| Copycat | 60% / 70% / 77% / 84% | 52% / 59% / 65% / 71% |
| Cyrus | 39% / 54% / 65% / 76% | 30% / 35% / 40% / 45% |
| Gladion | 40% / 54% / 66% / 75% | 30% / 35% / 40% / 45% |
| Protective Poncho | 39% / 53% / 66% / 76% | 30% / 35% / 40% / 45% |
| Teal Mask Ogerpon ex | 50% / 64% / 76% / 85% | 30% / 35% / 40% / 45% |
| Type: Null | 79% / 91% / 97% / 99% | 52% / 59% / 65% / 71% |

## What the bot does with it (k3 piloting, 400 games against each opponent bot)

k3 plays the list against the 8 table decks, 50 deals each, once against a bot that only ends its turn ('et': pure goldfish) and once against one that attaches and attacks ('aa': points given up before the list's first real attack). "Could" means a main attacker was in the Active Spot with an attack available; "did" means k3 used it.

**Bot numbers untrusted for this list**: some of its cards hit a path k3 prices badly (see the last section).

| | vs et, first | vs et, second | vs aa, first | vs aa, second |
|---|---|---|---|---|
| games | 195 | 205 | 195 | 205 |
| main attacker could / did attack by turn 2 | 0% / 0% | 16% / 16% | 0% / 0% | 15% / 15% |
| main attacker could / did attack by turn 3 | 16% / 16% | 31% / 31% | 11% / 11% | 32% / 32% |
| main attacker could / did attack by turn 4 | 35% / 35% | 37% / 37% | 21% / 21% | 38% / 38% |
| never attacked with a main attacker | 53% | 61% | 67% | 60% |
| points given up before the first main attack (average; share of games with any) | 0.00; 0% | 0.00; 0% | 0.46; 31% | 0.15; 13% |
| Stage 2 in play by turn 3 | 0% | 0% | 0% | 0% |
| dead cards at the end of turns 2-4 (average) | 1.9 | 1.6 | 1.8 | 1.5 |
| won (a sanity check, not a strength rating) | 100% | 99% | 95% | 98% |

Games that crashed (a card the engine can't play): 0.
Dead cards: cards in hand that no offered move could use when the list attacked or ended its turn (a Supporter held because one was already played that turn doesn't count).

## Where the bot is blind on this list

- **Copycat** (B1 225): its effect mentions the opponent's hand or deck: k3 scores it as doing nothing.
- **Pyukumuku** (A3 054): ability Innards Out pays off during the opponent's turn, which k3 doesn't search (its clock counts HP and the opponent's best damage, not effects like this).
- **Rocky Helmet** (A2 148): its effect pays off during the opponent's turn, which k3 doesn't search (its clock counts HP and the opponent's best damage, not effects like this).
- **Silvally** (B4 144): Gold Breaker: ExtraDamageIfEx estimated at printed damage: k3's damage estimate uses the printed damage.
- **Team Rocket's Scyther** (P-B 088): Second Strike: ExtraDamageIfHurt estimated at printed damage: k3's damage estimate uses the printed damage.

Engine commit 86e6154; goldfish seeds 22,200,000,000 + opponent x 10,000 + i (i < 50); card-draw model seed 22,100,000,000.
