# Skeptic pass: c-mega_altaria_ex_igglybuff.txt (Limitless archetype "Mega Altaria ex Igglybuff")

Date: 2026-09-26. Files under review: `decks/c-mega_altaria_ex_igglybuff.txt`, `provenance/c-mega_altaria_ex_igglybuff.json`, `card_check_c-mega_altaria_ex_igglybuff.md`, `cells_c-mega_altaria_ex_igglybuff.{py,md,csv,json}`, `coverage_c-mega_altaria_ex_igglybuff.json`, all in this folder. This file reports; it decides nothing and changes no rule.

How the pass was run: a fresh script written from the data description, not from the other agent's code (scratch `kt_census/skeptic_altaria_igglybuff.py`, output `skeptic_altaria_igglybuff.out.json`). It opened the 63 development-half standings files in `rl/results/limitless_skill_model_2026-09-25/raw/` (split.json), listed the 63 holdout ids and never opened a holdout standings or details file, took event names, sizes and dates from `events.json`, and read `matches.csv` rows from both halves only for the pooled cells (B2e README section 3). Card text came from `python lib/card.py "<SET> <NUMBER>"` from the repo root and the raw `lib/deckgym-database.json` entries; Limitless text came from `https://pocket.limitlesstcg.com/cards/<SET>/<NUMBER>` fetched on Sept 26 (WebFetch was rate-limited, so the pages were fetched with PowerShell `Invoke-WebRequest` and the HTML stripped to text; copies in scratch `kt_census/limitless_*.html`). No engine games were run; the goldfish coverage run was not repeated. The pass was interrupted by a usage limit and resumed later on Sept 26; on resumption the script was re-run from the repo root and printed the same 25-entry ranking, the same six carriers, "file vs source identical: True", and "cell diffs vs agent: []", and `python lib/card.py` and `python lib/deck_check.py` were run again with the same results, so every figure below was seen twice.

## Verdict in one line

The list, its provenance, its card check and its cells all reproduce. One small provenance gap: the third "ineligible better placing" (leonemesis, 9th of 24) has "(24 players)" where the event name belongs; `events.json` names it "🇧🇷 Hit Pocket #3 | TCG Pocket" (2026-08-29). Nothing else needs to change.

## (a) Is the chosen list the best-placing carrier entry in the development half?

Yes. The development half holds 25 standings entries with deck_name exactly "Mega Altaria ex Igglybuff", all 25 with a decklist, all 20 cards, one deck id (`mega-altaria-ex-b1-igglybuff-a4a`), in 20 events from 2026-08-26 to 2026-09-21. Six carry a census card, and the only census card any of them carries is 1 Protective Poncho B2 147; none carries a switch-1 card (groups 1 to 3 in `cards.json`). No entry has a same-name-other-printing line for any census card. This matches the provenance's "25 entries / 6 carriers / Poncho only" exactly, and the six carrier rows in `carrier_entries.csv` are the same six entries in the same order as my ranking.

All 25 entries, ranked by placing (unplaced last), then event size:

| Placing | Player | Event id | Size | Date | Record | Carries |
|---:|---|---|---:|---|---|---|
| 5 | carlos_781 | 6a9dc423ab080c8c957fc250 | 118 | 2026-09-07 | 8-2-0 | no |
| 6 | yunlong | 6a78c5912b308b6067b4f421 | 116 | 2026-09-05 | 8-2-1 | no |
| 9 | leonemesis | 6a88ce398302ae761e5f8954 | 24 | 2026-08-29 | 3-2-0 | no |
| **10** | **khaeruibnum** | **6a9e12feab080c8c957fc84e** | **73** | **2026-09-11** | **5-2-0** | **Poncho x1 (the chosen list)** |
| 18 | mrd | 6a9b4f52ab080c8c957fa3d7 | 97 | 2026-09-06 | 5-3-0 | no |
| 27 | mrd | 6a789b5ccdc0391d7fa61ba9 | 120 | 2026-09-05 | 4-3-1 | no |
| 29 | oscarparra | 6a9718fd629039f77d8a790e | 119 | 2026-09-02 | 4-3-0 | no |
| 34 | oscarparra | 6a918b3d629039f77d8a40ca | 66 | 2026-08-29 | 2-3-0 | no |
| 34 | khaeruibnum | 6aa1e900a4272c53be64c5ce | 64 | 2026-09-10 | 1-6-0 | Poncho x1 |
| 38 | pikatravai | 6a9829c8a4272c53be644d74 | 132 | 2026-09-07 | 4-3-0 | no |
| 42 | mrd | 6a9dc423ab080c8c957fc250 | 118 | 2026-09-07 | 4-3-0 | no |
| 43 | santyu | 6a94b2ffabb9482237504367 | 110 | 2026-09-02 | 3-3-0 | no |
| 61 | fluffy_panda1995 | 6aa22425a4272c53be64ca36 | 112 | 2026-09-10 | 2-3-0 | no |
| 63 | pamnardo_s2 | 6a8b75058302ae761e5fab7e | 81 | 2026-08-26 | 1-3-0 (drop after round 4) | Poncho x1 |
| 67 | pamnardo_s2 | 6a8f27e57a62de813013fb20 | 69 | 2026-08-26 | 0-3-0 (drop after round 3) | Poncho x1 |
| 80 | rcollinz | 6aa89ad438886b36383c071a | 80 | 2026-09-16 | 0-1-0 | no |
| 210 | mrd | 6a8c5eb881741245b151d7e3 | 378 | 2026-08-29 | 2-5-0 | no |
| 225 | oscarparra | 6a8c5eb881741245b151d7e3 | 378 | 2026-08-29 | 1-2-0 | no |
| unplaced | khaeruibnum | 6a7e2b83cdc0391d7fa65afb | 219 | 2026-09-11 | 1-3-0 (drop after round 4) | Poncho x1 |
| unplaced | tmcoy97 | 6a9f6899a4272c53be64a894 | 172 | 2026-09-08 | 0-2-0 | no |
| unplaced | pikatravai | 6a9f6899a4272c53be64a894 | 172 | 2026-09-08 | 2-3-0 | no |
| unplaced | carlos_781 | 6a9829c8a4272c53be644d74 | 132 | 2026-09-07 | 0-2-0 | no |
| unplaced | mrd | 6aa1e900a4272c53be64c5ce | 64 | 2026-09-10 | 1-3-0 | no |
| unplaced | khaeruibnum | 6aabc067f1243e65f98035ec | 53 | 2026-09-21 | 1-1-0 (drop after round 2) | Poncho x1 |
| unplaced | pikatravai | 6aa13feaa4272c53be64b94a | 49 | 2026-09-09 | 2-3-0 | no |

