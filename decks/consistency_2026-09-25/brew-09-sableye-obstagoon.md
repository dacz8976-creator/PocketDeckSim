# Consistency: brew-09-sableye-obstagoon

`decks/brews/brew-09-sableye-obstagoon.txt` · Energy: Darkness · main attacker: Mega Sableye ex (Basic), Cursed Jewel [DC] 80 · combo: Mega Sableye ex + Galarian Obstagoon

Ladder record: -

**In one line:** brew-09-sableye-obstagoon: one-Basic opening 75%; Mega Sableye ex online by own T3 92% first / 92% second (T4 95%/96%); combo by T4 63%/63%; goldfish (scripted pilot v aa): damaging attack by own T3 59% with 0.3 pts conceded first, Mega Sableye ex attacks by T4 67% with 0.4 conceded first, 2.0 dead cards/turn; unpriced-text cards (a): 1

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
| Mega Sableye ex | 38% | | Mega Sableye ex | 59% |
| Galarian Zigzagoon | 38% | | Galarian Zigzagoon | 59% |
|  |  | | Galarian Obstagoon | 42% |

## 2. Main attacker online

"Online" = Mega Sableye ex in play (Active or Bench) with the Energy for Cursed Jewel [DC] attached, at the moment you would attack. Fastest possible without acceleration: own turn 3 going first, 2 going second.

| | going first T2 | T3 | T4 | going second T2 | T3 | T4 |
|---|---|---|---|---|---|---|
| Mega Sableye ex online | 0% | 92% | 95% | 85% | 92% | 96% |
| Mega Sableye ex in play (any Energy) | 92% | 95% | 97% | 92% | 96% | 98% |
| online, draw/search cards not played | 0% | 69% | 74% | 65% | 70% | 74% |

Where "in play" is well above "online", Energy is the limit (one a turn); where both are low, finding the cards is the limit. The last row shows what the list's draw and search cards add.

## 3. Stage 2 in play

Stage 2 cards: Galarian Obstagoon. Rare Candy in the list: yes.

| | going first T3 | T4 | going second T3 | T4 |
|---|---|---|---|---|
| any Stage 2 in play (list as built) | 53% | 65% | 52% | 64% |
| same deals, Rare Candy never played | 0% | 0% | 0% | 0% |

## 4. Combo assembled

Pieces: Mega Sableye ex + Galarian Obstagoon. A Pokémon piece counts when it is in play; a Trainer piece when it is in hand or already played.

| by own turn | 2 | 3 | 4 | 5 |
|---|---|---|---|---|
| going first | 34% | 50% | 63% | 75% |
| going second | 34% | 49% | 63% | 75% |

Each piece on its own (going first / second):

| piece | by T3 | by T5 |
|---|---|---|
| Mega Sableye ex | 95% / 96% | 99% / 99% |
| Galarian Obstagoon | 53% / 52% | 76% / 76% |

### Drawing each card

