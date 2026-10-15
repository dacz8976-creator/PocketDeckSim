# Paired variant of a slow report (Oct 15, 2026)

`slow_report.py --paired-with rl/results/slow_reports/<date>_<base deck> --deck <variant file>` registers a deck that differs from a base deck by one or two cards as a **paired variant** of an earlier,
registered report of the base deck, so it is played on that report's own deals. Code: `rl/strength/slow_report_paired.py` and the hooks in `slow_report.py`; tests: `rl/strength/test_slow_report_paired.py`;
how to use it and what it checks: the README of `rl/strength/` ("A paired variant of a report") and the module docstring. Job: the coordinator's, Oct 15, for the two deck-13-A tests below (Dustin Oct 15:
"whatever tests that you think will be helpful for almost no weekly usage is good with me").

## The two variants (`decks/variants-2026-10-15/`)

Both start from `decks/dustin/13-a-ninetales-raticate.txt` (sha256 `f79ad459a118`) and replace the line `1 Ilima A3 149` by one other card on that same line (card 17 of 20), so the swapped card keeps its place:

| file | change | text of the new card (`lib/card.py`) | sha256 |
|---|---|---|---|
| `13-a-giant-cape.txt` | -1 Ilima A3 149, +1 Giant Cape A2 147 | "The Pokémon this card is attached to gets +20 HP." | `75097ab4fd8515b2…` |
| `13-a-big-malasada.txt` | -1 Ilima A3 149, +1 Big Malasada A3 142 | "Heal 10 damage and remove a random Special Condition from your Active Pokémon." | `0e9607b4c6b16fa7…` |

`lib/deck_check.py` passes both ("decks clean"); neither is a panel list. Candidate C (Vulpix A3 040) is left out: by its card text it targets neither of 13-A's two repeated problems (the opening Basic giving up the first point; Sleep).

## How a seed becomes a shuffle (read from the engine, then checked with the real program)

Harness (`rl/strength/src/main.rs` `run`): the seed of a game is `seed_base + pair x pair_stride + deal`, with `pair = deck_index x 1000 + opponent_index`; one deck, the same opponent order, the same
deals and `pair_stride` give the same seeds. Engine (`engine/src/game.rs` `Game::new`, `state/mod.rs` `State::initialize`, `deck.rs`): the game's `StdRng` is seeded with the seed; the deck is the file's cards in
file order (`2 X` is two consecutive cards, nothing is sorted); each deck is shuffled in seat order by Fisher-Yates (`SliceRandom::shuffle`: it swaps places and looks at no card); only a hand with no Basic
Pokémon is repaired afterwards, by choosing among the places that hold a Basic; then the coin for the first player and the Energy roll (`roll_energy` looks at the Energy types only). So a card that keeps its
place in the deck file keeps its place in the shuffle, and the twin games are dealt alike except for that card, as long as the swapped cards are both Basic or both not.

`shuffle_check.py` / `shuffle_check_output.txt` plays this with the real pinned program (km3 on both arms, about a second a game): base v the Giant Cape variant on 160 twin games, and a negative control with the
Cape on the last line. Aligned: **50 of 160 twin games are the same game from start to finish** (all 50 among the 56 where neither card was played); moved line: **8**. The first player is the same in all twins in
both runs. The pilots read their own deck list, so a twin can part from its base game before the card is drawn (6 of the 56 did).

## Dry runs (`dry_runs.py` / `dry_runs_output.txt`)

Both variants against the real base folder, nothing written. **On this laptop** each is refused for one reason only: the program (the laptop has the pinned binary `76df495b`, the base report was played by the
cloud rebuild `5011e227cf63`); the diff, the plan, the seeds (`24606700000`, "no new seed slot"), the pin (byte-equal), the eight panel lists and the base deck file all pass. **With the program check answered
as on the cloud runner** (a throwaway patch of `check_program`, labelled in the output) both exit 0 with "dry run: nothing written". The runners' own dry run is the real test of the program check.

## The counts on the variant's page, and the check of their code

The page of a variant has "Compared with the base report": the score change (variant minus base, 95% t range over the twin games) for kx3 and km3, overall and per list; how many twins ended the same way and
how many were the same game move for move; and "Did the card do its job?": plays of each swapped card per pilot, where a Tool went (Active or Bench, and which Pokémon), games where the opponent's first point
was a knock-out of our opening Active (never evolved or moved), and turns on which a charged Pokémon did not attack (an indicator of Sleep or Paralysis, not a measurement). The game records hold only the deck
side's moves and the points, so these cannot be counted and the page says so: how often the Cape holder survived an attack it would not have survived without the +20 (no Hit Points, damage or opponent moves),
which Special Condition Big Malasada removed (random, not recorded), Sleep itself.

The two board counts are a port of the throwaway scripts of the deck-13 analysis (Oct 15). `port_check_output.txt` runs the port and the two old scripts on the real base games: own turns, charged-but-idle
turns, idle turns of an ex, attacks and the opening-Active first-point counts agree on every list and both pilots (the old script also counts every Ilima move as a "warning", which is the one difference).

## Review

One reviewer subagent read the seed/pairing code and the engine (seed and shuffle claim, `check()`, the page maths). It confirmed the seed formula (0 of 320 real base seeds disagree), the shuffle claim for aligned swaps
with equal Basic-ness, the parsing, and the page maths, and found these, all fixed with a test each: Tool rows undercounted attachments with a single legal place (not logged: now shown as their own row); Pokémon
swapped in were counted as "played 0" (now Place/Evolve count); an opponent-board `Activate` (our Cyrus) was replayed as our own switch (7 of 65 in the base; now only our seat's); a first point whose Active had a
same-name benched copy promoted without a log line could not be told from a bench knock-out (now counted apart, 21 of 320 base games fit); the Basic-repair note understated its effect (extra random draws shift the
opponent's shuffle, the coin and the Energy rolls: now said, and the page states whether who went first was the same in all twins); `scrub_env_prefixes` was not compared when the pin's bytes differ; "same game
from start to finish" ignored turns and plies; Energy attach amounts were counted as 1; a program change during the variant's run was not flagged in the comparison. Not changed: the program must be the base report's
own (sha256) as the job asked, so a variant can be registered only where that program exists (both cloud runners keep `5011e227cf63`; the laptop has the pinned `76df495b`, hence the laptop dry run's refusal); both
seats of a deal share a seed and the t range treats the games as independent, as the base page already does.

## Tests

`cd rl/strength && python3 -B -m unittest -v test_slow_report_paired`; the whole slow-report set is in the README line "Tests:" (it now ends with `test_slow_report_paired`).
