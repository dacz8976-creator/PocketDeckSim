# Deck classifier — first run, 2026-09-10

Inputs: 15 QR-decoded decks (my_decks.json) + 8 Limitless tournament exact lists (tournament_decks.json).
Card text: deckgym-database.json (3,879 printings). Engine coverage: the effect->mechanic maps in deckgym-fork-s193/src/actions.
Rough by design; classifies and suggests, does not predict win rates.

Run: python3 deck_classifier.py deckgym-database.json deckgym-fork-s193/src my_decks.json tournament_decks.json "query=B4a 043"
New QR codes: python3 decode_qr.py screenshot.png  (needs s216_card_catalog_v1.json path inside the script)

```
# cards loaded 3879 · engine-mapped effect texts 716 · decks 23

## 01 Muk-Glimmora-Kingambit-Regigigas  [Darkness]  → DENIAL/CONTROL + TOOLBOX
   9 Pokémon / 11 Trainers · basics 5 · stage-2 1 · candy 1 · ex 0 · best hit 100 (Regigigas) · best dmg/energy 33.3
   families: DRAW_SEARCH×7, COIN_GAMBLE×4, STATUS_INFLICT×2, POINT×2, ABILITY_LOCK×1, DMG_SCALE×1
   denial 5 · durability 2 · snipe 0 · setup 9
   risks: 1-of evolution piece
   + STATUS_INFLICT→STATUS_AMP (amplifies or cashes in the condition): Team Rocket's Muk B4a 041, Mareanie B3b 046, Darkrai B2b 040, Toxapex B1 162, Paldean Clodsire ex A4b 238
   + STATUS_INFLICT→RETREAT_LOCK (keeps the afflicted Pokémon in the Active Spot): Team Rocket's Goo-zooka B4a 068
   + STATUS_INFLICT→GUST (drags the target you want afflicted into the Active Spot): Swellow B4a 104, Roaring Moon B3a 047, Umbreon ex B2 231, Cyrus A4b 326, Sabrina A4b 338
   + POINT→DMG_REDUCE (point tricks want long games): Team Rocket's Kecleon B4a 062, Furfrou B4a 064, Unfezant B4 139, Clear Veil B4 149, Wigglytuff B3b 052

## 02 Arceus-Crobat  [Darkness]  → MIDRANGE
   8 Pokémon / 12 Trainers · basics 6 · stage-2 2 · candy 2 · ex 2 · best hit 70 (Arceus ex) · best dmg/energy 50.0
   families: DRAW_SEARCH×7, DMG_SCALE×2, STATUS_IMMUNE×2, STATUS_INFLICT×2, EVO_ACCEL×2, BENCH_DMG×1
   denial 2 · durability 2 · snipe 1 · setup 9
   + DMG_SCALE→RETREAT_LOCK (if it scales with retreat cost): Team Rocket's Goo-zooka B4a 068
   + DMG_SCALE→ENERGY_ACCEL (if it scales with energy): Team Rocket's Raticate ex B4a 059, Delcatty B4 135, Psychic B4 150, Wally B4 153, Sableye B3a 040
   + STATUS_INFLICT→STATUS_AMP (amplifies or cashes in the condition): Team Rocket's Muk B4a 041, Mareanie B3b 046, Darkrai B2b 040, Toxapex B1 162, Paldean Clodsire ex A4b 238
   + STATUS_INFLICT→RETREAT_LOCK (keeps the afflicted Pokémon in the Active Spot): Team Rocket's Goo-zooka B4a 068

## 03 Wailord-Indeedee wall  [Water]  → WALL + SCALING-HITTER
   6 Pokémon / 14 Trainers · basics 4 · stage-2 0 · candy 0 · ex 3 · best hit 100 (Wailord ex) · best dmg/energy 25.0
   families: HEAL×7, DRAW_SEARCH×5, DMG_SCALE×3, STATUS_IMMUNE×2, COIN_GAMBLE×2, DMG_REDUCE×2
   denial 1 · durability 11 · snipe 1 · setup 5
   risks: typed costs outside declared energy: P; 1-of evolution piece
   + DMG_SCALE→RETREAT_LOCK (if it scales with retreat cost): Team Rocket's Goo-zooka B4a 068
   + DMG_SCALE→ENERGY_ACCEL (if it scales with energy): Team Rocket's Raticate ex B4a 059, Mega Sharpedo ex B4 035, Delcatty B4 135, Psychic B4 150, Wally B4 153
   + STATUS_IMMUNE→STATUS_INFLICT (lets you run status pressure without eating the mirror): Team Rocket's Master Plan B4a 070, Psyduck B4 030, Milotic ex B3b 015, Piplup B3b 019, Iron Bundle ex B3a 013
   + DMG_REDUCE→STATUS_INFLICT (stall while the condition ticks): Team Rocket's Master Plan B4a 070, Psyduck B4 030, Milotic ex B3b 015, Piplup B3b 019, Iron Bundle ex B3a 013

## 04 Absol-Hoopa-Darkrai  [Darkness]  → SNIPE
   7 Pokémon / 13 Trainers · basics 7 · stage-2 0 · candy 0 · ex 3 · best hit 100 (Hoopa ex) · best dmg/energy 33.3
   families: DRAW_SEARCH×6, TOOL_SUPPORT×2, BIG_HIT×2, BENCH_DMG×2, SELF_DMG×2, GUST×2
   denial 2 · durability 0 · snipe 4 · setup 7

## 05 Indeedee-Stoutland  [Psychic]  → WALL
   6 Pokémon / 14 Trainers · basics 4 · stage-2 2 · candy 2 · ex 2 · best hit 70 (Stoutland) · best dmg/energy 35.0
   families: DRAW_SEARCH×6, HEAL×3, DMG_SCALE×2, EVO_ACCEL×2, DMG_REDUCE×2, TOOL_SUPPORT×1
   denial 1 · durability 5 · snipe 1 · setup 9
   + DMG_SCALE→RETREAT_LOCK (if it scales with retreat cost): Team Rocket's Goo-zooka B4a 068
   + DMG_SCALE→ENERGY_ACCEL (if it scales with energy): Team Rocket's Raticate ex B4a 059, Delcatty B4 135, Wally B4 153, Carbink B3b 031, Regigigas B3 134
   + DMG_REDUCE→STATUS_INFLICT (stall while the condition ticks): Team Rocket's Master Plan B4a 070, Swoobat B4 076, Slowbro B3b 027, Espeon B3a 020, Flittle B3a 021
   + GUST→BENCH_DMG (soften the bench, then pull the damaged one up): Indeedee B2 076, Drifloon B1 107, Alakazam A2b 031, Rotom A2a 035, Lopunny A2 138

## 06 Mega Blaziken (tournament list)  [Fire]  → STATUS-LOCK + AGGRO
   6 Pokémon / 14 Trainers · basics 4 · stage-2 2 · candy 2 · ex 2 · best hit 120 (Mega Blaziken ex) · best dmg/energy 60.0
   families: DRAW_SEARCH×6, STATUS_INFLICT×3, BIG_HIT×2, EVO_ACCEL×2, BENCH_DMG×1, TOOL_SUPPORT×1
   denial 4 · durability 0 · snipe 2 · setup 8
   + STATUS_INFLICT→STATUS_AMP (amplifies or cashes in the condition): Salandit A1a 015
   + STATUS_INFLICT→RETREAT_LOCK (keeps the afflicted Pokémon in the Active Spot): Team Rocket's Goo-zooka B4a 068
   + STATUS_INFLICT→GUST (drags the target you want afflicted into the Active Spot): Swellow B4a 104, Houndour B1a 015, Sabrina A4b 338, Repel A3a 064, Pidgeot A3a 097
   + BENCH_DMG→GUST (finish what the spread damaged): Swellow B4a 104, Houndour B1a 015, Sabrina A4b 338, Repel A3a 064, Pidgeot A3a 097

## 07 Skarmory stall  [Metal]  → WALL + SNIPE
   3 Pokémon / 17 Trainers · basics 3 · stage-2 0 · candy 0 · ex 3 · best hit 70 (Skarmory ex) · best dmg/energy 35.0
   families: DMG_REDUCE×7, HEAL×4, DRAW_SEARCH×4, GUST×3, STATUS_IMMUNE×2, DMG_SCALE×1
   denial 3 · durability 13 · snipe 3 · setup 4
   risks: typed costs outside declared energy: P; very thin Pokémon count
   + DMG_REDUCE→STATUS_INFLICT (stall while the condition ticks): Team Rocket's Master Plan B4a 070, Swablu B3a 102, Minccino B3 142, Revavroom B2a 076, Slakoth B2 134
   + GUST→BENCH_DMG (soften the bench, then pull the damaged one up): Escavalier A3 120, Lopunny A2 138
   + STATUS_IMMUNE→STATUS_INFLICT (lets you run status pressure without eating the mirror): Team Rocket's Master Plan B4a 070, Swablu B3a 102, Minccino B3 142, Revavroom B2a 076, Slakoth B2 134
   + DMG_SCALE→RETREAT_LOCK (if it scales with retreat cost): Team Rocket's Goo-zooka B4a 068

## 08 Garchomp toolbox  [Water, Fighting]  → AGGRO
   8 Pokémon / 12 Trainers · basics 4 · stage-2 2 · candy 0 · ex 0 · best hit 120 (Garchomp) · best dmg/energy 40.0
   families: DRAW_SEARCH×6, BIG_HIT×2, DMG_REDUCE×2, COIN_GAMBLE×2, EVO_ACCEL×1, HEAL×1
   denial 0 · durability 3 · snipe 0 · setup 7
   risks: 2 energy types; Stage 2 line without Rare Candy
   + DMG_REDUCE→HEAL (reduction plus healing is super-additive): Wailord ex B4 037, Alomomola B4 045, Garganacl B3a 033, Castform Rainy Form B3 040, Chansey B3 127
   + DMG_REDUCE→STATUS_INFLICT (stall while the condition ticks): Team Rocket's Master Plan B4a 070, Psyduck B4 030, Mega Lopunny ex B4 228, Milotic ex B3b 015, Piplup B3b 019

## 09 Mega Manectric-Heliolisk  [Lightning]  → SNIPE + AGGRO
   8 Pokémon / 12 Trainers · basics 4 · stage-2 0 · candy 0 · ex 2 · best hit 80 (Mega Manectric ex) · best dmg/energy 40.0
   families: DRAW_SEARCH×6, COIN_GAMBLE×4, STATUS_INFLICT×2, BENCH_DMG×2, DMG_SCALE×2, TOOL_SUPPORT×1
   denial 3 · durability 0 · snipe 3 · setup 6
   + STATUS_INFLICT→RETREAT_LOCK (keeps the afflicted Pokémon in the Active Spot): Team Rocket's Goo-zooka B4a 068
   + STATUS_INFLICT→GUST (drags the target you want afflicted into the Active Spot): Swellow B4a 104, Yamper B1 095, Sabrina A4b 338, Repel A3a 064, Pidgeot A3a 097
   + BENCH_DMG→GUST (finish what the spread damaged): Swellow B4a 104, Yamper B1 095, Sabrina A4b 338, Repel A3a 064, Pidgeot A3a 097
   + DMG_SCALE→RETREAT_LOCK (if it scales with retreat cost): Team Rocket's Goo-zooka B4a 068

## 10 Xatu-Oricorio-TR Weezing  [Psychic]  → SNIPE
   8 Pokémon / 12 Trainers · basics 5 · stage-2 0 · candy 0 · ex 1 · best hit 60 (Team Rocket's Weezing ex) · best dmg/energy 50.0
   families: DRAW_SEARCH×6, COIN_GAMBLE×2, HP_SET×2, SELF_SWITCH×1, STATUS_INFLICT×1, EVO_ACCEL×1
   denial 2 · durability 0 · snipe 3 · setup 6
   risks: typed costs outside declared energy: D; 1-of evolution piece
   + HP_SET→STATUS_INFLICT (any tick finishes a 10-HP target at Checkup): Team Rocket's Master Plan B4a 070, Swoobat B4 076, Slowbro B3b 027, Espeon B3a 020, Flittle B3a 021
   + HP_SET→BENCH_DMG (chip finishes it): Indeedee B2 076, Drifloon B1 107, Alakazam A2b 031, Rotom A2a 035, Lopunny A2 138
   + STATUS_INFLICT→STATUS_AMP (amplifies or cashes in the condition): Hatterene B3 071
   + STATUS_INFLICT→RETREAT_LOCK (keeps the afflicted Pokémon in the Active Spot): Team Rocket's Goo-zooka B4a 068

## 11 Archaludon-Haxorus-Dragonair  [Fighting, Metal]  → SCALING-HITTER + RAMP
   11 Pokémon / 9 Trainers · basics 5 · stage-2 2 · candy 0 · ex 0 · best hit 110 (Archaludon) · best dmg/energy 30.0
   families: DRAW_SEARCH×5, COIN_GAMBLE×3, DMG_SCALE×2, ENERGY_ACCEL×2, BIG_HIT×1, DMG_REDUCE×1
   denial 1 · durability 2 · snipe 0 · setup 7
   risks: 2 energy types; Stage 2 line without Rare Candy; 1-of evolution piece
   + DMG_SCALE→RETREAT_LOCK (if it scales with retreat cost): Team Rocket's Goo-zooka B4a 068
   + ENERGY_ACCEL→BIG_HIT (gets the expensive attack online early): Landorus B4a 037, Hariyama B4 080, Groudon B4 083, Mega Gallade ex B4 084, Conkeldurr B4 089
   + DMG_REDUCE→HEAL (reduction plus healing is super-additive): Garganacl B3a 033, Chansey B3 127, Audino B3 140, Mega Audino ex B3 141, Diantha B2 149
   + DMG_REDUCE→STATUS_INFLICT (stall while the condition ticks): Team Rocket's Master Plan B4a 070, Mega Lopunny ex B4 228, Swablu B3a 102, Toxicroak B3 083, Minccino B3 142

## 12 Ariados-Whimsicott-Ogerpon  [Grass]  → MIDRANGE
   9 Pokémon / 11 Trainers · basics 5 · stage-2 0 · candy 0 · ex 3 · best hit 60 (Teal Mask Ogerpon ex) · best dmg/energy 30.0
   families: DRAW_SEARCH×6, RETREAT_LOCK×4, DMG_SCALE×2, STATUS_IMMUNE×1, HEAL×1, EVO_ACCEL×1
   denial 4 · durability 2 · snipe 0 · setup 6
   + RETREAT_LOCK→STATUS_INFLICT (trapped Pokémon can't shed the condition): Team Rocket's Master Plan B4a 070, Dustox B4 005, Accelgor B4 014, Sinistcha B4 018, Swablu B3a 102
   + DMG_SCALE→ENERGY_ACCEL (if it scales with energy): Team Rocket's Raticate ex B4a 059, Delcatty B4 135, Psychic B4 150, Wally B4 153, Regigigas B3 134
   + STATUS_IMMUNE→STATUS_INFLICT (lets you run status pressure without eating the mirror): Team Rocket's Master Plan B4a 070, Dustox B4 005, Accelgor B4 014, Sinistcha B4 018, Swablu B3a 102
   + HEAL→DMG_REDUCE (reduction plus healing is super-additive): Team Rocket's Kecleon B4a 062, Furfrou B4a 064, Unfezant B4 139, Clear Veil B4 149, Wigglytuff B3b 052

## 13 A.Ninetales-Raticate  [Water]  → DENIAL/CONTROL + AGGRO + RAMP
   8 Pokémon / 12 Trainers · basics 4 · stage-2 0 · candy 0 · ex 4 · best hit 80 (Alolan Ninetales ex) · best dmg/energy 40.0
   families: DRAW_SEARCH×7, ENERGY_DENIAL×4, COIN_GAMBLE×2, ENERGY_ACCEL×2, EVO_ACCEL×2, GUST×2
   denial 6 · durability 0 · snipe 2 · setup 9
   + ENERGY_DENIAL→RETREAT_LOCK (a stranded, energy-less Active can't leave): Team Rocket's Goo-zooka B4a 068
   + ENERGY_DENIAL→DMG_REDUCE (buy the turns denial needs): Team Rocket's Kecleon B4a 062, Furfrou B4a 064, Samurott B4 044, Unfezant B4 139, Clear Veil B4 149
   + ENERGY_ACCEL→BIG_HIT (gets the expensive attack online early): Team Rocket's Articuno ex B4a 014, Wailord ex B4 037, Walrein B4 040, Swanna ex B4 141, Swampert B4 207
   + GUST→BENCH_DMG (soften the bench, then pull the damaged one up): Seaking B4a 098, Kyogre B4 041, Samurott B4 044, Rapid Strike Urshifu B3 051, Palafin B2a 028

## 14 Comfey-Raticate-Hypno  [Psychic]  → DENIAL/CONTROL + SNIPE + RAMP
   9 Pokémon / 11 Trainers · basics 5 · stage-2 0 · candy 0 · ex 2 · best hit 70 (Team Rocket's Raticate ex) · best dmg/energy 35.0
   families: DRAW_SEARCH×7, COIN_GAMBLE×3, GUST×3, ENERGY_DENIAL×2, ENERGY_ACCEL×2, EVO_ACCEL×2
   denial 6 · durability 2 · snipe 3 · setup 9
   + GUST→BENCH_DMG (soften the bench, then pull the damaged one up): Indeedee B2 076, Drifloon B1 107, Alakazam A2b 031, Rotom A2a 035, Lopunny A2 138
   + GUST→HP_SET (pull the target you can finish): Xatu A4 082
   + ENERGY_DENIAL→DMG_REDUCE (buy the turns denial needs): Team Rocket's Kecleon B4a 062, Furfrou B4a 064, Sinistea B4a 100, Unfezant B4 139, Clear Veil B4 149
   + ENERGY_ACCEL→BIG_HIT (gets the expensive attack online early): Team Rocket's Mewtwo B4a 030, Swanna ex B4 141, Mega Gardevoir ex B4 227, Ursaluna B3b 058, Greedent B3b 063

## 15 Jolteon-Oricorio-Raticate  [Lightning]  → DENIAL/CONTROL + AGGRO + RAMP
   9 Pokémon / 11 Trainers · basics 5 · stage-2 0 · candy 0 · ex 4 · best hit 80 (Jolteon ex) · best dmg/energy 40.0
   families: DRAW_SEARCH×7, EVO_ACCEL×4, COIN_GAMBLE×2, ENERGY_DENIAL×2, ENERGY_ACCEL×2, GUST×2
   denial 5 · durability 3 · snipe 2 · setup 9
   + ENERGY_DENIAL→DMG_REDUCE (buy the turns denial needs): Team Rocket's Kecleon B4a 062, Furfrou B4a 064, Unfezant B4 139, Clear Veil B4 149, Wigglytuff B3b 052
   + ENERGY_ACCEL→BIG_HIT (gets the expensive attack online early): Thundurus B4 059, Swanna ex B4 141, Ursaluna B3b 058, Greedent B3b 063, Mega Ampharos ex B3b 103
   + GUST→BENCH_DMG (soften the bench, then pull the damaged one up): Team Rocket's Zapdos ex B4a 021, Toxtricity ex B4a 106, Heliolisk B4 061, Minun B4 210, Pawmo B3a 015
   + DMG_REDUCE→HEAL (reduction plus healing is super-additive): Chansey B3 127, Audino B3 140, Mega Audino ex B3 141, Lucky Ice Pop B2 145, Diantha B2 149

## T-altaria  [Psychic]  → DENIAL/CONTROL + STATUS-LOCK
   10 Pokémon / 10 Trainers · basics 7 · stage-2 0 · candy 0 · ex 1 · best hit 40 (Mega Altaria ex) · best dmg/energy 40.0
   families: STATUS_INFLICT×7, DRAW_SEARCH×6, EVO_ACCEL×2, STATUS_AMP×2, DMG_SCALE×1, GUST×1
   denial 8 · durability 0 · snipe 1 · setup 6
   risks: 1-of evolution piece

## T-blaziken  [Fire]  → STATUS-LOCK + AGGRO
   6 Pokémon / 14 Trainers · basics 4 · stage-2 2 · candy 2 · ex 2 · best hit 120 (Mega Blaziken ex) · best dmg/energy 60.0
   families: DRAW_SEARCH×6, STATUS_INFLICT×3, BIG_HIT×2, EVO_ACCEL×2, BENCH_DMG×1, GUST×1
   denial 4 · durability 0 · snipe 2 · setup 8

## T-hydreigon  [Darkness]  → AGGRO
   6 Pokémon / 14 Trainers · basics 4 · stage-2 2 · candy 2 · ex 1 · best hit 130 (Hydreigon) · best dmg/energy 43.3
   families: DRAW_SEARCH×6, BIG_HIT×2, GUST×2, EVO_ACCEL×2, COIN_GAMBLE×2, HEAL×2
   denial 3 · durability 2 · snipe 2 · setup 8

## T-lucario  [Fighting]  → AGGRO
   7 Pokémon / 13 Trainers · basics 4 · stage-2 0 · candy 0 · ex 2 · best hit 90 (Mega Lucario ex) · best dmg/energy 45.0
   families: DRAW_SEARCH×6, BENCH_DMG×1, STATUS_IMMUNE×1, HEAL×1, GUST×1, TOOL_SUPPORT×1
   denial 1 · durability 3 · snipe 2 · setup 6
   risks: 1-of evolution piece

## T-sceptile  [Grass]  → SNIPE
   9 Pokémon / 11 Trainers · basics 3 · stage-2 3 · candy 0 · ex 1 · best hit 130 (Mega Sceptile ex) · best dmg/energy 65.0
   families: DRAW_SEARCH×7, EVO_ACCEL×4, HEAL×3, GUST×2, BENCH_DMG×1, BIG_HIT×1
   denial 3 · durability 3 · snipe 3 · setup 7
   risks: Stage 2 line without Rare Candy; 1-of evolution piece

## T-suicune  [Water]  → RAMP
   7 Pokémon / 13 Trainers · basics 5 · stage-2 2 · candy 2 · ex 3 · best hit 90 (Baxcalibur) · best dmg/energy 30.0
   families: DRAW_SEARCH×7, ENERGY_ACCEL×2, EVO_ACCEL×2, DMG_REDUCE×1, STATUS_IMMUNE×1, HEAL×1
   denial 0 · durability 3 · snipe 0 · setup 11

## T-vespiquen  [Grass]  → WALL
   7 Pokémon / 13 Trainers · basics 5 · stage-2 0 · candy 0 · ex 5 · best hit 70 (Vespiquen ex) · best dmg/energy 35.0
   families: DRAW_SEARCH×4, SELF_DMG×2, COIN_GAMBLE×2, DMG_REDUCE×2, GUST×2, STATUS_IMMUNE×1
   denial 2 · durability 4 · snipe 2 · setup 4
   risks: ex-heavy (2-point KOs)

## T-weezing  [Darkness]  → DENIAL/CONTROL + SNIPE
   7 Pokémon / 13 Trainers · basics 5 · stage-2 0 · candy 0 · ex 5 · best hit 100 (Hoopa ex) · best dmg/energy 33.3
   families: DRAW_SEARCH×6, BIG_HIT×2, BENCH_DMG×2, SELF_DMG×2, SELF_SWITCH×2, STATUS_INFLICT×2
   denial 5 · durability 0 · snipe 4 · setup 7
   risks: ex-heavy (2-point KOs)

# nearest neighbours (cosine on family vector)
   01 Muk-Glimmora-Kingambit-Regigigas           ~ 11 Archaludon-Haxorus-Dragonair (0.69) | T-blaziken (0.55)
   02 Arceus-Crobat                              ~ 09 Mega Manectric-Heliolisk (0.77) | T-altaria (0.60)
   03 Wailord-Indeedee wall                      ~ 05 Indeedee-Stoutland (0.89) | T-sceptile (0.73)
   04 Absol-Hoopa-Darkrai                        ~ T-weezing (0.85) | T-hydreigon (0.64)
   05 Indeedee-Stoutland                         ~ 03 Wailord-Indeedee wall (0.89) | 07 Skarmory stall (0.80)
   06 Mega Blaziken (tournament list)            ~ T-blaziken (1.00) | T-weezing (0.77)
   07 Skarmory stall                             ~ T-vespiquen (0.93) | T-lucario (0.81)
   08 Garchomp toolbox                           ~ 07 Skarmory stall (0.64) | 11 Archaludon-Haxorus-Dragonair (0.64)
   09 Mega Manectric-Heliolisk                   ~ 02 Arceus-Crobat (0.77) | T-blaziken (0.64)
   10 Xatu-Oricorio-TR Weezing                   ~ T-weezing (0.48) | T-altaria (0.41)
   11 Archaludon-Haxorus-Dragonair               ~ 05 Indeedee-Stoutland (0.73) | 01 Muk-Glimmora-Kingambit-Regigigas (0.69)
   12 Ariados-Whimsicott-Ogerpon                 ~ 03 Wailord-Indeedee wall (0.39) | 02 Arceus-Crobat (0.35)
   13 A.Ninetales-Raticate                       ~ 14 Comfey-Raticate-Hypno (0.82) | 15 Jolteon-Oricorio-Raticate (0.82)
   14 Comfey-Raticate-Hypno                      ~ 15 Jolteon-Oricorio-Raticate (0.95) | 13 A.Ninetales-Raticate (0.82)
   15 Jolteon-Oricorio-Raticate                  ~ 14 Comfey-Raticate-Hypno (0.95) | 13 A.Ninetales-Raticate (0.82)
   T-altaria                                     ~ T-blaziken (0.77) | 06 Mega Blaziken (tournament list) (0.77)
   T-blaziken                                    ~ 06 Mega Blaziken (tournament list) (1.00) | T-weezing (0.77)
   T-hydreigon                                   ~ T-sceptile (0.80) | 04 Absol-Hoopa-Darkrai (0.64)
   T-lucario                                     ~ T-vespiquen (0.85) | 07 Skarmory stall (0.81)
   T-sceptile                                    ~ T-hydreigon (0.80) | 03 Wailord-Indeedee wall (0.73)
   T-suicune                                     ~ 15 Jolteon-Oricorio-Raticate (0.66) | 11 Archaludon-Haxorus-Dragonair (0.65)
   T-vespiquen                                   ~ 07 Skarmory stall (0.93) | T-lucario (0.85)
   T-weezing                                     ~ 04 Absol-Hoopa-Darkrai (0.85) | T-blaziken (0.77)

# complements for Team Rocket's Weezing ex B4a 043  (families: EVO_ACCEL, STATUS_INFLICT)
   STATUS_INFLICT → STATUS_AMP: amplifies or cashes in the condition  [14 cards] e.g. Muk A1 175, Salandit A1a 015, Scolipede A1a 055, Paldean Clodsire ex A2b 048, Nihilego A3a 042, Heatmor A4 037, Toxapex B1 162, Illumise B2b 004, Darkrai B2b 040, Breloom B3 012
   STATUS_INFLICT → RETREAT_LOCK: keeps the afflicted Pokémon in the Active Spot  [2 cards] e.g. Ariados B1a 006, Team Rocket's Goo-zooka B4a 068
   STATUS_INFLICT → GUST: drags the target you want afflicted into the Active Spot  [19 cards] e.g. Victreebel A1 020, Grapploct A1 163, Pidgeot A1 188, Sabrina A1 225, Cyrus A2 150, Hariyama A3 091, Lana A3 152, Repel A3a 064, Umbreon ex A4 112, Rillaboom B1 027

# complements for Nihilego A3a 042  (families: STATUS_AMP, STATUS_INFLICT)
   STATUS_AMP → STATUS_INFLICT: supplies the condition it amplifies  [137 cards] e.g. Vileplume A1 013, Venomoth A1 017, Tentacruel A1 063, Articuno A1 083, Frosmoth A1 093, Eelektross A1 109, Pincurchin A1 112, Hypno A1 125, Nidoking A1 171, Grimer A1 174
   STATUS_INFLICT → STATUS_AMP: amplifies or cashes in the condition  [13 cards] e.g. Muk A1 175, Salandit A1a 015, Scolipede A1a 055, Paldean Clodsire ex A2b 048, Heatmor A4 037, Toxapex B1 162, Illumise B2b 004, Darkrai B2b 040, Breloom B3 012, Oricorio B3 068
   STATUS_INFLICT → RETREAT_LOCK: keeps the afflicted Pokémon in the Active Spot  [2 cards] e.g. Ariados B1a 006, Team Rocket's Goo-zooka B4a 068
   STATUS_INFLICT → GUST: drags the target you want afflicted into the Active Spot  [19 cards] e.g. Victreebel A1 020, Grapploct A1 163, Pidgeot A1 188, Sabrina A1 225, Cyrus A2 150, Hariyama A3 091, Lana A3 152, Repel A3a 064, Umbreon ex A4 112, Rillaboom B1 027

# complements for Arceus ex A2a 071  (families: DMG_SCALE, STATUS_IMMUNE)
   DMG_SCALE → RETREAT_LOCK: if it scales with retreat cost  [2 cards] e.g. Ariados B1a 006, Team Rocket's Goo-zooka B4a 068
   DMG_SCALE → ENERGY_ACCEL: if it scales with energy  [58 cards] e.g. Lilligant A1 030, Magneton A1 098, Gardevoir A1 132, Meltan A1 181, Misty A1 220, Brock A1 224, Lt. Surge A1 226, Exeggcute A1a 001, Vaporeon A1a 019, Magmar A2 023
   STATUS_IMMUNE → STATUS_INFLICT: lets you run status pressure without eating the mirror  [138 cards] e.g. Vileplume A1 013, Venomoth A1 017, Tentacruel A1 063, Articuno A1 083, Frosmoth A1 093, Eelektross A1 109, Pincurchin A1 112, Hypno A1 125, Nidoking A1 171, Grimer A1 174

```
