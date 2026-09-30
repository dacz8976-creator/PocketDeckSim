Decision this informs: none. This is a bounded diagnosis, and nothing gates on it (the Fable coordinator via Dustin, Sept 30). There is no engine change, no `players/` change, no table game and no candidate proposed.

Seeds: none new. Every game here is a floor game (`../floor_dustin_2026-09-30/`), replayed on its own seed exactly as `floor.py` played it.

# Why km3 almost never plays Iris or Team Rocket's Goo-zooka

The floor run flags two cards km3 rarely plays:
- Iris in Dustin's deck 11: 233 of 3,068 chances, 7.6%.
- Team Rocket's Goo-zooka in decks 14 and 15: 4.1% and 3.8%.

This replays 40 of deck 11's floor games and 20 each of decks 14 and 15's at the official engine's source (main `d363ba8`). At every decision where the card was offered, it records km3's own score for each move.

## In plain words

- **Iris: km3 plays it exactly when it matters.**
  - Iris adds a point only when Haxorus knocks out the opponent's Active that turn.
  - In these 40 games that could change a result on 3 turns: a Haxorus knockout of an ex from 0 points, where Iris makes it the third point. km3 played Iris on all 3 and won each game on that turn.
  - On the 83 turns it held Iris back, Haxorus wasn't in play (78), or had too few Energy to attack (2), or attacked without a knockout (1). On the other 2 its knockout already won the game.
  - The low rate is how seldom Haxorus attacks in this deck, not a blind spot.
- **Goo-zooka: km3's score never sees what it does.**
  - Playing it changes km3's score by exactly 0 on every chance turn. Its effect lands on the opponent's turn, and the score has no term for the opponent's Retreat Cost.
  - The card leaving the hand costs 1 point of score, so km3 always prefers to keep it.
  - In 10 hand-picked turns where it wasn't played, a competent player would have played it in 7. In each, the opponent's Active, often damaged, retreated the next turn with exactly its Retreat Cost in Energy. Raising the cost by 1 would have stranded it, or spent their attachment and cost them their attack.

## Question 1: what km3 played instead, and what its score said the card was worth

**Chance turns** are the floor's own count: turns where playing the card was offered. For Iris, a Supporter, turns where another Supporter was played are left out. In every replayed game the chance turns and uses equal the floor's per-game count.

| | Iris (deck 11) | Goo-zooka (deck 14) | Goo-zooka (deck 15) |
|---|---|---|---|
| chance turns in the replayed games | 88 | 84 | 63 |
| played | 5 | 1 | 3 |
| not played | 83 | 83 | 60 |

**What km3 played at the card's first offer in a turn it didn't play it:**
- Iris: Attach 17, Evolve 17, a Basic to the Bench 15, Poké Ball 9, Lucky Ice Pop 7, Rainbow Cave's effect 7, an Ability 3, an attack 3, Retreat 2, end the turn 2, Rainbow Cave 1.
- Deck 14: Attach 19, Evolve 18, Poké Ball 10, a Basic to the Bench 10, Professor's Research 5, Retreat 5, an attack 4, Team Rocket's Researcher 4, Copycat 2, end the turn 2, Sightseer 2, Cyrus 1, Elegant Cape 1.
- Deck 15: Evolve 11, Professor's Research 7, a Basic to the Bench 7, Attach 7, an attack 5, Poké Ball 5, Sabrina 5, Copycat 4, Retreat 4, Lisia 2, Pokémon Center Lady 2, Cyrus 1.

The turn went on to attack in 35 (Iris), 53 and 39 of these turns, with a knockout in 10, 11 and 15.

