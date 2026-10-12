# Both kx3 versions on Dustin's 121 pause-game positions (the spec; written Oct 12, before any run)

**Why.** Sonnet's read of the new pause games (`../pause_games_new_2026-10-12/`, main b0805130) has 121 of Dustin's real turn starts with
his first move and plan, and km3's at 12 seeds (first move agrees in 55 of 115). This is the largest set of his real decisions we
have. The coordinator asked for the frozen kx3 and the candidate kx3 on all of them, read quiz-4 style: per position, Dustin v km3 v
frozen v candidate.

## Programs: all three bots on the official engine (main-c045ede), each in Sonnet's harness

The harness is `pg_pos` (`/home/dacz8976/pgd/build/engine/examples/pg_pos.rs`), patched print-only by `pgd_patch.py` (the 8c score
dump plus action labels). It was built on main-8626a35, whose `players/` has no kx3, so it is rebuilt three times, each from a git
archive of the commit's `engine/` with `pg_pos.rs` added and `pgd_patch.py` applied:
- **F (the frozen kx3):** laptop/kx3-on-rules2 cd20a97a, d513e37b's players on c045ede's engine (step 4). Bot code `kx3`.
- **C (the candidate kx3):** a second merge made the same way, 172cbe9c (the combined candidate's code) + c045ede0, with
  `git merge-tree`. Checks: `players/` byte-equal to 172cbe9c's, and every other engine file the side that changed it. Bot code
  `kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m64`.
- **K (km3 on the new engine):** either build. It re-measures km3's column on the official engine; Sonnet's ran on main-8626a35.

Before any position, each build's `strength`-style check is its `pg_pos` km3 output on 5 positions not flagged for rules switch 2. It
must equal Sonnet's km3 runs at the same seeds (the engine is identical outside the 26 switch files, and those positions touch none).

## Positions and seeds

- **Positions:** `positions_all.json` as committed at b0805130 (121; none marked held out).
- **Seeds:** 1-12, as Sonnet's km3, so each bot is compared at the same seeds.
- **Rules switch 2:** the 35 positions flagged in `position_list.tsv` are read separately. In those, the engines differ by design.
- **The opponent:** unknown in every game (hidden cards filled from the pilot's own list), so every row stays "approximate", as in
  Sonnet's read. Status conditions are not represented (15 positions).

## Cost first: a measured pilot before the shards

Sonnet stopped the frozen kx3 after more than 6 minutes on one position at 12 seeds with all 16 laptop cores. That is at least about
96 core-minutes per position, and the candidate costs about 2.9 times as much. The coordinator's estimate of about 65 sandbox hours is
therefore probably several times too low, so the first step measures it:
- each of F and C on 3 positions (one early turn, one middle, one late), 12 seeds, on one 4-core sandbox, timed;
- from that, the full cost at 12 seeds, and at 4 seeds as a cheaper option: the first-move share is then out of 4.

The coordinator and I then choose the seeds and the shard count. Dustin chooses only if the cost is large against the week's credits.

## Shards (Managed Agents, after the pilot)

- **One shard per deck family**, so a shard's positions share a deck file. The families: Kingdra ex / Weezing ex 35; Aegislash 14;
  Conkeldurr 22; New deck 6 17; New deck 24 6; Scolipede 5; the rest as `position_list.tsv` lists them.
- **Per shard, one bot:** F and C are separate shards, so a C shard's 2.9× cost doesn't hold up F's.
- **The brief:** the Managed Agents brief's shape. Build its `pg_pos` from the named commit, check the 5 km3 positions, run its
  positions with `--only <id>` one by one (so a lost sandbox costs one position), and tar the `runs_<bot>/` folder with its sha256.

## The reading (the laptop's)

- **Per position:** his first move and plan; the first-move distribution over 12 seeds and the modal plan for each of km3 (new
  engine), F and C; agree or differ as Sonnet defined it (first move 10 or more of 12; plan cut after a draw card or Sabrina).
- **Tables:** by deck and by what differs: Item/Supporter order, retreat, evolution, energy, attack. Whether the candidate
  agrees with him more than the frozen kx3 does, paired by position.
- **"Neither" cases:** positions where none of the three bots makes his first move in a majority of seeds. They are listed for his
  next quiz.
- Flagged positions get their own table.
- Nothing is decided on this: it describes how the bots play his real positions.
