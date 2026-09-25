# Consistency: brew-01-arceus-crobat-xatu

`decks/brews/brew-01-arceus-crobat-xatu.txt` · Energy: Psychic · main attacker: Arceus ex (Basic), Ultimate Force [CCC] 70 · combo: Arceus ex + Crobat + Xatu

Ladder record: 1-3

**In one line:** brew-01-arceus-crobat-xatu: one-Basic opening 52%; Arceus ex online by own T3 0% first / 74% second (T4 84%/84%); combo by T4 45%/45%; goldfish (scripted pilot v aa, seat-balanced): 1.32 pts conceded before the first 30+ damage attack (by own T3 in 24%), Arceus ex attacks by T4 46% with 1.32 conceded first, 2.4 dead cards/turn; unpriced-text cards (a): 0

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
| Arceus ex | 17% | | Arceus ex | 49% |
| Zubat | 17% | | Zubat | 49% |
| Natu | 17% | | Crobat | 43% |
|  |  | | Natu | 49% |
|  |  | | Xatu | 43% |

## 2. Main attacker online

"Online" = Arceus ex in play (Active or Bench) with the Energy for Ultimate Force [CCC] attached, at the moment you would attack. Fastest possible without acceleration: own turn 4 going first, 3 going second.

| | going first T2 | T3 | T4 | going second T2 | T3 | T4 |
|---|---|---|---|---|---|---|
| Arceus ex online | 0% | 0% | 84% | 0% | 74% | 84% |
| Arceus ex in play (any Energy) | 84% | 90% | 94% | 84% | 90% | 95% |
| online, draw/search cards not played | 0% | 0% | 63% | 0% | 56% | 62% |

Where "in play" is well above "online", Energy is the limit (one a turn); where both are low, finding the cards is the limit. The last row shows what the list's draw and search cards add.

## 3. Stage 2 in play

Stage 2 cards: Crobat. Rare Candy in the list: yes.

| | going first T3 | T4 | going second T3 | T4 |
|---|---|---|---|---|
| any Stage 2 in play (list as built) | 51% | 65% | 51% | 65% |
| same deals, Rare Candy never played | 0% | 0% | 0% | 0% |

## 4. Combo assembled

Pieces: Arceus ex + Crobat + Xatu. A Pokémon piece counts when it is in play; a Trainer piece when it is in hand or already played.

| by own turn | 2 | 3 | 4 | 5 |
|---|---|---|---|---|
| going first | 10% | 27% | 45% | 64% |
| going second | 11% | 27% | 45% | 64% |

Each piece on its own (going first / second):

| piece | by T3 | by T5 |
|---|---|---|
| Arceus ex | 90% / 90% | 97% / 97% |
| Crobat | 51% / 51% | 77% / 77% |
| Xatu | 69% / 70% | 87% / 87% |

### Drawing each card

Each card, drawn or fetched at least once by own turn 3 / by own turn 5 (the opening hand counts; going first, the list's draw and search cards played; "no draw" = the same deals with them left in hand):

| card | copies | by T3 | by T5 | by T3, no draw | by T5, no draw |
|---|---|---|---|---|---|
| Arceus ex | 2 | 90% | 97% | 68% | 78% |
| Zubat | 2 | 95% | 99% | 69% | 79% |
| Crobat | 2 | 77% | 89% | 64% | 76% |
| Natu | 2 | 95% | 99% | 67% | 77% |
| Xatu | 2 | 77% | 90% | 64% | 76% |
| Rare Candy | 2 | 77% | 90% | 64% | 75% |
| Professor's Research | 2 | 65% | 77% | 65% | 76% |
| Poké Ball | 2 | 76% | 88% | 65% | 76% |
| Lisia | 1 | 49% | 62% | 39% | 49% |
| Will | 1 | 50% | 66% | 39% | 49% |
| Giant Cape | 1 | 50% | 66% | 39% | 49% |
| Cyrus | 1 | 50% | 66% | 39% | 50% |

## 5. Goldfish against the engine

The real engine (rules4: rl/addon-0.7.2/deckgym and the pdl_rl_env 0.7.2 add-on built from the same rules) plays this list against `decks/research/weezing.txt` piloted by the engine's `aa` bot (attach-and-attack: it puts its Energy on the Active and attacks whenever it can, and nothing else). Because the engine lists End Turn first among the legal moves and `aa` takes the first move when it cannot attach or attack, `aa` never benches a Pokémon, not even at setup, and never plays a Trainer: the opponent is one Active Pokémon, and knocking it out wins. That makes it a fixed clock (here mostly Hoopa ex: 30 a turn from its first Energy, 100 from its third), not a real opponent.

Two pilots for this list. **sp** (scripted pilot, the main reading): the solitaire model's priorities playing the real engine through the add-on. It leads with a Basic whose Ability works from the Active Spot (Pyukumuku's Innards Out, Entei ex's Legendary Pulse), else one outside the main line with the most HP (`--lead` overrides); benches Basics, plays the draw, search, Rare Candy and Energy cards, evolves, puts Energy on the main line, attaches defensive Tools, heals a hurt Active, uses Abilities that draw, search, add Energy, damage the opposing Active (Crobat's Cunning Link) or give it a Special Condition (Meowstic's Perplexing Ears), plays a Supporter such as Team Rocket's Master Plan when the Active's attack gains from the Condition this turn, and attacks for the most damage. When a main or combo Pokémon is Active and the turn's Energy lets it attack this turn for as much as a Benched one could, the Energy goes on it. Otherwise, when a Benched main or combo Pokémon can attack and the Active cannot (or the Benched one does 40+ more and the Active is outside the main line), the turn's Energy goes on the Active until it can retreat, and it retreats. **aa** (the brief's pilot): the engine's own bot on this side too, so both sides have a single Pokémon and the game ends at the first knockout; its "points conceded" can never exceed what one knockout gives. `et` ends every turn at once and never attacks, so it is not used. 150 games per pilot; the coin decides who goes first, so the seats get different numbers of games; the "both seats" row is the plain mean of the two seat means.

