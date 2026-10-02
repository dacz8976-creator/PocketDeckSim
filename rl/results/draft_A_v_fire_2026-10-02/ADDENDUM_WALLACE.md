# Draft A v the Fire list: the Wallace addendum (registered Oct 2, 2026, before any game)

**Who wrote this and why.** A Claude Code subagent (Opus 5.5) on the laptop, on a job from the coordinator session. This
addendum, `run_wallace.sh` and `analyze_wallace.py` were written before any game of the addendum. The main test
(`README.md`, `run.sh`, `analyze.py`, registered at 937183d; `RESULTS.md` at 3e6cd559) is not changed. Nothing here is
committed by this job: Dustin or the coordinator commits it, or not. `run_wallace.sh` refuses to play until these three
files and the new list are committed, so the definitions below are fixed before the first game.

**Not a ranking and not a ladder forecast.** One list plays one saved opponent list, with the bot (km3) on both sides.
The result says how the bot does with the Wallace version against that one list, next to draft A and deck 13 on the same
deals. It does not say which deck is better on the ladder, and no number here predicts Dustin's ladder results.

## 1. Why

Dustin, Oct 2 (laptop chat, verbatim): "Wallace supporter would help sharpedo get going quicker". Asked what Wallace should
replace: "1 Wallace for 1 Misty".

Wallace (B3b 068, `python3 lib/card.py`): "Choose 1 of your [W] Pokémon in play with a maximum HP of 50 or less. Put a
random [W] Pokémon from your deck that evolves from that Pokémon onto that Pokémon to evolve it."

- In this list only **Carvanha** (B4 034, Water, 50 HP) can be chosen, and the only card in the deck that evolves from it is
  **Mega Sharpedo ex** (B4 035). Alolan Vulpix has 60 HP; Lapras has no evolution here; Elegant Cape's +30 HP is for a
  Stage 1, so it can't take Carvanha above 50.
- How the engine plays it (rules/04 and rules/09; `rl/results/rules_recordings_2026-10-01/WALLACE_second_read_sonnet.md`):
  the player picks the Pokémon, then the engine puts a random matching Pokémon from the deck on it. With no Mega Sharpedo
  ex left in the deck, nothing evolves (the deck is shuffled). Wallace can be played whenever a Water Pokémon with maximum
  HP 50 or less is in play and the deck isn't empty, including on the list's first turn and on a Carvanha placed that turn
  (rules/04: seen in battle 150630, and Dustin). The smoke (section 4) showed it: going first, the bot played Wallace on its
  own turn 1 on its Active Carvanha, which became Mega Sharpedo ex.

The question: with Wallace in place of one Misty, does the bot get Mega Sharpedo ex and Turbo Shark going sooner against
the Fire list, and how does the list do against it next to draft A and deck 13 on the same deals?

## 2. The list

`decks/brews/drafts_2026-10-01/draft-A-wallace.txt`: draft A's list (`draft-A-shark-tempo.txt`, blob 19331d7) with one
Misty (A1 220) replaced by one Wallace (B3b 068). Same format, 20 cards. Wallace's line sits right after the remaining
Misty; every other line is byte for byte draft A's. `python3 lib/deck_check.py files` passes it ("decks clean"), and the
engine loaded and played it in the smoke.

```
Energy: Water
2 Carvanha B4 034
2 Mega Sharpedo ex B4 035
2 Alolan Vulpix B2 028
2 Alolan Ninetales ex B2 029
1 Lapras A3 044
1 Misty A1 220
1 Wallace B3b 068
2 Professor's Research P-A 007
2 Poké Ball P-A 005
1 Copycat B1 225
1 Cyrus A2 150
1 Irida A2a 072
1 Elegant Cape B3b 065
1 Lucky Ice Pop B2 145
```

| role | path | git blob | sha256 |
|---|---|---|---|
| the Wallace version | `decks/brews/drafts_2026-10-01/draft-A-wallace.txt` | `f231dc58051fdf35374892c06b9220f317f54201` | `b5b66d02a0f20da6388ed90db83e6b72eb91134070795a0be36e6d5a3b0ab504` |

Draft A, deck 13 and the Fire list are the README's section 2, unchanged; `run_wallace.sh` checks all four lists. Wallace
B3b 068 is a regular (non-promo) card, so the drafts' ownership rule (`OWNERSHIP.md`) needs no check for it.

## 3. Engine, pilots and programs

- **Engine, goldfish and pilots:** the README's section 3, unchanged. `rl/engine-2026-10-02/deckgym` main-8626a35 (sha256
  `2f7e5fd6e0ae21fffcb9a4df6e70dc3302e2a372f1fde1eb2bb1aa106747a62e`), goldfish
  (`cecc76fbe51b33276e0e2e787b6eacba41c52ef4eaa36c5a20954caeedc50b66`), km3 on both sides (`--players km3,km3`; every
  result file must name `KM { max_depth: 3 }` for both players).
