# Coverage checklist

**Current status: full battle independently accepted, registered and archived unchanged. Competitive result destination: Pause Games.**

Reviewer: sol_competitive_20261002_021402000; gpt-6.1-sol/high. Complete first pass of 0-430.026667s. Lead acceptance complete.

One extraction used `extract_auto_review.py --step 4 --width 390 --decode-threads 2`, retaining 108 frames in `overview/sample_frames` and twelve contact sheets. All twelve sheets were inspected. Native gaps were filled using the same helper with exact timestamps and two decode threads. No duplicated broad extraction occurred. Native composites are crops of retained source frames, with labels only.

| Phase | Reviewed | Source references |
| --- | --- | --- |
| Matchmaking/setup, 0-35s | Yes | sheet 01; native 35 |
| Owner turn 1, 35-52s | Yes | sheet 02; native 48 |
| Opponent turn 2, 52-72s | Yes | sheet 02 |
| Owner turn 3, 72-82s | Yes | sheet 03 |
| Opponent turn 4, 82-98s | Yes | sheet 03; native 92 |
| Owner turn 5, 98-112s | Yes | sheets 03-04 |
| Opponent turn 6, 112-130s | Yes | sheet 04; native 122,124 |
| Owner turn 7, 130-148s | Yes | sheets 04-05 |
| Opponent turn 8, 148-204s | Yes | sheets 05-06; native 160,165,171,177,180,188,193,199,205 |
| Owner turn 9, 204-280s | Yes | sheets 06-08; native 205,211,232,236,241,249,254,263,265,268,272 |
| Opponent turn 10, 280-314s | Yes | sheet 09; native 291,296,300,309 |
| Owner turn 11, 314-366s | Yes | sheets 09-11; native 331,336,350,360 |
| Opponent turn 12, 366-396s | Yes | sheet 11; native 373,383,386,392 |
| Owner turn 13, 396-408s | Yes | sheet 12; native 402,410 |
| Opponent turn 14, 408-424s | Yes | sheet 12; native 410,416,422 |
| Terminal result, 424-430.026667s | Yes | sheet 12; native 429,429.9 |

Reconciled: owner went first; first three Water attachments are on non-ex Wailord; Sabrina switches to ex; turn-nine Water goes to ex for Shore; turn-eleven Water goes to benched non-ex; turn-thirteen fifth Water enables 110 Whale Pump. HP: ex250->140->240->150->230->KO; non-ex200->KO; Diancie170->60. Score: 0-0 until exKO,0-2 after exKO,0-3 after non-exKO. Final stats independently match 110 damage done and fourteen turns. Intermediate animated HP numbers at406s and416s are not stable board states.

No supplied turn is omitted. Hidden cards remain unknown. The legal strategy alternative is checked by Astra and the lead and does not affect outcome or coverage completion.


## Lead and Astra reconciliation

Astra accepted choosing Indeedee as a legal tempo alternative under the observed110-damage continuation: survive at20HP, optionally heal while Active, retreat free before replacing Peculiar Plaza, promote non-ex Wailord and attach fourth Water for100 damage on turn9. This leaves Mega Gardevoir110HP and exposes a damaged two-point Indeedee on Bench; it is not a guaranteed reversal of the loss. See [bounded Astra checks](../BATCH_2026-10-02_COMPETITIVE/ASTRA_TACTICAL_CHECKS.md). This reconciliation supersedes the uncertainty at first submission. Raw reports remain in worker_submission.
