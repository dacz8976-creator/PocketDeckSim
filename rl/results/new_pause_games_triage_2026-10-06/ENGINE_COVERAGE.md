# Engine coverage of the new Pause Games batch (Oct 6)

Status source: the pinned official engine's card status (`engine_version` 0.1.0-pdl.rules4, schema 1; 3879 cards; main-8626a35, the same program the strength runs use). "Dispatch coverage and known limitations; Complete is not independent game-rule certification."

The engine's status values in that dump: Complete 3871, RulesUnverified 8; no card is missing or partial. RulesUnverified cards are implemented but carry a documented unverified rule choice.

## The eight RulesUnverified cards, and whether the batch touches them

| card | id | in one of his 14 lists | opponent card seen |
|---|---|---|---|
| Victini | B3 025 | no | no |
| Revavroom | B4 115 | no | no |
| Hisuian Basculegion | B4a 018 | no | no |
| Gholdengo | B4a 051 | no | no |
| Team Rocket's Researcher | B4a 069 | no | no |
| Team Rocket's Researcher | B4a 085 | no | no |
| Gholdengo | B4a 109 | no | no |
| Victini | P-B 049 | no | no |

None of the eight appears in his lists or among the opponent cards the reviews name.

## His 14 lists

Every card slot resolved to its printings through the prepared deck entries' `semantic_variant_references` (the QR identifies the playable card, not the artwork), and each printing's status was read.

### Butterfree / Accelgor (New deck 24; Energy: Grass)

| count | card | printings checked | engine status |
|---|---|---|---|
| 2 | Caterpie | B3b 001, B3b 091 | Complete x2 |
| 2 | Metapod | B3b 002, B3b 092 | Complete x2 |
| 2 | Butterfree | B3b 003, B3b 093 | Complete x2 |
| 2 | Shelmet | B4 013 | Complete x1 |
| 2 | Accelgor | B4 014, B4 159 | Complete x2 |
| 2 | Poké Ball | A2b 111, P-A 005 | Complete x2 |
| 2 | Quick-Grow Extract | B1a 067, B1a 103 | Complete x2 |
| 2 | Lucky Ice Pop | B2 145 | Complete x1 |
| 2 | Professor’s Research | A4b 373, P-A 007 | Complete x2 |
| 1 | Hiking Trail | B2b 069 | Complete x1 |
| 1 | Fragrant Forest | B3 153 | Complete x1 |

### Mega Blaziken / Combusken (New deck 1; Energy: Fire)

| count | card | printings checked | engine status |
|---|---|---|---|
| 2 | Torchic | B1 033, B3 206, P-B 007 | Complete x3 |
| 2 | Combusken | B1 034, B3 207 | Complete x2 |
| 2 | Mega Blaziken ex | B1 036, B1 254, B1 284, B3 226 | Complete x4 |
| 1 | Heatmor | B1 044 | Complete x1 |
| 1 | Castform Sunny Form | B3 024, P-B 057 | Complete x2 |
| 2 | Poké Ball | A2b 111, P-A 005 | Complete x2 |
| 2 | Flame Patch | B1 217, B1 331 | Complete x2 |
| 1 | Field Blower | B3 147 | Complete x1 |
| 1 | Rocky Helmet | A2 148, A4b 322, A4b 323 | Complete x3 |
| 2 | Professor’s Research | A4b 373, P-A 007 | Complete x2 |
| 1 | Cyrus | A2 150, A2 190, A4b 326, A4b 327 | Complete x4 |
| 2 | Copycat | B1 225, B1 270 | Complete x2 |
| 1 | Hiking Trail | B2b 069 | Complete x1 |

### Wailord / Mega Sharpedo / Suicune (New deck 6; Energy: Water)

