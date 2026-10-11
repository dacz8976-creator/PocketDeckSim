# A worker's brief for a sharded strength run (one page; the coordinator fills in the ALL-CAPS names and sends it)

You are worker WORKER. You play only your slices (`SHARDS.md`): each slice is one deck of one registration. You never change a
registration, never play another worker's deck, and never set any `DECKGYM_*` variable.

0. **Run every command below from the root of your clone.** The registrations record `repo_root` as `.`, so the harness and the stamp read
   the decks from your own checkout (`rl/strength/src/main.rs:194`; `split_collect.py`'s deck hashes).
1. **Checkout.** Clone or fetch the repository and check out main at MAIN_COMMIT (it has the registrations under
   `rl/results/thinking_time_2026-10/reg_*/` and the collector `rl/strength/split_collect.py`). Fetch `claude/playout-pilot`.
2. **Build, once.** `rl/strength/build.sh 172cbe9ce0f2cb7946b489422b56d3fce5ca6219 $HOME/kxc/172cbe9c/strength`. It must print engine tree
   `69a5a4419da2...` (claude/playout-pilot's) and harness source `bf9c5d6814007f1f`. Keep the program file and its `.build.json` record
   beside it. Your program's sha256 will differ from the registration's (another machine); the stamp's self-check below is what admits it.
3. **For each slice, in your order:**
   1. **Stamp before play** (gate 1 and the self-check):
      `python3 rl/strength/split_collect.py stamp --manifest REG/manifest.json --program $HOME/kxc/172cbe9c/strength --worker WORKER --out OUT --only-deck DECK`.
      `OUT` is a new folder `rl/results/thinking_time_2026-10/workers/WORKER_REGNAME_DECK/`.
      - The stamp replays the manifest's 12-game self-check for km3 and the slice's kx3 setting. Every digest must equal the manifest's;
        km3's must be `81b572198c04d5d1`, the pinned km3 (gate 1).
      - A mismatch, or any refusal: **stop, play nothing**, and report it in your status line.
   2. **Play:** `nice -n 19 $HOME/kxc/172cbe9c/strength run --manifest REG/manifest.json --out OUT --only-deck DECK --threads 2`.
      - Start it detached (`setsid nohup ... &`, with its own log), so a session ending can't stop it.
      - It resumes where it stopped: run the same command again after a restart.
   3. **Seal after play:** `python3 rl/strength/split_collect.py seal --manifest REG/manifest.json --program $HOME/kxc/172cbe9c/strength --out OUT`.
      Seal only when the slice shows 160 games (80 kx3, 80 km3) and `errors.jsonl` is empty or absent. Never edit the folder after
      sealing.
   4. **Push between slices:** commit `OUT` (games.jsonl, errors.jsonl if any, worker.json, worker_seal.json, the run's logs) to your
      branch `cloud/think-WORKER`, then push. Never push to main.
4. **Status line.** After each step, and every 2 hours while a slice plays, add one line to `rl/results/thinking_time_2026-10/workers/STATUS_WORKER.txt`
   (in the same commit when you push):
   `<UTC time> WORKER <registration> <deck>: <stamp ok|STOP: why> <n>/160 games, <e> errors, sealed <yes|no>, pushed <commit|no>`
5. **When your slices are done**, say so in one message to the coordinator with your branch and last commit. The laptop merges each
   registration (`split_collect.py merge`) and reads it. You read no results and report none to Dustin.

If something here doesn't fit what you find (a command refuses, a hash differs), stop and say exactly what you saw. Don't work around it.
