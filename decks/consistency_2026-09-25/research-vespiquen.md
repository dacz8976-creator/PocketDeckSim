# Consistency: research-vespiquen

`decks/research/vespiquen.txt` · Energy: Grass · main attacker: Vespiquen ex (Stage 1), Chase Order [GG] 70 · combo: Vespiquen ex + Shuckle ex

**In one line:** research-vespiquen: one-Basic opening 63%; Vespiquen ex online by own T3 75% first / 75% second (T4 84%/84%); combo by T4 82%/82%; goldfish (scripted pilot v aa): damaging attack by own T3 37% with 0.4 pts conceded first, Vespiquen ex attacks by T4 57% with 0.5 conceded first, 1.7 dead cards/turn; unpriced-text cards (a): 1

Turns are the player's own turns (own turn 1 is your first turn whether you go first or second). Going first: no Energy on own turn 1, but you draw. Nobody evolves on their own turn 1. Solitaire figures come from 10,000 deals per seat (about ±1 point); the opening table is exact.

## 1. Opening hand

5 Basic Pokémon in 20 cards. The 5-card hand is dealt at random; only a hand with no Basic has one random card swapped for a random Basic, so extra Basics are not favoured. The opening is the same going first or second.

| Basics in the opening hand | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| exact | 63% | 29% | 7% | 0% | 0% |
| solitaire check | 64% | 29% | 7% | 0% | 0% |

**Exactly one Basic: 63%** (of which 19% are swap-in hands that had none).

| Only Basic in the hand is… | chance | | Card in the opening hand | chance |
|---|---|---|---|---|
| Combee | 25% | | Combee | 52% |
| Shuckle ex | 25% | | Vespiquen ex | 43% |
| Teal Mask Ogerpon ex | 13% | | Shuckle ex | 52% |

## 2. Main attacker online

"Online" = Vespiquen ex in play (Active or Bench) with the Energy for Chase Order [GG] attached, at the moment you would attack. Fastest possible without acceleration: own turn 3 going first, 2 going second.

| | going first T2 | T3 | T4 | going second T2 | T3 | T4 |
|---|---|---|---|---|---|---|
| Vespiquen ex online | 0% | 75% | 84% | 59% | 75% | 84% |
| Vespiquen ex in play (any Energy) | 58% | 75% | 84% | 59% | 75% | 84% |
| online, draw/search cards not played | 0% | 41% | 48% | 33% | 41% | 48% |

Where "in play" is well above "online", Energy is the limit (one a turn); where both are low, finding the cards is the limit. The last row shows what the list's draw and search cards add.

## 3. Stage 2 in play

No Stage 2 in the list.

## 4. Combo assembled

Pieces: Vespiquen ex + Shuckle ex. A Pokémon piece counts when it is in play; a Trainer piece when it is in hand or already played.

| by own turn | 2 | 3 | 4 | 5 |
|---|---|---|---|---|
| going first | 53% | 72% | 82% | 90% |
| going second | 54% | 72% | 82% | 90% |

Each piece on its own (going first / second):

| piece | by T3 | by T5 |
|---|---|---|
| Vespiquen ex | 75% / 75% | 90% / 91% |
| Shuckle ex | 97% / 96% | 99% / 99% |

### Drawing each card

