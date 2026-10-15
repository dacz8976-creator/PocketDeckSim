# Bounded independent verification

Verifier: sol_batch_check_last. September 30, 2026. This is an independent spot check of the completed primary packet, not a second full-battle review. Read SOURCE.json, REVIEW.md, COVERAGE.md, SUMMARY.json and UNCERTAINTIES.json in full. Source binding is inherited from the recorded intake: 20260930_144608000_iOS.MP4, SHA-256 e048a913159ad112f1ed57a05abd21107a6775c95fb2be80dd19f647e787295b, 347723081 bytes, 189.373333 seconds. No source rehash was performed here.

## Directly inspected saved evidence

All image paths below are relative to this packet directory. No new extraction was needed.

| Exact image path | Source time | Confirmed observation |
|---|---|---|
| overview/sheet_01.jpg | Sample labels 1.5-25.5 s | AI Opponent against Dacz8976 at 4.5; Going second at 7.5; checked Auto in setup; Hitmonchan ex Active, Hitmonchan ex and Passimian ex Bench; Bombirdier Active. |
| keyframes/t0037.00.jpg | 37.00 s | Checked Auto, both scores zero; Bombirdier 70; Hitmonchan 130; opposing Skitty/Zorua/Alolan Grimer Bench. Quick Straight printed 50 and Weakness exclusion readable. |
| keyframes/t0048.00.jpg | 48.00 s | Opponent Professor's Research displayed, Draw 2 cards. This independently checks an ordinary Trainer action without inferring hidden draw identities. |
| keyframes/t0169.00.jpg | 169.00 s | Owner score 2-0, Hitmonchan 40 HP with one Fighting, Gastly 10; Rhyperior 160 with four Fighting, Passimian 130 without attached Energy yet; Potion and Mankey remain in hand. |
| keyframes/t0172.00.jpg | 172.00 s | Same score and Active HP, now one Fighting on Passimian; four remain on Rhyperior. |
| keyframes/t0174.00.jpg | 174.00 s | Final Quick Straight animation shows 50 and explicit damage-is-not-affected-by-Weakness text. |
| keyframes/t0189.00.jpg | 189.00 s | Explicit Victory vs. Alolan Muk Deck (Deluxe Pack: Mega), went second, 12 turns, owner 3/opponent 0, damage done 300; Hitmonchan ex Card of the Game. |

## Consistency assessment and limits

No contradiction found in the inspected visual anchors or packet documents. Coverage intervals span setup, all 12 turns, and terminal result continuously, with targeted checks specified for short actions. Six reported 50-damage attacks reconcile to 300 result damage; 130 minus reported 90 damage reconciles to the directly inspected terminal 40 HP. Six owner attachments reconcile to the inspected final 1 Active + 4 Rhyperior + 1 Passimian. These arithmetic checks assess internal consistency; this verifier did not independently replay all six attacks or every intermediate turn.

Opening AI/Auto and terminal outcome are independently visually confirmed. The saved images support the reported decisive pre-state, final attachment and attack, followed by an explicit 3-0 result. Hidden cards, exact subsecond boundaries, complete deck lists and Auto decision rationale remain outside the check. This bounded sample cannot establish that every primary visual claim is correct, or independently certify continuous Auto state throughout the full video.

Disposition: bounded independent check passed; no consequential conflict or new Astra escalation identified. Excluded from Ladder Log as instructed. Primary packet and original media preserved. No shared log, index, map, ladder write or source move performed by this verifier.
