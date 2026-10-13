# Step 4's kx3 replay check: registrations and shards (Oct 12)

Registered on the laptop on Oct 12 (`--repo .`, program /home/dacz8976/kx_r2/strength, sha256 76df495b). In every registration the
self-checks equal the slow-report pin's: km3 81b572198c04d5d1, kx3 31d638dbc818b0fa.

| registration | decks v opponents | deals | games (kx3 + km3) | manifest sha256 |
|---|---|---|---|---|
| replay_a | 09, 06, 10 v the 8 panel lists | 0-1 | 96 + 96 | 51a502f5… |
| replay_b | 01, 05, draft A v the 8 panel lists | 0-1 | 96 + 96 | 977afc71… |
| replay_c | 10 v t-weezing (Will's row) | 0-4 | 10 + 10 | 2219f8ff… |

**For the workers (Managed Agents, `../thinking_time_2026-10/WORKER_BRIEF_MA.md`), with these differences:**
- build `rl/strength/build.sh cd20a97a2e76897fae9883389cee4bf7ce5b3d97 $HOME/kx_r2/strength` (branch laptop/kx3-on-rules2);
- it must print engine tree `4ebb30a94173…` and harness `bf9c5d6814007f1f`;
- the stamp's self-check must print km3 `81b572198c04d5d1` and kx3 `31d638dbc818b0fa`;
- REG is `rl/results/kx3_on_rules2_2026-10/replay_<x>`, and the worker folders are `rl/results/kx3_on_rules2_2026-10/workers/<W>_<reg>_<deck>`.

**Shards.** Estimated wall hours are the frozen kx3's laptop time per game (the development run) × 2.7 for a sandbox ÷ 2 for
`--threads 2`. Each worker adds about 3 h of setup: the build, then the stamp's two self-checks, kx3 about 2 h.

| worker | slices, in order | est. play h |
|---|---|---:|
| R1 | replay_b 05-indeedee-stoutland; replay_c 10-xatu-oricorio-tr-weezing | 4.0 + 0.5 |
| R2 | replay_b 01-muk-glimmora-kingambit-regigigas; replay_a 09-mega-manectric-heliolisk | 3.8 + 1.2 |
| R3 | replay_b draft-A-shark-tempo; replay_a 10-xatu-oricorio-tr-weezing; replay_a 06-mega-blaziken-tournament-list | 1.9 + 1.5 + 1.0 |

**Reading, fixed in SPEC.md section 4:**
- Every game is compared by key with the development run's game (`split_collect.py compare`, content without timing), and every
  pair must be equal, except deck 10 v t-weezing.
- There, each changed game must show Will's new rule acting (round 2's `will_*` counters at or before the first difference), or
  kx3 seeing it in its search.
- Any other change is a stop that goes to Dustin.
- The km3 games are also checked against the development run's, as a build check.