| count | card | printings checked | engine status |
|---|---|---|---|
| 2 | Wailmer | B4 036 | Complete x1 |
| 2 | Wailord | B1 057 | Complete x1 |
| 2 | Carvanha | B4 034 | Complete x1 |
| 2 | Mega Sharpedo ex | B4 035, B4 182, B4 196 | Complete x3 |
| 2 | Suicune ex | A4a 020, A4a 080, A4a 090, B2a 127 | Complete x4 |
| 2 | Poké Ball | A2b 111, P-A 005 | Complete x2 |
| 1 | Lucky Ice Pop | B2 145 | Complete x1 |
| 2 | Professor’s Research | A4b 373, P-A 007 | Complete x2 |
| 1 | Irida | A2a 072, A2a 087, A4b 330, A4b 331 | Complete x4 |
| 1 | Copycat | B1 225, B1 270 | Complete x2 |
| 1 | Wallace | B3b 068, B3b 085 | Complete x2 |
| 2 | Soothing Shore | B4 154 | Complete x1 |

### Hatterene / Aromatisse / Togekiss (New deck 6; Energy: Psychic)

| count | card | printings checked | engine status |
|---|---|---|---|
| 2 | Hatenna | B3 069 | Complete x1 |
| 1 | Hattrem | B3 070 | Complete x1 |
| 2 | Hatterene | B3 071 | Complete x1 |
| 1 | Spritzee | B1 115 | Complete x1 |
| 1 | Spritzee | B1a 035 | Complete x1 |
| 1 | Aromatisse | B1a 036 | Complete x1 |
| 1 | Aromatisse | B1 116 | Complete x1 |
| 1 | Togepi | A2 063, P-A 041 | Complete x2 |
| 1 | Togepi | A4 078, A4 173 | Complete x2 |
| 1 | Togetic | A2 064 | Complete x1 |
| 2 | Togekiss | A4 080 | Complete x1 |
| 2 | Poké Ball | A2b 111, P-A 005 | Complete x2 |
| 2 | Rare Candy | A3 144, A4b 314, A4b 315, A4b 379 | Complete x4 |
| 2 | Professor’s Research | A4b 373, P-A 007 | Complete x2 |

### Aegislash / Tinkaton ex / Team Rocket's Tinkaton (label not read; Energy: Metal)

| count | card | printings checked | engine status |
|---|---|---|---|
| 2 | Honedge | B1 170 | Complete x1 |
| 1 | Doublade | B1 171 | Complete x1 |
| 1 | Aegislash | B1 172, B1a 102 | Complete x2 |
| 1 | Aegislash | B2 120 | Complete x1 |
| 1 | Tinkatuff | B2a 073, B2a 124 | Complete x2 |
| 1 | Tinkaton ex | A2b 054, A2b 086, A2b 094, A4b 266, B2a 129 | Complete x5 |
| 2 | Team Rocket’s Tinkatink | B4a 048 | Complete x1 |
| 1 | Team Rocket’s Tinkaton | B4a 050, B4a 075 | Complete x2 |
| 2 | Poké Ball | A2b 111, P-A 005 | Complete x2 |
| 2 | Rare Candy | A3 144, A4b 314, A4b 315, A4b 379 | Complete x4 |
| 2 | Lucky Ice Pop | B2 145 | Complete x1 |
| 2 | Metal Core Barrier | B2 148, B2b 117 | Complete x2 |
| 2 | Professor’s Research | A4b 373, P-A 007 | Complete x2 |

### Aegislash / Team Rocket's Tinkaton (label not read; Energy: Metal)

| count | card | printings checked | engine status |
|---|---|---|---|
| 2 | Honedge | B1 170 | Complete x1 |
| 1 | Doublade | B1 171 | Complete x1 |
| 1 | Aegislash | B1 172, B1a 102 | Complete x2 |
| 1 | Aegislash | B2 120 | Complete x1 |
| 1 | Tinkatuff | B2a 073, B2a 124 | Complete x2 |
| 2 | Team Rocket’s Tinkatink | B4a 048 | Complete x1 |
| 2 | Team Rocket’s Tinkaton | B4a 050, B4a 075 | Complete x2 |
| 2 | Poké Ball | A2b 111, P-A 005 | Complete x2 |
| 2 | Rare Candy | A3 144, A4b 314, A4b 315, A4b 379 | Complete x4 |
| 2 | Lucky Ice Pop | B2 145 | Complete x1 |
| 2 | Metal Core Barrier | B2 148, B2b 117 | Complete x2 |
| 2 | Professor’s Research | A4b 373, P-A 007 | Complete x2 |

