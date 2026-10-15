# Ladder validation: do the bots' numbers hold on his ladder?

Draft v3 for `rl/results/ladder_validation/`. Agents do all the bookkeeping from the existing Ladder Log; Dustin logs
nothing new. Full rules, tables, commands and sources: `DETAILS.md`.

## The question
For one deck version: did his ladder record land where the bots said? Whether the simulator ranks decks well is a
separate question that needs many decks (see "Ranking decks").

## Who plays what
- In every bot run, **km3 plays the 8 panel lists** (fixed tournament lists).
- The **frozen kx3** (strong bot) knows those 8 lists, so its number is the **optimistic end**. km3 against km3 is the
  like-for-like number.
- The Ladder Log names the opponent's Pokémon, not their skill or rank. Only numbers from the engine in use when the
  file was saved are compared; older ones are kept and marked.

## Save first, then read
- A **version** is the deck's card list: comments and spacing don't count, any card change does.
- Each version gets a **predictions file** once it has a slow report or is on the ladder sheet. It holds every
  committed bot number for that card list, so nobody picks which ones count.
- The laptop commits it on main directly, never by a merge, and never edits it. A later number goes in an addendum
  with new bots only.
- A game is a **test** only if its video started at least 10 minutes after the file reached main. A game with no video
  name is feedback (an agent can add the name from the Battle Logs folder), and so is any game already logged or
  recorded when the file was saved.
- The reader checks that the file and the code are unchanged, and lists any Ladder Log entry edited since the last
  reading.

## Which version he played
Agents tie each game to the deck file on main when it was played. Before each reading they compare his side's cards in
the review packets; a game with a different card is left out. His notes help but are never needed.

## What a reading says, in this order
1. **Games against a panel list** (about 1 in 4): wins against the bots' expected wins, and how often that happens if
   the bots are right, in words.
2. **Other games**: the record, no prediction.
3. **Level check**: the whole record against each bot's range, assuming the other opponents are about as hard as the
   panel.

A win by the opponent's concession is a full win. An early concession can hide the opponent's deck, so it lands in
"other games" and the panel games look worse than they were; the reading says by how much. The first reading with 20
test games (or the one at season end or retirement, if sooner) is the version's **verdict**; others are interim.

## What one deck can show
If his win rate matched the bot's number, deck 12's wins would land in these ranges 95% of the time (DETAILS §5):

| deck 12 bot | 10 games | 20 games | 40 games |
|---|---|---|---|
| frozen kx3, 61.3% (optimistic end) | 3-9 | 8-17 | 18-31 |
| km3, same deals, 34.1% | 1-7 | 3-11 | 7-20 |
| km3 floor, 33.1% | 1-6 | 3-11 | 8-19 |

Twenty games give only about 5 against panel lists, so they catch only big misses. One deck can't check the matchup
numbers or show that the simulator ranks decks.

## Ranking decks
Checking the bots' order of decks needs about 9 to 30+ decks of 20 games each, depending on how far apart the decks
really are (his past decks suggest about 12 points) and how closely the bots follow that; at his usual 10 games a deck,
more than 30. At one deck a season, that is 9 months to 2.5+ years (DETAILS §7).

## Deck 12 so far (feedback only)
- Oct 14: 10 games, 2-8. The bot numbers came before game 1; the predictions file and these rules came after game 10.
- Against panel lists: 2 games, both lost (Blaziken, Suicune). The strong bot expected 1.0 wins; losing both happens
  about 1 time in 5. Other games: 2-6.
- **Verdict: the 2 games against panel lists show nothing either way. If his other 8 opponents were about as hard as
  the panel, 2-8 would be below the strong bot's range (about 1 time in 40; its number is the optimistic end) and
  inside the everyday bot's.**
- Bot games compared: 2,240, of which 160 kx3.

## Now
- Commit the six staged predictions files (brew 07, deck 12, deck 13, brew 09, draft D, brew 10). Brew 08 and draft A
  have no current-engine number. Games played after that commit are tests.
- Deck 13 has 10 games from Oct 14 (5-5), all feedback.
- Read each version at 10 and 20 test games, at season end (about Oct 28) and at retirement. Report each reading once,
  in plain words.
