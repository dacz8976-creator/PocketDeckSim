# Consistency: brew-10-diancie-giratina

`decks/brews/brew-10-diancie-giratina.txt` · Energy: Psychic · main attacker: Mega Diancie ex (Basic), Brilliant Storm [CCC] 40 · combo: Mega Diancie ex + Giratina ex

Ladder record: -

**In one line:** brew-10-diancie-giratina: one-Basic opening 52%; Mega Diancie ex online by own T3 0% first / 78% second (T4 87%/87%); combo by T4 90%/89%; goldfish (scripted pilot v aa, seat-balanced): 0.48 pts conceded before the first 30+ damage attack (by own T3 in 38%), Mega Diancie ex attacks by T4 81% with 0.54 conceded first, 2.6 dead cards/turn; unpriced-text cards (a): 1

Turns are the player's own turns (own turn 1 is your first turn whether you go first or second). Going first: no Energy on own turn 1, but you draw. Nobody evolves on their own turn 1. Solitaire figures come from 10,000 deals per seat (about ±1 point); the opening table is exact.

## 1. Opening hand

6 Basic Pokémon in 20 cards. The 5-card hand is dealt at random; only a hand with no Basic has one random card swapped for a random Basic, so extra Basics are not favoured. The opening is the same going first or second.

| Basics in the opening hand | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| exact | 52% | 35% | 12% | 1% | 0% |
| solitaire check | 52% | 35% | 12% | 1% | 0% |

**Exactly one Basic: 52%** (of which 13% are swap-in hands that had none).

| Only Basic in the hand is… | chance | | Card in the opening hand | chance |
|---|---|---|---|---|
| Mega Diancie ex | 17% | | Mega Diancie ex | 49% |
| Giratina ex | 17% | | Giratina ex | 49% |
| Carbink | 17% | |  |  |

## 2. Main attacker online

"Online" = Mega Diancie ex in play (Active or Bench) with the Energy for Brilliant Storm [CCC] attached, at the moment you would attack. Fastest possible without acceleration: own turn 4 going first, 3 going second.

| | going first T2 | T3 | T4 | going second T2 | T3 | T4 |
|---|---|---|---|---|---|---|
| Mega Diancie ex online | 0% | 0% | 87% | 0% | 78% | 87% |
| Mega Diancie ex in play (any Energy) | 87% | 92% | 95% | 87% | 91% | 95% |
| online, draw/search cards not played | 0% | 0% | 63% | 0% | 56% | 63% |

Where "in play" is well above "online", Energy is the limit (one a turn); where both are low, finding the cards is the limit. The last row shows what the list's draw and search cards add.

## 3. Stage 2 in play

No Stage 2 in the list.

## 4. Combo assembled

Pieces: Mega Diancie ex + Giratina ex. A Pokémon piece counts when it is in play; a Trainer piece when it is in hand or already played.

| by own turn | 2 | 3 | 4 | 5 |
|---|---|---|---|---|
| going first | 76% | 84% | 90% | 94% |
| going second | 76% | 84% | 89% | 94% |

Each piece on its own (going first / second):

| piece | by T3 | by T5 |
|---|---|---|
| Mega Diancie ex | 92% / 91% | 97% / 97% |
| Giratina ex | 92% / 92% | 97% / 97% |

### Drawing each card

Each card, drawn or fetched at least once by own turn 3 / by own turn 5 (the opening hand counts; going first, the list's draw and search cards played; "no draw" = the same deals with them left in hand):

| card | copies | by T3 | by T5 | by T3, no draw | by T5, no draw |
|---|---|---|---|---|---|
| Mega Diancie ex | 2 | 92% | 97% | 68% | 78% |
| Giratina ex | 2 | 92% | 97% | 68% | 78% |
| Carbink | 2 | 92% | 97% | 69% | 79% |
| Professor's Research | 2 | 77% | 86% | 65% | 76% |
| Poké Ball | 2 | 81% | 90% | 65% | 76% |
| Copycat | 2 | 76% | 88% | 64% | 76% |
| Cyrus | 1 | 59% | 72% | 39% | 50% |
| Pokémon Center Lady | 1 | 59% | 72% | 40% | 50% |
| Giant Cape | 2 | 86% | 94% | 64% | 75% |
| Starting Plains | 1 | 59% | 72% | 39% | 49% |
| Peculiar Plaza | 1 | 60% | 73% | 39% | 49% |
| Lucky Ice Pop | 1 | 60% | 72% | 39% | 49% |
| Field Blower | 1 | 59% | 71% | 39% | 49% |

## 5. Goldfish against the engine

The real engine (rules4: rl/addon-0.7.2/deckgym and the pdl_rl_env 0.7.2 add-on built from the same rules) plays this list against `decks/research/weezing.txt` piloted by the engine's `aa` bot (attach-and-attack: it puts its Energy on the Active and attacks whenever it can, and nothing else). Because the engine lists End Turn first among the legal moves and `aa` takes the first move when it cannot attach or attack, `aa` never benches a Pokémon, not even at setup, and never plays a Trainer: the opponent is one Active Pokémon, and knocking it out wins. That makes it a fixed clock (here mostly Hoopa ex: 30 a turn from its first Energy, 100 from its third), not a real opponent.

Two pilots for this list. **sp** (scripted pilot, the main reading): the solitaire model's priorities playing the real engine through the add-on. It leads with a Basic whose Ability works from the Active Spot (Pyukumuku's Innards Out, Entei ex's Legendary Pulse), else one outside the main line with the most HP (`--lead` overrides); benches Basics, plays the draw, search, Rare Candy and Energy cards, evolves, puts Energy on the main line, attaches defensive Tools, heals a hurt Active, uses Abilities that draw, search, add Energy, damage the opposing Active (Crobat's Cunning Link) or give it a Special Condition (Meowstic's Perplexing Ears), plays a Supporter such as Team Rocket's Master Plan when the Active's attack gains from the Condition this turn, and attacks for the most damage. When a main or combo Pokémon is Active and the turn's Energy lets it attack this turn for as much as a Benched one could, the Energy goes on it. Otherwise, when a Benched main or combo Pokémon can attack and the Active cannot (or the Benched one does 40+ more and the Active is outside the main line), the turn's Energy goes on the Active until it can retreat, and it retreats. **aa** (the brief's pilot): the engine's own bot on this side too, so both sides have a single Pokémon and the game ends at the first knockout; its "points conceded" can never exceed what one knockout gives. `et` ends every turn at once and never attacks, so it is not used. 150 games per pilot; the coin decides who goes first, so the seats get different numbers of games; the "both seats" row is the plain mean of the two seat means.

