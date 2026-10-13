# A worker's brief for a Managed Agents session (non-interactive; the coordinator fills in the ALL-CAPS names and adds his wait and checkpoint rules)

You are worker WORKER. Your registration is REG, which is `rl/results/exam_m32_m64_2026-10/reg_m32` or `.../reg_m64`. Your decks are DECKS,
from `SHARDS.md`. You have no push access, so you hand off files, not commits.
- You play only your decks of your registration.
- You never change a registration, never play another worker's deck, and never set any `DECKGYM_*` variable.
- Nobody answers questions mid-run. When something doesn't fit, stop and write what you saw (step 5).

0. **Run every command below from the root of your clone.** The registrations record `repo_root` as `.`, so the harness and the stamp read
   the decks from your own checkout.
1. **Checkout (read-only).** Clone the public repository and check out main at MAIN_COMMIT. Fetch `claude/playout-pilot`.
2. **Build, once.**
   1. Run `cargo fetch` (with network) in the clone's `engine/` first: an offline cargo finds no crates.
   2. Build in the background, with the default STRENGTH_JOBS (a command limit kills a long foreground build):
      `nohup rl/strength/build.sh 172cbe9ce0f2cb7946b489422b56d3fce5ca6219 $HOME/kxc/172cbe9c/strength > /mnt/session/outputs/WORKER_build.log 2>&1 &`
   3. Wait for it to end. It must print engine tree `69a5a4419da2...` and harness source `bf9c5d6814007f1f`.
   4. Copy the program's `.build.json` record to `/mnt/session/outputs/WORKER_build.json`.
3. **Your slice, in one folder.** Set `OUT=/mnt/session/outputs/WORKER_REGNAME`, where REGNAME is `reg_m32` or `reg_m64`. In the commands
   below, `ONLY` stands for `--only-deck` repeated once per deck of yours, with the full deck names from `SHARDS.md`, for example
   `--only-deck 02-arceus-crobat --only-deck 11-archaludon-haxorus-dragonair`. The harness plays them in the registration's order.
   1. **Stamp before play** (gate 1 and the self-check), once:
      `python3 rl/strength/split_collect.py stamp --manifest REG/manifest.json --program $HOME/kxc/172cbe9c/strength --worker WORKER --out $OUT ONLY`.
      - Run it in the background (nohup) and wait.
      - Its 12 km3 games take seconds. Its 12 kx3 games run one after another, each using several cores for its play-outs.
      - There is no output until the end, which takes up to about 4 hours for m32 and about 7.5 for m64 on a 4-core sandbox.
      - A live process using CPU is not a hang.
      - Keep checking at least every 30 minutes until the step ends. An idle session can lose its sandbox, and the stamp then starts again
        from zero.
      - Every replayed self-check digest must equal the manifest's:
        - km3 `81b572198c04d5d1`;
        - m32 `869789a10142e83f`;
        - m64 `724e581a9c51711f`.
      - A mismatch or any refusal: stop, play nothing (step 5).
   2. **Play**, in the background so polling can't cut it:
      `nohup nice -n 19 $HOME/kxc/172cbe9c/strength run --manifest REG/manifest.json --out $OUT ONLY --threads 2 > $OUT/run.log 2>&1 &`.
      If it stops, run the same command again: it resumes.
   3. **Seal after play.** Only when the folder shows 96 games per deck of yours (48 kx3, 48 km3) and `errors.jsonl` is empty or absent:
      `python3 rl/strength/split_collect.py seal --manifest REG/manifest.json --program $HOME/kxc/172cbe9c/strength --out $OUT`.
      After the seal, never touch `$OUT` again.
   4. **Pack it for the hand-off** (the export flattens folders). With `S=WORKER_REGNAME`, run
      `tar -C /mnt/session/outputs -cf /mnt/session/outputs/$S.tar $S/` and then
      `(cd /mnt/session/outputs && sha256sum $S.tar > $S.tar.sha256)`. The tar only reads the folder, so the seal still holds.
4. **Status.** After each step, and every 2 hours during play, add one line to `/mnt/session/outputs/STATUS_WORKER.txt`:
   `<UTC time> WORKER <registration> <decks>: <stamp ok|STOP: why> <n>/<96 x decks> games, <e> errors, sealed <yes|no>`
5. **Stopping.** On any refusal, hash mismatch, failed program or anything unexpected:
   - write a line starting `STOP:` to the status file, with exactly what you saw;
   - leave every file as it is, and end the session.

   Don't work around it.
6. **Hand-off.** When your folder is sealed and packed, write `DONE` as the last status line and end.
   - The laptop side collects `<S>.tar`, checks its `.tar.sha256`, extracts it and re-checks the seal.
   - It then commits the folder unchanged, byte for byte, under `rl/results/exam_m32_m64_2026-10/workers/`.
   - Empty files are not exported, so never use an empty file as a signal: the status lines are the signals.
   - The seal binds the games to the program, manifest and deck files, so the merge (`split_collect.py merge`) proves nothing changed in
     transit.
   - You read no results and report none to Dustin.
