# Future Pause Games review protocol

Owner instruction received October 2, 2026. Applies to future newly requested games designated for [Pause Games](https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd). Adds to the current full-battle review, source binding, independent lead checks, logging and archive workflow in [START_HERE_VIDEO_REVIEW.md](START_HERE_VIDEO_REVIEW.md). No previous recording is to be reopened for this change. Ladder battles, Auto practice and rules tests keep their existing requirements unless the owner expands the scope.

## Assign and save one packet per game

Owner routing clarification, October 2, 2026: the external Pause Games log contains human battles only. A visible Auto control, even OFF, identifies a computer battle and excludes it from Pause Games and ladder totals. The owner may explicitly request this capture protocol for a computer comparison while keeping its packets and review-index rows local. Honor that destination separately from the deck-list source URL; do not add a computer game to the external artifact.

Give the reviewer this protocol and [the reusable assignment](Review_Log/templates/pause_games/ASSIGNMENT.md). Copy the JSON templates into the new game's packet, remove `.template` from their filenames, and replace template rows with actual observations. If a source contains several games, create a separate game packet and ledger for each; share the frozen source binding and distinguish source-local timestamps. Split clips of one battle stay one game and identify the source file for every observation.

Retain the current SOURCE.json, ASSIGNMENT.json, REVIEW.md, COVERAGE.md, SUMMARY.json, UNCERTAINTIES.json and lead acceptance. Add:

- PAUSE_GAME.json: game and source identities, all five opening cards, the chosen Active, capture completeness and limitations.
- DECK_USED.json: a dated snapshot of the exact 20-card deck copied from the Pause Games log, including duplicates and variant labels shown there.
- TURN_LEDGER.json: exactly one row for each recorded game turn, owner and opponent, with named hand observations, numbered actions and both boards before and after.
- TURN_EVIDENCE.json: setup, draw-based candidate frames, the selected hand views, before-end views, board boundaries, drawn/search cards, opponent fan and discard snapshots, each with source filename and seconds.
- turn_evidence/: the retained full-resolution frames and their bottom-hand and top-screen crops.

Templates and field guidance are in [the template README](Review_Log/templates/pause_games/README.md). These are local packet files for Claude's later analysis; do not change the external artifact's layout or add unsupported fields to its UI. Save the usual game entry and provide a packet reference using its existing supported review-reference field. If that field cannot carry the reference, record the exact source-filename-to-packet mapping in the batch report and external receipt.

## Opening hand

Find a frame before the owner places the Active, with all five opening cards exposed and no card zoom covering the hand. Save the full-size frame and hand crop. Transcribe all five names left to right, including the card chosen as Active, and record that selection separately. Do not mistake the four cards left after placement for the original five. Record any setup redraw or replacement that is actually shown.

An opening hidden by the recording, overlapping cards or a zoom remains explicitly unavailable. The deck list or a later hand is not proof of the missing opening identities.

## Hand frames and timing

For every owner turn, locate the end of the normal draw animation in source time. Capture approximately +1, +3 and +6 seconds, plus one frame just before End Turn. Select the clearest candidate that shows the hand after the draw and before the first play, with the hand spread and no card zoom. Preserve left-to-right ordering, duplicates and any unreadable card slots. Record the owner's ending hand size.

Use native-resolution frames. For each candidate retain the full frame, a crop of the bottom fifth (hand and owner Energy Zone), and a crop of the top covering the opponent's hand fan, clocks and Energy Zone. A top crop can be adjusted to the recorded layout; save its pixel coordinates. The bottom crop is full width from 80% of frame height to the bottom. Do not enlarge a reduced overview and call it full-resolution evidence.

The +1/+3/+6 candidates are tied to the observed draw, not a fixed four-second grid. A coarse overview may locate events but cannot supply this hand record. The existing [frame extractor](Recording_QA/extract_auto_review.py) supports explicit `--times` for full-resolution seeks; use those or an equivalent bounded extraction, then crop the native frames and save the coordinates.

If the owner plays before +1 second, inspect a denser window between the draw and first action. Later candidates that already show a play cannot stand in for the opening hand. Label why a scheduled candidate was unsuitable. Do not assign a missing draw timestamp or manufacture a frame across a cut. When an attack ends the turn without an End Turn button, use the last clear hand before the attack/end action and label that substitution. Also capture the board after the attack, effects, knockouts, replacements and relevant checkups resolve; a pre-End Turn board is not the resulting end board.

## Draws, searches and numbered actions

Name every owner card drawn or found, including the normal draw, both Professor's Research cards, the Pokemon found by Poke Ball, and every Copycat card. Keep each card as a separate entry with its source, reveal order when visible, timestamp and evidence. Hidden opponent draws keep their visible counts with unknown identities. Treat a search as a search, not a normal draw. Track any revealed cards returned, discarded or shuffled away.

Number plays in their exact order within each turn. The first voluntary move is play 1, so Claude can compare the first decision. Include attachments with Energy type, number and destination; every retreat with paid Energy and replacements; switches; Trainers, Tools and Stadiums; abilities; attack and target; and visible system decisions. Preserve the order of nested choices or effects inside the numbered play and link their draw/search entries to that play number.

A zero-heads Misty, an unsuccessful search, a no-effect action and a declined prompt are still recorded. Include the choice at a warning such as "you can still play a Supporter," with whether it was accepted or declined. Automatic effects and checkups have their own ordered event details and are not silently combined with a voluntary card play. Do not label an option declined merely because it was never selected or visibly offered.

