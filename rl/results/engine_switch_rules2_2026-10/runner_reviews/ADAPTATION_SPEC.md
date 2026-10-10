# Rules switch 2: adapting the Oct 1 runners (spec for the implementers)

Written Oct 9, late evening, by the spec writer. Read-only: nothing was built, played, fetched, committed or pushed. Every
git fact is as last fetched on the laptop: `origin/claude/coin-prevention-round2` tip **31616338** (22:14 UTC Oct 9, the (e)
revert switches), `main` = `origin/main` = **7f45d110**.

Sources: `rl/results/engine_switch_rules2_2026-10/PLAN.md` ("PLAN Lnn" = its line), `RELEASE_PACKAGE.md`, the old folder
`rl/results/engine_switch_rules_2026-10/` (its README.md and runners; "old sitting1.sh:Lnn" = the line as read), and the
branch (`git show`): `coin_prevention_repair_2026-09-30/instrument_scan.py`, `engine_switch_rules2_2026-10/early_warning_8b/`,
`round2_readiness_2026-10-02/counter_smoke/pairs.tsv`, `coin_prevention_round2_2026-10-01/revert_switches/`,
`engine/src/actions/apply_action_helpers.rs`.

Section 0 of PLAN wins over sections 1-9 (PLAN L3). Where this spec departs from PLAN's letter, section 14 says so and why.

---

## 0. The files and a suggested split

All copies go in `O = rl/results/engine_switch_rules2_2026-10/` (pin scripts in `O/pin/`). The old folder is read, never written.

| Implementer | Files (copied from the old folder, then adapted) | Changes |
|---|---|---|
| A | `sitting1.sh`, `sitting1_check.py`, `switch_check.py`; `floor_with.py` (byte copy); **the shared data files** (Appendix A) | 31 + 9 + 2 items |
| B | `sitting2.sh`, `sitting2_check.py` | 32 + 12 items |
| C | `pin/pin_rules.sh`, `pin/update_manifest_rules.py`, `pin/README.md` (adapted); `checkpoint.sh`, `quiet.sh`, `.gitignore` (byte copies) | 20 + 9 + 1 items |

Item counts include a few items that only say "unchanged" (S1-8, S1-25, S2-9, S2-10, S2-28, C1-7, C1-8, C2-9, C2-12), kept so
nobody re-derives them. A writes the data files first; B and C read them and never hard-code a value that is in them.

---

## 1. The shared convention (all three implementers)

### 1.1 Paths
- `R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"`, `REL=rl/results/engine_switch_rules2_2026-10`, `O="$R/$REL"`.
- `OLDREL=rl/results/engine_switch_rules_2026-10` (the Oct 1 switch's folder: read-only input; its reused game files,
  `pairs_8.tsv`, `pairs_7c.tsv`, `seeds_8.txt`, `carriers/`, `scratch_8b/` are read there, in place, blob-checked).
