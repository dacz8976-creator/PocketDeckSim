# Consistency: research-sceptile

`decks/research/sceptile.txt` · Energy: Grass · main attacker: Mega Sceptile ex (Stage 2), Terminating Tail [GG] 130 · combo: Mega Sceptile ex + Butterfree

**In one line:** research-sceptile: one-Basic opening 86%; Mega Sceptile ex online by own T3 41% first / 41% second (T4 64%/64%); combo by T4 54%/55%; goldfish (scripted pilot v aa): damaging attack by own T3 68% with 0.2 pts conceded first, Mega Sceptile ex attacks by T4 20% with 0.5 conceded first, 2.7 dead cards/turn; unpriced-text cards (a): 2

Turns are the player's own turns (own turn 1 is your first turn whether you go first or second). Going first: no Energy on own turn 1, but you draw. Nobody evolves on their own turn 1. Solitaire figures come from 10,000 deals per seat (about ±1 point); the opening table is exact.

## 1. Opening hand

3 Basic Pokémon in 20 cards. The 5-card hand is dealt at random; only a hand with no Basic has one random card swapped for a random Basic, so extra Basics are not favoured. The opening is the same going first or second.

| Basics in the opening hand | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| exact | 86% | 13% | 1% | 0% | 0% |
| solitaire check | 86% | 13% | 1% | 0% | 0% |

**Exactly one Basic: 86%** (of which 40% are swap-in hands that had none).

| Only Basic in the hand is… | chance | | Card in the opening hand | chance |
|---|---|---|---|---|
| Caterpie | 57% | | Caterpie | 71% |
| Treecko | 29% | | Metapod | 41% |
|  |  | | Butterfree | 41% |
|  |  | | Treecko | 38% |
|  |  | | Grovyle | 23% |
|  |  | | Mega Sceptile ex | 23% |

## 2. Main attacker online

"Online" = Mega Sceptile ex in play (Active or Bench) with the Energy for Terminating Tail [GG] attached, at the moment you would attack. Fastest possible without acceleration: own turn 3 going first, 3 going second.

| | going first T2 | T3 | T4 | going second T2 | T3 | T4 |
|---|---|---|---|---|---|---|
| Mega Sceptile ex online | 0% | 41% | 64% | 0% | 41% | 64% |
| Mega Sceptile ex in play (any Energy) | 0% | 41% | 64% | 0% | 41% | 64% |
| online, draw/search cards not played | 0% | 18% | 24% | 0% | 18% | 23% |

Where "in play" is well above "online", Energy is the limit (one a turn); where both are low, finding the cards is the limit. The last row shows what the list's draw and search cards add.

## 3. Stage 2 in play

Stage 2 cards: Butterfree, Mega Sceptile ex. Rare Candy in the list: no.

| | going first T3 | T4 | going second T3 | T4 |
|---|---|---|---|---|
| any Stage 2 in play (list as built) | 90% | 96% | 91% | 97% |

## 4. Combo assembled

Pieces: Mega Sceptile ex + Butterfree. A Pokémon piece counts when it is in play; a Trainer piece when it is in hand or already played.

| by own turn | 2 | 3 | 4 | 5 |
|---|---|---|---|---|
| going first | 0% | 28% | 54% | 72% |
| going second | 0% | 29% | 55% | 72% |

Each piece on its own (going first / second):

| piece | by T3 | by T5 |
|---|---|---|
| Mega Sceptile ex | 41% / 41% | 77% / 77% |
| Butterfree | 78% / 79% | 93% / 94% |

### Drawing each card

