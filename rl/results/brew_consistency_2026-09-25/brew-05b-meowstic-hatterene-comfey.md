# Brew 05b: Meowstic / Hatterene / Comfey

List: `decks/brews/brew-05b-meowstic-hatterene-comfey.txt`. Main attackers: Hatterene. Combo: Meowstic, Hatterene in play by your turn 3.
Ladder Log: 3-3 (Sept 15 list).
- "Comfey the only Basic to start off, not ideal."
- "2 cards left to draw and I don't have the second Meowstic or Hatterene."
- "Good setup this time, Meowstic and Hatterene evolved on turn two."

**List check:** Hatterene (Stage 2) has no Hattrem in the list: Rare Candy only.

## What the cards allow (20,000 shuffles, no opponent)

The card-draw model plays solitaire: draws, plays its draw and search cards, puts Basics down, evolves, and gives each turn's energy to the Pokémon closest to attacking. It shows what the list can do, not what a player or bot will do.

| | going first | going second |
|---|---|---|
| Opening hand with one Basic | 64% | 64% |
| A main attacker could attack by your turn 2 | 0% | 31% |
| A main attacker could attack by your turn 3 | 50% | 50% |
| A main attacker could attack by your turn 4 | 67% | 67% |
| Stage 2 in play by your turn 3 | 50% | 50% |
| Combo in play by your turn 3 | 32% | 32% |
| Stuck cards in hand, end of turns 1-4 | 3.2, 2.1, 1.8, 1.7 | 3.2, 2.1, 1.8, 1.7 |

When the opening hand has one Basic, it is: Espurr (26% of all games), Hatenna (25% of all games), Comfey (12% of all games).

**Chance each card has been in your hand by the end of your turn 1 / 2 / 3 / 4** (going second; going first is the same card count, a turn earlier in the game). "With search" plays the list's draw and search cards; "draws only" is the exact odds from drawing alone, ignoring the rule that the opening hand always has a Basic.

| card | with search | draws only |
|---|---|---|
| Hatterene | 64% / 79% / 89% / 94% | 52% / 59% / 65% / 71% |
| Meowstic | 65% / 80% / 89% / 94% | 52% / 59% / 65% / 71% |
| Comfey | 56% / 71% / 81% / 88% | 30% / 35% / 40% / 45% |
| Copycat | 59% / 69% / 76% / 83% | 52% / 59% / 65% / 71% |
| Espurr | 83% / 92% / 96% / 98% | 52% / 59% / 65% / 71% |
| Hatenna | 83% / 93% / 97% / 98% | 52% / 59% / 65% / 71% |
| Peculiar Plaza | 39% / 53% / 65% / 74% | 30% / 35% / 40% / 45% |
| Poké Ball | 64% / 78% / 86% / 91% | 52% / 59% / 65% / 71% |
| Professor's Research | 62% / 72% / 79% / 84% | 52% / 59% / 65% / 71% |
| Rare Candy | 65% / 80% / 89% / 94% | 52% / 59% / 65% / 71% |
| Team Rocket's Master Plan | 64% / 79% / 88% / 94% | 52% / 59% / 65% / 71% |

## What the bot does with it (k3 piloting, 400 games against each opponent bot)

k3 plays the list against the 8 table decks, 50 deals each, once against a bot that only ends its turn ('et': pure goldfish) and once against one that attaches and attacks ('aa': points given up before the list's first real attack). "Could" means a main attacker was in the Active Spot with an attack available; "did" means k3 used it.

**Bot numbers untrusted for this list**: some of its cards hit a path k3 prices badly (see the last section).

| | vs et, first | vs et, second | vs aa, first | vs aa, second |
|---|---|---|---|---|
| games | 196 | 204 | 196 | 204 |
| main attacker could / did attack by turn 2 | 0% / 0% | 14% / 14% | 0% / 0% | 14% / 14% |
| main attacker could / did attack by turn 3 | 17% / 17% | 22% / 22% | 16% / 16% | 23% / 23% |
| main attacker could / did attack by turn 4 | 28% / 28% | 25% / 25% | 29% / 29% | 27% / 27% |
| never attacked with a main attacker | 69% | 71% | 66% | 71% |
| points given up before the first main attack (average; share of games with any) | 0.00; 0% | 0.00; 0% | 0.28; 21% | 0.23; 17% |
| Stage 2 in play by turn 3 | 49% | 39% | 47% | 38% |
| dead cards at the end of turns 2-4 (average) | 1.5 | 1.6 | 1.5 | 1.6 |
| won (a sanity check, not a strength rating) | 100% | 100% | 99% | 97% |

Games that crashed (a card the engine can't play): 0.
Dead cards: cards in hand that no offered move could use when the list attacked or ended its turn (a Supporter held because one was already played that turn doesn't count).

## Where the bot is blind on this list

- **Copycat** (B1 225): its effect mentions the opponent's hand or deck: k3 scores it as doing nothing.
- **Hatterene** (B3 071): Mental Crush: ExtraDamageIfDefenderStatus estimated at printed damage: k3's damage estimate uses the printed damage.

Engine commit 86e6154; goldfish seeds 22,200,000,000 + opponent x 10,000 + i (i < 50); card-draw model seed 22,100,000,000.
