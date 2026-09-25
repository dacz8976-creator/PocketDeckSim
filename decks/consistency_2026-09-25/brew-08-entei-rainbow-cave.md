# Consistency: brew-08-entei-rainbow-cave

`decks/brews/brew-08-entei-rainbow-cave.txt` · Energy: Fire · main attacker: Entei ex (Basic), Blazing Beatdown [RR] 60 · combo: Entei ex + Rainbow Cave + Flame Patch

Ladder record: -

**In one line:** brew-08-entei-rainbow-cave: one-Basic opening 95%; Entei ex online by own T3 100% first / 100% second (T4 100%/100%); combo by T4 84%/85%; goldfish (scripted pilot v aa, seat-balanced): 0.00 pts conceded before the first 30+ damage attack (by own T3 in 100%), Entei ex attacks by T4 100% with 0.00 conceded first, 2.3 dead cards/turn; unpriced-text cards (a): 1

Turns are the player's own turns (own turn 1 is your first turn whether you go first or second). Going first: no Energy on own turn 1, but you draw. Nobody evolves on their own turn 1. Solitaire figures come from 10,000 deals per seat (about ±1 point); the opening table is exact.

## 1. Opening hand

2 Basic Pokémon in 20 cards. The 5-card hand is dealt at random; only a hand with no Basic has one random card swapped for a random Basic, so extra Basics are not favoured. The opening is the same going first or second.

| Basics in the opening hand | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| exact | 95% | 5% | 0% | 0% | 0% |
| solitaire check | 95% | 5% | 0% | 0% | 0% |

**Exactly one Basic: 95%** (of which 55% are swap-in hands that had none).

| Only Basic in the hand is… | chance | | Card in the opening hand | chance |
|---|---|---|---|---|
| Entei ex | 95% | | Entei ex | 100% |
|  |  | | Flame Patch | 40% |
|  |  | | Rainbow Cave | 40% |

## 2. Main attacker online

"Online" = Entei ex in play (Active or Bench) with the Energy for Blazing Beatdown [RR] attached, at the moment you would attack. Fastest possible without acceleration: own turn 3 going first, 2 going second.

| | going first T2 | T3 | T4 | going second T2 | T3 | T4 |
|---|---|---|---|---|---|---|
| Entei ex online | 55% | 100% | 100% | 100% | 100% | 100% |
| Entei ex in play (any Energy) | 100% | 100% | 100% | 100% | 100% | 100% |
| online, draw/search cards not played | 28% | 100% | 100% | 100% | 100% | 100% |

Where "in play" is well above "online", Energy is the limit (one a turn); where both are low, finding the cards is the limit. The last row shows what the list's draw and search cards add.

## 3. Stage 2 in play

No Stage 2 in the list.

## 4. Combo assembled

Pieces: Entei ex + Rainbow Cave + Flame Patch. A Pokémon piece counts when it is in play; a Trainer piece when it is in hand or already played.

| by own turn | 2 | 3 | 4 | 5 |
|---|---|---|---|---|
| going first | 55% | 75% | 84% | 85% |
| going second | 55% | 76% | 85% | 85% |

Each piece on its own (going first / second):

| piece | by T3 | by T5 |
|---|---|---|
| Entei ex | 100% / 100% | 100% / 100% |
| Rainbow Cave | 87% / 87% | 91% / 91% |
| Flame Patch | 87% / 87% | 94% / 94% |

### Drawing each card

