# Battle Log OCR review record

**Recorded:** 2026-08-26 (America/Chicago)  
**Location:** Beside the first battle-log video, outside the Pocket Deck Lab project  
**Purpose:** Preserve the independent browser-test findings and the recommended card-resolution workflow for the next project lead.

## Bottom line

The current prototype is workable as a first human-reviewed extraction tool. It successfully reads useful battle-log phrases from the supplied recording, creates editable suggestions, and saves the exact human-approved JSON. Its OCR output is noisy, fragmented, and repetitive, but that is not a reason to reject this stage. Dustin intends to inspect and correct every row.

The project already contains most of the card-name-to-card-code resolver that Dustin described. The missing part is a small UI connection between the OCR review screen and that resolver. This should be the next bounded feature; it does not require a new recognition architecture.

## Read-only browser test performed

Source recording:

`ScreenRecording_08-26-2026 21-47-38_1.MP4`

- HEVC, 1170 x 2532, approximately 175.62 seconds.
- The Linux headless browser could read its duration and seek time, but could not decode video frames. It reported a video size of `0 x 0` and generated a blank `1 x 1` crop.
- The prototype incorrectly called that blank crop successful. It should eventually detect `videoWidth === 0`, `videoHeight === 0`, or a `1 x 1` canvas and give a clear codec warning.
- This is a Linux/HEVC environment limitation, not evidence that OCR or the battle-log workflow is infeasible.
- A temporary H.264 copy was made only in `/tmp`. It loaded correctly at 1170 x 2532, and the selected crop produced a real 1053 x 1899 image. Neither the source video nor the Pocket Deck Lab project was modified.

Tesseract OCR:

- The browser library and OCR worker loaded successfully.
- A full 12-frame sample produced 150 editable row suggestions.
- Useful recognized examples included:
  - `Put in the Active Spot`
  - `Put on the Bench`
  - `An Energy was attached`
  - `Wave Splash`
  - `Took 40 damage`
  - `HP 100/100 > 60/100`
  - `Knocked Out`
  - `Got 1 point`
  - `Healed 20 damage`
  - `Ended their turn`
- There were also nonsense fragments, headers, icons interpreted as text, and duplicates. Card IDs were generally blank because set/card numbers are not displayed clearly in the battle log.

Human review and export:

- Edit passed.
- Add-row passed.
- Delete-row passed.
- Reorder passed.
- Any edit correctly invalidated the previous approval preview.
- Refreshing the preview enabled approval again.
- The approved JSON downloaded successfully, was valid JSON, and matched the displayed preview exactly.

## Card-name to actual-card mapping

### Direct answer

Yes, the desired review process is feasible:

1. OCR proposes a name or partial name and preserves the raw text.
2. Dustin confirms or corrects the name.
3. The existing resolver returns possible playable cards and their DeckGym/set-number codes.
4. The screen shows the differences that matter: HP, move/attack, damage/effect, ability, and whether the card occurs in the decoded deck QR.
5. Dustin selects the correct playable card or selects `Unknown / new card`.
6. Exact artwork is a separate optional choice and must not block approval.

The current OCR prototype does **not** yet provide this candidate picker. It has only a free-text `card_id` field. However, the accepted section 216 catalog and resolver already provide the underlying candidate lookup.

### Identity fields that must remain separate

- `entity_id` / `entity_key`: the playable semantic card identity carried by the deck QR.
- `printing_id` / `deckgym_id`: a specific set-and-number printing, such as `A1 128`.
- `functional_id`: Pocket Deck Lab's mechanics fingerprint.
- `base_deckgym_id`: the representative simulator ID for that functional card.
- `alias_id`: one set/number/artwork alias associated with the playable entity.

For simulator learning, the important answer is normally the semantic/functional card, not the artwork printing.

### Concrete example already verified

If the confirmed name is `Mewtwo`, the current resolver returns two mechanically different candidates:

- `A1 128` — 120 HP, `Power Blast`; printing aliases include `A1 128` and `P-A 010`.
- `B4 070` — 120 HP, `Psychic`; printing aliases include `B4 070` and `B4 212`.

If the player's decoded deck QR contains entity 1280, the resolver reduces that choice to the `A1 128` playable card group. It still cannot say whether the player used the `A1 128` or `P-A 010` artwork because the QR deliberately does not contain printing/art information.

Another useful example is `Unown`:

- `A2a 034` — ability `CHECK`; `A2a 078` is an alternate printing/art alias of this same playable card.
- `A4 084` — ability `GUARD`.
- `A4 085` — ability `POWER`.

This illustrates why choices should be grouped by mechanically distinct playable card. Alternate art codes should be nested under that choice, not presented as different gameplay cards.

### How often name alone is enough

