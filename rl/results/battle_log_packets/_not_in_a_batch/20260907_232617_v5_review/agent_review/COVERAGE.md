# Full-battle coverage

Source spans **00:00.000-07:21.538**, from opponent introduction to literal Defeat. All **11 numbered turns**, setup and terminal outcome were reviewed. This is a full action-level reconstruction using overview plus dense event-boundary samples, not a claim to have inspected every encoded frame. Hidden state is not reconstructed.

Retained evidence: **381** full-resolution source JPEGs in `frames/`, with elapsed-second filenames; contact sheets have on-image minute/second labels. Example: `frames/433.400.jpg` is 07:13.400. The first frame at or after each requested timestamp was decoded. Boundaries below are approximate.

| Segment | Interval | Verified coverage |
|---|---|---|
| Setup | 00:00-00:40 | Named opponent Ddiioocc, player going second at 00:10; Eevee Active; opposing Falinks Active, Hitmonchan ex and second Falinks Benched. No Energy attached. |
| T1 opponent | 00:40-00:48 | Professor's Research at 00:42; draws; no Energy attachment or attack. |
| T2 player | 00:48-01:40 | Sabrina draw; Lisia obtains two Team Rocket's Rattata; both Benched; one Lightning attached to Eevee at 01:33-01:34; Stampede at 01:37, actual 0 damage at 01:38. |
| T3 opponent | 01:40-02:15 | Fighting to Active Falinks; Poke Ball at 01:48.100-01:48.700; Riolu Benched; Arena of Antiquity; Invade 60 KOs Eevee; opponent point 1; Rattata promoted. |
| T4 player | 02:15-02:43 | Pokemon Center Lady draw; Research draws Jolteon ex and Oricorio; Oricorio Benched; Lightning to Active Rattata; Ambush Tails at 02:38, actual 0 damage. |
| T5 opponent | 02:43-03:31 | Fighting to Benched Riolu; Sabrina forces Rattata out and Oricorio in; Invade 60 leaves Oricorio at 10 HP. |
| T6 player | 03:31-03:57 | Copycat draw, not play; Research draws Eevee and second Jolteon ex; Eevee Benched, Lightning attached; Team Rocket's Goo-zooka played; no attack. |
| T7 opponent | 03:57-04:21 | Second Fighting to Riolu; Invade 60 KOs Oricorio; opponent point 2; Eevee promoted. |
| T8 player | 04:21-05:18 | Raticate ex draw/evolution; Thieving Incisors moves sole Fighting from Active Falinks to Raticate; Eevee evolves to Jolteon; Copycat, Poke Ball explicit no-target result; second Lightning to Jolteon; Mach Bolt 60 leaves Falinks at 10. |
| T9 opponent | 05:18-05:56 | Riolu evolves to Mega Lucario ex 190; third Fighting attached; Electromagnetic Wall 20 leaves 170; Giovanni played; no attack/retreat observed. |
| T10 player | 05:56-06:48 | Jolteon ex draw; unused-Energy warning then Lightning attached to Rattata; Mach Bolt 60 KOs Falinks; player point 1; Mega Lucario promoted with 3 Fighting. |
| T11 opponent | 06:48-07:20 | Fourth Fighting to Mega Lucario; Electromagnetic Wall 20 leaves 150; Research; Fighting Pulse 180 KOs Jolteon ex; +2 points animation, final displayed markers 1-3. |
| Terminal | 07:20-07:21.538 | Literal Defeat at 07:21.000/07:21.300. Recording ends on banner, not a statistical results page. |

## Coverage checks

- Every attack declaration and resulting HP state reviewed. Damage numbers separately verified, including subsecond 60 at 05:15.400 and 180 at 07:13.400.
- Energy generation/preview kept separate from successful attachment; actual attached icons and before/after transfer states checked.
- Raticate's effect is an Energy transfer, not generation; the Fighting type is retained.
- Coin result for the one observed Ambush is explicitly Tails. Other reviewed attacks do not show attack coin flips.
- No retreat with an Energy payment observed. Sabrina causes a forced switch on T5; the later switches are KO promotions.
- Manual interaction is visible. No Auto toggle appears; exact matchmaking category and AI status are not independently asserted.
- No turns left unreviewed. Remaining limits are recorded in `UNCERTAINTIES.json`.