Each card, drawn or fetched at least once by own turn 3 / by own turn 5 (the opening hand counts; going first, the list's draw and search cards played; "no draw" = the same deals with them left in hand):

| card | copies | by T3 | by T5 | by T3, no draw | by T5, no draw |
|---|---|---|---|---|---|
| Entei ex | 2 | 100% | 100% | 100% | 100% |
| Professor's Research | 2 | 85% | 95% | 63% | 75% |
| Copycat | 2 | 89% | 97% | 62% | 74% |
| Pokémon Center Lady | 1 | 69% | 83% | 38% | 48% |
| Sabrina | 1 | 70% | 83% | 38% | 48% |
| Cyrus | 1 | 70% | 83% | 38% | 48% |
| Lucky Ice Pop | 2 | 92% | 98% | 62% | 74% |
| Flame Patch | 2 | 91% | 94% | 62% | 74% |
| Repel | 1 | 70% | 83% | 38% | 49% |
| Poké Ball | 1 | 67% | 78% | 37% | 48% |
| Giant Cape | 2 | 92% | 98% | 62% | 74% |
| Rainbow Cave | 2 | 89% | 91% | 62% | 75% |
| Starting Plains | 1 | 69% | 83% | 38% | 48% |

## 5. Goldfish against the engine

The real engine (rules4: rl/addon-0.7.2/deckgym and the pdl_rl_env 0.7.2 add-on built from the same rules) plays this list against `decks/research/weezing.txt` piloted by the engine's `aa` bot (attach-and-attack: it puts its Energy on the Active and attacks whenever it can, and nothing else). Because the engine lists End Turn first among the legal moves and `aa` takes the first move when it cannot attach or attack, `aa` never benches a Pokémon, not even at setup, and never plays a Trainer: the opponent is one Active Pokémon, and knocking it out wins. That makes it a fixed clock (here mostly Hoopa ex: 30 a turn from its first Energy, 100 from its third), not a real opponent.

Two pilots for this list. **sp** (scripted pilot, the main reading): the solitaire model's priorities playing the real engine through the add-on. It leads with a Basic whose Ability works from the Active Spot (Pyukumuku's Innards Out, Entei ex's Legendary Pulse), else one outside the main line with the most HP (`--lead` overrides); benches Basics, plays the draw, search, Rare Candy and Energy cards, evolves, puts Energy on the main line, attaches defensive Tools, heals a hurt Active, uses Abilities that draw, search, add Energy, damage the opposing Active (Crobat's Cunning Link) or give it a Special Condition (Meowstic's Perplexing Ears), plays a Supporter such as Team Rocket's Master Plan when the Active's attack gains from the Condition this turn, and attacks for the most damage. When a main or combo Pokémon is Active and the turn's Energy lets it attack this turn for as much as a Benched one could, the Energy goes on it. Otherwise, when a Benched main or combo Pokémon can attack and the Active cannot (or the Benched one does 40+ more and the Active is outside the main line), the turn's Energy goes on the Active until it can retreat, and it retreats. **aa** (the brief's pilot): the engine's own bot on this side too, so both sides have a single Pokémon and the game ends at the first knockout; its "points conceded" can never exceed what one knockout gives. `et` ends every turn at once and never attacks, so it is not used. 150 games per pilot; the coin decides who goes first, so the seats get different numbers of games; the "both seats" row is the plain mean of the two seat means.

"30+ attack" (the headline tempo reading) = the list's first attack that did 30 or more damage to the opposing Active or knocked it out (Poison or Burn the attack applied counts at the next Checkup; Poison or Burn that was already there does not). "Damaging attack" = the first attack that did any damage, chip damage included (Hatenna's Stampede for 10 counts). "Conceded" = the opponent's points at that moment (or at the end if it never came); ± is the standard error of the mean over these games: simulation noise only, nothing about the ladder. "Main attacks" = the first attack by the main attacker. "Dead" = cards in hand at the end of the turn that the rules did not let you play then (own turns 1-4; a second Supporter after one was played counts as dead; cards that need an opposing Bench, such as Cyrus and Sabrina, are left out because this opponent never has one).

| pilot | seat | games | won | 30+ attack by T3 | by T4 | never | conceded before it | damaging attack by T3 | never | conceded before it | main attacks by T3 | by T4 | never | conceded before main | dead cards / turn |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sp | first | 74 | 100% | 100% | 100% | 0% | 0.00 ± 0.00 | 100% | 0% | 0.00 ± 0.00 | 100% | 100% | 0% | 0.00 | 2.3 |
| sp | second | 76 | 100% | 100% | 100% | 0% | 0.00 ± 0.00 | 100% | 0% | 0.00 ± 0.00 | 100% | 100% | 0% | 0.00 | 2.2 |
| sp | **both seats** | 74 + 76 | - | 100% | 100% | 0% | 0.00 ± 0.00 | 100% | 0% | 0.00 ± 0.00 | 100% | 100% | 0% | 0.00 | 2.3 |
| aa | first | 75 | 32% | - | - | - | - | 100% | 0% | 0.00 ± 0.00 | - | - | - | - | 1.0 |
| aa | second | 75 | 23% | - | - | - | - | 100% | 0% | 0.00 ± 0.00 | - | - | - | - | 1.0 |
| aa | **both seats** | 75 + 75 | - | - | - | - | - | 100% | 0% | 0.00 ± 0.00 | - | - | - | - | 1.0 |

Who made the first damaging attack (sp, both seats, 150 games): Entei ex 100%.

Who made the first 30+ attack (sp, both seats, 150 games): Entei ex 100%.

Who led (Active at the start) (sp, both seats, 150 games): Entei ex 100%.

Games in which the scripted pilot retreated at least once: 0%.

Most often dead at end of turn (sp): Flame Patch 29%, Copycat 26%, Rainbow Cave 22%, Pokémon Center Lady 19% of turn-ends.

Most often dead at end of turn (aa): Flame Patch 60%, Lucky Ice Pop 17%, Pokémon Center Lady 11% of turn-ends.

Engine game seeds (one per game): sp: 21,002,070,000 to 21,002,070,149, aa: 21,002,075,000 to 21,002,075,149. The won column is against a single Pokémon that never plays a Trainer and means little; read the tempo columns. The `aa` opponent also never plays a card, so its hand grows and Copycat draws more than it would on the ladder.

## 6. Coverage flag

