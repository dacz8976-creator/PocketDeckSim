# The full run: a worker's brief for a Managed Agents session (non-interactive; the coordinator fills in MAIN_COMMIT and WORKER, and adds his wait and checkpoint rules)

Two parts, each with its own harness pin. Never mix them.
- **PART 1, the study:** the 119 positions of `SPEC.md` on the **old** harness (pg_pos.rs 790ae7b1). This keeps them consistent with the
  committed km3 measure.
- **PART 2, the Oct 13 set:** Sonnet's 8 positions on the **new** harness (pg_pos.rs dfcd9682, with Special Conditions and the knock-out
  count). It is a separate registration with its own km3 gate.

The cost pilot measured the timings per position (12 seeds, 4-core sandbox): an early turn takes 13-19 min, a middle one about 7, a late
one under a minute.

| worker | part | bot code (`--bot`) | commit | its `engine` tree | harness pg_pos.rs | positions | est. h |
|---|---|---|---|---|---|---|---:|
| PF1-PF4 | 1 | `kx3` | cd20a97a2e76897fae9883389cee4bf7ce5b3d97 (`laptop/kx3-on-rules2`) | 4ebb30a941737d16b80adddbd1466761e0670e63 | old: from e1ead95e | `shards/S1.txt`-`S4.txt` | 4.2-4.6 |
| PC1-PC4 | 1 | `kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m64` | 9a0bc5ac28ccf421044c3c68dc2779123b607bca (`laptop/kx3cand-on-rules2`) | 5d557d350b6d3d69bbe739b57814ef9769ebdc1d | old: from e1ead95e | `shards/S1.txt`-`S4.txt` | 5.1-5.5 |
| P8 | 2 | first `kx3` on cd20a97a, then the m64 code on 9a0bc5ac | both commits above | both trees above | new: MAIN_COMMIT's | `shards/S8.txt` | about 2.5 |

PFk and PCk play the same list, Sk.

Your names:
- `O=/mnt/session/outputs` and `D=$O/WORKER`.
- **Everything you write goes inside `$D/`**, so the hand-off is one folder.
- `B` is your build's name: F or C (P8 builds both).
- `COMMIT` and `BOT` come from your row.
- You never set any `DECKGYM_*` variable.
- Nobody answers questions mid-run, so when something doesn't fit, stop and write what you saw (step 6).

0. **Run every command from the root of your clone.** Set the variables again in every new shell.
1. **Checkout (read-only).** Clone the public repository, check out main at MAIN_COMMIT, and fetch your branches.
   `git rev-parse COMMIT:engine` must print your row's tree.
2. **Build** (P8: once for F, then once for C).
   ```
   W=$HOME/pg_B; mkdir -p $W $D && git archive COMMIT engine | tar -x -C $W && find $W -type f -exec touch {} +
   # PART 1 (the old harness):
   git show e1ead95e:rl/results/pause_games_decisions_2026-10-02/harness/pg_pos.rs > $W/engine/examples/pg_pos.rs
   # PART 2 (P8, the new harness):
   cp rl/results/pause_games_decisions_2026-10-02/harness/pg_pos.rs $W/engine/examples/pg_pos.rs
   python3 -B rl/results/pause_games_decisions_2026-10-02/harness/pgd_patch.py $W/engine
   (cd $W/engine && cargo fetch --locked)
   nohup bash -c "cd $W/engine && CARGO_TARGET_DIR=$W/target cargo build --release --locked --offline --example pg_pos" > $D/build_B.log 2>&1 &
   ```
   - Wait for the build to end.
   - `sha256sum $W/engine/examples/pg_pos.rs` must start `790ae7b1b91e18f4` (PART 1) or `dfcd968259ce93ea` (PART 2).
   - `pgd_patch.py` must start `01b17932001c57f0`.
   - Write the program's sha256, `nproc` and the CPU model to `$D/build_B.txt`.
   - Set `PG=$W/target/release/examples/pg_pos`.
