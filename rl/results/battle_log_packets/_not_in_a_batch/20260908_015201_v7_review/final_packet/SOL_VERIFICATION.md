# Sol selective verification

Sol performed a read-only targeted review of the Gemini v7 draft against the source recording. The source SHA-256 matched `65B404F8EC8CB712EF9D19FA5BC87E051EDC80050067BC179E8387AE404CE258`, and the recording cutoff was confirmed at 68.120 seconds.

## Confirmed

- The player opens Duraludon Active with Rainbow Cave, Iris, Copycat, and Professor's Research remaining in hand.
- The opponent opens Team Rocket's Rattata Active with Corphish and a second Team Rocket's Rattata Benched.
- Turn 1 is complete: the opponent benches Chien-Pao ex, then ends the turn without an Energy attachment or attack.
- Turn 2 is complete: the player draws and benches Dratini, plays Professor's Research, uses Poke Ball to find Axew, benches Axew, plays Rainbow Cave, uses its effect, manually attaches Metal Energy to Duraludon, and ends the turn.
- The recording shows only the Opponent Turn 3 banner before ending. No Turn 3 action, attack, knockout, score change, or terminal result is shown.
- At the cutoff, the score is 0-0. Duraludon has 100 HP and one Metal Energy; Dratini and Axew are Benched without Energy. The opponent has four Pokemon in play without visible Energy.

## Correction supplied

- Rainbow Cave does not directly convert Fighting Energy into Metal Energy. The generated Fighting Energy is discarded, Rainbow Cave's effect causes the next Energy to be generated, and that next Energy is Metal. The player then manually attaches the Metal Energy to Duraludon.

AI, Solo, and Auto metadata were not independently verified because they do not affect the battle reconstruction. The full available recording was checked. Its clip-specific outcome is unknown because it ends mid-battle, but the confirmed continuation `20260908_015702000_iOS.MP4` resolves the linked full battle as a player win, 3-2. No Astra escalation was needed. Sol did not modify files or registries.
