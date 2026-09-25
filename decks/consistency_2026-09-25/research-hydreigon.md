# Consistency: research-hydreigon

`decks/research/hydreigon.txt` · Energy: Darkness · main attacker: Hydreigon (Stage 2), Hyper Ray [DDD] 130 · combo: Hydreigon + Mega Absol ex

**In one line:** research-hydreigon: one-Basic opening 75%; Hydreigon online by own T3 53% first / 53% second (T4 65%/66%); combo by T4 55%/56%; goldfish (scripted pilot v aa, seat-balanced): 0.65 pts conceded before the first 30+ damage attack (by own T3 in 53%), Hydreigon attacks by T4 56% with 0.68 conceded first, 1.8 dead cards/turn; unpriced-text cards (a): 2

Turns are the player's own turns (own turn 1 is your first turn whether you go first or second). Going first: no Energy on own turn 1, but you draw. Nobody evolves on their own turn 1. Solitaire figures come from 10,000 deals per seat (about ±1 point); the opening table is exact.

## 1. Opening hand

4 Basic Pokémon in 20 cards. The 5-card hand is dealt at random; only a hand with no Basic has one random card swapped for a random Basic, so extra Basics are not favoured. The opening is the same going first or second.

| Basics in the opening hand | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| exact | 75% | 22% | 3% | 0% | 0% |
| solitaire check | 75% | 22% | 3% | 0% | 0% |

**Exactly one Basic: 75%** (of which 28% are swap-in hands that had none).

| Only Basic in the hand is… | chance | | Card in the opening hand | chance |
|---|---|---|---|---|
| Deino | 38% | | Deino | 59% |
| Bombirdier | 19% | | Hydreigon | 42% |
| Mega Absol ex | 19% | | Mega Absol ex | 32% |

## 2. Main attacker online

"Online" = Hydreigon in play (Active or Bench) with the Energy for Hyper Ray [DDD] attached, at the moment you would attack. Fastest possible without acceleration: own turn 4 going first, 3 going second.

| | going first T2 | T3 | T4 | going second T2 | T3 | T4 |
|---|---|---|---|---|---|---|
| Hydreigon online | 39% | 53% | 65% | 39% | 53% | 66% |
| Hydreigon in play (any Energy) | 39% | 53% | 65% | 39% | 53% | 66% |
| online, draw/search cards not played | 19% | 25% | 34% | 18% | 26% | 33% |

Where "in play" is well above "online", Energy is the limit (one a turn); where both are low, finding the cards is the limit. The last row shows what the list's draw and search cards add.

## 3. Stage 2 in play

Stage 2 cards: Hydreigon. Rare Candy in the list: yes.

| | going first T3 | T4 | going second T3 | T4 |
|---|---|---|---|---|
| any Stage 2 in play (list as built) | 53% | 65% | 53% | 66% |
| same deals, Rare Candy never played | 0% | 0% | 0% | 0% |

## 4. Combo assembled

Pieces: Hydreigon + Mega Absol ex. A Pokémon piece counts when it is in play; a Trainer piece when it is in hand or already played.

| by own turn | 2 | 3 | 4 | 5 |
|---|---|---|---|---|
| going first | 28% | 42% | 55% | 68% |
| going second | 27% | 41% | 56% | 69% |

Each piece on its own (going first / second):

| piece | by T3 | by T5 |
|---|---|---|
| Hydreigon | 53% / 53% | 76% / 77% |
| Mega Absol ex | 79% / 78% | 90% / 90% |

### Drawing each card

