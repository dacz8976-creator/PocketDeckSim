# Ladder validation: details

The rules in full, the tables and the sources behind `SPEC.md`. Sources are tagged (S1)-(S9) at the end. Times are UTC.

## 1. Files
- `make_predictions.py` writes `predictions/<deck>@<id>.json` (never overwritten). `<id>` is the version: the first
  12 hex digits of the sha256 of the deck's normalised card list (Energy, then count, name, set and number of each card,
  sorted). An addendum is `<deck>@<id>+<tag>.json`.
- `read_ladder.py` reads a Ladder Log export against `predictions/`, read only. With `--out` it writes one new file.
- `versions.json` (created when the first note is needed): the agents' version notes, committed on main, append-only.
- `readings/<date>_<what>.txt`: each counting reading's `--out` file, committed. The next reading compares the Ladder
  Log with the newest one and lists every edited game.
- Both scripts are standard library only and have self-tests (`--selftest`, with and without git; see section 10).

## 2. Registration, test and feedback
- **Registration time** of a predictions file: its first readable commit on main (the committer's clock), or the file's
  own `written_at` if later, or the time this clone's reflog shows the commit reaching main if later still. A file
  committed on a branch and fast-forwarded later is caught by the reflog on the laptop's clone. The rule is still that
  predictions files are committed on main directly (by path).
- **Integrity**: the reading uses the first-committed bytes. It flags a working copy or a main tip that differs from
  them, a file deleted from main (still read), and a file written by different code. Each file saves the sha256 of
  both scripts, and the reader prints CODE CHANGED if either differs.
- **Play time** comes from the iOS video name in the note (`20261014_142546000_iOS` = 14:25:46). An agent can also add
  the name to the version notes from the Battle Logs listing. Other recording names are not read as times.
- **Test** only if every one of these holds:
  1. the video start is known and is not after the log time;
  2. it is at least 10 minutes after registration;
  3. the game was not in the Ladder Log when the file was written (the file saves the game ids);
  4. its video is newer than the newest video then (the file saves it).
  Everything else is **feedback**: "time unknown" (no video name), "time doubtful" (video after the log time), "early",
  or "seen". 33 of the 76 logged games have no video name, all from last season (S1).
- **Verdict**: the first reading with 20 test games of a version, or the reading at season end or retirement if that
  comes first. Others are interim. The reader prints which.

## 3. Versions, version notes and card checks
- **Assumed tie**: the game's Ladder Log section, and the card list in the deck file on main when it was played. If the
  deck file was not on main yet, the game is not read.
- **Shared section**: several deck files may be logged under one section ("Deck 13-A"). Then the file's `log_label`
  found in the note decides. If no label is found, the game is "ambiguous" and not read. If the note names a different
  "Deck N-X" from the only file's label, the game is not read either.
- **Version notes** (`versions.json`): one entry per game. The key is `"<section>/<game id>"`. The fields are:
  - `evidence`: a packet or frame path, **required**; a note without it is ignored;
  - `version`: a card-list id; this makes the tie "confirmed" and works for a game in any section;
  - `cards`: `"checked"` or `"mismatch: <card>"`;
  - `video`: a recovered iOS video name.
  The reader takes main's committed copy and checks it is append-only. It lists every game a note added, removed or
  gave a time to, and prints the record with and without the notes.
- **Card check**: before each reading, an agent compares his side's cards in each test game's review packet with the
  card list. A mismatch takes the game out. The reading gives the record on checked games beside the record on all.
  Why this matters: last season brew 03a's game 3 note says a second poison tool replaced the Cape, while the deck
  file still has Giant Cape (S1).

## 4. Opponent matching, rule v1 (saved in every predictions file)
The text is cleaned first:
- lower case, curly quotes straightened, hyphens to spaces, spaces collapsed;
- "M Altaria" is read as "Mega Altaria" (only for the Megas the rule names).

A game goes on the first list whose name appears as whole words:

| list | the opponent field must name | unless it also names |
|---|---|---|
| Altaria | Mega Altaria | |
| Blaziken | Mega Blaziken | |
| Hydreigon | Hydreigon | |
| Lucario | Mega Lucario | Raticate |
| Sceptile | Mega Sceptile | |
| Suicune | Suicune ex, or Suicune with Baxcalibur | |
| Vespiquen | Vespiquen | |
| Weezing | Weezing ex | Magmar (the TR Magmar build, ruling P3) |
| readout only, no bot number | Mega Charizard Y; Mega Sharpedo; Mega Rayquaza | |

- **Exact** if every Pokémon named is in that list's file; anything else named makes it a **variant**. They are
  reported apart.
- A guess word ("likely", "maybe", "probably", "possibly", "?") makes a game **inferred**: shown apart, never scored.
- The self-test fixes 44 spellings. For example "Mega-Blaziken ex" and "Suicune / Baxcalibur" match; "Altaria ex" and
  "Mega Charizard ex" (form unknown) do not.
- **On the 76 games logged by Oct 15 01:30** (S1), 19 matched a panel list:
  - 14 of 56 last season (Sept 15-29), 5 of 20 this season, 7 of the 19 variants;
  - so about 1 game in 4 (25%) can be scored against a matchup forecast.
- The reader's self-test pins rule v1's result on each of the Oct 14 snapshot's 66 games (16 matched: 14 of 56 and
  2 of 10) (S8).