The three entries placed above 10th (carlos_781 5th, yunlong 6th, leonemesis 9th) all have decklists and carry no census card by id or by name, so they are ineligible under the B2e rule, exactly as the provenance says. No other carrier shares the 10th placing, so the event-size tiebreaker was not needed. The provenance's descriptions of the other five carriers check out card for card: the Kelp Classic list is the chosen list with 1 Mars A2 155 in place of Team Rocket's Thieving Machine B4a 067; pamnardo_s2's two entries are the same 20 cards as each other and differ from the chosen list by -1 Mega Altaria ex, -2 Leaf, -1 Copycat, -1 Thieving Machine, +1 Eevee B1 184, +1 Espeon B3a 020, +1 Lisia B1 226, +1 Training Area B2 153, +1 X Speed P-A 002; khaeruibnum's two unplaced entries are the same 20 cards as the chosen list. carlos_781's 5th-place list swaps 2 Leaf, 1 Thieving Machine and 1 Poncho for 1 Lisia, 1 Training Area and 2 X Speed; yunlong's 6th-place list has no Poncho and runs Lisia, Training Area, Mars, Field Blower, Repel and Small Balloon (so "X Speed or Repel/Small Balloon" in the provenance reads right: X Speed is carlos_781's, Repel/Small Balloon yunlong's).

Event facts for the chosen entry, from `events.json` and `matches.csv`: "♨️Sauna X Ev4de POG Tournament #27|10 USD+Top 4 FA", id 6a9e12feab080c8c957fc84e, 73 players, 73 standings rows, start 2026-09-11T03:10Z, split development; rounds 1 to 6 Swiss BO1 then round 7 a single-elimination bracket BO3 (39, 36, 34, 30, 24, 20 and 15 match rows), which is what the provenance says. The "10th of 73, 5-2-0, country ID, no drop" fields all match the standings entry.

## (b) Does the file match the source decklist card for card and printing for printing?

Yes, exactly. The standings entry for player `khaeruibnum` in the development file `raw/6a9e12feab080c8c957fc84e_standings.json.gz` lists: pokemon 2 Swablu B1 196, 2 Mega Altaria ex B1 102, 2 Darkrai B2b 40, 2 Igglybuff A4a 59; trainer 2 Professor's Research P-A 7, 2 Leaf A1a 68, 2 Copycat B1 225, 1 Cyrus A2 150, 1 Sabrina A1 225, 2 Poké Ball P-A 5, 1 Team Rocket's Thieving Machine B4a 67, 1 Protective Poncho B2 147; energy ["Psychic"]. The file has the same 12 name/set/number lines with the same counts (numbers zero-padded to three digits), 20 cards, and "Energy: Psychic". Multiset comparison: zero differences. `python lib/card.py` reports each of the 12 ids as "1 printings, 1 distinct", so no printing choice arose. `python lib/deck_check.py files <file>` printed "decks clean", exit 0. The file is 279 bytes, UTF-8 without BOM, LF only, ends with a newline, 13 lines.

## (c) Re-derived card-text comparisons and one Limitless cell

Card text, engine (`python lib/card.py`, raw database entry) against Limitless (fetched Sept 26):

