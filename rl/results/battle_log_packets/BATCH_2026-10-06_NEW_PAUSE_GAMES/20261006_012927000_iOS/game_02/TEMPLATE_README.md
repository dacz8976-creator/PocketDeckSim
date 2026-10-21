# Pause Games packet templates

For future newly requested Pause Games reviews only. Read [the complete protocol](../../../PAUSE_GAMES_REVIEW_PROTOCOL.md) and pass [ASSIGNMENT.md](ASSIGNMENT.md) to the reviewer. Previous games and recordings are outside this change.

Copy these files beside the new game's current review, drop `.template` from each copied name, and fill them from the recording and the named live-log deck:

- [PAUSE_GAME.template.json](PAUSE_GAME.template.json): source bindings, opening five slots and selected Active, file references and capture completeness.
- [DECK_USED.template.json](DECK_USED.template.json): the exact live-log deck snapshot with 20 total card slots, duplicates preserved, retrieval provenance and version conflicts.
- [TURN_LEDGER.template.json](TURN_LEDGER.template.json): one actual row per game turn, owner and opponent.
- [TURN_EVIDENCE.template.json](TURN_EVIDENCE.template.json): source-local frame candidates and selections, native crop coordinates, discard views and unavailable captures.
- [REVIEW_SUPPLEMENT.md](REVIEW_SUPPLEMENT.md): add its opening, per-game turn table and capture-limits sections to the existing prose review.

The JSON files are clearly marked `is_template: true`. Set that to false in filled copies. `not_reviewed`, `not_captured` and the example row are scaffolding, not evidence. Replace them rather than claim a completed packet with untouched placeholders. Do not copy a previous game's completed hand or deck into a new game.

Each source record points to the corresponding frozen SOURCE.json and its actual filename and SHA. Each image has an evidence ID, source filename, seek timestamp and retained image paths. Reference IDs from the hand, action, draw, board and discard records. Keep requested seek time distinct from an actual frame timestamp when that timestamp has not been measured. Crop pixel bounds use `[x0, y0, x1, y1]`; bottom crops span the full width and final fifth of native height. Preserve the full frame too.

Opening `cards_left_to_right` always retains the five original slots; the selected Active is recorded separately. In each owner-turn hand, preserve every visible position and duplicate. Use card objects with `position`, `name`, `variant` if established, `basis`, `evidence_ids` and `limit_reason`. A hidden/unreadable slot has a null name and a specific reason, rather than being removed from the array. An exact hand count can still be known while a name is unreadable.

`hand_at_start` describes the acting player's hand. For owner turns its identities should match `owner_hand_start`. Opponent identities are unknown unless revealed. Count the opponent's fan at each owner turn start in `opponent_hand_at_owner_turn_start`; public transaction arithmetic is an inference recorded separately, not a replacement for a visually counted fan.

Repeat the example `plays_in_order` object for each actual voluntary action, numbering from 1. Use kinds such as card_play, energy_attachment, retreat, switch, ability, attack and prompt_response. Record visible no-effect attempts as actions with their result. Nested choices/effects remain ordered inside the action, and draw/search groups link to the action number that caused them. The normal turn draw has no linked voluntary-play number. Add each Research card and each Copycat card individually. Actions with no card, such as a retreat or declined warning, have a null card name with the action kind and details filled.

Use the Active Pokemon shape for every object in `bench_in_position_order`. Both board states contain owner and opponent, maximum/current HP, damage, typed Energy, Tool, conditions, active effects, points, Stadium and both Energy Zones. An effect should identify its name, source, affected player/Pokemon, restriction or mark, and expiry if visible. End board is after the ending action and its consequences, with phase timing explicit.

Use null for unknown or unreviewed values and explain the limitation. Use an empty array only when the relevant list is known to be empty; use `"none"` for an observed absent scalar such as no Tool or no Stadium, and 0 only for an established zero count. Do not derive hidden future Energy or hand identities from the deck list.

DECK_USED.json uses `cards_in_log_order` with exactly 20 names or name/variant objects for a verified list. Duplicate names occupy separate slots. `counts_by_name_and_variant` records the corresponding quantities, whose total must also be 20. If the list or game version cannot be verified, keep `exact_list_status` limited and explain why. Captured log text or an image must be saved locally beside the snapshot or linked to a preserved batch snapshot.

Turn count, action order, draw identities, HP/Energy/point changes and hand counts must agree between the ledger and prose. Preserve all inspected recording limitations in PAUSE_GAME.json. Capture status after review is complete, complete_with_recording_limits or incomplete_review. No changes to the battle-completion or archive rules are implied.
