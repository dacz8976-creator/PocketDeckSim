# Slow report: real-program smoke (km3 on both seats, no kx3 game played)

**This is a check that the wrapper works against the real frozen program and against real rebuilds of it, not a result about any deck.** `rl/strength/slow_report.py` was run end to end
with the pinned program (`/home/dacz8976/kx/strength`, sha256 `5a8f5c83...`, the exact file in `slow_report_pin.json`) and, for run 3, with real rebuilds of the pinned source made by
`rl/strength/build.sh` as it is committed with this folder (cargo 1.93.1, three builds of about 7 minutes each, the machine otherwise idle). The pin used is a **copy**
(`builds/pin_smoke_copy.json`) whose pilot is the cheap **km3** (about a second a game), so the headline says `km3 (smoke, not kx3)`; the copy also has `seed_reserved` emptied, so the runs
take the slots the real pin reserves for them (684, 685 and 686). No kx3 game was played. The deck is a copy of the content of a held-out list (`07-skarmory-stall`) saved as
`decks/events/smoke-held.txt` in a scratch checkout (not committed), to exercise stage `use`: the run was accepted, the held-out names were recorded under `heldout_registry` /
`heldout_in_run`, `heldout_decks` is empty for the program's own guard, and `heldout_locked` stayed true. Because the pilot is km3 on both sides, the score and the km3 comparison on the
page (+0.0, every difference the same) say nothing about a deck.

**The pin copy is not the committed pin, so every run here was registered with the test-only variable `SLOW_REPORT_ALLOW_UNCOMMITTED_PIN=1`** (see `smoke.sh`). The wrapper otherwise
refuses a pin that is not byte-equal to the one committed at HEAD ("REFUSED: the pin is not the committed one: ... Nothing was written."; shown in step 5 of `smoke_console.txt`, with git's
own first line). The variable is recorded: `pin_committed: bypassed` and the reason are in each manifest and PREREGISTRATION.md, the page says "**NOT the committed pin**", and the texts
that would say "the committed pin" (the registered engine text, the self-check lines, the rebuild paragraph, the program-changed line) say "the pin file in use (NOT the committed pin: test use)"
instead. The scratch checkout is not a git repository either, so "not a git repository" is what git said.

What each part shows (all in `smoke_console.txt`, as run; the commands are `smoke.sh`):

1. `--dry-run`: the plan lines, question first ("question: how does ... do when km3 plays it ..., and is that better than ..."), then the size as "32 km3 games + 32 cheap km3
   baseline games ... 64 games in all", the school-morning note, the pin line, "stage use ... the held-out lock is untouched"; nothing written.
2. **Run 1** (`run1_complete_under_nohup/`, seed slot 684): started under `nohup`; a `SIGHUP` was sent in the middle and the wrapper kept running (the handler leaves an ignored SIGHUP
   ignored); a second wrapper on the same folder was refused while it ran; the run finished with 64 games, registered before the first game, with the page (`SLOW_REPORT.md`: Question,
   then Size "32 km3 games + 32 cheap km3 baseline games", every range saying which games it refers to), `REPORT.md` and the log (a `sitting_call` event records the school-morning
   choice used and the sha256 of the program that sitting ran; `school_choice_overridden` is false when the resume command is run as printed).
3. **Run 2** (`run2_sigterm_and_resume/`, slot 685): a `SIGTERM` after 6 games: exit code 143, the log says `interrupted`, **no program left running**; `--dir` resumed with the 58
   games missing; 64 games, 64 distinct keys (no game played twice); the page is the finished one.