## 5. Forecasts and win ranges
- **Matchup forecast**: the km3 floor's shape across the 8 lists (240 games a list), shifted by one constant on the
  log-odds scale (solved by bisection) so the 8 forecasts average exactly to the bot's number.
  - The shape comes from the newest current-engine floor, else the newest older one (flagged). An addendum uses its
    base file's shape.
  - The raw per-list cells (6 to 20 games) are saved, not used: they are mostly noise.
- **Win range**: the 95% range of wins in m games if his ladder rate equalled the bot's number, with the bot's own
  uncertainty included (beta-binomial, Beta(x+1/2, n-x+1/2)).

Deck 12 (card list 5c3b7d688afa; file sha256 4d059bd2...; one version, first committed 83fd3496 Sept 24) (S2, S3, S6, S7):

| bot | number (95% range) | games | wins in 10 / 20 / 40 | first committed | engine |
|---|---|---|---|---|---|
| frozen kx3 (slow report), the optimistic end | 61.3% (53.5-68.5) | 160 | 3-9 / 8-17 / 18-31 | Oct 14 06:50 runner branch (521106c2); main 13:56 (55295ea7) | current |
| km3 (slow report same deals) | 34.1% (27.2-41.7) | 160 | 1-7 / 3-11 / 7-20 | same | current |
| km3 floor | 33.1% (31.0-35.2) | 1,920 | 1-6 / 3-11 / 8-19 | Oct 12 05:36 (7f235df3) | current |
| frozen kx3 (Oct 5 exam) | 62.5% | 48 | | Oct 6 10:11 (766c585f) | older: out |
| m64 (exam) | 68.8% | 48 | 4-10 / 9-18 / 19-35 | games Oct 14 11:55 in `workers/E10_reg_m64` (cd2c05ce), merged 22:15 (893434e6); first m64 figure 22:28 (f4c487e0) | older: out |
| m32 (exam) | 70.8% | 48 | | Oct 14 20:55 (f46d68f8) | older: out |
| km3 floor (Sept 30) | 31.4% | 1,920 | | Sept 30 21:34 (46908102) | older: out |

- The older engines count two Ariados as one, which is this deck's key damage rule.
- Calibrated forecasts, frozen kx3, by list (Altaria, Blaziken, Hydreigon, Lucario, Sceptile, Suicune, Vespiquen,
  Weezing): 75.2, 42.0, 63.5, 52.1, 56.4, 61.7, 61.2, 77.9.
- His real mix changes the number little: 61.3 at equal weights, 56.7 at last season's mix (rule v1's 14 matched
  games). The real gap is that about 3 games in 4 match no panel list.

## 6. Concessions
- A win by the opponent's concession is a full win in every record. 17 of his 34 logged wins came that way (S1):
  - 12 of 27 last season (12 of 29 in the Oct 14 snapshot), 6 of brew 08's 7;
  - all 5 of deck 13's wins.
- **The bias**: an opponent who concedes early often never shows the attacker, so the win lands off the panel, while a
  loss to a panel deck is always identified. In the 76 games:
  - panel games went 5-14, with 1 concession win;
  - off-panel games went 29-28, with 16 concession wins (13-28 without them).
  So the panel games are short of wins, and the matched check leans against the bot.