The accepted local catalog contains 2,087 Pokemon functional classes:

- Name alone uniquely identifies 636 classes and leaves 1,451 ambiguous.
- Name plus HP identifies substantially more but leaves 951 ambiguous.
- Name plus HP plus attack title/damage/effect identifies 2,082 of 2,087 classes.
- The remaining five are three ability-distinct Unown and two full-energy-cost-distinct Kartana.
- All 157 current Trainer functional classes are unique by name in this catalog.

These are catalog-uniqueness measurements, not promises about OCR accuracy.

## Can the reader distinguish alternate artwork?

Not reliably, and it generally does not need to for the simulator.

- OCR text alone cannot distinguish artwork.
- The current reader does not perform artwork recognition.
- The small battle-log thumbnail might support optional image/template ranking later, but compression, size, and partial visibility will make it less reliable than name/HP/move matching.
- A deck QR cannot identify artwork. It stores semantic entity IDs, and alternate artworks or rarities of the same playable card share that ID.
- The catalog preserves artwork/printing aliases, so exact art can be recorded later when genuinely known.
- Some identical image files are reused for different printing codes, meaning even perfect visual matching cannot always determine the exact set-number printing.

Therefore the review UI should allow:

- playable card confirmed, exact artwork unknown; and
- exact artwork optionally selected when Dustin genuinely recognizes it.

Artwork uncertainty must not prevent battle events from being used to investigate simulator rules or human decisions.

## How the deck QR helps

The retained public QR format decodes to Pokemon semantic entity IDs, Trainer semantic entity IDs, and energy types. A known player's deck QR can sharply restrict the name candidates to cards actually in that deck.

Recommended behavior:

- Use the known QR as a candidate filter for that player's cards.
- Do not use the player's QR to constrain the opponent's cards unless the opponent deck is also known.
- Keep duplicate quantities from the decoded deck.
- Preserve an unknown numeric entity ID even when the local catalog does not recognize it yet.
- Do not treat QR membership as evidence of exact artwork.

## Team Rocket's Ambition release

The current pinned section 216 catalog is community database release 2.9.2 and stops at set B4 plus existing promos. It does not contain Team Rocket's Ambition.

Consequences:

- The generic QR decoder should still be able to extract new numeric entity IDs if the payload format is unchanged.
- The present catalog cannot attach names, mechanics, DeckGym codes, or printing aliases to those new IDs yet.
- The strict resolver will return `unresolved/stale_catalog` for unknown entities. That is safe behavior, but it must not block the OCR review.
- The UI should permit `Unknown / new Team Rocket card`, retain the OCR text and any QR entity ID, and allow reconciliation after the catalog and DeckGym data are refreshed.
- Artwork-only additions should become aliases of an existing playable entity. Mechanically new cards require new DeckGym mechanics records.

The new release is therefore a catalog-refresh task, not a reason to postpone the first battle-log extraction loop.

## Small next implementation step

Connect the current editable OCR prototype to the existing resolver with the smallest useful interface:

1. Preserve every raw OCR line unchanged.
2. Add a human-confirmed `card_name` field.
3. After confirmation, show grouped playable-card candidates from the section 216 resolver.
4. For each candidate, show base DeckGym ID, HP, attacks/moves, ability, aliases, and known-deck membership.
5. Let Dustin select one candidate or `Unknown / new card`.
6. Store `entity_id`, `functional_id`, and `base_deckgym_id` when selected.
7. Store `printing_id` only when actually known; otherwise leave it null/unknown.
8. Never block transcript approval because the card is unresolved.
9. Do not add artwork recognition, automatic simulator ingestion, or accuracy gates to this step.

## Relevant existing project components

These files are inside `/mnt/c/Users/dacz8/Projects/Pocket Deck Lab` and were inspected read-only:

- `apps/battle_log/s244_battle_log_review.html`
- `apps/battle_log/s244_battle_log_review.js`
- `apps/battle_log/s244_battle_log_review_model.js`
- `s216_card_catalog_v1.json`
- `s216_card_resolver.py`
- `s216_BATTLE_LOG_CARD_RESOLUTION_DESIGN_2026-08-24.md`
- `s216_BATTLE_LOG_CARD_RESOLUTION_RESULT_2026-08-24.md`
- `deckgym-database.json`
- `results/CANON_MAP.tsv`
- `third_party/s216/tcgp-deck-qr-102d75e/docs/format.md`
- `third_party/s216/tcgp-deck-qr-102d75e/src/payload.js`

## Scope and preservation note

This review did not edit the Pocket Deck Lab project or the source recording. The only persistent file created by the independent reviewer is this record outside the project. Browser software, the H.264 test copy, and the approved test download were temporary `/tmp` artifacts.