Write hand size at the end of every owner turn. Reconcile the start count, additions and removals where the footage permits; mark an inferred count and its basis separately from a directly counted fan. Never silently infer an exact card identity from arithmetic.

## Both boards and Energy Zones

At the start and end of every turn, record both players' Active and every Bench Pokemon, preserving Bench position. For each Pokemon include:

- exact visible name and variant when established;
- current HP, maximum HP and damage;
- attached Energy count and types, including mixed Energy;
- Tool;
- Special Conditions;
- active effects, targets and their remaining duration when established.

Include the Stadium, both point totals and the displayed game turn number. Record effects such as Item lock, an Energy-Zone attachment block and a delayed-damage mark, even when they do not alter HP immediately. Preserve relevant board-wide effects too. Maximum HP must account for visible Tools or other established modifiers; if printed or effective maximum HP is unknown, keep it unknown rather than calculate a confident damage total.

For both players, record the Energy Zone's "this turn" and "next" lines at the turn boundaries: Energy type, visible count or availability, and the evidence. If the opponent's next Energy is hidden, say so. Do not derive it from the apparent deck type. Record Energy left unused and changes caused by effects when visible.

## Opponent hand and discards

At the start of each owner turn, count the card backs in the opponent's fan from the top-screen crop. There is no numeric display to copy. Save the chosen frame and count method. If overlap prevents an exact count, record unknown or a supported range with a reason; never turn a range into an exact number. Reconcile public additions and removals as a separate inference if useful.

Capture each player's opened discard pile every few turns when the recording shows it, aiming for every two to three owner turns and after major discard effects. Record pile contents, duplicates, scroll coverage and which player the pile belongs to. A partial scroll is not the full pile. A play-derived discard history can supplement the observation, with its inferential basis, but cannot replace a requested pile view. If the owner never opens a pile, mark that snapshot as not shown rather than inventing it or requiring a retrospective replay.

## Exact deck beside each game

Read the named deck in Pause Games for the batch before logging and save its exact 20 cards beside every game, with duplicate counts, Energy configuration if the log provides it, URL, deck label, retrieval date/time and captured source text or image. Count the actual 20 card slots, rather than 20 different names. Use the version corresponding to the game; preserve a mismatch or uncertain version if the current log has changed or conflicts with filmed cards. Do not silently repair the log or substitute a list guessed from visible gameplay.

A shared batch snapshot may be reused as the source, but every game must carry its own DECK_USED.json. If the live log lacks a readable full list, document that limit and retain the visible core; do not claim that the exact 20-card snapshot is verified. A later deck edit must not overwrite the saved game snapshot.

## Structured ledger and prose

Use JSON as the default structured format. TURN_LEDGER.json has one row per game turn, including opponent turns. Required row fields are turn number, player, source-local timing, hand at start, draws/searches, numbered plays, starting board, board after, owner ending hand size, opponent hand count, evidence and limits. Both board fields include both players and their Energy Zones. Opponent card identities remain hidden unless revealed; the owner-hand-by-name requirement is for the owner's turns.

Opening setup has its own PAUSE_GAME.json record; it is not invented as turn 0. Keep the existing narrative review and a readable per-game turn table, so the machine ledger supplements rather than replaces prose. Link each prose turn to its JSON row and chosen evidence. A CSV export is optional; the JSON meets the requested JSON-or-CSV requirement.

Represent unknown values as `null` with a reason and evidence status. An empty list means known empty, not uninspected. Preserve observation, inference and owner testimony separately. Names, hand position and event order are not inferred from the deck list. Every source timestamp stays local to its recording; split clips never receive a fabricated continuous timeline.

## Lead acceptance checklist

- All recorded turns and the terminal sequence remain covered by the current full-review process.
- Setup includes five opening slots and selected Active, or an explicit source limitation.
- Every owner turn has draw-based candidate timing and a chosen pre-play hand, before-end hand/count and retained native crops, or a specific unavailable reason.
- Every owner draw/search is named, or each unreadable/hidden slot is explicitly unresolved; Research, Poke Ball and Copycat are individually reconciled when used.
- Numbered action order includes no-effect actions, Energy targets and retreat costs, and observed declines.
- Both start/end boards reconcile HP, maximum HP, damage, Energy, Tools, conditions, effects, Stadium, points, turn number and both Energy Zone lines.
- Opponent fan counts and periodic discard snapshots are evidenced or explicitly unavailable.
- The exact 20-card deck snapshot is saved per game, or its missing/uncertain log version is reported.
- There is one JSON row per recorded turn, matching the prose/table and bound to the source identity.
- The lead independently checks the opening, at least one ordinary owner's first move, consequential draw/search order and ending hand reconciliation, using the retained evidence. Use Astra for consequential ambiguity after bounded inspection, according to the current workflow.

Use `complete`, `complete_with_recording_limits` or `incomplete_review` for this capture supplement. Unknown facts after adequate inspection can be recording limits; uninspected footage or unreconciled material claims are unfinished review. Clearly distinguish full battle review from the completeness of hand/deck replay evidence. No guessed identities are accepted just to fill the template.

## Recording availability

For the fullest future packet, the recording needs to show the five-card hand before Active placement, an unzoomed hand after draws before play, and opened discard piles periodically. Extraction can recover only what is recorded. Do not control or alter the user's gameplay to satisfy this protocol. Report absent views precisely and retain the original footage unchanged.