Each card, drawn or fetched at least once by own turn 3 / by own turn 5 (the opening hand counts; going first, the list's draw and search cards played; "no draw" = the same deals with them left in hand):

| card | copies | by T3 | by T5 | by T3, no draw | by T5, no draw |
|---|---|---|---|---|---|
| Mega Sableye ex | 2 | 95% | 99% | 74% | 82% |
| Galarian Zigzagoon | 2 | 94% | 98% | 74% | 82% |
| Galarian Obstagoon | 2 | 79% | 90% | 64% | 75% |
| Rare Candy | 2 | 78% | 89% | 64% | 75% |
| Professor's Research | 2 | 72% | 84% | 64% | 76% |
| Poké Ball | 2 | 79% | 89% | 63% | 75% |
| Copycat | 2 | 75% | 88% | 64% | 75% |
| Cyrus | 1 | 57% | 74% | 38% | 49% |
| Pokémon Center Lady | 1 | 57% | 73% | 38% | 49% |
| Deceptive Needle | 1 | 57% | 73% | 38% | 49% |
| Giant Cape | 1 | 57% | 74% | 38% | 48% |
| Starting Plains | 1 | 57% | 74% | 39% | 50% |
| Field Blower | 1 | 57% | 73% | 39% | 49% |

## 5. Goldfish against the engine

The real engine (rules4: rl/addon-0.7.2/deckgym and the pdl_rl_env 0.7.2 add-on built from the same rules) plays this list against `decks/research/weezing.txt` piloted by the engine's `aa` bot (attach-and-attack: it puts its Energy on the Active and attacks whenever it can, and nothing else). Because the engine lists End Turn first among the legal moves and `aa` takes the first move when it cannot attach or attack, `aa` never benches a Pokémon, not even at setup, and never plays a Trainer: the opponent is one Active Pokémon, and knocking it out wins. That makes it a fixed clock (here mostly Hoopa ex: 30 a turn from its first Energy, 100 from its third), not a real opponent.

Two pilots for this list. **sp** (scripted pilot, the main reading): the solitaire model's priorities playing the real engine through the add-on: benches Basics, plays the draw, search, Rare Candy and Energy cards, evolves, puts Energy on the main line, attaches defensive Tools, heals a hurt Active, retreats to a Pokémon that can attack, and attacks for the most damage. **aa** (the brief's pilot): the engine's own bot on this side too, so both sides have a single Pokémon and the game ends at the first knockout; its "points conceded" can never exceed what one knockout gives. `et` ends every turn at once and never attacks, so it is not used. 150 games per pilot; the coin decides who goes first.

"Damaging attack" = the list's first attack that damaged or knocked out the opposing Active (poison it applied counts). "Conceded" = the opponent's points at that moment (or at the end if it never came). "Main attacks" = the first attack by the main attacker. "Dead" = cards in hand at the end of the turn that the rules did not let you play then (own turns 1-4; a second Supporter after one was played counts as dead; cards that need an opposing Bench, such as Cyrus and Sabrina, are left out because this opponent never has one).

| pilot | seat | games | won | damaging attack by T2 | by T3 | by T4 | never | points conceded before it | conceded 2+ | main attacks by T3 | by T4 | never | conceded before main | dead cards / turn |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sp | first | 70 | 99% | 4% | 46% | 80% | 0% | 0.44 | 1% | 39% | 67% | 17% | 0.50 | 2.0 |
| sp | second | 80 | 100% | 60% | 70% | 86% | 0% | 0.15 | 0% | 49% | 68% | 16% | 0.36 | 2.1 |
| aa | first | 73 | 67% | 41% | 100% | 100% | 0% | 0.00 | 0% | - | - | - | - | 1.5 |
| aa | second | 77 | 70% | 100% | 100% | 100% | 0% | 0.00 | 0% | - | - | - | - | 1.5 |

Most often dead at end of turn (sp): Galarian Obstagoon 45%, Rare Candy 37%, Copycat 24%, Pokémon Center Lady 18% of turn-ends.

Most often dead at end of turn (aa): Galarian Obstagoon 50%, Rare Candy 48%, Field Blower 28%, Pokémon Center Lady 9% of turn-ends.

Engine game seeds (one per game): sp: 21,002,080,000 to 21,002,080,149, aa: 21,002,085,000 to 21,002,085,149. The won column is against a single Pokémon that never plays a Trainer and means little; read the tempo columns. The `aa` opponent also never plays a card, so its hand grows and Copycat draws more than it would on the ladder.

## 6. Coverage flag

Cards that hit known blind spots of the engine's bots, so the simulator's numbers for this list are less trustworthy where these cards matter:
- **(a)** text names the opponent's hand or deck: blind k3 leaves the move unpriced (engine/src/observation.rs `hidden_continuation_reason`).
- **(b)** attack effect outside the damage estimator: the bots value the attack at printed damage (engine/src/players/value_functions.rs `estimated_attack_damage_ex`, fallback `_ => fixed`; effect texts read from engine/src/actions/effect_mechanic_map.rs). "b-" = the effect does not change damage (status, self-damage), so only its side effect is unvalued.
- **(c)** played from hand: the opponent-reply search (the `o` tiers such as b3o3n4; k3 has no reply ply) only considers attacks, retreats, Abilities, draws and the turn's Energy (engine/src/players/expectiminimax_player.rs `is_public_information_action`).

