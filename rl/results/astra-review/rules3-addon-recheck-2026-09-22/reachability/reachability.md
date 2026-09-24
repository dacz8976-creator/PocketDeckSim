# Rules3 static reachability for the frozen Run 4 pool

Date: 2026-09-22. Scope: static possibility only, before candidate-pair selection. No games, training, rebuilding, or engine edits. This updates the Sept. 21 exposure method against active rules3 and the current rules/05 list; it does not inherit the prior rules1/2 conclusions. Deck hashes below were re-computed and match `runs/pool5-v22-perdeck-01/identity.json`.

## Frozen input identity

| Deck | SHA-256 | Frozen list path |
|---|---|---|
| Blaziken | `69c521a33339a45633c5770b3e4acad5b8912f9367288a3044147e7fa45d5800` | `decks/dustin/06-mega-blaziken-tournament-list.txt` |
| Lucario | `46a4820bc788b4fd9ac1d9491e62bf7123c467441e7e30012e42e8a70c91e3f3` | `Boss Folder/competitive-deck-study-2026-09-08/round-robin-checkpoint/reports/research/decks/lucario.txt` |
| Weezing | `c322fe64d6052bf9c55875ecf8bebcf9460e819df19d21fc8a20a04ff7a79e9b` | `Boss Folder/competitive-deck-study-2026-09-08/round-robin-checkpoint/reports/research/decks/weezing.txt` |
| Altaria | `435a2bebc567ca8357696e400643fdc821cc36ae4765a7a16663fd4413a3bd7f` | `Boss Folder/competitive-deck-study-2026-09-08/round-robin-checkpoint/reports/research/decks/altaria.txt` |
| Suicune | `7affe6530b8d096b2d81425380bbb92c303de84458bc2fd1ee0936c40f922633` | `Boss Folder/competitive-deck-study-2026-09-08/round-robin-checkpoint/reports/research/decks/suicune.txt` |

## Add-on delayed-resolution cases

| Case from recheck request | Reachability in the pool | Evidence and scope |
|---|---|---|
| 1. Attack post-damage choice defers retaliation/KO/points | **Yes, any matchup containing Weezing.** | Team Rocket's Koffing B4a 042 has Reverse Thrust: 10 damage, then switch itself with a Benched Pokémon. The effect opens a post-damage choice. It can be used into a damaged target or retaliation source; possibility does not establish how often it happens. `deckgym-database.json` exact B4a 042 text; frozen Weezing list. |
| 2. Knockout wave contains Glimmora/Dusknoir coin to deny points | **No, all five decks.** | Neither card nor another card with that Knocked-Out point-denial coin text occurs in these frozen lists. `deckgym-database.json`; all five frozen lists. |
| 3. End turn waits on a point-denial coin or Active evolves at end of opponent's turn | **No, all five decks.** | No listed card has the point-denial coin or an end-of-opponent-turn evolution effect. (Suicune's end-turn draw/heal effects, Darkrai's Bad Dreams, and Deceptive Needle are different effects and do not match either trigger.) `deckgym-database.json`; all five frozen lists. |

**Recheck implication:** case 1 is reachable if Weezing is selected, so it needs a runtime forecast probe. Reachability alone does not establish that the current forecast is wrong or that a forced-step change fixes a demonstrated mismatch; measure that before deciding. A genuine multi-option switch is a player decision and cannot be automatically selected as a rule step. Cases 2 and 3 are absent in this pool. If the selected pair excludes Weezing, none of the three cases is statically reachable here.

## Still-open rules that the frozen pairings can reach

