# Full-file coverage reconciliation

Source: `20260926_213750000_iOS.MP4`, SHA-256 `7e8cc6827c198327ecf60628c46a2a7fbb03acf8eaaaac6c3e16b0e272346530`, duration 370.74 seconds.

| Source interval | Coverage | Result |
| --- | --- | --- |
| 00:00–00:20 | Lead-in, deal, coin result, opening board | Reviewed; player goes second. |
| 00:20–01:04 | Turns 1–2 | Reviewed; both players develop, no points. |
| 01:05–02:29 | Turns 3–4 | Reviewed; player survives at 10 HP, evolves, and damages Entei ex. |
| 02:30–03:19 | Turn 5 | Reviewed; Mega Charizard Y ex appears, Entei ex KOs Linoone, opponent scores 1. |
| 03:20–03:59 | Turns 6–7 | Reviewed; Obstagoon damages Entei ex to 10 HP, no score change. |
| 04:00–04:44 | Turn 8 | Reviewed; Entei ex is KO'd, player scores 2. |
| 04:45–05:29 | Turn 9 | Reviewed; first Crimson Dive KOs Obstagoon, opponent scores 1. |
| 05:30–05:44 | Turn 10 | Reviewed; Zweilous damages Mega Charizard Y ex. |
| 05:45–06:00 | Turn 11 | Reviewed; second Crimson Dive KOs Zweilous, opponent reaches 3. |
| 06:00–06:10.74 | Terminal state and summary | Reviewed; Defeat and Card of the Game shown, then file ends. |

Coverage method: stable-state sampling across the whole file at five-second spacing, with source-resolution checks around attacks, KOs, point screens, score transitions, and the final result. The review covers the complete available footage. The selected stills are representative evidence, not substitutes for the source video.

No discontinuity, cut to another match, missing terminal result, or uncovered source interval was found. Brief animations can occur between sampled stable states; ambiguous card interactions are kept uncertain in `REVIEW.md` rather than reconstructed from expected play.