- Each reading prints the off-panel concession wins and repeats the matched check with 1 in 4 of them counted as panel
  wins, at the bot's own number. The 1 in 4 is the panel share in the log.

## 7. Ranking decks
- **The test**: a one-sided 5% rank correlation between the bots' numbers and his ladder win rates, with an 80% chance
  of passing if the link is real. Simulated 1,000 times per setting (S4). The model gives each deck a true ladder rate
  0.5 + spread × (r × its panel position + the rest at random), where r is how closely the bots' numbers follow the
  true rates. At 20 games a deck it needs about:
  - 9 decks with r = 1 and a 15-point spread;
  - 14 decks with r = 1 and a 10-point spread;
  - 23 decks with r = 0.8 and a 10-point spread;
  - more than 30 with r = 0.5 or a 5-point spread.
- At 10 games a deck (r = 0.8, spread 10), even 30 decks give only a 74% chance, so it needs more than 30.
- **The spread**: his 11 decks with 3 or more logged games, deck 12 included (59 games), spread about 12 points (S5).
- **The time**: this season runs Oct 14 06:00 to about Oct 28. His last-season games ran Sept 15-29, then ranked play
  paused until Oct 14. A new season about once a month is inferred from that, not stated anywhere (S1, S9). At one deck
  a season, 9 to 30+ decks is about 9 months to 2.5+ years.
