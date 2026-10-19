# Exam of Dustin's ladder decisions, 2026-10-19

## What it is
The exam holds 51 decision points from 27 of Dustin's real ranked games (Oct 14-16). Each point is one whole turn of his.
- **Each point gives:** the board, the engine's full list of legal first actions, what Dustin did, and any other turns a strong player with the same plan could reasonably have chosen.
- **It asks:** does a bot play these turns the way a good player of his decks would?
- **No bot has seen it:** no bot was developed on these games (they aren't in stage A, the Oct 18 diagnostic or the pause-game sets), and no bot has been run on these positions.

File: `exam_2026-10-19.json`, format `pds-exam-v1.5.1`. One file serves any bot: km3, kx3, the AI judge, and later an external bot through upstream's `docs/bot-protocol.md`.

## What a candidate may see (`bot_view`)
A candidate sees only `points[i].position` and `points[i].legal_root`.
- **`position`:** pg_pos's input. It carries no "force" line and no hidden future: no deck order, no next draw, no coin result.
- **`legal_root`:** the engine's legal first actions. These are the full list, not any bot's candidates.
- **The answer key:** everything under `points[i].answer`, and `answer_kind`. It must never be shown to a candidate, the AI judge included.

## The file
- **Top level:**
  - `decks`: the list file, deck kinds and why;
  - `categories`, `coverage` and `untested`;
  - `scoring`, `free_chance_first_decision` and `known_limits`;
  - `points`.
- **Each point:**
  - `id`, `game`, `deck`, `deck_kinds`, `answer_kind`, `source` (the game's REVIEW.md and the turn), `position` and `legal_root`;
  - `answer`, which holds:
    - `his_move`: his whole turn, as engine labels;
    - `first_segment`: his actions up to and including his first chance action;
    - `acceptable`: other whole turns, each with a reason;
    - `ambiguous`: a question for Dustin, or null;
    - `why_his`;
    - `legal_steps`: the engine's legal list at each step of his line, up to the first hidden draw or coin;
    - `free_chance_first_variants`.

## Scoring (operative contract, v1.3; fixed before any candidate output)
The `scoring` field in the JSON is authoritative; this summarises it.
- **Candidate view:** only `position` and `legal_root`. Nothing under `answer`, and not `answer_kind`.
- **Segment:** a candidate's first segment is its actions up to and including its first chance action, or its whole turn if it has none.
  - Chance actions are Professor's Research, Poké Ball, Copycat, Lisia, Sightseer, Lucky Ice Pop, a random evolution pick, and `UseStadium` while Mesagoza is the Stadium.
  - Playing a Stadium is never a chance action, and using a deterministic Stadium (Rainbow Cave, for example) isn't either.
- **Two metrics, reported separately:**
  - (1) prefix agreement on every scored point;
  - (2) plan-segment agreement on the points with `answer.segment_scope == "full"` (19 of the 51 points).
  - A point is "full" only if EVERY accepted segment (his and each acceptable line) holds all of that line's strategic actions; its shortest accepted segment sets its scope (`scope_rule`). "partial" and "none" points count for prefix agreement only.
  - Prefix agreement is not plan quality.
- **A match:** the segment matches `answer.first_segment` or the `first_segment` of any `acceptable` line.
  - Matching is by replay: both segments are applied to the position and the resulting states compared up to the chance boundary.
  - Label matching is a fallback only, must be reported as such, and compares labels with `build/label_adapter.py` `same_action()`, so targets are never dropped.
- **The key (v1.5):** what a good player of his decks would do, using his judgment. It's his recorded move by default; where he said otherwise, `answer.key_line` holds the key (`key_rule`). All 51 points are scored. Lines in `answer.rejected_alternatives` never count. Points with `decided_game: true` are also reported separately.
- **Statistics:** game-level bootstrap, paired across candidates; an unclear difference is "inconclusive". Results are per deck kind and answer kind, always labelled "three decks only".
- **Labels:** see `label_format`. Arguments are kept as `Name#{json}`.
## Deck mix
| deck | points | deck kinds (how it must be played) |
|---|---:|---|
| 12 (Whimsicott ex / Ariados / Ogerpon ex) | 14 | fast pressure, evolution and setup, Bench preparation, control and combinations |
| 13-A (Alolan Ninetales ex / TR Raticate ex) | 23 | evolution and setup, Bench preparation, control and combinations |
| Kingambit, list A | 14 | evolution and setup, Bench preparation, sacrifice and recovery, control and combinations |

Kingambit is one hard case (27% of points), not the gatekeeper. The answer kinds are prepare 23, attack now 23, sacrifice 5 and abandon 0 (v1.5).

## Coverage, deck kind x answer kind
A point usually tests more than one deck kind, so the rows aren't independent and add up to more than 51.

| deck kind | prepare | sacrifice | attack now | abandon |
|---|---:|---:|---:|---:|
| fast pressure | 0 | 0 | 7 | 0 |
| evolution and setup | 14 | 3 | 12 | 0 |
| Bench preparation | 17 | 4 | 11 | 0 |
| sacrifice and recovery | 3 | 2 | 2 | 0 |
| control and combinations | 16 | 3 | 15 | 0 |

## What is untested
- **Abandon:** there are no points. None of his usable recorded ladder turns had him drop his plan.
- **Fast pressure:** there are only attack-now points (7), all from deck 12.
- **Sacrifice:** there are 5 points, so results are indicative only.

## How the labels were made
- **His move by default:** `his_move` is exactly what he did. It was checked label by label against the engine (BUILD.md).
- **Alternatives:** the Opus labelling agent added them from the review, the card text and the Pocket rules. They appear only where another whole turn was comparable, and each has a one-line reason. There are 13 across 11 points.
- **Ambiguous points:** 5 points carry a question for Dustin. Their alternatives are marked "(pending Dustin's answer)".
- **No bot output was seen while labelling.** No bot ran, and no bot result files were opened.
- **The laptop's final check:**
  - It removed each position's `kind` field, which leaked the answer kind.
  - It moved the answer key under `answer`.
  - It added `first_segment`.
  - It recorded the free-chance decision.

## Known limits
- **Order around a draw:** settled in v1.2-v1.3 (`answer.draw_first`): draw-first is accepted at 7 points and not at 3 (Copycat, and one turn where Lucky Ice Pop isn't yet legal).
- **Approximate positions:** every position is approximate on the opponent's side. Their list is unknown, and their hand size and discard are estimated from the review (BUILD.md).
- **First-turn Energy:** fixed in v1.2. LAD-20261016_024253000_iOS-t1 (going first) has no Energy on turn 1, and Attach is no longer in its legal_root.

## Provenance (`build/`)
- **The inventory:** INVENTORY.md and inventory.json, covering 36 games and 178 of his turns: 91 usable and 19 near-usable.
- **The selection and build:** selection.json, BUILD.md, positions.json and legal.jsonl.
- **The legal-moves-only patch:** `pg_pos_legal_only.diff`, applied to stage A's pg_pos source. It never constructs a bot.
- **The worker briefs:** INV, A and B.
- **Cost:** credit jobs of $1.95 (inventory), $4.14 (build) and $2.35 (labels).

## v1.2 changes (Oct 19, before any candidate output; Astra's checkpoint-1 review)
Made by a recovery copy of the laptop session. No bot, judge or API call was used. The changes:
- **Candidate view:** `position.approximate_reason` and `notes` now hold only a generic note. Some of the old text named later draws or coin results; it moved to `answer.build_notes`.
- **First segments:** recomputed with one rule for every line. A segment ends at the first chance action: a draw, search, coin, random pick, or UseStadium on Mesagoza.
- **Scope:** each point carries `answer.segment_scope` (full 20 / partial 10 / none 21). Plan-segment agreement uses only "full"; prefix agreement is reported separately and is not plan quality.
- **Draw-first orders:** settled in `answer.draw_first`.
  - Accepted for Research, Poké Ball and Lucky Ice Pop (9 points; added to `acceptable`).
  - Not accepted for Copycat (2 points: the cards played first would be shuffled away).
- **Dustin's 5 points:** set to `status: pending_dustin`. Their alternatives moved to `pending_alternatives` and don't count. These points aren't scored until he answers.
- **Matching:** precommitted as replay equivalence, not label sets (see `scoring`).
- **Fixes:**
  - LAD-20261016_024253000_iOS-t1: going first, turn 1 has no Energy. `energy_now` is now none, and Attach left `legal_root`.
  - LAD-20261016_020517000_iOS-t2: `UseStadium` added after Play:Mesagoza; its flip found Glimmet.
  - The two Quick-Grow Extract lines now name their target: benched Spinarak (in_play_idx 1) and the Active Cottonee (in_play_idx 0).
- **Every point** carries `fresh: true`.
- **Re-validation:** all 51 positions re-checked with the legal-moves-only tool (`build/legal_v12.jsonl`): 0 problems, 0 PGDUMP lines.
- **Previous version:** `exam_2026-10-19.v11_43265934.json`.

## v1.3 changes (Oct 19, before any candidate output; Astra's follow-up 20261019T1122Z)
Made by the same recovery copy. No bot, judge, build or API call was used. The changes:
- **Stadium rule:** `UseStadium` is a chance action only while Mesagoza is the Stadium. Playing a Stadium is deterministic.
- **Mesagoza lines:**
  - LAD-20261016_024253000_iOS-t1: `UseStadium` added. The review says he used Mesagoza's coin (tails).
  - LAD-20261015_210617000_iOS-t6: the alternative whose reason is Mesagoza's free coin now actually flips (`UseStadium`).
- **An illegal alternative removed:** the Lucky Ice Pop-first line in LAD-20261016_015753000_iOS-t5. Pop isn't in that turn's legal_root, so draw-first isn't accepted there. 7 draw-first points remain accepted, and 3 are not. (v1.2 said 9 accepted; that was a miscount, it was 8.)
- **Labels:** answer-key and legal_root labels now use the judge's `Name#{json}` form (`build/label_adapter.py`, lossless, fixture-tested).
- **Legality checks:** every recorded, accepted and pending line (71 lines) was checked with the existing legal-moves binary (`build/vlines_v13.jsonl`): no unmatched action, 0 PGDUMP lines.
- **Unrun checks** (no rebuild was possible, C: under 0.5 GB free):
  - Steps after a hidden draw or coin can't be checked (45 lines stop there).
  - `UseStadium` after `Play:Mesagoza` is unchecked, because the tool stops at Play:Mesagoza.
  - The judge's exact label string depends on serde_json's key order, assumed sorted. Comparing parsed arguments avoids depending on it.
- **Snapshots:** `exam_2026-10-19.v11_43265934.json` and `exam_2026-10-19.v12_fa6c9b7e.json`.

## v1.4 changes (Oct 19, the live laptop session; before any candidate output)
No bot, judge, API call or search was used. The legal-moves tool was rebuilt (12 s, 2 jobs, nice 19) and printed 0 PGDUMP lines.
- **Scope rule (coordinator):** a point's `segment_scope` is set by its shortest accepted segment.
  - It is "full" only if every accepted line's first segment holds all of that line's strategic actions.
  - It is "none" if his own segment holds none of his.
  - Otherwise it is "partial", and the point counts for prefix agreement only.
  - The parts are recorded in `segment_scope_by_line` and `segment_scope_his`. The old value is kept as `segment_scope_v13`.
  - One point changed: LAD-20261015_210617000_iOS-t6, full → partial. Its accepted Mesagoza-coin line scores only Play:Mesagoza + UseStadium, before the Energy and the attack.
- **Counts:**
  - all 51 points: full 19, partial 11, none 21;
  - the 46 scored points (5 pending Dustin): full 17, partial 11, none 18.
  - Full scored points by deck: 13-A 10, Kingambit 5, deck 12 2.
  - Full scored points by kind: attack now 8, prepare 7, sacrifice 2.
- **The rebuilt checker:** `build/pg_pos_legal_only_v14.diff` against stage A's pg_pos; binary sha256 prefix dcefe4eabbe56873.
  - Playing Mesagoza is now deterministic (applied). `UseStadium` while Mesagoza is the Stadium is the chance stop, matching the scoring rule.
- **Re-validation of all 71 lines** (51 his, 14 accepted alternatives, 6 pending), in `build/vlines_v14.jsonl` and `build/VALIDATION_v14.json`:
  - **On the candidate positions:**
    - 0 position problems, and every forced action is legal.
    - The tool's chance stop equals the line's `first_segment` in 70 of 71 lines.
    - The one exception is LAD-20261014_153908000_iOS-t6: its segment ends at Quick-Grow Extract's random evolution pick. That is the engine's own pick, which the tool shows but doesn't apply; his target, benched Spinarak, is among its options.
  - **UseStadium after Play:Mesagoza** is now checked: legal and the chance stop in LAD-20261016_020517000_iOS-t2 (his line) and LAD-20261015_210617000_iOS-t6 (alt0).
  - **After the chance:** the build's verification variants put the recorded draws in the hand up front, take out the chance actions, and apply the coin results as reviewed.
    - 43 of the 46 lines with a chance action were validated to the end.
    - In the other 3, every action matched, and the tool stopped only at EndTurn, because Hiking Trail draws at the end of the turn (161324 t5 his and pend0, 143111 t10 his).
    - 25 lines have no chance action.
- **Still unvalidated:**
  - **The coin outcome of the alternative Mesagoza flip** in 210617 t6 alt0: its continuation is checked assuming tails, since an alternative has no recorded outcome.
  - **`UseStadium` in LAD-20261016_024253000_iOS-t1:** it comes after Copycat. Its continuation is checked with the reviewed tails, but the UseStadium step itself isn't separately checked in the post-Copycat state.
  - **The draws inside the variants** are the review's account of what he drew. They can't check whether a candidate's different draw would make the same later actions legal; a candidate gets the engine's own draw.
- **Snapshot:** `exam_2026-10-19.v13_4b72704f.json`.

## v1.5 changes (Oct 19, the live laptop session; before any candidate output)
Dustin answered the 5 pending points. His exact words are stored in `answer.dustin_answer`, and the coordinator made the labelling decisions. No bot, judge, API call or search was used.

**The general rule (`key_rule`):** the key is what a good player of his decks would do, using his judgment.
- It is his recorded move by default. `answer.his_move` always stays the record.
- Where he said otherwise, `answer.key_line` holds the key, and `answer.recorded_move_acceptable` is false. That applies to 2 points.
- `answer.first_segment` is the key's first segment.
- Lines he or the coordinator ruled out are listed in `answer.rejected_alternatives` and never count.

| point | his answer, in short | key | changes |
|---|---|---|---|
| 161324 t5 (deck 12) | sacrificing Spinarak was the better option; Whimsicott ex knocked out ends the game | his move | X Speed into Whimsicott ex: rejected. X Speed with Cottonee Active as the sacrifice ("could have been considered"): added as acceptable, with his reason for keeping X Speed |
| 225451 t4 (13-A) | Sabrina pulled up the Rotom ex with 1 Energy so it can't get its second | his move (Sabrina) | keep-Sabrina line: rejected |
| 031512 t2 (Kingambit) | "Not attacking was a mistake"; Pawniard stays in hand until something is knocked out | Poké Ball, Darkness on Glimmet, Hang Down, Pawniard kept in hand | his recorded no-attack line and bench Pawniard + Hang Down: rejected. answer_kind prepare → attack now (the key now deals damage this turn; old value in `answer_kind_v14`) |
| 031512 t8 (Kingambit) | not much benefit either way | his move | the Pawniard-Energy line: acceptable too |
| 215114 t10 (13-A) | attaching to Rattata "would have been the better move there". He first said the game was over, then corrected it on re-watching: he won (v1.5.1) | the Water goes on the new Rattata | his recorded line: rejected as play quality. Not `decided_game` (his correction) |

- **Counts:**
  - answer kinds: prepare 23, attack now 23, sacrifice 5;
  - scope over all 51 points (all scored): full 19, partial 11, none 21;
  - full points by deck: 13-A 11, Kingambit 6, deck 12 2;
  - full points by kind: attack now 9, prepare 7, sacrifice 3;
  - lines: 16 acceptable alternatives, 2 key lines, 5 rejected lines.
- **Re-validation:** all 69 lines (51 recorded, 2 keys, 16 acceptable) were checked with the rebuilt legal-only tool, in `build/vlines_v15.jsonl` and `build/VALIDATION_v15.json`.
  - 0 position problems and 0 PGDUMP lines.
  - Every forced action is legal.
  - The chance stop equals the first segment in 68 of 69 lines. The other is Quick-Grow's engine random pick, as in v1.4.
  - After the chance, 42 lines were validated to the end. 3 matched every action and stop only at Hiking Trail's end-of-turn draw, including the new X Speed / Cottonee line (8/8). 24 lines have no chance action.
- **Snapshot:** `exam_2026-10-19.v14_f71de2a9.json`.

## v1.5.1 (Oct 19): Dustin's correction for 215114 t10
His words: "For 5. I think I thought I had lost, but just finished the video and I won. The energy attachment to rattata didn't matter, but would have been the better move there".
- The key is unchanged: the turn's Water goes on the new Rattata.
- His recorded line is still not acceptable.
- The point is no longer `decided_game`, so no point carries that flag now.
- The correction is stored with his earlier words in `answer.dustin_answer.correction`.
- No line changed, so v1.5's validation stands.
