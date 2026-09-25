# kd3 mixed rows, Sept 25 (run before kd3's table is read)

**What these are for:**
- kd3 is read against kp3 under the veto rule pre-registered on Sept 25 (rules v2).
- Under v2, a veto counts only when mixed rows on the same deals show that the changed pilot's own side got worse. A mixed row has kd3 on one deck only and kp3 on the other.
- These are those rows. They cover all 28 pairings in both directions, fixed before any kd3 table existed, so no choice depends on which vetoes fire.

**Build:**
- `legality_scan` was built in WSL from `git archive` of 0c0e7f9, the commit the cloud's kd3 table runs at (its 68117fa).
- It is not the official engine. It carries the amended kd:
  - Dustin's option 3 at 97ca8f4.
  - The second-review fixes at 5ae7490.
  - The third-review fixes at 8004222.
- A first attempt at 5ae7490 was stopped after 8004222 changed kd. None of its rows are used or kept here.

**Checks before these rows are used:**
1. **kp3 is unchanged on this build.** kp3 plays the other side of every mixed game. A spot replay of pairings 0–2 (1,500 games) is compared with the kp3 reference files, move by move (`spot_kp3_p0-2_compare.txt`). The cloud's full replay covers the rest.
   - On the stopped 5ae7490 build it matched 1,500 of 1,500 on every field, including the move hash. The 0c0e7f9 result is filled in when its run finishes.
   - The file's last line reads "NOT IDENTICAL" only because compare.py expects the full table: the reference also holds the other 12,500 games, which the spot does not play.
2. **kd3 is the same kd3 as the table's.** When the cloud pushes the finished `kd3_500.jsonl`, its commit must still be 0c0e7f9 (or have the same `engine/`). One pairing of kd3 v kd3 from this build must also match the cloud's file move by move. If either check fails, these rows are rerun on the table's build.

**How they are read:**
```
score.py --rules v2 --old-games kp3_500_* --new-games kd3_500.jsonl --mixed mixed_kd3_first.jsonl mixed_kd3_second.jsonl --old kp3 --new kd3 --limitless limitless_v2_dev.json --limitless-events limitless_v2_dev_events.json
```

**Files:**
- `run_kd_mixed.sh`: the commands.
- `mixed_kd3_first`: kd3 on the first-named deck.
- `mixed_kd3_second`: kd3 on the second-named deck.
- `spot_kp3_p0-2*`: the kp3 spot replay.
- `timing.txt`: wall times.
