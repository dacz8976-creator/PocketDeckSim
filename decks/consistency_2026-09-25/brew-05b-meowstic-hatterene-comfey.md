# Consistency: brew-05b-meowstic-hatterene-comfey

`decks/brews/brew-05b-meowstic-hatterene-comfey.txt` · Energy: Psychic · main attacker: Hatterene (Stage 2), Mental Crush [PP] 70 · combo: Meowstic + Hatterene

Ladder record: 3-3

**In one line:** brew-05b-meowstic-hatterene-comfey: one-Basic opening 63%; Hatterene online by own T3 51% first / 50% second (T4 64%/63%); combo by T4 53%/52%; goldfish (scripted pilot v aa): damaging attack by own T3 79% with 0.4 pts conceded first, Hatterene attacks by T4 65% with 1.1 conceded first, 2.5 dead cards/turn; unpriced-text cards (a): 1

Turns are the player's own turns (own turn 1 is your first turn whether you go first or second). Going first: no Energy on own turn 1, but you draw. Nobody evolves on their own turn 1. Solitaire figures come from 10,000 deals per seat (about ±1 point); the opening table is exact.

## 1. Opening hand

5 Basic Pokémon in 20 cards. The 5-card hand is dealt at random; only a hand with no Basic has one random card swapped for a random Basic, so extra Basics are not favoured. The opening is the same going first or second.

| Basics in the opening hand | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| exact | 63% | 29% | 7% | 0% | 0% |
| solitaire check | 63% | 30% | 7% | 0% | 0% |

**Exactly one Basic: 63%** (of which 19% are swap-in hands that had none).

| Only Basic in the hand is… | chance | | Card in the opening hand | chance |
|---|---|---|---|---|
| Espurr | 25% | | Espurr | 52% |
| Hatenna | 25% | | Meowstic | 43% |
| Comfey | 13% | | Hatenna | 52% |
|  |  | | Hatterene | 43% |

## 2. Main attacker online

"Online" = Hatterene in play (Active or Bench) with the Energy for Mental Crush [PP] attached, at the moment you would attack. Fastest possible without acceleration: own turn 3 going first, 2 going second.

| | going first T2 | T3 | T4 | going second T2 | T3 | T4 |
|---|---|---|---|---|---|---|
| Hatterene online | 0% | 51% | 64% | 35% | 50% | 63% |
| Hatterene in play (any Energy) | 36% | 51% | 64% | 35% | 50% | 63% |
| online, draw/search cards not played | 0% | 24% | 32% | 17% | 24% | 32% |

Where "in play" is well above "online", Energy is the limit (one a turn); where both are low, finding the cards is the limit. The last row shows what the list's draw and search cards add.

## 3. Stage 2 in play

Stage 2 cards: Hatterene. Rare Candy in the list: yes.

| | going first T3 | T4 | going second T3 | T4 |
|---|---|---|---|---|
| any Stage 2 in play (list as built) | 51% | 64% | 50% | 63% |
| same deals, Rare Candy never played | 0% | 0% | 0% | 0% |

## 4. Combo assembled

Pieces: Meowstic + Hatterene. A Pokémon piece counts when it is in play; a Trainer piece when it is in hand or already played.

| by own turn | 2 | 3 | 4 | 5 |
|---|---|---|---|---|
| going first | 18% | 36% | 53% | 68% |
| going second | 17% | 36% | 52% | 67% |

Each piece on its own (going first / second):

| piece | by T3 | by T5 |
|---|---|---|
| Meowstic | 72% / 72% | 90% / 90% |
| Hatterene | 51% / 50% | 76% / 74% |

### Drawing each card