4. **Run 3, the cloud route with real rebuilds** (`run3_cloud_route_real_rebuild_and_restart/`, slot 686):
   - `build.sh` built the pinned source (engine ref `d513e37b`) with cargo to `rebuilt/strength` and wrote the build record beside it (`builds/first_build.build.json`): engine tree as
     archived `31dbd2e6e8ec...` (equal to the pin's `engine_tree`), harness source `bf9c5d68...` (equal to the pin's), rustc 1.93.1, cargo 1.93.1, machine, jobs, the build folders, the
     environment variables it removed (none were set) and the cargo config files that apply (none) and the exact rebuild command. The program's sha256 is `c06238fb...`, **not** the pinned
     `5a8f5c83...`: a rebuild is not byte-identical to the pinned binary here, which is why the wrapper replays the self-checks instead of comparing bytes.
   - Registering with `--program` was refused first without the test variable (pin not committed), then accepted with it: the wrapper took the *rebuilt* route, read the build record (it must
     exist, be for this file and have the pinned tree and harness), replayed the self-check on that program (km3 only here, because the smoke's pilot and reference are both km3; a real
     cloud registration replays kx3 and km3) against the pin's digest, and recorded `program_route: rebuilt`, the build record (in the manifest and on the page, with its sha256), the
     registering machine, the school choice (off) and a resume command that carries it.
   - A **restart** was simulated by running the same `build.sh` command with other build folders (`build2` / `target2`) to the same output path: the new program has sha256 `18f39c0b...`
     (`builds/second_build_other_folders.build.json`), again not the pinned one and not the registered one. `--dir --dry-run` said what a resume would do ("another sha256 than registered;
     its build record is for the pinned source, so a resume would replay both self-checks again ... and log it as 'program changed mid-run'"). The resume (a slice of 8 games, `--max-games
     8`, counted across both arms) checked the pin against the registration, replayed the self-check, found it equal, logged a **`program_changed` event** (old and new sha256, the new
     record, the self-check text, where it was replayed) and played the 8 games; the page says "**The program changed mid-run** ... 0 games of the 8 played so far were started before this
     change and 8 after".
   - **The registered command, again from scratch.** The first build's own `rebuild_command` was run once more with the build and target folders removed first
     (`builds/third_build_same_command_from_scratch.build.json`; the record names the main checkout's `build.sh` because the smoke built with `STRENGTH_REPO` pointing there to read the
     pinned commit, so the build.sh under test was run instead, all else as recorded). Its program is **byte-identical** to the first build (sha256 `c06238fb...` both times; the records
     differ only in `built_at`, `program` and `rebuild_command`). So on this machine the recorded command does give the registered bytes back, and a different build folder (the second
     build) does not. One machine, one toolchain, one cargo cache: this is not a claim about the cloud image.
   - Three refusals, each with nothing written: `/bin/true` (no build record beside it), a program whose build record says another engine tree
     (`builds/forged_for_the_refusal.build.json`), and a pin that points at the rebuilt copy without `--program` (the message points at `--program`).

These builds were made by `build.sh` as it was at dc403ed7. Four small changes were made to it afterwards and are tested with stub tools only (no real build was repeated, because the laptop was busy with a long run): the `rebuild_command` in a record names the script that ran (here the records name the main checkout's `build.sh`, because the smoke built with `STRENGTH_REPO` pointing there), the harness hash is taken from the copies that were compiled, the scratch repository that computes the tree id has attributes switched off, and the record gained `build_fs` (so the records in `builds/` have no such entry).

Not shown here: the school-morning cut against the real program (covered by the unit tests with a fake program and clock), a real kx3 game or a real kx3 self-check replay (hours),
whether the kx3 digest comes out the same on another CPU or libm (untested: the first cloud registration will say, and is refused if it does not match), the `build.sh` lock, failed-cargo
and environment-removal behaviour (covered by the unit tests with stub tools; the real builds here had nothing to remove and nothing failed), and what the build record cannot prove
(it is written by the same script on the same machine; a hand-made one with the pinned values would be accepted, and only the replayed self-checks stand behind the bytes).
`games.sha256` holds the hashes of the games files (runs 1 and 2: about 200 KB each, not copied; run 3 is copied) and of the pinned and the three rebuilt programs. The manifests record
the scratch checkout's path (`repo_root`) as registered.
