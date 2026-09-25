# Consistency: research-lucario

`decks/research/lucario.txt` · Energy: Fighting · main attacker: Mega Lucario ex (Stage 1), Fighting Pulse [FF] 90 · combo: Mega Lucario ex + Lucario

Ladder record: Limitless ~50%

**In one line:** research-lucario: one-Basic opening 75%; Mega Lucario ex online by own T3 72% first / 73% second (T4 80%/81%); combo by T4 28%/27%; goldfish (scripted pilot v aa, seat-balanced): 0.24 pts conceded before the first 30+ damage attack (by own T3 in 83%), Mega Lucario ex attacks by T4 73% with 0.50 conceded first, 2.0 dead cards/turn; unpriced-text cards (a): 1

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
| Riolu | 38% | | Riolu | 59% |
| Bonsly | 19% | | Mega Lucario ex | 42% |
| Hitmonlee | 19% | | Lucario | 23% |

## 2. Main attacker online

"Online" = Mega Lucario ex in play (Active or Bench) with the Energy for Fighting Pulse [FF] attached, at the moment you would attack. Fastest possible without acceleration: own turn 3 going first, 2 going second.

| | going first T2 | T3 | T4 | going second T2 | T3 | T4 |
|---|---|---|---|---|---|---|
| Mega Lucario ex online | 0% | 72% | 80% | 60% | 73% | 81% |
| Mega Lucario ex in play (any Energy) | 61% | 72% | 80% | 61% | 73% | 81% |
| online, draw/search cards not played | 0% | 42% | 48% | 36% | 42% | 48% |

Where "in play" is well above "online", Energy is the limit (one a turn); where both are low, finding the cards is the limit. The last row shows what the list's draw and search cards add.

## 3. Stage 2 in play

No Stage 2 in the list.

## 4. Combo assembled

Pieces: Mega Lucario ex + Lucario. A Pokémon piece counts when it is in play; a Trainer piece when it is in hand or already played.

| by own turn | 2 | 3 | 4 | 5 |
|---|---|---|---|---|
| going first | 9% | 20% | 28% | 35% |
| going second | 9% | 20% | 27% | 35% |

Each piece on its own (going first / second):

| piece | by T3 | by T5 |
|---|---|---|
| Mega Lucario ex | 72% / 73% | 87% / 87% |
| Lucario | 32% / 32% | 43% / 43% |

### Drawing each card

Each card, drawn or fetched at least once by own turn 3 / by own turn 5 (the opening hand counts; going first, the list's draw and search cards played; "no draw" = the same deals with them left in hand):

| card | copies | by T3 | by T5 | by T3, no draw | by T5, no draw |
|---|---|---|---|---|---|
| Riolu | 2 | 93% | 98% | 74% | 82% |
| Mega Lucario ex | 2 | 84% | 93% | 63% | 75% |
| Lucario | 1 | 59% | 72% | 38% | 49% |
| Bonsly | 1 | 80% | 89% | 45% | 54% |
| Hitmonlee | 1 | 78% | 89% | 46% | 55% |
| Professor's Research | 2 | 75% | 85% | 64% | 76% |
| Copycat | 2 | 76% | 88% | 65% | 75% |
| Korrina | 1 | 58% | 73% | 38% | 48% |
| Pokémon Center Lady | 1 | 59% | 73% | 39% | 49% |
| Cyrus | 1 | 57% | 72% | 39% | 49% |
| Poké Ball | 2 | 79% | 89% | 63% | 75% |
| Field Blower | 1 | 59% | 72% | 38% | 48% |
| X Speed | 1 | 59% | 73% | 39% | 49% |
| Protective Poncho | 1 | 59% | 73% | 38% | 48% |
| Arena of Antiquity | 1 | 58% | 72% | 38% | 49% |

## 5. Goldfish against the engine

The real engine (rules4: rl/addon-0.7.2/deckgym and the pdl_rl_env 0.7.2 add-on built from the same rules) plays this list against `decks/research/weezing.txt` piloted by the engine's `aa` bot (attach-and-attack: it puts its Energy on the Active and attacks whenever it can, and nothing else). Because the engine lists End Turn first among the legal moves and `aa` takes the first move when it cannot attach or attack, `aa` never benches a Pokémon, not even at setup, and never plays a Trainer: the opponent is one Active Pokémon, and knocking it out wins. That makes it a fixed clock (here mostly Hoopa ex: 30 a turn from its first Energy, 100 from its third), not a real opponent.

Two pilots for this list. **sp** (scripted pilot, the main reading): the solitaire model's priorities playing the real engine through the add-on. It leads with a Basic whose Ability works from the Active Spot (Pyukumuku's Innards Out, Entei ex's Legendary Pulse), else one outside the main line with the most HP (`--lead` overrides); benches Basics, plays the draw, search, Rare Candy and Energy cards, evolves, puts Energy on the main line, attaches defensive Tools, heals a hurt Active, uses Abilities that draw, search, add Energy, damage the opposing Active (Crobat's Cunning Link) or give it a Special Condition (Meowstic's Perplexing Ears), plays a Supporter such as Team Rocket's Master Plan when the Active's attack gains from the Condition this turn, and attacks for the most damage. When a main or combo Pokémon is Active and the turn's Energy lets it attack this turn for as much as a Benched one could, the Energy goes on it. Otherwise, when a Benched main or combo Pokémon can attack and the Active cannot (or the Benched one does 40+ more and the Active is outside the main line), the turn's Energy goes on the Active until it can retreat, and it retreats. **aa** (the brief's pilot): the engine's own bot on this side too, so both sides have a single Pokémon and the game ends at the first knockout; its "points conceded" can never exceed what one knockout gives. `et` ends every turn at once and never attacks, so it is not used. 150 games per pilot; the coin decides who goes first, so the seats get different numbers of games; the "both seats" row is the plain mean of the two seat means.

