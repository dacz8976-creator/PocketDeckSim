# Bounded independent verification

Verifier: sol_batch_check_last. September 30, 2026. Independent spot check of the completed primary packet, not a second full-battle review. Read SOURCE.json, REVIEW.md, COVERAGE.md, SUMMARY.json and UNCERTAINTIES.json in full. Source binding is inherited from the intake: 20260930_145405000_iOS.MP4, SHA-256 5ffb8cd9f98fc90eedcb61778bc3c9716caffdbf84714eb92883a59993f9eac8, 267745666 bytes, 147.196667 seconds. This verifier did not rehash media.

## Directly inspected saved evidence

Paths are relative to this packet. Six reusable images inspected; no new extraction.

| Exact image path | Source time | Confirmed observations |
|---|---|---|
| sheet_01.jpg | Sample labels 1.5-25.5 s | AI Opponent vs Dacz8976 at 4.5, Going second at 7.5, checked Auto in setup; Growlithe Active and Magmar Bench; Galarian Meowth Active; opponent develops Beldum/Rookidee/Meltan Bench. |
| keyframes/t0038.00.jpg | 38.00 s | Ordinary Growlithe attack animation; Dig Claws printed 20; Galarian Meowth printed Fire Weakness +20. Poke Ball discard and second Magmar in hand are visible. This animation frame is not treated as a stable post-attack HP readout. |
| reconciliation.jpg | Exact labels 38,44,45,65,71,103,110,118,121 s | At 44, checked Auto, Meowth20/Growlithe70 and owner Fire; 45 Slash animation. At71 first point and Growlithe50. At103 evolved Arcanine ex110 with three Fire facing Meltan70. At110 second-point award. At118 second Meltan70, Arcanine90 and score2-0; 121 Beam animation. The 65-s Meowth10 readout is a transient damage animation, not a contradictory stable HP state. |
| keyframes/t0129.00.jpg | 129.00 s | Pre-terminal score2-0; Arcanine70 with three Fire, Meltan70 with one Metal; Magmar80/Charcadet60 Bench with empty center; Charmander in hand; generated Fire remains in Energy Zone. Inferno Onrush120 and 20 self-damage text visible. |
| keyframes/t0132.50.jpg | 132.50 s | Meltan0, Arcanine50, same three Fire and two-point score during knockout processing. Supports terminal knockout and20 recoil; generated Fire still visible. |
| keyframes/t0147.00.jpg | 147.00 s | Explicit Victory vs Aegislash Deck (Deluxe Pack: Mega), Arcanine ex Card of the Game. Faded result panel remains readable: went second, eight turns, owner3/opponent0, damage360. |

## Coverage consistency and limits

No material discrepancy found between directly inspected anchors and primary documents. Coverage ranges cover setup, every turn1-8, ending and results without an interval gap. Reported attacks40+40+140+140 reconcile to360 result damage. Reported accumulated damage40 before evolution leaves Arcanine110 of150; subsequent recoil20, Beam20 and final recoil20 reconcile to independently inspected90,70 and50. Direct visual anchors support three Fire on Active and unused turn8 generated Fire.

This sample independently establishes AI/Auto at sampled phases, ordinary action, evolved decisive board, terminal knockout/recoil and result. It does not independently replay all four attacks, every brief Trainer action, the exact evolution instant, or continuous Auto status. Sheet artwork may show transient animated HP, so only stable states are reconciled. Hidden hand/deck contents, precise subsecond ordering and Auto rationale remain unknown as the primary packet states. Challenge title alone is not evidence of an Aegislash play.

Disposition: bounded independent check passed. No consequential conflict or new Astra escalation identified. Ladder excluded as instructed. Primary files and original media preserved; no shared log/index/map/ladder write or media move by this verifier.