### Skarmory ex / Aegislash / Orthworm (label not read; Energy: Metal)

| count | card | printings checked | engine status |
|---|---|---|---|
| 2 | Skarmory ex | A4 124, A4 194, A4 209, A4b 252 | Complete x4 |
| 2 | Honedge | B1 170 | Complete x1 |
| 1 | Doublade | B1 171 | Complete x1 |
| 1 | Aegislash | B1 172, B1a 102 | Complete x2 |
| 1 | Aegislash | B2 120 | Complete x1 |
| 1 | Orthworm | B2a 077, B2a 098, B3a 101 | Complete x3 |
| 2 | Poké Ball | A2b 111, P-A 005 | Complete x2 |
| 2 | Rare Candy | A3 144, A4b 314, A4b 315, A4b 379 | Complete x4 |
| 2 | Lucky Ice Pop | B2 145 | Complete x1 |
| 1 | Steel Apron | A4 153 | Complete x1 |
| 2 | Metal Core Barrier | B2 148, B2b 117 | Complete x2 |
| 2 | Professor’s Research | A4b 373, P-A 007 | Complete x2 |
| 1 | Copycat | B1 225, B1 270 | Complete x2 |

### Aegislash / Melmetal ex / Magnezone (label not read; Energy: Metal)

| count | card | printings checked | engine status |
|---|---|---|---|
| 1 | Magnemite | A2a 053, A2a 080 | Complete x2 |
| 1 | Magneton | A2a 054 | Complete x1 |
| 1 | Magnezone | A2a 055 | Complete x1 |
| 1 | Honedge | B1 170 | Complete x1 |
| 1 | Honedge | B2 118 | Complete x1 |
| 1 | Doublade | B1 171 | Complete x1 |
| 1 | Doublade | B2 119 | Complete x1 |
| 1 | Aegislash | B1 172, B1a 102 | Complete x2 |
| 1 | Aegislash | B2 120 | Complete x1 |
| 2 | Meltan | A1 181 | Complete x1 |
| 2 | Melmetal ex | B1 174, B1 264, B1 282 | Complete x3 |
| 2 | Poké Ball | A2b 111, P-A 005 | Complete x2 |
| 2 | Steel Apron | A4 153 | Complete x1 |
| 1 | Metal Core Barrier | B2 148, B2b 117 | Complete x2 |
| 2 | Professor’s Research | A4b 373, P-A 007 | Complete x2 |

### Nidoking / Nihilego / Darkrai ex (two Darkrai) (label not read; Energy: Darkness)

| count | card | printings checked | engine status |
|---|---|---|---|
| 2 | Darkrai ex | A2 110, A2 187, A2 202, A4b 245, A4b 378, P-A 042 | Complete x6 |
| 2 | Nidoran♂ | A1 169, A4 226 | Complete x2 |
| 1 | Nidorino | A1 170, A4 227 | Complete x2 |
| 2 | Nidoking | A1 171, A1 241, A4 228 | Complete x3 |
| 2 | Nihilego | A3a 042, A3a 103, A4b 246, A4b 247 | Complete x4 |
| 2 | Poké Ball | A2b 111, P-A 005 | Complete x2 |
| 2 | Lucky Ice Pop | B2 145 | Complete x1 |
| 1 | Poison Barb | A3 146 | Complete x1 |
| 1 | Deceptive Needle | B4 148 | Complete x1 |
| 1 | Heavy Helmet | B1 219 | Complete x1 |
| 2 | Professor’s Research | A4b 373, P-A 007 | Complete x2 |
| 1 | Copycat | B1 225, B1 270 | Complete x2 |
| 1 | Wally | B4 153, B4 193 | Complete x2 |

### Nidoking / Nihilego / Darkrai ex (one Darkrai) (label not read; Energy: Darkness)

