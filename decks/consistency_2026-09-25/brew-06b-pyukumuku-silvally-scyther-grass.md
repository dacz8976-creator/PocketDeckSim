# Consistency: brew-06b-pyukumuku-silvally-scyther-grass

`decks/brews/brew-06b-pyukumuku-silvally-scyther-grass.txt` · Energy: Grass · main attacker: Silvally (Stage 1), Gold Breaker [CCC] 60 · combo: Pyukumuku + Silvally

Ladder record: 0-3

**In one line:** brew-06b-pyukumuku-silvally-scyther-grass: one-Basic opening 41%; Silvally online by own T3 0% first / 72% second (T4 83%/83%); combo by T4 84%/83%; goldfish (scripted pilot v aa): damaging attack by own T3 14% with 1.5 pts conceded first, Silvally attacks by T4 38% with 1.6 conceded first, 2.4 dead cards/turn; unpriced-text cards (a): 1

Turns are the player's own turns (own turn 1 is your first turn whether you go first or second). Going first: no Energy on own turn 1, but you draw. Nobody evolves on their own turn 1. Solitaire figures come from 10,000 deals per seat (about ±1 point); the opening table is exact.

## 1. Opening hand

7 Basic Pokémon in 20 cards. The 5-card hand is dealt at random; only a hand with no Basic has one random card swapped for a random Basic, so extra Basics are not favoured. The opening is the same going first or second.

| Basics in the opening hand | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| exact | 41% | 39% | 18% | 3% | 0% |
| solitaire check | 40% | 39% | 17% | 3% | 0% |

**Exactly one Basic: 41%** (of which 8% are swap-in hands that had none).

| Only Basic in the hand is… | chance | | Card in the opening hand | chance |
|---|---|---|---|---|
| Pyukumuku | 12% | | Pyukumuku | 47% |
| Type: Null | 12% | | Type: Null | 47% |
| Team Rocket's Scyther | 12% | | Silvally | 44% |
| Teal Mask Ogerpon ex | 6% | |  |  |

## 2. Main attacker online

"Online" = Silvally in play (Active or Bench) with the Energy for Gold Breaker [CCC] attached, at the moment you would attack. Fastest possible without acceleration: own turn 4 going first, 3 going second.

| | going first T2 | T3 | T4 | going second T2 | T3 | T4 |
|---|---|---|---|---|---|---|
| Silvally online | 0% | 0% | 83% | 0% | 72% | 83% |
| Silvally in play (any Energy) | 67% | 80% | 88% | 66% | 80% | 88% |
| online, draw/search cards not played | 0% | 0% | 42% | 0% | 34% | 41% |

Where "in play" is well above "online", Energy is the limit (one a turn); where both are low, finding the cards is the limit. The last row shows what the list's draw and search cards add.

## 3. Stage 2 in play

No Stage 2 in the list.

## 4. Combo assembled

Pieces: Pyukumuku + Silvally. A Pokémon piece counts when it is in play; a Trainer piece when it is in hand or already played.

| by own turn | 2 | 3 | 4 | 5 |
|---|---|---|---|---|
| going first | 56% | 74% | 84% | 91% |
| going second | 56% | 74% | 83% | 90% |

Each piece on its own (going first / second):

| piece | by T3 | by T5 |
|---|---|---|
| Pyukumuku | 92% / 92% | 97% / 97% |
| Silvally | 80% / 80% | 93% / 93% |

### Drawing each card