- **`analyze.py`:** the registered file, unchanged (blob `35f01a46a4a98e6c32f01a5960221dbcf4bda117`, sha256
  `6ae4ec850f0a4678e03620be15b0a001b49cd910bfb2e55829f16c6422903563`, as in `provenance.txt`). `analyze_wallace.py` imports
  it and edits nothing in it.
- **`decks/screen/floor.py` has changed since the main test.** 9e139e65 (Sonnet's drafts fixes) added the `ATTACKERS`
  table, the floor page's "main attacker" label for draft A. The main test ran with sha256 `8e5395e6…` (blob `ec133dab`);
  the file is now sha256 `763278659ea9a1ac7983c9cd2da2ff5f1f2c1e96468818cb84b29c106bb4b1e0` (blob
  `2f9f5b06ec40b982886afde76e361a7094d1e2fe`), and `run_wallace.sh` pins that. A check on Oct 2 (the two files' top-level
  definitions compared with Python's `ast`) found the change limited to the docstring, `ATTACKERS`, `main_attackers`,
  `self_check` and `main`. None of them is used by `analyze.py`, or by anything `analyze.py` uses from floor.py (it passes
  an empty attacker set). So the addendum's games are read exactly as the main test's were.

## 4. The deals: seeds, seats and size

- **The same 1,000 deals as the main test** (README section 4). The Wallace version in seat 0: seed 23,200,000,000 + i. In
  seat 1 (the Fire list in seat 0): 23,200,000,500 + i. i = 0 to 499. Calls of 50 with `--seed-stream`: chunk c (0 to 9) of
  seat s plays `--seed 23,200,000,000 + 500 × s + 50 × c --num 50`.
- **Size: 1,000 games, 500 per seat.** Fixed now: no games are added or dropped after looking.
- **Pairing.** Each Wallace game pairs with draft A's and with deck 13's recorded game on the same deal (same seed and
  seat), from the main test's `games/*.jsonl` (committed at 3e6cd559). Nothing of draft A or deck 13 is replayed.
  `run_wallace.sh` checks those 40 files are committed and unchanged; `analyze_wallace.py` checks they are the registered
  2,000 games.
- **Seeds:** the main test's block and deals, no new seeds except smokes: 23,200,900,004 and 23,200,900,005 (Oct 2, this
  addendum's 2-game smoke, the Wallace version in seat 0; files deleted; not part of the test).

## 5. How it runs (`run_wallace.sh`)

`bash rl/results/draft_A_v_fire_2026-10-02/run_wallace.sh` in WSL or the cloud, from a git checkout. `--plan` runs every
check except the commit checks and prints the 20 planned calls, playing and writing nothing.

1. **Refuses** before any game unless: this addendum, `run_wallace.sh`, `analyze_wallace.py` and the Wallace list are
   committed and unmodified; `README.md` and `analyze.py` are committed and unmodified, and `analyze.py` has the sha256
   above; the main test's 40 game files are committed and unmodified; the engine passes run.sh's checks
   (`current_engine.py`, the manifest's release main-8626a35, the deckgym and goldfish hashes); floor.py has the sha256 of
   section 3; the four lists have their pinned sha256 and blob ids. It also refuses a second copy of itself running.
2. **Records** in `wallace/provenance.txt`: the date, git HEAD, and the sha256 of deckgym, goldfish, floor.py,
   `analyze.py`, `analyze_wallace.py`, `run_wallace.sh`, this addendum, the README, `current_engine.py`,
   `project_manifest.json`, `lib/deckgym-database.json`, `engine/src/players/public_pricing_player.rs` and the four lists;
   Python, machine.
3. **Coverage:** the official goldfish's `--coverage` on the Wallace list (no game), into
   `wallace/coverage/wallace_coverage.json`.
4. **Games:** 20 calls (2 seats × 10 chunks), run.sh's command line with the Wallace list. `analyze_wallace.py extract`
   runs `analyze.py`'s own extraction with all its checks (50 result files, every game completed, the seeds exactly S to
   S + 49 inside the registered block, the card ids in each seat equal to the registered lists, km3 on both sides, the
   printed wins equal to the result files, one trace file per ply), adds the Wallace fields (section 6.W), and writes
   `wallace/games/wallace_s<seat>_c<NN>.jsonl`. The traces are deleted.
5. **Page:** `analyze_wallace.py report` writes `wallace/RESULTS.md`. It refuses unless the Wallace games are exactly the
   1,000 registered deals, none repeated, and the main test's games are its registered 2,000.

Resumable: a finished chunk is never replayed; every output is written as `.part` and renamed. The main test's own files
are only read; everything new goes in `wallace/`. Time: the main test's 2,000 games took 3 min 19 s (`run.log`), so expect
about 2 minutes.

## 6. The metrics

The README's section 6 definitions, applied to the Wallace version's 1,000 games by `analyze.py`'s own functions: 6.1 (win
rate), 6.3 (went first / went second, seat), 6.4 (attacks by own turn), 6.5 (Sharpedo's line: L1 to L5, L3v, L4v, the
lines through turn 2 and 3, the plan's line, own turn 2's Turbo Shark by where its Energy went, the first Turbo Shark by
own turn, the Bench-arming count and what it led to), 6.6 (coverage flags, from the Wallace list's own coverage file) and
6.7 (did Mega Sharpedo ex, Alolan Ninetales ex and Lapras attack at all). The README's 6.2 becomes the two comparisons of
section 7. The 6.5 tables are shown for the Wallace version beside draft A's recorded games on the same deals, so "quicker"
can be read straight off: L1 / L1w, L2, and the own turn of the first Turbo Shark.

**How the README's words treat Wallace.** An evolution by Wallace is the card's effect, not "an Evolve chosen" (the engine
has no Evolve decision for it). So L1, L4 and an arm's `evolved` count Evolves only, exactly as registered; section 6.W
adds the Wallace evolutions. Attacks, Turbo Shark and the Bench arming are counted the same way whichever route put Mega
Sharpedo ex into play.

### 6.W Wallace's own counts (new)

- **Wallace played:** a decision of the list whose chosen action is Play with Wallace (B3b 068). For each: its own turn
  and game turn (the README's words).
- **Target:** the Pokémon on the spot chosen at the list's next decision (the engine's `ChooseRandomEvolutionTarget`), and
  whether that spot is the Active Spot or the Bench.
- **Result:** at the next decision after that (either player's), that spot holds the same Pokémon (same first card) under
  a new name: "evolved into" that name; under the same name: "not evolved" (no Mega Sharpedo ex left in the deck). "No
  target choice" (no choice followed the Wallace) and "unknown" (no later decision, or the spot changed) are expected 0.
- **Per game:** **WP** Wallace was played; **W1** a Wallace on own turn 1 made Mega Sharpedo ex; **W2** a Wallace on own
  turn 2 or earlier made Mega Sharpedo ex; **L1w** = L1 or W2, Mega Sharpedo ex in play by own turn 2 by an Evolve or by
  Wallace. Draft A has no Wallace, so its L1w is its L1.
- **Shown:** WP, W1, W2, L1 and L1w as counts and shares of the 1,000 games (a game that ended before that own turn counts
  as no), for all games, going first and going second, with draft A's L1 beside; Wallaces by own turn (1 to 6, 7 or
  later); by target and spot; by result; games with more than one Wallace (expected 0: the list has one); the win rate in
  games with W2 and without (descriptive only, not cause and effect).

## 7. The comparisons, intervals and readings

- **The Wallace version v draft A, paired on the same deals.** For each deal d: D(d) = (the Wallace version won d: 1 or 0)
  − (draft A won d: 1 or 0). The mean of D over the 1,000 deals ± 1.96 × s / √n, s the standard deviation of D (divisor
  n − 1): the README's section 7 interval. Also: the deals both won, only one won (each way), neither won; the same mean for
  each seat alone (descriptive); and the deals on which the two lists did not both go first or both go second.
- **The Wallace version v deck 13, paired on the same deals.** The same, with D(d) = (the Wallace version won d) − (deck 13
  won d).
- **Each win rate** with its 95% Wilson interval (README section 7). Draws are not wins.
- **Readings, fixed now, descriptive, with no adoption decision.** For each of the two comparisons:
  - the paired interval lies entirely above zero: the Wallace version beat the Fire list more often than the other list
    did on the same deals, by more than the paired interval;
  - the paired interval includes zero: no difference seen;
  - the paired interval lies entirely below zero: the other list beat the Fire list more often on the same deals.
  Beside each reading, and not changing it: if the point difference is under 5 points, the page says so (START_HERE calls
  a difference that size noise for two versions of one shell, which the Wallace version and draft A are). Secondary:
  whether the Wallace version's own Wilson interval lies above 50%, below it, or around it.
- The two comparisons share the Wallace games, and the main test already compared draft A with deck 13. The readings are
  descriptive and are not adjusted for that.

## 8. What this is not

Not a ranking. Not a ladder forecast. One opponent list (the Charizard Y / Entei list, not Blaziken, not the other Fire
lists on the ladder), played by the bot on both sides. A better number for the Wallace version would say Wallace helps km3
with this list against this list, and nothing more. Nothing here adopts, drops or ranks a list; what to do with the result
is Dustin's call.

## 9. Files

- This registration: `ADDENDUM_WALLACE.md`, `run_wallace.sh`, `analyze_wallace.py` (`python3 analyze_wallace.py
  --self-test` runs `analyze.py`'s self-test, then, on made-up games (no engine game), a Wallace that evolved, one that
  didn't and one with no target choice, W1, W2 and L1w beside L1 and L2, and that the list is draft A with one Misty
  swapped for one Wallace), and the list `decks/brews/drafts_2026-10-01/draft-A-wallace.txt`.
- After the run: `wallace/provenance.txt`, `wallace/run.log`, `wallace/coverage/wallace_coverage.json`,
  `wallace/games/*.jsonl` (20 files), `wallace/RESULTS.md`. If `analyze_wallace.py` and this addendum ever disagree on a
  definition, this addendum (with the README it points to) is the registration and the page is the thing to fix.
