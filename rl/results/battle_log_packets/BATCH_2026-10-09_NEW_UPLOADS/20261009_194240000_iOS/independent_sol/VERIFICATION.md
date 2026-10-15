# Independent Sol verification

Verifier: `/root/verify_194240`, model `gpt-6-sol`, effort `high`. Decision: **ACCEPT**. Source: `20261009_194240000_iOS.MP4`, SHA-256 `eaf837456911cdebf75c99c2b09a1f3f68bab9b2e8bfd4990cc3d4d3b648d630`, 117061306 bytes, 67.645624 seconds. Elapsed source times below are supported by the packet's original-resolution stills, 1 fps overview and reused dense contact sheets. This was a bounded independent check, not another full first pass.

## Independently checked evidence

- At 2-4 seconds the chosen opponent is AI-labeled Greninja ex Deck (Deluxe Pack: Mega). The Auto option changes from OFF to ON before Battle is launched. The Auto badge stays on during play (`contact_00.jpg`, `contact_01.jpg`, `contact_03.jpg`). This is a computer battle, excluded from Ladder Log and Pause Games. The enabled Auto control supports attributing the owner's in-battle choices to Auto rather than a manual player choice.
- Setup at 14-25 seconds shows the owner going second, Electrike Active against Froakie Active, both at 60 HP, with both Benches empty and 0-0 points. The opening five visible cards are Electrike, Copycat, Heliolisk, Field Blower and Professor's Research (`contact_01.jpg`, `contact_02.jpg`, `evidence/setup_hand.jpg`, `evidence/active_pair.jpg`). Hidden deck contents remain unknown.
- Independently sampled ordinary turn, opponent turn 1 at 25-34 seconds: the opponent plays Professor's Research around 28.4 seconds and Soothing Shore around 31.8-33.4 seconds. The Research draw identities are hidden. No visible Energy attachment, Bench play, attack, damage, condition or point change occurs. Froakie and Electrike stay at 60 HP (`contact_dense_A_00.jpg` through `contact_dense_A_03.jpg`). The phone notification obscures the very top of the display during part of this interval but does not obscure the Active Pokemon, Bench slots or displayed Trainer cards.
- Owner turn 2 at 34-46 seconds: Mega Manectric ex is drawn. Its visible card text says Stage 1 and Evolves from Electrike. The card remains in hand, with no evolution performed. The owner plays one Professor's Research, and the two cards shown arriving in hand are Cyrus and another Professor's Research. Neither drawn Supporter is played. One Lightning Energy is attached to Electrike. No search, Tool play, switch, status or healing is visible (`evidence/draw_mega_manectric.jpg`, `contact_dense_C_00.jpg` through `contact_dense_C_02.jpg`, `contact_dense_B_00.jpg` through `contact_dense_B_03.jpg`, `evidence/lightning_attach.jpg`).
- At 46-58 seconds Quick Attack flips heads. The game displays 60 weakness damage against Froakie's 60 HP; Froakie reaches zero, leaves the Active position, and the owner receives exactly one point. Electrike remains at 60 HP with a Lightning Energy. The empty opposing Bench explains the immediate ending (`contact_05.jpg` through `contact_07.jpg`, `evidence/coin_heads.jpg`, `evidence/weakness_60.jpg`, `evidence/point_award.jpg`). There is no other knockout or score change.
- At 60-67.646 seconds the game declares the owner victorious. The summary says went second, two turns played, owner one point, opponent zero points, and 60 damage done against Greninja ex Deck (Deluxe Pack: Mega) (`contact_07.jpg`, `contact_08.jpg`, `evidence/results.jpg`). The deck label does not show Greninja ex entering play.

## Reconciliation

I read the completed `REVIEW.md`, `COVERAGE.md` and `FINDINGS.json`. A draft `REVIEW.md` incorrectly said Mega Manectric ex could not evolve directly from Electrike. Direct inspection of `evidence/draw_mega_manectric.jpg` showed the opposite. The lead corrected the review to the observed facts, and I re-read the corrected file. Its timeline, classification, result, score and stated limits now match the independently checked source. The six coverage intervals span setup through the result page with no uncovered battle phase. The exact final bytes read for this acceptance have these SHA-256 hashes:

| Primary file | SHA-256 |
| --- | --- |
| `REVIEW.md` | `b33461fbc4f44c80661b2d19f26b1b3ac4ca64d99082b079f8e0509699c7be60` |
| `COVERAGE.md` | `f34467dd30a183db58c273e540a544c3720670d622703eb10d3aebc364870a58` |
| `FINDINGS.json` | `fbd4ace3e8762509211afd5318fabe25b981234b2990f97283e4bfdeb56d0f70` |

Required changes: none. If any of these primary files changes, recheck the changed content and refresh its hash before relying on this acceptance. Opponent hand contents, Research draw identities and the full owner deck list remain unknown from the footage.