Each card, drawn or fetched at least once by own turn 3 / by own turn 5 (the opening hand counts; going first, the list's draw and search cards played; "no draw" = the same deals with them left in hand):

| card | copies | by T3 | by T5 | by T3, no draw | by T5, no draw |
|---|---|---|---|---|---|
| Espurr | 2 | 92% | 97% | 69% | 79% |
| Meowstic | 2 | 84% | 95% | 63% | 75% |
| Hatenna | 2 | 91% | 97% | 71% | 80% |
| Hatterene | 2 | 80% | 90% | 64% | 75% |
| Comfey | 1 | 76% | 91% | 43% | 52% |
| Rare Candy | 2 | 79% | 90% | 64% | 76% |
| Professor's Research | 2 | 72% | 86% | 64% | 76% |
| Copycat | 2 | 75% | 88% | 65% | 76% |
| Poké Ball | 2 | 79% | 92% | 65% | 75% |
| Team Rocket's Master Plan | 2 | 83% | 96% | 64% | 75% |
| Peculiar Plaza | 1 | 57% | 78% | 39% | 49% |

## 5. Goldfish against the engine

The real engine (rules4: rl/addon-0.7.2/deckgym and the pdl_rl_env 0.7.2 add-on built from the same rules) plays this list against `decks/research/weezing.txt` piloted by the engine's `aa` bot (attach-and-attack: it puts its Energy on the Active and attacks whenever it can, and nothing else). Because the engine lists End Turn first among the legal moves and `aa` takes the first move when it cannot attach or attack, `aa` never benches a Pokémon, not even at setup, and never plays a Trainer: the opponent is one Active Pokémon, and knocking it out wins. That makes it a fixed clock (here mostly Hoopa ex: 30 a turn from its first Energy, 100 from its third), not a real opponent.

Two pilots for this list. **sp** (scripted pilot, the main reading): the solitaire model's priorities playing the real engine through the add-on: benches Basics, plays the draw, search, Rare Candy and Energy cards, evolves, puts Energy on the main line, attaches defensive Tools, heals a hurt Active, retreats to a Pokémon that can attack, and attacks for the most damage. **aa** (the brief's pilot): the engine's own bot on this side too, so both sides have a single Pokémon and the game ends at the first knockout; its "points conceded" can never exceed what one knockout gives. `et` ends every turn at once and never attacks, so it is not used. 150 games per pilot; the coin decides who goes first.

"Damaging attack" = the list's first attack that damaged or knocked out the opposing Active (poison it applied counts). "Conceded" = the opponent's points at that moment (or at the end if it never came). "Main attacks" = the first attack by the main attacker. "Dead" = cards in hand at the end of the turn that the rules did not let you play then (own turns 1-4; a second Supporter after one was played counts as dead; cards that need an opposing Bench, such as Cyrus and Sabrina, are left out because this opponent never has one).

| pilot | seat | games | won | damaging attack by T2 | by T3 | by T4 | never | points conceded before it | conceded 2+ | main attacks by T3 | by T4 | never | conceded before main | dead cards / turn |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sp | first | 66 | 64% | 21% | 65% | 92% | 6% | 0.55 | 5% | 39% | 70% | 24% | 1.08 | 2.4 |
| sp | second | 84 | 67% | 51% | 89% | 98% | 0% | 0.26 | 0% | 48% | 62% | 32% | 1.12 | 2.5 |
| aa | first | 70 | 11% | 76% | 100% | 100% | 0% | 0.00 | 0% | - | - | - | - | 1.7 |
| aa | second | 80 | 8% | 100% | 100% | 100% | 0% | 0.00 | 0% | - | - | - | - | 1.6 |

Most often dead at end of turn (sp): Rare Candy 44%, Hatterene 38%, Meowstic 26%, Team Rocket's Master Plan 23% of turn-ends.

Most often dead at end of turn (aa): Rare Candy 52%, Hatterene 52%, Meowstic 44% of turn-ends.

Engine game seeds (one per game): sp: 21,002,010,000 to 21,002,010,149, aa: 21,002,015,000 to 21,002,015,149. The won column is against a single Pokémon that never plays a Trainer and means little; read the tempo columns. The `aa` opponent also never plays a card, so its hand grows and Copycat draws more than it would on the ladder.

## 6. Coverage flag