"30+ attack" (the headline tempo reading) = the list's first attack that did 30 or more damage to the opposing Active or knocked it out (Poison or Burn the attack applied counts at the next Checkup; Poison or Burn that was already there does not). "Damaging attack" = the first attack that did any damage, chip damage included (Hatenna's Stampede for 10 counts). "Conceded" = the opponent's points at that moment (or at the end if it never came); ± is the standard error of the mean over these games: simulation noise only, nothing about the ladder. "Main attacks" = the first attack by the main attacker. "Dead" = cards in hand at the end of the turn that the rules did not let you play then (own turns 1-4; a second Supporter after one was played counts as dead; cards that need an opposing Bench, such as Cyrus and Sabrina, are left out because this opponent never has one).

| pilot | seat | games | won | 30+ attack by T3 | by T4 | never | conceded before it | damaging attack by T3 | never | conceded before it | main attacks by T3 | by T4 | never | conceded before main | dead cards / turn |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sp | first | 90 | 64% | 1% | 22% | 60% | 1.73 ± 0.13 | 10% | 52% | 1.60 ± 0.14 | 0% | 20% | 62% | 1.76 | 2.3 |
| sp | second | 60 | 87% | 47% | 72% | 20% | 0.92 ± 0.14 | 75% | 5% | 0.40 ± 0.09 | 45% | 72% | 20% | 0.88 | 2.5 |
| sp | **both seats** | 90 + 60 | - | 24% | 47% | 40% | 1.32 ± 0.10 | 42% | 29% | 1.00 ± 0.08 | 22% | 46% | 41% | 1.32 | 2.4 |
| aa | first | 83 | 7% | - | - | - | - | 59% | 34% | 0.57 ± 0.09 | - | - | - | - | 1.8 |
| aa | second | 67 | 9% | - | - | - | - | 100% | 0% | 0.00 ± 0.00 | - | - | - | - | 1.7 |
| aa | **both seats** | 83 + 67 | - | - | - | - | - | 80% | 17% | 0.28 ± 0.05 | - | - | - | - | 1.8 |

Who made the first damaging attack (sp, both seats, 150 games): Arceus ex 49%, (none) 33%, Zubat 10%, Natu 8%.

Who made the first 30+ attack (sp, both seats, 150 games): Arceus ex 54%, (none) 44%, Xatu 2%.

Who led (Active at the start) (sp, both seats, 150 games): Zubat 46%, Natu 39%, Arceus ex 15%.

Games in which the scripted pilot retreated at least once: 20%.

Most often dead at end of turn (sp): Crobat 26%, Rare Candy 24%, Xatu 19%, Will 9% of turn-ends.

Most often dead at end of turn (aa): Rare Candy 50%, Crobat 48%, Xatu 48% of turn-ends.

