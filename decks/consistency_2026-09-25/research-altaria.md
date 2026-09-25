# Consistency: research-altaria

`decks/research/altaria.txt` · Energy: Psychic · main attacker: Mega Altaria ex (Stage 1), Mega Harmony [PP] 40 · combo: Mega Altaria ex + Espeon

Ladder record: Limitless ~53%

**In one line:** research-altaria: one-Basic opening 41%; Mega Altaria ex online by own T3 51% first / 51% second (T4 61%/62%); combo by T4 49%/49%; goldfish (scripted pilot v aa, seat-balanced): 0.90 pts conceded before the first 30+ damage attack (by own T3 in 46%), Mega Altaria ex attacks by T4 41% with 1.17 conceded first, 2.2 dead cards/turn; unpriced-text cards (a): 1

Turns are the player's own turns (own turn 1 is your first turn whether you go first or second). Going first: no Energy on own turn 1, but you draw. Nobody evolves on their own turn 1. Solitaire figures come from 10,000 deals per seat (about ±1 point); the opening table is exact.

## 1. Opening hand

7 Basic Pokémon in 20 cards. The 5-card hand is dealt at random; only a hand with no Basic has one random card swapped for a random Basic, so extra Basics are not favoured. The opening is the same going first or second.

| Basics in the opening hand | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| exact | 41% | 39% | 18% | 3% | 0% |
| solitaire check | 41% | 38% | 18% | 3% | 0% |

**Exactly one Basic: 41%** (of which 8% are swap-in hands that had none).

| Only Basic in the hand is… | chance | | Card in the opening hand | chance |
|---|---|---|---|---|
| Swablu | 12% | | Swablu | 47% |
| Eevee | 12% | | Mega Altaria ex | 24% |
| Darkrai | 12% | | Eevee | 47% |
| Igglybuff | 6% | | Espeon | 44% |

## 2. Main attacker online

"Online" = Mega Altaria ex in play (Active or Bench) with the Energy for Mega Harmony [PP] attached, at the moment you would attack. Fastest possible without acceleration: own turn 3 going first, 2 going second.

| | going first T2 | T3 | T4 | going second T2 | T3 | T4 |
|---|---|---|---|---|---|---|
| Mega Altaria ex online | 0% | 51% | 61% | 38% | 51% | 62% |
| Mega Altaria ex in play (any Energy) | 38% | 51% | 61% | 38% | 51% | 62% |
| online, draw/search cards not played | 0% | 23% | 29% | 17% | 22% | 28% |

Where "in play" is well above "online", Energy is the limit (one a turn); where both are low, finding the cards is the limit. The last row shows what the list's draw and search cards add.

## 3. Stage 2 in play

No Stage 2 in the list.

## 4. Combo assembled

Pieces: Mega Altaria ex + Espeon. A Pokémon piece counts when it is in play; a Trainer piece when it is in hand or already played.

| by own turn | 2 | 3 | 4 | 5 |
|---|---|---|---|---|
| going first | 20% | 36% | 49% | 60% |
| going second | 20% | 36% | 49% | 61% |

Each piece on its own (going first / second):

| piece | by T3 | by T5 |
|---|---|---|
| Mega Altaria ex | 51% / 51% | 69% / 70% |
| Espeon | 70% / 70% | 86% / 86% |

### Drawing each card