| count | card | printings checked | engine status |
|---|---|---|---|
| 1 | Darkrai ex | A2 110, A2 187, A2 202, A4b 245, A4b 378, P-A 042 | Complete x6 |
| 2 | Nidoran♂ | A1 169, A4 226 | Complete x2 |
| 1 | Nidorino | A1 170, A4 227 | Complete x2 |
| 2 | Nidoking | A1 171, A1 241, A4 228 | Complete x3 |
| 2 | Nihilego | A3a 042, A3a 103, A4b 246, A4b 247 | Complete x4 |
| 2 | Poké Ball | A2b 111, P-A 005 | Complete x2 |
| 2 | Lucky Ice Pop | B2 145 | Complete x1 |
| 1 | Poison Barb | A3 146 | Complete x1 |
| 1 | Deceptive Needle | B4 148 | Complete x1 |
| 1 | Heavy Helmet | B1 219 | Complete x1 |
| 2 | Professor’s Research | A4b 373, P-A 007 | Complete x2 |
| 1 | Cyrus | A2 150, A2 190, A4b 326, A4b 327 | Complete x4 |
| 1 | Copycat | B1 225, B1 270 | Complete x2 |
| 1 | Wally | B4 153, B4 193 | Complete x2 |

### Scolipede / Mega Sableye ex (label not read; Energy: Darkness)

| count | card | printings checked | engine status |
|---|---|---|---|
| 2 | Venipede | A1a 053 | Complete x1 |
| 2 | Whirlipede | A1a 054 | Complete x1 |
| 2 | Scolipede | A1a 055 | Complete x1 |
| 2 | Mega Sableye ex | B3b 041, B3b 081, B3b 088 | Complete x3 |
| 2 | Poké Ball | A2b 111, P-A 005 | Complete x2 |
| 2 | Lucky Ice Pop | B2 145 | Complete x1 |
| 2 | Poison Barb | A3 146 | Complete x1 |
| 1 | Deceptive Needle | B4 148 | Complete x1 |
| 2 | Professor’s Research | A4b 373, P-A 007 | Complete x2 |
| 1 | Cyrus | A2 150, A2 190, A4b 326, A4b 327 | Complete x4 |
| 1 | Copycat | B1 225, B1 270 | Complete x2 |
| 1 | Wally | B4 153, B4 193 | Complete x2 |

### Terapagos ex / Silvally / Persian (label not read; Energy: Grass, Darkness, Metal)

| count | card | printings checked | engine status |
|---|---|---|---|
| 1 | Snorlax ex | A3b 057, A3b 084, A3b 091, A4b 288 | Complete x4 |
| 1 | Meowth | B2 124, B2 204 | Complete x2 |
| 1 | Meowth | A1 196, A1 246, B1 312, P-A 012 | Complete x4 |
| 2 | Persian | A1 197, B1 313 | Complete x2 |
| 2 | Terapagos ex | B3a 068, B3a 085, B3a 093 | Complete x3 |
| 2 | Type: Null | A3a 060, A4b 300, A4b 301, B1a 096 | Complete x4 |
| 2 | Silvally | A3a 061, A3a 074, A4b 302, A4b 303, B1a 097 | Complete x5 |
| 2 | Poké Ball | A2b 111, P-A 005 | Complete x2 |
| 2 | Lucky Ice Pop | B2 145 | Complete x1 |
| 1 | Field Blower | B3 147 | Complete x1 |
| 2 | Professor’s Research | A4b 373, P-A 007 | Complete x2 |
| 1 | Cyrus | A2 150, A2 190, A4b 326, A4b 327 | Complete x4 |
| 1 | Copycat | B1 225, B1 270 | Complete x2 |

### Conkeldurr / Sandslash / Hitmonchan ex (label not read; Energy: Fighting)

| count | card | printings checked | engine status |
|---|---|---|---|
| 2 | Timburr | A3 094 | Complete x1 |
| 1 | Conkeldurr | A3 096 | Complete x1 |
| 1 | Conkeldurr | B4 089 | Complete x1 |
| 1 | Hitmonchan ex | B1 124, B1 261, B1 279, B3 229 | Complete x4 |
| 2 | Sandshrew | B2 077, B2 170 | Complete x2 |
| 1 | Sandslash | B2 078 | Complete x1 |
| 1 | Sandslash | A1 138 | Complete x1 |
| 2 | Poké Ball | A2b 111, P-A 005 | Complete x2 |
| 2 | Rare Candy | A3 144, A4b 314, A4b 315, A4b 379 | Complete x4 |
| 2 | Lucky Ice Pop | B2 145 | Complete x1 |
| 2 | Professor’s Research | A4b 373, P-A 007 | Complete x2 |
| 1 | Cyrus | A2 150, A2 190, A4b 326, A4b 327 | Complete x4 |
| 1 | Copycat | B1 225, B1 270 | Complete x2 |
| 1 | Wally | B4 153, B4 193 | Complete x2 |