"30+ attack" (the headline tempo reading) = the list's first attack that did 30 or more damage to the opposing Active or knocked it out (Poison or Burn the attack applied counts at the next Checkup; Poison or Burn that was already there does not). "Damaging attack" = the first attack that did any damage, chip damage included (Hatenna's Stampede for 10 counts). "Conceded" = the opponent's points at that moment (or at the end if it never came); ± is the standard error of the mean over these games: simulation noise only, nothing about the ladder. "Main attacks" = the first attack by the main attacker. "Dead" = cards in hand at the end of the turn that the rules did not let you play then (own turns 1-4; a second Supporter after one was played counts as dead; cards that need an opposing Bench, such as Cyrus and Sabrina, are left out because this opponent never has one).

| pilot | seat | games | won | 30+ attack by T3 | by T4 | never | conceded before it | damaging attack by T3 | never | conceded before it | main attacks by T3 | by T4 | never | conceded before main | dead cards / turn |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sp | first | 81 | 88% | 80% | 95% | 5% | 0.27 ± 0.06 | 84% | 2% | 0.17 ± 0.05 | 59% | 73% | 20% | 0.58 | 1.9 |
| sp | second | 69 | 91% | 86% | 91% | 4% | 0.20 ± 0.06 | 87% | 3% | 0.13 ± 0.05 | 64% | 72% | 22% | 0.42 | 2.1 |
| sp | **both seats** | 81 + 69 | - | 83% | 93% | 5% | 0.24 ± 0.04 | 85% | 3% | 0.15 ± 0.03 | 62% | 73% | 21% | 0.50 | 2.0 |
| aa | first | 79 | 24% | - | - | - | - | 75% | 25% | 0.25 ± 0.05 | - | - | - | - | 1.3 |
| aa | second | 71 | 24% | - | - | - | - | 70% | 30% | 0.30 ± 0.05 | - | - | - | - | 1.3 |
| aa | **both seats** | 79 + 71 | - | - | - | - | - | 73% | 27% | 0.27 ± 0.04 | - | - | - | - | 1.3 |

Who made the first damaging attack (sp, both seats, 150 games): Mega Lucario ex 43%, Bonsly 26%, Riolu 26%, (none) 3%, Lucario 3%.

Who made the first 30+ attack (sp, both seats, 150 games): Mega Lucario ex 55%, Riolu 27%, Bonsly 11%, (none) 5%, Lucario 3%.

Who led (Active at the start) (sp, both seats, 150 games): Riolu 47%, Hitmonlee 28%, Bonsly 25%.

Games in which the scripted pilot retreated at least once: 31%.

Most often dead at end of turn (sp): Field Blower 47%, Mega Lucario ex 36%, Copycat 26%, Lucario 25% of turn-ends.

Most often dead at end of turn (aa): Mega Lucario ex 46%, Field Blower 33%, Lucario 28%, Pokémon Center Lady 15% of turn-ends.

Engine game seeds (one per game): sp: 21,002,100,000 to 21,002,100,149, aa: 21,002,105,000 to 21,002,105,149. The won column is against a single Pokémon that never plays a Trainer and means little; read the tempo columns. The `aa` opponent also never plays a card, so its hand grows and Copycat draws more than it would on the ladder.

## 6. Coverage flag