Engine game seeds (one per game): sp: 21,002,020,000 to 21,002,020,149, aa: 21,002,025,000 to 21,002,025,149. The won column is against a single Pokémon that never plays a Trainer and means little; read the tempo columns. The `aa` opponent also never plays a card, so its hand grows and Copycat draws more than it would on the ladder.

## 6. Coverage flag

Cards that hit known blind spots of the engine's bots, so the simulator's numbers for this list are less trustworthy where these cards matter:
- **(a)** text names the opponent's hand or deck: blind k3 leaves the move unpriced (engine/src/observation.rs `hidden_continuation_reason`).
- **(b)** attack effect outside the damage estimator: the bots value the attack at printed damage (engine/src/players/value_functions.rs `estimated_attack_damage_ex`, fallback `_ => fixed`; effect texts read from engine/src/actions/effect_mechanic_map.rs). "b-" = the effect does not change damage (status, self-damage), so only its side effect is unvalued.
- **(c)** played from hand: the opponent-reply search (the `o` tiers such as b3o3n4; k3 has no reply ply) only considers attacks, retreats, Abilities, draws and the turn's Energy (engine/src/players/expectiminimax_player.rs `is_public_information_action`).

| card | flags |
|---|---|
| Arceus ex ×2 | **(c)** a copy benched from hand changes the board (passive Ability): not seen by the reply search |
| Crobat ×2 | **(c)** evolves from hand: the opponent's reply search never sees the evolution |
| Xatu ×2 | **(b)** attack Life Drain: damage-changing effect, mechanic CoinFlipSetOpponentActiveRemainingHp has no damage estimator; the bots value it at printed 0<br>**(c)** evolves from hand: the opponent's reply search never sees the evolution |
| Rare Candy ×2 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Lisia ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Giant Cape ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Cyrus ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |

**Reading:** the damage of Xatu is read as printed. Bot numbers for this list are untrusted to that extent.

## Draw, search and Energy effects in this list

What the solitaire model plays (card text from lib/card.py):

| card | text | model |
|---|---|---|
| Rare Candy ×2 | Choose 1 of your Basic Pokémon in play. If you have a Stage 2 card in your hand that evolves from that Pokémon, put that card onto the Basic Pokémon to evolve it, skipping the Stage 1. You can't use this card during your first turn or on a Basic Pokémon that was put into play this turn. | modeled: Basic straight to Stage 2 (not own turn 1, not a Basic played this turn) |
| Professor's Research ×2 | Draw 2 cards. | modeled: draw 2 |
| Poké Ball ×2 | Put a random Basic Pokémon from your deck into your hand. | modeled: search 1 random Basic Pokémon to hand |
| Lisia ×1 | Put 2 random Basic Pokémon with 50 HP or less from your deck into your hand. | modeled: search 2 random Basic Pokémon (HP<=50) to hand |
| Will ×1 | The next time you flip any number of coins for the effect of an attack, Ability, or Trainer card after using this card on this turn, the first coin flip will definitely be heads. | ignored: not a draw, search, evolution or Energy effect |
| Giant Cape ×1 | The Pokémon this card is attached to gets +20 HP. | ignored: not a draw, search, evolution or Energy effect |
| Cyrus ×1 | Switch in 1 of your opponent's Benched Pokémon that has damage on it to the Active Spot. | ignored: not a draw, search, evolution or Energy effect |

## How the solitaire pilot plays

Setup: all Basics in hand go into play (Active: the `--lead` Basic if given, else a Basic whose Ability works from the Active Spot, else one outside the main line with the most HP). Each own turn: draw; then repeat until nothing changes: play a Stadium that does something here, use it, play Items (Poké Ball and other searches take a random matching card, as printed; Rare Candy on the main line first), bench Basics the plan needs (others only while the Bench has room to spare), evolve (main line first), use draw Abilities, attach Tool pieces; when nothing else moves, one Supporter: a search that finds a missing piece, else a draw, else Copycat when the hand is small and holds nothing needed (Copycat assumes the opponent holds 4 cards). Then the turn's Energy (random among the declared types) goes to the main line first, then other combo attackers, else the Active; Energy from the discard or from Abilities is added; then the check; an Ability that ends the turn is used only when the main attacker cannot attack. No opponent, no knockouts, no retreat, no attacks (attack effects that set up, such as Flock or Glittering Gift, are ignored), no coin-flip Supporters. Hand limit 10.

Generated by `lib/consistency.py` in 32 s; solitaire seed 21,002,020,000 (Python random, same deals across variants).