### Snorlax ex / Team Rocket's Persian / Silvally (Water revision) (edit of New deck 6 (game 2); Energy: Water)

| count | card | printings checked | engine status |
|---|---|---|---|
| 1 | Snorlax ex | A3b 057, A3b 084, A3b 091, A4b 288 | Complete x4 |
| 2 | Team Rocket's Meowth | B4a 060 | Complete x1 |
| 2 | Team Rocket's Persian | B4a 061 | Complete x1 |
| 2 | Type: Null | A3a 060, A4b 300, A4b 301, B1a 096 | Complete x4 |
| 1 | Silvally | B4 144 | Complete x1 |
| 1 | Silvally | A3a 061, A3a 074, A4b 302, A4b 303, B1a 097 | Complete x5 |
| 2 | Poké Ball | A2b 111, P-A 005 | Complete x2 |
| 2 | Lucky Ice Pop | B2 145 | Complete x1 |
| 1 | Field Blower | B3 147 | Complete x1 |
| 2 | Professor's Research | A4b 373, P-A 007 | Complete x2 |
| 1 | Cyrus | A2 150, A2 190, A4b 326, A4b 327 | Complete x4 |
| 1 | Copycat | B1 225, B1 270 | Complete x2 |
| 2 | Soothing Shore | B4 154 | Complete x1 |

Total printings checked in the 14 lists: 363; statuses: {'Complete': 363}.

## Opponent cards named in the reviews' boards, plays and reveals

Names come from the ledgers (both boards at every boundary, every opponent play, every public reveal). Hidden draws and searches stay unnamed, so cards he never saw are not here. A name is matched to every printing with that name; the status shown is the worst across them.