Each card, drawn or fetched at least once by own turn 3 / by own turn 5 (the opening hand counts; going first, the list's draw and search cards played; "no draw" = the same deals with them left in hand):

| card | copies | by T3 | by T5 | by T3, no draw | by T5, no draw |
|---|---|---|---|---|---|
| Deino | 2 | 94% | 98% | 74% | 82% |
| Hydreigon | 2 | 79% | 90% | 63% | 75% |
| Bombirdier | 1 | 78% | 89% | 45% | 54% |
| Mega Absol ex | 1 | 79% | 90% | 45% | 55% |
| Professor's Research | 2 | 71% | 83% | 63% | 76% |
| Copycat | 2 | 75% | 88% | 63% | 75% |
| Cyrus | 1 | 57% | 74% | 39% | 49% |
| Sabrina | 1 | 57% | 74% | 39% | 50% |
| Poké Ball | 2 | 78% | 89% | 63% | 75% |
| Rare Candy | 2 | 79% | 89% | 64% | 75% |
| Lucky Ice Pop | 2 | 83% | 94% | 64% | 75% |
| Deceptive Needle | 2 | 83% | 94% | 64% | 75% |

## 5. Goldfish against the engine

The real engine (rules4: rl/addon-0.7.2/deckgym and the pdl_rl_env 0.7.2 add-on built from the same rules) plays this list against `decks/research/weezing.txt` piloted by the engine's `aa` bot (attach-and-attack: it puts its Energy on the Active and attacks whenever it can, and nothing else). Because the engine lists End Turn first among the legal moves and `aa` takes the first move when it cannot attach or attack, `aa` never benches a Pokémon, not even at setup, and never plays a Trainer: the opponent is one Active Pokémon, and knocking it out wins. That makes it a fixed clock (here mostly Hoopa ex: 30 a turn from its first Energy, 100 from its third), not a real opponent.

Two pilots for this list. **sp** (scripted pilot, the main reading): the solitaire model's priorities playing the real engine through the add-on. It leads with a Basic whose Ability works from the Active Spot (Pyukumuku's Innards Out, Entei ex's Legendary Pulse), else one outside the main line with the most HP (`--lead` overrides); benches Basics, plays the draw, search, Rare Candy and Energy cards, evolves, puts Energy on the main line, attaches defensive Tools, heals a hurt Active, uses Abilities that draw, search, add Energy, damage the opposing Active (Crobat's Cunning Link) or give it a Special Condition (Meowstic's Perplexing Ears), plays a Supporter such as Team Rocket's Master Plan when the Active's attack gains from the Condition this turn, and attacks for the most damage. When a main or combo Pokémon is Active and the turn's Energy lets it attack this turn for as much as a Benched one could, the Energy goes on it. Otherwise, when a Benched main or combo Pokémon can attack and the Active cannot (or the Benched one does 40+ more and the Active is outside the main line), the turn's Energy goes on the Active until it can retreat, and it retreats. **aa** (the brief's pilot): the engine's own bot on this side too, so both sides have a single Pokémon and the game ends at the first knockout; its "points conceded" can never exceed what one knockout gives. `et` ends every turn at once and never attacks, so it is not used. 150 games per pilot; the coin decides who goes first, so the seats get different numbers of games; the "both seats" row is the plain mean of the two seat means.

"30+ attack" (the headline tempo reading) = the list's first attack that did 30 or more damage to the opposing Active or knocked it out (Poison or Burn the attack applied counts at the next Checkup; Poison or Burn that was already there does not). "Damaging attack" = the first attack that did any damage, chip damage included (Hatenna's Stampede for 10 counts). "Conceded" = the opponent's points at that moment (or at the end if it never came); ± is the standard error of the mean over these games: simulation noise only, nothing about the ladder. "Main attacks" = the first attack by the main attacker. "Dead" = cards in hand at the end of the turn that the rules did not let you play then (own turns 1-4; a second Supporter after one was played counts as dead; cards that need an opposing Bench, such as Cyrus and Sabrina, are left out because this opponent never has one).

| pilot | seat | games | won | 30+ attack by T3 | by T4 | never | conceded before it | damaging attack by T3 | never | conceded before it | main attacks by T3 | by T4 | never | conceded before main | dead cards / turn |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sp | first | 71 | 86% | 51% | 75% | 11% | 0.54 ± 0.13 | 65% | 8% | 0.31 ± 0.10 | 42% | 62% | 27% | 0.59 | 1.8 |
| sp | second | 79 | 80% | 56% | 65% | 19% | 0.76 ± 0.15 | 70% | 10% | 0.34 ± 0.10 | 42% | 51% | 35% | 0.77 | 1.9 |
| sp | **both seats** | 71 + 79 | - | 53% | 70% | 15% | 0.65 ± 0.10 | 67% | 9% | 0.33 ± 0.07 | 42% | 56% | 31% | 0.68 | 1.8 |
| aa | first | 78 | 60% | - | - | - | - | 100% | 0% | 0.00 ± 0.00 | - | - | - | - | 1.4 |
| aa | second | 72 | 44% | - | - | - | - | 100% | 0% | 0.00 ± 0.00 | - | - | - | - | 1.3 |
| aa | **both seats** | 78 + 72 | - | - | - | - | - | 100% | 0% | 0.00 ± 0.00 | - | - | - | - | 1.3 |

Who made the first damaging attack (sp, both seats, 150 games): Hydreigon 47%, Deino 33%, (none) 9%, Mega Absol ex 6%, Bombirdier 4%.

Who made the first 30+ attack (sp, both seats, 150 games): Hydreigon 68%, (none) 15%, Mega Absol ex 8%, Deino 5%, Bombirdier 4%.

Who led (Active at the start) (sp, both seats, 150 games): Mega Absol ex 39%, Deino 37%, Bombirdier 24%.

Games in which the scripted pilot retreated at least once: 47%.

Most often dead at end of turn (sp): Hydreigon 48%, Rare Candy 44%, Lucky Ice Pop 25%, Copycat 19% of turn-ends.

Most often dead at end of turn (aa): Hydreigon 51%, Rare Candy 49%, Lucky Ice Pop 15% of turn-ends.

Engine game seeds (one per game): sp: 21,002,120,000 to 21,002,120,149, aa: 21,002,125,000 to 21,002,125,149. The won column is against a single Pokémon that never plays a Trainer and means little; read the tempo columns. The `aa` opponent also never plays a card, so its hand grows and Copycat draws more than it would on the ladder.

## 6. Coverage flag

