# Deck journal build: report for the laptop's review

Built from `rl/deck_journal/SPEC.md` by the Sonnet credit worker. Standard library only; no engine binary, no cargo.
Files: `journal.py`, `test_journal.py` (17 tests: the spec's 9 groups, 15 tests, plus 2 extras), `first_fill.py`,
`journals/01-muk-glimmora-kingambit-regigigas.json` and its generated `.md`. Run the tests with
`python3 rl/deck_journal/test_journal.py` (add `-W ignore` to silence `lib/deck_check.py`'s unclosed-file warnings).

## First fill (done)
- Deck 01 (`35d98d0dcaf2`): origin "deck file on main" (first commit Sept 24). 19 bot results: replay_b on the
  current engine (km3 and kx3, 32 games each), 17 older-engine results from 8 strength / thinking-time runs, and the
  km3 floor (`floor_dustin_2026-09-30`, older engine). `replay_a` of the rules2 runs holds no deck 01 games.
- His list (`73dfed58d1d6`): parent deck 01 (inferred), the 4 diff lines and the 2 printing-only lines the spec
  names, 12 `played` games bound by filmed deck code (all 12; none binds to deck 01), reason "not stated", plus one
  note that deck 01's file is not the list he plays. Its list comes from `KW261013_010837000.txt` (25 committed
  KW files have this list; any would give the same id).
- The view says "Bots: none on this list yet" for his list, and no deck 01 number appears under it.

## Where I followed the spec over the repository, or had to choose
1. **No `versions.json` exists on main yet**, and no Kingambit predictions file. The ladder paths
   (`ladder_from_notes`, `ladder_from_reading`, `add-result --kind ladder` / `ladder-notes`) are tested only on
   synthetic games and a synthetic reading result, not on a real reading. No Kingambit ladder result is filed.
2. **The setup tester is not on this branch.** I assumed the `setup` result's shape (run folder, tester file sha256,
   seeds, deals, clock, measures with x/n, a pass-through `paired_vs_parent`; the tool computes the Wilson range).
   `add-result --kind setup --measures <json>` reads `{"measures": {name: {"label","x","n","clock"}}, "paired": ...}`.
   The view shows "Setup odds: not computed yet" until a setup result exists. Change the reader when its output is fixed.
3. **A bot result needs a deck file.** His list has no file on main, so a bot number can't be filed under it (the
   check against "this file or a committed copy with the same card list" has nothing to compare). That is the
   spec's own rule (bot numbers only under the id that bot played) taken literally.
4. **Extra fields in an entry** beyond the spec's JSON: `file` (deck file path or null), `file_first_commit_date`
   (for the view's "(Sept 24)"), `origin_source` (the list file or packet, checked committed). Every result has
   `kind, at, by, source, commit`.
5. **"Committed"** means tracked, no uncommitted edits, at HEAD of the working clone; the result's `commit` is the
   last commit touching the source. The append-only check runs against the file on disk and against `main`'s copy
   (or `origin/main` if there is no local `main`); a stale local `main` only makes the check weaker, not stricter.
6. **Order of `diff` lines**: removals first, then additions (the spec's example interleaves them; pairs can't be
   told apart from the code). `printing_only` lists each distinct swap once, however many copies.
7. **`played` result**: filled from the packet's `SUMMARY.json` `result` only when it is win, loss or draw
   (7 of 12 have it); otherwise null. The view does not show it (not a ladder game).
8. **The spec's "KW files reproduce all 12 filmed codes exactly"** is not re-tested; binding compares card sets, as
   the spec says. The curly-apostrophe test rewrites the KW list text; it doesn't read a packet's own list.
9. **Dates in the view** come from the iOS video names (local time), not UTC.
10. **Older-engine runs filed**: all 8 manifests that name deck 01 (`strength_*` x6, `thinking_time_2026-10/reg_m16_b`
    and `reg_m32_b`). The spec said "the older-engine strength runs"; I took every committed run that tested the file.
    The view collapses them into one line with the range of their numbers (they mix bots and settings).
11. Not done: the second Haxorus list files (spec: their own deck's journal); the view's "kx3 games n of N total"
    wording (each bot line says its own games); no `--fill` for other decks (`first_fill.py` is Kingambit only).
