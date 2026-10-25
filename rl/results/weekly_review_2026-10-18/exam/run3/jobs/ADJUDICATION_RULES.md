# Exam v2: the adjudication rules (v1.6's rules, restated without any of v1.6's point answers)

Source: exam v1.6 (commit 5518fd60), `exam/README.md` (scoring and the v1.2-v1.6 sections) and `exam/build/B_BRIEF.md`. Nothing here names a v1.6 point or its answer. Written Oct 21, 2026, for run 3 (PREREG_RUN3.md); updated Oct 24 (UTC) for addendum 5 (certified_by, the v2 chance actions, the first segment's stop at an opponent's choice, drops only with evidence).

## 1. What a point is
- **The turn:** one whole turn of Dustin's in a real ranked game.
- **The position:** the board at the start of that turn, his whole hand, and the engine's list of legal first actions.
- **No hidden future:** no deck order, no next draw, no coin result, nothing he learned only later.

## 2. The key (the "key_rule")
- **The key** is what a good player of his decks would do, using his judgment.
  - It is **his recorded move** by default (`his_move`, always kept as the record).
  - Only where Dustin himself later says otherwise does `key_line` hold a different key, and then `recorded_move_acceptable` is false.
- **Acceptable alternatives** are other WHOLE-turn lines that a strong player with the SAME plan could reasonably choose in this position.
  - Each one carries a one-line reason.
  - List only genuinely comparable lines. It is fine, and common, to list none.
  - A line is a set of actions, unless order changes the outcome; then say so.
  - Write each line in the engine's legal labels (`Name#{json}` form for actions with arguments).
- **Rejected alternatives** are lines ruled out by Dustin's words or by the coordinator's decision from them. Each carries `certified_by`: `dustin` or `coordinator_decision_from_his_words`, nothing else (PREREG_RUN3 addendum 5, G4: v1.6's `coordinator_interpretation` is not used in v2). They never count.
- **Ambiguous:** when the labeller genuinely can't tell whether his move or an alternative is better, the point gets ONE plain question for Dustin.
  - Aim for a handful: at most 6 in this part (each part is about v1.6's size, and v1.6 allowed 6). The exam is labelled in 5 parts, so at most 30 in all (PREREG_RUN3 addendum 8, K7).
  - The alternative is held as pending (it doesn't count) until he answers. His words are stored verbatim.
- **answer_kind**, one of:
  - prepare: get something ready for a later turn;
  - sacrifice: let a Pokémon fall, or not save it, for a later gain;
  - attack now: deal damage or a knockout this turn;
  - abandon: drop the planned line because it can't work now.
- **why_his:** one line on what his move achieves, from the review and the card text.
- **deck_kinds** (per deck, by how the deck must be played; several allowed): fast pressure, evolution and setup, Bench preparation, sacrifice and recovery, control and combinations. Each kind gets a one-line justification from the list and the card text.

## 3. Mechanical rules (applied by the assembly, not by the labeller)
- **Chance actions:** Professor's Research, Poké Ball, Copycat, Lisia, Sightseer, Lucky Ice Pop, Quick-Grow Extract's evolution step, and `UseStadium` while Mesagoza is the Stadium, plus any other card whose effect draws, searches, flips a coin or picks at random. For v2 (PREREG_RUN3 addendum 5, M1 and R1) this covers:
  - Wallace's evolution step (as Quick-Grow's);
  - `UseStadium` while Fragrant Forest is the Stadium;
  - Lusamine's AttachFromDiscard when the discard holds 3+ Energy of 2+ types;
  - using Dustox's Variety Powder;
  - using Team Rocket's Raticate ex's Thieving Incisors (R1).
  - Quick-Grow and Wallace: the player picks the target, and the evolution card is random. The segment ends at the pick.
  - Playing a Stadium is never a chance action. Using a deterministic Stadium isn't one either.
  - Big Malasada is NOT a chance action, although its text removes "a random Special Condition". This follows from R1: the frozen plan lister forecasts one outcome there and doesn't stop (addendum 5, M1 and G13).
- **The first segment** of a line is its actions up to and including its first chance action, or its first action after which the OPPONENT must act (Sabrina; a knockout during the turn, after which he picks a new Active), whichever comes first; the whole turn if it has neither.
  - This is R1, ACCEPTED by the coordinator on Oct 24 (coordinator-038, mailbox id 20261024T0210Z; addendum 5, G13): the first segment is exactly where frozen-7's plan lister ends the plan the line reaches.
  - `run3/check_lister_v2.py` reports it for every accepted line before the freeze. Where cut() differs, the lister's segment is recorded and used.
- **Draw-first orders:** where a line's draw could legally come first, the draw-first order is accepted for Research, Poké Ball and Lucky Ice Pop, and not for Copycat (the cards played first would be shuffled away). It applies only where the draw is in that turn's legal list.
- **Scope** (`segment_scope`) is set by the shortest accepted segment:
  - "full" only if every accepted line's first segment holds all of that line's strategic actions;
  - "none" if his own segment holds none of his;
  - otherwise "partial".
  - Plan-segment agreement uses "full" points only. Prefix agreement uses every eligible point.
- **Matching** is by replay: both segments are applied to the position and the states compared up to the chance boundary. Label matching is a reported fallback only.
- **Validation:** every recorded, key and accepted line must be legal step by step in the legal-moves-only tool, with no unmatched action and no search (no PGDUMP line).
  - A point is dropped ONLY with the verbatim tool output that forces it (addendum 5, G1).
  - An accepted ALTERNATIVE that fails is removed from that point, with its output recorded; the point keeps its key line. This was accepted by the coordinator on Oct 24 (coordinator-038; addendum 5, G13): an illegal alternative can't be picked by either bot, so the rule is symmetric.
- **Exposure:** a game whose answer material reached the judge's developer is excluded from the primary, kept and reported separately with a dated reason.