Cards that hit known blind spots of the engine's bots, so the simulator's numbers for this list are less trustworthy where these cards matter:
- **(a)** text names the opponent's hand or deck: blind k3 leaves the move unpriced (engine/src/observation.rs `hidden_continuation_reason`).
- **(b)** attack effect outside the damage estimator: the bots value the attack at printed damage (engine/src/players/value_functions.rs `estimated_attack_damage_ex`, fallback `_ => fixed`; effect texts read from engine/src/actions/effect_mechanic_map.rs). "b-" = the effect does not change damage (status, self-damage), so only its side effect is unvalued.
- **(c)** played from hand: the opponent-reply search (the `o` tiers such as b3o3n4; k3 has no reply ply) only considers attacks, retreats, Abilities, draws and the turn's Energy (engine/src/players/expectiminimax_player.rs `is_public_information_action`).

| card | flags |
|---|---|
| Hydreigon ×2 | **(b-)** attack Hyper Ray: effect not in the damage estimate (mechanic SelfDiscardAllEnergy has no damage estimator); damage read as printed 130<br>**(c)** evolves from hand: the opponent's reply search never sees the evolution |
| Bombirdier ×1 | **(c)** a copy benched from hand changes the board (passive Ability): not seen by the reply search |
| Mega Absol ex ×1 | **(a)** attack Darkness Claw names the opponent's hand or deck: blind k3 leaves it unpriced<br>**(b-)** attack Darkness Claw: effect not in the damage estimate (mechanic DarknessClaw has no damage estimator); damage read as printed 80 |
| Copycat ×2 | **(a)** card names the opponent's hand or deck: blind k3 leaves it unpriced |
| Cyrus ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Sabrina ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Rare Candy ×2 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Lucky Ice Pop ×2 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Deceptive Needle ×2 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |

**Reading:** k3 leaves Mega Absol ex, Copycat unpriced. Bot numbers for this list are untrusted to that extent.

## Draw, search and Energy effects in this list

What the solitaire model plays (card text from lib/card.py):

| card | text | model |
|---|---|---|
| Hydreigon ×2 | Ability Roar in Unison: Once during your turn, you may take 2 [D] Energy from your Energy Zone and attach it to this Pokémon. If you do, do 30 damage to this Pokémon. | ability modeled: extra 2 [D] to itself |
| Professor's Research ×2 | Draw 2 cards. | modeled: draw 2 |
| Copycat ×2 | Shuffle your hand into your deck. Draw a card for each card in your opponent's hand. | modeled: shuffle hand in, draw opponent-hand-size |
| Cyrus ×1 | Switch in 1 of your opponent's Benched Pokémon that has damage on it to the Active Spot. | ignored: not a draw, search, evolution or Energy effect |
| Sabrina ×1 | Switch out your opponent's Active Pokémon to the Bench. (Your opponent chooses the new Active Pokémon.) | ignored: not a draw, search, evolution or Energy effect |
| Poké Ball ×2 | Put a random Basic Pokémon from your deck into your hand. | modeled: search 1 random Basic Pokémon to hand |
| Rare Candy ×2 | Choose 1 of your Basic Pokémon in play. If you have a Stage 2 card in your hand that evolves from that Pokémon, put that card onto the Basic Pokémon to evolve it, skipping the Stage 1. You can't use this card during your first turn or on a Basic Pokémon that was put into play this turn. | modeled: Basic straight to Stage 2 (not own turn 1, not a Basic played this turn) |
| Lucky Ice Pop ×2 | Heal 20 damage from your Active Pokémon. If you healed any damage in this way, flip a coin. If heads, put this Lucky Ice Pop into your hand instead of the discard pile. | ignored: not a draw, search, evolution or Energy effect |
| Deceptive Needle ×2 | At the end of your turn, if the [D] Pokémon this card is attached to is in the Active Spot, do 10 damage to your opponent's Active Pokémon. | ignored: not a draw, search, evolution or Energy effect |

## How the solitaire pilot plays

Setup: all Basics in hand go into play (Active: the `--lead` Basic if given, else a Basic whose Ability works from the Active Spot, else one outside the main line with the most HP). Each own turn: draw; then repeat until nothing changes: play a Stadium that does something here, use it, play Items (Poké Ball and other searches take a random matching card, as printed; Rare Candy on the main line first), bench Basics the plan needs (others only while the Bench has room to spare), evolve (main line first), use draw Abilities, attach Tool pieces; when nothing else moves, one Supporter: a search that finds a missing piece, else a draw, else Copycat when the hand is small and holds nothing needed (Copycat assumes the opponent holds 4 cards). Then the turn's Energy (random among the declared types) goes to the main line first, then other combo attackers, else the Active; Energy from the discard or from Abilities is added; then the check; an Ability that ends the turn is used only when the main attacker cannot attack. No opponent, no knockouts, no retreat, no attacks (attack effects that set up, such as Flock or Glittering Gift, are ignored), no coin-flip Supporters. Hand limit 10.

Generated by `lib/consistency.py` in 29 s; solitaire seed 21,002,120,000 (Python random, same deals across variants).