"30+ attack" (the headline tempo reading) = the list's first attack that did 30 or more damage to the opposing Active or knocked it out (Poison or Burn the attack applied counts at the next Checkup; Poison or Burn that was already there does not). "Damaging attack" = the first attack that did any damage, chip damage included (Hatenna's Stampede for 10 counts). "Conceded" = the opponent's points at that moment (or at the end if it never came); ± is the standard error of the mean over these games: simulation noise only, nothing about the ladder. "Main attacks" = the first attack by the main attacker. "Dead" = cards in hand at the end of the turn that the rules did not let you play then (own turns 1-4; a second Supporter after one was played counts as dead; cards that need an opposing Bench, such as Cyrus and Sabrina, are left out because this opponent never has one).

| pilot | seat | games | won | 30+ attack by T3 | by T4 | never | conceded before it | damaging attack by T3 | never | conceded before it | main attacks by T3 | by T4 | never | conceded before main | dead cards / turn |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sp | first | 66 | 94% | 5% | 83% | 6% | 0.73 ± 0.12 | 5% | 6% | 0.73 ± 0.12 | 0% | 82% | 8% | 0.67 | 2.7 |
| sp | second | 84 | 99% | 71% | 100% | 0% | 0.23 ± 0.05 | 71% | 0% | 0.23 ± 0.05 | 63% | 81% | 15% | 0.40 | 2.5 |
| sp | **both seats** | 66 + 84 | - | 38% | 92% | 3% | 0.48 ± 0.07 | 38% | 3% | 0.48 ± 0.07 | 32% | 81% | 12% | 0.54 | 2.6 |
| aa | first | 79 | 13% | - | - | - | - | 0% | 67% | 1.04 ± 0.09 | - | - | - | - | 0.5 |
| aa | second | 71 | 38% | - | - | - | - | 18% | 62% | 1.03 ± 0.11 | - | - | - | - | 0.4 |
| aa | **both seats** | 79 + 71 | - | - | - | - | - | 9% | 65% | 1.03 ± 0.07 | - | - | - | - | 0.5 |

Who made the first damaging attack (sp, both seats, 150 games): Mega Diancie ex 85%, Giratina ex 13%, (none) 3%.

Who made the first 30+ attack (sp, both seats, 150 games): Mega Diancie ex 85%, Giratina ex 13%, (none) 3%.

Who led (Active at the start) (sp, both seats, 150 games): Giratina ex 50%, Carbink 33%, Mega Diancie ex 17%.

Games in which the scripted pilot retreated at least once: 65%.

Most often dead at end of turn (sp): Carbink 12%, Copycat 11%, Mega Diancie ex 9%, Pokémon Center Lady 9% of turn-ends.

Most often dead at end of turn (aa): Field Blower 30%, Lucky Ice Pop 10%, Pokémon Center Lady 7% of turn-ends.

Engine game seeds (one per game): sp: 21,002,090,000 to 21,002,090,149, aa: 21,002,095,000 to 21,002,095,149. The won column is against a single Pokémon that never plays a Trainer and means little; read the tempo columns. The `aa` opponent also never plays a card, so its hand grows and Copycat draws more than it would on the ladder.

## 6. Coverage flag