Cards that hit known blind spots of the engine's bots, so the simulator's numbers for this list are less trustworthy where these cards matter:
- **(a)** text names the opponent's hand or deck: blind k3 leaves the move unpriced (engine/src/observation.rs `hidden_continuation_reason`).
- **(b)** attack effect outside the damage estimator: the bots value the attack at printed damage (engine/src/players/value_functions.rs `estimated_attack_damage_ex`, fallback `_ => fixed`; effect texts read from engine/src/actions/effect_mechanic_map.rs). "b-" = the effect does not change damage (status, self-damage), so only its side effect is unvalued.
- **(c)** played from hand: the opponent-reply search (the `o` tiers such as b3o3n4; k3 has no reply ply) only considers attacks, retreats, Abilities, draws and the turn's Energy (engine/src/players/expectiminimax_player.rs `is_public_information_action`).

| card | flags |
|---|---|
| Meowstic ×2 | **(c)** evolves from hand: the opponent's reply search never sees the evolution |
| Hatterene ×2 | **(b)** attack Mental Crush: damage-changing effect, mechanic ExtraDamageIfDefenderStatus has no damage estimator; the bots value it at printed 70<br>**(c)** evolves from hand: the opponent's reply search never sees the evolution |
| Comfey ×1 | **(c)** a copy benched from hand changes the board (passive Ability): not seen by the reply search |
| Rare Candy ×2 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Copycat ×2 | **(a)** card names the opponent's hand or deck: blind k3 leaves it unpriced |
| Team Rocket's Master Plan ×2 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Peculiar Plaza ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |

**Reading:** k3 leaves Copycat unpriced; the damage of Hatterene is read as printed. Bot numbers for this list are untrusted to that extent.

## Draw, search and Energy effects in this list

What the solitaire model plays (card text from lib/card.py):

| card | text | model |
|---|---|---|
| Rare Candy ×2 | Choose 1 of your Basic Pokémon in play. If you have a Stage 2 card in your hand that evolves from that Pokémon, put that card onto the Basic Pokémon to evolve it, skipping the Stage 1. You can't use this card during your first turn or on a Basic Pokémon that was put into play this turn. | modeled: Basic straight to Stage 2 (not own turn 1, not a Basic played this turn) |
| Professor's Research ×2 | Draw 2 cards. | modeled: draw 2 |
| Copycat ×2 | Shuffle your hand into your deck. Draw a card for each card in your opponent's hand. | modeled: shuffle hand in, draw opponent-hand-size |
| Poké Ball ×2 | Put a random Basic Pokémon from your deck into your hand. | modeled: search 1 random Basic Pokémon to hand |
| Team Rocket's Master Plan ×2 | Your opponent's Active Pokémon is now Confused. Flip a coin. If tails, your Active Pokémon is now also Confused. | ignored: not a draw, search, evolution or Energy effect |
| Peculiar Plaza ×1 | The Retreat Cost of each [P] Pokémon in play (both yours and your opponent's) is 2 less. | ignored: not a draw, search, evolution or Energy effect |

## How the solitaire pilot plays

Setup: all Basics in hand go into play (Active: a Basic with an "if Active" draw Ability, else one outside the main line). Each own turn: draw; then repeat until nothing changes: play a Stadium that does something here, use it, play Items (Poké Ball and other searches take a random matching card, as printed; Rare Candy on the main line first), bench Basics the plan needs (others only while the Bench has room to spare), evolve (main line first), use draw Abilities, attach Tool pieces; when nothing else moves, one Supporter: a search that finds a missing piece, else a draw, else Copycat when the hand is small and holds nothing needed (Copycat assumes the opponent holds 4 cards). Then the turn's Energy (random among the declared types) goes to the main line first, then other combo attackers, else the Active; Energy from the discard or from Abilities is added; then the check; an Ability that ends the turn is used only when the main attacker cannot attack. No opponent, no knockouts, no retreat, no attacks (attack effects that set up, such as Flock or Glittering Gift, are ignored), no coin-flip Supporters. Hand limit 10.

Generated by `lib/consistency.py` in 43 s; solitaire seed 21,002,010,000 (Python random, same deals across variants).
