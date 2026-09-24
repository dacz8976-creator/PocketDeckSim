# Static reachability for the frozen Run 4 pool, rules4 recheck

Date: 2026-09-22. Scope: static possibility for the exact five-deck Run 4 pool, with the narrow T2 result incorporated. This is a current-source recheck of the frozen rules3 reachability audit, not a new experiment. No games, training, builds, or engine edits were performed for this report. Rules4 is now active and passed the 1,826-test engine suite, including the narrow T2 regression in both seats. Its identified release is linked below.

## Frozen input identity

The current deck files were SHA-256 checked against `Boss Folder/rl-feasibility-2026-09-18/runs/pool5-v22-perdeck-01/identity.json`; all five still match. Paths and identities:

| Deck | SHA-256 | Frozen list path |
|---|---|---|
| Blaziken | `69c521a33339a45633c5770b3e4acad5b8912f9367288a3044147e7fa45d5800` | `decks/dustin/06-mega-blaziken-tournament-list.txt` |
| Lucario | `46a4820bc788b4fd9ac1d9491e62bf7123c467441e7e30012e42e8a70c91e3f3` | `Boss Folder/competitive-deck-study-2026-09-08/round-robin-checkpoint/reports/research/decks/lucario.txt` |
| Weezing | `c322fe64d6052bf9c55875ecf8bebcf9460e819df19d21fc8a20a04ff7a79e9b` | `Boss Folder/competitive-deck-study-2026-09-08/round-robin-checkpoint/reports/research/decks/weezing.txt` |
| Altaria | `435a2bebc567ca8357696e400643fdc821cc36ae4765a7a16663fd4413a3bd7f` | `Boss Folder/competitive-deck-study-2026-09-08/round-robin-checkpoint/reports/research/decks/altaria.txt` |
| Suicune | `7affe6530b8d096b2d81425380bbb92c303de84458bc2fd1ee0936c40f922633` | `Boss Folder/competitive-deck-study-2026-09-08/round-robin-checkpoint/reports/research/decks/suicune.txt` |

## Delayed-resolution exposure

| Case | Pool reachability | Evidence and boundary |
|---|---|---|
| 1. Post-damage player choice defers retaliation, Knock Out, and points | Yes, any pairing with Weezing, including Weezing–Lucario. | Weezing list includes Team Rocket's Koffing B4a 042. Local `lib/card.py` resolves its Reverse Thrust as 10 damage followed by a switch with a Benched Pokémon. This is a genuine player-selected follow-up, not an automatic forced rule step. A possible damaging target/retaliation state establishes reachability, not frequency or a demonstrated forecast mismatch. Runtime forecast diagnosis is separate. |
| 2. Knockout wave includes a Glimmora/Dusknoir coin that denies points | No, none of the five lists. | Current exact lists contain neither named printing nor a matching point-denial coin effect. Card text checked against the local card data. |
| 3. End turn waits on point-denial coin or Active evolves at opponent-turn end | No, none of the five lists. | No listed card has either trigger. This does not mean there are no end-turn abilities: Darkrai and Soothing Shore are present in the pool but are different effects. |

## T2 and terminal reachability

T2 supplies one observed video configuration: Dustin starts with 2 points and a lone Active at 10 HP; after the attack and Destiny Burst, Dustin has 3 points and no Pokémon, while the opponent still has two Benched Pokémon, and the result overlay reads Tie. The opponent's final 2 points are inferred from the Knocked-Out ex, not read after the overlay. The T2 engine regression was also run in both seats; that is regression coverage, not a second observed video configuration. T2 settles only the observed finish. It does not verify a general win-condition counting model for both-empty boards or both players at three or more points; those broader outcomes remain untested here.

The frozen rules3 deck audit identifies a reachable construction in Weezing: Hoopa ex B4 103's Dynamite Punch does 100 damage to the opponent's Active and 20 damage to itself. With Hoopa at 20 HP and as its owner's last Pokémon, it can Knock Out an opposing Active worth enough points to bring Hoopa's owner to 3 while Hoopa is Knocked Out by its self-damage; the opponent must remain below 3 and retain at least one Benched Pokémon. This mirrors the observed one-empty-board T2 shape without asserting both boards are empty or establishing frequency. For Weezing–Lucario, only the video-observed configuration is settled; rules4 implements the narrow cross-condition tie and passed its mirrored regression tests. This does not settle the broader simultaneous-finish combinations.

