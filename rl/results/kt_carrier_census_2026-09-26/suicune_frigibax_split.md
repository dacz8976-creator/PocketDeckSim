# kt carrier census, follow-up: which Frigibax does Suicune run?

Written Sept 26, 2026 by the census subagent. This file REPORTS; it decides nothing and changes no rule. Development-half standings only (the 63 events in `split.json`); the 63 holdout standings were never opened. Card texts below were printed by `python lib/card.py` from the repo root; nothing is from memory. Numbers: `suicune_frigibax_split.py` (beside this file, output `suicune_frigibax_split.json`), which recounts straight from the raw standings and agrees with `census.csv` and `carrier_entries.csv` on every figure.

## In plain words

- **The panel's Suicune list carries one of each printing.** `decks/screen/opponents/t-suicune.txt` (and `decks/research/suicune.txt`, the same 20 cards by id) has `1 Frigibax B2a 034` and `1 Frigibax P-B 037`. Only P-B 037 (Stiffen, the -20 cut) is a switch-1 card; B2a 034 (Chilly, plain 20 damage) is outside the set.
- **On Limitless, Stiffen is the minority build.** All 200 Suicune ex Baxcalibur development lists run exactly two Frigibax. 178 run 2x B2a 034 and no Stiffen; 16 run the 1+1 split the panel runs; 6 run 2x P-B 037. So **22 lists (11%) carry Stiffen**, **194 (97%) carry Chilly**, **16 carry both**, 0 carry neither.
- **The panel's list is one of those 16, card for card.** 13 of the 200 lists equal `t-suicune.txt` 20 of 20, and all 13 are 1+1 lists from Aug 28 to Sept 3 (PMPT #44 and three Pop Ups). Their best placing is BigDev, 14th of 378 at PMPT #44 (8-3-0).
- **Best placings among the 22 Stiffen carriers:** Danico 11th of 112 (Breakfast Club Daily #5, Sept 10, 6-3-0, 2x P-B 037); BigDev 14th of 378 (PMPT #44, Aug 29, 8-3-0, 1+1, the panel's exact list); Nj_210zz 20th of 97 (Breakfast Club Xastur's Showdown, Aug 28, 5-2-1, 2x P-B 037). No Stiffen carrier finished in a top 8; 13 of the 22 dropped. Every one of the archetype's five 1st places ran 2x B2a 034.
- **How often kp3 uses Stiffen on the table: 55 uses on 124 offered turns (44.4%) in 700 Suicune games**, kp3 on both sides, the table's first 100 deals of each of Suicune's 7 pairings. Source: the cloud branch's `rl/results/tool_turn_effect_census_2026-09-25/kp3_census.txt` (commit 3ac9bdd on `origin/claude/pensive-ptolemy-spwc0b`, not on main; read with `git show`, nothing checked out). Per Suicune game that is 0.08 uses, about one every 13 games. The trainer audit and the unpriced census do not count attack uses (details below).

## The two printings (`python lib/card.py`, verbatim)

```
== P-B 037: 1 printings, 1 distinct
Frigibax  [P-B 037]  Water  Stage 0  HP 60  weak Metal  retreat 1
  [W] Stiffen — During your opponent's next turn, this Pokémon takes -20 damage from attacks.

== B2a 034: 1 printings, 1 distinct
Frigibax  [B2a 034]  Water  Stage 0  HP 60  weak Metal  retreat 1
  [W] Chilly 20
```

Same name, HP, type, Weakness and Retreat Cost; only the attack differs. In the engine (from `cards.md`, group 3 entry): Stiffen is `CardEffect::ReducedDamage{amount:20}` on the attacker's own Active for the opponent's next turn, which is what kt switch 1 prices; Chilly is plain damage with no effect. `cards.md` lists Frigibax "In Dustin's files: none", and `census.csv` marks Suicune ex Baxcalibur `dustin=False` under both rules (no Pokémon in the archetype name appears in any `decks/dustin`, `decks/brews` or B2e file), so there is no Dustin-overlap question here as there is for Rayquaza.

## The panel's list

| file | Frigibax lines | note |
|---|---|---|
| `decks/screen/opponents/t-suicune.txt` | `1 Frigibax B2a 034`, `1 Frigibax P-B 037` | the table deck |
| `decks/research/suicune.txt` | `1 B2a 034`, `1 P-B 037` | same 20 ids |
| `decks/classifier/tournament_decks.json` "T-suicune" | `"B2a 034": 1, "P-B 037": 1` | the Sept 10 Limitless exact list the panel deck came from |

## The census numbers (Suicune ex Baxcalibur, development half)

Archetype standing: Sept 10 top-30 rank 5 (269 players); window rank 5 by development matches (1,036). 200 entries, 200 with a decklist, from 47 events; every list has 20 cards.

| count | lists | copies | note |
|---|---:|---:|---|
| carry Frigibax P-B 037 (Stiffen) | **22** | 28 | 16 lists with 1 copy, 6 with 2 |
| carry Frigibax B2a 034 (Chilly) | **194** | 372 | 178 lists with 2 copies, 16 with 1 |
| carry both printings (1+1) | **16** | | the panel's split |
| P-B 037 only (2x Stiffen) | 6 | | |
| B2a 034 only (2x Chilly) | 178 | | 89% of the archetype |
| neither | 0 | | every list runs exactly 2 Frigibax; no third printing seen |
| equal to `t-suicune.txt`, 20 of 20 | 13 | | all 13 are 1+1 lists, Aug 28 to Sept 3 |

Cards shared with the panel's list, over all 200: 20/20 in 13 lists, 19/20 in 15, 18/20 in 54, 17/20 in 75, 16/20 in 36, 15/20 in 7. The 2x-Chilly winners share 16 to 18 of 20 with the panel.

## All 22 Stiffen carriers, by placing

Placing, event size, player (Limitless handle), event, date, record, copies of each printing, whether the entry dropped, and cards shared with `t-suicune.txt`. Two entries have no placing recorded (both dropped).

| placing | of | player | event | date | record | P-B 037 | B2a 034 | drop | shares |
|---:|---:|---|---|---|---|---:|---:|---|---:|
| 11 | 112 | danico (Danico) | The Breakfast Club Daily #5 - $5 + FA | 2026-09-10 | 6-3-0 | 2 | 0 | | 15/20 |
| 14 | 378 | bigdev (BigDev) | PMPT #44 - TEAM ROCKETS AMBITION!!! ($100 USD) | 2026-08-29 | 8-3-0 | 1 | 1 | | 20/20 |
| 20 | 97 | nj_210zz | The Breakfast Club Xastur's Showdown - $5 + OAK | 2026-08-28 | 5-2-1 | 2 | 0 | | 19/20 |
| 23 | 68 | nyrq (nyrq the rookie) | TH Event's Presents: When DX Pack?! | 2026-09-23 | 3-3-1 | 2 | 0 | | 15/20 |
| 25 | 66 | koehearts | Pop Up Series 8 | 2026-08-29 | 3-2-0 | 1 | 1 | | 20/20 |
| 28 | 60 | cosmooo | Block Dragon Pop Up | 2026-09-03 | 2-2-0 | 1 | 1 | drop | 20/20 |
| 28 | 57 | joset305 | Dark League Pop Up | 2026-08-30 | 1-5-0 | 1 | 1 | | 15/20 |
| 30 | 66 | leviedelman | Pop Up Series 8 | 2026-08-29 | 2-2-0 | 1 | 1 | drop | 20/20 |
| 43 | 60 | gigagoat | Block Dragon Pop Up | 2026-09-03 | 1-3-0 | 1 | 1 | drop | 20/20 |
| 53 | 119 | diegolq | Plasma Daily #23 | 2026-09-02 | 2-4-0 | 1 | 1 | | 20/20 |
| 55 | 66 | knowticetko | Pop Up Series 8 | 2026-08-29 | 0-2-0 | 1 | 1 | drop | 20/20 |
| 57 | 378 | diegolq | PMPT #44 | 2026-08-29 | 6-3-0 | 1 | 1 | | 20/20 |
| 61 | 119 | marckedcards | Plasma Daily #23 | 2026-09-02 | 0-6-0 | 1 | 1 | | 17/20 |
| 68 | 97 | dietdrkelp | The Breakfast Club Xastur's Showdown | 2026-08-28 | 1-2-0 | 1 | 1 | drop | 20/20 |
| 107 | 378 | porkyra | PMPT #44 | 2026-08-29 | 4-3-0 | 1 | 1 | drop | 20/20 |
| 156 | 378 | tree121 | PMPT #44 | 2026-08-29 | 2-4-1 | 2 | 0 | drop | 15/20 |
| 187 | 378 | gin1234 | PMPT #44 | 2026-08-29 | 2-3-0 | 1 | 1 | drop | 20/20 |
| 189 | 378 | javiercazorla | PMPT #44 | 2026-08-29 | 2-3-0 | 1 | 1 | drop | 20/20 |
| 259 | 378 | danico | PMPT #44 | 2026-08-29 | 1-4-0 | 2 | 0 | drop | 15/20 |
| 325 | 378 | waterbetter | PMPT #44 | 2026-08-29 | 0-1-0 | 1 | 1 | drop | 20/20 |
| none | 110 | bruhs | Sauna X Almond POG Tournament #24 | 2026-09-02 | 0-3-0 | 2 | 0 | drop | 19/20 |
| none | 77 | diegolq | The Dark League Tournament POP UP | 2026-09-02 | 1-3-0 | 1 | 1 | drop | 18/20 |

Decklist URLs for every row are in `carrier_entries.csv` and `suicune_frigibax_split.json`.

For contrast, the ten best 2x-Chilly (no Stiffen) finishes: 1st of 114 (ibrakadabra, Sept 14, 9-1-1), 1st of 48 (akasatana, Sept 3, 9-0-1), 1st of 38 (giaacomoo, Sept 13), 1st of 33 (team_humble, Sept 13), 1st of 6 (tobias_oak, Sept 11), 2nd of 95 (iromm, Sept 18, 6-1-0), 2nd of 29 (shohei02, Aug 26), 3rd of 66 (nakopol91, Aug 29), 3rd of 6, 4th of 81 (tobysxe, Aug 26). A time pattern, reported and not interpreted: the 13 panel-identical 1+1 lists all sit between Aug 28 and Sept 3; after Sept 3 the only Stiffen carriers are Danico (Sept 10) and nyrq (Sept 23), both 2x P-B 037 in a different shell (15 of 20 shared with the panel).

## How often kp3 uses Stiffen on the table

**Found: 55 uses on 124 offered turns, 44.4%, over 700 Suicune games.** The line, verbatim from the cloud branch's `rl/results/tool_turn_effect_census_2026-09-25/kp3_census.txt` (commit 3ac9bdd, "Tool / turn-effect census and draft kt spec", on `origin/claude/pensive-ptolemy-spwc0b`; the folder is not on main, so it was read with `git show 3ac9bdd:<path>` and nothing was checked out or built):

```
suicune     attack Stiffen                           124            55   44.4
```

Its README says the same in words: "Frigibax's Stiffen (Suicune list; ...): offered on 124 turns, used on 55 (44%)", and "The only one is Frigibax's Stiffen in the Suicune list, used 55 times in 700 Suicune games". What the run was: kp3 on both sides, the table's deals only (seeds 72,000,000 + pairing x 10,000 + i, i < 100), all 28 pairings, 2,800 games whose move fingerprints equal kp3's own table games 2,800 of 2,800; Suicune is in 7 pairings, so 700 Suicune games; "offered" is the owner's turns on which the attack could be used, "used" the turns on which it was; census engine 1981bb4. It covers the table's first 100 deals per pairing, a fifth of the 500-deal table; the table's remaining deals have no Stiffen count. `kt_spec_review.md` (line 133) already uses this figure as the baseline for its switch-1 prediction ("Stiffen use rises from 44% of offered turns"), and `docs/REVIEW_2026-09-24_direction.md` section 8 quotes the "55 uses in 700 Suicune games".

Where it is not: `rl/results/trainer_audit_2026-09-25/` counts Trainers and Tool episodes only (`audit_trainers.tsv`, `audit_tools.tsv`; its `games.jsonl.gz` records hold `trainers` and `tool_episodes`, and none of the 1,290 records with a Suicune opponent mentions Stiffen). `rl/results/unpriced_census_2026-09-25/census_kp3.json` lists "Stiffen (Frigibax)" only as the root of branches the search could not price (hidden 9 offered / 6 chosen; boundary 17 / 7 and 303 / 76), which is not a use count. The Sept 23 table files record results and fingerprints, not attacks.

## What each reading of clause (d) gives, stated without taking a position

- Read as "a non-Dustin top-30 archetype with at least one usable decklist carrying a group 1-3 card": Suicune ex Baxcalibur qualifies. 22 of 200 lists carry P-B 037; 13 of them are the panel's own `t-suicune.txt` card for card, so a usable list already exists in `decks/screen/opponents/`; the best placing is 11th of 112 (Danico's 2x Stiffen shell) or 14th of 378 (the panel's exact list).
- Read as "the archetype's typical list carries the card": it does not. 178 of 200 lists (89%) run 2x Chilly and no Stiffen, every 1st place did, no Stiffen carrier reached a top 8, and 13 of the 22 dropped.
- Either way, the card the table would see is the one copy of P-B 037 in the panel's own Suicune list, so a switch-1 effect on Suicune shows up in the table's existing Suicune cells (the 7 pairings), where kp3 already uses Stiffen on 44% of offered turns. Section 8's sentence that the fix can be seen "through [the archetype's Limitless cells] even though the eight lists cannot" assumed the eight lists carry none of the cards; the Suicune list carries this one, and the tool census recorded that when it was run. Whether a table deck can serve as the (d) archetype, and whether an 11% carrier share counts as "carries the relevant cards", are readings for Dustin, not for this file.

## Files

- `suicune_frigibax_split.py`: the recount (development standings only, holdout never opened); `suicune_frigibax_split.json`: its output, with every carrier's URL.
- Scratch (not in the repo): `scratchpad/kt_census/git_lookup.sh`, `git_show_census.sh` (the read-only git lookups), `peek_audit_games.py` (the trainer-audit record check), `suicune_split.py`, `panel_vs_lists.py` (first drafts of the recount).
- Earlier files this rests on: `census.csv` (row Suicune ex Baxcalibur / Frigibax: 22 lists, 28 copies, 194 same-name-other-printing B2a 034), `carrier_entries.csv` (the 22 rows), `recount_diff.md` point 5, `cards.md` (Frigibax P-B 037, group 3).
