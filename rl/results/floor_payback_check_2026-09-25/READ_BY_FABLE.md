# Second read of the Payback pre-use check (Fable, separate session, Sept 25, 13:30 to 14:00)

**Result: the second read agrees. The check passes.** Both Payback lists read "fail" and the k3 control reads "untrusted", on the laptop's run and on my re-runs. Nothing was built; the only commands run were the verification commands below, from the repo root in WSL, on the official engine as pinned.

## What was checked and what it showed

1. **Hashes and commits.** `rl/engine-2026-09-25/deckgym` sha256 f4d235e596cdd713546c17450fd66bd9d5eefe4baf53e93d66d8bbe1628e1034 and `rl/engine-2026-09-25/goldfish` sha256 318c82c897f08a376e836bd23f68d1aa53d8312adc00b04603137a6c86dbe997, both as named in `project_manifest.json`'s available release and on every page. `decks/screen/floor.py` in the working tree is identical to its commit dc17627 (`git diff --stat dc17627 -- decks/screen/floor.py` is empty). The check's pass and fail were committed in 32b3d6a before any game; the results are 94ebe02.

2. **Every page line reproduced from the saved per-game records.** My own recount of `<deck>_games.jsonl` (wins by opponent and seat, converted to the engine's "player 0 won / player 1 won / draws" form) matches all sixteen per-call lines on each of the five pages, the totals (brew-06 128, brew-06b 281, deck 14 control 195, brew-05b 597, deck 07 908 of 1,920), the draw counts, and the verdict edges (349 or fewer fail, 350 to 418 borderline, 419 or more clear). Each file holds 1,920 distinct (seed, seat, opponent) records.

3. **A plain `run_screen.py` at 240 games per matchup, same seeds, both Payback lists** (the laptop's own command, run again by me): brew-06 128 of 1,920 and brew-06b 281 of 1,920, with per-opponent wins identical to the laptop's `run_screen.txt` and equal to the sum of each page's two per-call lines for that opponent. Tracing changed no game.

4. **Two calls re-run by seed with results output** (`deckgym simulate --num 120 --players kp3,kp3 --seed-stream --results-output ... -p`): t-altaria with the deck in seat 0 (seed 7100) and t-sceptile with the deck in seat 1 (seed 11600). Matched game by game on `randomness.game_seed` against the saved records: 120 of 120 and 120 of 120 agree on winner, draw, final turn and final points (the records store points in player order). The deck's wins in the re-runs, 13 and 2, are the page's lines.

5. **A flagged card recounted from a trace with my own parser.** The t-altaria seat-0 call re-run with `--data-output`: over its 120 games, a Silvally attack was offered while Silvally was the deck's Active on 75 turns and chosen on all 75. Consistent with the page's total of 595 used of 597 opportunities over all sixteen calls (99.7%); not an exact reproduction of that total, see the limitation below.

6. **The flagged sets against the coverage files and the lists.** brew-06's coverage file has 13 entries, one per distinct card in the list; its flags are Pyukumuku (Innards Out pays off on the opponent's turn), Rocky Helmet (pays off on the opponent's turn), Silvally (Gold Breaker estimated at printed damage) and Copycat (unpriced text); Copycat drops out under kp3 because its text is among the 62 audited texts in `engine/src/players/public_pricing_player.rs` (a sorted array of exactly 62 strings, binary-searched), so the page's three flagged cards are right. brew-06b likewise: 13 entries, flags Pyukumuku, Rocky Helmet, Silvally, Team Rocket's Scyther (Second Strike at printed damage), and Copycat dropping out; the page's four are right. The control page under k3 flags Copycat and Thieving Incisors, both correctly, since k3 does not price them.

7. **The control reads "control reading, not a floor verdict (pilots k3 on the deck and k3 on the panel, not kp3 on both): untrusted"**, with Team Rocket's Raticate ex as an activated ability used on 50 of 1,628 opportunities (3.1%), inside the 3 to 5% the brew pilot check measured. Team Rocket's Goo-zooka is also under 25% (64 of 4,510), as the README says.

## Two notes on the procedure, not on the result

- The per-game records (`<deck>_games.jsonl`) carry wins, points, turns and the harness fields but not the per-card opportunity and use counts, so the README's "hand recount of one flagged card from `<deck>_games.jsonl`" cannot be done as written. The counts can only be rechecked by re-tracing games, which is what item 5 does for one call. An exact recount of a page's totals would need either per-call counts written by `floor.py` (into the jsonl or the page) or a full re-trace of all sixteen calls (about 9 GB of traces at 1,920 games). Suggest `floor.py` writes the per-call counts per flagged card; then a reader can re-trace one call and compare exactly.
- The laptop was running kd's mixed rows at the same time, so my plain screen run took about 10 minutes and the re-runs about a minute; that changes nothing in the results, which are seeded.

## Commands (run from the repo root in WSL)

```
python3 decks/screen/run_screen.py decks/brews/brew-06-pyukumuku-silvally-payback.txt decks/brews/brew-06b-pyukumuku-silvally-scyther-grass.txt --games 240
rl/engine-2026-09-25/deckgym simulate --num 120 --players kp3,kp3 --seed 7100 --seed-stream --data-output <scratch>/data_altaria_seat0 --results-output <scratch>/res_altaria_seat0 -p decks/brews/brew-06-pyukumuku-silvally-payback.txt decks/screen/opponents/t-altaria.txt
rl/engine-2026-09-25/deckgym simulate --num 120 --players kp3,kp3 --seed 11600 --seed-stream --results-output <scratch>/res_sceptile_seat1 -p decks/screen/opponents/t-sceptile.txt decks/brews/brew-06-pyukumuku-silvally-payback.txt
```

The recount, comparison and trace-count scripts are in this session's scratch folder and are trivial (a few dozen lines each); they are not added to the repo.
