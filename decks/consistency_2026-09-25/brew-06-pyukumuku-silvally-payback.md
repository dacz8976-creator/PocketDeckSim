# Consistency: brew-06-pyukumuku-silvally-payback

`decks/brews/brew-06-pyukumuku-silvally-payback.txt` · Energy: Psychic · main attacker: Silvally (Stage 1), Gold Breaker [CCC] 60 · combo: Pyukumuku + Silvally

Ladder record: 0-3

**In one line:** brew-06-pyukumuku-silvally-payback: one-Basic opening 41%; Silvally online by own T3 0% first / 72% second (T4 83%/83%); combo by T4 83%/84%; goldfish (scripted pilot v aa, seat-balanced): 1.44 pts conceded before the first 30+ damage attack (by own T3 in 15%), Silvally attacks by T4 35% with 1.56 conceded first, 2.8 dead cards/turn; unpriced-text cards (a): 1

Turns are the player's own turns (own turn 1 is your first turn whether you go first or second). Going first: no Energy on own turn 1, but you draw. Nobody evolves on their own turn 1. Solitaire figures come from 10,000 deals per seat (about ±1 point); the opening table is exact.

## 1. Opening hand

7 Basic Pokémon in 20 cards. The 5-card hand is dealt at random; only a hand with no Basic has one random card swapped for a random Basic, so extra Basics are not favoured. The opening is the same going first or second.

| Basics in the opening hand | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| exact | 41% | 39% | 18% | 3% | 0% |
| solitaire check | 40% | 40% | 18% | 3% | 0% |

**Exactly one Basic: 41%** (of which 8% are swap-in hands that had none).

| Only Basic in the hand is… | chance | | Card in the opening hand | chance |
|---|---|---|---|---|
| Pyukumuku | 12% | | Pyukumuku | 47% |
| Type: Null | 12% | | Type: Null | 47% |
| Team Rocket's Mewtwo | 12% | | Silvally | 44% |
| Comfey | 6% | |  |  |

## 2. Main attacker online

"Online" = Silvally in play (Active or Bench) with the Energy for Gold Breaker [CCC] attached, at the moment you would attack. Fastest possible without acceleration: own turn 4 going first, 3 going second.

| | going first T2 | T3 | T4 | going second T2 | T3 | T4 |
|---|---|---|---|---|---|---|
| Silvally online | 0% | 0% | 83% | 0% | 72% | 83% |
| Silvally in play (any Energy) | 66% | 80% | 88% | 67% | 80% | 88% |
| online, draw/search cards not played | 0% | 0% | 41% | 0% | 34% | 43% |

Where "in play" is well above "online", Energy is the limit (one a turn); where both are low, finding the cards is the limit. The last row shows what the list's draw and search cards add.

## 3. Stage 2 in play

No Stage 2 in the list.

## 4. Combo assembled

Pieces: Pyukumuku + Silvally. A Pokémon piece counts when it is in play; a Trainer piece when it is in hand or already played.

| by own turn | 2 | 3 | 4 | 5 |
|---|---|---|---|---|
| going first | 56% | 74% | 83% | 90% |
| going second | 56% | 74% | 84% | 91% |

Each piece on its own (going first / second):

| piece | by T3 | by T5 |
|---|---|---|
| Pyukumuku | 92% / 92% | 97% / 97% |
| Silvally | 80% / 80% | 93% / 93% |

### Drawing each card

