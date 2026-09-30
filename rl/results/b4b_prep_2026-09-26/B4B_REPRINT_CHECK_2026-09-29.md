# B4b reprint check (Sept 29, read-only; two Opus agents, the second an independent recheck)

Upstream deckgym-core main 9044ff6 ("B4b"), after 09e964f. **Answer: B4b is reprint-only.** All 429 B4b cards and 8 of 9 new promos are reprints with identical game text. The one new card is P-B 099 Mega Garchomp ex, an October promo, as RUN5's A5 said. Both agents agree; the verifier's corrections (commit count, name count, the engine caveat) are in its section and change nothing in the answer.

## Check

**B4b is reprint-only: yes.** Upstream's B4b commit (9044ff6) adds 438 cards. All 429 B4b cards are reprints with game text identical to an earlier printing. Eight of the nine new promos are reprints too. The one new card in the window is **P-B 099 Mega Garchomp ex**, as RUN5 said. I changed nothing, ran no games or builds, and did not push the fork.

**How I checked**
- **Commit range:** 09e964f..9044ff6 is only two commits. 09e964f is engine-only. 9044ff6 ("B4b") changes only `database.json`, `src/card_ids.rs` and `src/database.rs`. The six lines it removes from `database.rs` just move chunk boundaries.
- **What was added:** 4317 − 3879 = 438 new entries. No existing entry was changed or removed. 429 are "Deluxe Pack: Mega (B4b)", B4b 001–429, covering 240 distinct names. Nine are "Promo B", P-B 095–103.
- **What "same text" means:** a card counts as a reprint if everything except id, rarity and booster_pack is identical: name, stage, evolves-from, HP, type, ability, attacks (cost, name, damage, effect), weakness and retreat.
- **Compared against:**
  - Upstream's data before B4b (09e964f): 437 of 438 match exactly.
  - The repo's `lib/deckgym-database.json`, the file `lib/card.py` reads: the same 437 match. This file is identical to upstream's pre-B4b data (3879 entries, none different). It has no B4b ids, and `lib/card.py "Mega Garchomp ex"` finds nothing.
- **RUN5's five "new" cards:** all confirmed as reprints of the ids RUN5 named.
  - Meloetta B4b 111/309/405 = B2 070
  - Eevee B4b 183/353/408 = B1 184
  - Fidough B4b 117/312/406 = B3b 034
  - Copycat B4b 225/391/424 = B1 225
  - Elesa B4b 422 = B3b 066

**The only new card: P-B 099 Mega Garchomp ex** (Promo B, ◊◊◊◊)
- Stage 2, evolves from Gabite. 220 HP, Dragon type, no weakness, retreat 2 Colorless, no ability.
- Attack "Falling Edge": costs Water, Fighting, Colorless. Does 190 damage. "Discard 2 random Energy from this Pokémon."
- No earlier card has this name, so there is no text to compare.
- Its Gible (P-B 097) and Gabite (P-B 098) are reprints of B4a 052 and B4a 053.
- The effect text is already handled in both upstream's and the fork's `effect_mechanic_map.rs` as `SelfDiscardRandomEnergy{count:2}`. The same text is on Giratina A2a 061 and Rayquaza B4 119.

**Engine caveat (only matters if a deck list uses B4b ids):** at 9044ff6, upstream's engine doesn't recognise 89 of the new B4b ids. The code that plays those cards looks them up by card id, and B4b 001–429 added only the data.
- Affected cards: every B4b Trainer except Elegant Cape (Items, Supporters, Tools, Stadiums), Bellibolt ex 101, Mimikyu ex 115, Dragalge ex 148, Haxorus 176/348 and Meowth 180/352.
- Trainers fall through to "not implemented", so they can't be played.
- Earlier-id deck lists are unaffected. The fork can't read B4b ids at all, since its data has none.

**Non-card changes in 09e964f** ("Expose public agent observations and fix stale knockout promotions")

Two changes can alter play:
1. **Promotion to an emptied slot** (`src/actions/apply_action_helpers.rs`, in `handle_knockouts`): after knockouts, choices to promote a Pokémon into a now-empty slot are removed. Case fixed: a knockout removes an HP bonus, which knocks out a damaged Benched Pokémon after promotion choices were already queued. Before, promoting that empty slot could leave the Active Spot empty. The only "Each of your … gets +N HP" ability is Lilligant's ("Each of your [G] Pokémon gets +20 HP."). Test: `tests/hp_aura_promotion_test.rs`.
2. **Lethal knock-back** (`src/actions/apply_attack_action.rs`, in `knock_back_attack` and `coin_flip_knock_back_opponent_active`): if the hit knocks out the opponent's Active, the switch choice is no longer queued on top of the promotion. Before, the opponent chose a new Active twice. Affected attacks:
   - Hariyama Push Out, Grapploct Knock Back, Houndour Roar, Yamper Roar, Throh Circle Throw
   - Chinchou Luring Glow (the coin-flip version)
   - Test: `tests/knock_back_knockout_test.rs`.

The rest doesn't change play:
- **Serialisation:** `serde::Serialize` added to the mechanic types in `src/actions/abilities/mechanic.rs` and `src/actions/attacks/mechanic.rs`.
- **Deck and observation:** `Deck::energy_types()` in `src/deck.rs`; a new `src/state/observation.rs` (read-only public views and a redacted snapshot for bots); `PlayedCard::public_details` in `src/state/played_card.rs`; `src/state/mod.rs` exports it.
- **External bots:** `src/players/external_player.rs` gets an opt-in snapshot, Windows `cmd /D /S /C` support and single-line buffered writes, documented in `docs/bot-protocol.md`.