| Open question in `rules/05_open_questions.md` | Deck/pair reachability | Basis and qualification |
|---|---|---|
| #2: last Pokémon Knocked Out in the exchange that grants its owner a third point | **Any matchup containing Weezing.** | Weezing has Hoopa ex B4 103; Dynamite Punch deals 100 to the opponent's Active and 20 to itself. A last-Active Hoopa at 20 HP can be Knocked Out by that self-damage in the attack that KOs the opponent and awards the third point. This is a reachable constructed state, not a frequency claim. |
| #21: promotion order after both Actives are Knocked Out during Checkup | **Weezing–Blaziken only among the ten pool pairings.** | Team Rocket's Weezing ex B4a 043's Boiler Smog can Poison and Burn the opposing Active on evolution; Mega Blaziken ex B1 036 can Burn the opposing Active with Mega Burning. With both Actives Burned and sufficiently damaged, both can be Knocked Out in one Checkup. Static sequence only. |
| #22: whether Checkup on turn 30 completes and can still win | **Possible in any pairing if a game reaches turn 30.** | No pool-specific effect is required. Static possibility only; this audit does not estimate the chance a game lasts that long. |
| #24: random search uniform over cards or names | **Reachable in every deck.** | Each list has Poké Ball P-A 005 and multiple Basic Pokémon identities in the deck, so distinct candidate weighting can affect the result. |
| #26: which discard pile receives a replaced Stadium | **Lucario–Suicune only.** | Lucario includes Training Area B2 153 and Arena of Antiquity B3 154; Suicune includes Soothing Shore B4 154. Either can replace the other's Stadium. The question concerns the displaced Stadium's owner/discard destination. |

The other current open questions in `rules/05` do not match these exact lists/pairings: #4 has no Blessed Salt/Snowy Terrain or other relevant Checkup-healing ability/order case in the pool (Darkrai and Soothing Shore are end-turn effects); #9 has no hand-return effect; #11's zero-before-Weakness case is not reached by the listed attack/weakness combinations; #12's Silcoon/Cascoon prevention is absent; #19 Heavy Helmet is absent; #20's named Scizor/Golisopod/Crobat/Flutter Mane line is absent; #25 has no Ilima-like return-to-hand loop; #27 Bidoof is absent. Settled entries and engine defects are not relabeled as open rules here.

## Rules3 Energy-choice branch relevance

None of the rules3 forced Energy-payment choice mechanics applies to these lists: no Gouging Fire or Walking Wake, and all five decks use one Energy type, so a Retreat cannot present distinct typed Energy payments. Suicune's Chien-Pao ex B2a 037 discards all Water Energy (not an untyped select-N payment). Thus the new rules3 Energy-choice branches are statically absent for all ten pairings.

## Pair screening matrix

`1` = delayed case 1; `2` = open #2; `21` = open #21; `22` = turn-limit question possible; `24` = random-search question; `26` = Stadium replacement question. The matrix is reachability only.

| Pair | Reachable items |
|---|---|
| Blaziken–Lucario | 22, 24 |
| Blaziken–Weezing | 1, 2, 21, 22, 24 |
| Blaziken–Altaria | 22, 24 |
| Blaziken–Suicune | 22, 24 |
| Lucario–Weezing | 1, 2, 22, 24 |
| Lucario–Altaria | 22, 24 |
| Lucario–Suicune | 22, 24, 26 |
| Weezing–Altaria | 1, 2, 22, 24 |
| Weezing–Suicune | 1, 2, 22, 24 |
| Altaria–Suicune | 22, 24 |

## Source trail

- Run identity and exact pool paths/hashes: `Boss Folder/rl-feasibility-2026-09-18/runs/pool5-v22-perdeck-01/identity.json` and `settings.json`.
- Card names/text: `lib/card.py` and its adjacent `deckgym-database.json`; queried by the exact printing IDs listed above. Hashes checked against the current source files.
- Open-rule inventory: `rules/05_open_questions.md`, with current repair status cross-checked against `rules/09_engine_repairs_2026-09-22.md` and `Boss Folder/rules3-repairs-2026-09-22/README.md`.
- Recheck scope and three cases: `Boss Folder/rl-feasibility-2026-09-18/results/astra-review/RULES2_ADDON_RECHECK_REQUEST_20260922.md`.
- Method reference only; old conclusion rechecked against current lists and source: `Boss Folder/rl-feasibility-2026-09-18/results/astra-review/RUN4_RULES_EXPOSURE_20260921.md`.

This is not an engine test, measured rate, or claim about likely play. Deck exposure cannot prove that a state occurs in training; the chosen-pair replay and `v2_2_checks` remain necessary.