Each card, drawn or fetched at least once by own turn 3 / by own turn 5 (the opening hand counts; going first, the list's draw and search cards played; "no draw" = the same deals with them left in hand):

| card | copies | by T3 | by T5 | by T3, no draw | by T5, no draw |
|---|---|---|---|---|---|
| Pyukumuku | 2 | 93% | 98% | 67% | 78% |
| Type: Null | 2 | 93% | 98% | 66% | 76% |
| Silvally | 2 | 92% | 97% | 65% | 76% |
| Team Rocket's Mewtwo | 2 | 94% | 99% | 68% | 78% |
| Comfey | 1 | 74% | 87% | 41% | 51% |
| Professor's Research | 2 | 78% | 88% | 64% | 77% |
| Poké Ball | 2 | 84% | 93% | 65% | 76% |
| Copycat | 2 | 77% | 89% | 65% | 76% |
| Gladion | 1 | 62% | 76% | 39% | 49% |
| Red | 1 | 63% | 78% | 39% | 50% |
| Cyrus | 1 | 62% | 78% | 39% | 50% |
| Rocky Helmet | 1 | 63% | 79% | 40% | 50% |
| Field Blower | 1 | 62% | 78% | 39% | 50% |

## 5. Goldfish against the engine

The real engine (rules4: rl/addon-0.7.2/deckgym and the pdl_rl_env 0.7.2 add-on built from the same rules) plays this list against `decks/research/weezing.txt` piloted by the engine's `aa` bot (attach-and-attack: it puts its Energy on the Active and attacks whenever it can, and nothing else). Because the engine lists End Turn first among the legal moves and `aa` takes the first move when it cannot attach or attack, `aa` never benches a Pokémon, not even at setup, and never plays a Trainer: the opponent is one Active Pokémon, and knocking it out wins. That makes it a fixed clock (here mostly Hoopa ex: 30 a turn from its first Energy, 100 from its third), not a real opponent.

Two pilots for this list. **sp** (scripted pilot, the main reading): the solitaire model's priorities playing the real engine through the add-on. It leads with a Basic whose Ability works from the Active Spot (Pyukumuku's Innards Out, Entei ex's Legendary Pulse), else one outside the main line with the most HP (`--lead` overrides); benches Basics, plays the draw, search, Rare Candy and Energy cards, evolves, puts Energy on the main line, attaches defensive Tools, heals a hurt Active, uses Abilities that draw, search, add Energy, damage the opposing Active (Crobat's Cunning Link) or give it a Special Condition (Meowstic's Perplexing Ears), plays a Supporter such as Team Rocket's Master Plan when the Active's attack gains from the Condition this turn, and attacks for the most damage. When a main or combo Pokémon is Active and the turn's Energy lets it attack this turn for as much as a Benched one could, the Energy goes on it. Otherwise, when a Benched main or combo Pokémon can attack and the Active cannot (or the Benched one does 40+ more and the Active is outside the main line), the turn's Energy goes on the Active until it can retreat, and it retreats. **aa** (the brief's pilot): the engine's own bot on this side too, so both sides have a single Pokémon and the game ends at the first knockout; its "points conceded" can never exceed what one knockout gives. `et` ends every turn at once and never attacks, so it is not used. 150 games per pilot; the coin decides who goes first, so the seats get different numbers of games; the "both seats" row is the plain mean of the two seat means.

"30+ attack" (the headline tempo reading) = the list's first attack that did 30 or more damage to the opposing Active or knocked it out (Poison or Burn the attack applied counts at the next Checkup; Poison or Burn that was already there does not). "Damaging attack" = the first attack that did any damage, chip damage included (Hatenna's Stampede for 10 counts). "Conceded" = the opponent's points at that moment (or at the end if it never came); ± is the standard error of the mean over these games: simulation noise only, nothing about the ladder. "Main attacks" = the first attack by the main attacker. "Dead" = cards in hand at the end of the turn that the rules did not let you play then (own turns 1-4; a second Supporter after one was played counts as dead; cards that need an opposing Bench, such as Cyrus and Sabrina, are left out because this opponent never has one).

| pilot | seat | games | won | 30+ attack by T3 | by T4 | never | conceded before it | damaging attack by T3 | never | conceded before it | main attacks by T3 | by T4 | never | conceded before main | dead cards / turn |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sp | first | 79 | 52% | 8% | 16% | 58% | 1.71 ± 0.15 | 8% | 58% | 1.71 ± 0.15 | 0% | 9% | 65% | 1.82 | 2.7 |
| sp | second | 71 | 82% | 23% | 69% | 23% | 1.17 ± 0.12 | 24% | 21% | 1.14 ± 0.11 | 14% | 61% | 31% | 1.30 | 2.9 |
| sp | **both seats** | 79 + 71 | - | 15% | 43% | 40% | 1.44 ± 0.09 | 16% | 40% | 1.42 ± 0.09 | 7% | 35% | 48% | 1.56 | 2.8 |
| aa | first | 74 | 18% | - | - | - | - | 47% | 51% | 0.51 ± 0.06 | - | - | - | - | 0.8 |
| aa | second | 76 | 9% | - | - | - | - | 49% | 51% | 0.51 ± 0.06 | - | - | - | - | 0.9 |
| aa | **both seats** | 74 + 76 | - | - | - | - | - | 48% | 51% | 0.51 ± 0.04 | - | - | - | - | 0.8 |