Each card, drawn or fetched at least once by own turn 3 / by own turn 5 (the opening hand counts; going first, the list's draw and search cards played; "no draw" = the same deals with them left in hand):

| card | copies | by T3 | by T5 | by T3, no draw | by T5, no draw |
|---|---|---|---|---|---|
| Swablu | 2 | 90% | 96% | 67% | 77% |
| Mega Altaria ex | 1 | 61% | 75% | 40% | 51% |
| Eevee | 2 | 88% | 95% | 67% | 78% |
| Espeon | 2 | 86% | 94% | 65% | 76% |
| Darkrai | 2 | 93% | 98% | 66% | 77% |
| Igglybuff | 1 | 74% | 87% | 41% | 50% |
| Professor's Research | 2 | 76% | 87% | 65% | 76% |
| Copycat | 2 | 76% | 88% | 65% | 76% |
| Sabrina | 1 | 62% | 77% | 39% | 49% |
| Poké Ball | 2 | 83% | 92% | 65% | 76% |
| Field Blower | 1 | 62% | 77% | 40% | 50% |
| Small Balloon | 1 | 62% | 78% | 39% | 49% |
| Training Area | 1 | 62% | 77% | 39% | 49% |

## 5. Goldfish against the engine

The real engine (rules4: rl/addon-0.7.2/deckgym and the pdl_rl_env 0.7.2 add-on built from the same rules) plays this list against `decks/research/weezing.txt` piloted by the engine's `aa` bot (attach-and-attack: it puts its Energy on the Active and attacks whenever it can, and nothing else). Because the engine lists End Turn first among the legal moves and `aa` takes the first move when it cannot attach or attack, `aa` never benches a Pokémon, not even at setup, and never plays a Trainer: the opponent is one Active Pokémon, and knocking it out wins. That makes it a fixed clock (here mostly Hoopa ex: 30 a turn from its first Energy, 100 from its third), not a real opponent.

Two pilots for this list. **sp** (scripted pilot, the main reading): the solitaire model's priorities playing the real engine through the add-on. It leads with a Basic whose Ability works from the Active Spot (Pyukumuku's Innards Out, Entei ex's Legendary Pulse), else one outside the main line with the most HP (`--lead` overrides); benches Basics, plays the draw, search, Rare Candy and Energy cards, evolves, puts Energy on the main line, attaches defensive Tools, heals a hurt Active, uses Abilities that draw, search, add Energy, damage the opposing Active (Crobat's Cunning Link) or give it a Special Condition (Meowstic's Perplexing Ears), plays a Supporter such as Team Rocket's Master Plan when the Active's attack gains from the Condition this turn, and attacks for the most damage. When a main or combo Pokémon is Active and the turn's Energy lets it attack this turn for as much as a Benched one could, the Energy goes on it. Otherwise, when a Benched main or combo Pokémon can attack and the Active cannot (or the Benched one does 40+ more and the Active is outside the main line), the turn's Energy goes on the Active until it can retreat, and it retreats. **aa** (the brief's pilot): the engine's own bot on this side too, so both sides have a single Pokémon and the game ends at the first knockout; its "points conceded" can never exceed what one knockout gives. `et` ends every turn at once and never attacks, so it is not used. 150 games per pilot; the coin decides who goes first, so the seats get different numbers of games; the "both seats" row is the plain mean of the two seat means.

"30+ attack" (the headline tempo reading) = the list's first attack that did 30 or more damage to the opposing Active or knocked it out (Poison or Burn the attack applied counts at the next Checkup; Poison or Burn that was already there does not). "Damaging attack" = the first attack that did any damage, chip damage included (Hatenna's Stampede for 10 counts). "Conceded" = the opponent's points at that moment (or at the end if it never came); ± is the standard error of the mean over these games: simulation noise only, nothing about the ladder. "Main attacks" = the first attack by the main attacker. "Dead" = cards in hand at the end of the turn that the rules did not let you play then (own turns 1-4; a second Supporter after one was played counts as dead; cards that need an opposing Bench, such as Cyrus and Sabrina, are left out because this opponent never has one).

| pilot | seat | games | won | 30+ attack by T3 | by T4 | never | conceded before it | damaging attack by T3 | never | conceded before it | main attacks by T3 | by T4 | never | conceded before main | dead cards / turn |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sp | first | 69 | 75% | 32% | 64% | 17% | 1.06 ± 0.13 | 42% | 9% | 0.81 ± 0.11 | 14% | 43% | 42% | 1.32 | 2.1 |
| sp | second | 81 | 80% | 59% | 81% | 12% | 0.74 ± 0.11 | 69% | 4% | 0.44 ± 0.08 | 22% | 40% | 56% | 1.02 | 2.2 |
| sp | **both seats** | 69 + 81 | - | 46% | 73% | 15% | 0.90 ± 0.09 | 56% | 6% | 0.63 ± 0.07 | 18% | 41% | 49% | 1.17 | 2.2 |
| aa | first | 80 | 10% | - | - | - | - | 64% | 34% | 0.34 ± 0.05 | - | - | - | - | 1.0 |
| aa | second | 70 | 11% | - | - | - | - | 81% | 19% | 0.17 ± 0.05 | - | - | - | - | 1.0 |
| aa | **both seats** | 80 + 70 | - | - | - | - | - | 73% | 26% | 0.25 ± 0.03 | - | - | - | - | 1.0 |

Who made the first damaging attack (sp, both seats, 150 games): Mega Altaria ex 40%, Espeon 27%, Igglybuff 17%, Swablu 7%, (none) 6%, Eevee 4%.

Who made the first 30+ attack (sp, both seats, 150 games): Mega Altaria ex 46%, Espeon 29%, (none) 15%, Igglybuff 9%, Swablu 1%.

Who led (Active at the start) (sp, both seats, 150 games): Eevee 45%, Darkrai 29%, Swablu 17%, Igglybuff 9%.

Games in which the scripted pilot retreated at least once: 21%.

Most often dead at end of turn (sp): Field Blower 48%, Espeon 32%, Copycat 20%, Darkrai 18% of turn-ends.

Most often dead at end of turn (aa): Espeon 37%, Field Blower 28%, Mega Altaria ex 26% of turn-ends.

Engine game seeds (one per game): sp: 21,002,110,000 to 21,002,110,149, aa: 21,002,115,000 to 21,002,115,149. The won column is against a single Pokémon that never plays a Trainer and means little; read the tempo columns. The `aa` opponent also never plays a card, so its hand grows and Copycat draws more than it would on the ladder.

