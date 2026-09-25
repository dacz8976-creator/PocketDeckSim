# Consistency: research-blaziken

`decks/research/blaziken.txt` · Energy: Fire · main attacker: Mega Blaziken ex (Stage 2), Mega Burning [RR] 120 · combo: Mega Blaziken ex

**In one line:** research-blaziken: one-Basic opening 75%; Mega Blaziken ex online by own T3 53% first / 53% second (T4 66%/66%); combo by T4 66%/66%; goldfish (scripted pilot v aa, seat-balanced): 0.79 pts conceded before the first 30+ damage attack (by own T3 in 50%), Mega Blaziken ex attacks by T4 60% with 0.92 conceded first, 2.9 dead cards/turn; unpriced-text cards (a): 1

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
| Torchic | 38% | | Torchic | 59% |
| Heatmor | 19% | | Mega Blaziken ex | 42% |
| Castform Sunny Form | 19% | |  |  |

## 2. Main attacker online

"Online" = Mega Blaziken ex in play (Active or Bench) with the Energy for Mega Burning [RR] attached, at the moment you would attack. Fastest possible without acceleration: own turn 3 going first, 2 going second.

| | going first T2 | T3 | T4 | going second T2 | T3 | T4 |
|---|---|---|---|---|---|---|
| Mega Blaziken ex online | 0% | 53% | 66% | 39% | 53% | 66% |
| Mega Blaziken ex in play (any Energy) | 38% | 53% | 66% | 39% | 53% | 66% |
| online, draw/search cards not played | 0% | 26% | 33% | 18% | 26% | 33% |

Where "in play" is well above "online", Energy is the limit (one a turn); where both are low, finding the cards is the limit. The last row shows what the list's draw and search cards add.

## 3. Stage 2 in play

Stage 2 cards: Mega Blaziken ex. Rare Candy in the list: yes.

| | going first T3 | T4 | going second T3 | T4 |
|---|---|---|---|---|
| any Stage 2 in play (list as built) | 53% | 66% | 53% | 66% |
| same deals, Rare Candy never played | 0% | 0% | 0% | 0% |

## 4. Combo assembled

Pieces: Mega Blaziken ex. A Pokémon piece counts when it is in play; a Trainer piece when it is in hand or already played.

| by own turn | 2 | 3 | 4 | 5 |
|---|---|---|---|---|
| going first | 38% | 53% | 66% | 78% |
| going second | 39% | 53% | 66% | 77% |

### Drawing each card

Each card, drawn or fetched at least once by own turn 3 / by own turn 5 (the opening hand counts; going first, the list's draw and search cards played; "no draw" = the same deals with them left in hand):

| card | copies | by T3 | by T5 | by T3, no draw | by T5, no draw |
|---|---|---|---|---|---|
| Torchic | 2 | 94% | 98% | 75% | 83% |
| Mega Blaziken ex | 2 | 80% | 91% | 64% | 75% |
| Heatmor | 1 | 81% | 92% | 46% | 55% |
| Castform Sunny Form | 1 | 80% | 91% | 45% | 54% |
| Professor's Research | 2 | 73% | 86% | 63% | 75% |
| Copycat | 2 | 77% | 89% | 64% | 75% |
| Cyrus | 1 | 60% | 78% | 39% | 49% |
| Flame Patch | 2 | 85% | 96% | 63% | 75% |
| Rare Candy | 2 | 79% | 90% | 64% | 75% |
| Poké Ball | 2 | 80% | 91% | 63% | 75% |
| Field Blower | 1 | 59% | 78% | 39% | 49% |
| Rocky Helmet | 1 | 60% | 79% | 39% | 49% |
| Hiking Trail | 1 | 57% | 73% | 39% | 49% |

## 5. Goldfish against the engine

The real engine (rules4: rl/addon-0.7.2/deckgym and the pdl_rl_env 0.7.2 add-on built from the same rules) plays this list against `decks/research/weezing.txt` piloted by the engine's `aa` bot (attach-and-attack: it puts its Energy on the Active and attacks whenever it can, and nothing else). Because the engine lists End Turn first among the legal moves and `aa` takes the first move when it cannot attach or attack, `aa` never benches a Pokémon, not even at setup, and never plays a Trainer: the opponent is one Active Pokémon, and knocking it out wins. That makes it a fixed clock (here mostly Hoopa ex: 30 a turn from its first Energy, 100 from its third), not a real opponent.

Two pilots for this list. **sp** (scripted pilot, the main reading): the solitaire model's priorities playing the real engine through the add-on. It leads with a Basic whose Ability works from the Active Spot (Pyukumuku's Innards Out, Entei ex's Legendary Pulse), else one outside the main line with the most HP (`--lead` overrides); benches Basics, plays the draw, search, Rare Candy and Energy cards, evolves, puts Energy on the main line, attaches defensive Tools, heals a hurt Active, uses Abilities that draw, search, add Energy, damage the opposing Active (Crobat's Cunning Link) or give it a Special Condition (Meowstic's Perplexing Ears), plays a Supporter such as Team Rocket's Master Plan when the Active's attack gains from the Condition this turn, and attacks for the most damage. When a main or combo Pokémon is Active and the turn's Energy lets it attack this turn for as much as a Benched one could, the Energy goes on it. Otherwise, when a Benched main or combo Pokémon can attack and the Active cannot (or the Benched one does 40+ more and the Active is outside the main line), the turn's Energy goes on the Active until it can retreat, and it retreats. **aa** (the brief's pilot): the engine's own bot on this side too, so both sides have a single Pokémon and the game ends at the first knockout; its "points conceded" can never exceed what one knockout gives. `et` ends every turn at once and never attacks, so it is not used. 150 games per pilot; the coin decides who goes first, so the seats get different numbers of games; the "both seats" row is the plain mean of the two seat means.

