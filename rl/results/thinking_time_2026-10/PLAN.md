# The thinking-time test: the pre-registration (written Oct 11, before any game)

Approved by the coordinator on Oct 11 as designed. It is registered with `strength_prereg.py` on Monday after the reset, and played on the
cloud fleet in shards through the collector (`SHARDS.md`, `WORKER_BRIEF.md`). This file is fixed before any game; the registrations'
PREREGISTRATION.md files point here for PRIMARY and the reading.

**Question.** The combined candidate (kx3 `_tools _zs3 _m64`) beat the frozen kx3 by +3.9 ± 3.1 points per 100 games, but takes about 2.9
times as long per game (`../strength_2026-10-08_kx3_combined/PAIR_COMBINED.txt`). How much of that gain is kept with less thinking? Dustin
wants a fast screener plus a slower, more accurate deck tester, ideally no slower than a real game (Oct 10).

**Settings** (one program, the combined run's: claude/playout-pilot 172cbe9c, laptop build sha256 f5a6ae95...; the suffixes are the pilot
code's parameters, `playout_player.rs:131`; `_m` must be above R = 16):
- **m32:** `kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m32`: close calls play on to 32 play-outs, not 64.
- **m16:** `kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3`: no extension (16 play-outs), with the Tool rule and the 3-standard-error bar.
- Already played, reused, no new games: the **frozen kx3** (the development run's arm X, `../strength_2026-10-03_kx3_dev/`) and the
  **candidate m64** (the combined run's arm X).

**Decks and deals.** The six development decks without Wailord (Dustin, Oct 10: "we could maybe stop using it in future tests"), against
the same 8 opponents, 5 deals, both seats, on the development run's own seeds: 480 kx3 games per setting, each paired with its frozen and
candidate game on the same key, plus 480 km3 reference games per setting (about a second each). Because the harness numbers a deck's seeds
by its place in the list (`rl/strength/src/main.rs:229-233`), each setting is two registrations:
- slice **a**: 09 Manectric, 06 Blaziken, 10 Xatu at seed_base 24,400,000,000 (the development run's);
- slice **b**: 01 Muk, 05 Indeedee-Stoutland, draft A at seed_base 24,440,000,000 (= 24,400,000,000 + 4 × 1,000 × 10,000: the seeds those
  decks had at places 4-6).
`make_think_configs.py` writes the four configs (`configs/`) and checked that all 960 keys of a setting get the development run's seed. The
seeds are the development run's own, reused on purpose for the pairing: no new seed block.

**Registration.** On the laptop, from the repository root, `python3 rl/strength/strength_prereg.py --config rl/results/thinking_time_2026-10/configs/config_<setting>_<slice>.json
--out rl/results/thinking_time_2026-10/reg_<setting>_<slice> --repo .`. `--repo .` records `repo_root` as `.`, so each worker's harness and stamp read the decks in its own
checkout (the harness loads decks under the manifest's repo_root). Each registration plays the 12-game self-check for km3 and its setting, on
the combined run's program (sha256 f5a6ae95...).

**Build check.** Every km3 game must replay the development run's game for game (`split_collect.py compare`, by key), or the pairing is void.

**PRIMARY.** For each setting S: S − frozen, in game score (win 1, tie ½, loss 0), on the same (deck, opponent, deal, seat): mean ± 1.96
sd/√n over the 480 pairs. Also, on the same 480 pairs: S − candidate (what the cheaper setting loses), and candidate − frozen (the reference).
Each is reported pooled, every deck weighted equally, per group (fast: 09, 06, 10; setup: 01, 05; draft A in the middle) and per deck, with
pace (turns per game, first-attack own turn) and time per kx3 game.

**Reading, fixed now.**
- The recommended deck tester is the cheapest setting (by play-out cap: m16, then m32, then the full candidate m64) whose S − frozen
  interval is entirely above zero. If neither cheaper setting's is, the full candidate stays the recommendation.
- The frozen kx3 stays the screener.
- Dustin picks from the table (gain over frozen, loss against the candidate, time per game). The held-out exam then runs his pick.
- A deck whose interval is entirely below zero is reported, not a veto. Nothing is read from a part of the run.

**Time.** The order of cost is by construction (fewer play-outs). Time per game is reported per worker as measured. The cloud ran about 2.4
times slower than the laptop on earlier work, so laptop-speed figures are labelled as estimates. Estimates before play (laptop speed): m32
about 1.7 times the frozen kx3, m16 about 1.05 times; about 41 and 26 laptop game-hours, about 160 cloud game-hours for both.