**The fork doesn't have either fix, and I couldn't test whether it already behaves correctly (no builds).**
- The fork's `engine/src` has neither upstream guard.
- It has its own `prune_stale_bench_activate_choices` (`engine/src/actions/apply_action_helpers.rs:1032`). That function skips frames where the Active Spot is empty.
- Its `knock_back_attack` (`engine/src/actions/apply_attack_action.rs:4952`) has no check for a lethal hit.

**Full table (438 cards; "REPRINT = …" lists every earlier printing with identical text)**
```
B4b 001 | Bulbasaur | REPRINT = B1a 001
B4b 002 | Ivysaur | REPRINT = B1a 002
B4b 003 | Mega Venusaur ex | REPRINT = B1a 004, B1a 076, B1a 083
B4b 004 | Caterpie | REPRINT = B3b 001, B3b 091
B4b 005 | Metapod | REPRINT = B3b 002, B3b 092
B4b 006 | Butterfree | REPRINT = B3b 003, B3b 093
B4b 007 | Scyther | REPRINT = B2b 001, B2b 087
B4b 008 | Mega Pinsir ex | REPRINT = B1 002, B1 251, B1 272
B4b 009 | Celebi | REPRINT = B3 004, B3 233, P-B 079
B4b 010 | Treecko | REPRINT = B3 005, B3 156, P-B 061
B4b 011 | Grovyle | REPRINT = B3 006, B3 157
B4b 012 | Mega Sceptile ex | REPRINT = B3 008, B3 180, B3 194, P-B 087
B4b 013 | Budew | REPRINT = B3 013, B3 159
B4b 014 | Combee | REPRINT = B4 010
B4b 015 | Vespiquen ex | REPRINT = B4 011, B4 180, B4 194
B4b 016 | Cottonee | REPRINT = B1 015, B3 205
B4b 017 | Whimsicott ex | REPRINT = B1 016, B1 252, B1 273, B3 225
B4b 018 | Petilil | REPRINT = B1 017
B4b 019 | Lilligant | REPRINT = B1 018, B1 329
B4b 020 | Durant | REPRINT = B3 018
B4b 021 | Sprigatito | REPRINT = B2a 001, B2a 116
B4b 022 | Floragato | REPRINT = B2a 002, B2a 117, P-B 069
B4b 023 | Meowscarada ex | REPRINT = B2a 003, B2a 100, B2a 110, B3a 104, P-B 063
B4b 024 | Smoliv | REPRINT = B2a 007
B4b 025 | Dolliv | REPRINT = B2a 008
B4b 026 | Arboliva | REPRINT = B2a 009, B2b 116
B4b 027 | Teal Mask Ogerpon | REPRINT = B4 019
B4b 028 | Teal Mask Ogerpon ex | REPRINT = B2 017, B2 180, B2 194
B4b 029 | Charmander | REPRINT = B2b 007, B2b 091
B4b 030 | Charmeleon | REPRINT = B2b 008, B2b 092
B4b 031 | Mega Charizard X ex | REPRINT = B2b 009, B2b 076, B2b 111
B4b 032 | Mega Charizard Y ex | REPRINT = B1a 014, B1a 077, B1a 087, B4a 105
B4b 033 | Growlithe | REPRINT = B3b 010, P-B 077
B4b 034 | Ponyta | REPRINT = B4 020, B4 160
B4b 035 | Rapidash ex | REPRINT = B1 031, B1 253, B1 274
B4b 036 | Cyndaquil | REPRINT = B4 024
B4b 037 | Quilava | REPRINT = B4 025, B4 161
B4b 038 | Typhlosion ex | REPRINT = B4 026, B4 181, B4 195
B4b 039 | Torchic | REPRINT = B1 033, B3 206, P-B 007
B4b 040 | Combusken | REPRINT = B1 034, B3 207
B4b 041 | Mega Blaziken ex | REPRINT = B1 036, B1 254, B1 284, B3 226
B4b 042 | Numel | REPRINT = B3 021
B4b 043 | Mega Camerupt ex | REPRINT = B3 023, B3 181, B3 195
B4b 044 | Victini | REPRINT = B3 025, P-B 049
B4b 045 | Blacephalon ex | REPRINT = B2 023, B2 181, B2 195, B4 224
B4b 046 | Fuecoco | REPRINT = B2a 016, B2a 094
B4b 047 | Crocalor | REPRINT = B2a 017
B4b 048 | Skeledirge | REPRINT = B2a 018
B4b 049 | Charcadet | REPRINT = B2a 019, B3a 095, P-B 035
B4b 050 | Armarouge ex | REPRINT = B2a 020, B2a 101, B2a 111, B3a 105
B4b 051 | Hearthflame Mask Ogerpon | REPRINT = B2 027
B4b 052 | Squirtle | REPRINT = B1a 017
B4b 053 | Wartortle | REPRINT = B1a 018
B4b 054 | Mega Blastoise ex | REPRINT = B1a 020, B1a 078, B1a 084
B4b 055 | Alolan Vulpix | REPRINT = B2 028, B4 204, P-B 032
B4b 056 | Alolan Ninetales ex | REPRINT = B2 029, B2 182, B2 196, B4 225
B4b 057 | Slowpoke | REPRINT = B2b 015, B2b 095, P-B 042
B4b 058 | Mega Slowbro ex | REPRINT = B2b 016, B2b 077, B2b 083, B2b 112
B4b 059 | Magikarp | REPRINT = B1 050, B1 232
B4b 060 | Mega Gyarados ex | REPRINT = B1 052, B1 255, B1 285, B3b 101
B4b 061 | Vaporeon ex | REPRINT = B3 037, B3 182, B3 196, B3b 102
B4b 062 | Mudkip | REPRINT = B2 033, B4 205
B4b 063 | Marshtomp | REPRINT = B2 034, B4 206
B4b 064 | Mega Swampert ex | REPRINT = B2 036, B2 183, B2 197, B4 226
B4b 065 | Carvanha | REPRINT = B4 034
B4b 066 | Mega Sharpedo ex | REPRINT = B4 035, B4 182, B4 196
B4b 067 | Wailmer | REPRINT = B4 036
B4b 068 | Wailord ex | REPRINT = B4 037, B4 183, B4 197
B4b 069 | Feebas | REPRINT = B3b 014
B4b 070 | Milotic ex | REPRINT = B3b 015, B3b 078, B3b 086
B4b 071 | Froakie | REPRINT = B1 071
B4b 072 | Frogadier | REPRINT = B1 072
B4b 073 | Greninja ex | REPRINT = B1 073, B1 256, B1 275, B3 227
B4b 074 | Sobble | REPRINT = B3 048, B3 203
B4b 075 | Drizzile | REPRINT = B3 049
B4b 076 | Inteleon | REPRINT = B3 050
B4b 077 | Iron Bundle ex | REPRINT = B3a 013, B3a 081, B3a 089
B4b 078 | Frigibax | REPRINT = B2a 034
B4b 079 | Arctibax | REPRINT = B2a 035
B4b 080 | Baxcalibur | REPRINT = B2a 036, B2a 130
B4b 081 | Chien-Pao ex | REPRINT = B2a 037, B2a 102, B2a 112, P-B 041
B4b 082 | Pikachu | REPRINT = B4 049, P-B 082
B4b 083 | Raichu | REPRINT = B4 050, B4 164, B4 232
B4b 084 | Magnemite | REPRINT = B1a 024
B4b 085 | Magneton | REPRINT = B1a 025
B4b 086 | Magnezone ex | REPRINT = B3 054, B3 183, B3 197
B4b 087 | Jolteon ex | REPRINT = B1 081, B1 257, B1 276, B3 228
B4b 088 | Mareep | REPRINT = B1 082, B3b 094, P-B 015
B4b 089 | Flaaffy | REPRINT = B1 083, B3b 095
B4b 090 | Mega Ampharos ex | REPRINT = B1 085, B1 258, B1 277, B3b 103
B4b 091 | Electrike | REPRINT = B2b 026, B2b 098
B4b 092 | Mega Manectric ex | REPRINT = B2b 027, B2b 078, B2b 084, B2b 113
B4b 093 | Rotom ex | REPRINT = B4 055, B4 184, B4 202
B4b 094 | Helioptile | REPRINT = B4 060
B4b 095 | Heliolisk | REPRINT = B4 061
B4b 096 | Dedenne ex | REPRINT = B3b 024, B3b 079, B3b 090
B4b 097 | Yamper | REPRINT = B3b 025
B4b 098 | Toxel | REPRINT = B2 054, B2 166, B4a 099
B4b 099 | Toxtricity ex | REPRINT = B2 055, B2 184, B2 198, B4a 106
B4b 100 | Tadbulb | REPRINT = B2 056, B3a 096
B4b 101 | Bellibolt ex | REPRINT = B2a 042, B2a 103, B2a 113, B3a 106
B4b 102 | Iron Thorns | REPRINT = B3a 018
B4b 103 | Miraidon ex | REPRINT = B3a 019, B3a 082, B3a 090
B4b 104 | Ralts | REPRINT = B4 071, B4 167
B4b 105 | Kirlia | REPRINT = B4 072
B4b 106 | Mega Gardevoir ex | REPRINT = B2 066, B2 185, B2 203, B4 227
B4b 107 | Mega Altaria ex | REPRINT = B1 102, B1 259, B1 286, B3a 107
B4b 108 | Wynaut | REPRINT = B4 074, B4 168
B4b 109 | Chingling | REPRINT = B1 109
B4b 110 | Mime Jr. | REPRINT = B4 068
B4b 111 | Meloetta | REPRINT = B2 070, B2 233, P-B 050
B4b 112 | Sylveon | REPRINT = B3b 030, B3b 073
B4b 113 | Klefki | REPRINT = B1 120, B1 330
B4b 114 | Mega Diancie ex | REPRINT = B3b 032, B3b 080, B3b 087
B4b 115 | Mimikyu ex | REPRINT = B2 073, B2 186, B2 199, B4a 107
B4b 116 | Indeedee ex | REPRINT = B1 121, B1 260, B1 278, B3b 104
B4b 117 | Fidough | REPRINT = B3b 034
B4b 118 | Bramblin | REPRINT = B3 072
B4b 119 | Brambleghast | REPRINT = B3 073, B3 167
B4b 120 | Flutter Mane ex | REPRINT = B3a 026, B3a 083, B3a 091
B4b 121 | Gimmighoul | REPRINT = B2a 054, B2a 096, B2a 122
B4b 122 | Onix | REPRINT = B1a 038, B3 211
B4b 123 | Hitmonchan ex | REPRINT = B1 124, B1 261, B1 279, B3 229
B4b 124 | Trapinch | REPRINT = B3 076
B4b 125 | Mega Lopunny ex | REPRINT = B1a 042, B1a 079, B1a 085, B4 228
B4b 126 | Riolu | REPRINT = B3 079, B3 169
B4b 127 | Mega Lucario ex | REPRINT = B3 081, B3 184, B3 204
B4b 128 | Mega Gallade ex | REPRINT = B4 084, B4 185, B4 198
B4b 129 | Roggenrola | REPRINT = B2 085, B4 213
B4b 130 | Boldore | REPRINT = B2 086, B4 214
B4b 131 | Gigalith ex | REPRINT = B2 087, B2 187, B2 200, B4 229
B4b 132 | Dwebble | REPRINT = B3 087
B4b 133 | Crustle ex | REPRINT = B3 088, B3 185, B3 198
B4b 134 | Rockruff | REPRINT = B3b 038
B4b 135 | Falinks | REPRINT = B2 092, B2 172, B4 215
B4b 136 | Koraidon ex | REPRINT = B3a 036, B3a 084, B3a 092
B4b 137 | Alolan Grimer | REPRINT = B2 096
B4b 138 | Alolan Muk | REPRINT = B2 097, B2 173
B4b 139 | Gastly | REPRINT = B2b 037, B2b 100, P-B 047
B4b 140 | Haunter | REPRINT = B2b 038, B2b 101
B4b 141 | Mega Gengar ex | REPRINT = B2b 039, B2b 079, B2b 114
B4b 142 | Mega Sableye ex | REPRINT = B3b 041, B3b 081, B3b 088
B4b 143 | Mega Absol ex | REPRINT = B1 151, B1 262, B1 280, B3 230, P-B 009
B4b 144 | Darkrai | REPRINT = B2b 040
B4b 145 | Zorua | REPRINT = B3 105, B3 174
B4b 146 | Zoroark ex | REPRINT = B3 106, B3 186, B3 199, B4 230
B4b 147 | Skrelp | REPRINT = B1 159, B3 218
B4b 148 | Dragalge ex | REPRINT = B1 160, B1 263, B1 281, B3 231
B4b 149 | Hoopa ex | REPRINT = B4 103, B4 186, B4 199
B4b 150 | Zarude | REPRINT = B3 114, P-B 060
B4b 151 | Bombirdier | REPRINT = B3 115, B3 234
B4b 152 | Roaring Moon | REPRINT = B3a 047, B3a 109
B4b 153 | Galarian Meowth | REPRINT = B2 110, B4 218
B4b 154 | Galarian Perrserker | REPRINT = B2 111, B2 177, B4 219
B4b 155 | Mega Steelix ex | REPRINT = B1a 052, B1a 080, B1a 086, B3 232
B4b 156 | Mega Scizor ex | REPRINT = B2b 047, B2b 080, B2b 115
B4b 157 | Mega Mawile ex | REPRINT = B2 113, B2 188, B2 201, B4a 108
B4b 158 | Beldum | REPRINT = B4 106, P-B 086
B4b 159 | Metang | REPRINT = B4 107
B4b 160 | Mega Metagross ex | REPRINT = B4 109, B4 187, B4 200
B4b 161 | Honedge | REPRINT = B1 170
B4b 162 | Doublade | REPRINT = B1 171
B4b 163 | Aegislash | REPRINT = B2 120
B4b 164 | Aegislash | REPRINT = B1 172, B1a 102
B4b 165 | Meltan | REPRINT = B1 173
B4b 166 | Melmetal ex | REPRINT = B1 174, B1 264, B1 282
B4b 167 | Corviknight ex | REPRINT = B3 124, B3 187, B3 200
B4b 168 | Gholdengo ex | REPRINT = B2a 078, B2a 104, B2a 114
B4b 169 | Dratini | REPRINT = B4 116
B4b 170 | Dragonair | REPRINT = B4 117, B4 175, B4 233
B4b 171 | Vibrava | REPRINT = B3 125
B4b 172 | Flygon ex | REPRINT = B3 126, B3 188, B3 201
B4b 173 | Mega Rayquaza ex | REPRINT = B4 120, B4 188, B4 203
B4b 174 | Axew | REPRINT = B2b 054, B2b 108
B4b 175 | Fraxure | REPRINT = B2b 055, B2b 109
B4b 176 | Haxorus | REPRINT = B2b 056, B2b 110, P-B 045
B4b 177 | Drampa | REPRINT = B4 124
B4b 178 | Rattata | REPRINT = B4 129, B4 220
B4b 179 | Raticate | REPRINT = B4 130, B4 178, B4 221
B4b 180 | Meowth | REPRINT = B2 124, B2 204
B4b 181 | Mega Kangaskhan ex | REPRINT = B2 127, B2 189, B2 202, B4 231
B4b 182 | Tauros ex | REPRINT = B1 183, B1 265, B1 283
B4b 183 | Eevee | REPRINT = B1 184, P-B 011, P-B 054
B4b 184 | Skitty | REPRINT = B1 193
B4b 185 | Delcatty | REPRINT = B1 194, B1 248
B4b 186 | Swablu | REPRINT = B1 196, B3a 102
B4b 187 | Buneary | REPRINT = B1a 062, B1a 075, B4 223, P-B 019
B4b 188 | Munchlax | REPRINT = B3b 054, B3b 105
B4b 189 | Lillipup | REPRINT = B3 137
B4b 190 | Mega Audino ex | REPRINT = B3 141, B3 189, B3 202
B4b 191 | Hisuian Zorua | REPRINT = B3b 059, P-B 076
B4b 192 | Hisuian Zoroark ex | REPRINT = B3b 060, B3b 082, B3b 089
B4b 193 | Ducklett | REPRINT = B4 140
B4b 194 | Swanna ex | REPRINT = B4 141, B4 189, B4 201
B4b 195 | Rookidee | REPRINT = B3 145
B4b 196 | Corvisquire | REPRINT = B3 146
B4b 197 | Terapagos ex | REPRINT = B3a 068, B3a 085, B3a 093
B4b 198 | Lucky Ice Pop | REPRINT = B2 145
B4b 199 | Electric Generator | REPRINT = B2a 086, B2a 131
B4b 200 | Order Pad | REPRINT = B4 145
B4b 201 | Quick-Grow Extract | REPRINT = B1a 067, B1a 103
B4b 202 | Field Blower | REPRINT = B3 147
B4b 203 | Flame Patch | REPRINT = B1 217, B1 331
B4b 204 | Deceptive Needle | REPRINT = B4 148
B4b 205 | Lucky Egg | REPRINT = B3 148
B4b 206 | Small Balloon | REPRINT = B3b 064, B3b 106
B4b 207 | Ancient Booster Energy Capsule | REPRINT = B3a 069
B4b 208 | Future Booster Energy Capsule | REPRINT = B3a 070
B4b 209 | Protective Poncho | REPRINT = B2 147, B2 234
B4b 210 | Metal Core Barrier | REPRINT = B2 148, B2b 117
B4b 211 | Elegant Cape | REPRINT = B3b 065
B4b 212 | Iris | REPRINT = B2b 067, B2b 081
B4b 213 | Juliana | REPRINT = B3a 071, B3a 086
B4b 214 | Diantha | REPRINT = B2 149, B2 190
B4b 215 | Calem | REPRINT = B2b 068, B2b 082
B4b 216 | Puppy-Loving Girl | REPRINT = B3b 067, B3b 084
B4b 217 | Korrina | REPRINT = B3 149, B3 190
B4b 218 | Clemont | REPRINT = B1a 068, B1a 081
B4b 219 | Serena | REPRINT = B1a 069, B1a 082
B4b 220 | May | REPRINT = B1 223, B1 268
B4b 221 | Skyla | REPRINT = B4 152, B4 192
B4b 222 | Arven | REPRINT = B2a 091, B2a 108, B2a 115
B4b 223 | Wallace | REPRINT = B3b 068, B3b 085
B4b 224 | Wally | REPRINT = B4 153, B4 193
B4b 225 | Copycat | REPRINT = B1 225, B1 270
B4b 226 | Lisia | REPRINT = B1 226, B1 271
B4b 227 | Fragrant Forest | REPRINT = B3 153
B4b 228 | Arena of Antiquity | REPRINT = B3 154
B4b 229 | Soothing Shore | REPRINT = B4 154
B4b 230 | Bounded Field | REPRINT = B3 155
B4b 231 | Mesagoza | REPRINT = B2a 093
B4b 232 | Training Area | REPRINT = B2 153
B4b 233 | Rainbow Cave | REPRINT = B4 155
B4b 234 | Hiking Trail | REPRINT = B2b 069
B4b 235 | Starting Plains | REPRINT = B2 154
B4b 236 | Peculiar Plaza | REPRINT = B2 155
B4b 237 | Bulbasaur | REPRINT = B1a 001
B4b 238 | Ivysaur | REPRINT = B1a 002
B4b 239 | Caterpie | REPRINT = B3b 001, B3b 091
B4b 240 | Metapod | REPRINT = B3b 002, B3b 092
B4b 241 | Butterfree | REPRINT = B3b 003, B3b 093
B4b 242 | Scyther | REPRINT = B2b 001, B2b 087
B4b 243 | Celebi | REPRINT = B3 004, B3 233, P-B 079
B4b 244 | Treecko | REPRINT = B3 005, B3 156, P-B 061
B4b 245 | Grovyle | REPRINT = B3 006, B3 157
B4b 246 | Budew | REPRINT = B3 013, B3 159
B4b 247 | Combee | REPRINT = B4 010
B4b 248 | Cottonee | REPRINT = B1 015, B3 205
B4b 249 | Petilil | REPRINT = B1 017
B4b 250 | Lilligant | REPRINT = B1 018, B1 329
B4b 251 | Durant | REPRINT = B3 018
B4b 252 | Sprigatito | REPRINT = B2a 001, B2a 116
B4b 253 | Floragato | REPRINT = B2a 002, B2a 117, P-B 069
B4b 254 | Smoliv | REPRINT = B2a 007
B4b 255 | Dolliv | REPRINT = B2a 008
B4b 256 | Arboliva | REPRINT = B2a 009, B2b 116
B4b 257 | Teal Mask Ogerpon | REPRINT = B4 019
B4b 258 | Charmander | REPRINT = B2b 007, B2b 091
B4b 259 | Charmeleon | REPRINT = B2b 008, B2b 092
B4b 260 | Growlithe | REPRINT = B3b 010, P-B 077
B4b 261 | Ponyta | REPRINT = B4 020, B4 160
B4b 262 | Cyndaquil | REPRINT = B4 024
B4b 263 | Quilava | REPRINT = B4 025, B4 161
B4b 264 | Torchic | REPRINT = B1 033, B3 206, P-B 007
B4b 265 | Combusken | REPRINT = B1 034, B3 207
B4b 266 | Numel | REPRINT = B3 021
B4b 267 | Victini | REPRINT = B3 025, P-B 049
B4b 268 | Fuecoco | REPRINT = B2a 016, B2a 094
B4b 269 | Crocalor | REPRINT = B2a 017
B4b 270 | Skeledirge | REPRINT = B2a 018
B4b 271 | Charcadet | REPRINT = B2a 019, B3a 095, P-B 035
B4b 272 | Hearthflame Mask Ogerpon | REPRINT = B2 027
B4b 273 | Squirtle | REPRINT = B1a 017
B4b 274 | Wartortle | REPRINT = B1a 018
B4b 275 | Alolan Vulpix | REPRINT = B2 028, B4 204, P-B 032
B4b 276 | Slowpoke | REPRINT = B2b 015, B2b 095, P-B 042
B4b 277 | Magikarp | REPRINT = B1 050, B1 232
B4b 278 | Mudkip | REPRINT = B2 033, B4 205
B4b 279 | Marshtomp | REPRINT = B2 034, B4 206
B4b 280 | Carvanha | REPRINT = B4 034
B4b 281 | Wailmer | REPRINT = B4 036
B4b 282 | Feebas | REPRINT = B3b 014
B4b 283 | Froakie | REPRINT = B1 071
B4b 284 | Frogadier | REPRINT = B1 072
B4b 285 | Sobble | REPRINT = B3 048, B3 203
B4b 286 | Drizzile | REPRINT = B3 049
B4b 287 | Inteleon | REPRINT = B3 050
B4b 288 | Frigibax | REPRINT = B2a 034
B4b 289 | Arctibax | REPRINT = B2a 035
B4b 290 | Baxcalibur | REPRINT = B2a 036, B2a 130
B4b 291 | Pikachu | REPRINT = B4 049, P-B 082
B4b 292 | Raichu | REPRINT = B4 050, B4 164, B4 232
B4b 293 | Magnemite | REPRINT = B1a 024
B4b 294 | Magneton | REPRINT = B1a 025
B4b 295 | Mareep | REPRINT = B1 082, B3b 094, P-B 015
B4b 296 | Flaaffy | REPRINT = B1 083, B3b 095
B4b 297 | Electrike | REPRINT = B2b 026, B2b 098
B4b 298 | Helioptile | REPRINT = B4 060
B4b 299 | Heliolisk | REPRINT = B4 061
B4b 300 | Yamper | REPRINT = B3b 025
B4b 301 | Toxel | REPRINT = B2 054, B2 166, B4a 099
B4b 302 | Tadbulb | REPRINT = B2 056, B3a 096
B4b 303 | Iron Thorns | REPRINT = B3a 018
B4b 304 | Ralts | REPRINT = B4 071, B4 167
B4b 305 | Kirlia | REPRINT = B4 072
B4b 306 | Wynaut | REPRINT = B4 074, B4 168
B4b 307 | Chingling | REPRINT = B1 109
B4b 308 | Mime Jr. | REPRINT = B4 068
B4b 309 | Meloetta | REPRINT = B2 070, B2 233, P-B 050
B4b 310 | Sylveon | REPRINT = B3b 030, B3b 073
B4b 311 | Klefki | REPRINT = B1 120, B1 330
B4b 312 | Fidough | REPRINT = B3b 034
B4b 313 | Bramblin | REPRINT = B3 072
B4b 314 | Brambleghast | REPRINT = B3 073, B3 167
B4b 315 | Gimmighoul | REPRINT = B2a 054, B2a 096, B2a 122
B4b 316 | Onix | REPRINT = B1a 038, B3 211
B4b 317 | Trapinch | REPRINT = B3 076
B4b 318 | Riolu | REPRINT = B3 079, B3 169
B4b 319 | Roggenrola | REPRINT = B2 085, B4 213
B4b 320 | Boldore | REPRINT = B2 086, B4 214
B4b 321 | Dwebble | REPRINT = B3 087
B4b 322 | Rockruff | REPRINT = B3b 038
B4b 323 | Falinks | REPRINT = B2 092, B2 172, B4 215
B4b 324 | Alolan Grimer | REPRINT = B2 096
B4b 325 | Alolan Muk | REPRINT = B2 097, B2 173
B4b 326 | Gastly | REPRINT = B2b 037, B2b 100, P-B 047
B4b 327 | Haunter | REPRINT = B2b 038, B2b 101
B4b 328 | Darkrai | REPRINT = B2b 040
B4b 329 | Zorua | REPRINT = B3 105, B3 174
B4b 330 | Skrelp | REPRINT = B1 159, B3 218
B4b 331 | Zarude | REPRINT = B3 114, P-B 060
B4b 332 | Bombirdier | REPRINT = B3 115, B3 234
B4b 333 | Roaring Moon | REPRINT = B3a 047, B3a 109
B4b 334 | Galarian Meowth | REPRINT = B2 110, B4 218
B4b 335 | Galarian Perrserker | REPRINT = B2 111, B2 177, B4 219
B4b 336 | Beldum | REPRINT = B4 106, P-B 086
B4b 337 | Metang | REPRINT = B4 107
B4b 338 | Honedge | REPRINT = B1 170
B4b 339 | Doublade | REPRINT = B1 171
B4b 340 | Aegislash | REPRINT = B2 120
B4b 341 | Aegislash | REPRINT = B1 172, B1a 102
B4b 342 | Meltan | REPRINT = B1 173
B4b 343 | Dratini | REPRINT = B4 116
B4b 344 | Dragonair | REPRINT = B4 117, B4 175, B4 233
B4b 345 | Vibrava | REPRINT = B3 125
B4b 346 | Axew | REPRINT = B2b 054, B2b 108
B4b 347 | Fraxure | REPRINT = B2b 055, B2b 109
B4b 348 | Haxorus | REPRINT = B2b 056, B2b 110, P-B 045
B4b 349 | Drampa | REPRINT = B4 124
B4b 350 | Rattata | REPRINT = B4 129, B4 220
B4b 351 | Raticate | REPRINT = B4 130, B4 178, B4 221
B4b 352 | Meowth | REPRINT = B2 124, B2 204
B4b 353 | Eevee | REPRINT = B1 184, P-B 011, P-B 054
B4b 354 | Skitty | REPRINT = B1 193
B4b 355 | Delcatty | REPRINT = B1 194, B1 248
B4b 356 | Swablu | REPRINT = B1 196, B3a 102
B4b 357 | Buneary | REPRINT = B1a 062, B1a 075, B4 223, P-B 019
B4b 358 | Munchlax | REPRINT = B3b 054, B3b 105
B4b 359 | Lillipup | REPRINT = B3 137
B4b 360 | Hisuian Zorua | REPRINT = B3b 059, P-B 076
B4b 361 | Ducklett | REPRINT = B4 140
B4b 362 | Rookidee | REPRINT = B3 145
B4b 363 | Corvisquire | REPRINT = B3 146
B4b 364 | Lucky Ice Pop | REPRINT = B2 145
B4b 365 | Electric Generator | REPRINT = B2a 086, B2a 131
B4b 366 | Order Pad | REPRINT = B4 145
B4b 367 | Quick-Grow Extract | REPRINT = B1a 067, B1a 103
B4b 368 | Field Blower | REPRINT = B3 147
B4b 369 | Flame Patch | REPRINT = B1 217, B1 331
B4b 370 | Deceptive Needle | REPRINT = B4 148
B4b 371 | Lucky Egg | REPRINT = B3 148
B4b 372 | Small Balloon | REPRINT = B3b 064, B3b 106
B4b 373 | Ancient Booster Energy Capsule | REPRINT = B3a 069
B4b 374 | Future Booster Energy Capsule | REPRINT = B3a 070
B4b 375 | Protective Poncho | REPRINT = B2 147, B2 234
B4b 376 | Metal Core Barrier | REPRINT = B2 148, B2b 117
B4b 377 | Elegant Cape | REPRINT = B3b 065
B4b 378 | Iris | REPRINT = B2b 067, B2b 081
B4b 379 | Juliana | REPRINT = B3a 071, B3a 086
B4b 380 | Diantha | REPRINT = B2 149, B2 190
B4b 381 | Calem | REPRINT = B2b 068, B2b 082
B4b 382 | Puppy-Loving Girl | REPRINT = B3b 067, B3b 084
B4b 383 | Korrina | REPRINT = B3 149, B3 190
B4b 384 | Clemont | REPRINT = B1a 068, B1a 081
B4b 385 | Serena | REPRINT = B1a 069, B1a 082
B4b 386 | May | REPRINT = B1 223, B1 268
B4b 387 | Skyla | REPRINT = B4 152, B4 192
B4b 388 | Arven | REPRINT = B2a 091, B2a 108, B2a 115
B4b 389 | Wallace | REPRINT = B3b 068, B3b 085
B4b 390 | Wally | REPRINT = B4 153, B4 193
B4b 391 | Copycat | REPRINT = B1 225, B1 270
B4b 392 | Lisia | REPRINT = B1 226, B1 271
B4b 393 | Fragrant Forest | REPRINT = B3 153
B4b 394 | Arena of Antiquity | REPRINT = B3 154
B4b 395 | Soothing Shore | REPRINT = B4 154
B4b 396 | Bounded Field | REPRINT = B3 155
B4b 397 | Mesagoza | REPRINT = B2a 093
B4b 398 | Training Area | REPRINT = B2 153
B4b 399 | Rainbow Cave | REPRINT = B4 155
B4b 400 | Hiking Trail | REPRINT = B2b 069
B4b 401 | Starting Plains | REPRINT = B2 154
B4b 402 | Peculiar Plaza | REPRINT = B2 155
B4b 403 | Charmeleon | REPRINT = B2b 008, B2b 092
B4b 404 | Baxcalibur | REPRINT = B2a 036, B2a 130
B4b 405 | Meloetta | REPRINT = B2 070, B2 233, P-B 050
B4b 406 | Fidough | REPRINT = B3b 034
B4b 407 | Dratini | REPRINT = B4 116
B4b 408 | Eevee | REPRINT = B1 184, P-B 011, P-B 054
B4b 409 | Mega Venusaur ex | REPRINT = B1a 004, B1a 076, B1a 083
B4b 410 | Mega Sceptile ex | REPRINT = B3 008, B3 180, B3 194, P-B 087
B4b 411 | Mega Charizard X ex | REPRINT = B2b 009, B2b 076, B2b 111
B4b 412 | Mega Charizard Y ex | REPRINT = B1a 014, B1a 077, B1a 087, B4a 105
B4b 413 | Mega Blaziken ex | REPRINT = B1 036, B1 254, B1 284, B3 226
B4b 414 | Mega Blastoise ex | REPRINT = B1a 020, B1a 078, B1a 084
B4b 415 | Mega Gyarados ex | REPRINT = B1 052, B1 255, B1 285, B3b 101
B4b 416 | Mega Gardevoir ex | REPRINT = B2 066, B2 185, B2 203, B4 227
B4b 417 | Mega Altaria ex | REPRINT = B1 102, B1 259, B1 286, B3a 107
B4b 418 | Mega Lucario ex | REPRINT = B3 081, B3 184, B3 204
B4b 419 | Mega Gengar ex | REPRINT = B2b 039, B2b 079, B2b 114
B4b 420 | Mega Rayquaza ex | REPRINT = B4 120, B4 188, B4 203
B4b 421 | Iris | REPRINT = B2b 067, B2b 081
B4b 422 | Elesa | REPRINT = B3b 066, B3b 083
B4b 423 | Arven | REPRINT = B2a 091, B2a 108, B2a 115
B4b 424 | Copycat | REPRINT = B1 225, B1 270
B4b 425 | Mega Charizard X ex | REPRINT = B2b 009, B2b 076, B2b 111
B4b 426 | Dedenne ex | REPRINT = B3b 024, B3b 079, B3b 090
B4b 427 | Mega Diancie ex | REPRINT = B3b 032, B3b 080, B3b 087
B4b 428 | Miraidon ex | REPRINT = B3a 019, B3a 082, B3a 090
B4b 429 | Koraidon ex | REPRINT = B3a 036, B3a 084, B3a 092
P-B 095 | Darkrai | REPRINT = B2b 040
P-B 096 | Falinks | REPRINT = B2 092, B2 172, B4 215
P-B 097 | Gible | REPRINT = B4a 052
P-B 098 | Gabite | REPRINT = B4a 053
P-B 099 | Mega Garchomp ex | NEW CARD (no earlier printing; not in lib DB)
P-B 100 | Delcatty | REPRINT = B4 135
P-B 101 | Charmander | REPRINT = B2b 007, B2b 091
P-B 102 | Drampa | REPRINT = B4 124
P-B 103 | Pikachu ex | REPRINT = A2b 022, A2b 082, A2b 092, A4b 132, B1 321
```

