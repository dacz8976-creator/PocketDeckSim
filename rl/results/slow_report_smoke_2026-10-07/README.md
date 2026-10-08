# Slow report: real-program smoke (km3 on both seats, no kx3 game played)

**This is a check that the wrapper works against the real frozen program, not a result about any deck.** `rl/strength/slow_report.py` was run end to end with the pinned program
(`/home/dacz8976/kx/strength`, sha256 `5a8f5c83...`, the exact file in `slow_report_pin.json`) but with a copy of the pin whose pilot is the cheap **km3** (about a second a game),
so the headline says `km3 (smoke, not kx3)`; that copy also has `seed_reserved` emptied, so the runs take the slots the real pin reserves for them (684, 685 and 686). No kx3 game was
played. The deck is a copy of the content of a held-out list (`07-skarmory-stall`) saved as `decks/events/smoke-held.txt` in a scratch checkout (not committed), to exercise
stage `use`: the run was accepted, the held-out names were recorded under `heldout_registry` / `heldout_in_run`, `heldout_decks` is empty for the program's own guard, and
`heldout_locked` stayed true. Because the pilot is km3 on both sides, the score and the km3 comparison on the page (+0.0, every difference the same) say nothing about a deck.

What each part shows (all in `smoke_console.txt`, as run; the commands are `smoke.sh`):

1. `--dry-run`: the plan lines, question first ("question: how does ... do when km3 plays it ..., and is that better than ..."), then the size as "32 km3 games + 32 cheap km3
   baseline games ... 64 games in all", the school-morning note, "stage use ... the held-out lock is untouched"; nothing written.
2. **Run 1** (`run1_complete_under_nohup/`, seed slot 684): started under `nohup`; a `SIGHUP` was sent in the middle and the wrapper kept running (the handler leaves an ignored SIGHUP
   ignored); a second wrapper on the same folder was refused while it ran ("another slow_report.py (pid ...) or the program it started is already running ... (kill -TERM -<program
   pgid>)", exit 1); the run finished with 64 games, registered before the first game, with the page (`SLOW_REPORT.md`: Question, then Size "32 km3 games + 32 cheap km3 baseline games",
   every range saying which games it refers to), `REPORT.md` and the log (which now has a `sitting_call` event recording the school-morning choice used).
3. **Run 2** (`run2_sigterm_and_resume/`, slot 685): a `SIGTERM` after 6 games: exit code 143, the log says `interrupted`, **no program left running**; `--dir` resumed with the 58 games
   missing; 64 games, 64 distinct keys (no game played twice); the page is the finished one. Its registered resume command carries `--school-rule off` (the smoke runs register with the rule off).
4. **Run 3, the cloud route** (`run3_cloud_route_rebuilt_registration/`, slot 686): `--program` with a copy of the pinned binary plus one trailing byte (sha256 `61b95a0a6370...`,
   not the pinned `5a8f5c83a791`, the same behaviour): the wrapper took the *rebuilt* route, replayed the self-check on that copy (km3 only here, because the smoke's pilot and reference
   are both km3; a real cloud registration replays kx3 and km3) against the committed pin's digest, recorded `program_route: rebuilt`, the harness source hashes (the checkout's equals the
   pin's `bf9c5d68...`), the school choice (off) and a resume command that carries it, and printed the command that plays the run. Then two refusals, both with nothing written: a program
   that prints no self-check (`/bin/true`) is refused ("the self-check of km3 does not match the pin"), and a pin that points at the rebuilt copy without `--program` is refused with the
   message that points at `--program`. `engine_tree_in_checkout` is null here because the scratch checkout is not a git repository (informational then).

Not shown here: the school-morning cut against the real program (covered by the unit tests with a fake program and clock), a real kx3 game or a real kx3 self-check replay (hours),
the engine tree check against a real checkout (tested with a temporary git repository). The fresh kx3 report for a real deck is the next step, on the cloud per the plan.
`games.sha256` holds the hashes of the two `games.jsonl` files (about 200 KB each, not copied) and of the rebuilt copy. The manifests record the scratch checkout's path (`repo_root`) as registered.
