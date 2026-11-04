# Lane N smoke: the 55 newly supported printings and the decks that hold them

**The list.** R6 S's own card_status (`rl/results/dual_type_seam_2026-10-23/r6_release/logs/card_status.json`, the file
behind `r6_release/logs/lane_r.log:13`) had 55 of the 260 new C1/SP1/P-C printings as Missing*: 15 MissingAbility, 31
MissingAttack, 2 MissingTool and 7 MissingTrainer. These are "the 55 unsupported printings" of `rl/strength/README.md:53`
and the printings R8-04 to R8-08 implement (RELEASE_NOTES §1). At the tip all 55 are playable: 51 Complete and 4
RulesUnverified (Ribombee C1 015 and C1 135, Jigglypuff C1 051 and C1 184). `check_decks.py` takes the list from that file,
so it is not typed by hand; the table below is its output (status at the tip from the built card_status of 63657e0a's
engine, `/home/dacz8976/dual_target/release/card_status`, sha256 a76a975b…).

**The decks** (`decks/`, the deck-file format of `decks/research/`: an `Energy:` line, then `N SET NNN` lines). Each is a
legal 20-card list: at least one Basic, no name more than twice, Energy-line types the Energy Zone can make, every Stage 1
or 2 with the Pokémon it evolves from, and every card Complete or RulesUnverified (`check_decks.py`: ALL DECKS OK).

- **a01-a09** hold the 55, every one in at least one deck (55 of 55). They play km3 v km3 and kx3 v km3 against
  `decks/screen/opponents/t-altaria.txt` (a public panel list, old cards only), 2 deals x 2 seats each.
- **b01-b06** are the rule-row and item 11 decks of coordinator-148 §2.6, played km3 v km3 only: b01 Darkrai ex A2 110
  with Sableye B3a 040 (R8-10b); b02 Iris B4b 212 with Haxorus B4b 176 and B4b 348 (R8-10c); b03 Mega Blastoise ex
  B1a 020 (R8-10d); b04 Starting Plains B2 154 with Machop B2 079 and Conkeldurr B4 089 (R8-10e); b05 Rapid Strike Urshifu
  B3 051 against b06, Snover A2 044 and Sealeo B4 039 (item 11). b01-b04 play t-altaria; b05 plays b06.

| deck | Energy | what it is for |
|---|---|---|
| a01-grass-honey | Grass | Venusaur x2 printings, Ribombee x2, Vespiquen, Sweet Honey x2, Abandoned Station |
| a02-grass-items | Grass | Sawsbuck, Amoonguss, Super Potion, Max Repel, Full Heal, Eviolite |
| a03-fire | Fire | Charizard x2, Raboot x2, Volcanion, Ceruledge x2 |
| a04-water | Water | Palkia x2, Dewgong x2, Frogadier x2 (and Super Potion) |
| a05-lightning | Lightning | Pawmot C1 050 and C1 142, Electrode, Light Ball on Pikachu ex A1 096 |
| a06-psychic-lunala | Psychic | Lunala C1 066 and C1 198, Jigglypuff x2, Deoxys C1 062 and P-C 003, Alakazam x2 |
| a07-psychic-promo-c | Psychic | Lunala P-C 008, Malamar P-C 005, Genome Converter Y with Mega Mewtwo Y ex P-C 002 |
| a08-eevee-colorless | Psychic, Darkness | Eevee, Espeon, Umbreon x2, Pidgey, Pidgeot, Porygon-Z |
| a09-fighting-metal | Fighting, Metal, Lightning | Pupitar x2, Whiscash, Melmetal x2, Pawmot C1 216 (and Eviolite) |
| b01-darkrai-sableye | Darkness | R8-10b: Nightmare Aura on a Jeweled Gift attach |
| b02-iris-haxorus | Fighting, Metal | R8-10c: Iris's extra point with the B4b Haxorus |
| b03-mega-blastoise | Water | R8-10d: Triple Bombardment with exactly 1 opposing Benched Pokémon |
| b04-starting-plains | Fighting | R8-10e: Shatter and Bedrock Breaker discarding Starting Plains |
| b05-urshifu | Water | item 11: Rapid Strike Urshifu's Double Type, played against b06 |
| b06-snover-sealeo | Water | item 11: Ice Shard (+30) and Frozen Splash (+70) against an Active Urshifu |

Not covered (no such card in the database): "Dewgong against Carefree Steps" (laptop-068:106, cited by lane_plan §2.7); no
card is named Carefree Steps in `engine/database.json`. Dewgong's Dual Blizzard is in a04.

