# Scratch notes for REGISTRATION_DRAFT.md (Sept 28)

Read-only counts of files already in the tree, made in WSL Python from the session scratch folder (not in the repo). No game, no build. If a number in the draft looks off, this is where it came from.

## 1. The census classes (from `trainer_audit_2026-09-25/census_table.md`, 61 rows)

| Kind | Read | Part read | Not read | Read wrongly |
|---|---:|---:|---:|---:|
| Tool (13) | 2 (Giant Cape, Leaf Cape) | 5 | 5 | 1 (Poncho) |
| Supporter (27) | 19 | 5 (Guzma, Ilima, Mars, Pokémon Center Lady, Master Plan) | 3 (Cheren, Jasmine, Boss) | 0 |
| Item (11) | 7 (incl. X Speed) | 4 (Field Blower, Flute, Repel, Goo-zooka) | 0 | 0 |
| Stadium (10) | 1 (Starting Plains) | 9 | 0 | 0 |
| Total (61) | 29 | 23 | 8 | 1 |

kt's territory among the 32 not fully read: 11 Tools, Cheren, Jasmine, Guzma, Field Blower, Repel = 16. The other 16: Boss; Ilima, Mars, Pokémon Center Lady, Master Plan; Flute, Goo-zooka; 9 Stadiums.

## 2. Play rates (from `audit_trainers.tsv`, summed over decks; played turns / offered turns)

Team Rocket's Boss 18 / 664 (2.7%): brew 02 9 / 339, Suicune 9 / 325. Goo-zooka 337 / 3,330 (10.1%): brew 03a 29 / 878, 03b 12 / 581, deck 12 243 / 673 (36%), deck 14 24 / 569, deck 15 29 / 629. X Speed 940 / 4,347 (21.6%). Peculiar Plaza 326 / 468 (69.7%): brew 05b 179 / 196 (91%), brew 10 147 / 272 (54%). Training Area 234 / 703 (33.3%): Altaria 126 / 387 (32.6%), deck 09 108 / 316 (34.2%). Arena of Antiquity 93 / 416 (22.4%). Rainbow Cave 204 / 2,397 (8.5%). Soothing Shore 474 / 1,550 (30.6%). Master Plan 269 / 1,106 (24.3%). Pokémon Center Lady 1,111 / 1,509 (73.6%). Mars 83 / 174 (47.7%). Ilima 78 / 448 (17.4%). Flute 4 / 248 (1.6%). Copycat 5,728 / 8,126 (70.5%).

Games in which the card was offered: Altaria's Training Area 182 of 240, Lucario's Arena 164 of 240.

## 3. X Speed, the 221 turns with no retreat (from `xspeed_census_2026-09-27/games.jsonl`, 2,400 games, 944 X Speed turns)

| | Turns |
|---|---:|
| X Speed turns | 944 |
| Retreat later that turn | 723 |
| No retreat | 221 |
| ...of which Copycat played the same turn | 87 (72 after X Speed, 15 before; 63 were the very next move) |
| ...of which attacked, no Copycat | 101 |
| ...neither Copycat nor attack | 33 |
| No retreat, no Copycat | 134 |
| ...in a game of deck 12 (own Hiking Trail) or against t-blaziken (its Hiking Trail) | 96 (41 vs Blaziken only, 46 deck 12 only, 9 both) |
| ...neither | 38 |

Deck 12: 143 X Speed turns, 75 with no retreat, 20 of them with Copycat. What follows X Speed on the 134 no-Copycat turns: Attach 44, Goo-zooka 35, Attack 15, Place 9, Hiking Trail 6, Evolve 5, UseStadium 4. The file records move kinds, not Stadiums, so "a Trail can be in play" is an upper bound. The census's own game-level split (deck 12: 57% with its Trail, 10% without) is in `trainer_audit_2026-09-25/census.json`, X Speed row.

## 4. The card term (`value_functions.rs:761-762`)

`(my.hand − opp.hand) + (opp.deck − my.deck)`. With 20-card decks, deck = 20 − hand − discard − in play, so the term is `2 × (my.hand − opp.hand) + (my.discard − opp.discard) + (my.in_play − opp.in_play)`. Per card: hand 2, discard or in play 1, deck 0. Checks against the census: Copycat = −1 + 2 × (opponent's hand − the bot's remaining hand); a played Item with an unseen effect = −1; playing a card before Copycat = +1 against shuffling it.

