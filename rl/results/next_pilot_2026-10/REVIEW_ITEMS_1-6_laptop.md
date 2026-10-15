# ky3 items 1-6: the laptop's code review (Oct 15)

**What I reviewed:**
- the six commits on `sonnet/ky3-pilot`, 805ea224 to b8ab8f4c, each diffed against 9a0bc5ac;
- the item 5 and 6 job reports;
- the code as written against `DESIGN_NOTE.md`, `DESIGN_NOTE_CASES.md` and `BUILD_BRIEF.md` on main.

**What I didn't do:** I ran nothing. The review was one reader with no workflow, and I checked each finding against the code, git and the repository. No gate may run until the fixes marked "before gate" are in.

## Verdict

| item | verdict |
|---|---|
| 1. ky3 with no switch | **Fits.** `closest_list` is F's d513e37b fallback line for line: the same distance, the same tie rule and one `gen_range`. F is "the frozen kx3's players (d513e37b)" in the replay_a/b records. The self-check prints 31d638dbc818b0fa, and km3 still prints 81b572198c04d5d1. "F's move at every seed" is still gate 2's job. |
| 2. `_infer` | **Fits.** `closest && !infer`. Off, nothing changes. kx refuses the switch. |
| 3. `_punch` | **Fits.** It is bit-equal when off: the `punch` check short-circuits `kd_attacker`, and `punch_turns` is `None`. The note's six tests are there, and the threat pick uses 120. The move cap isn't rewired, which the note allows. One test is weaker than asked (L2). |
| 4. `_queue` | **Fits.** It is gated by the search flag and set only through `km_with_corrections` on ky's own seat, so the simulated opponent stays plain km3. Every `ExpectiMiniMaxPlayer` literal carries `false`. One test is weaker than asked (L2). |
| 5. `_atk` | **Two fixes before gate 1** (M1, M2). Parse, `skip_stands`, the board copy and the watch are sound. The watch reads only: a test pins it move for move. It reads after the checkup, because `finish_turn_after_checkup` advances the turn. |
| 6. Position tools and EXPECTED.md | **Incomplete** (M3, M4, L1). The tools look right, but no old position has been exported yet. |

## Fix before gate 1

**M1. `_atk` never treats km3's own attack as "km's move."**
- `km_line` is set only for a km3 move that is *not* an attack (playout_player.rs, `atk_review`). When km3 proposed an attack, that attack joins `moves` with `is_km_line: false`. `atk_pick` then plays the best-scoring free attack, which can be a different attack from km3's.
- This is `_atk`'s main positive case: 6 of F's 8 skips are F leaving km3's attack. The note says "ky3 plays km's move if km's line attacks this turn."
- **Fix:** flag the attack equal to `report.candidates[0].action` (always km3's move, at :1309/:1411) as the km line.
- **Test:** two free attacks, where km3's attack scores lower and is still picked.

**M2. "Looked" is not recorded when no attack does anything, or when a step fails.**
- `atk_review` returns silently in these cases: no attack damages and km3's line doesn't attack (`moves` empty), `attack_effects` panics, or every play-out round fails.
- Gate 1 counts a negative only if `_atk` "looked" in 6 of 12 replays, and gate 2 matches the games "where it never looked". Both need a reliable signal.
- 10 v Altaria 1|0 t7 is exactly the empty-`moves` case ("does something" fails). It would read as "not exercised" though the rule looked.
- **Fix:** write a reason on every return after the look condition: "_atk looked: no attack does anything", "_atk: effects failed", "_atk: play-outs failed".
- **Test:** a Sing-only board.

**M3. The old positions are not exported, and the job's reason is wrong.**
- The item 5 report says the combined run's `games.jsonl` and manifest "aren't in the repo". They are, on this branch and on main:
  - `rl/results/strength_2026-10-08_kx3_combined/games.jsonl` (3.7 MB) and `manifest.json`;
  - the development run's at `strength_2026-10-03_kx3_dev/`.
- Section A's positives, the 13 same-position turns, 03 v Vespiquen and draft A v Blaziken all come from this export. So gate 0 can't start without it.
- **What's left:**
  - a `requests.tsv` (case id, game key, decision, km3_move) built from the skip records;
  - the old-tree build and `--export` (as `run_skip_exact.sh` builds it);
  - `skip_positions.py`, with kept.json and dropped.tsv committed.
- It costs no API credit if the laptop does it (C: is at 40 GB free) and takes about 1-2 hours. The orchestrator decides who.

## Fix or label before the cases are used

**M4. Game 3 T4's opponent is a 14-card world.**
- His hand of 2 and deck of 2 were chosen so that pg_pos's check passes. pg_pos's `filler` means "the opponent's exact 20-card list", and his `deck_count` must equal what the list leaves. The video didn't show those counts.
- The real deck held 6 more unseen cards. In every play-out his next draws are exactly Magnezone, Miraidon ex, Cyrus and Poké Ball, and his deck is empty after two turns.
- As a paired keep check this is tolerable if it is labelled approximate. km3 retreats into Whimsicott ex at 12 of 12, and F and ky3 see the same world. It isn't tolerable as `_expo`'s negative later.
- **Also unchecked** (the job says so): whether `KX_EXTRA_LISTS` accepts a 14-card list. It must, or F and ky3 never get Miraidon ex.
- **Fix:** before gate 0, check the load. Then either pad the unseen part to the video's counts with a stated no-name filler, or carry the "approximate world" label into every result for this case.

**L1. Deck 13-A G5 T4 isn't built.** It is an adoption-blocking negative (DESIGN_NOTE §5), so build it by hand like game 3 T4 before gate 1. Otherwise gate 1's report must say adoption can't be judged.

## Minor

**L2. Two unit tests are weaker than the cases file asks.**
- `_queue` VK_110 only asserts a jump of more than 9,000 at a depth-zero leaf. The ask was Place:Pawniard's root score of about 11,781, against 1,691.
- `_punch` total 5b uses a lone Mega Kangaskhan ex at 1 point, not FINDINGS' t09 board.
- Either use the FINDINGS boards, or say in the test why not.

**L3. The orchestrator should confirm the skip rule's reading.**
- Code: a skip stands when the mean is at least t **and** the mean is more than 2 SE above 0.
- The other reading: mean minus 2 SE is at least t.
- The code's reading lets skips stand more often. That's the safer side for the right-to-pass cases, so I'd keep it. It's a one-line confirmation.

## One design question (not a defect)

`_atk` plays the attack *now*, in place of the chosen move. So on a turn where the chosen move is setup (an attach, a Bench placement, an evolution), the attack ends the turn before that setup. The note says exactly this, and the retreat skips (06 v Lucario 4|1 t3) need it: a look only at End Turn would miss them.
- The cost falls on the Bench-building failure Dustin named.
- 10 v Suicune 4|1 t3 (evolve Natu, no Peck) is the gate 1 negative that measures it.
- No change now. If that negative fails, the next round could look only at End Turn and at moves that remove the attacker.

## Who and what next

- **Code fixes (M1, M2, plus the L2 tests):** small, about 50 lines with tests. Use the credit worker on `sonnet/ky3-pilot`, but not in `~/credit_work/ky3` while the item 7 driver uses it.
- **M3:** the laptop or the credit worker, as the orchestrator decides.
- **M4 and L1:** by hand, before gate 0 and gate 1.
- Item 7 branched from 5f63372d, which comes before `_atk`, so these fixes don't touch it.