Cards that hit known blind spots of the engine's bots, so the simulator's numbers for this list are less trustworthy where these cards matter:
- **(a)** text names the opponent's hand or deck: blind k3 leaves the move unpriced (engine/src/observation.rs `hidden_continuation_reason`).
- **(b)** attack effect outside the damage estimator: the bots value the attack at printed damage (engine/src/players/value_functions.rs `estimated_attack_damage_ex`, fallback `_ => fixed`; effect texts read from engine/src/actions/effect_mechanic_map.rs). "b-" = the effect does not change damage (status, self-damage), so only its side effect is unvalued.
- **(c)** played from hand: the opponent-reply search (the `o` tiers such as b3o3n4; k3 has no reply ply) only considers attacks, retreats, Abilities, draws and the turn's Energy (engine/src/players/expectiminimax_player.rs `is_public_information_action`).

| card | flags |
|---|---|
| Entei ex ×2 | **(c)** a copy benched from hand changes the board (passive Ability): not seen by the reply search |
| Copycat ×2 | **(a)** card names the opponent's hand or deck: blind k3 leaves it unpriced |
| Pokémon Center Lady ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Sabrina ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Cyrus ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Lucky Ice Pop ×2 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Flame Patch ×2 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Repel ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Giant Cape ×2 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Rainbow Cave ×2 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Starting Plains ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |

**Reading:** k3 leaves Copycat unpriced. Bot numbers for this list are untrusted to that extent.

## Draw, search and Energy effects in this list

What the solitaire model plays (card text from lib/card.py):

| card | text | model |
|---|---|---|
| Entei ex ×2 | Ability Legendary Pulse: At the end of your turn, if this Pokémon is in the Active Spot, draw a card. | ability modeled: end of turn draw 1 (if Active) |
| Professor's Research ×2 | Draw 2 cards. | modeled: draw 2 |
| Copycat ×2 | Shuffle your hand into your deck. Draw a card for each card in your opponent's hand. | modeled: shuffle hand in, draw opponent-hand-size |
| Pokémon Center Lady ×1 | Heal 30 damage from 1 of your Pokémon, and it recovers from all Special Conditions. | ignored: not a draw, search, evolution or Energy effect |
| Sabrina ×1 | Switch out your opponent's Active Pokémon to the Bench. (Your opponent chooses the new Active Pokémon.) | ignored: not a draw, search, evolution or Energy effect |
| Cyrus ×1 | Switch in 1 of your opponent's Benched Pokémon that has damage on it to the Active Spot. | ignored: not a draw, search, evolution or Energy effect |
| Lucky Ice Pop ×2 | Heal 20 damage from your Active Pokémon. If you healed any damage in this way, flip a coin. If heads, put this Lucky Ice Pop into your hand instead of the discard pile. | ignored: not a draw, search, evolution or Energy effect |
| Flame Patch ×2 | Attach a [R] Energy from your discard pile to your Active [R] Pokémon. | modeled: attach 1 [R] from discard to the Active |
| Repel ×1 | Switch out your opponent's Active Basic Pokémon to the Bench. (Your opponent chooses the new Active Pokémon.) | ignored: not a draw, search, evolution or Energy effect |
| Poké Ball ×1 | Put a random Basic Pokémon from your deck into your hand. | modeled: search 1 random Basic Pokémon to hand |
| Giant Cape ×2 | The Pokémon this card is attached to gets +20 HP. | ignored: not a draw, search, evolution or Energy effect |
| Rainbow Cave ×2 | Once during each player's turn, that player may discard the Energy that has been generated in their Energy Zone. If they do, the next Energy is produced. | modeled: discard the generated Energy for a new one (feeds discard-pile Energy) |
| Starting Plains ×1 | Each Basic Pokémon in play (both yours and your opponent's) gets +20 HP. | ignored: not a draw, search, evolution or Energy effect |

## How the solitaire pilot plays

Setup: all Basics in hand go into play (Active: the `--lead` Basic if given, else a Basic whose Ability works from the Active Spot, else one outside the main line with the most HP). Each own turn: draw; then repeat until nothing changes: play a Stadium that does something here, use it, play Items (Poké Ball and other searches take a random matching card, as printed; Rare Candy on the main line first), bench Basics the plan needs (others only while the Bench has room to spare), evolve (main line first), use draw Abilities, attach Tool pieces; when nothing else moves, one Supporter: a search that finds a missing piece, else a draw, else Copycat when the hand is small and holds nothing needed (Copycat assumes the opponent holds 4 cards). Then the turn's Energy (random among the declared types) goes to the main line first, then other combo attackers, else the Active; Energy from the discard or from Abilities is added; then the check; an Ability that ends the turn is used only when the main attacker cannot attack. No opponent, no knockouts, no retreat, no attacks (attack effects that set up, such as Flock or Glittering Gift, are ignored), no coin-flip Supporters. Hand limit 10.

Generated by `lib/consistency.py` in 22 s; solitaire seed 21,002,070,000 (Python random, same deals across variants).