3. **The km3 gate.** Every line must print EQUAL. One DIFFERENT: stop and play nothing (step 6).
   ```
   S='s=lambda r:{k:v for k,v in r.items() if k not in ("ms","time","elapsed","wall_s")}'
   cmp_km3() { python3 -c "import json,sys; $S; a=[s(json.loads(l)) for l in open(sys.argv[1]) if l.strip()]; b=[s(json.loads(l)) for l in open(sys.argv[2]) if l.strip()]; print(sys.argv[3], 'EQUAL' if a==b else 'DIFFERENT')" "$@"; }
   ```
   - **PART 1:**
     - `P=rl/results/pause_games_new_2026-10-12` and `REF=rl/results/pause_positions_kx3_2026-10/runs_km3`.
     - `DECKARGS=(); for f in $P/decks/KW*.txt; do DECKARGS+=(--deck "$(basename $f .txt)=$f"); done`.
     - The gate positions are KW-261005_034953000-t02, -t04, -t08, -t10, -t16.
   - **PART 2 (P8, for each build):**
     - `P=rl/results/pause_games_new_2026-10-13/v2` and `REF=$P/runs_km3`.
     - `DECKARGS=(); for f in $P/decks/*.txt; do DECKARGS+=(--deck "$(basename $f .txt)=$f"); done`.
     - The gate positions are the 8 of `shards/S8.txt`.
   - For each gate position `id`:
     `$PG --positions $P/positions_all.json "${DECKARGS[@]}" --seeds 1,2,3,4,5,6,7,8,9,10,11,12 --bot km3 --only $id > $D/check_B/out_$id.jsonl 2> $D/check_B/err_$id.txt`
     (run `mkdir -p $D/check_B` first), then `cmp_km3 $D/check_B/out_$id.jsonl $REF/out_$id.jsonl "B $id"`.
4. **The positions.** One at a time, in your list's order, each timed with bash's own `time`. The sandboxes have no `/usr/bin/time`.
   Put this in a script file and start it with `nohup bash <file> &`. It must run under bash, with `PG`, `P`, `DECKARGS`, `BOT` and `D`
   set as above:
   ```
   mkdir -p $D/runs_B
   TIMEFORMAT='elapsed %R s, user %U s, sys %S s'
   while read -r id; do
     [ -n "$id" ] || continue
     [ -f $D/runs_B/out_$id.jsonl ] && [ "$(grep -c . $D/runs_B/out_$id.jsonl)" = 13 ] && continue   # done already: a resume skips it
     echo "$id start $(date -u +%FT%TZ)" >> $D/runs_B/TIMING.txt
     { time $PG --positions $P/positions_all.json "${DECKARGS[@]}" --seeds 1,2,3,4,5,6,7,8,9,10,11,12 --bot BOT --only $id > $D/runs_B/out_$id.jsonl 2> $D/runs_B/err_$id.txt ; } 2>> $D/runs_B/TIMING.txt
     echo "$id end $(date -u +%FT%TZ) exit $?" >> $D/runs_B/TIMING.txt
     tar -C $O -cf $O/WORKER_checkpoint.tar WORKER/      # the checkpoint copy after every position
   done < rl/results/pause_positions_kx3_2026-10/shards/SHARD.txt
   ```
   - SHARD is your list: S1-S4, or S8.
   - Each `out_<id>.jsonl` must hold 13 lines: 12 seeds and the summary.
   - A live process using CPU is not a hang. Keep checking at least every 30 minutes.
   - If the sandbox is lost: restore `$D` from the last checkpoint copy, then build again and redo the gate. The loop skips every position
     already done.
   - P8: run the list with F's build and `kx3`, then build C, redo its gate, and run the list again with the m64 code into `runs_C`.
5. **Status.** After each step, and every hour while positions play, add one line to `$D/STATUS.txt`:
   `<UTC time> WORKER: <build ok|gate 5/5 EQUAL|n of N positions done|STOP: why>`
6. **Stopping.** On a wrong tree or file hash, a failed build, a DIFFERENT gate line, a program error, or anything unexpected:
   - write a line starting `STOP:` to the status file, with exactly what you saw;
   - leave every file as it is, and end the session.

   Don't work around it.
7. **Hand-off.** When all your positions are done:
   ```
   tar -C $O -cf $O/WORKER.tar WORKER/ && (cd $O && sha256sum WORKER.tar > WORKER.tar.sha256)
   ```
   Everything is under the one top folder `WORKER/`, as the collector needs. Then write `DONE` as the last status line and end. You read
   no results and report none to Dustin. The laptop reads the runs and writes the reading.