Cards that hit known blind spots of the engine's bots, so the simulator's numbers for this list are less trustworthy where these cards matter:
- **(a)** text names the opponent's hand or deck: blind k3 leaves the move unpriced (engine/src/observation.rs `hidden_continuation_reason`).
- **(b)** attack effect outside the damage estimator: the bots value the attack at printed damage (engine/src/players/value_functions.rs `estimated_attack_damage_ex`, fallback `_ => fixed`; effect texts read from engine/src/actions/effect_mechanic_map.rs). "b-" = the effect does not change damage (status, self-damage), so only its side effect is unvalued.
- **(c)** played from hand: the opponent-reply search (the `o` tiers such as b3o3n4; k3 has no reply ply) only considers attacks, retreats, Abilities, draws and the turn's Energy (engine/src/players/expectiminimax_player.rs `is_public_information_action`).

| card | flags |
|---|---|
| Giratina ex ×2 | **(b-)** attack Chaotic Impact: effect not in the damage estimate (mechanic SelfDamage has no damage estimator); damage read as printed 130 |
| Carbink ×2 | **(b-)** attack Glittering Gift: effect not in the damage estimate (mechanic AttachEnergyFromZoneToTwoBenched has no damage estimator); damage read as printed 0 |
| Copycat ×2 | **(a)** card names the opponent's hand or deck: blind k3 leaves it unpriced |
| Cyrus ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Pokémon Center Lady ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Giant Cape ×2 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Starting Plains ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Peculiar Plaza ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Lucky Ice Pop ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Field Blower ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |

**Reading:** k3 leaves Copycat unpriced. Bot numbers for this list are untrusted to that extent.

## Draw, search and Energy effects in this list

What the solitaire model plays (card text from lib/card.py):

| card | text | model |
|---|---|---|
| Giratina ex ×2 | Ability Broken-Space Bellow: Once during your turn, you may take a [P] Energy from your Energy Zone and attach it to this Pokémon. If you use this Ability, your turn ends. | ability modeled: extra 1 [P] to itself, ends the turn |
| Carbink ×2 | Glittering Gift: Choose 2 of your Benched Pokémon. For each of those Pokémon, take a [P] Energy from your Energy Zone and attach it to that Pokémon. | attack Glittering Gift ignored (attacks are not modeled as setup) |
| Professor's Research ×2 | Draw 2 cards. | modeled: draw 2 |
| Poké Ball ×2 | Put a random Basic Pokémon from your deck into your hand. | modeled: search 1 random Basic Pokémon to hand |
| Copycat ×2 | Shuffle your hand into your deck. Draw a card for each card in your opponent's hand. | modeled: shuffle hand in, draw opponent-hand-size |
| Cyrus ×1 | Switch in 1 of your opponent's Benched Pokémon that has damage on it to the Active Spot. | ignored: not a draw, search, evolution or Energy effect |
| Pokémon Center Lady ×1 | Heal 30 damage from 1 of your Pokémon, and it recovers from all Special Conditions. | ignored: not a draw, search, evolution or Energy effect |
| Giant Cape ×2 | The Pokémon this card is attached to gets +20 HP. | ignored: not a draw, search, evolution or Energy effect |
| Starting Plains ×1 | Each Basic Pokémon in play (both yours and your opponent's) gets +20 HP. | ignored: not a draw, search, evolution or Energy effect |
| Peculiar Plaza ×1 | The Retreat Cost of each [P] Pokémon in play (both yours and your opponent's) is 2 less. | ignored: not a draw, search, evolution or Energy effect |
| Lucky Ice Pop ×1 | Heal 20 damage from your Active Pokémon. If you healed any damage in this way, flip a coin. If heads, put this Lucky Ice Pop into your hand instead of the discard pile. | ignored: not a draw, search, evolution or Energy effect |
| Field Blower ×1 | Discard a Pokémon Tool card from a Pokémon (yours or your opponent's), or discard a Stadium card in play. | ignored: not a draw, search, evolution or Energy effect |

## How the solitaire pilot plays

Setup: all Basics in hand go into play (Active: the `--lead` Basic if given, else a Basic whose Ability works from the Active Spot, else one outside the main line with the most HP). Each own turn: draw; then repeat until nothing changes: play a Stadium that does something here, use it, play Items (Poké Ball and other searches take a random matching card, as printed; Rare Candy on the main line first), bench Basics the plan needs (others only while the Bench has room to spare), evolve (main line first), use draw Abilities, attach Tool pieces; when nothing else moves, one Supporter: a search that finds a missing piece, else a draw, else Copycat when the hand is small and holds nothing needed (Copycat assumes the opponent holds 4 cards). Then the turn's Energy (random among the declared types) goes to the main line first, then other combo attackers, else the Active; Energy from the discard or from Abilities is added; then the check; an Ability that ends the turn is used only when the main attacker cannot attack. No opponent, no knockouts, no retreat, no attacks (attack effects that set up, such as Flock or Glittering Gift, are ignored), no coin-flip Supporters. Hand limit 10.

Generated by `lib/consistency.py` in 22 s; solitaire seed 21,002,090,000 (Python random, same deals across variants).
