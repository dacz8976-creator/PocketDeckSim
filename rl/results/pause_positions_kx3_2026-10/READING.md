# The kx3 position study: the reading (Oct 14)

The main and flagged tables follow `SPEC.md`, which was fixed before any run. Added afterwards:
- part 2;
- the C-against-F list;
- the plan column;
- the ranges.

SPEC.md counts 35 rules-switch-2 positions, but `position_list.tsv` flags 36.

**Question.** On Dustin's real turn starts from his pause games, how often do the bots make his first move? Does the full candidate (C)
play more like him than the frozen kx3 (F)?
- "Stronger" here means the strength runs on the 7 development decks: F scored 16.6 points more than km3 per 100 games, and C 3.9 more
  than F.
- Each bot played each position 12 times, seeds 1-12.
- All nine workers are in (`workers/`), and every worker's km3 gate matched the committed runs.

**Answer.**
- **About half the time.** On the 68 main positions, km3 makes his first move in 54% of its replays, F in 50% and C in 43%.
- **And no: C plays less like him than F does.** Making his move less often is not the same as playing worse (below).

| bot | share of the 12 replays where the first move is his | agree (10+ of 12) / split / differ (0-2 of 12) | his plan up to his first draw card, in 10+ of 12 |
|---|---:|---|---:|
| km3 | 54.3% | 33 / 8 / 27 | 19 |
| frozen kx3 (F) | 49.8% | 27 / 14 / 27 | 16 |
| candidate (C) | 42.8% | 24 / 11 / 33 | 14 |

**What counts:**
- The main positions are those with a plan of his to compare, no rules-switch-2 flag and no Special Condition.
  - 117 of the 119 have a plan; 034953 t16 and 123812 t09 have none.
- Plans are compared up to the first draw card or Sabrina. End of turn and Bench slot numbers are ignored.

**Position by position** (each position counts once; percentage points of the 12 replays, not game points):
- **C against F:** C makes his first move about 7 points less often. The 95% range is 1 to 13 less, and it holds when positions from the
  same game are resampled together.
  - C is higher on 8 positions, lower on 16 and the same on 44.
  - Almost the whole gap is four positions where F makes his move in 11-12 of 12 and C in none: 213625 t07, 032857 t04, 032023 t12 and
    021629 t16.
  - On the other 64, C is about 1 point lower.
- **F against km3:** about 4.5 points less (range about 2 to 8 less).
- **C against km3:** about 11.5 points less (range about 5 to 18 less).

The two separate tables point the same way, though several of their ranges include zero. 031138 t06 is in both.

| positions | km3 | F | C |
|---|---:|---:|---:|
| rules switch 2, 36 | 62.5% | 60.4% | 53.7% |
| Special Condition, 14 | 50.0% | 42.3% | 31.5% |

The Special Condition table can't be fully trusted: these bots played those positions without the condition.

## What this does and doesn't say

**Agreeing with Dustin is not the same as playing well.** A bot that parts from him more often may be finding better moves, or it may
have habits he rightly avoids. This study can't tell which. Nothing is decided on it; it describes how the bots play his real positions.

**One rare pattern: ending the turn at once.** On a few positions, a kx3 version ends the turn without doing anything, while km3 and the
other version attack:
- C on 213625 t07 (7 of 12 replays), 010837 t09 (11 of 12) and 010837 t11 (12 of 12);
- F on 034953 t14 (7 of 12);
- F also on 014423 t07 (6 of 12). Nobody attacks there, so F skips his evolution and Energy instead.

What it is and isn't:
- **In three of the four attack cases, the skipped attack was a sure knock-out on a 30-HP Active.**
- **It is the same kind of mistake** the combined run's skip hand check found (`../strength_2026-10-08_kx3_combined/HAND_CHECK_SKIPS_laptop.md`).
  - That check found these skips rare and equally common in both bots.
  - Four positions can't say whether C does it more.
- **It bears on the next pilot round's attack rule,** which Dustin ruled must be tested both ways. The 014423 t07 case involves no attack,
  so that rule wouldn't cover it.