Each card, drawn or fetched at least once by own turn 3 / by own turn 5 (the opening hand counts; going first, the list's draw and search cards played; "no draw" = the same deals with them left in hand):

| card | copies | by T3 | by T5 | by T3, no draw | by T5, no draw |
|---|---|---|---|---|---|
| Caterpie | 2 | 97% | 99% | 83% | 88% |
| Metapod | 2 | 96% | 99% | 90% | 94% |
| Butterfree | 2 | 89% | 98% | 78% | 88% |
| Treecko | 1 | 90% | 97% | 52% | 60% |
| Grovyle | 1 | 83% | 95% | 58% | 70% |
| Mega Sceptile ex | 1 | 68% | 90% | 46% | 60% |
| Professor's Research | 2 | 69% | 84% | 63% | 76% |
| Erika | 1 | 57% | 81% | 38% | 50% |
| Copycat | 1 | 51% | 69% | 37% | 49% |
| Sabrina | 1 | 56% | 80% | 39% | 50% |
| Cyrus | 1 | 57% | 80% | 38% | 49% |
| Quick-Grow Extract | 2 | 79% | 92% | 64% | 76% |
| Leaf Cape | 1 | 56% | 80% | 38% | 50% |
| Fragrant Forest | 2 | 77% | 90% | 63% | 77% |

## 5. Goldfish against the engine

The real engine (rules4: rl/addon-0.7.2/deckgym and the pdl_rl_env 0.7.2 add-on built from the same rules) plays this list against `decks/research/weezing.txt` piloted by the engine's `aa` bot (attach-and-attack: it puts its Energy on the Active and attacks whenever it can, and nothing else). Because the engine lists End Turn first among the legal moves and `aa` takes the first move when it cannot attach or attack, `aa` never benches a Pokémon, not even at setup, and never plays a Trainer: the opponent is one Active Pokémon, and knocking it out wins. That makes it a fixed clock (here mostly Hoopa ex: 30 a turn from its first Energy, 100 from its third), not a real opponent.

Two pilots for this list. **sp** (scripted pilot, the main reading): the solitaire model's priorities playing the real engine through the add-on: benches Basics, plays the draw, search, Rare Candy and Energy cards, evolves, puts Energy on the main line, attaches defensive Tools, heals a hurt Active, retreats to a Pokémon that can attack, and attacks for the most damage. **aa** (the brief's pilot): the engine's own bot on this side too, so both sides have a single Pokémon and the game ends at the first knockout; its "points conceded" can never exceed what one knockout gives. `et` ends every turn at once and never attacks, so it is not used. 150 games per pilot; the coin decides who goes first.

"Damaging attack" = the list's first attack that damaged or knocked out the opposing Active (poison it applied counts). "Conceded" = the opponent's points at that moment (or at the end if it never came). "Main attacks" = the first attack by the main attacker. "Dead" = cards in hand at the end of the turn that the rules did not let you play then (own turns 1-4; a second Supporter after one was played counts as dead; cards that need an opposing Bench, such as Cyrus and Sabrina, are left out because this opponent never has one).

| pilot | seat | games | won | damaging attack by T2 | by T3 | by T4 | never | points conceded before it | conceded 2+ | main attacks by T3 | by T4 | never | conceded before main | dead cards / turn |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sp | first | 66 | 98% | 14% | 27% | 97% | 0% | 0.52 | 3% | 14% | 29% | 58% | 0.85 | 2.7 |
| sp | second | 84 | 99% | 56% | 100% | 100% | 0% | 0.01 | 0% | 10% | 13% | 87% | 0.25 | 2.6 |
| aa | first | 96 | 33% | 100% | 100% | 100% | 0% | 0.00 | 0% | - | - | - | - | 1.8 |
| aa | second | 54 | 67% | 100% | 100% | 100% | 0% | 0.00 | 0% | - | - | - | - | 1.9 |

Most often dead at end of turn (sp): Butterfree 27%, Fragrant Forest 23%, Mega Sceptile ex 23%, Metapod 15% of turn-ends.

Most often dead at end of turn (aa): Metapod 47%, Butterfree 34%, Mega Sceptile ex 32%, Grovyle 27% of turn-ends.

Engine game seeds (one per game): sp: 21,002,150,000 to 21,002,150,149, aa: 21,002,155,000 to 21,002,155,149. The won column is against a single Pokémon that never plays a Trainer and means little; read the tempo columns. The `aa` opponent also never plays a card, so its hand grows and Copycat draws more than it would on the ladder.

## 6. Coverage flag

Cards that hit known blind spots of the engine's bots, so the simulator's numbers for this list are less trustworthy where these cards matter:
- **(a)** text names the opponent's hand or deck: blind k3 leaves the move unpriced (engine/src/observation.rs `hidden_continuation_reason`).
- **(b)** attack effect outside the damage estimator: the bots value the attack at printed damage (engine/src/players/value_functions.rs `estimated_attack_damage_ex`, fallback `_ => fixed`; effect texts read from engine/src/actions/effect_mechanic_map.rs). "b-" = the effect does not change damage (status, self-damage), so only its side effect is unvalued.
- **(c)** played from hand: the opponent-reply search (the `o` tiers such as b3o3n4; k3 has no reply ply) only considers attacks, retreats, Abilities, draws and the turn's Energy (engine/src/players/expectiminimax_player.rs `is_public_information_action`).