- Darkrai (B2b 040): engine Darkness, Basic (stage 0), HP 100, weakness Grass, retreat 2, Ability "Bad Dreams: At the end of each turn, if your opponent's Active Pokémon is Asleep, do 20 damage to that Pokémon.", attack [CCC] Dark Slumber 40 "Your opponent's Active Pokémon is now Asleep." Limitless: Darkness, 100 HP, Basic, Ability Bad Dreams with the identical sentence, CCC Dark Slumber 40 with the identical sentence, Weakness Grass, Retreat 2. Match, as the card check reports.
- Protective Poncho (B2 147): engine Trainer, `trainer_card_type` "Tool", text "As long as the Pokémon this card is attached to is on your Bench, prevent all damage done to that Pokémon by your opponent's attacks and Abilities." Limitless: "Trainer - Tool", identical text. Match, as the card check reports.
- A third, since it is the deck's attacker: Mega Altaria ex (B1 102): engine Psychic, Stage 1 from Swablu, HP 190, weakness Metal, retreat 1, [PP] Mega Harmony 40 "This attack does 30 more damage for each of your Benched Pokémon.", no ability. Limitless: Psychic, 190 HP, Stage 1, Evolves from Swablu, PP Mega Harmony 40+ with the identical sentence, Weakness Metal, Retreat 1, plus the Mega Evolution ex rule box (3 points when Knocked Out). Match; "40+" against 40 is notation, and the rule box has no database field, both as the card check notes.

One Limitless cell, re-derived from `matches.csv` with the scoreboard's rules (held side by exact deck_name, panel side by archetype label, decisive = win or loss by the winner column, tie = half a point counted in n, double loss excluded and shown as DL, byes never pair, mirrors skipped, every record one unit): Mega Altaria ex Igglybuff against lucario (Mega Lucario ex Lucario), development half 7-5-0 with 2 DL, n = 12, 58.3% +/- 27.9; pooled 16-11-1 with 3 DL, n = 28, 58.9% +/- 18.2. Both agree with `cells_c-mega_altaria_ex_igglybuff.md`. As a by-product the script computed all eight cells, the equal-weight averages (development 45.1 +/- 11.2, pooled 51.9 +/- 11.7), the match-weighted rows (24-19-0 DL 3, n 43, 55.8%; 48-42-4 DL 5, n 94, 53.2%) and the record totals (135 development records: 120 scored, 7 DL, 8 bye; 271 pooled: 240 scored, 18 DL, 13 bye): zero differences against the agent's JSON. The winner column behaves as the rules assume (ties carry winner 0, double losses -1; 866 ties and 1,063 double losses in the 30,216 rows; no mirror rows exist for this deck_name). The 120 scored development records are also the "120 dev matches, window rank 34" figure in the provenance.

## (d) Does the list carry the census cards it claims?

Yes. Checking all 12 ids and all 12 names in the file against `cards.json` (50 entries, 82 ids): the only hit is Protective Poncho B2 147, 1 copy, kind "other", not a switch-1 kind. No file line matches a census card by name under another printing. `cards.json` holds Poncho under `group4_considered / tools_and_trainers` with the decision "listed under kt switch 2 at a price of 0; NOT a switch-1 relevant card", and `cards.md` section "Protective Poncho [B2 147, B2 234] (Tool)" says the same, so the provenance's "group 4: kt switch 2, priced at 0; NOT a switch-1 card" and `carries_switch1_card: false` are right. (`cards.md` also notes Poncho sits in two of Dustin's files, 05-indeedee-stoutland and brew-06b; that is about the card, not the archetype, and does not bear on the Dustin test below.)

## Other claims checked

- Not Dustin's: grepping `decks/dustin/*.txt` (15 files) and `decks/brews/*.txt` (13 files) for Altaria, Swablu, Igglybuff and Darkrai finds only "1 Darkrai ex A2 110" in 04-absol-hoopa-darkrai and brew-07-hoopa-darkrai-sableye, a different card from the list's Darkrai B2b 040 and not part of the archetype name. Neither Mega Altaria ex nor Igglybuff is in any of his files or in a B2e archetype name. Not Dustin's at any level of the census's rule.
- Sept-10 top 30: "Mega Altaria ex Igglybuff" is the 29th entry of `decks/classifier/limitless_2026-09-10.json` with 34 players, as stated.
- Coverage: the goldfish hash quoted in the card check (318c82c8...be997) is the one `rl/engine-2026-09-25/README.md` lists for `goldfish`. The coverage JSON's two "its effect" flags (Copycat, Thieving Machine) and ten clean cards are reported as the tool gave them; the run itself was not repeated here.

## What should change

1. `provenance/c-mega_altaria_ex_igglybuff.json`, `ineligible_better_placings[2]` (leonemesis): the "event" field reads "(24 players)". The event is "🇧🇷 Hit Pocket #3 | TCG Pocket", id 6a88ce398302ae761e5f8954, 24 players, 2026-08-29, 9th place, 3-2-0, `https://play.limitlesstcg.com/tournament/6a88ce398302ae761e5f8954/player/leonemesis/decklist`. A one-field fix; it does not touch the chosen list, the ranking, or any number.

Nothing else. The chosen list is the best-placing development-half carrier, the file is the source list exactly, the card texts and the cell reproduce, and the census-card claim is right.