- Build folders on the WSL disk: `B=/home/dacz8976/engine-rules2-<S>`, `W=/home/dacz8976/engine-rules2-watch-<S>`
  (`S` = the candidate's first 7 hex). The `2` keeps them apart from the Oct 1 folders `engine-rules-5a18d31*`.
- Candidate ref: `refs/pocketdecksim/rules-switch2-candidate` (the Oct 1 ref `rules-switch-candidate` stays as it is).
- Locks and flags (unchanged names, now in `O`): `.sitting1.lock|.ours|.pgid|.ckpt|.hardstop`, the same for `.sitting2.*`;
  pin lock `/tmp/pocketdecksim_pin_rules2_2026-10.lock`.

### 1.2 Data files (committed in `O`, read at every start and by `--dry-run`, never written by a runner)
Formats and exact contents are in Appendix A. Rules every reader follows:
- **No shell evaluation.** `switch2.env` is `KEY=VALUE` lines read with a strict regex `^([A-Z0-9_]+)=([^ ]*)$`, never `source`d.
  `.tsv` files: `#` comment lines, then a header row, then tab-separated rows.
- **The marker.** A file whose first line starts `# TO FINALIZE` is not final. A value `TO_FINALIZE` in `switch2.env` is not set.
  A runner refuses to start (exit 2, "start refused: <file>: <key> is TO FINALIZE (PLAN: P is not final yet)") when a file or
  key **it needs** carries the marker; `--dry-run` prints each marker as a NOTE and goes on, so the dry run is usable now.
  Needs: sitting 1: `P`, `P_TREE`, `COIN_SCRIPT_BLOB`, `SUITE_AT_P`, `allowed_engine_files.tsv`, `engine_commits.tsv`,
  `counters.tsv`, `floor_7c.tsv`; sitting 2: the same plus `MAGNEZONE_CARD_CHECK`, `tools_8c.tsv`, `reuse.tsv`; the pin:
  everything, `ENGINE_DIR` and `FR_REL` included.
- **Checked, not trusted.** Every value is checked against git at the start (dry run too): e.g. `allowed_engine_files.tsv` must
  equal `git diff --no-renames --name-status <OFFICIAL> <P> -- engine/` exactly (paths and statuses), `engine_commits.tsv` must
  equal `git log --format=%H <OFFICIAL>..<P> -- engine/` as a set, `counters.tsv` must equal the names the candidate's two
  instrument scripts write (section 1.11). A mismatch is "start refused" (before any candidate exists) or a HALT (after).
- The START line of each sitting carries the sha256 (16 hex) of every data file, as it carries the scripts'.
- Each data file is a helper for the "committed as it is here" start check (old sitting1.sh:L932-936).

### 1.3 Parameters (environment knobs; the same names and defaults in both sittings)
| Knob | Default | Meaning |
|---|---|---|
| `THREADS` | 14 | `RAYON_NUM_THREADS` for legality_scan |
| `NICE` | 10 | nice for every game program and build |
| `JOBS` | 14 | cargo jobs (sitting 1) |
| `DEADLINE` | `school` | the latest time a step may **end** by its estimate (= "no new game after"); `school`, `HH:MM` (UTC, the next one), an ISO time, or `off` |
| `SCHOOL_CUT` | `10:15` | the UTC time `school` uses (5:15 am CDT) |
| `HARD_STOP` | `auto` | the watchdog's stop; `auto` = DEADLINE itself (a step still going at 5:15 stops cleanly, PLAN L28); or `HH:MM`, ISO, `off` |
| `PUSH_BY` | `auto` | the time the record must be pushed by; `auto` = DEADLINE + 105 min (12:00 UTC = 7:00 am CDT for 10:15); or `HH:MM`, ISO |
| `ALLOW_DAYTIME` | `1` | `0` brings back the Oct 1 refusal of a start between 11:30 and 21:00 UTC without an explicit DEADLINE |
| `BUSY_OK` | `0` | `1` lets a sitting start beside another game program or launch_detached run (noted); default refuses (PLAN L356: "never beside a sitting") |
| `RATE`, `SAFETY`, `OVERHEAD_MIN`, `EST5_MIN`, `EST6_MIN` | 8.6, 1.25, 10, 40, 25 | as Oct 1 (timing.tsv is new in `O`, so RATE holds until 2,000 games are timed) |
| `SITTING1_AFTER_HALT`, `SITTING2_AFTER_HALT` | unset | as Oct 1 |
| `PIN_AFTER_HALT`, `PIN_DUSTIN`, `PIN_CHECK_WITHOUT_8C`, `PIN_BUILD_DIR` | unset | pin only (section 10) |

### 1.4 The deadline (one function, copied verbatim into both sittings)
- `DEADLINE=school` (default): the first **Monday-Friday** `SCHOOL_CUT` (UTC) strictly after the start. A run started Saturday or
  Sunday gets Monday Oct 12 10:15 UTC; weekend mornings have no cut (Dustin, Oct 9: the laptop over the weekend; the rule applies
  Monday, PLAN L27-29). Bash: for k in 0..7, `d=$(date -u -d "@$((T0 + k*86400))" +%F)`, `t=$(date -u -d "$d $SCHOOL_CUT" +%s)`,
  `dow=$(date -u -d "$d" +%u)`; the first `dow <= 5 && t > T0` wins.
- `HARD_STOP=auto` -> `HS=DL` (was `DL + 1200` in sitting 1, old L282, and `DL + 600` in sitting 2, old sitting2.sh:L232).
- `PUSH_BY=auto` -> `PB=DL + 6300`. `push_lim` (old sitting1.sh:L365-372, sitting2.sh:L339-346) uses `PB` where it used
  `DL + 1800`: past DL, `l = (PB - now) / 4`, bounded `[30, max]`.
- `DEADLINE=off`: `DL=0`, `HS=0` (no watchdog) unless HARD_STOP is given, `PB=0` (push_lim returns its max), as Oct 1's `off`.
- The step-start estimate (old `begin_step`, L824-830) is unchanged: a step whose estimate ends after DL is not started
  (PAUSED). The KNOBS text and the START line name DL, HS and PB in UTC.

### 1.5 STATUS lines and exit codes
- Grammar unchanged from Oct 1 (old sitting1.sh:L100-120): `SITTING n START|HALT|STOPPED|PAUSED|DONE|NOT PUSHED|RESUMED AFTER
  HALT`, `STEP <n> DONE <S> <time> <summary>`, in `O/STATUS.txt`; HALT/STOPPED/PAUSED/DONE/NOT PUSHED also in `O/PIN_STATUS.txt`;
  never the words FAILED or MISMATCH (reword as old L295-299). Step ids: sitting 1 `4 5 6 7 7b 7c-seeds 7c`; sitting 2
  `8-seeds 8b 8 9 10` (`8c` is the gate's STEP label only, as Oct 1).
- Every STEP line of 7c, 8b, 8 and 9 contains exactly one phrase `changed <N> of <M> deals` (7c: its named row only; `changed 0 of
  ...` when none). The pin sums them (section 10).
- **Exit codes (new, so a chain `sitting1.sh && sitting2.sh` under launch_detached is safe):** 0 DONE or "already DONE"; 1 HALT
  or STOPPED; 2 start refused or usage; **3 PAUSED** (old L829 and sitting2.sh:L804 exit 0 on PAUSED: change to `exit 3`).
- Sitting 2 refuses (exit 2, no HALT line) when sitting 1 is not DONE yet; it halts only when sitting 1's evidence does not
  match its record (old sitting2.sh:L431-432 halts on both: split them).

### 1.6 Checkpoints
`checkpoint.sh` is a byte copy (section 13). Commit titles: `Rules switch 2 sitting <n>, <title> (rl/results/engine_switch_rules2_2026-10 only)`.
Body names `Candidate <C> (main <M7> + P <P7>)`. The push rules, the private index and the shared-index exception are Oct 1's.

### 1.7 Seeds and pairings (seed = base + pairing x 10,000 + i, legality_scan reads the pairing from the pairs file, L615-619)
| Block | Pairings | Rows | Deals | Source |
|---|---|---|---|---|
| 23,100,000,000 (Oct 1's, registered) | 0-31 | step 8 carriers (Oct 1's, replayed new + watch; old reused) | km3 500, k3 250 | `OLDREL/pairs_8.tsv` (blob 3ef02030) |
| 23,100,000,000 | 32-35 | 8b Oct 1's scratch rows (old reused) | 40 | the cloud's `early_warning_8b/pairs_8b.tsv` (= old pairs_8.tsv rows 32-35) |
| 23,100,000,000 | **36-37** | 8b brew-07 / brew-09 v t-altaria (the cloud's rows) | 40 | the cloud's `pairs_8b.tsv` (blob 0f6f4e37) |
| 23,100,000,000 | 40-71 | 7c Oct 1's 32 rows (decks 02/06/08/14 v panel) | 60 | `OLDREL/pairs_7c.tsv` (blob d747cf5f) |
| **23,300,000,000 (new)** | 0-23 | 7c new rows: deck 10 (0-7), D first list (8-15), D amended (16-23), each v the 8 sorted panel lists | 60 | `O/pairs_7c2.tsv` (sitting 1 writes it at 7c-seeds) |
| 23,300,000,000 | 40-46 | 8b new rows: 40 deck 12 v t-weezing, 41 deck 12 v t-lucario, 42 deck 10 v t-weezing, 43 brew-04 v t-weezing, 44 water_round2 v meowth_carefree, 45 houndoom_victini v c-magnezone, 46 deck 10 v c-magnezone | 40 | `O/pairs_8b2.tsv` (sitting 2, 8-seeds) |
| 23,300,000,000 | 60-62 | step 8 Will rows: 60 deck 10, 61 brew-01, 62 brew-04, each v t-weezing | km3 500, k3 250 | `O/pairs_will.tsv` (sitting 2, 8-seeds) |

Pairings 24-39, 47-59, 63-99 of the new block are unused. Panel order is `sorted(glob decks/screen/opponents/t-*.txt)`:
t-altaria 0, t-blaziken 1, t-hydreigon 2, t-lucario 3, t-sceptile 4, t-suicune 5, t-vespiquen 6, t-weezing 7 (so deck 10 v
t-weezing in 7c2 is pairing 7). The start check (old sitting1.sh:L944-945, sitting2.sh:L1135-1136) becomes: the committed
`START_HERE.md` has a line holding `23,300,000,000` **and** `36–37` (the row drafted in `seed_row_23_3B.md` names both).
The 36-37 rows' seed base is read from the cloud's pairs file (`seed_first - 10,000 x pairing`, the same for every row) and must
be 23,100,000,000; if the cloud replays them on 23.3B (its README offers to), the file and the runner follow without an edit.

### 1.8 Programs and the environment
- New (plain): `B/engine/target/release/{deckgym,examples/legality_scan,examples/goldfish}`; watch: `W/.../examples/legality_scan`.
- Old: `rl/engine-2026-10-02/{deckgym,legality_scan,goldfish}` (main-8626a35; sha256 in `switch2.env`); `project_manifest.json`'s
  `available_release.name` must be `main-8626a35` with those paths and hashes.
- **Environment hygiene (new, both sittings and the pin).** At P the engine reads 13 process-wide switches
  (`apply_action_helpers.rs`:618-745 at 31616338): `DECKGYM_ROUND2_OFF`, `DECKGYM_FLAT_RETURN_DAMAGE`, `DECKGYM_NO_PLAIN_HIT_COIN`,
  `DECKGYM_PLAIN_QUEUED_SITES`, `DECKGYM_NO_OWN_SIDE_COIN`, `DECKGYM_WILL_SKIPS_GATE_COINS`,
  `DECKGYM_NO_VICTORY_STAR_AFTER_BLOCK_COIN`, `DECKGYM_TRAP_TERRITORY_ONCE`, `DECKGYM_NO_OWN_SIDE_GUTS`,
  `DECKGYM_NO_PERISH_ON_QUEUED_HIT`, `DECKGYM_LUXURY_COIN_ANY_STADIUM`, `DECKGYM_FOSSIL_UNDER_ITEM_LOCK`, `DECKGYM_FOSSIL_NOT_ITEM`
  (and the older `DECKGYM_UNBOUNDED_ENERGY_MOVES`). One left set would play another engine and still pass every program hash.
  A start is refused when any variable matching `^DECKGYM_` or named `PDL_EQUIV_DEALS` or `GOLDFISH_TRACE` is set; the START
  line says `env: no DECKGYM_* set`. The dry run lists any it finds.

### 1.9 Starting a sitting (launch_detached)
Usage text in both headers (replaces old sitting1.sh:L159-160, sitting2.sh:L127-128):
```
bash rl/strength/launch_detached.sh start rules2-sitting1 --dir "$R" -- bash "$R/rl/results/engine_switch_rules2_2026-10/sitting1.sh"
bash rl/strength/launch_detached.sh start rules2-sitting2 --dir "$R" -- bash "$R/rl/results/engine_switch_rules2_2026-10/sitting2.sh"
# or both in one: -- bash -c 'bash .../sitting1.sh && bash .../sitting2.sh'   (exit 3 = PAUSED stops the chain)
```
launch_detached gives the run its own session and group (`setsid nohup`, stdin `/dev/null`, log `$HOME/runs/<NAME>.log`), so
the old re-exec (`exec setsid`, old L179-181) is skipped there and kept for a plain `bash sitting1.sh`. A TERM from
`launch_detached.sh stop` is the runner's STOPPED (old trap L971). HUP is ignored on entry under nohup and cannot be re-trapped;
that is fine. Resumption after a stop or a WSL restart is Oct 1's: kept complete game files are reused, `/tmp` copies are made
again, stale `.ckpt`/`.hardstop` flags are removed at start.
`BUSY_OK=0` check (new, before the START line): refuse when a process named `legality_scan`, `deckgym`, `goldfish`, `cargo`,
`rustc` or `tool_census` runs outside this run's process group, or when `$HOME/runs/*.pid` names a live launch_detached run other
than this one (its own name is in `LAUNCH_DETACHED_RUN`); the 2-day combined run must have ended.

### 1.10 Reserved names in `O` (the pin's merge would conflict)
P's branch already has files in this same folder: `early_warning_8b/**`, `tightened_rule.py`, `test_tightened_rule.py`,
`tests_after_tightened_rule.log`, `tests_before_tightened_rule.log` (and whatever (a) adds). If main's `O` holds one of those paths
with other bytes, `git merge-tree` of main and P stops with a conflict at step 4 and at the pin. Rules:
- No runner, data file or copy uses those names. PLAN L241's "copies of `tightened_rule.py`, `classify_8c.py` and
  `coin_lookahead.py` go in this folder" must not be done under those names (the cloud's `tightened_rule.py` lands here by the merge).
- Copies taken from the candidate get new names: the cloud's pairs file -> `O/pairs_8b_cloud.tsv`; `water_round2.txt` ->
  `O/scratch_8b2/water_round2.txt`; D's first list -> `O/floor_7c/d_first/draft-D-entei-grimhound.txt`.
- Both dry runs and step 4 check: `git ls-tree -r --name-only <P> -- $REL/` intersected with main's and the working copy's paths
  under `$REL` is empty, or each shared path has the same blob.

### 1.11 The counter model (`counters.tsv`, Appendix A.4)
The watch build writes 42 counters (both scripts, read from the cloud's watch rows at P's branch and the coin script's
`R2_COUNTERS`/`R2_KEYED` lists, lines 562-570 at 31616338). Roles:
- `reach2` (16, PLAN L289 plus section 0's P2 counter): `coin_queued_by_attack`* `coin_plain_damage_by_attack`
  `coin_plain_damage_chosen` `perish_plain_hit_offered` `perish_plain_hit_chosen` `coin_own_side_split` `guts_own_side_split`
  `will_confused_attack` `will_block_coin_attack` `vs_block_coin_built` `vs_block_coin_choice_offered`
  `trap_territory_offer_changed` `trap_territory_outcome_changed` `luxury_coin_opp_stadium` `fossil_item_lock`
  `attack_return_weakness`. *For reach, `coin_queued_by_attack` counts only the keys in ROUND2_QUEUED: `Wild Swing`,
  `Wellspring Dance`, `Tornado Shot`, `Double Splash`, `Triple Bombardment`, `Mischievous Ring`, `Litter`,
  `Double-Punching Family` (the cloud's `tightened_rule.py`, this folder on the branch); for the 7b zero check, every key counts.
- `offgate2` (10): `offgate_by_attack` (keyed) `offgate_plain_attack_damage` `offgate_guts_opponent_split`
  `offgate_confused_attack` `offgate_block_coin_attack` `offgate_vs_ungated_built` `offgate_trap_territory_one`
  `offgate_luxury_coin_offered` `offgate_fossil_offered` `offgate_return_by_source` (keyed).
- `superset2` (1): `trap_territory_two_in_play`. Never reach (PLAN L289).
- round 1 (15, both engines have round 1, so never reach for this switch): `r1_exact` `vs_confusion_first_built`
  `vs_confused_choice_chosen` `vs_confused_choice_offered` `coin_cut_recorded` `coin_full_prevention` `coin_queued_offered`
  `coin_queued_offered_any`; `r1_heads` `vs_confused_choice` (int) `vs_confused_choice_first` (int or null); `r1_offgate`
  `offgate_helper_choice` `offgate_discard_then_damage` `offgate_helper_by_mechanic` (keyed; its union must equal
  offgate_helper_choice's ticks, old sitting1_check.py:L93-101); `r1_superset` `vs_confused_attack` `coin_defender_attack`
  `coin_queued_attack_damage` (ints).
- Shapes: `exact` = `{"n","first","ticks"}` checked as old `as_exact` (L77-90); `keyed` = `{key: [ascending int ticks]}`, fired
  when any list is non-empty; `int`; `int_or_null`. A missing or malformed counter is exit 2 (not the watch build's output).
- Uncounted parts (no counter; a report line only): P3's seven Fossil-as-Item places, Bounded Field x2, P1's caveat text, the
  Victini caveat text. No replayed list reaches them (PLAN L178, L343; RELEASE_PACKAGE "Recorded").

### 1.12 Changed games: categories and the hand-off
A changed game (new differs from old on a field the old file records) in a **named row** (PLAN L280: 8b, 8, 9's pairings 32-39
and 80-87, and deck 10 v t-weezing in 7c) gets one category from its watch row:
`reach` (a reach2 counter fired) / `offgate_only` (no reach2, an offgate2 fired: **CONDITION 3**, the Oct 1 ruling carried by
Dustin's yes to question 1, PLAN L294, L333) / `other_only` (only round-1 or superset counters, or round-1 keys of
coin_queued_by_attack) / `none` (no counter at all).
**None of the four halts the runner** (section 14, A7): every row goes to `handoff_8c.tsv`, and 8c decides by PLAN L288-291
(on the board at the first difference, or lookahead with both halves and the revert check; otherwise a stop). The runner still
halts on: watch not equal to new, a missing, extra or repeated deal, a malformed counter, and any changed game in a row named
equal.

---

## 2. Known values (use these; each is also in `switch2.env` or a .tsv)

| What | Value | Where from |
|---|---|---|
| Official engine (old side) | main-8626a35 = `8626a35861b88ae86a70c2386d47f9d765cfa2bc`, engine/ tree `38af8b0cc4f35fdccc647ed540a56ec8f5e6c1d5` | main, manifest |
| Main now | `7f45d110f768b4bb5cb0a58c19417fad63b235d5`, engine/ tree 38af8b0 (unchanged) | git |
| Old programs | `rl/engine-2026-10-02/`: deckgym `2f7e5fd6e0ae21fffcb9a4df6e70dc3302e2a372f1fde1eb2bb1aa106747a62e`, legality_scan `978912748c83fd6c8ee8e3e966c9a6b95c9fdf1eb9d500c7367b2c1463e71699`, goldfish `cecc76fbe51b33276e0e2e787b6eacba41c52ef4eaa36c5a20954caeedc50b66` | SHA256SUMS = manifest |
| Branch tip (P not final) | `316163384641dfba546e22e967cf1be8f0a80d5e`, engine/ tree `639d2f804ad9277137cec8f4de8790194f3b0b22` | git |
| Earlier engine commits | 140c0be2 (tree 8d71f693, P2+switch+P3), b8a8621a (P1), b0dc4844 (Bounded Field x2, tree 976fab20) | git |
| Merge-base main/branch | 7c1b62f8 (the branch changes nothing outside `engine/` and `rl/results/` since it) | git |
| Coin watch script | `rl/results/coin_prevention_repair_2026-09-30/instrument_scan.py`, blob at the tip `306f1f6969af39c54bd09a164c8fab27a083c194` (sha256 7cc1914e01e28ce6...; b7e3bc00's, with P2's counters). da08620's was 1b2678bd (sha256 e42e32d8...); main's is df6e9d5e | git |
| VS watch script | `rl/results/victory_star_repair_2026-09-30/instrument_scan.py`, blob `cd8fe70b291b9d5258a384bca444379a71601bb5` (unchanged on the branch) | git |
| Cloud 8b rows | `early_warning_8b/` at 19a20e1a (`19a20e1aec7a998a6e7b88aa28652809b3e647d8`), README fixed at 63c28e6e; `pairs_8b.tsv` blob 0f6f4e37; `8b_new_km3.jsonl` sha256 d2f6a03f..., `8b_new_k3.jsonl` 9501a401..., `8b_pinned_km3.jsonl` b56ba7ee..., `8b_pinned_k3.jsonl` c0e1e3e5... ; played on 140c0be2, not P | git |
| Cloud 8b decks | brew-07 sha256 30422795..., brew-09 ec0a9376..., t-altaria c3a57b9c... (`decks_sha256.txt`); equal to main's today | git |
| Reused old side (8) | `OLDREL/5a18d31_8_new_km3.jsonl` sha256 `22ac692917ecbd0cc0f29b05165cb68a49ea58854d0cd4b05d8a59485f508f71` (16,000), `5a18d31_8_new_k3.jsonl` `64dc6dcc38711279ab5332850d388a0d7840f85e8de1875c99a43bc8b7cc68b3` (8,000) | old step_8.sha256 |
| Reused old side (8b 32-35) | `OLDREL/5a18d31_8b_new_km3.jsonl` `bf5405377a887ac9afb379b1a45573647720c07928ea989b1d56698c07577eff` (160), `5a18d31_8b_new_k3.jsonl` `2d4ad0b4fa2d500b3c220c64cdacbfe967259250268da9fbe1721036442b65ec` (160) | old step_8b.sha256 |
| Their program | the 5a18d31 plain legality_scan = `978912748c83...` = `rl/engine-2026-10-02/legality_scan` (old programs.sha256) | old README L65, L146 |
| Old 8 deck blobs | `OLDREL/seeds_8.txt` "Deck files" (17 files: 8 panel lists, l-sharpedo 34c28791, 4 carriers, 4 scratch); all equal to the working copy today | git |
| 7c floor pages | `floor_dustin_2026-09-30/{02,06,08,14,10}-*` blobs at 4690810 = main; D root at 99cdec0c (`draft-D-entei-grimhound{_games.jsonl 6d0774c4, _coverage.json 1894ae22, .md f72628ea}`); D amended at 19c77835 (`draft-D_amended/...` 7052f09b, cac95950, d1ff6899) | git |
| D lists | first: 9cc6667 blob `b15acdd100cfd216d180ad12bd2da659a0226807`, sha256 `4821877fa5d202a3470f9b76d424f750d1883fee1516ecbce2a33937c8d49585`; today: blob `1d32ead74f0f3fe0f08c038a345d97fa10678065`, sha256 `31035755a6d09148a709dd9d869625b7e588f13d0150cac99a9c58ef5469be6f` | git |
| floor.py | made the Sept 30 pages and D root: blob ec133dab (sha256 `8e5395e63a14636827260bcb6e8631f02734aec690d9cf334fce606ed20dce0a`); main today and D amended: blob 2f9f5b06 (sha256 `763278659ea9a1ac7983c9cd2da2ff5f1f2c1e96468818cb84b29c106bb4b1e0`); `git diff ec133dab 2f9f5b06` sha256 `e8d161353d9baf660c47910a196d3e93e71da3b76092aaa0425dcb3da8032235` (ATTACKERS, draft A only) | git |
| 8b new-row decks | deck 12 blob dbc90f33, deck 10 cee34f84, brew-01 6df57fc0, brew-04 fab9c888, brew-07 ce150697, brew-09 65162e7f, c-magnezone a976b0db (`rl/results/kt_carrier_census_2026-09-26/decks/c-magnezone_ex_magnezone.txt`), houndoom_victini e7853011 (`OLDREL/carriers/alternates/`), water_round2 08cf5ecb (branch only: `rl/results/coin_prevention_round2_2026-10-01/smoke/water_round2.txt`), meowth_carefree 26815670 (`OLDREL/scratch_8b/`, the same bytes as the round-2 smoke's copy) | git |
| Step 7 references | the 15 of old REF7 (sitting1.sh:L218-234), sha256 unchanged on main (4 spot-checked) | git |
| Step 9 references | old SPEC9 (sitting2.sh:L183-190) unchanged; B2e pairings 32-39 = h-whimsicott v panel, 80-87 = deck 12 v panel (`b2e_pairings.tsv`) | git |

---

## 3. Unknown values, and how the copies take them (never a guess)

| Unknown | Taken from | Who fills it | Runner behaviour until then |
|---|---|---|---|
| P (the final engine commit) and its engine tree | `switch2.env` `P`, `P_TREE` (`TO_FINALIZE`; tip as of now in a comment) | laptop session, when the cloud says P landed (after (a)) | sitting 1 refuses; dry run uses the branch tip and says so |
| Allowed engine files at P | `allowed_engine_files.tsv` (26 rows as of 31616338, marker line) | same | refuses |
| Engine commits 8626a35..P | `engine_commits.tsv` (24 as of 31616338, marker) | same | refuses |
| The coin script's blob at P | `switch2.env` `COIN_SCRIPT_BLOB` (306f1f69 as of now, `TO_FINALIZE`) | same | refuses |
| (e)'s switches (names, gates) | `counters.tsv` column `revert_switch` and `switch2.env` `DECKGYM_SWITCHES` (13 names as of 31616338), marker | same | hand-off text only; the env refusal uses the `^DECKGYM_` pattern, so a new name is covered anyway |
| The cloud's 8c tools (classifier, probe, revert script, tracer, validate) | `tools_8c.tsv` (paths at the candidate; marker) | laptop session after (a) and (b) land | sitting 2 refuses; each path must exist at the candidate |
| The suite at P (precondition g) | `switch2.env` `SUITE_AT_P=<commit>:<path>` | the cloud or Sonnet | sitting 1 refuses unless the file exists at that commit and holds `0 failed` and names P |
| The cloud's card check of `c-magnezone_ex_magnezone.txt` (8b rows 45-46, PLAN L262 "after the cloud's card checks") | `switch2.env` `MAGNEZONE_CARD_CHECK=<commit>:<path>` | the cloud | sitting 2 refuses before 8-seeds |
| The candidate C, short S, program hashes | `candidate.txt`, `programs.sha256`, `watch.sha256` (written by sitting 1) | sitting 1 | as Oct 1 |
| trace_load.txt's line | `O/trace_load.txt`, committed by the laptop session (proposed: `TRACE LOAD 0` + the cloud's 8b commit, with `CLOUD8B` lines) | laptop session | step 8 waits, as Oct 1 |
| Pin: programs folder `rl/engine-<pin date>/`, step 15's re-check folder | `switch2.env` `ENGINE_DIR`, `FR_REL` (`TO_FINALIZE`) | laptop session at the pin | pin refuses; must not equal `rl/engine-2026-10-02` |
| 8c result, counts, Dustin's words | `O/8c_RESULT.txt`, `O/8c_DECISION.md`, `PIN_DUSTIN` | Sonnet/cloud, coordinator, Dustin | pin refuses |
| Pin documents | `O/pin/docs/` with DOCS.sha256, BASE.sha256 (as Oct 1) | laptop session | pin refuses |
| Where Sonnet's note 8 and the km3 B2e reference (question 3a) are recorded | pin `NOTED_DOCS` (section 10) | laptop session | a NOTE line, not a stop |
| The seed row's date | `seed_row_23_3B.md` says "Oct 10"; fix it to the commit's day | laptop session | n/a |

---

## 4. `sitting1.sh` (implementer A; 31 changes)

S1-1. **Header** (old L1-168). Rewrite for switch 2: PLAN L256-261 and L271-273; Dustin's Oct 9 answers (PLAN L24-29: "1-3
sure", go "update if everything passes"; the laptop over the weekend). Drop R/F1-F7/cae37a3 text; keep the anchored-line,
checkpoint, push and resumption text; replace the usage with section 1.9; knobs with section 1.3. Games: 151,240 + 28,000 + 20,160
= **199,400** (PLAN L224 "about 199,000").

S1-2. **REL** (old L173): `REL=rl/results/engine_switch_rules2_2026-10`; add `OLDREL=rl/results/engine_switch_rules_2026-10`.

S1-3. **Data files** (new, right after L182): read `switch2.env`, `allowed_engine_files.tsv`, `engine_commits.tsv`,
`counters.tsv`, `floor_7c.tsv` with the section 1.2 rules; refuse on a marker (except `--dry-run`).

S1-4. **Fixed names** (old L184-199). Delete RC, RBR, RTREE, CAE, C9, F_ENGINE, F_TESTS, ALLOWED, PAGES. New: `P`, `P_TREE`,
`P_BRANCH=origin/claude/coin-prevention-round2`, `OFFICIAL=8626a35861b88ae86a70c2386d47f9d765cfa2bc`,
`MAIN_ENGINE=38af8b0cc4f35fdccc647ed540a56ec8f5e6c1d5` (PLAN L93: main's engine is still the pinned tree), `ALLOWED` (path
+ status) from the tsv, `ENGINE_COMMITS` (+ kind) from the tsv, `CREF=refs/pocketdecksim/rules-switch2-candidate`.

S1-5. **Watch scripts** (old L200-201): same two paths; expected blobs `VS_SCRIPT_BLOB=cd8fe70b...` and
`COIN_SCRIPT_BLOB` (P's) from switch2.env. PLAN L258.

S1-6. **Old programs** (old L202-206, L617-628). `OLDP="$R/rl/engine-2026-10-02"` with the three hashes of section 2;
`old_programs()` checks the manifest's `available_release` is `main-8626a35` with `rl/engine-2026-10-02/{deckgym,legality_scan,
goldfish}` (old L626 named main-d363ba8 and rl/engine-2026-09-30).

S1-7. **7c names** (old L190, L209-215). Replace `PAGES`, `FLOOR_DIR`, `FLOOR_DECKS` by the 7 pages of `floor_7c.tsv`
(Appendix A.5): 02, 06, 08, 14, 10 (4690810), D_root (99cdec0c), D_amended (19c77835). Keep `SEED7C=23100000000`,
`P7C=40-71`, `OFFGATE7C=40,42,47,48,50,55,56,58,63` (Oct 1's 32 rows, "as before", PLAN L261) with the pairs file
`$OLDREL/pairs_7c.tsv` used **in place**, blob `d747cf5f38f740cad6425c74f5b921e65fef5589` checked (no regeneration). Add
`SEED7C2=23300000000`, `P7C2=0-23`, `D7C2=8-23` (D's pairings), `TWEEZ7C2=7` (deck 10 v t-weezing).

S1-8. **REF7 / SPEC7 / SPEC7B** (old L218-257): unchanged (PLAN L259 "the same files as the last plan's step 7"; L260 the same
28 cells). REFS (old L235-236) adds the 7 pages' 21 files (36 references in all).

S1-9. **SPEC7C** (old L258): `("7c_watch_km3|km3|P7C|60|P7C" "7c_old_km3|km3|P7C|60|P7C" "7c2_watch_km3|km3|P7C2|60|P7C2"
"7c2_old_km3|km3|P7C2|60|P7C2")`. `scan_args` (old L646-655) adds `P7C) --pairs "$R/$OLDREL/pairs_7c.tsv"` and
`P7C2) --pairs "$O/pairs_7c2.tsv" --root "$R" --seed-base 23300000000`; `pl_of`/`cells_of` (L656-657) add P7C2 = 24 cells.

S1-10. **Knobs** (old L261-284): section 1.3 and 1.4 (DEADLINE `school`, HARD_STOP `auto` = DL, PUSH_BY, ALLOW_DAYTIME, BUSY_OK).

S1-11. **push_lim** (old L365-372): `PB` replaces `DL + 1800` (section 1.4).

S1-12. **ckpt_msg** (old L373-378): section 1.6 text; "PLAN.md steps 4-7c".

S1-13. **p_checks** (replaces `r_checks`, old L441-464). PLAN L44, L133, L256: P by commit, not branch head.
- `P` readable; on `P_BRANCH` (on a resume, "no longer on it" is a note, as old L446-447);
- `git rev-parse P:engine` = `P_TREE`;
- `git merge-base --is-ancestor $OFFICIAL $P` (P stacks on the official engine; d1b986c4 merged it);
- `git log --format=%H $OFFICIAL..$P -- engine/` as a set = `engine_commits.tsv`'s ids;
- each `tests` commit's `git diff-tree -r --name-only` under `engine/` is only `engine/tests/*` and each such path is in ALLOWED;
  each `src` commit touches `engine/src/`; each `merge` commit has two parents; no non-merge commit touches anything outside
  `engine/` and `rl/results/` (true for all 23 today);
- `git diff --no-renames --name-status $OFFICIAL $P -- engine/` = ALLOWED (path and status) exactly;
- `git diff --quiet $OFFICIAL $P -- engine/src/players/`, and no `Cargo.lock` or `Cargo.toml` anywhere in that diff (PLAN L133,
  L256: "players/, Cargo.lock and Cargo.toml must be unchanged"; old L497 checked Cargo.lock only).

S1-14. **cand_msg** (old L465-479): "Merge claude/coin-prevention-round2 at <P7> (P) into main: the rules switch 2 candidate
(Dustin, Oct 9: "1-3 sure", go "update if everything passes")", the scope of PLAN L43-60 and RELEASE_PACKAGE "What it is", the
changed paths list, "engine/ is P's tree <P_TREE7> byte for byte".

S1-15. **candidate_checks** (old L480-507):
- main's engine/ = 38af8b0 (was 9c84fef, L482-483);
- the candidate's engine/ = `P_TREE` (L485);
- outside `rl/results/`, `git diff --no-renames --name-status main cand` = ALLOWED with **each listed status** (L490 required `M`
  only; `engine/tests/rules_repair_return_damage_weakness.rs` is `A`);
- players/, Cargo.lock, Cargo.toml unchanged; nothing deleted (as L496-500, plus Cargo.toml);
- the candidate's VS script blob = `VS_SCRIPT_BLOB` and coin script blob = `COIN_SCRIPT_BLOB` = P's (L501-503 compared with R);
- the reserved-name check of section 1.10;
- the note (L506) as before.

S1-16. **Preconditions at start** (new, after the helper check, old L932-936): `SUITE_AT_P` exists at its commit, names P's 7 or
40 hex, and holds a `0 failed` line (PLAN L246, precondition g); otherwise "start refused". The START line names it.

S1-17. **Env hygiene and busy check** (new, before the START line): sections 1.8 and 1.9.

S1-18. **Daytime refusal** (old L938-943, dry run L913): only when `ALLOW_DAYTIME=0`.

S1-19. **Seed registration** (old L944-945, dry run L904-906): section 1.7's START_HERE check (`23,300,000,000` and `36–37`).

S1-20. **Step 5 build folders** (old L1073): `B=/home/dacz8976/engine-rules2-$S; W=/home/dacz8976/engine-rules2-watch-$S`.
Cargo as before (L1093-1096: `unset CARGO_TARGET_DIR`, `--locked`, archive folder on the WSL disk). PLAN L257 "as-is".

S1-21. **Inputs** (old L541-549 `inputs_rel`): add `decks/dustin/10-xatu-oricorio-tr-weezing.txt`,
`decks/brews/drafts_2026-10-01/draft-D-entei-grimhound.txt`, `lib/brew_pages.py`, `lib/brew_consistency.py` (kept),
`decks/screen/floor.py` (kept). D's first-list copy is **not** in the candidate: it is recorded at 7c-seeds in its own record
`<S>_inputs7c.sha256` (S1-27), checked before and after step 7c.

S1-22. **floor.py rule** (old L574-575: "floor.py must be the blob the floor pages were made with (4690810's)"). Main's floor.py
is now 2f9f5b06 (9e139e65, Oct 2), which halts the old check. New rule: the working copy's floor.py sha256 is one of
`floor_7c.tsv`'s `floor_py_ok` values for every page (8e5395e6... or 76327865...), and when it differs from the page's
`floor_py_made` value, `git diff <made blob> <current blob>` must have the pinned sha256 `e8d16135...` and floor.py's `ATTACKERS`
keys (read with `ast`) must not name the page's deck. Section 14, A9.

S1-23. **floor_pages_check / extract_refs** (old L591-616): per page, each of its 3 files is the blob at its `ref_commit`
(4690810, 99cdec0c or 19c77835) and main's; extract into `B/ref/<ref_dir>/...` blob-checked; REFSUM covers all 36.

S1-24. **Step 6 watch build** (old L1111-1159; PLAN L258): order unchanged (VS script, then the coin script; the smoke showed
either order gives the same lines, cf3cffe); blobs checked against switch2.env (L1123-1128 compared with R). The counter list of
L1138-1143 becomes **all 42 names of counters.tsv** (`grep -q "\"$x\""` each); the text "it writes all 15 counters" (L1144)
becomes 42. `watch_patch.txt` names P.

S1-25. **Step 7** (old L1161-1174): unchanged (151,240 games; PLAN L259).

S1-26. **Step 7b** (old L1176-1191; PLAN L260). Identity watch v plain unchanged (L1185). The counters call (L1187) becomes
`counters_check counters_7b.txt "<label>" --zero-role reach2 --require offgate_plain_attack_damage,offgate_by_attack,offgate_confused_attack
--report-rest` (sitting1_check.py C1-3). Stop: any reach2 above 0, or a required off-gate at 0 everywhere (PLAN L282). The STEP line
lists each required off-gate's games and every other counter's games (round-1 ones included, a NOTE when above 0; section 14 A13).

S1-27. **Step 7c-seeds** (old L1197-1216, now its own STEP id `7c-seeds`, as Oct 1's line L1213-1215). Before any 7c game:
- check `$OLDREL/pairs_7c.tsv` blob d747cf5f (Oct 1's 32 rows);
- write `pairs_7c2.tsv` (`sitting1_check.py pairs7c2`) and `seeds_7c2.txt` (block, rows, each deck path with its git blob);
- copy D's first list byte for byte from `9cc666761df5c2598457a41bfa400ce835bd975c:decks/brews/drafts_2026-10-01/draft-D-entei-grimhound.txt`
  to `O/floor_7c/d_first/draft-D-entei-grimhound.txt` (git cat-file; blob b15acdd1 and sha256 4821877f checked; the basename
  must stay, floor.py names the page by it);
- write `<S>_inputs7c.sha256` (the D copy, deck 10, today's D list, the panel, floor.py);
- `floor_7c/NOTE.txt` (old L1206-1212 text, plus: the Sept 30 pages were made with rl/engine-2026-09-30's goldfish, so the replay's
  "- Coverage from" line names rl/engine-2026-10-02/goldfish by design);
- checkpoint, then `STEP 7c-seeds DONE`.

S1-28. **Step 7c floors** (old `run_floor` L726-770, loop L1218). Per page of floor_7c.tsv, output folder
`O/floor_7c/<page_id>/` (two D pages share a basename, so one folder each); deck argument as the tsv says (D_root: the copy).
The comparison is `sitting1_check.py floor <newdir> <refdir> <name> --label L` plus the page's mode options (C1-4):
`--allow-coverage-program` always; `--report-opponent t-weezing` for page 10; `--allow-caveat "B3 025"` for both D pages.
**The replay-on-the-old-engine rule** (PLAN L261 last bullet): when a page's comparison does not pass (exit 1), the runner first
plays the same call with the old deckgym (`floor_with.py $OLDP/deckgym <its sha256> floor.py <deck> --out floor_7c/<page_id>/oldengine`),
writes that comparison (old engine v the recorded page) to `identity_7c.txt` ("the difference predates switch 2" or "it comes
with switch 2"), then halts as before. Deck 10's t-weezing differences are not a failure (reported; "a new page in step 15").

S1-29. **Step 7c scans** (old L1219-1224). Oct 1's 32 rows: watch and old (`$OLD_SCAN`, cwd `B/engine`), `ident` watch v old on
1,920 deals (as L1222-1223). New 24 rows: watch and old on `pairs_7c2.tsv`; `ident` with `--exclude-pairings 7` on 1,380 deals; the
deck 10 v t-weezing pairing (7) goes through `sitting2_check.py touched` with `--old 7c2_old --new 7c2_watch --watch 7c2_watch
--pairings 7 --step 7c` (watch is the new side here: 7b showed watch = plain) into `handoff_7c_km3.tsv` (section 14, A11).
Counters (`counters_7c.txt`): Oct 1's rows: round-1 `r1_exact`, `r1_heads` and `r1_superset` all 0 and `offgate_helper_choice`
above 0 in OFFGATE7C ("as before", old L1224); reach2 reported (NOTE when above 0). New rows: `offgate_vs_ungated_built` above 0
in at least one game of pairings 8-23 (PLAN L261: "must be above 0 on D"); `offgate_confused_attack` reported on 0-7.
Sitting 1 now also uses `sitting2_check.py` and `counters.tsv`: both join the private copies (old L974), the CODE line
(old L999) and the committed-helper check (old L932-936).

S1-30. **Counts and estimates** (old L798-807 games_left, L1196, L1227, L1232): 7c = 7 pages x 1,920 + 2 x 1,920 + 2 x 1,440 =
20,160; the 7c STEP line carries `changed <N> of 60 deals` for pairing 7 and the deck 10 page's t-weezing line.

S1-31. **Dry run** (old L856-919): same checks on the merge tree of main and the tip of `P_BRANCH` when `P` is `TO_FINALIZE`
(said so), plus: the data files and their markers; reserved names; the ALLOWED, ENGINE_COMMITS and counter checks; both scripts
applied to a scratch `legality_scan.rs` (L882-887) with all 42 counter names present; pairs7c2 written in /tmp; floor_7c.tsv's
blobs and the floor.py rule; env and busy checks; the deadline, hard stop and push-by times; `git push --dry-run`.

## 5. `sitting1_check.py` (implementer A; 9 changes)

C1-1. **Docstring** (L1-36): switch 2; the counters model of section 1.11; the floor modes; pairs7c2.

C1-2. **Counter definitions** (L39-55: EXACT_DICT, SUPERSET_INT, HEADS_*, OFFGATE, REPAIR, CARRIED). Replace with
`load_counters(path)` reading `counters.tsv` -> `{name: (script, shape, role, mechanic, revert_switch)}` and role sets; keep the
module-level names sitting2_check.py imports, recomputed from the file (`REACH2`, `OFFGATE2`, `SUPERSET2`, `R1_EXACT`, `R1_HEADS`,
`R1_OFFGATE`, `R1_SUPERSET`, `ROUND2_QUEUED`). Drop `CARRIED` (Oct 1's rows 13 and 22). Keep `as_exact` (L77-90), `check_by_mechanic`
(L93-101), `as_int` (L104-108); add `as_keyed(g, name)` (dict of str -> strictly ascending int lists; returns the total tick count),
`as_int_or_null`, and `value(g, name)` dispatching on shape. A counter missing from a game is `Malformed` (exit 2).

C1-3. **`counters`** (L111-197): new options `--counters counters.tsv` (required), `--zero-role ROLE` (repeatable: every counter
of that role 0 in every game; any key of a keyed one), `--zero NAME,...`, `--require NAME,... [--in PAIRINGS]` (each above 0 in
at least one game in scope), `--report-rest`. Output: one line per file (games; the zero roles "read 0 in all n games" or "are NOT
all 0: k games, first (p, i) (names)"), one line per pairing that had any counter fire (each fired counter: games, ticks), one
line per required counter, then `<label>: PASS|does not pass: ...` (the same exit codes 0/1/2). Remove `--require-discard`.

C1-4. **`floor`** (L200-243). Keep the per-game comparison (key (opponent, seat, seed), union of fields). Add:
- `--allow-coverage-program`: the page line `- Coverage from <program> (sha256 <64 hex>; ...` is normalized (program and hash),
  and both values are printed (the Sept 30 pages name rl/engine-2026-09-30/goldfish; floor.py now takes the manifest's,
  rl/engine-2026-10-02/goldfish). Without it this line alone would halt all five Sept 30 pages (section 14, A10b).
- `--report-opponent NAME`: games against NAME may differ: counted (changed games, wins before and after) and printed, not a
  failure; every other opponent's games must be equal; when NAME's games differ, the page may differ only in lines that mention
  NAME or the totals (the verdict line, the flagged line, the worst-matchup list, the failure-mode tables) and the line "a new
  page in step 15" is printed; the coverage must still be byte-equal.
- `--allow-caveat "B3 025"`: the coverage file may differ only in that key's `limitations` list; the page only in the table row
  that starts `| <name> (B3 025) |`, and only in its engine cell. The difference is printed in full. (Expected: no difference,
  since the coverage comes from the old goldfish; section 14, A10.)
- `--expect-games N` (default the reference's count).

C1-5. **`pairs7c`** (L246-274): kept for the dry run (it must still write Oct 1's file byte for byte); its docstring says so.

C1-6. **`pairs7c2`** (new): `--repo R --out FILE [--seeds-out FILE]`: rows for pairings 0-23, columns as pairs_7c.tsv,
`block=rules2_7c`, held lists in this order and keys: `10-xatu-oricorio-tr-weezing` (`decks/dustin/10-xatu-oricorio-tr-weezing.txt`),
`draft-D-first` (`rl/results/engine_switch_rules2_2026-10/floor_7c/d_first/draft-D-entei-grimhound.txt`), `draft-D-amended`
(`decks/brews/drafts_2026-10-01/draft-D-entei-grimhound.txt`), each v the 8 sorted panel lists; `seed_first = 23,300,000,000 +
10,000 x p`, `seed_last = seed_first + 59`, `sub_block_end = seed_first + 9,999`. The seeds file lists every deck with its blob.

C1-7. **Exit codes and Malformed** (L277-298): unchanged.

C1-8. **REL/short()** (L58-59): unchanged (it splits on `/rl/results/`).

C1-9. **Imports for sitting2_check.py**: the names in C1-2 must exist at import time (sitting2_check.py imports them, old L62-63);
`load_counters` reads the path in env `SWITCH2_COUNTERS` or the `counters.tsv` next to the script (the runners pass the private
copy's folder).

## 6. `switch_check.py` (implementer A; 2 changes and a note)

SC-1. **`same`** (L64-105, parser L193-194): add `--pairings P` and `--exclude-pairings P` (comma list and ranges). They filter
both NEW and every REF before counting; `--expect` counts the filtered deals. Used by step 9 (B2e without 32-39, 80-87 = 40,000)
and 7c2 (without pairing 7 = 1,380).
SC-2. **Docstring** (L2-25): name the switch-2 callers; document the two options.
SC-3. Nothing else: CORE (L28-29), `complete`, `rules`, `cli`, `screen`, `pairs-decks` unchanged.

## 7. `sitting2.sh` (implementer B; 32 changes)

S2-1. **Header** (old L1-137): switch 2 (PLAN L262-267, L272-273); the reuse of Oct 1's old side (PLAN L233); the named rows (PLAN
L280); the categories of section 1.12; usage section 1.9; knobs section 1.3. Games: 8b 2,800, 8 54,750, 9 74,500, 10 5,040 =
**137,090** (PLAN L225 "about 137,000"; 8b is 480 above PLAN L262's 2,320 because of the cloud's rows 36-37, section 14 A5).

S2-2. **REL** (old L142) and OLDREL; data files read as S1-3 (`switch2.env`, `counters.tsv`, `tools_8c.tsv`, `reuse.tsv`).

S2-3. **Candidate** (old L153-155): `CAND` is read from `candidate.txt` (no constant), checked: two parents, the second = P, the
first = the `main` line, `C:engine` = `P_TREE`; `S1_STEPS=(4 5 6 7 7b 7c-seeds 7c)`; but `7c-seeds` has no manifest (as Oct 1):
check its STEP line only.

S2-4. **Old programs** (old L156-160, L463-474): as S1-6.

S2-5. **Carriers and scratch** (old L161-177 E/EBR/CARRIERS/SCRATCH/SHARPEDO, L589-612 e_checks/scratch_checks). Nothing is
copied for step 8: the carriers, scratch decks, panel and l-sharpedo are read in place from `$OLDREL` and `decks/`, and each must
be the blob `$OLDREL/seeds_8.txt` lists (17 files, all equal today). `reuse_checks()` (new) also checks: `$OLDREL/pairs_8.tsv` blob
3ef02030; every file of `reuse.tsv` (Appendix A.6) has its sha256, line count and `bot_a`, and its `.run` record names
`legality_scan sha256 978912748c83...` (the old program) with `--pairs .../engine_switch_rules_2026-10/pairs_8.tsv
--seed-base 23100000000 --bot <bot> --pairings <its pairings> --games <n>`.

S2-6. **8b's new decks** (new; PLAN L262). `copy_blob` (old L613-625) kept, used at 8-seeds for: the cloud's pairs file
(`<P>:$REL/early_warning_8b/pairs_8b.tsv`, blob 0f6f4e37) -> `O/pairs_8b_cloud.tsv`; `water_round2.txt` (`<P>:rl/results/
coin_prevention_round2_2026-10-01/smoke/water_round2.txt`, blob 08cf5ecb) -> `O/scratch_8b2/water_round2.txt`. The cloud's
`decks_sha256.txt` values must equal the working copy's files for every deck `pairs_8b_cloud.tsv` names.

S2-7. **Seeds** (old L178 `SEED8`, `P8`, `P8B`): `SEED_OLD=23100000000`: `P8=0-31` (`$OLDREL/pairs_8.tsv`),
`P8B_CLOUD=32-37` (`O/pairs_8b_cloud.tsv`; base checked = 23.1B, section 1.7); `SEED_NEW=23300000000`: `P8B_NEW=40-46`
(`O/pairs_8b2.tsv`), `PWILL=60-62` (`O/pairs_will.tsv`).

S2-8. **SPEC9** (old L183-192): unchanged references and seeds; add `NAMED9=32,33,34,35,36,37,38,39,80,81,82,83,84,85,86,87`
(PLAN L266, L280).

S2-9. **Step 10 names** (old L194-207): unchanged (PLAN L267 "as-is").

S2-10. **HELPERS** (old L208): add `floor_with.py`? No (sitting 2 does not use it). Add the data files (`switch2.env`,
`counters.tsv`, `tools_8c.tsv`, `reuse.tsv`) to the committed-as-it-is check.

S2-11. **Knobs** (old L211-234): section 1.3, 1.4 (HARD_STOP auto = DL, was DL + 600 at L232).

S2-12. **SCANS8B / SCANS8** (old L302-303): 8b: `8b_cloud_{new,watch}_<bot>` (32-37), `8b_cloud_old_<bot>` (36-37 only),
`8b_new2_{old,new,watch}_<bot>` (40-46); 8: `8_{new,watch}_<bot>` (0-31), `8_will_{old,new,watch}_<bot>` (60-62).

S2-13. **rebuild_combined** (old L304-318): identity 7 + 7c + 9 + 10; touched 7c + 8b + 8 + 9; the hand-off from
`handoff_{7c_km3,8b_km3,8b_k3,8_km3,8_k3,9_km3}.tsv` and those steps' scan files.

S2-14. **ckpt_msg** (old L347-352): section 1.6.

S2-15. **s1_checks** (old L423-439): S2-3; "not DONE yet" is a refusal (exit 2), a changed manifest is a HALT (section 1.5).

S2-16. **set_paths** (old L440-445): build folders of section 1.1.

S2-17. **Inputs by group** (old L484-501 group_rel): group 8 = the decks of `$OLDREL/pairs_8.tsv` rows 0-31,
`pairs_8b_cloud.tsv`, `pairs_8b2.tsv`, `pairs_will.tsv`, plus the reused files of reuse.tsv; group 9, group 10 unchanged.

S2-18. **expected_blob** (old L538-549): `$OLDREL/carriers/*` and `$OLDREL/scratch_8b/*`: the blob in `$OLDREL/seeds_8.txt`;
`$REL/scratch_8b2/water_round2.txt`: P's blob; `$REL/floor_7c/d_first/*`: 9cc6667's; everything else: the candidate's.

S2-19. **Step 8-seeds** (old L1215-1246). Before any game: fetch (2 min); `MAGNEZONE_CARD_CHECK` present at its commit (else
"start refused" at the start, not here); reuse_checks; copy the two files of S2-6; write `pairs_8b2.tsv`, `pairs_will.tsv`
(`sitting2_check.py pairs --set 8b2|will`) and `seeds_8_2.txt` (both blocks, every row's seed ranges per bot, every deck with its
blob, and the reused files with their sha256); `extract_refs2`, `write_inputs2` (old L564-588, unchanged but for the groups);
checkpoint; `STEP 8-seeds DONE`; then main's copies are the blobs (old L1242-1245).

S2-20. **run_scan** (old L643-690): unchanged, but the RULE-finding exception for the old engine (L684-689) names
`rl/engine-2026-10-02` (main-8626a35).

S2-21. **carrier_set** (old L717-727) becomes `scan_set step family bot pairs seedbase pairings deals oldmode`:
`oldmode=play` runs old, new, watch (as before); `oldmode=reuse:<file>[,<file>]` runs new and watch and passes the reused file(s)
as `--old` (for 8b_cloud: the reused 32-35 file **and** the played 36-37 file). Then `ident` watch v new (as L724-725) and
`touched_check` (as L704-716, with the new options of C2-4).

S2-22. **step_summary** (old L729-737): calls the new `stepsum` (C2-5) with every watch file and row file of the step.

S2-23. **Counts and estimates** (old L765-786): 8b = new + watch 2 x 240 per bot (32-37) + old 80 per bot (36-37) + 3 x 280 per bot
(40-46) = 2,800; 8 = 2 x (16,000 + 8,000) + 3 x (1,500 + 750) = 54,750; 9 = 66,500 + 8,000; 10 = 5,040.

S2-24. **run_step8** (old L811-819): carriers (`P8`, reused old) km3 500 then k3 250; Will rows (`PWILL`, old played) km3 500 then
k3 250; `stepsum 8`. STEP line: PLAN L264's counts, `changed <N> of <M> deals`, the categories, CONDITION 3.

S2-25. **8b** (old L1248-1258): the cloud rows (32-37) then the new rows (40-46), km3 then k3, 40 deals; `stepsum 8b`.

S2-26. **cloud8b_same / gate_8c** (old L821-877). `trace_load.txt` is `O/trace_load.txt` (PLAN L243). CLOUD8B lines compare
pairings 32-37, 240 deals per bot (was 32-35, 160). New optional line `CLOUD8B_OLD <commit> <bot> <path>` compares this run's
played old rows (36-37) with the cloud's `8b_pinned_<bot>.jsonl` filtered to 36-37 (80 deals): a difference halts as CLOUD 8B does.
The gate (TRACE LOAD n <= 50 or a DUSTIN line) is unchanged (PLAN L263 "as-is").

S2-27. **Step 9** (old L1270-1282; PLAN L266). Plain: the 6 SPEC9 scans as before (66,500). Identity: B2e with
`--exclude-pairings 32-39,80-87` (40,000), the other 5 whole (as before). The named 16: a watch scan `9_watch_b2e_km3`
(`--pairings` NAMED9, `--games 500`, the B2e pairs file, seed 21,106,000,000; 8,000 games); `ident` watch v the plain scan with
`--pairings` NAMED9 (8,000); `touched_check` with `--old` the B2e reference (from B/ref2) and `--pairings` NAMED9 -> `handoff_9_km3.tsv`,
`touched_9.txt`; `stepsum 9`. A changed game in the 80 others halts (PLAN L279); in the 16 it goes to 8c (PLAN L266).

S2-28. **Step 10** (old L1284-1311): unchanged.

S2-29. **Start checks** (old L1124-1136, 1149-1157): `s1_lock_held` on this folder's lock; helpers and data files committed;
daytime only with `ALLOW_DAYTIME=0`; START_HERE (section 1.7); env and busy (sections 1.8, 1.9); `tools_8c.tsv` final and each
of its paths present at the candidate; `MAGNEZONE_CARD_CHECK` set and present.

S2-30. **The end** (old L1313-1328): unchanged logic; the PIN_STATUS text names the switch-2 counts; PAUSED exits 3.

S2-31. **Dry run** (old L988-1114): the same structure, with the new reuse, copy, pairs, refs and gate checks; it makes
`pairs_8b2.tsv` and `pairs_will.tsv` in /tmp and blob-checks their decks; it shows `pairs_8b_cloud.tsv`'s rows 32-37 with the seed
base it reads; the tools of tools_8c.tsv at the candidate (replaces L1038-1042's vs_trace/vs_probe/coin_probe/coin_lookahead check).

S2-32. **Private copies** (old L1163-1165): add `counters.tsv` to the private folder (sitting2_check.py reads it next to itself).

## 8. `sitting2_check.py` (implementer B; 12 changes)

C2-1. **Docstring** (L1-58): switch 2 throughout.

C2-2. **Imports** (L61-63): the new names of C1-2 (`REACH2`, `OFFGATE2`, ..., `value`, `as_keyed`, `load_counters`).

C2-3. **Constants** (L65-107). `REL` switch 2; `OLDREL`; `BASE_OLD=23_100_000_000`, `BASE_NEW=23_300_000_000`; row sets:
`ROWS_8B2` (pairing 40-46 as section 1.7, with held_key/held_file/opponent/panel_file below), `ROWS_WILL` (60-62);
`DEALS={"8b": {"km3": 40, "k3": 40}, "8": {"km3": 500, "k3": 250}, "9": {"km3": 500}, "7c": {"km3": 60}}`;
`PAIRINGS_8B_CLOUD=(32..37)`; the reach of section 1.11 (coin_queued_by_attack restricted to ROUND2_QUEUED);
`MECHANICS` (12, for the verdicts): sites (coin_queued_by_attack R2 keys), plain-hit coin (coin_plain_damage_by_attack,
coin_plain_damage_chosen), own-side coin (coin_own_side_split), own-side Guts (guts_own_side_split), Perish Body
(perish_plain_hit_offered, _chosen), Will Confused (will_confused_attack), Will block coin (will_block_coin_attack), Victory Star
block coin (vs_block_coin_built, vs_block_coin_choice_offered), Trap Territory (trap_territory_offer_changed, _outcome_changed),
Luxury Coin (luxury_coin_opp_stadium), Fossil lock (fossil_item_lock), return Weakness (attack_return_weakness). Remove
`ROWS13_22`, `GROUPS`, `VERDICTS` A/B(a)/B(b), `FULL_PREV`, the old `COND3` wording; `COND3 = "CONDITION 3 (the Oct 1 ruling,
carried by Dustin's yes to question 1, PLAN L294, L333: a changed game where only round 2's off-gate counters fired)"`.
New HEADER (L103-106): `step, bot, pairing, i, seed, held_file, held_blob, panel_file, panel_blob, old_moves, new_moves,
moves_differ, differing_fields, old_winner, new_winner, old_points, new_points, category, reach2_counters, offgate2_counters,
round1_counters, superset_counters, revert_switches` (compact JSON with every tick; `revert_switches` = the switch names of the
fired reach2 counters' mechanics, from counters.tsv).
Row definitions for `ROWS_8B2`: 40 `12-ariados-whimsicott-ogerpon` v t-weezing; 41 the same v t-lucario; 42
`10-xatu-oricorio-tr-weezing` v t-weezing; 43 `brew-04-xatu-slowking` v t-weezing; 44 `water_round2`
(`rl/results/engine_switch_rules2_2026-10/scratch_8b2/water_round2.txt`) v `meowth_carefree`
(`rl/results/engine_switch_rules_2026-10/scratch_8b/meowth_carefree.txt`); 45 `houndoom_victini`
(`rl/results/engine_switch_rules_2026-10/carriers/alternates/houndoom_victini.txt`) v `magnezone`
(`rl/results/kt_carrier_census_2026-09-26/decks/c-magnezone_ex_magnezone.txt`); 46 `10-xatu-oricorio-tr-weezing` v `magnezone`.
`ROWS_WILL`: 60 `10-xatu-oricorio-tr-weezing`, 61 `brew-01-arceus-crobat-xatu`, 62 `brew-04-xatu-slowking`, each v
`decks/screen/opponents/t-weezing.txt`. Opponent names as Oct 1 (`t-` removed for the panel).

C2-4. **`touched`** (L223-348). `--old F [F ...]` (union by (pairing, i); a deal in two files is a duplicate, issue); `--pairings P`
(filter all three sides; for step 9's reference and 7c2); `--step 7c|8b|8|9`; `--counters counters.tsv`. The all-zero halt
(L262, L267-268, L337-340) is removed (section 1.12; section 14 A7). Category per changed game; per pairing: games, identical,
changed, by category; per counter role: games, ticks, changed games where it fired; the off-gate presence of every offgate2
counter in identical games; `changed games with no reach2 counter: N of M`; the CONDITION 3 count. Issues (exit 1): counts,
duplicates, different deals, malformed counters, watch differing from new. Exit 2 on unreadable input.

C2-5. **`stepsum`** (L366-422): one verdict per MECHANICS entry ("reached in N games (M ticks)" or "UNREACHED (rests on its
tests)"), the uncounted parts of section 1.11 as one report line, every offgate2 counter's presence in identical games (a report:
PLAN L260 requires off-gates only on the table), the categories, the CONDITION 3 count, `SUMMARY: ...` with
`changed <N> of <M> deals (<K> with no reach2 counter)` (the pin and gate_8c read this phrase; old L866 greps it).

C2-6. **`pairs`** (replaces `pairs8`, L155-190): `--set 8b2|will --repo R --out F [--seeds-out F]`; the old 8 rows are not
regenerated (Oct 1's file is used in place). Missing deck file: exit 2.

C2-7. **ENGINES / TRACER / CLASSIFIER / RULE texts** (L425-458): old = main-8626a35 (`rl/engine-2026-10-02/`, legality_scan
97891274...; for reused rows "Oct 1's recorded new-engine games, the same program"); new = the candidate (main + P, engine/ =
P_TREE); the tools from `tools_8c.tsv` with their paths at the candidate; the rule = PLAN L288-291 (three changes: the reach list
of section 1.11; a prefix game judged like any board difference; lookahead needs the code gate, v2 finding the condition and the
revert check), the categories, "a judgment call doesn't stop the replays; the pin waits for Dustin's word" (PLAN L286); the revert
switches table (gate -> `DECKGYM_*` name) from counters.tsv.

C2-8. **`handoff`** (L461-525): HEADER of C2-3; totals per step and bot by category; per reach2 counter; the files with sha256
(L514-517); seeds: both blocks.

C2-9. **`trace_gate`** (L528-558): unchanged.

C2-10. **`cloud8b`** (L561-611): `PAIRINGS_8B` -> 32-37; `--expect` default 240; `--pairings P` to compare a subset (36-37 for
CLOUD8B_OLD, 80 deals); the "owed" text names pairings 32-37. `CLOUD_CORE`, `PATH_FIELDS` unchanged.

C2-11. **`main`** (L614-640): the new subcommands and options.

C2-12. **blob_id / read_set / read_rows** (L120-123, L193-206, L351-363): unchanged.

## 9. `checkpoint.sh`, `quiet.sh`, `.gitignore`, `floor_with.py`
Byte copies (blobs daf3f538, 16315a40, ff44c03a, 7e4880fe). Each works from its own folder (`quiet.sh` sets `O` from its path;
`checkpoint.sh` takes REL as an argument; `.gitignore` covers `.sitting1.*`, `.sitting2.*`, `*.part`, `*.broken_*`). Their
comments name Oct 1's scripts; that is history, not a fault.

## 10. `pin/pin_rules.sh` (implementer C; 21 changes)

P-1. **Header** (L1-45): PLAN L268 (steps 11-14), Dustin's Oct 9 go ("1-3 sure", "update if everything passes"; PLAN L24-29)
and "the pin still waits for his word on any judgment call" (PLAN L29, L286).

P-2. **Paths** (L52-57): `REL` switch 2; `PREL` = `switch2.env` `ENGINE_DIR` (refuse if `TO_FINALIZE`, if it equals
`rl/engine-2026-10-02`, or if it exists and is not a recorded copy, as L311-315); `FRREL` = `FR_REL`.

P-3. **Fixed names** (L59-68): `C` and `MAIN_C` from `candidate.txt` (`candidate`, `main`); `RC` = `P`; `RTREE` = `P_TREE`;
`MAIN_ENGINE=38af8b0cc4f35fdccc647ed540a56ec8f5e6c1d5`; `CREF` = rules-switch2-candidate; `ALLOWED` + statuses from
`allowed_engine_files.tsv`.

P-4. **WANT** (L70-72): read from this folder's `programs.sha256` (the plain build's three lines) and cross-checked with the
`sha256 <hex> <name> (new, plain)` lines in PIN_STATUS.txt (as L289), not constants.

P-5. **STEPS** (L73): `(4 5 6 7 7b 7c 8-seeds 8b 8 9 10)` (with manifests); also require the `STEP 7c-seeds DONE` line.

P-6. **COND3** (L74): no constant; the CONDITION 3 count of `handoff_8c.tsv` (`category == offgate_only`).

P-7. **Documents** (L75-76; PLAN L268). `REQUIRED_DOCS=(START_HERE.md CLAUDE.md rl/RUN5.md "$REL/README.md")`;
`NOTED_DOCS=(rules/09_engine_repairs_2026-09-22.md rules/04_actions_cards_effects.md rules/02_damage_knockouts_points.md
rl/results/rules_recordings_2026-10-01/READOUT.md "$REL/PLAN.md")` plus, when known, the file holding Sonnet's note 8 and the
km3 B2e reference record (question 3a). START_HERE's draft must name `ENGINE_DIR` and keep the 23.3B seed row; CLAUDE.md's must
name `ENGINE_DIR` (L482-483 checked `rl/engine-2026-10-02`).

P-8. **PIN_SUBJECT** (L78): `'^Pin rules switch 2 (main-'`. The old `'^Pin the rules engine (main-'` matches the Oct 2 pin commit
24374a00 already on main, so gate 1 (L196-197) would answer "the pin is already done" and stop (section 14, A8).

P-9. **Lock** (L191): `/tmp/pocketdecksim_pin_rules2_2026-10.lock`; the sitting locks (L202-203) are this folder's.

P-10. **Gate 2** (L206-238): unchanged logic, with C and the steps of P-5; the `PREPARE` line check as before.

P-11. **Gate 3, the 8c line** (L241-276; pin/README.md L36-52). `handoff_8c.tsv` committed and unchanged; its row count HN must
equal the sum of the `changed <N> of <M> deals` phrases of the STEP 7c, 8b, 8 and 9 lines. The one line of `8c_RESULT.txt`:
```
8C PASS <result commit, 40 hex> verdicts: on_board <b>, lookahead <l>, unexplained <u>, judgment <j>; revert <r> of <l> reproduced; condition3 <c> traced <c>; changed <n> accounted <n>; dustin <a> (8c_DECISION.md); net unaccounted 0; 8b_rows_vs_cloud equal
```
Checks: `b + l + u + j = n = HN`; `r = l` (PLAN L291: the revert check reproduces the old choice and scores for every lookahead
game; a game failing it is a stop, so it cannot be in the line); `c` = the hand-off's CONDITION 3 count; `a = u + j`; when `a > 0`:
`8c_DECISION.md` committed and unchanged, and `PIN_DUSTIN='<his words>'` set (noted in PIN_STATUS.txt as `PIN DUSTIN: ...`),
else stop "a judgment call waits for Dustin's word" (PLAN L29, L286); the result commit is here.

P-12. **Gate 4** (L279-299): programs from `programs.sha256` (P-4); `E` from the build folder `engine-rules2-<S>`.

P-13. **Gate 6** (L307-341): the old programs folder check (L316) is `rl/engine-2026-10-02` (its SHA256SUMS); the km3 default
check and the busy check unchanged; the env check of section 1.8 (no `DECKGYM_*` while the pin runs `current_engine.py`).

P-14. **Gate 7, the merge** (L344-400): `RC=P`; main's engine/ = 38af8b0 (L356); `MAIN_C` from candidate.txt (L357-358); the
merge's engine/ = `P_TREE`; outside rl/results/ exactly ALLOWED **with their statuses** (L364-368 required `M` only); players/,
Cargo.lock **and Cargo.toml** unchanged; nothing deleted or retyped; the reserved-name check (section 1.10).

P-15. **build_docs** (L403-490): L443's `rl/engine-2026-10-02/` -> `$PREL/`; L482-483 as P-7.

P-16. **engine_readme** (L499-528): new text (switch 2): built from one `git archive` of C (main + P, engine/ = P_TREE),
the three parts and P1 (PLAN L43-60, RELEASE_PACKAGE), Bounded Field x2, the revert switches (the `DECKGYM_*` names; default
on; "set one and the program is another engine; never set them in a recorded run"), `players/` unchanged, km3 the working pilot,
the evidence counts (from the 8c line and the STEP lines), the approval words, the history line (`../engine-2026-10-02/` kept).

P-17. **build_final** (L529-549): the new `update_manifest_rules.py` arguments (U-2).

P-18. **Merge and pin messages** (L599-612, L737-755): switch-2 text; the pin subject starts `Pin rules switch 2 (main-<M7>)`.

P-19. **fr_gate** (L550-558): unchanged logic, on `FR_REL`.

P-20. **Drafts folder** (L769): `~/pin_rules2_drafts_<M7>`.

P-21. **`pin/README.md`** (adapted): the switch-2 paths, the 8c line of P-11, `PIN_DUSTIN`, the documents of P-7.

## 11. `pin/update_manifest_rules.py` (implementer C; 9 changes)

U-1. Docstring (L1-11): switch 2.
U-2. Arguments (L18-24): `<merge> <built candidate> <P> <SHA256SUMS> <base manifest> <out> <engine dir> <8c line file> [--check]`
(all shas 40 hex; the engine dir must match `^rl/engine-2026-1[0-2]-[0-3][0-9]$`); counts parsed from the 8c line (P-11 grammar).
U-3. `R_SHA` (L15) -> the `<P>` argument; the MERGED regex (L33) uses P[:7].
U-4. `OLD_NAME = "main-8626a35"` (L16); `NEW_DIR` from the argument (L17).
U-5. superseded (L40-41): `"<date> by main-<M7> (rules switch 2: the round-2 coin package, Cursed Jewel's Weakness, Fossils as
Items; <engine dir>/)"`.
U-6. `built` (L55-59): the date and time from PIN_STATUS's build line, the candidate, P, P_TREE.
U-7. `identity_evidence` (L60-75): step 7 151,240; 7b 28,000 (round-2 exact counters 0, the three off-gates above 0); 7c 20,160
(the deck 10 t-weezing count); 8b 2,800 and 8 54,750 with old/new/watch and the reused old side; 9 74,500 (80 B2e pairings,
Scizor and the second lists equal; the 16 named rows' changed games); 10; the 8c counts; the 26 engine files (17 source, 9 tests);
players/, Cargo.lock, Cargo.toml unchanged.
U-8. `approved` (L76-80): Dustin, Oct 9: "1-3 sure" (go, "update if everything passes"), "Alright it is fine to use the laptop
over the weekend"; plus `PIN_DUSTIN` when given.
U-9. `purpose` (L81-91): the switch-2 scope and the `DECKGYM_*` switches; km3 unchanged; the 0.7.2 add-on note kept.

---

## 12. What PLAN's step table asks, and where it lands

| PLAN step (line) | Runner | Spec items |
|---|---|---|
| 4 (L256) | sitting1.sh | S1-4, S1-13 to S1-15 |
| 5 (L257) | sitting1.sh | S1-20 to S1-23 |
| 6 (L258) | sitting1.sh | S1-5, S1-24 |
| 7 (L259) | sitting1.sh | S1-25 |
| 7b (L260) | sitting1.sh, sitting1_check.py | S1-26, C1-3 |
| 7c (L261) | sitting1.sh, sitting1_check.py, switch_check.py, sitting2_check.py touched | S1-7, S1-27 to S1-30, C1-4, C1-6, SC-1 |
| 8b (L262) | sitting2.sh, sitting2_check.py | S2-5 to S2-7, S2-19, S2-21, S2-25, S2-26, C2-3, C2-6, C2-10 |
| gate (L263) | sitting2.sh | S2-26, C2-9 |
| 8 (L264) | sitting2.sh | S2-21, S2-24 |
| 8c (L265) | hand-off only | C2-4, C2-7, C2-8 |
| 9 (L266) | sitting2.sh, switch_check.py | S2-8, S2-27, SC-1 |
| 10 (L267) | sitting2.sh | S2-28 (unchanged) |
| 11-14 (L268) | pin_rules.sh, update_manifest_rules.py | P-1 to P-21, U-1 to U-9 |
| stop rule (L278-284) | all | section 1.12, S1-26, S2-27 |
| mechanic check (L288-291) | 8c; the hand-off text | C2-7 |

## 13. Carried over unchanged (no edit beyond the names above)

- The framework of both sittings: `main()` wrapper, `set -euo pipefail`, the re-exec under setsid, the lock (fd 9), notes and
  anchored lines, `halt`/`die`/`on_exit`/`stopped_or_failed`, `durable`, `leftovers`, `record_commit`, `not_pushed`, `push_why`,
  `checkpoint`, `done_files`, `ckpt_list`, `skip_done`/`finish_step`/`step_done`/`manifest_files`, `rate`, `need_s`,
  `begin_step`, `run_record`/`kept`/`set_aside`/`timing_row`, `run_scan`, `ident`, the watchdog, the shared-index handling
  (unstage at start; refuse staged changes), `unpushed_check`, `git_locks`, the AFTER_HALT handling, the private copies in /tmp
  and the CODE line. Sitting 2's `origin_ahead` before every commit (its Oct 1 fix) is kept.
- Step 7, 7b's identity, step 10, `trace_gate`, `cli_compare`, `out_run`, `play_*`, `gold_compare`, `screen_compare`,
  `extract_refs2`/`write_inputs2`/`check_inputs`/`check_refs`/`step_io`.
- `switch_check.py` but SC-1/SC-2; `checkpoint.sh`, `quiet.sh`, `.gitignore`, `floor_with.py` as byte copies.
- In the pin: the undo machinery, `merge_clash`, the sweep, `docs_base_ok`, the private-index commit, the size gate, the
  calibrate km3 check, the busy check, `current_engine.py` in a scratch folder.

## 14. Ambiguities and contradictions (PLAN or the brief against the facts or the old runners)

A1. **The coin watch script's version.** PLAN L258: "the coin script from P's branch (da08620's version, unchanged at 57c6586)";
the brief repeats "da08620's version". The fact: b7e3bc00 (Oct 8, "the return-damage counters") changed it; at the tip its blob is
306f1f69, not da08620's 1b2678bd. da08620's has no `attack_return_weakness` or `offgate_return_by_source`, which section 0 (c),
PLAN L70, requires. The spec takes P's blob (S1-5, S1-24). Only the coin script is a new blob; the VS script is unchanged (cd8fe70b).

A2. **Step 4's file list.** PLAN L256: "exactly the 17 engine files above; if question 2a lands first, it also takes
`apply_trainer_action.rs`, `shared_mutations.rs`, `effect_mechanic_map.rs` and `effect_ability_mechanic_map.rs`"; PLAN L69:
"Step 4's allowed file list then takes P2's files". The fact (`git diff --name-status 8626a35 31616338 -- engine/`): 26 files, 17
source and 9 tests. P3 (140c0be2) changed `apply_abilities_action.rs`, `apply_attack_action.rs`, `apply_trainer_action.rs`,
`shared_mutations.rs`, `models/card.rs`, `move_generation_trainer.rs`; **neither `effect_mechanic_map.rs` nor
`effect_ability_mechanic_map.rs` changed**. P2 added `apply_action_helpers.rs`, `hooks/counterattack.rs`, `hooks/mod.rs`,
`actions/mod.rs` and a new test file with status `A` (`rules_repair_return_damage_weakness.rs`), which the old check (status M
only, old sitting1.sh:L490, pin_rules.sh:L367) would refuse. The list is a data file, finalized at P.

A3. **The reach list.** PLAN L289: "The reach counters are da08620's exact list"; section 0, PLAN L70: "(c) gains an exact counter
for 'an attack's return damage took Weakness'". Section 0 wins: 16 names (section 1.11).

A4. **8b's seed block.** PLAN L252: "New seeds (8b's new rows and step 8's Will rows) come from a block outside every range ... for
example 23,300,000,000"; the brief: "the laptop's rows must equal the cloud's early_warning_8b/ rows". The cloud played its new rows
36-37 on 23,100,000,000 (its README: "Not yet in START_HERE's seed table ... The plan said otherwise"). Equality needs the same
seeds, so 36-37 stay on 23.1B and are registered by the drafted row; the other new rows use 23.3B. If the cloud replays 36-37 on
23.3B, the runner follows its pairs file (section 1.7).

A5. **8b's rows.** PLAN L262 lists 4 + 5 + 2 rows (2,320 games) and no brew-07/09 rows; the cloud's early warning (decision 14,
relayed Oct 9) added brew-07 and brew-09 v t-altaria as 36-37, and RELEASE_PACKAGE names "brew 07 and 09 against t-altaria" as
expected to change. The spec plays them (+480 games: 2,800).

A6. **7c's new rows have no seed block in PLAN.** PLAN L252 names new seeds for 8b and step 8 only; L261's "watch rows for deck 10
and D's two lists v the panel, 60 deals" (2,880 games) are new deals too. The spec puts them on 23.3B pairings 0-23 and the drafted
row registers them.

A7. **The old "all counters 0 means identical" halt.** Old sitting2_check.py L19-23: "A game whose watch row has every REPAIR
counter at 0 ... must equal the old game, new and watch alike: one that differs is the halt". PLAN L280-281 and L288-291: a
changed game in a named row is judged by the mechanic check, and "in lookahead" is explained with both halves and the revert check.
Evidence: in the cloud's own 8b rows, k3 pairing 37 i 35 changed with **no counter at all** (checked from its committed rows) and the
cloud classified it lookahead with both halves (RETURN). Kept, the old halt would stop sitting 2 at 8b. The spec drops it for named
rows and sends such games to 8c as category `none`. If the coordinator prefers to keep a runner halt for some rows, it can be a
per-step option (`--zero-counter halt`), but no named row qualifies today.

A8. **The pin's "already done" test.** Old pin_rules.sh L78 `PIN_SUBJECT='^Pin the rules engine (main-'` and L196-197 `git log
--grep`: the Oct 2 pin commit "Pin the rules engine (main-8626a35) ..." (24374a00) is on main, so the copy would stop at gate 1
saying the pin is done. Changed in P-8.

A9. **floor.py is no longer the pages' blob.** Old sitting1.sh L574-575 requires 4690810's floor.py (ec133dab) for "floor.py's
own call". Main's is 2f9f5b06 since 9e139e65 (Oct 2): the change adds an `ATTACKERS` table naming draft A only; the floor
addendum found the Payback pages byte-equal under it (`run_addendum.sh`, 19c77835). D amended was made with 2f9f5b06, the other six
pages with ec133dab. Running the old blob would mean writing floor.py outside this folder (its ROOT is its own path), which the
runners may not do. The spec allows both with a pinned-diff check (S1-22). This is an operational call for the coordinator.

A10. **"Only the caveat line may differ" (PLAN L192, L261) will not be seen in 7c.** floor_with.py replaces only the deckgym;
the coverage (and the page's Victini row, read from it) comes from the manifest's goldfish, main-8626a35's, which prints the old
caveat. So D's replays should be equal; the tolerance stays as allowed, not expected. The new caveat shows on step 15's pages.
A10b. A related difference PLAN does not mention: the five Sept 30 pages (02, 06, 08, 14, 10) name
`rl/engine-2026-09-30/goldfish (sha256 8f6056a0...)` in their "- Coverage from" line; the replay names
`rl/engine-2026-10-02/goldfish (sha256 cecc76fb...)`. The old checker normalizes only the "- Engine:" line, so it would halt on all
five. C1-4 adds `--allow-coverage-program`; the coverage file itself must still be byte-equal (none of those decks holds Victini,
the only caveat switch 1 changed).

A11. **Deck 10 v t-weezing in 7c's watch rows.** PLAN L280 names "deck 10's t-weezing floor row" as allowed to change; L261's new
watch row deck 10 v t-weezing (pairing 7 of 23.3B) plays the same matchup on new seeds and can change for the same reason (Will).
PLAN does not name it. The spec treats it like the floor row: named, its changed games go to 8c (`handoff_7c_km3.tsv`). If the
coordinator reads PLAN literally, it becomes an equal row and a change there halts.

A12. **The deadline.** PLAN L314-316 (section 8) describes the runners' default deadline 11:30 UTC (6:30 am) with a hard stop 10
minutes later; PLAN L28 (Oct 9, wins): "no new game after 5:15 am Central; a step still going pauses cleanly". The spec's default:
DEADLINE = the next weekday 10:15 UTC, HARD_STOP = DEADLINE, PUSH_BY = 12:00 UTC (section 1.4). "Pauses cleanly" for a running
step is the watchdog's STOPPED record (committed and pushed; a plain start resumes); a step that would not end in time is PAUSED.

A13. **7b's round-1 counters.** Oct 1's 7b required every repair counter 0 (old L1187). PLAN L260 now requires only round 2's exact
counters at 0 and reports "the others". The spec follows PLAN, with a NOTE when a round-1 counter is above 0 on the table.

A14. **The 23.3B block's place.** START_HERE's 20B row says "new blocks go above the last one used" (the last used is
24,601,000,000+); PLAN L252 picks 23,300,000,000 "outside every range". Both hold: 23.3B is free. PLAN's choice is kept.

A15. **The pin's documents.** PLAN L268 doesn't name `rules/02_damage_knockouts_points.md` §2 (P2's rule, PLAN L46) or the
`DECKGYM_*` switches; RELEASE_PACKAGE's scope includes P2. The spec lists rules/02 among the noted documents and the switches in the
engine README and the manifest.

A16. **The cloud's 8b rows were played on 140c0be2, not P.** P adds b8a8621a (text), b0dc4844 (Bounded Field x2) and 31616338 (the
switches, default on). The laptop's rows (on P) must still equal them (CLOUD8B); the cloud's revert-gates run checks "default (no
variable): byte for byte the recorded new rows". A difference halts and goes to the coordinator.

A17. **The (e) switches are engine code every game reads.** 31616338 changes 10 source files after the suite at b0dc4844
(5ec11518): precondition (g) needs the suite at P, and precondition (f)'s readers need 31616338 too (PLAN L245 predates it).
The runners check (g) through `SUITE_AT_P` (S1-16); (f) is not the runners' to check.

A18. **The trace-load gate's commit.** PLAN L243 wants `TRACE LOAD <n> <commit>`; the cloud's README proposes `TRACE LOAD 0`
"with this folder's commit (CLOUD_STATUS gives it)" without naming it. 19a20e1a (the rows) or 63c28e6e (the README's fixes) both
hold the files; the laptop session picks one when it writes `trace_load.txt`.

A19. **The brief's "17 files of section 0/3 plus P3's four files and their tests".** Section 0/3 never lists 17 files by name;
PLAN L133 says "9 source files and 8 test files" at 20e2651. The 17 at 20e2651 are in Appendix A.2's comment; P1, P2, P3, Bounded
Field and (e) bring the total to 26.

---

## Appendix A. The data files (exact contents to write in `O`)

### A.1 `switch2.env`
```
# Rules switch 2: the fixed names the runners read (KEY=VALUE; no spaces, no quotes; read with a regex, never sourced).
# TO_FINALIZE values are not set: a runner that needs one refuses to start (the dry run notes it).
# As of Oct 9 22:14 UTC the branch tip is 316163384641dfba546e22e967cf1be8f0a80d5e (engine tree 639d2f804ad9277137cec8f4de8790194f3b0b22);
# the cloud is still adding (a). P is the final engine commit, taken by commit, not by branch head (PLAN L44, L133).
P=TO_FINALIZE
P_TREE=TO_FINALIZE
P_BRANCH=origin/claude/coin-prevention-round2
OFFICIAL=8626a35861b88ae86a70c2386d47f9d765cfa2bc
OFFICIAL_TREE=38af8b0cc4f35fdccc647ed540a56ec8f5e6c1d5
OLD_RELEASE_NAME=main-8626a35
OLD_DIR=rl/engine-2026-10-02
OLD_DECKGYM_SHA256=2f7e5fd6e0ae21fffcb9a4df6e70dc3302e2a372f1fde1eb2bb1aa106747a62e
OLD_LEGALITY_SCAN_SHA256=978912748c83fd6c8ee8e3e966c9a6b95c9fdf1eb9d500c7367b2c1463e71699
OLD_GOLDFISH_SHA256=cecc76fbe51b33276e0e2e787b6eacba41c52ef4eaa36c5a20954caeedc50b66
CREF=refs/pocketdecksim/rules-switch2-candidate
VS_SCRIPT=rl/results/victory_star_repair_2026-09-30/instrument_scan.py
VS_SCRIPT_BLOB=cd8fe70b291b9d5258a384bca444379a71601bb5
COIN_SCRIPT=rl/results/coin_prevention_repair_2026-09-30/instrument_scan.py
# as of 31616338: 306f1f6969af39c54bd09a164c8fab27a083c194 (b7e3bc00's, with P2's counters)
COIN_SCRIPT_BLOB=TO_FINALIZE
SEED_OLD_BLOCK=23100000000
SEED_NEW_BLOCK=23300000000
CLOUD8B_DIR=rl/results/engine_switch_rules2_2026-10/early_warning_8b
CLOUD8B_PAIRS_BLOB=0f6f4e3794857c2e15c86fc39eeec228c8232c70
OLD_PAIRS_8_BLOB=3ef020309d1bfe3a5df05f4d6516216ff6210a8b
OLD_PAIRS_7C_BLOB=d747cf5f38f740cad6425c74f5b921e65fef5589
WATER_ROUND2_BLOB=08cf5ecb9653a1f3b00e9bc8c04d45cd29c82ba7
D_FIRST_COMMIT=9cc666761df5c2598457a41bfa400ce835bd975c
D_FIRST_BLOB=b15acdd100cfd216d180ad12bd2da659a0226807
D_FIRST_SHA256=4821877fa5d202a3470f9b76d424f750d1883fee1516ecbce2a33937c8d49585
# precondition (g): <commit>:<path> of the suite log at P ("0 failed", naming P)
SUITE_AT_P=TO_FINALIZE
# PLAN L262 "after the cloud's card checks": <commit>:<path> of the check of c-magnezone_ex_magnezone.txt
MAGNEZONE_CARD_CHECK=TO_FINALIZE
# the pin (set at the pin): the programs folder and step 15's re-check folder
ENGINE_DIR=TO_FINALIZE
FR_REL=TO_FINALIZE
```

### A.2 `allowed_engine_files.tsv`
```
# TO FINALIZE WHEN P LANDS. As of 31616338: git diff --no-renames --name-status 8626a35 <P> -- engine/ (26 rows: 17 source, 9 tests).
# The 17 at 20e2651 (PLAN L133) were apply_action.rs, apply_attack_action.rs, attack_outcome.rs, trainer_coin_plan.rs, card_validation.rs,
# hooks/core.rs, hooks/retreat.rs, move_generation_trainer.rs, state/mod.rs and 8 tests; P2, its off-switch, P3, P1, Bounded Field x2 and (e) add the rest.
status	path
M	engine/src/actions/apply_abilities_action.rs
M	engine/src/actions/apply_action.rs
M	engine/src/actions/apply_action_helpers.rs
M	engine/src/actions/apply_attack_action.rs
M	engine/src/actions/apply_trainer_action.rs
M	engine/src/actions/attack_outcome.rs
M	engine/src/actions/mod.rs
M	engine/src/actions/shared_mutations.rs
M	engine/src/actions/trainer_coin_plan.rs
M	engine/src/card_validation.rs
M	engine/src/hooks/core.rs
M	engine/src/hooks/counterattack.rs
M	engine/src/hooks/mod.rs
M	engine/src/hooks/retreat.rs
M	engine/src/models/card.rs
M	engine/src/move_generation/move_generation_trainer.rs
M	engine/src/state/mod.rs
M	engine/tests/b4a_attack_batch2_test.rs
M	engine/tests/gholdengo_luxury_coin_test.rs
M	engine/tests/pokemon/galarian_cursola_perish_body_test.rs
M	engine/tests/pokemon/legacy_ability_logic_test.rs
M	engine/tests/pokemon/meowth_carefree_steps_test.rs
M	engine/tests/pokemon/ursaluna_guts_test.rs
A	engine/tests/rules_repair_return_damage_weakness.rs
M	engine/tests/rules_repair_trainers.rs
M	engine/tests/victini_victory_star_test.rs
```

### A.3 `engine_commits.tsv`
```
# TO FINALIZE WHEN P LANDS. As of 31616338: git log --format=%H 8626a35..<P> -- engine/ (24). kind: tests = touches only engine/tests/ under engine/;
# merge = two parents; src = touches engine/src/. The runner checks each kind.
commit	kind	subject
99f5bc4a8b9b40f19e4e5a363de7ce2de87aaa9c	tests	Coin-flip prevention, the later round: failing tests first
e0ecf19f2ac990c7503f1a60927362f6906d853d	src	Coin-flip prevention, the later round: six sites flip the coin
9145eb38406c50617a01afe14faa5a923bd5dfdc	tests	Mega Kangaskhan ex's second punch: failing tests first
29e126a820067cead03ee6348fd4a2eaaeb4aac3	src	Mega Kangaskhan ex's second punch flips the coin (gated)
ce151c79f04dbe9209f7795e0e0e7970277739a2	merge	Merge R (f8cfa9c) into the later round's branch
59c7c2aed410a1daabc9557d1145462fd3c1fed6	tests	Card-text job, item 1: Will with a Confused attacker, tests first
27a0c37df0f9619900633967565129357f267fc7	src	Card-text job, item 1: Will goes to a Confused attacker's own first coin
7e131325e32f1c4556c22fda9c339cf89699f6dd	tests	Card-text job, item 3: tests first
46953bf3538e02d78b41ef2decb40d0880ea0bad	src	Card-text job, item 3: the four text-decided fixes
05eb84921de765ea4c8424b38563da3bed93b06b	tests	Card-text job, item 4: Trap Territory tests first
5155ff7a5c9f9587d437519e540c7a3009ef9300	src	Card-text job, item 4: Trap Territory counts once for each Ariados
53a3cca1915efd41613778ebfcee0f878ce71af7	tests	Card-text follow-up: tests first
3090abbb98e5954266dfca0effe03e69f320f60b	src	Card-text follow-up: the five approved changes
d3739b7d9351c59285a97b4b58cac311888627fb	tests	P2: tests first
5543a4bab99c32750f866f3fa4faf83b05337b12	src	P2: return damage left by an attack takes Weakness
14abfb040533b12c037a7034a69cb03d33e06196	tests	P2's off-switch: tests first
35e6acfdc19a8f6fa451af059412474d85a8c3d7	src	P2's off-switch: a parameter, on by default
c17e415d031efa3cfcfee8d19ad22a6460478a45	tests	P3: tests first
140c0be26ec02b34b4c6271e1c47888d0d28053e	src	P3: a Fossil is an Item card at the seven other places
b8a8621a8ea52facaa817e04903912618ed284de	src	P1: Gholdengo's caveat (text only)
6b111ba76aee976c70015a94aa46b4a853036fe5	tests	Bounded Field x2: tests first
b0dc48443fe6d009d8adb44f7b40d2ff9d565b32	src	Bounded Field doubles the hit back's Weakness (x2)
ade211508ea7907dd35a18a7ebffb2422ccb7279	tests	Switch 2 (e): tests first for the revert switches
316163384641dfba546e22e967cf1be8f0a80d5e	src	Switch 2 (e): one revert switch per gate (G1-G11)
```

### A.4 `counters.tsv`
`revert_switch` is read from `apply_action_helpers.rs`:690-745 at 31616338 (the comments name G6 Trap Territory, G9 Luxury Coin,
G10 the Fossil lock; the others follow its order); it is hand-off text only. TO FINALIZE WHEN P LANDS (marker line first).
```
# TO FINALIZE WHEN P LANDS. 42 counters: the watch build's (VS script cd8fe70b, coin script at P). Checked against both scripts' names at the candidate.
name	script	shape	role	mechanic	revert_switch
coin_queued_by_attack	coin	keyed	reach2	sites	DECKGYM_PLAIN_QUEUED_SITES
coin_plain_damage_by_attack	coin	keyed	reach2	plain_hit	DECKGYM_NO_PLAIN_HIT_COIN
coin_plain_damage_chosen	coin	exact	reach2	plain_hit	DECKGYM_NO_PLAIN_HIT_COIN
perish_plain_hit_offered	coin	exact	reach2	perish	DECKGYM_NO_PERISH_ON_QUEUED_HIT
perish_plain_hit_chosen	coin	exact	reach2	perish	DECKGYM_NO_PERISH_ON_QUEUED_HIT
coin_own_side_split	coin	exact	reach2	own_side_coin	DECKGYM_NO_OWN_SIDE_COIN
guts_own_side_split	coin	exact	reach2	own_side_guts	DECKGYM_NO_OWN_SIDE_GUTS
will_confused_attack	coin	exact	reach2	will	DECKGYM_WILL_SKIPS_GATE_COINS
will_block_coin_attack	coin	exact	reach2	will	DECKGYM_WILL_SKIPS_GATE_COINS
vs_block_coin_built	coin	exact	reach2	vs_block	DECKGYM_NO_VICTORY_STAR_AFTER_BLOCK_COIN
vs_block_coin_choice_offered	coin	exact	reach2	vs_block	DECKGYM_NO_VICTORY_STAR_AFTER_BLOCK_COIN
trap_territory_offer_changed	coin	exact	reach2	trap	DECKGYM_TRAP_TERRITORY_ONCE
trap_territory_outcome_changed	coin	exact	reach2	trap	DECKGYM_TRAP_TERRITORY_ONCE
luxury_coin_opp_stadium	coin	exact	reach2	luxury	DECKGYM_LUXURY_COIN_ANY_STADIUM
fossil_item_lock	coin	exact	reach2	fossil_lock	DECKGYM_FOSSIL_UNDER_ITEM_LOCK
attack_return_weakness	coin	exact	reach2	return	DECKGYM_FLAT_RETURN_DAMAGE
offgate_by_attack	coin	keyed	offgate2	sites	-
offgate_plain_attack_damage	coin	exact	offgate2	plain_hit	-
offgate_guts_opponent_split	coin	exact	offgate2	own_side_guts	-
offgate_confused_attack	coin	exact	offgate2	will	-
offgate_block_coin_attack	coin	exact	offgate2	vs_block	-
offgate_vs_ungated_built	coin	exact	offgate2	vs_block	-
offgate_trap_territory_one	coin	exact	offgate2	trap	-
offgate_luxury_coin_offered	coin	exact	offgate2	luxury	-
offgate_fossil_offered	coin	exact	offgate2	fossil_lock	-
offgate_return_by_source	coin	keyed	offgate2	return	-
trap_territory_two_in_play	coin	exact	superset2	trap	-
vs_confusion_first_built	vs	exact	r1_exact	-	-
vs_confused_choice_chosen	vs	exact	r1_exact	-	-
vs_confused_choice_offered	vs	exact	r1_exact	-	-
coin_cut_recorded	coin	exact	r1_exact	-	-
coin_full_prevention	coin	exact	r1_exact	-	-
coin_queued_offered	coin	exact	r1_exact	-	-
coin_queued_offered_any	coin	exact	r1_exact	-	-
vs_confused_choice	vs	int	r1_heads	-	-
vs_confused_choice_first	vs	int_or_null	r1_heads	-	-
offgate_helper_choice	coin	exact	r1_offgate	-	-
offgate_discard_then_damage	coin	exact	r1_offgate	-	-
offgate_helper_by_mechanic	coin	keyed	r1_offgate	-	-
vs_confused_attack	vs	int	r1_superset	-	-
coin_defender_attack	coin	int	r1_superset	-	-
coin_queued_attack_damage	coin	int	r1_superset	-	-
```
The file's second line (after the marker line) is the one place `ROUND2_QUEUED` is defined, parsed by `load_counters`:
```
# ROUND2_QUEUED	Wild Swing|Wellspring Dance|Tornado Shot|Double Splash|Triple Bombardment|Mischievous Ring|Litter|Double-Punching Family
```
(the cloud's `tightened_rule.py` at the tip lists the same eight; the dry run checks the two agree by reading that file's
`ROUND2_QUEUED` with `ast` at the candidate).

### A.5 `floor_7c.tsv`
```
# Step 7c's floor replays (PLAN L261). ref files: <ref_dir>/<name>{_games.jsonl,_coverage.json,.md}, each the blob at ref_commit and on main.
# FLOOR_PY_DIFF	ec133dab0b061a06199ff268ada501999c8c2f7d	2f9f5b06ec40b982886afde76e361a7094d1e2fe	e8d161353d9baf660c47910a196d3e93e71da3b76092aaa0425dcb3da8032235
# (blob made with, blob of today, sha256 of `git diff <a> <b>`: floor.py's ATTACKERS table, draft A only; 9e139e65, Oct 2)
page_id	name	ref_dir	ref_commit	deck	deck_blob	floor_py_made	floor_py_ok	mode
02	02-arceus-crobat	rl/results/floor_dustin_2026-09-30	4690810278b40b490d7c57aee2c7b35ae315ddab	decks/dustin/02-arceus-crobat.txt	133d3e83124ceaacc0d547f44647f4930881db88	8e5395e63a14636827260bcb6e8631f02734aec690d9cf334fce606ed20dce0a	8e5395e63a14636827260bcb6e8631f02734aec690d9cf334fce606ed20dce0a,763278659ea9a1ac7983c9cd2da2ff5f1f2c1e96468818cb84b29c106bb4b1e0	equal
06	06-mega-blaziken-tournament-list	rl/results/floor_dustin_2026-09-30	4690810278b40b490d7c57aee2c7b35ae315ddab	decks/dustin/06-mega-blaziken-tournament-list.txt	a7a2e016d74a72a344f8933a9eb461605c3e73e7	8e5395e63a14636827260bcb6e8631f02734aec690d9cf334fce606ed20dce0a	8e5395e63a14636827260bcb6e8631f02734aec690d9cf334fce606ed20dce0a,763278659ea9a1ac7983c9cd2da2ff5f1f2c1e96468818cb84b29c106bb4b1e0	equal
08	08-garchomp-toolbox	rl/results/floor_dustin_2026-09-30	4690810278b40b490d7c57aee2c7b35ae315ddab	decks/dustin/08-garchomp-toolbox.txt	1ad01fd6108a999b314d2987928b2666005373cc	8e5395e63a14636827260bcb6e8631f02734aec690d9cf334fce606ed20dce0a	8e5395e63a14636827260bcb6e8631f02734aec690d9cf334fce606ed20dce0a,763278659ea9a1ac7983c9cd2da2ff5f1f2c1e96468818cb84b29c106bb4b1e0	equal
14	14-comfey-raticate-hypno	rl/results/floor_dustin_2026-09-30	4690810278b40b490d7c57aee2c7b35ae315ddab	decks/dustin/14-comfey-raticate-hypno.txt	7cdedde506221ce370643c1171e83ea3dfc8c542	8e5395e63a14636827260bcb6e8631f02734aec690d9cf334fce606ed20dce0a	8e5395e63a14636827260bcb6e8631f02734aec690d9cf334fce606ed20dce0a,763278659ea9a1ac7983c9cd2da2ff5f1f2c1e96468818cb84b29c106bb4b1e0	equal
10	10-xatu-oricorio-tr-weezing	rl/results/floor_dustin_2026-09-30	4690810278b40b490d7c57aee2c7b35ae315ddab	decks/dustin/10-xatu-oricorio-tr-weezing.txt	cee34f8420703b028f08377e98d9721f623566dd	8e5395e63a14636827260bcb6e8631f02734aec690d9cf334fce606ed20dce0a	8e5395e63a14636827260bcb6e8631f02734aec690d9cf334fce606ed20dce0a,763278659ea9a1ac7983c9cd2da2ff5f1f2c1e96468818cb84b29c106bb4b1e0	report-opponent:t-weezing
D_root	draft-D-entei-grimhound	rl/results/floor_drafts_2026-10-02	99cdec0c0c578255fdaa8d2dea847e4b18de9748	rl/results/engine_switch_rules2_2026-10/floor_7c/d_first/draft-D-entei-grimhound.txt	b15acdd100cfd216d180ad12bd2da659a0226807	8e5395e63a14636827260bcb6e8631f02734aec690d9cf334fce606ed20dce0a	8e5395e63a14636827260bcb6e8631f02734aec690d9cf334fce606ed20dce0a,763278659ea9a1ac7983c9cd2da2ff5f1f2c1e96468818cb84b29c106bb4b1e0	equal,caveat:B3 025
D_amended	draft-D-entei-grimhound	rl/results/floor_drafts_2026-10-02/draft-D_amended	19c778352104c8900d65411c9b38423a4252a042	decks/brews/drafts_2026-10-01/draft-D-entei-grimhound.txt	1d32ead74f0f3fe0f08c038a345d97fa10678065	763278659ea9a1ac7983c9cd2da2ff5f1f2c1e96468818cb84b29c106bb4b1e0	8e5395e63a14636827260bcb6e8631f02734aec690d9cf334fce606ed20dce0a,763278659ea9a1ac7983c9cd2da2ff5f1f2c1e96468818cb84b29c106bb4b1e0	equal,caveat:B3 025
```
Every page also gets `--allow-coverage-program` (C1-4). The page files' blobs are in section 2 (all equal at their ref_commit and on
main today). D_root's ref files and D_amended's share a basename, so each page replays into its own `floor_7c/<page_id>/`.

### A.6 `reuse.tsv`
```
# Oct 1's recorded new-engine games, played by the 5a18d31 plain legality_scan (sha256 978912748c83..., the program in rl/engine-2026-10-02/): the old side of 8 and 8b's 32-35 (PLAN L233).
path	sha256	games	bot	pairings	deals
rl/results/engine_switch_rules_2026-10/5a18d31_8_new_km3.jsonl	22ac692917ecbd0cc0f29b05165cb68a49ea58854d0cd4b05d8a59485f508f71	16000	km3	0-31	500
rl/results/engine_switch_rules_2026-10/5a18d31_8_new_k3.jsonl	64dc6dcc38711279ab5332850d388a0d7840f85e8de1875c99a43bc8b7cc68b3	8000	k3	0-31	250
rl/results/engine_switch_rules_2026-10/5a18d31_8b_new_km3.jsonl	bf5405377a887ac9afb379b1a45573647720c07928ea989b1d56698c07577eff	160	km3	32-35	40
rl/results/engine_switch_rules_2026-10/5a18d31_8b_new_k3.jsonl	2d4ad0b4fa2d500b3c220c64cdacbfe967259250268da9fbe1721036442b65ec	160	k3	32-35	40
```

### A.7 `tools_8c.tsv` (TO FINALIZE: the cloud is still adding (a); paths at the candidate)
```
# TO FINALIZE WHEN P LANDS (after (a) and (b)). The 8c tools the hand-off names; each must exist at the candidate.
role	path
classifier	rl/results/engine_switch_rules2_2026-10/tightened_rule.py
classifier_tests	rl/results/engine_switch_rules2_2026-10/test_tightened_rule.py
classify_8b	rl/results/engine_switch_rules2_2026-10/early_warning_8b/classify_8b.py
probe	rl/results/round2_readiness_2026-10-02/coin_probe_v2.rs
probe_validate	rl/results/round2_readiness_2026-10-02/validate_v2.py
tracer	rl/results/victory_star_repair_2026-09-30/smoke/rerun_R/vs_trace.rs
revert_check	rl/results/coin_prevention_round2_2026-10-01/revert_switches/run_revert_gates.sh
revert_score_dump	rl/results/coin_prevention_round2_2026-10-01/revert_switches/score_dump_round2.rs
```