## Still-open rule exposure

| Question | Reachability in exact pool | Basis and qualification |
|---|---|---|
| #21: who promotes first after both Actives are Knocked Out during Checkup | Weezing–Blaziken only | Team Rocket's Weezing ex B4a 043 can Poison and Burn on evolution; Mega Blaziken ex B1 036 can Burn. Both Actives could be damaged and Burned for a double Knock Out. This is a constructed possibility. |
| #22: turn-30 Checkup completes and can still win | Possible for any pair if a game reaches turn 30 | No pair-specific card is needed. The question remains open for Weezing–Lucario; this static check does not estimate the chance a game lasts that long. |
| #24: random search weighting over cards or names | Reachable in every list | Each frozen list includes Poké Ball P-A 005 and multiple Basic Pokémon identities. The question remains open for Weezing–Lucario. |
| #26: destination of a displaced Stadium | Lucario–Suicune only | Lucario contains Training Area B2 153 and Arena of Antiquity B3 154; Suicune contains Soothing Shore B4 154. Not reachable in Weezing–Lucario. |

Other current open questions remain as classified in the frozen rules3 report: #4 has no Blessed Salt/Snowy Terrain or relevant Checkup-healing-order case in this pool; Darkrai and Soothing Shore are distinct end-turn effects. #9/#25 return-to-hand cases, #12 Silcoon/Cascoon prevention, #19 Heavy Helmet, #20 the named evolution line, and #27 Bidoof are absent. #11's zero-before-Weakness case is not reached by listed attack/weakness combinations. Settled entries and engine defects are not described as open gameplay rules.

## Energy-choice branches and pair matrix

None of the rules3 forced typed Energy-payment choices is present: no Gouging Fire or Walking Wake appears, and each list declares one Energy type. Suicune's Chien-Pao ex B2a 037 discards all Water Energy, not a select-N payment. These branches are statically absent across the ten pairings.

Matrix marks: `1` = delayed case 1; `T2` = reachable last-Hoopa terminal construction, with only the listed T2 configuration observed; `21`, `22`, `24`, `26` = questions above. This is possibility only.

| Pair | Reachable items |
|---|---|
| Blaziken–Lucario | 22, 24 |
| Blaziken–Weezing | 1, T2, 21, 22, 24 |
| Blaziken–Altaria | 22, 24 |
| Blaziken–Suicune | 22, 24 |
| Lucario–Weezing | 1, T2, 22, 24 |
| Lucario–Altaria | 22, 24 |
| Lucario–Suicune | 22, 24, 26 |
| Weezing–Altaria | 1, T2, 22, 24 |
| Weezing–Suicune | 1, T2, 22, 24 |
| Altaria–Suicune | 22, 24 |

## Source trail and status

- Frozen pool paths, hashes, and settings: `Boss Folder/rl-feasibility-2026-09-18/runs/pool5-v22-perdeck-01/identity.json` and `settings.json`; all five deck hashes rechecked for this report.
- Card printing text: local `lib/card.py` and adjacent `deckgym-database.json`; exact IDs are cited in the tables above and match the frozen lists.
- T2 video boundary and scoring inference: `Boss Folder/rules4-t2-repair-2026-09-22/T2-evidence.md` (video observes one seat configuration; final opponent points are inferred from the ex Knock Out). The same note records separate two-seat engine regression coverage, not video evidence.
- Method and frozen pair classifications: `Boss Folder/rl-feasibility-2026-09-18/results/astra-review/rules3-addon-recheck-2026-09-22/reachability/reachability.md`. That rules3 report remains unchanged.
- Current rules4 release identity: `Boss Folder/rules4-t2-repair-2026-09-22/release-identity.json`; executable SHA-256 `e6593ed816d0d5dbaf24fc8bc81a8317ed8069cda6ae7162c3d53e1fa7a12415`. The prior rules3 identity and report remain historical evidence.

No claim is made about event frequency, forecast correctness, or game strength. Reachability alone cannot establish that a forecast change is needed. The selected Weezing–Lucario pair also leaves #22 and #24 open; both require separate probes.

