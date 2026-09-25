# Brew 01: Arceus / Crobat / Xatu

List: `decks/brews/brew-01-arceus-crobat-xatu.txt`. Main attackers: Xatu, Arceus ex. Combo: Arceus ex, Crobat, Xatu in play by your turn 3.
Ladder Log: 1-3.
- "Never drew Crobat, or Xatu... Probably need more draw cards or Copycat."
- "Arceus ex takes 3 energy... Once again deck seems too difficult to draw cards you need."

**List check:** Crobat's Darkness Fang [D] can't be paid with Psychic Energy. Crobat (Stage 2) has no Golbat in the list: Rare Candy only.

## What the cards allow (20,000 shuffles, no opponent)

The card-draw model plays solitaire: draws, plays its draw and search cards, puts Basics down, evolves, and gives each turn's energy to the Pokémon closest to attacking. It shows what the list can do, not what a player or bot will do.

| | going first | going second |
|---|---|---|
| Opening hand with one Basic | 52% | 52% |
| A main attacker could attack by your turn 2 | 0% | 46% |
| A main attacker could attack by your turn 3 | 61% | 94% |
| A main attacker could attack by your turn 4 | 97% | 97% |
| Stage 2 in play by your turn 3 | 51% | 51% |
| Combo in play by your turn 3 | 24% | 24% |
| Stuck cards in hand, end of turns 1-4 | 2.9, 1.8, 1.6, 1.5 | 2.9, 1.8, 1.6, 1.5 |

When the opening hand has one Basic, it is: Arceus ex (17% of all games), Natu (17% of all games), Zubat (17% of all games).

**Chance each card has been in your hand by the end of your turn 1 / 2 / 3 / 4** (going second; going first is the same card count, a turn earlier in the game). "With search" plays the list's draw and search cards; "draws only" is the exact odds from drawing alone, ignoring the rule that the opening hand always has a Basic.

| card | with search | draws only |
|---|---|---|
| Arceus ex | 75% / 83% / 89% / 94% | 52% / 59% / 65% / 71% |
| Cyrus | 34% / 43% / 50% / 58% | 30% / 35% / 40% / 45% |
| Giant Cape | 36% / 44% / 51% / 59% | 30% / 35% / 40% / 45% |
| Natu | 80% / 90% / 95% / 97% | 52% / 59% / 65% / 71% |
| Poké Ball | 58% / 68% / 75% / 82% | 52% / 59% / 65% / 71% |
| Professor's Research | 51% / 59% / 66% / 73% | 52% / 59% / 65% / 71% |
| Rare Candy | 59% / 69% / 78% / 85% | 52% / 59% / 65% / 71% |
| Will | 36% / 44% / 51% / 59% | 30% / 35% / 40% / 45% |
| Zubat | 80% / 90% / 95% / 97% | 52% / 59% / 65% / 71% |

## What the bot does with it (k3 piloting, 400 games against each opponent bot)

k3 plays the list against the 8 table decks, 50 deals each, once against a bot that only ends its turn ('et': pure goldfish) and once against one that attaches and attacks ('aa': points given up before the list's first real attack). "Could" means a main attacker was in the Active Spot with an attack available; "did" means k3 used it.

**Bot numbers untrusted for this list**: some of its cards hit a path k3 prices badly (see the last section).

| | vs et, first | vs et, second | vs aa, first | vs aa, second |
|---|---|---|---|---|
| games | 193 | 207 | 193 | 207 |
| main attacker could / did attack by turn 2 | 0% / 0% | 14% / 14% | 0% / 0% | 11% / 11% |
| main attacker could / did attack by turn 3 | 18% / 18% | 63% / 63% | 11% / 11% | 60% / 60% |
| main attacker could / did attack by turn 4 | 55% / 55% | 67% / 67% | 39% / 39% | 66% / 66% |
| never attacked with a main attacker | 41% | 32% | 54% | 33% |
| points given up before the first main attack (average; share of games with any) | 0.00; 0% | 0.00; 0% | 0.46; 24% | 0.09; 8% |
| Stage 2 in play by turn 3 | 47% | 37% | 45% | 36% |
| dead cards at the end of turns 2-4 (average) | 2.5 | 2.3 | 2.5 | 2.3 |
| won (a sanity check, not a strength rating) | 97% | 98% | 88% | 96% |

Games that crashed (a card the engine can't play): 0.
Dead cards: cards in hand that no offered move could use when the list attacked or ended its turn (a Supporter held because one was already played that turn doesn't count).

## Where the bot is blind on this list

- **Xatu** (A4 082): Life Drain: CoinFlipSetOpponentActiveRemainingHp estimated at printed damage: k3's damage estimate uses the printed damage.

Engine commit 86e6154; goldfish seeds 22,200,000,000 + opponent x 10,000 + i (i < 50); card-draw model seed 22,100,000,000.