Who made the first damaging attack (sp, both seats, 150 games): Silvally 45%, (none) 41%, Type: Null 13%, Comfey 1%.

Who made the first 30+ attack (sp, both seats, 150 games): Silvally 48%, (none) 41%, Type: Null 9%, Comfey 1%.

Who led (Active at the start) (sp, both seats, 150 games): Pyukumuku 51%, Team Rocket's Mewtwo 23%, Type: Null 15%, Comfey 11%.

Games in which the scripted pilot retreated at least once: 9%.

Most often dead at end of turn (sp): Silvally 31%, Field Blower 21%, Team Rocket's Mewtwo 18%, Copycat 16% of turn-ends.

Most often dead at end of turn (aa): Silvally 40%, Field Blower 36% of turn-ends.

Engine game seeds (one per game): sp: 21,002,040,000 to 21,002,040,149, aa: 21,002,045,000 to 21,002,045,149. The won column is against a single Pokémon that never plays a Trainer and means little; read the tempo columns. The `aa` opponent also never plays a card, so its hand grows and Copycat draws more than it would on the ladder.

## 6. Coverage flag

Cards that hit known blind spots of the engine's bots, so the simulator's numbers for this list are less trustworthy where these cards matter:
- **(a)** text names the opponent's hand or deck: blind k3 leaves the move unpriced (engine/src/observation.rs `hidden_continuation_reason`).
- **(b)** attack effect outside the damage estimator: the bots value the attack at printed damage (engine/src/players/value_functions.rs `estimated_attack_damage_ex`, fallback `_ => fixed`; effect texts read from engine/src/actions/effect_mechanic_map.rs). "b-" = the effect does not change damage (status, self-damage), so only its side effect is unvalued.
- **(c)** played from hand: the opponent-reply search (the `o` tiers such as b3o3n4; k3 has no reply ply) only considers attacks, retreats, Abilities, draws and the turn's Energy (engine/src/players/expectiminimax_player.rs `is_public_information_action`).

| card | flags |
|---|---|
| Pyukumuku ×2 | **(c)** a copy benched from hand changes the board (passive Ability): not seen by the reply search |
| Silvally ×2 | **(b)** attack Gold Breaker: damage-changing effect, mechanic ExtraDamageIfEx has no damage estimator; the bots value it at printed 60<br>**(c)** evolves from hand: the opponent's reply search never sees the evolution |
| Team Rocket's Mewtwo ×2 | **(b-)** attack Psychic Explosion: effect not in the damage estimate (mechanic SelfDamage has no damage estimator); damage read as printed 130 |
| Comfey ×1 | **(c)** a copy benched from hand changes the board (passive Ability): not seen by the reply search |
| Copycat ×2 | **(a)** card names the opponent's hand or deck: blind k3 leaves it unpriced |
| Red ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Cyrus ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Rocky Helmet ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Field Blower ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |

**Reading:** k3 leaves Copycat unpriced; the damage of Silvally is read as printed. Bot numbers for this list are untrusted to that extent.

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
| Field Blower ×1 | Discard a Pokémon Tool card from a Pokémon (yours or your opponent's), or discard a Stadium card in play. | ignored: not a draw, search, evolution or Energy effect |

## How the solitaire pilot plays

Setup: all Basics in hand go into play (Active: the `--lead` Basic if given, else a Basic whose Ability works from the Active Spot, else one outside the main line with the most HP). Each own turn: draw; then repeat until nothing changes: play a Stadium that does something here, use it, play Items (Poké Ball and other searches take a random matching card, as printed; Rare Candy on the main line first), bench Basics the plan needs (others only while the Bench has room to spare), evolve (main line first), use draw Abilities, attach Tool pieces; when nothing else moves, one Supporter: a search that finds a missing piece, else a draw, else Copycat when the hand is small and holds nothing needed (Copycat assumes the opponent holds 4 cards). Then the turn's Energy (random among the declared types) goes to the main line first, then other combo attackers, else the Active; Energy from the discard or from Abilities is added; then the check; an Ability that ends the turn is used only when the main attacker cannot attack. No opponent, no knockouts, no retreat, no attacks (attack effects that set up, such as Flock or Glittering Gift, are ignored), no coin-flip Supporters. Hand limit 10.

Generated by `lib/consistency.py` in 19 s; solitaire seed 21,002,040,000 (Python random, same deals across variants).