**Where C parts from F most** (by 4 or more replays on his first move):
- 7 of the 68 main positions, plus 5 more among the switch-2 and condition positions, all with C lower;
- the four main positions above, where C ends the turn, plays something else first, or retreats before evolving.

**What differs**, comparing each bot's most common plan with his:
- The label is the first kind in a fixed list, so any Supporter or Item in the differing stretch puts a position in the first group.
- Supporter or Item choice or order is the most common label: 18-21 of the 45-49 positions per bot where the plans differ. About half of
  those part on a Supporter or Item step itself.
- Evolution timing comes next (8-10).
- The Oct 2 read also led with Supporters and Items (17 of 20 turns there, counted another way).

**The opponent's deck list is unknown** in every position. His hidden cards (hand and deck) are filled from the pilot's own list, so every
row is approximate.

## For his next quiz

- **52 "neither" positions,** out of the 117 with a plan of his: no bot makes his first move in 7 or more of 12 replays.
  - 32 are main, 14 rules switch 2 and 7 Special Condition; 031138 t06 is both.
  - In 37 of them, all three bots pick the same other first move.
- They are listed in `reading/reading_output.txt` with each bot's most common first move.
- The quiz is his to take whenever he likes. It is evidence about the bots, not a gate.

## Part 2: Sonnet's 8 Oct 13 positions

These ran on the new harness, which carries Special Conditions and the knock-out count.

The laptop's review of the Oct 12-13 positions, added on Oct 14 (`../pause_games_new_2026-10-13/v2/REVIEW_POSITIONS_laptop.md`), found
field errors in two of these eight:
- 203719 t17 gives the opponent's next Energy as Darkness; it should be Lightning.
- 015659 t05 gives the opponent's hand as 5 cards; it should be 6.

The other six are right on every field.

**010837 t09 and t11.** His Glimmet is Active with Kingambit on his Bench. The opponent's Mega Kangaskhan ex is Active at t09, and at t11 it
is on the Bench behind a 30-HP Pichu.
- **km3 and F** retreat into Kingambit and use Overlord's Blade in 12 of 12 replays at both turns.
  - The Blade adds 40 for each time his own Pokémon have been knocked out: twice here.
  - At t09 that makes 60 + 80 = 140 on the 180-HP Kangaskhan.
  - At t11 the Blade is a sure knock-out on the Pichu, whatever the count.
- **C** ends the turn at once in 11 of 12 replays at t09 and in 12 of 12 at t11.
- **He** attacked with Hang Down.
- **The Kangaskhan's attack** is priced at 80, not 120, by km3's forecast of the opponent's turn, which all three bots use
  (`../kangaskhan_pricing_2026-10-13/`).
  - F's and C's play-outs count the full 120.
  - It doesn't explain C's end of turn: F has the same forecast and attacks, and km3 with the forecast fixed changes none of its plans in
    this game.

**010837 t03:** km3 makes his first move in 12 of 12, F in 8, C in 1.

**The other five:**
- On 020824 t11, all three make his first move in 12 of 12.
- On 014423 t07, km3 and C do in 12 of 12 and F in 6; in F's other 6 it ends the turn at once.
- On 203719 t17, 015659 t05 and 210041 t06, none of them makes his first move in any replay.

## How it was run

- `read_positions.py` gathers the workers' runs and applies Sonnet's comparison rules to each bot
  (`../pause_games_new_2026-10-12/harness/kw_report.py`). It writes `reading/`.
- km3 is the committed `runs_km3`.
- **Checked independently:** a second script that recomputed every count from the raw out files matched every position and table. The
  ranges were checked by resampling whole games.
- **Timing** (from the workers' `TIMING.txt`, 12 replays on a 4-core sandbox):
  - F took from a few seconds to about 40 minutes per position; C took up to about 1.75 hours.
  - The longest for both was game 213625 (New deck 24).
  - In all, F used about 14 sandbox-hours and C about 35, for the 127 positions.