Each card, drawn or fetched at least once by own turn 3 / by own turn 5 (the opening hand counts; going first, the list's draw and search cards played; "no draw" = the same deals with them left in hand):

| card | copies | by T3 | by T5 | by T3, no draw | by T5, no draw |
|---|---|---|---|---|---|
| Combee | 2 | 95% | 99% | 70% | 80% |
| Vespiquen ex | 2 | 83% | 93% | 64% | 75% |
| Shuckle ex | 2 | 97% | 99% | 70% | 79% |
| Teal Mask Ogerpon ex | 1 | 88% | 96% | 44% | 53% |
| Professor's Research | 2 | 75% | 85% | 65% | 77% |
| Copycat | 2 | 77% | 90% | 64% | 76% |
| Cyrus | 1 | 59% | 74% | 39% | 49% |
| Sabrina | 1 | 59% | 74% | 40% | 50% |
| X Speed | 2 | 84% | 94% | 64% | 75% |
| Field Blower | 1 | 59% | 74% | 39% | 49% |
| Leaf Cape | 2 | 85% | 94% | 64% | 76% |
| Fragrant Forest | 2 | 81% | 90% | 65% | 76% |

## 5. Goldfish against the engine

The real engine (rules4: rl/addon-0.7.2/deckgym and the pdl_rl_env 0.7.2 add-on built from the same rules) plays this list against `decks/research/weezing.txt` piloted by the engine's `aa` bot (attach-and-attack: it puts its Energy on the Active and attacks whenever it can, and nothing else). Because the engine lists End Turn first among the legal moves and `aa` takes the first move when it cannot attach or attack, `aa` never benches a Pokémon, not even at setup, and never plays a Trainer: the opponent is one Active Pokémon, and knocking it out wins. That makes it a fixed clock (here mostly Hoopa ex: 30 a turn from its first Energy, 100 from its third), not a real opponent.

Two pilots for this list. **sp** (scripted pilot, the main reading): the solitaire model's priorities playing the real engine through the add-on: benches Basics, plays the draw, search, Rare Candy and Energy cards, evolves, puts Energy on the main line, attaches defensive Tools, heals a hurt Active, retreats to a Pokémon that can attack, and attacks for the most damage. **aa** (the brief's pilot): the engine's own bot on this side too, so both sides have a single Pokémon and the game ends at the first knockout; its "points conceded" can never exceed what one knockout gives. `et` ends every turn at once and never attacks, so it is not used. 150 games per pilot; the coin decides who goes first.

"Damaging attack" = the list's first attack that damaged or knocked out the opposing Active (poison it applied counts). "Conceded" = the opponent's points at that moment (or at the end if it never came). "Main attacks" = the first attack by the main attacker. "Dead" = cards in hand at the end of the turn that the rules did not let you play then (own turns 1-4; a second Supporter after one was played counts as dead; cards that need an opposing Bench, such as Cyrus and Sabrina, are left out because this opponent never has one).

| pilot | seat | games | won | damaging attack by T2 | by T3 | by T4 | never | points conceded before it | conceded 2+ | main attacks by T3 | by T4 | never | conceded before main | dead cards / turn |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sp | first | 73 | 88% | 15% | 16% | 21% | 73% | 0.56 | 21% | 59% | 64% | 27% | 0.55 | 1.6 |
| sp | second | 77 | 95% | 42% | 56% | 60% | 36% | 0.18 | 6% | 49% | 51% | 43% | 0.36 | 1.7 |
| aa | first | 77 | 42% | 74% | 100% | 100% | 0% | 0.00 | 0% | - | - | - | - | 0.8 |
| aa | second | 73 | 71% | 100% | 100% | 100% | 0% | 0.00 | 0% | - | - | - | - | 1.0 |

Most often dead at end of turn (sp): Vespiquen ex 30%, Fragrant Forest 28%, Copycat 20%, Shuckle ex 12% of turn-ends.

Most often dead at end of turn (aa): Vespiquen ex 48%, Field Blower 27% of turn-ends.

Engine game seeds (one per game): sp: 21,002,170,000 to 21,002,170,149, aa: 21,002,175,000 to 21,002,175,149. The won column is against a single Pokémon that never plays a Trainer and means little; read the tempo columns. The `aa` opponent also never plays a card, so its hand grows and Copycat draws more than it would on the ladder.

## 6. Coverage flag

Cards that hit known blind spots of the engine's bots, so the simulator's numbers for this list are less trustworthy where these cards matter:
- **(a)** text names the opponent's hand or deck: blind k3 leaves the move unpriced (engine/src/observation.rs `hidden_continuation_reason`).
- **(b)** attack effect outside the damage estimator: the bots value the attack at printed damage (engine/src/players/value_functions.rs `estimated_attack_damage_ex`, fallback `_ => fixed`; effect texts read from engine/src/actions/effect_mechanic_map.rs). "b-" = the effect does not change damage (status, self-damage), so only its side effect is unvalued.
- **(c)** played from hand: the opponent-reply search (the `o` tiers such as b3o3n4; k3 has no reply ply) only considers attacks, retreats, Abilities, draws and the turn's Energy (engine/src/players/expectiminimax_player.rs `is_public_information_action`).

