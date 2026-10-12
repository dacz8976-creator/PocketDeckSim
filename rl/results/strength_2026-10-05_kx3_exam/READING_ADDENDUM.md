# The exam's reading, addendum (Oct 5, written while the exam was running, before any of its result was read)

The pre-registered primary result stays as it is: the pooled paired difference, with every deck's row printed.

This adds a split by deck group and a pace report, after Dustin's note (Oct 5, verbatim): "It's deck dependent when
building the bench is helpful. Some decks are meant to play fast. Some reward buildup."

**The groups, fixed now.** The 11 held-out decks were never labelled, so the rule is mechanical and blind to results:
- Rank the decks by the mean length in turns of the reference arm's games: km3 on the deck against the panel, in this exam.
- The 4 shortest are the **fast** group, the 4 longest the **setup** group, and the middle 3 are reported unlabelled.
- Game length under km3 is not the score being compared, so using it doesn't bias the reading.
- One exception: Dustin calls deck 07 (Skarmory stall) a setup deck. It goes in the setup group whatever its rank, and the
  next-longest deck moves to the middle.

**Reported per group and per deck, each as a paired difference with its 95% interval:**
- the score gain (kx3 minus km3);
- the change in turns per game;
- the change in the deck's first-attack turn (the deck player's first logged `Attack:` action, by own turn; a game with
  no attack is counted at its last own turn).

These are descriptive. Six comparisons per matchup don't support ranking matchups, and the groups are small.

**For comparison:** the development run, by its own groups (aggro 09, 06, 10; setup 03, 01, 05; draft A apart), from
`../strength_2026-10-03_kx3_dev/games.jsonl`.