## 5. Limitless carrier counts (development half only, 63 events, 4,722 lists; the holdout half's files were never opened; the 35 archetypes of the kt census)

Lists carrying the card, of the archetype's lists (Sept 10 rank / window rank):

| Archetype | Lists | Arena of Antiquity | Training Area | Goo-zooka | Ariados (Trap Territory) | Boss | Mars | X Speed | Plaza |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Mega Lucario ex Lucario (1 / 1) | 398 | **391 (98%)** | 0 | 6 | 0 | 0 | 3 | 344 (86%) | 0 |
| Mega Altaria ex Espeon (2 / 2) | 336 | 0 | **329 (98%)** | 0 | 0 | 0 | 0 | 15 | 0 |
| Vespiquen ex Shuckle ex (4 / 4) | 233 | 0 | 0 | 0 | 0 | 0 | 12 | 232 (100%) | 0 |
| Suicune ex Baxcalibur (5 / 5) | 200 | 0 | 0 | 0 | 0 | 72 (36%) | 62 (31%) | 0 | 0 |
| Team Rocket's Weezing ex Hoopa ex (6 / 7) | 152 | 0 | 0 | 1 | 0 | 0 | 13 | 142 (93%) | 0 |
| Mega Manectric ex Heliolisk (11 / 12) | 111 | 0 | 87 (78%) | 0 | 0 | 4 | 0 | 0 | 0 |
| Team Rocket's Raticate ex Alolan Ninetales ex (10 / 22) | 55 | 0 | 23 (42%) | 11 (20%) | 0 | 0 | 0 | 4 | 0 |
| Whimsicott ex Ariados (26 / 44) | 21 | 0 | 0 | **21 (100%)** | **21 (100%)** | 0 | 0 | 13 | 0 |
| Mega Altaria ex Greninja (16 / 10) | 125 | 0 | 12 (10%) | 0 | 0 | 0 | 9 | 1 | 0 |

Training Area also: Mega Altaria ex 43 of 44, Mega Altaria ex Chingling 38 of 38, Mega Altaria ex Igglybuff 21 of 25, Milotic ex Eevee ex 44 of 51, Mega Sharpedo ex Gyarados 29 of 35, Mega Manectric ex Team Rocket's Electrode 10 of 22. Peculiar Plaza, Future Booster Energy Capsule and Beastite: 0 lists in all 35 archetypes. Hoopa ex Mega Absol ex: Goo-zooka 5 of 128, Mars 52 of 128, X Speed 87 of 128.

## 6. Which decks carry which cards (my scan of `decks/` files by card id)

- Arena of Antiquity: `research/lucario`, `v-lucario_2`. Training Area: `research/altaria`, `g-mega_scizor_revavroom`, `h-manectric`, `h-raticate`, Dustin 09.
- Goo-zooka: `h-whimsicott` (2), Dustin 12 (2), 14, 15, brews 03a (2), 03b. Trap Territory (Ariados): Dustin 12, `h-whimsicott`. Peculiar Plaza: brews 05b, 10.
- X Speed: `research/lucario`, `vespiquen` (2), `weezing`, `v-lucario_2`, `v-weezing_2`, `h-hoopa_absol`, Dustin 04 and 12, brews 02, 03a, 04, 05, 07. Boss: `research/suicune`, brew 02. Master Plan: brews 05, 05b (2 each). Ilima: Dustin 01, 02, 13, 15. Flute: Dustin 08, 14. Rainbow Cave: `g-dragonair_mega_rayquaza` (2), `h-charizardy_entei`, `h-garchomp`, `l-charizardy` (2), Dustin 08, 11 (2), brew 08 (2).
- Hiking Trail: `research/blaziken`, `g-mega_altaria_greninja`, Dustin 06, 10 (2), 12.
- None of the 10 lists of the 45 cells carries Goo-zooka, Peculiar Plaza or Trap Territory.

## 7. Panel stages, for the Training Area prediction (from `card.py` and the lists)

Stage 1 attackers among the panel: Mega Lucario ex, Lucario, Vespiquen ex, Team Rocket's Weezing ex, Mega Altaria ex, Espeon. Stage 2 or Basic: Mega Blaziken ex, Hydreigon, Mega Sceptile ex, Baxcalibur (Stage 2); Suicune ex, Chien-Pao ex, Hoopa ex, Mega Absol ex, Mega Rayquaza ex (Basic).