"30+ attack" (the headline tempo reading) = the list's first attack that did 30 or more damage to the opposing Active or knocked it out (Poison or Burn the attack applied counts at the next Checkup; Poison or Burn that was already there does not). "Damaging attack" = the first attack that did any damage, chip damage included (Hatenna's Stampede for 10 counts). "Conceded" = the opponent's points at that moment (or at the end if it never came); ± is the standard error of the mean over these games: simulation noise only, nothing about the ladder. "Main attacks" = the first attack by the main attacker. "Dead" = cards in hand at the end of the turn that the rules did not let you play then (own turns 1-4; a second Supporter after one was played counts as dead; cards that need an opposing Bench, such as Cyrus and Sabrina, are left out because this opponent never has one).

| pilot | seat | games | won | 30+ attack by T3 | by T4 | never | conceded before it | damaging attack by T3 | never | conceded before it | main attacks by T3 | by T4 | never | conceded before main | dead cards / turn |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sp | first | 76 | 68% | 26% | 64% | 29% | 1.14 ± 0.13 | 41% | 7% | 0.50 ± 0.06 | 20% | 58% | 37% | 1.26 | 3.0 |
| sp | second | 74 | 85% | 74% | 82% | 11% | 0.43 ± 0.10 | 81% | 3% | 0.14 ± 0.04 | 55% | 62% | 34% | 0.58 | 2.8 |
| sp | **both seats** | 76 + 74 | - | 50% | 73% | 20% | 0.79 ± 0.08 | 61% | 5% | 0.32 ± 0.04 | 38% | 60% | 35% | 0.92 | 2.9 |
| aa | first | 74 | 19% | - | - | - | - | 78% | 22% | 0.22 ± 0.05 | - | - | - | - | 2.0 |
| aa | second | 76 | 20% | - | - | - | - | 79% | 21% | 0.21 ± 0.05 | - | - | - | - | 2.1 |
| aa | **both seats** | 74 + 76 | - | - | - | - | - | 79% | 21% | 0.21 ± 0.03 | - | - | - | - | 2.1 |

Who made the first damaging attack (sp, both seats, 150 games): Mega Blaziken ex 48%, Torchic 39%, Castform Sunny Form 7%, (none) 5%, Heatmor 2%.

Who made the first 30+ attack (sp, both seats, 150 games): Mega Blaziken ex 63%, (none) 20%, Castform Sunny Form 9%, Torchic 5%, Heatmor 2%.

Who led (Active at the start) (sp, both seats, 150 games): Torchic 37%, Castform Sunny Form 32%, Heatmor 31%.

Games in which the scripted pilot retreated at least once: 21%.

Most often dead at end of turn (sp): Flame Patch 48%, Mega Blaziken ex 40%, Rare Candy 40%, Copycat 16% of turn-ends.

Most often dead at end of turn (aa): Rare Candy 54%, Flame Patch 53%, Mega Blaziken ex 46%, Field Blower 31% of turn-ends.

Engine game seeds (one per game): sp: 21,002,140,000 to 21,002,140,149, aa: 21,002,145,000 to 21,002,145,149. The won column is against a single Pokémon that never plays a Trainer and means little; read the tempo columns. The `aa` opponent also never plays a card, so its hand grows and Copycat draws more than it would on the ladder.

## 6. Coverage flag