Files are in `C:\Users\dacz8\AppData\Local\Temp\claude\C--Users-dacz8-Projects\1b119d13-736d-4588-ba63-0e9ef1756970\scratchpad\wf_b4b\checker\`:
- `table.tsv`: the full table with rarity and kind
- `rows.json`: every new card's full text
- `wire_out.txt`: the list of B4b ids the engine doesn't recognise
- `cmp.py`, `wire.py`: the scripts that did the comparison

## Independent recheck

**Verifier result: I agree. B4b is reprint-only. The only new card is P-B 099 Mega Garchomp ex.** I found two small wording errors in the checker's summary and a real error in its engine caveat. None of them changes the answer.

**How I checked (my own scripts, read-only)**
- **Commit:** 9044ff6 has one parent, 09e964f. It changes only `database.json`, `src/card_ids.rs` and `src/database.rs`. The lines it removes from `database.rs` are just the old `populate_database_chunk_29/30` boundaries. `card_ids.rs` loses no lines.
- **What was added:** upstream's data goes from 3879 to 4317 entries. 438 are added, none removed, none changed.
  - 429 are "Deluxe Pack: Mega (B4b)", ids B4b 001–429 with no gaps.
  - 9 are "Promo B (P-B)", P-B 095–103: Darkrai, Falinks, Gible, Gabite, Mega Garchomp ex, Delcatty, Charmander, Drampa, Pikachu ex.
- **What "same text" means:** everything except id, rarity and booster_pack must match exactly, plus the card kind (Pokémon or Trainer).
- **Result:** 437 of 438 match an earlier printing in upstream's pre-B4b data. Every B4b card name appeared before B4b.
- **The repo's copy:** `lib/deckgym-database.json` is identical to upstream's pre-B4b `database.json` (same ids, same entries, same order).
- **`lib/card.py`:** "Mega Garchomp ex" returns 0 printings. B2 070 Meloetta, B3b 066 Elesa and B4a 053 Gabite show the expected text.
- **RUN5's five "new" cards:** all are reprints of the ids RUN5 named.
  - Meloetta B4b 111/309/405 = B2 070
  - Eevee B4b 183/353/408 = B1 184
  - Fidough B4b 117/312/406 = B3b 034
  - Copycat B4b 225/391/424 = B1 225
  - Elesa B4b 422 = B3b 066
- **Checker's table:** its rows B4b 001–131 match mine exactly, including every earlier-printing id. Rows 132 onward were cut off in what I was given. My script still covers all 438 entries, and every one except P-B 099 is a reprint.
- **Promos:** 8 of 9 are reprints. Gible = B4a 052, Gabite = B4a 053.
- **Mega Garchomp ex (P-B 099):** Stage 2 from Gabite, 220 HP, Dragon, no weakness, retreat 2. Falling Edge costs Water, Fighting, Colorless and does 190: "Discard 2 random Energy from this Pokémon." Earlier names only include "Garchomp" and "Garchomp ex". The effect text is already in upstream's and the fork's `effect_mechanic_map.rs`. The same text is on A2a 061 and B4 119.

**Disagreements**
1. **Commit count (wording only):** "09e964f..9044ff6 is only two commits" is wrong. That range holds one commit, 9044ff6. The two commits after the fork's last data sync are 09e964f and 9044ff6 (ca4b67f..9044ff6).
2. **Name count (small miscount):** "429 are B4b … covering 240 distinct names" is wrong. The 429 B4b cards have 236 distinct names. 240 is the count across all 438 added cards, promos included.
3. **Engine caveat (the real error):** the checker's 89 matches a simple count: B4b ids that aren't referenced in upstream's code while an earlier printing's id is. That count overstates the problem.
   - **Tools and Stadiums work.** Upstream matches them by effect text, not card id: `is_tool_effect_implemented`, `has_tool`/`tool_position` in `src/tools.rs`, and `is_stadium_effect_implemented`/`has_stadium` in `src/stadiums.rs`. All 16 B4b Tool entries (8 names) and all 20 Stadium entries (10 names) are reprints of implemented ones, so they should play. Elegant Cape isn't special. Only Items (12) and Supporters (34) go through the id `match` in `trainer_move_generation_implementation`, which returns `None` for unknown ids. After that, `move_generation/mod.rs` calls `.expect("Trainer card not implemented")`, so it panics rather than just skipping the card.
   - **Three of the seven Pokémon are false alarms.** The only references to their earlier ids are inside test code (`#[cfg(test)]`):
     - Bellibolt ex: `apply_attack_action.rs:6998`
     - Mimikyu ex: `apply_action_helpers.rs:1133`
     - Meowth: `attack_outcome.rs:734` (B2 124)
   - **The real Pokémon gaps are three cards:** Dragalge ex B4b 148 (`hooks/counterattack.rs:48-50`, checked by id) and Haxorus B4b 176/348 (`apply_action_helpers.rs:773`, checked by id).
   - None of this matters unless a deck list uses B4b ids.

I didn't re-check the checker's notes on the 09e964f changes or its claims about the fork's engine. I changed nothing and ran no games or builds.

On your question "Can't you push the fork?": no, not from this job. I was limited to read-only checks, and pushing publishes to a public repo, so it needs your clear yes first. That call belongs to the main session.

My scripts and full table are in `C:\Users\dacz8\AppData\Local\Temp\claude\C--Users-dacz8-Projects\1b119d13-736d-4588-ba63-0e9ef1756970\scratchpad\wf_b4b\verifier\`:
- `verifier_table.txt` (all 438 cards with verdicts)
- `verify.py`
- `verify2.sh`
- `engine_ids.py`
