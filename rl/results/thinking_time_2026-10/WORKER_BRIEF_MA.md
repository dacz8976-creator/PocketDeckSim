# A worker's brief for a Managed Agents session (non-interactive; the coordinator fills in the ALL-CAPS names)

The same work as `WORKER_BRIEF.md`, for a Managed Agents sandbox with no push access. You hand off files, not commits. You are worker
WORKER. You play only your slices (`SHARDS.md`), never change a registration, never play another worker's deck, and never set any
`DECKGYM_*` variable. Nobody answers questions mid-run, so when something doesn't fit, stop and write what you saw (step 5).

0. **Run every command below from the root of your clone.** The registrations record `repo_root` as `.`, so the harness and the stamp read
   the decks from your own checkout.
1. **Checkout (read-only).** Clone the public repository and check out main at MAIN_COMMIT. Fetch `claude/playout-pilot`.
2. **Build, once.** `rl/strength/build.sh 172cbe9ce0f2cb7946b489422b56d3fce5ca6219 $HOME/kxc/172cbe9c/strength`. It must print engine tree
   `69a5a4419da2...` and harness source `bf9c5d6814007f1f`. Copy the program's `.build.json` record to `/mnt/session/outputs/WORKER_build.json`.
3. **For each slice, in your order**, with `OUT=/mnt/session/outputs/WORKER_REGNAME_DECK` (a new folder per slice):
   1. **Stamp before play** (gate 1 and the self-check):
      `python3 rl/strength/split_collect.py stamp --manifest REG/manifest.json --program $HOME/kxc/172cbe9c/strength --worker WORKER --out $OUT --only-deck DECK`.
      Every replayed self-check digest must equal the manifest's, and km3's must be `81b572198c04d5d1`. A mismatch or any refusal:
      stop, play nothing (step 5).
   2. **Play**, in the background so polling can't cut it:
      `nohup nice -n 19 $HOME/kxc/172cbe9c/strength run --manifest REG/manifest.json --out $OUT --only-deck DECK --threads 2 > $OUT/run.log 2>&1 &`.
      If it stops, run the same command again: it resumes.
   3. **Seal after play**, only when the slice shows 160 games (80 kx3, 80 km3) and `errors.jsonl` is empty or absent:
      `python3 rl/strength/split_collect.py seal --manifest REG/manifest.json --program $HOME/kxc/172cbe9c/strength --out $OUT`.
      After the seal, never touch `$OUT` again.
4. **Status.** After each step, and every 2 hours while a slice plays, add one line to `/mnt/session/outputs/STATUS_WORKER.txt`:
   `<UTC time> WORKER <registration> <deck>: <stamp ok|STOP: why> <n>/160 games, <e> errors, sealed <yes|no>`
5. **Stopping.** On any refusal, hash mismatch, failed program or anything unexpected, write a line starting `STOP:` to the status file
   with exactly what you saw, leave every file as it is, and end the session. Don't work around it.
6. **Hand-off.** When your slices are sealed, write `DONE` as the last status line and end. The laptop side collects
   `/mnt/session/outputs/` and commits each slice folder unchanged (byte for byte) under `rl/results/thinking_time_2026-10/workers/`.
   The seal binds the games to the program, manifest and deck files, so the merge (`split_collect.py merge`) proves nothing changed in
   transit. You read no results and report none to Dustin.