Cards that hit known blind spots of the engine's bots, so the simulator's numbers for this list are less trustworthy where these cards matter:
- **(a)** text names the opponent's hand or deck: blind k3 leaves the move unpriced (engine/src/observation.rs `hidden_continuation_reason`).
- **(b)** attack effect outside the damage estimator: the bots value the attack at printed damage (engine/src/players/value_functions.rs `estimated_attack_damage_ex`, fallback `_ => fixed`; effect texts read from engine/src/actions/effect_mechanic_map.rs). "b-" = the effect does not change damage (status, self-damage), so only its side effect is unvalued.
- **(c)** played from hand: the opponent-reply search (the `o` tiers such as b3o3n4; k3 has no reply ply) only considers attacks, retreats, Abilities, draws and the turn's Energy (engine/src/players/expectiminimax_player.rs `is_public_information_action`).

| card | flags |
|---|---|
| Mega Blaziken ex ×2 | **(b-)** attack Mega Burning: effect not in the damage estimate (mechanic SelfDiscardEnergyAndInflictStatus has no damage estimator); damage read as printed 120<br>**(c)** evolves from hand: the opponent's reply search never sees the evolution |
| Castform Sunny Form ×1 | **(b-)** attack Sunny Scorching: effect not in the damage estimate (mechanic InflictStatusIfStadiumInPlay has no damage estimator); damage read as printed 30 |
| Copycat ×2 | **(a)** card names the opponent's hand or deck: blind k3 leaves it unpriced |
| Cyrus ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Flame Patch ×2 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Rare Candy ×2 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Field Blower ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Rocky Helmet ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |

**Reading:** k3 leaves Copycat unpriced. Bot numbers for this list are untrusted to that extent.

## Draw, search and Energy effects in this list

What the solitaire model plays (card text from lib/card.py):

| card | text | model |
|---|---|---|
| Professor's Research ×2 | Draw 2 cards. | modeled: draw 2 |
| Copycat ×2 | Shuffle your hand into your deck. Draw a card for each card in your opponent's hand. | modeled: shuffle hand in, draw opponent-hand-size |
| Cyrus ×1 | Switch in 1 of your opponent's Benched Pokémon that has damage on it to the Active Spot. | ignored: not a draw, search, evolution or Energy effect |
| Flame Patch ×2 | Attach a [R] Energy from your discard pile to your Active [R] Pokémon. | modeled: attach 1 [R] from discard to the Active |
| Rare Candy ×2 | Choose 1 of your Basic Pokémon in play. If you have a Stage 2 card in your hand that evolves from that Pokémon, put that card onto the Basic Pokémon to evolve it, skipping the Stage 1. You can't use this card during your first turn or on a Basic Pokémon that was put into play this turn. | modeled: Basic straight to Stage 2 (not own turn 1, not a Basic played this turn) |
| Poké Ball ×2 | Put a random Basic Pokémon from your deck into your hand. | modeled: search 1 random Basic Pokémon to hand |
| Field Blower ×1 | Discard a Pokémon Tool card from a Pokémon (yours or your opponent's), or discard a Stadium card in play. | ignored: not a draw, search, evolution or Energy effect |
| Rocky Helmet ×1 | If the Pokémon this card is attached to is in the Active Spot and is damaged by an attack from your opponent's Pokémon, do 20 damage to the Attacking Pokémon. | ignored: not a draw, search, evolution or Energy effect |
| Hiking Trail ×1 | At the end of each player's turn, that player draws cards until they have 3 cards in their hand. | modeled: end of turn: draw up to 3 |

## How the solitaire pilot plays

Setup: all Basics in hand go into play (Active: the `--lead` Basic if given, else a Basic whose Ability works from the Active Spot, else one outside the main line with the most HP). Each own turn: draw; then repeat until nothing changes: play a Stadium that does something here, use it, play Items (Poké Ball and other searches take a random matching card, as printed; Rare Candy on the main line first), bench Basics the plan needs (others only while the Bench has room to spare), evolve (main line first), use draw Abilities, attach Tool pieces; when nothing else moves, one Supporter: a search that finds a missing piece, else a draw, else Copycat when the hand is small and holds nothing needed (Copycat assumes the opponent holds 4 cards). Then the turn's Energy (random among the declared types) goes to the main line first, then other combo attackers, else the Active; Energy from the discard or from Abilities is added; then the check; an Ability that ends the turn is used only when the main attacker cannot attack. No opponent, no knockouts, no retreat, no attacks (attack effects that set up, such as Flock or Glittering Gift, are ignored), no coin-flip Supporters. Hand limit 10.

Generated by `lib/consistency.py` in 25 s; solitaire seed 21,002,140,000 (Python random, same deals across variants).