| card | flags |
|---|---|
| Combee ×2 | **(b-)** attack Reckless Charge: effect not in the damage estimate (mechanic SelfDamage has no damage estimator); damage read as printed 30 |
| Vespiquen ex ×2 | **(b)** attack Chase Order: damage-changing effect, mechanic OptionalDiscardBenchedBasicForExtraDamage has no damage estimator; the bots value it at printed 70<br>**(c)** evolves from hand: the opponent's reply search never sees the evolution |
| Shuckle ex ×2 | **(c)** a copy benched from hand changes the board (passive Ability): not seen by the reply search |
| Teal Mask Ogerpon ex ×1 | **(c)** a copy benched from hand changes the board (passive Ability): not seen by the reply search |
| Copycat ×2 | **(a)** card names the opponent's hand or deck: blind k3 leaves it unpriced |
| Cyrus ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Sabrina ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| X Speed ×2 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Field Blower ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Leaf Cape ×2 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |

**Reading:** k3 leaves Copycat unpriced; the damage of Vespiquen ex is read as printed. Bot numbers for this list are untrusted to that extent.

## Draw, search and Energy effects in this list

What the solitaire model plays (card text from lib/card.py):

| card | text | model |
|---|---|---|
| Professor's Research ×2 | Draw 2 cards. | modeled: draw 2 |
| Copycat ×2 | Shuffle your hand into your deck. Draw a card for each card in your opponent's hand. | modeled: shuffle hand in, draw opponent-hand-size |
| Cyrus ×1 | Switch in 1 of your opponent's Benched Pokémon that has damage on it to the Active Spot. | ignored: not a draw, search, evolution or Energy effect |
| Sabrina ×1 | Switch out your opponent's Active Pokémon to the Bench. (Your opponent chooses the new Active Pokémon.) | ignored: not a draw, search, evolution or Energy effect |
| X Speed ×2 | During this turn, the Retreat Cost of your Active Pokémon is 1 less. | ignored: not a draw, search, evolution or Energy effect |
| Field Blower ×1 | Discard a Pokémon Tool card from a Pokémon (yours or your opponent's), or discard a Stadium card in play. | ignored: not a draw, search, evolution or Energy effect |
| Leaf Cape ×2 | The [G] Pokémon this card is attached to gets +30 HP. | ignored: not a draw, search, evolution or Energy effect |
| Fragrant Forest ×2 | Once during each player's turn, that player may put a random Basic [G] Pokémon from their deck into their hand. | modeled: search 1 random Basic [G] Pokémon to hand (once a turn) |

## How the solitaire pilot plays

Setup: all Basics in hand go into play (Active: a Basic with an "if Active" draw Ability, else one outside the main line). Each own turn: draw; then repeat until nothing changes: play a Stadium that does something here, use it, play Items (Poké Ball and other searches take a random matching card, as printed; Rare Candy on the main line first), bench Basics the plan needs (others only while the Bench has room to spare), evolve (main line first), use draw Abilities, attach Tool pieces; when nothing else moves, one Supporter: a search that finds a missing piece, else a draw, else Copycat when the hand is small and holds nothing needed (Copycat assumes the opponent holds 4 cards). Then the turn's Energy (random among the declared types) goes to the main line first, then other combo attackers, else the Active; Energy from the discard or from Abilities is added; then the check; an Ability that ends the turn is used only when the main attacker cannot attack. No opponent, no knockouts, no retreat, no attacks (attack effects that set up, such as Flock or Glittering Gift, are ignored), no coin-flip Supporters. Hand limit 10.

Generated by `lib/consistency.py` in 22 s; solitaire seed 21,002,170,000 (Python random, same deals across variants).