Each card, drawn or fetched at least once by own turn 3 / by own turn 5 (the opening hand counts; going first, the list's draw and search cards played; "no draw" = the same deals with them left in hand):

| card | copies | by T3 | by T5 | by T3, no draw | by T5, no draw |
|---|---|---|---|---|---|
| Pyukumuku | 2 | 93% | 98% | 66% | 77% |
| Type: Null | 2 | 92% | 98% | 67% | 77% |
| Silvally | 2 | 92% | 98% | 65% | 76% |
| Team Rocket's Scyther | 2 | 94% | 99% | 68% | 78% |
| Teal Mask Ogerpon ex | 1 | 74% | 88% | 41% | 51% |
| Professor's Research | 2 | 78% | 88% | 65% | 76% |
| Poké Ball | 2 | 84% | 93% | 64% | 76% |
| Copycat | 2 | 76% | 89% | 64% | 76% |
| Gladion | 1 | 61% | 75% | 40% | 49% |
| Red | 1 | 62% | 78% | 39% | 49% |
| Cyrus | 1 | 62% | 78% | 40% | 50% |
| Rocky Helmet | 1 | 61% | 78% | 39% | 49% |
| Protective Poncho | 1 | 62% | 78% | 39% | 49% |

## 5. Goldfish against the engine

The real engine (rules4: rl/addon-0.7.2/deckgym and the pdl_rl_env 0.7.2 add-on built from the same rules) plays this list against `decks/research/weezing.txt` piloted by the engine's `aa` bot (attach-and-attack: it puts its Energy on the Active and attacks whenever it can, and nothing else). Because the engine lists End Turn first among the legal moves and `aa` takes the first move when it cannot attach or attack, `aa` never benches a Pokémon, not even at setup, and never plays a Trainer: the opponent is one Active Pokémon, and knocking it out wins. That makes it a fixed clock (here mostly Hoopa ex: 30 a turn from its first Energy, 100 from its third), not a real opponent.

Two pilots for this list. **sp** (scripted pilot, the main reading): the solitaire model's priorities playing the real engine through the add-on: benches Basics, plays the draw, search, Rare Candy and Energy cards, evolves, puts Energy on the main line, attaches defensive Tools, heals a hurt Active, retreats to a Pokémon that can attack, and attacks for the most damage. **aa** (the brief's pilot): the engine's own bot on this side too, so both sides have a single Pokémon and the game ends at the first knockout; its "points conceded" can never exceed what one knockout gives. `et` ends every turn at once and never attacks, so it is not used. 150 games per pilot; the coin decides who goes first.

"Damaging attack" = the list's first attack that damaged or knocked out the opposing Active (poison it applied counts). "Conceded" = the opponent's points at that moment (or at the end if it never came). "Main attacks" = the first attack by the main attacker. "Dead" = cards in hand at the end of the turn that the rules did not let you play then (own turns 1-4; a second Supporter after one was played counts as dead; cards that need an opposing Bench, such as Cyrus and Sabrina, are left out because this opponent never has one).

| pilot | seat | games | won | damaging attack by T2 | by T3 | by T4 | never | points conceded before it | conceded 2+ | main attacks by T3 | by T4 | never | conceded before main | dead cards / turn |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sp | first | 83 | 46% | 0% | 6% | 20% | 67% | 1.84 | 63% | 0% | 13% | 75% | 1.94 | 2.3 |
| sp | second | 67 | 85% | 24% | 24% | 78% | 21% | 1.12 | 43% | 15% | 69% | 28% | 1.19 | 2.6 |
| aa | first | 82 | 15% | 29% | 50% | 50% | 50% | 0.50 | 0% | - | - | - | - | 0.5 |
| aa | second | 68 | 37% | 51% | 51% | 51% | 49% | 0.49 | 0% | - | - | - | - | 0.5 |

Most often dead at end of turn (sp): Silvally 39%, Copycat 20%, Team Rocket's Scyther 19%, Red 18% of turn-ends.

Most often dead at end of turn (aa): Silvally 39% of turn-ends.

Engine game seeds (one per game): sp: 21,002,050,000 to 21,002,050,149, aa: 21,002,055,000 to 21,002,055,149. The won column is against a single Pokémon that never plays a Trainer and means little; read the tempo columns. The `aa` opponent also never plays a card, so its hand grows and Copycat draws more than it would on the ladder.

## 6. Coverage flag