## 6. Coverage flag

Cards that hit known blind spots of the engine's bots, so the simulator's numbers for this list are less trustworthy where these cards matter:
- **(a)** text names the opponent's hand or deck: blind k3 leaves the move unpriced (engine/src/observation.rs `hidden_continuation_reason`).
- **(b)** attack effect outside the damage estimator: the bots value the attack at printed damage (engine/src/players/value_functions.rs `estimated_attack_damage_ex`, fallback `_ => fixed`; effect texts read from engine/src/actions/effect_mechanic_map.rs). "b-" = the effect does not change damage (status, self-damage), so only its side effect is unvalued.
- **(c)** played from hand: the opponent-reply search (the `o` tiers such as b3o3n4; k3 has no reply ply) only considers attacks, retreats, Abilities, draws and the turn's Energy (engine/src/players/expectiminimax_player.rs `is_public_information_action`).

| card | flags |
|---|---|
| Swablu ×2 | **(b-)** attack Sing: effect not in the damage estimate (mechanic InflictStatusConditions has no damage estimator); damage read as printed 0 |
| Mega Altaria ex ×1 | **(c)** evolves from hand: the opponent's reply search never sees the evolution |
| Eevee ×2 | **(c)** a copy benched from hand changes the board (passive Ability): not seen by the reply search |
| Espeon ×2 | **(b-)** attack Hypnoblast: effect not in the damage estimate (mechanic InflictStatusConditions has no damage estimator); damage read as printed 40<br>**(c)** evolves from hand: the opponent's reply search never sees the evolution |
| Darkrai ×2 | **(b-)** attack Dark Slumber: effect not in the damage estimate (mechanic InflictStatusConditions has no damage estimator); damage read as printed 40<br>**(c)** a copy benched from hand changes the board (passive Ability): not seen by the reply search |
| Igglybuff ×1 | **(b-)** attack Sleepy Lullaby: effect not in the damage estimate (mechanic InflictStatusConditions has no damage estimator); damage read as printed 10 |
| Copycat ×2 | **(a)** card names the opponent's hand or deck: blind k3 leaves it unpriced |
| Sabrina ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Field Blower ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Small Balloon ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Training Area ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |

**Reading:** k3 leaves Copycat unpriced. Bot numbers for this list are untrusted to that extent.

## Draw, search and Energy effects in this list

What the solitaire model plays (card text from lib/card.py):

| card | text | model |
|---|---|---|
| Eevee ×2 | Ability Boosted Evolution: As long as this Pokémon is in the Active Spot, it can evolve during your first turn or the turn you play it. | ability modeled: can evolve on its first turn (if Active) |
| Professor's Research ×2 | Draw 2 cards. | modeled: draw 2 |
| Copycat ×2 | Shuffle your hand into your deck. Draw a card for each card in your opponent's hand. | modeled: shuffle hand in, draw opponent-hand-size |
| Sabrina ×1 | Switch out your opponent's Active Pokémon to the Bench. (Your opponent chooses the new Active Pokémon.) | ignored: not a draw, search, evolution or Energy effect |
| Poké Ball ×2 | Put a random Basic Pokémon from your deck into your hand. | modeled: search 1 random Basic Pokémon to hand |
| Field Blower ×1 | Discard a Pokémon Tool card from a Pokémon (yours or your opponent's), or discard a Stadium card in play. | ignored: not a draw, search, evolution or Energy effect |
| Small Balloon ×1 | The Retreat Cost of the Basic Pokémon this card is attached to is 1 less. | ignored: not a draw, search, evolution or Energy effect |
| Training Area ×1 | Attacks used by Stage 1 Pokémon in play (both yours and your opponent's) do +10 damage to the opponent's Active Pokémon. | ignored: not a draw, search, evolution or Energy effect |

## How the solitaire pilot plays

Setup: all Basics in hand go into play (Active: the `--lead` Basic if given, else a Basic whose Ability works from the Active Spot, else one outside the main line with the most HP). Each own turn: draw; then repeat until nothing changes: play a Stadium that does something here, use it, play Items (Poké Ball and other searches take a random matching card, as printed; Rare Candy on the main line first), bench Basics the plan needs (others only while the Bench has room to spare), evolve (main line first), use draw Abilities, attach Tool pieces; when nothing else moves, one Supporter: a search that finds a missing piece, else a draw, else Copycat when the hand is small and holds nothing needed (Copycat assumes the opponent holds 4 cards). Then the turn's Energy (random among the declared types) goes to the main line first, then other combo attackers, else the Active; Energy from the discard or from Abilities is added; then the check; an Ability that ends the turn is used only when the main attacker cannot attack. No opponent, no knockouts, no retreat, no attacks (attack effects that set up, such as Flock or Glittering Gift, are ignored), no coin-flip Supporters. Hand limit 10.

Generated by `lib/consistency.py` in 23 s; solitaire seed 21,002,110,000 (Python random, same deals across variants).