| card | flags |
|---|---|
| Mega Sableye ex ×2 | **(b-)** attack Cursed Jewel: effect not in the damage estimate (mechanic DamageAndCardEffect has no damage estimator); damage read as printed 80 |
| Galarian Obstagoon ×2 | **(b)** attack Merciless Strike: damage-changing effect, mechanic ExtraDamageIfHurt has no damage estimator; the bots value it at printed 70<br>**(c)** evolves from hand: the opponent's reply search never sees the evolution |
| Rare Candy ×2 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Copycat ×2 | **(a)** card names the opponent's hand or deck: blind k3 leaves it unpriced |
| Cyrus ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Pokémon Center Lady ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Deceptive Needle ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Giant Cape ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Starting Plains ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Field Blower ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |

**Reading:** k3 leaves Copycat unpriced; the damage of Galarian Obstagoon is read as printed. Bot numbers for this list are untrusted to that extent.

## Draw, search and Energy effects in this list

What the solitaire model plays (card text from lib/card.py):

| card | text | model |
|---|---|---|
| Rare Candy ×2 | Choose 1 of your Basic Pokémon in play. If you have a Stage 2 card in your hand that evolves from that Pokémon, put that card onto the Basic Pokémon to evolve it, skipping the Stage 1. You can't use this card during your first turn or on a Basic Pokémon that was put into play this turn. | modeled: Basic straight to Stage 2 (not own turn 1, not a Basic played this turn) |
| Professor's Research ×2 | Draw 2 cards. | modeled: draw 2 |
| Poké Ball ×2 | Put a random Basic Pokémon from your deck into your hand. | modeled: search 1 random Basic Pokémon to hand |
| Copycat ×2 | Shuffle your hand into your deck. Draw a card for each card in your opponent's hand. | modeled: shuffle hand in, draw opponent-hand-size |
| Cyrus ×1 | Switch in 1 of your opponent's Benched Pokémon that has damage on it to the Active Spot. | ignored: not a draw, search, evolution or Energy effect |
| Pokémon Center Lady ×1 | Heal 30 damage from 1 of your Pokémon, and it recovers from all Special Conditions. | ignored: not a draw, search, evolution or Energy effect |
| Deceptive Needle ×1 | At the end of your turn, if the [D] Pokémon this card is attached to is in the Active Spot, do 10 damage to your opponent's Active Pokémon. | ignored: not a draw, search, evolution or Energy effect |
| Giant Cape ×1 | The Pokémon this card is attached to gets +20 HP. | ignored: not a draw, search, evolution or Energy effect |
| Starting Plains ×1 | Each Basic Pokémon in play (both yours and your opponent's) gets +20 HP. | ignored: not a draw, search, evolution or Energy effect |
| Field Blower ×1 | Discard a Pokémon Tool card from a Pokémon (yours or your opponent's), or discard a Stadium card in play. | ignored: not a draw, search, evolution or Energy effect |

## How the solitaire pilot plays

Setup: all Basics in hand go into play (Active: a Basic with an "if Active" draw Ability, else one outside the main line). Each own turn: draw; then repeat until nothing changes: play a Stadium that does something here, use it, play Items (Poké Ball and other searches take a random matching card, as printed; Rare Candy on the main line first), bench Basics the plan needs (others only while the Bench has room to spare), evolve (main line first), use draw Abilities, attach Tool pieces; when nothing else moves, one Supporter: a search that finds a missing piece, else a draw, else Copycat when the hand is small and holds nothing needed (Copycat assumes the opponent holds 4 cards). Then the turn's Energy (random among the declared types) goes to the main line first, then other combo attackers, else the Active; Energy from the discard or from Abilities is added; then the check; an Ability that ends the turn is used only when the main attacker cannot attack. No opponent, no knockouts, no retreat, no attacks (attack effects that set up, such as Flock or Glittering Gift, are ignored), no coin-flip Supporters. Hand limit 10.

Generated by `lib/consistency.py` in 47 s; solitaire seed 21,002,080,000 (Python random, same deals across variants).
