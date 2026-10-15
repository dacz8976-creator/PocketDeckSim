# The cost pilot: a worker's brief for a Managed Agents session (non-interactive; the coordinator fills in MAIN_COMMIT and adds his wait and checkpoint rules)

**What it is for.** It measures cost only, before the full run on the 119 positions (`SPEC.md`, "Cost first").
- Two workers, one per bot, each on its own 4-core sandbox and run at the same time: **PF** runs F (the frozen kx3) and **PC** runs C
  (the candidate kx3).
- Each plays the same 3 positions at 12 seeds and times them.
- The positions are early, middle and late turns of one game, 034953. They carry no Special Condition and no rules-switch-2 flag.
- You play only your bot. You never set any `DECKGYM_*` variable. Nobody answers questions mid-run, so when something doesn't fit, stop
  and write what you saw (step 6).

| worker | bot code (`--bot`) | commit to build | its `engine` tree (`git rev-parse <commit>:engine`) |
|---|---|---|---|
| PF | `kx3` | cd20a97a2e76897fae9883389cee4bf7ce5b3d97 (branch `laptop/kx3-on-rules2`) | 4ebb30a941737d16b80adddbd1466761e0670e63 |
| PC | `kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m64` | 9a0bc5ac28ccf421044c3c68dc2779123b607bca (branch `laptop/kx3cand-on-rules2`) | 5d557d350b6d3d69bbe739b57814ef9769ebdc1d |

Below:
- `B` is F or C, and `PB` is your worker name (PF or PC), in file names too.
- `COMMIT` and `BOT` come from your row.
- `O=/mnt/session/outputs`.
- Set `W`, `O`, `P`, `Q` and `DECKARGS` again in every new shell.

0. **Run every command from the root of your clone.**
1. **Checkout (read-only).** Clone the public repository, check out main at MAIN_COMMIT, and fetch your row's branch.
   `git rev-parse COMMIT:engine` must print your row's tree.
2. **Build, once.** The harness and its print-only patch come from main:
   ```
   W=$HOME/pg_B; mkdir -p $W && git archive COMMIT engine | tar -x -C $W && find $W -type f -exec touch {} +
   cp rl/results/pause_games_decisions_2026-10-02/harness/pg_pos.rs $W/engine/examples/pg_pos.rs
   python3 -B rl/results/pause_games_decisions_2026-10-02/harness/pgd_patch.py $W/engine
   (cd $W/engine && cargo fetch --locked)
   nohup bash -c "cd $W/engine && CARGO_TARGET_DIR=$W/target cargo build --release --locked --offline --example pg_pos" > $O/PB_build.log 2>&1 &
   ```
   - The `cargo fetch` needs the network, and an offline cargo finds no crates.
   - The build runs in the background because a command limit kills a long foreground build. Wait for it to end.
   - `sha256sum` of `pg_pos.rs` must start `790ae7b1b91e18f4`, and of `pgd_patch.py` `01b17932001c57f0`.
   - Write the program's sha256 (`$W/target/release/examples/pg_pos`), `nproc` and the CPU model (`lscpu | grep 'Model name'`) to
     `$O/PB_build.txt`.
3. **The check (gate).** km3 on 5 positions must equal the laptop's committed km3 runs, so the build plays as the laptop's does:
   ```
   P=rl/results/pause_games_new_2026-10-12; Q=rl/results/pause_positions_kx3_2026-10
   DECKARGS=(); for f in $P/decks/KW*.txt; do DECKARGS+=(--deck "$(basename $f .txt)=$f"); done
   mkdir -p $O/PB_check
   for t in 02 04 08 10 16; do id=KW-261005_034953000-t$t
     $W/target/release/examples/pg_pos --positions $P/positions_all.json "${DECKARGS[@]}" --seeds 1,2,3,4,5,6,7,8,9,10,11,12 --bot km3 --only $id > $O/PB_check/out_$id.jsonl 2> $O/PB_check/err_$id.txt
     python3 -c "import json,sys; s=lambda r:{k:v for k,v in r.items() if k not in ('ms','time','elapsed','wall_s')}; a=[s(json.loads(l)) for l in open(sys.argv[1]) if l.strip()]; b=[s(json.loads(l)) for l in open(sys.argv[2]) if l.strip()]; print(sys.argv[3], 'EQUAL' if a==b else 'DIFFERENT')" $O/PB_check/out_$id.jsonl $Q/runs_km3/out_$id.jsonl $id
   done
   ```
   All 5 must print EQUAL (km3 takes seconds). One DIFFERENT: stop and play nothing (step 6).
4. **The pilot.** These 3 positions, in this order, one at a time. Each runs in the background so polling can't cut it, and is timed:
   KW-261005_034953000-t02 (early), KW-261005_034953000-t10 (middle), KW-261005_034953000-t16 (late).
   ```
   mkdir -p $O/PB_runs
   TIMEFORMAT='elapsed %R s, user %U s, sys %S s'
   for id in KW-261005_034953000-t02 KW-261005_034953000-t10 KW-261005_034953000-t16; do
     echo "$id start $(date -u +%FT%TZ)" >> $O/PB_runs/TIMING.txt
     { time $W/target/release/examples/pg_pos --positions $P/positions_all.json "${DECKARGS[@]}" --seeds 1,2,3,4,5,6,7,8,9,10,11,12 --bot BOT --only $id > $O/PB_runs/out_$id.jsonl 2> $O/PB_runs/err_$id.txt ; } 2>> $O/PB_runs/TIMING.txt
     echo "$id end $(date -u +%FT%TZ) exit $?" >> $O/PB_runs/TIMING.txt
   done
   ```
   - Put the loop in a script file and start it with `nohup bash <file> &`. It must run under bash: it times with bash's own `time` and
     `TIMEFORMAT`, because the sandboxes have no `/usr/bin/time` (corrected Oct 13, after the first launch stopped there).
   - On the laptop (16 cores), one seed of the early position took 49 s for F (568 CPU-seconds) and 39 s for C (463). So expect very
     roughly an hour or more per position in a 4-core sandbox, and later positions may cost more. A live process using CPU is not a hang.
   - Keep checking at least every 30 minutes. An idle session can lose its sandbox; if it does, start again from step 2, and a finished
     position need not be played again.
   - Each `out_<id>.jsonl` must hold 13 lines: 12 seeds and the summary.
5. **Status.** After each step, and every hour while a position plays, add one line to `$O/STATUS_PB.txt`:
   `<UTC time> PB: <build ok|check 5/5 EQUAL|position n/3 done|STOP: why>`
6. **Stopping.** On a wrong engine tree or file hash, a failed build, a DIFFERENT check, a program error, or anything unexpected:
   - write a line starting `STOP:` to the status file, with exactly what you saw;
   - leave every file as it is, and end the session.

   Don't work around it.
7. **Hand-off.** When the 3 positions are done:
   ```
   tar -C $O -cf $O/PB_pilot.tar PB_build.txt PB_build.log PB_check PB_runs STATUS_PB.txt && (cd $O && sha256sum PB_pilot.tar > PB_pilot.tar.sha256)
   ```
   Then write `DONE` as the last status line and end. You read no results and report none to Dustin. The laptop reads the timings and
   writes the cost table.