**The card's score minus the best move's score** (km3's root scores: the same scores its real decision used):

| where | gap | Iris | deck 14 | deck 15 |
|---|---|---|---|---|
| first offer in the turn | 0 (a tie) | 5 | 2 | 6 |
| | −1 | 36 | 20 | 15 |
| | −2 to −20 | 8 | 8 | 6 |
| | below −20 | 34 | 53 | 33 |
| last offer in the turn | 0 (a tie) | 7 | 2 | 6 |
| | −1 | 76 | 67 | 49 |
| | below −20 | 0 | 14 | 5 |

At the last offer km3's move was:
- Iris: end the turn 48, an attack 35;
- deck 14: an attack 52, end the turn 28, Copycat 3;
- deck 15: an attack 37, end the turn 18, Copycat 5.

**Reading the gaps:**
- **−1 is the card leaving the hand.** km's score counts each card in hand as +1 (`(my.hand_size − opp.hand_size) × hand_size`, `parametric_value_function_ex6`). A card whose effect scores 0 (question 2) is worth exactly −1 to play.
- **The ties at the last offer** are all turns whose best line already wins (score 100,000). There the −1 no longer counts.
- **The larger gaps come from the search, not the card.** km3 looks three moves ahead, within its own turn (`km3`: depth 3; the opponent's reply isn't searched). Playing the card uses one of the three, so a line that needs all three, such as attach, retreat, attack, no longer fits in the search.
  - By the last offer the gap is back to −1 in every Iris turn.
  - The 19 Goo-zooka turns still below −20 at the last offer come just before Copycat (8) or Entrap (11):
    - Copycat shuffles the hand into the deck, so the card was never offered after it.
    - Entrap is itself three moves: the attack, choosing the new Active, and its damage.
- **The 4 times km3 did play Goo-zooka:**
  - 3 were exact ties: deck 15's 7601 turn 3, 8100 turn 7 and 8600 turn 7.
  - The fourth (deck 14, 11100 turn 6) scored best by 436, just before Copycat. The card's own effect scored 0 there too, so the gain came from the line the search found after it, not from the card.
- **The 5 times km3 played Iris:**
  - 3 were the winning Haxorus knockouts above. There the search scored Iris as a win (100,000) and every move without it lower.
  - 2 did nothing (8601 turn 9 and 8602 turn 5). Both were exact ties with another move, and there was no Haxorus attack.

## Question 2: does the score read the card's effect at all?

**No, for both cards. There's no flat +10 either: that goes only to a Tool on the Active.**

- **Measured:** at the first and the last offer of every chance turn (88, 84 and 63 turns), km's score on the real position after really playing the card, minus its score after only moving the card from hand to the discard pile. It is **0.0 in every turn**.
- **Iris:** its point exists only if Haxorus knocks out the Active this turn. The score counts points, so km3 sees Iris only when its three-move look-ahead reaches that knockout in the same turn.
  - The census (`../trainer_audit_2026-09-25/census_table.md`) says "read (the search plays it out)", and that it doesn't land after the turn.
  - That is what happened here: all 3 turns where Iris mattered were scored as wins and played.
- **Goo-zooka:** its effect is the opponent's Retreat Cost during their next turn.
  - km's score has a term for your own Active's Retreat Cost (`−my.active_retreat_cost`) and none for the opponent's. km3's search stops the moment its turn ends (`opponent_ply: 0`), so it never reaches the opponent's retreat.
  - The census calls it "partly read", but only through Whimsicott ex's Grass Knot (deck 12). No attack in decks 14 or 15 reads the opponent's Retreat Cost (Boost Dash, Entrap, Mumble, Ambush, Spinning Attack, Mach Bolt, Zzzap, Stampede). So in these two decks its effect is not read at all.
- **The census was taken on kp3.** km adds the defender's damage cuts and the Stadium bonus to the clock. Neither touches these two cards, and the measured 0.0 agrees.

## Question 3: 20 turns where the card was offered and not played

These were hand-picked from the traces:
- **Iris:** all 5 turns with a Haxorus in play, 3 of the 8 turns where another attacker knocked out, and 2 ordinary turns.
- **Goo-zooka:** turns where the opponent retreated the next turn or a gust was played, picked to show both answers.

So the 7 of 10 for Goo-zooka is not a rate. The judgment in each line is mine, read from the turn's trace and the opponent's next turn.

| card | deck | opponent | seat | seed | turn | play it? | why |
|---|---|---|---|---|---|---|---|
| Iris | 11 | t-altaria | 0 | 7101 | 2 | no | No Haxorus in play (Dratini alone), so no Haxorus attack this turn. |
| Iris | 11 | t-altaria | 0 | 7103 | 10 | no | No Haxorus in play (Axew, Dratini, Axew). |
| Iris | 11 | t-altaria | 0 | 7106 | 8 | no | Haxorus is Active with 0 Energy; one attachment can't pay Frenzied Blade's 3. |
| Iris | 11 | t-altaria | 0 | 7106 | 10 | no | Haxorus reached only 2 Energy this turn (Dragon's Blessing plus the attachment); Frenzied Blade needs 3. |
| Iris | 11 | t-lucario | 0 | 10100 | 7 | no | The knockout was Dragonair's Draconic Whip on Hitmonlee; Iris counts only Haxorus. |
| Iris | 11 | t-sceptile | 0 | 11102 | 9 | no | Dragonair's Draconic Whip knocked out Butterfree; Iris counts only Haxorus. |
| Iris | 11 | t-altaria | 1 | 7602 | 11 | no | Archaludon's Protect Charge took the winning point; Iris counts only Haxorus. |
| Iris | 11 | t-vespiquen | 1 | 13603 | 8 | no | Frenzied Blade (50 + 20 × 4 Benched) left Teal Mask Ogerpon ex at 30hp: no knockout, so nothing to add. |
| Iris | 11 | t-blaziken | 0 | 8102 | 12 | no difference | Haxorus's knockout of Torchic was the third point; the game is won with or without Iris. |
| Iris | 11 | t-suicune | 0 | 12101 | 10 | no difference | Haxorus knocked out Suicune ex from 2 points; won without Iris. |
| Goo-zooka | 14 | t-hydreigon | 0 | 9102 | 4 | yes | Thieving Incisors left Deino (Retreat Cost 1) with 0 Energy. Next turn they attached one and retreated into Hydreigon, which knocked out Comfey. At cost 2 that retreat fails. |
| Goo-zooka | 14 | t-suicune | 1 | 12600 | 4 | yes | Chien-Pao ex, down to 60hp and 1 Energy, retreated next turn and Suicune ex attacked. At cost 2 it stays in front of Raticate ex's Boost Dash (70), or the attachment goes to the retreat and Suicune can't attack. |
| Goo-zooka | 14 | t-hydreigon | 1 | 9600 | 3 | yes, mildly | Deino (1 Energy, cost 1) retreated next turn into Bombirdier, which then attached and hit Comfey for 30. At cost 2 the retreat takes their attachment and Bombirdier can't attack. |
| Goo-zooka | 15 | t-blaziken | 0 | 8101 | 3 | yes | Sabrina brought up Torchic and Ambush left it at 20hp. Next turn they attached, retreated into Castform and knocked out Rattata. After Sabrina, Goo-zooka makes that retreat cost 2 with 1 Energy. |
| Goo-zooka | 15 | t-sceptile | 1 | 11602 | 4 | yes | Sabrina brought up Grovyle and Mach Bolt left it at 30hp. They attached (Electromagnetic Wall: 10hp) and retreated into Butterfree, which hit Jolteon ex for 60. At cost 2 Grovyle is stuck at 10hp. |
| Goo-zooka | 15 | t-vespiquen | 1 | 13600 | 6 | yes | Mach Bolt left Shuckle ex at 40hp with 1 Energy. It retreated and the fresh Shuckle ex attacked. At cost 2 the damaged ex stays in, or the attachment goes to the retreat and nothing attacks. |
| Goo-zooka | 15 | t-altaria | 0 | 7102 | 2 | yes | Igglybuff (cost 0) retreated free into Espeon, which took the attachment and knocked out Oricorio. At cost 1 the attachment pays the retreat and Espeon can't attack. |
| Goo-zooka | 14 | t-altaria | 0 | 7100 | 9 | no | Their Active, Mega Altaria ex, is their attacker and stayed in; its Mega Harm won the next turn whatever its Retreat Cost. |
| Goo-zooka | 14 | t-blaziken | 0 | 8103 | 4 | no (can't) | Entrap brought up Torchic, and nothing can be played after an attack. Played before it, Goo-zooka lands on Mega Blaziken ex, not Torchic. |
| Goo-zooka | 15 | t-weezing | 1 | 14600 | 4 | no | Sabrina brought up Hoopa ex with 0 Energy and Retreat Cost 2; one attachment can't pay 2, so it was stuck anyway. |

**Across all 143 Goo-zooka turns not played:**
- the opponent retreated on its next turn in 30 (13 in deck 14, 17 in deck 15);
- in 25 of those its Active held exactly its printed Retreat Cost in Energy, so +1 would have made them attach to it first or stay;
- a gust was played that turn in 24 (Cyrus, Sabrina or Entrap).

These are counts, not judged turns.

## How it was done

1. **The deals** (`select_deals.py`, `deals.txt`). A fixed rule over the floor's per-game files: games where the card had more chances than uses. For each deck, one game per opponent per pass, seats alternating by pass, until the quota: 40 for Iris, 20 each for Goo-zooka's two decks, 80 in all. That is within the 40 per card.
   - They were picked from 1,172, 1,319 and 1,327 qualifying games.
2. **The replay** (`trainer_diag.rs`, `diag_helper.rs`). This is a program in a scratch copy of the engine at `d363ba8`, the source of `rl/engine-2026-09-30/deckgym`. Nothing in the repository's `engine/` changed.
   - It plays km3 against km3 as `deckgym simulate --seed-stream` does: `create_players`, `Game::new` on the game's seed, `play_tick`.
   - At each decision of the deck's seat where the card is offered, it asks for km3's root score of every offered move. `diag_km_root_scores` uses the same observation, determinization seed and search seed as the real decision, under the same public pricing.
   - It also computes the static effect (question 2) and prints the boards, the rest of the turn and the opponent's moves.
   - Build: `git archive d363ba8 engine | tar -x`, append `diag_helper.rs` to `engine/src/players/expectiminimax_player.rs`, copy `trainer_diag.rs` to `engine/examples/`, then `cargo build --release --example trainer_diag`.
   - Run from the repository root, once per line of `deals.txt`: `trainer_diag --deck decks/dustin/<deck>.txt --opponents decks/screen/opponents --card "<card>" --games "<games>"`. The output is gzipped into `rows_<deck>.jsonl.gz`.
3. **The analysis** (`analyze.py`). It writes `turns.jsonl`, one row per chance turn, and prints `summary_output.txt`.

## Checks

- All 80 replays end as the floor's per-game files say: points, turns and winner.
- Each game's chance turns and uses equal the floor's own count, its `flagged` field.
- At all 844 probed decisions, the move km3 played has the best root score. In 21 of them two copies of the same move tie, and km3 picks the other copy.
- `analyze.py` asserts all three before it writes anything.

## Limits

- 80 games, picked by a fixed rule from games where the card went unplayed. The counts describe these games; they are not the floor's rates.
- The 20 judgments are one reader's, from the traces. They say what the opponent actually did next, not everything it could have done: a switching card in their hand, for example, could have undone Goo-zooka.
- The static effect is read one move deep on the real position. Anything the card changes later reaches km3 only through its search, and question 1's scores cover that part.
- This finds where the score is blind. It doesn't test any change, and none is proposed.

## Files

- `README.md`: this note.
- `select_deals.py`, `deals.txt`: the deals.
- `trainer_diag.rs`, `diag_helper.rs`: the replay program and the helper it needs.
- `rows_11-archaludon-haxorus-dragonair.jsonl.gz`, `rows_14-comfey-raticate-hypno.jsonl.gz`, `rows_15-jolteon-oricorio-raticate.jsonl.gz`: the replay's rows.
- `analyze.py`, `turns.jsonl`, `summary_output.txt`: the analysis.
- `sha256.txt`: hashes of the files and of the scratch `trainer_diag` program.