| printing | name | R6 S status | tip status | deck(s) |
|---|---|---|---|---|
| C1 003 | Venusaur | MissingAbility | Complete | a01-grass-honey |
| C1 008 | Vespiquen | MissingAttack | Complete | a01-grass-honey |
| C1 010 | Sawsbuck | MissingAttack | Complete | a02-grass-items |
| C1 012 | Amoonguss | MissingAttack | Complete | a02-grass-items |
| C1 015 | Ribombee | MissingAbility | RulesUnverified | a01-grass-honey |
| C1 018 | Charizard | MissingAbility | Complete | a03-fire |
| C1 019 | Volcanion | MissingAttack | Complete | a03-fire |
| C1 023 | Raboot | MissingAbility | Complete | a03-fire |
| C1 028 | Ceruledge | MissingAttack | Complete | a03-fire |
| C1 033 | Dewgong | MissingAttack | Complete | a04-water |
| C1 038 | Palkia | MissingAttack | Complete | a04-water |
| C1 041 | Frogadier | MissingAbility | Complete | a04-water |
| C1 045 | Electrode | MissingAttack | Complete | a05-lightning |
| C1 050 | Pawmot | MissingAbility | Complete | a05-lightning |
| C1 051 | Jigglypuff | MissingAttack | RulesUnverified | a06-psychic-lunala |
| C1 055 | Alakazam | MissingAttack | Complete | a06-psychic-lunala |
| C1 060 | Espeon | MissingAttack | Complete | a08-eevee-colorless |
| C1 062 | Deoxys | MissingAttack | Complete | a06-psychic-lunala |
| C1 066 | Lunala | MissingAttack | Complete | a06-psychic-lunala |
| C1 076 | Pupitar | MissingAttack | Complete | a09-fighting-metal |
| C1 078 | Whiscash | MissingAttack | Complete | a09-fighting-metal |
| C1 084 | Umbreon | MissingAttack | Complete | a08-eevee-colorless |
| C1 097 | Melmetal | MissingAbility | Complete | a09-fighting-metal |
| C1 102 | Pidgey | MissingAttack | Complete | a08-eevee-colorless |
| C1 104 | Pidgeot | MissingAttack | Complete | a08-eevee-colorless |
| C1 107 | Eevee | MissingAttack | Complete | a08-eevee-colorless |
| C1 110 | Porygon-Z | MissingAttack | Complete | a08-eevee-colorless |
| C1 119 | Sweet Honey | MissingTrainer | Complete | a01-grass-honey |
| C1 120 | Super Potion | MissingTrainer | Complete | a02-grass-items, a04-water |
| C1 121 | Max Repel | MissingTrainer | Complete | a02-grass-items |
| C1 122 | Full Heal | MissingTrainer | Complete | a02-grass-items |
| C1 123 | Eviolite | MissingTool | Complete | a02-grass-items, a09-fighting-metal |
| C1 124 | Light Ball | MissingTool | Complete | a05-lightning |
| C1 131 | Abandoned Station | MissingTrainer | Complete | a01-grass-honey |
| C1 132 | Venusaur | MissingAbility | Complete | a01-grass-honey |
| C1 135 | Ribombee | MissingAbility | RulesUnverified | a01-grass-honey |
| C1 136 | Charizard | MissingAbility | Complete | a03-fire |
| C1 137 | Raboot | MissingAbility | Complete | a03-fire |
| C1 138 | Ceruledge | MissingAttack | Complete | a03-fire |
| C1 140 | Palkia | MissingAttack | Complete | a04-water |
| C1 141 | Frogadier | MissingAbility | Complete | a04-water |
| C1 142 | Pawmot | MissingAbility | Complete | a05-lightning |
| C1 146 | Pupitar | MissingAttack | Complete | a09-fighting-metal |
| C1 150 | Melmetal | MissingAbility | Complete | a09-fighting-metal |
| C1 152 | Sweet Honey | MissingTrainer | Complete | a01-grass-honey |
| C1 184 | Jigglypuff | MissingAttack | RulesUnverified | a06-psychic-lunala |
| C1 186 | Umbreon | MissingAttack | Complete | a08-eevee-colorless |
| C1 193 | Dewgong | MissingAttack | Complete | a04-water |
| C1 197 | Alakazam | MissingAttack | Complete | a06-psychic-lunala |
| C1 198 | Lunala | MissingAttack | Complete | a06-psychic-lunala |
| C1 216 | Pawmot | MissingAbility | Complete | a09-fighting-metal |
| P-C 003 | Deoxys | MissingAttack | Complete | a06-psychic-lunala |
| P-C 005 | Malamar | MissingAttack | Complete | a07-psychic-promo-c |
| P-C 008 | Lunala | MissingAttack | Complete | a07-psychic-promo-c |
| P-C 009 | Genome Converter Y | MissingTrainer | Complete | a07-psychic-promo-c |