| card | printings with that name | engine status | games (hhmmss of the recording; g2 = second game of 012927) |
|---|---|---|---|
| Alolan Diglett | 5 | Complete | 012140 |
| Arena of Antiquity | 1 | Complete | 033529 |
| Axew | 2 | Complete | 034953 |
| Budew | 2 | Complete | 213625 |
| Bulbasaur | 7 | Complete | 032857 |
| Charizard ex | 10 | Complete | 124532 |
| Charmander | 10 | Complete | 124532 |
| Charmeleon | 9 | Complete | 124532 |
| Combee | 4 | Complete | 213625 |
| Comfey | 2 | Complete | 032023 |
| Copperajah | 2 | Complete | 020518 |
| Copycat | 2 | Complete | 012927, 033529, 034229, 214731 |
| Cufant | 2 | Complete | 020518 |
| Cyclizar | 7 | Complete | 214731 |
| Cynthia | 2 | Complete | 012927 |
| Cyrus | 4 | Complete | 003547, 033529 |
| Dialga ex | 7 | Complete | 012140 |
| Dragonair | 10 | Complete | 214731 |
| Dratini | 7 | Complete | 214731 |
| Electric Generator | 2 | Complete | 031138 |
| Elegant Cape | 1 | Complete | 003547 |
| Entei ex | 5 | Complete | 124532 |
| Exeggcute | 7 | Complete | 213625 |
| Finizen | 1 | Complete | 032023 |
| Flame Patch | 2 | Complete | 124532, 215749 |
| Fragrant Forest | 1 | Complete | 213625, 214731 |
| Fraxure | 2 | Complete | 034953 |
| Froakie | 7 | Complete | 031138 |
| Garchomp | 3 | Complete | 012927 |
| Giant Cape | 3 | Complete | 032023 |
| Gible | 7 | Complete | 012927 |
| Gourgeist | 1 | Complete | 003547, 183108 |
| Greavard | 3 | Complete | 003547, 183108 |
| Greninja | 6 | Complete | 031138 |
| Happiny | 2 | Complete | 012927, 034953 |
| Haxorus | 3 | Complete | 034953 |
| Hiking Trail | 1 | Complete | 003547, 213625, 214731, 215749 |
| Hitmonlee | 3 | Complete | 033529 |
| Honedge | 2 | Complete | 012140 |
| Houndstone | 2 | Complete | 003547, 183108 |
| Ivysaur | 5 | Complete | 032857 |
| Leaf Cape | 3 | Complete | 032857, 213625 |
| Leftovers | 1 | Complete | 214731 |
| Lucky Ice Pop | 1 | Complete | 032023, 032857, 033529 |
| Manaphy | 6 | Complete | 032023 |
| Marshadow | 4 | Complete | 033529 |
| May | 2 | Complete | 020518, 124532 |
| Mega Diancie ex | 3 | Complete | 034229, 123812 |
| Mega Gardevoir ex | 4 | Complete | 034229, 123812 |
| Mega Lucario ex | 3 | Complete | 033529 |
| Mega Rayquaza ex | 3 | Complete | 214731 |
| Mega Venusaur ex | 3 | Complete | 032857 |
| Meloetta | 5 | Complete | 183108 |
| Meltan | 5 | Complete | 215749 |
| Metapod | 3 | Complete | 213625 |
| Mewtwo ex | 7 | Complete | 034229 |
| Munchlax | 2 | Complete | 012927, 034953 |
| Order Pad | 1 | Complete | 012927/g2 |
| Oricorio | 16 | Complete | 003547 |
| Palafin | 1 | Complete | 032023 |
| Peculiar Plaza | 1 | Complete | 003547, 034229, 123812, 183108 |
| Pinsir | 6 | Complete | 213625 |
| Poke Ball | 2 | Complete | 012140, 032023, 034229, 034953, 123812, 124532 |
| Poké Ball | 2 | Complete | 003547, 012927, 033529, 214731 |
| Pokemon Center Lady | 2 | Complete | 123812, 124532 |
| Pokémon Center Lady | 2 | Complete | 003547 |
| Potion | 1 | Complete | 215749 |
| Professor's Research | 2 | Complete | 003547, 032857, 034229, 034953, 123812, 124532, 213625, 214731, 215749 |
| Professor’s Research | 2 | Complete | 012927, 012927/g2, 020518, 033529, 183108 |
| Protective Poncho | 2 | Complete | 012927 |
| Pumpkaboo | 1 | Complete | 003547, 183108 |
| Quick-Grow Extract | 2 | Complete | 032857 |
| Rainbow Cave | 1 | Complete | 012927, 034953, 124532, 214731 |
| Ralts | 10 | Complete | 034229, 123812 |
| Rare Candy | 4 | Complete | 012927, 031138, 034229, 123812 |
| Red Card | 1 | Complete | 215749 |
| Riolu | 8 | Complete | 033529 |
| Rocky Helmet | 3 | Complete | 214731 |
| Rookidee | 3 | Complete | 215749 |
| Sabrina | 4 | Complete | 032857 |
| Serena | 2 | Complete | 032857 |
| Soothing Shore | 1 | Complete | 003547 |
| Stakataka | 2 | Complete | 020518 |
| Tapu Koko ex | 6 | Complete | 031138 |
| Teal Mask Ogerpon ex | 3 | Complete | 213625 |
| Team Rocket's Thieving Machine | 1 | Complete | 124532 |
| Team Rocket's Tinkatink | 1 | Complete | 020518 |
| Team Rocket's Tinkaton | 2 | Complete | 020518 |
| Team Rocket's Tinkatuff | 1 | Complete | 020518 |
| Tinkatink | 5 | Complete | 012140, 215749 |
| Togedemaru | 4 | Complete | 020518 |
| Vespiquen ex | 3 | Complete | 213625 |
| Wally | 2 | Complete | 012927 |
| Wiglett | 5 | Complete | 032023 |
| Wugtrio ex | 4 | Complete | 032023 |
| X Speed | 1 | Complete | 032023 |
| Zeraora | 5 | Complete | 012927/g2, 031138 |

97 opponent card names, all found in the engine's data, all Complete.

