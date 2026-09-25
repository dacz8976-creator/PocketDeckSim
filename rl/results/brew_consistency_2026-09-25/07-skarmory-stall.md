# Deck 07: Skarmory stall

List: `decks/dustin/07-skarmory-stall.txt`. Main attackers: Skarmory ex.
Ladder Log: 3-1.

**List check:** Indeedee ex's Psychic [PP] can't be paid with Metal Energy.

## What the cards allow (20,000 shuffles, no opponent)

The card-draw model plays solitaire: draws, plays its draw and search cards, puts Basics down, evolves, and gives each turn's energy to the Pokémon closest to attacking. It shows what the list can do, not what a player or bot will do.

| | going first | going second |
|---|---|---|
| Opening hand with one Basic | 86% | 86% |
| A main attacker could attack by your turn 2 | 0% | 92% |
| A main attacker could attack by your turn 3 | 95% | 95% |
| A main attacker could attack by your turn 4 | 97% | 97% |
| Stage 2 in play by your turn 3 | n/a | n/a |
| Stuck cards in hand, end of turns 1-4 | 1.5, 0.9, 0.5, 0.6 | 1.5, 0.9, 0.5, 0.6 |

When the opening hand has one Basic, it is: Skarmory ex (57% of all games), Indeedee ex (29% of all games).

**Chance each card has been in your hand by the end of your turn 1 / 2 / 3 / 4** (going second; going first is the same card count, a turn earlier in the game). "With search" plays the list's draw and search cards; "draws only" is the exact odds from drawing alone, ignoring the rule that the opening hand always has a Basic.

| card | with search | draws only |
|---|---|---|
| Skarmory ex | 92% / 95% / 97% / 98% | 52% / 59% / 65% / 71% |
| Cyrus | 57% / 67% / 75% / 82% | 52% / 59% / 65% / 71% |
| Indeedee ex | 67% / 75% / 81% / 86% | 30% / 35% / 40% / 45% |
| Jasmine | 57% / 67% / 75% / 82% | 52% / 59% / 65% / 71% |
| Lucky Ice Pop | 33% / 42% / 49% / 55% | 30% / 35% / 40% / 45% |
| Metal Core Barrier | 57% / 67% / 75% / 82% | 52% / 59% / 65% / 71% |
| Poké Ball | 57% / 66% / 73% / 80% | 52% / 59% / 65% / 71% |
| Pokémon Center Lady | 34% / 42% / 49% / 56% | 30% / 35% / 40% / 45% |
| Professor's Research | 49% / 57% / 64% / 71% | 52% / 59% / 65% / 71% |
| Sabrina | 33% / 41% / 48% / 55% | 30% / 35% / 40% / 45% |
| Starting Plains | 33% / 42% / 49% / 56% | 30% / 35% / 40% / 45% |

## What the bot does with it (k3 piloting, 400 games against each opponent bot)

k3 plays the list against the 8 table decks, 50 deals each, once against a bot that only ends its turn ('et': pure goldfish) and once against one that attaches and attacks ('aa': points given up before the list's first real attack). "Could" means a main attacker was in the Active Spot with an attack available; "did" means k3 used it.

**Bot numbers untrusted for this list**: some of its cards hit a path k3 prices badly (see the last section).

| | vs et, first | vs et, second | vs aa, first | vs aa, second |
|---|---|---|---|---|
| games | 194 | 206 | 194 | 206 |
| main attacker could / did attack by turn 2 | 0% / 0% | 73% / 73% | 0% / 0% | 71% / 71% |
| main attacker could / did attack by turn 3 | 71% / 71% | 94% / 94% | 71% / 71% | 92% / 92% |
| main attacker could / did attack by turn 4 | 95% / 95% | 96% / 96% | 95% / 95% | 95% / 95% |
| never attacked with a main attacker | 2% | 1% | 3% | 2% |
| points given up before the first main attack (average; share of games with any) | 0.00; 0% | 0.00; 0% | 0.04; 2% | 0.01; 0% |
| Stage 2 in play by turn 3 | 0% | 0% | 0% | 0% |
| dead cards at the end of turns 2-4 (average) | 2.2 | 1.9 | 1.7 | 1.4 |
| won (a sanity check, not a strength rating) | 98% | 99% | 97% | 99% |

Games that crashed (a card the engine can't play): 0.
Dead cards: cards in hand that no offered move could use when the list attacked or ended its turn (a Supporter held because one was already played that turn doesn't count).

## Where the bot is blind on this list

- **Jasmine** (A4 160): its effect pays off during the opponent's turn, which k3 doesn't search (its clock counts HP and the opponent's best damage, not effects like this).
- **Metal Core Barrier** (B2 148): its effect pays off during the opponent's turn, which k3 doesn't search (its clock counts HP and the opponent's best damage, not effects like this).
- **Skarmory ex** (A4 124): attack Steel Wing pays off during the opponent's turn, which k3 doesn't search (its clock counts HP and the opponent's best damage, not effects like this).

Engine commit 86e6154; goldfish seeds 22,200,000,000 + opponent x 10,000 + i (i < 50); card-draw model seed 22,100,000,000.
