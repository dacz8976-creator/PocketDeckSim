# Ogerpon video intake and sparse triage

Date: 2026-09-07 (America/Chicago)  
Scope: two newly arrived recordings; read-only intake and sparse visual review

## Source identity and relationship

Both source files were hashed twice after arrival. Their sizes, modification times, and SHA-256 values remained unchanged across the review. Detailed container/stream metadata is in `metadata/SOURCES.json`.

| Label | Recording | Bytes | Duration | SHA-256 | Triage |
|---|---|---:|---:|---|---|
| A | `20260908_010207000_iOS.MP4` | 448,053,217 | 240.60 s | `f4956d25fdc445c48fec9d6705de40a4721e37367bece727aa0d7e50e09ccc1f` | Separate Water matchup; no Ogerpon is visible in the 13 sparse frames. |
| B | `20260908_012720000_iOS.MP4` | 530,226,009 | 282.63 s | `b9e76626643d8950cb7a4277487da2262b5fa96faf9e87454495ebe896d47085` | Ogerpon-containing game. |

These do not appear to be split parts of one match. They have different creation times about 25 minutes apart, different decks and boards, and each sparse sequence runs from its own loading/opening state to its own terminal result or point-resolution screen.

## Ogerpon game

Recording B visibly contains **Teal Mask Ogerpon ex** on the owner's side. The green checked **Auto** control is visible during ordinary board states and both focused status sequences, consistent with Auto being enabled.

Two status-prevention events are readable:

- Around 95 seconds, the Teal Mask Ogerpon ex card/Ability callout shows **Soothing Wind**. At 100 seconds, the game reports **“Teal Mask Ogerpon ex didn't become Poisoned.”** Ogerpon already has attached Energy in the surrounding board frames.
- Around 195 seconds, the opposing Team Rocket's Weezing ex uses **Confusion Gas**. At 200 seconds, the game reports **“Teal Mask Ogerpon ex didn't become Confused.”**

The first sequence is consistent with an attempted Poison from the visible Poison Barb interaction; the decisive video-bound fact is the explicit failed-to-become-Poisoned callout following the Soothing Wind display. The second sequence directly pairs the named Confusion Gas attack with the failed-to-become-Confused callout.

These frames demonstrate prevention while Ogerpon already has Energy. They do **not** show an already afflicted Pokémon receiving Energy and recovering, so this intake makes no recovery-on-Energy claim. They also do not establish the complete timing of every effect between sampled frames.

Recording A remains useful as an ordinary unrelated battle, but its sparse sample contains no Ogerpon or status-prevention/recovery event suitable for this focused question.

## Artifacts and method

- `contact-sheets/a_sparse.jpg`: 13 frames, 0–240 seconds in 20-second steps.
- `contact-sheets/b_sparse.jpg`: 15 frames, 0–280 seconds in 20-second steps.
- `contact-sheets/b_status_focus.jpg`: ten focused frames around 85–105 and 185–205 seconds.
- `frames/`: the individual low-resolution frames used by those sheets.
- `EXTRACTIONS.json`: timestamps, exact one-thread extraction arguments, decoder identity, and contact-sheet input order.
- `ARTIFACT_MANIFEST.json`: byte sizes and SHA-256 values for every preserved artifact other than the manifest itself.

Every video frame was obtained with an independent seek and a single decoded frame. The videos were not decoded end to end. No OCR, engine build, simulation, Cargo command, source edit, or project/Boss write was performed.