Cards that hit known blind spots of the engine's bots, so the simulator's numbers for this list are less trustworthy where these cards matter:
- **(a)** text names the opponent's hand or deck: blind k3 leaves the move unpriced (engine/src/observation.rs `hidden_continuation_reason`).
- **(b)** attack effect outside the damage estimator: the bots value the attack at printed damage (engine/src/players/value_functions.rs `estimated_attack_damage_ex`, fallback `_ => fixed`; effect texts read from engine/src/actions/effect_mechanic_map.rs). "b-" = the effect does not change damage (status, self-damage), so only its side effect is unvalued.
- **(c)** played from hand: the opponent-reply search (the `o` tiers such as b3o3n4; k3 has no reply ply) only considers attacks, retreats, Abilities, draws and the turn's Energy (engine/src/players/expectiminimax_player.rs `is_public_information_action`).

| card | flags |
|---|---|
| Riolu ×2 | **(b)** attack Fighting Fist: damage-changing effect, mechanic ExtraDamageIfEx has no damage estimator; the bots value it at printed 10 |
| Mega Lucario ex ×2 | **(c)** evolves from hand: the opponent's reply search never sees the evolution |
| Lucario ×1 | **(c)** evolves from hand: the opponent's reply search never sees the evolution |
| Bonsly ×1 | **(b-)** attack Teary Attack: effect not in the damage estimate (mechanic DamageAndCardEffect has no damage estimator); damage read as printed 10 |
| Copycat ×2 | **(a)** card names the opponent's hand or deck: blind k3 leaves it unpriced |
| Korrina ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Pokémon Center Lady ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Cyrus ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Field Blower ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| X Speed ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Protective Poncho ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Arena of Antiquity ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |

**Reading:** k3 leaves Copycat unpriced; the damage of Riolu is read as printed. Bot numbers for this list are untrusted to that extent.

## Draw, search and Energy effects in this list

What the solitaire model plays (card text from lib/card.py):

| card | text | model |
|---|---|---|
| Professor's Research ×2 | Draw 2 cards. | modeled: draw 2 |
| Copycat ×2 | Shuffle your hand into your deck. Draw a card for each card in your opponent's hand. | modeled: shuffle hand in, draw opponent-hand-size |
| Korrina ×1 | During this turn, attacks used by your [F] Pokémon do +30 damage to your opponent's Active Pokémon ex. | ignored: not a draw, search, evolution or Energy effect |
| Pokémon Center Lady ×1 | Heal 30 damage from 1 of your Pokémon, and it recovers from all Special Conditions. | ignored: not a draw, search, evolution or Energy effect |
| Cyrus ×1 | Switch in 1 of your opponent's Benched Pokémon that has damage on it to the Active Spot. | ignored: not a draw, search, evolution or Energy effect |
| Poké Ball ×2 | Put a random Basic Pokémon from your deck into your hand. | modeled: search 1 random Basic Pokémon to hand |
| Field Blower ×1 | Discard a Pokémon Tool card from a Pokémon (yours or your opponent's), or discard a Stadium card in play. | ignored: not a draw, search, evolution or Energy effect |
| X Speed ×1 | During this turn, the Retreat Cost of your Active Pokémon is 1 less. | ignored: not a draw, search, evolution or Energy effect |
| Protective Poncho ×1 | As long as the Pokémon this card is attached to is on your Bench, prevent all damage done to that Pokémon by your opponent's attacks and Abilities. | ignored: not a draw, search, evolution or Energy effect |
| Arena of Antiquity ×1 | Attacks used by each [F] Pokémon in play (both yours and your opponent's) do +20 damage to the opponent's Active Pokémon ex. | ignored: not a draw, search, evolution or Energy effect |

## How the solitaire pilot plays

Setup: all Basics in hand go into play (Active: the `--lead` Basic if given, else a Basic whose Ability works from the Active Spot, else one outside the main line with the most HP). Each own turn: draw; then repeat until nothing changes: play a Stadium that does something here, use it, play Items (Poké Ball and other searches take a random matching card, as printed; Rare Candy on the main line first), bench Basics the plan needs (others only while the Bench has room to spare), evolve (main line first), use draw Abilities, attach Tool pieces; when nothing else moves, one Supporter: a search that finds a missing piece, else a draw, else Copycat when the hand is small and holds nothing needed (Copycat assumes the opponent holds 4 cards). Then the turn's Energy (random among the declared types) goes to the main line first, then other combo attackers, else the Active; Energy from the discard or from Abilities is added; then the check; an Ability that ends the turn is used only when the main attacker cannot attack. No opponent, no knockouts, no retreat, no attacks (attack effects that set up, such as Flock or Glittering Gift, are ignored), no coin-flip Supporters. Hand limit 10.

Generated by `lib/consistency.py` in 20 s; solitaire seed 21,002,100,000 (Python random, same deals across variants).