| card | flags |
|---|---|
| Caterpie ×2 | **(a)** Ability Quick Growth searches this deck automatically: the opposing bot's end of turn is left unpriced<br>**(c)** a copy benched from hand changes the board (passive Ability): not seen by the reply search |
| Metapod ×2 | **(c)** evolves from hand: the opponent's reply search never sees the evolution |
| Butterfree ×2 | **(b-)** attack Sunny Wind: effect not in the damage estimate (mechanic SelfHeal has no damage estimator); damage read as printed 60<br>**(c)** evolves from hand: the opponent's reply search never sees the evolution |
| Grovyle ×1 | **(c)** evolves from hand: the opponent's reply search never sees the evolution |
| Mega Sceptile ex ×1 | **(b-)** attack Terminating Tail: effect not in the damage estimate (mechanic SelfDiscardEnergyAndInflictStatus has no damage estimator); damage read as printed 130<br>**(c)** evolves from hand: the opponent's reply search never sees the evolution |
| Erika ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Copycat ×1 | **(a)** card names the opponent's hand or deck: blind k3 leaves it unpriced |
| Sabrina ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Cyrus ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Quick-Grow Extract ×2 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Leaf Cape ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |

**Reading:** k3 leaves Caterpie, Copycat unpriced. Bot numbers for this list are untrusted to that extent.

## Draw, search and Energy effects in this list

What the solitaire model plays (card text from lib/card.py):

| card | text | model |
|---|---|---|
| Caterpie ×2 | Ability Quick Growth: At the end of your opponent's turn, if this Pokémon is in the Active Spot, put a random card from your deck that evolves from this Pokémon onto this Pokémon to evolve it. | ability modeled: evolves from the deck after the opponent's turn (if Active) |
| Professor's Research ×2 | Draw 2 cards. | modeled: draw 2 |
| Erika ×1 | Heal 50 damage from 1 of your [G] Pokémon. | ignored: not a draw, search, evolution or Energy effect |
| Copycat ×1 | Shuffle your hand into your deck. Draw a card for each card in your opponent's hand. | modeled: shuffle hand in, draw opponent-hand-size |
| Sabrina ×1 | Switch out your opponent's Active Pokémon to the Bench. (Your opponent chooses the new Active Pokémon.) | ignored: not a draw, search, evolution or Energy effect |
| Cyrus ×1 | Switch in 1 of your opponent's Benched Pokémon that has damage on it to the Active Spot. | ignored: not a draw, search, evolution or Energy effect |
| Quick-Grow Extract ×2 | Choose 1 of your [G] Pokémon in play. Put a random [G] Pokémon from your deck that evolves from that Pokémon onto that Pokémon to evolve it. You can't use this card during your first turn or on a Pokémon that was put into play this turn. | modeled: evolve a [G] Pokémon from the deck |
| Leaf Cape ×1 | The [G] Pokémon this card is attached to gets +30 HP. | ignored: not a draw, search, evolution or Energy effect |
| Fragrant Forest ×2 | Once during each player's turn, that player may put a random Basic [G] Pokémon from their deck into their hand. | modeled: search 1 random Basic [G] Pokémon to hand (once a turn) |

## How the solitaire pilot plays

Setup: all Basics in hand go into play (Active: a Basic with an "if Active" draw Ability, else one outside the main line). Each own turn: draw; then repeat until nothing changes: play a Stadium that does something here, use it, play Items (Poké Ball and other searches take a random matching card, as printed; Rare Candy on the main line first), bench Basics the plan needs (others only while the Bench has room to spare), evolve (main line first), use draw Abilities, attach Tool pieces; when nothing else moves, one Supporter: a search that finds a missing piece, else a draw, else Copycat when the hand is small and holds nothing needed (Copycat assumes the opponent holds 4 cards). Then the turn's Energy (random among the declared types) goes to the main line first, then other combo attackers, else the Active; Energy from the discard or from Abilities is added; then the check; an Ability that ends the turn is used only when the main attacker cannot attack. No opponent, no knockouts, no retreat, no attacks (attack effects that set up, such as Flock or Glittering Gift, are ignored), no coin-flip Supporters. Hand limit 10.

Generated by `lib/consistency.py` in 19 s; solitaire seed 21,002,150,000 (Python random, same deals across variants).