- **What makes it slower**:
  - versions of one deck are not independent decks;
  - no deck reached 20 games last season (the most was brew 08's 10);
  - decks picked because the bot rated them high tend to fall short of their numbers.

## 8. Deck 12's reading (feedback only; `reading_deck12_feedback.txt`, S8)
- **Matched**: 2 games, both exact, both lost (Blaziken, Suicune).
  - Frozen kx3: 1.04 expected wins; losing both happens with chance 0.222 (about 1 time in 5).
  - km3 same deals: 0.51 expected, 0.547. km3 floor: 0.560.
- **Off-panel**: 8 games, 2-6. Mega Sharpedo (readout) 1-0; the other 7 (Lightning decks, Mega Swampert, Charizard,
  Mega Venusaur) 1-6. One loss was his concession.
- **Level check**, assuming off-panel opponents are like the panel on average: 2-8.
  - Frozen kx3: range 3-9, so 2 is below it. A record this far off happens about 1 time in 40 (two-sided 0.024,
    one-sided 0.012).
  - km3 same deals: range 1-7, inside (two-sided 0.575). km3 floor: range 1-6, inside (two-sided 0.611).
  - m64 (older engine, record only): two-sided 0.010.
- Bot games compared: 2,240, of which 160 kx3 (160 + 160 + 1,920).
- **What he played is unconfirmed.** All 14 card names in the file appear on his side in the reviews and no other card
  does, but counts and Energy are unchecked. The clips starting 14:54:49 and 16:43:28 open on a deck-share QR code an
  agent can check (S7).

## 9. Staged predictions files (Oct 15)
Each file holds every committed source of its card list; older-engine ones are kept and marked (S7). With git, the
writer refuses a file that leaves out a committed slow report or exam of the version. Floor pages don't record their
card list, so the writer lists every floor page with the deck's name that it was not given.

| deck (Ladder Log section) | file | current-engine numbers | forecast shape |
|---|---|---|---|
| brew 07 (brew-07) | `brew-07-hoopa-darkrai-sableye@0a7d9d5a9df9.json` | kx3 79.1, km3 63.1, floor 60.8 | current floor |
| deck 12 (d12) | `12-ariados-whimsicott-ogerpon@5c3b7d688afa.json` | kx3 61.3, km3 34.1, floor 33.1 | current floor |
| deck 13 (d13, "Deck 13-A") | `13-a-ninetales-raticate@5aeff5e9af57.json` | kx3 70.6, km3 51.3 | Sept 30 floor (older) |
| brew 09 (brew-09) | `brew-09-sableye-obstagoon@5254637c9b25.json` | kx3 66.9, km3 45.6, floor 43.6 | current floor |
| draft D (no section yet; "draft-D" placeholder) | `draft-D-entei-grimhound@506d5204b13c.json` | kx3 43.1, km3 24.4, floor 31.1 | current floor |
| brew 10 (brew-10) | `brew-10-diancie-giratina@c4f525355f06.json` | kx3 70.6, km3 40.9 | Sept 30 floor (older) |

- **Missing**: brew 08 and draft A (Wallace) have only older-engine slow reports (engine tree 31dbd2e6e8ec), so they
  get no file yet.
- **Deck 13 so far**: 10 games logged under d13 (videos Oct 14 21:44:36-23:47:28), 5-5, all feedback.
  - Matched: Mega Altaria L (exact), Hydreigon / Mega Absol ex / Absol / Bombirdier W (variant), Suicune ex L (exact).
  - Readout: Mega Charizard Y W, Mega Rayquaza W.
  - 5 unmatched.
  - Its slow report reached main Oct 13 18:59:55 (367ac414), before its first game.
- **Draft D**: if its games are logged under another section, agents tie them with version notes. Only the amended
  list's floor (`D_amended`) is in the file; `D_root`, `D_victini-passive` and the Oct 2 root page ran the first list.

## 10. Commands
- **Write a file** (on main, then commit it on main by path). Deck 12's staged line is below; the others are in the
  same form with their own sources (S7):
  ```
  python3 rl/results/ladder_validation/make_predictions.py --deck decks/dustin/12-ariados-whimsicott-ogerpon.txt \
    --log-doc d12 --slow-report rl/results/slow_reports/2026-10-13_12-ariados-whimsicott-ogerpon \
    --exam rl/results/strength_2026-10-05_kx3_exam --exam rl/results/exam_m32_m64_2026-10/reg_m64 \
    --exam rl/results/exam_m32_m64_2026-10/reg_m32 \
    --floor rl/results/floor_recheck_rules2_2026-10/pages/12/12-ariados-whimsicott-ogerpon.md \
    --floor rl/results/floor_dustin_2026-09-30/12-ariados-whimsicott-ogerpon.md \
    --export <Ladder Log export> --newest-video <newest Battle Logs video name> \
    --first-game 2026-10-14T14:25:46Z --games-already-read 10 --note "..."
  ```
- **Read** (export the log read only first, with ArtifactData `list` on collection `logs`, limit 1000):
  ```
  python3 rl/results/ladder_validation/read_ladder.py --export <export> \
    --out rl/results/ladder_validation/readings/<date>_<what>.txt
  ```
  `--as-if-committed now` makes a dry run that is never a counting reading.
- **Self-tests**:
  ```
  make_predictions.py --selftest [--no-git]
  read_ladder.py --selftest --export rl/results/ladder_validation/selftest_snapshot_2026-10-14 [--no-git]
  ```
  The snapshot is 18 per-section files, 66 games (the Ladder Log read only, Oct 14 ~23:30). Without git, the tests skip what
  needs commit history. The Oct 15 01:58 export behind the staging dry run is `readings/2026-10-15_ladderlog_export.json`.

## Sources
- S1: Ladder Log (artifact GHSfGSCzNiWNj8SFPXV3R1, collection `logs`), read only.
  - The Oct 14 snapshot: 66 games, 56 of them Sept 15-29 (Central time Sept 15-28) and 10 on Oct 14.
  - The Oct 15 01:58 read: 19 sections, 76 games, saved as `ladderlog_export.json`.
- S2: `slow_reports/2026-10-13_12-ariados-whimsicott-ogerpon/`. In games.jsonl, `pilot_opp` is km3 in every game;
  SLOW_REPORT.md says "the optimistic end".
- S3: `make_predictions.py` on deck 12 (ranges, calibrated forecasts).
- S4: the round's simulation output (`sims_output.txt`, 1,000 simulations per setting).
- S5: the round's statistics (`stats_output.txt`, section F).
- S6: `floor_recheck_rules2_2026-10/pages/12/` (the page and `_games.jsonl`; "km3 on the panel").
- S7: git (read only): commits 521106c2, 55295ea7, 7f235df3, 766c585f, cd2c05ce, 893434e6, f4c487e0, f46d68f8,
  367ac414, 46908102, and the ladder sheet 2c6bdf38. Also the manifests and the Codex QA reviews.
- S8: `read_ladder.py` self-test on the snapshot, and `reading_deck12_feedback.txt` (a dry run on the Oct 15 read).
- S9: the Battle Logs folder listing (file names only). The newest video at staging was `20261014_234728000_iOS.MP4`.
