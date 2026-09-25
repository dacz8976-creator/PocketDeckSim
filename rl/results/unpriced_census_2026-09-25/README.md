Decision this informs: what the A1 coverage flag and kp adoption should treat as k3's blind spots. In k3 that is four cards: Copycat (in all eight table lists), Darkness Claw, Team Rocket's Boss and Mars. k3 scores them as doing nothing and rarely plays them. kp3 prices all four. What k3 and kp3 still both leave unpriced is Sceptile's Quick Growth and the setup reveal. Engine: census program at f8dfaf5. Its kp3 plays the same games as 858b6fe and as c7cb688, which adds the audited-text list (checked on 60 games).

Seeds: the table's deals only. 72,000,000 + pairing × 10,000 + i, i < 200, all 28 pairings, even i = first-named deck in seat 0.

# Unpriced-branch census (B2a), Sept 25

`engine/examples/unpriced_census.rs` replays the table's games with the same loop as the legality scan. Its k3 games are the k3 table's games: 5,600 of 5,600 move fingerprints match `../per_game_table_2026-09-25/k3_500.jsonl`. At every decision with more than one move, the search reports the branches it could not price and why. This census counts them per deck.

Three kinds of reason:

- **Hidden.** The branch needs the opponent's hidden cards, so it is scored as the position before it: as if nothing happened. "Itself" means the candidate move is that branch, for example Copycat played now.
- **Boundary.** At the end of the searched turn, the public-reply certificate declined, so the position gets k3's ordinary static value. This is on 91–98% of decisions for both bots. It is how k3 ends every search, not a blind spot in these decks.
- **Other.** The opponent's face-down setup, and private pending choices.

## The moves k3 scores as doing nothing

| deck | decisions (k3) | k3: such a move was available / was chosen | kp3: available / chosen | how often k3 plays the card when it's available |
|---|---:|---:|---:|---|
| Altaria | 32,936 | 38.5% / 2.3% | 5.9% / 0.1% | Copycat 6.5% of 10,909 |
| Blaziken | 27,829 | 39.5% / 1.6% | 2.9% / 0.1% | Copycat 4.2% of 10,257 |
| Hydreigon | 35,745 | 45.9% / 4.3% | 3.2% / 0.0% | Copycat 6.9% of 12,632; Darkness Claw 13.6% of 4,796 |
| Lucario | 26,891 | 36.3% / 1.4% | 3.2% / 0.1% | Copycat 3.7% of 9,051 |
| Sceptile | 29,516 | 22.7% / 0.6% | 0.7% / 0.0% | Copycat 2.7% of 6,500 |
| Suicune | 38,299 | 42.1% / 1.9% | 3.4% / 0.2% | Copycat 2.7% of 10,418; Team Rocket's Boss 3.9% of 9,372 |
| Vespiquen | 35,100 | 37.1% / 1.5% | 3.9% / 0.2% | Copycat 3.9% of 11,775 |
| Weezing | 31,549 | 43.1% / 1.4% | 4.0% / 0.1% | Copycat 3.2% of 10,143; Mars 1.2% of 6,559 |

"Available" is the share of the deck's decisions where one of its candidate moves was itself scored as nothing, and "chosen" is the share where the bot then played one. kp3 plays different games, so its decision counts differ a little (28,885 to 37,893).

What this shows:

- **Under k3 the text rule is the whole story.** Every "itself" entry with a card name is the opponent-hand-or-deck text rule, and it's the same four cards: Copycat, Darkness Claw, Team Rocket's Boss and Mars. One is available in 23–46% of a deck's decisions. k3 plays them rarely: Copycat 3–7% of the times it's available, Mars 1%. When it does play one, the pick comes from tie-breaks and moves that score no better, not from knowing what the card does.
- **kp3 prices all four.** What's left under kp3, 0.7–5.9% of decisions, is two EndTurn cases that don't depend on card text:
  - **Setup.** Ending the setup turn while the opponent's starting Pokémon are still face-down (every deck, 0 chosen by design).
  - **Quick Growth.** When Sceptile's Active has Quick Growth (B3b 001: at the end of the opponent's turn, put a random card from the deck that evolves from it onto it), ending your turn against it is left unpriced, because it searches a deck the searcher can't see. This is the whole of the leftover in Sceptile's opponents' rows. k3 and kp3 leave it the same.
- **What pricing does not give.** kp3 prices these effects' public parts: Darkness Claw's damage, Copycat's draw count, Mars's draw count. It gives no credit for a payoff that depends on what the hidden cards are. Penny, Portrait, Team Rocket's Boss and similar cards are priced only for their public parts.

## Files

- `census_{k3,kp3}.txt`: the per-deck readout. `census_{k3,kp3}.json`: every (candidate, reason) with offered and chosen counts, plus every unpriced branch with its count.
- `games_{k3,kp3}.jsonl`: one line per game with its move fingerprint (the k3 games match the k3 table's).
- `run_census.sh`: the command (census program built at f8dfaf5).