Cards that hit known blind spots of the engine's bots, so the simulator's numbers for this list are less trustworthy where these cards matter:
- **(a)** text names the opponent's hand or deck: blind k3 leaves the move unpriced (engine/src/observation.rs `hidden_continuation_reason`).
- **(b)** attack effect outside the damage estimator: the bots value the attack at printed damage (engine/src/players/value_functions.rs `estimated_attack_damage_ex`, fallback `_ => fixed`; effect texts read from engine/src/actions/effect_mechanic_map.rs). "b-" = the effect does not change damage (status, self-damage), so only its side effect is unvalued.
- **(c)** played from hand: the opponent-reply search (the `o` tiers such as b3o3n4; k3 has no reply ply) only considers attacks, retreats, Abilities, draws and the turn's Energy (engine/src/players/expectiminimax_player.rs `is_public_information_action`).

| card | flags |
|---|---|
| Pyukumuku ×2 | **(c)** a copy benched from hand changes the board (passive Ability): not seen by the reply search |
| Silvally ×2 | **(b)** attack Gold Breaker: damage-changing effect, mechanic ExtraDamageIfEx has no damage estimator; the bots value it at printed 60<br>**(c)** evolves from hand: the opponent's reply search never sees the evolution |
| Team Rocket's Scyther ×2 | **(b)** attack Second Strike: damage-changing effect, mechanic ExtraDamageIfHurt has no damage estimator; the bots value it at printed 20 |
| Teal Mask Ogerpon ex ×1 | **(c)** a copy benched from hand changes the board (passive Ability): not seen by the reply search |
| Copycat ×2 | **(a)** card names the opponent's hand or deck: blind k3 leaves it unpriced |
| Red ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Cyrus ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Rocky Helmet ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Protective Poncho ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |

**Reading:** k3 leaves Copycat unpriced; the damage of Silvally, Team Rocket's Scyther is read as printed. Bot numbers for this list are untrusted to that extent.

## Draw, search and Energy effects in this list

What the solitaire model plays (card text from lib/card.py):

| card | text | model |
|---|---|---|
| Professor's Research ×2 | Draw 2 cards. | modeled: draw 2 |
| Poké Ball ×2 | Put a random Basic Pokémon from your deck into your hand. | modeled: search 1 random Basic Pokémon to hand |
| Copycat ×2 | Shuffle your hand into your deck. Draw a card for each card in your opponent's hand. | modeled: shuffle hand in, draw opponent-hand-size |
| Gladion ×1 | Put 1 random Type: Null or Silvally from your deck into your hand. | modeled: search 1 random Type: Null/Silvally to hand |
| Red ×1 | During this turn, attacks used by your Pokémon do +20 damage to your opponent's Active Pokémon ex. | ignored: not a draw, search, evolution or Energy effect |
| Cyrus ×1 | Switch in 1 of your opponent's Benched Pokémon that has damage on it to the Active Spot. | ignored: not a draw, search, evolution or Energy effect |
| Rocky Helmet ×1 | If the Pokémon this card is attached to is in the Active Spot and is damaged by an attack from your opponent's Pokémon, do 20 damage to the Attacking Pokémon. | ignored: not a draw, search, evolution or Energy effect |
| Protective Poncho ×1 | As long as the Pokémon this card is attached to is on your Bench, prevent all damage done to that Pokémon by your opponent's attacks and Abilities. | ignored: not a draw, search, evolution or Energy effect |

## How the solitaire pilot plays

Setup: all Basics in hand go into play (Active: a Basic with an "if Active" draw Ability, else one outside the main line). Each own turn: draw; then repeat until nothing changes: play a Stadium that does something here, use it, play Items (Poké Ball and other searches take a random matching card, as printed; Rare Candy on the main line first), bench Basics the plan needs (others only while the Bench has room to spare), evolve (main line first), use draw Abilities, attach Tool pieces; when nothing else moves, one Supporter: a search that finds a missing piece, else a draw, else Copycat when the hand is small and holds nothing needed (Copycat assumes the opponent holds 4 cards). Then the turn's Energy (random among the declared types) goes to the main line first, then other combo attackers, else the Active; Energy from the discard or from Abilities is added; then the check; an Ability that ends the turn is used only when the main attacker cannot attack. No opponent, no knockouts, no retreat, no attacks (attack effects that set up, such as Flock or Glittering Gift, are ignored), no coin-flip Supporters. Hand limit 10.

Generated by `lib/consistency.py` in 27 s; solitaire seed 21,002,050,000 (Python random, same deals across variants).
