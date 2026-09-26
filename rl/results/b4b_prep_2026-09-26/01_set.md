# B4b: what it is (research note, 2026-09-26)

Scope: plan item A5 (B4b as a data refresh plus a card-effect pass). This note establishes the set. It does not touch the engine.
Checked on the night of 2026-09-25/26, three to four days before release. Everything marked **unverified** should be re-checked
against the Limitless database once the set is live (https://pocket.limitlesstcg.com/cards/B4b returned HTTP 404 on 2026-09-26).

## Bottom line

- **Name and code:** "Deluxe Pack: Mega", set code **B4b** (Japanese: ハイクラスパックMEGA). Sources: official
  https://www.pokemon.com/us/news/pokemon-tcg-pocket-deluxe-pack-mega-coming-soon ; https://www.pokemon-zone.com/sets/b4b/ ;
  https://game8.co/games/Pokemon-TCG-Pocket/archives/625370 ; https://gamewith.jp/pokemon-tcg-pocket/578648
- **Release:** Tuesday **September 29, 2026, 6:00 p.m. PDT** (official page above) = Wednesday September 30, 01:00 UTC
  (https://ptcgpocket.gg/b4b/) = September 30, 10:00 JST (GameWith). Available for one month, through October 28/29
  (https://noisypixel.net/pokemon-tcg-pocket-deluxe-pack-mega-community-decks/ ; https://www.thegamer.com/pokemon-tcg-pocket-deluxe-pack-mega-every-card-confirmed/).
  C1 (new series) follows on **October 28, 2026** (https://www.pokemon-zone.com/schedule/upcoming/).
- **What it is:** a **reprint-only** set, the B-series counterpart of last year's A4b "Deluxe Pack: ex". Official wording: it
  "features many cards introduced in previous expansions, from Mega Rising to Ruler of the Skies, including reissues of every
  ♦♦♦♦ card from those expansions", plus "parallel foil cards or cards with awesome new artwork"; four-card packs with one
  Pokémon ex guaranteed (official page above). pokemon-zone: "This one-pack set will feature only reprints from previous sets
  of the B series". GameWith (Japanese), explicitly: 新規性能のカードはなし, "no cards with new performance; all cards are
  reprints or same-performance alternate illustrations; there are no completely new cards" (https://gamewith.jp/pokemon-tcg-pocket/578648).
- **Coverage:** B1 Mega Rising through B4 Ruler of the Skies. **B4a Team Rocket's Ambition is excluded** (GameWith:
  「ロケット団の野望」カードは排出なし). Sportskeeda's phrase "through Team Rocket's Ambition" contradicts the official page and
  GameWith; treat it as wrong.
- **Total card count: unverified.** No source had published a count as of 2026-09-26 (Game8, Dexerto, TheGamer, Serebii,
  pokemon-zone all say not confirmed). Precedent: A4b had **379** cards = 353 regular + 26 secret (23 ☆ + 1 ♛ + 2 ✵), per
  https://www.serebii.net/tcgpocket/deluxepackex/ and https://www.pokemon-zone.com/sets/a4b/ and Limitless
  https://pocket.limitlesstcg.com/cards/A4b. Expect the same order of magnitude.
- **Genuinely new card text in B4b: none.** Zero new Pokémon, Trainers or Tools. The five cards the earlier laptop note called
  "new" (Meloetta, Eevee, Fidough, Copycat, Elesa) are **new-artwork reprints** of existing B-series printings with identical
  text (table below; the Japanese text on GameWith pins each one to a specific existing printing).
- **One genuinely new card is arriving in the same window, but not in B4b:** **Mega Garchomp ex**, in **Promo-B Series Vol. 13**,
  from a solo-battle Drop Event in mid-to-late October 2026 (official page; pokemon-zone; GameWith
  https://gamewith.jp/pokemon-tcg-pocket/578652: メガガブリアスexは収録カードではなく...完全新規カード). It is not in the fork's
  database. Details in its own section below.

### Correction to the earlier laptop note

The note said B4b is "Deluxe Pack: Mega, mostly reprints plus about five new cards (Meloetta, Eevee, Fidough, Copycat, Elesa)".
Name and "mostly reprints" are right. "About five new cards" is wrong: those five are new *illustrations* (☆ and ☆☆ rarities)
of cards already in the game and already in the fork's database and engine. I could not find that note in the repo (a grep for
"Fidough" across *.md returned nothing), so this correction is against the task text, not a file.

## Precedent check inside the fork's own data: A4b

Every one of the 379 A4b entries in `lib/deckgym-database.json` has text identical (name, HP, type, stage, weakness, retreat,
ability, attacks) to a non-A4b printing: 0 of 379 differ (checked by script on 2026-09-26 over
`C:\Users\dacz8\Projects\Pocket Deck Sim\PocketDeckSim\lib\deckgym-database.json`, comparing all fields except id, rarity and
booster_pack). That is what "reprint-only" looks like in the data, and it is the expected result for B4b.

## What the fork already holds

- `lib/deckgym-database.json` and `engine/database.json` hold the same 3,879 card IDs (byte-different formatting, identical ID
  sets; checked 2026-09-26). Sets present: A1..A4b, B1..B4a, P-A (117), P-B (94). No B4b, no Promo-B Vol. 13.
- `engine/database.json` is the input to `engine/src/bin/card_enum_generator.rs`, which generates `engine/src/card_ids.rs` and
  `engine/src/database.rs`. New printings of existing cards are registered in the mechanic maps as aliases of the earlier
  printing, e.g. `CardId::B1225Copycat | CardId::B1270Copycat` in `engine/src/actions/apply_trainer_action.rs:236` and
  `CardId::B3b066Elesa | CardId::B3b083Elesa` at line 304. B4b will be more of the same.
- The B1..B4 ◊◊◊◊ pool that the official notice says is reissued in full: **70 distinct cards** in the fork database (all ex;
  list in the table below). B4a's six ◊◊◊◊ (Team Rocket's Articuno/Moltres/Raticate/Slowking/Weezing/Zapdos ex) are not
  in scope per GameWith.

## Sources used (and what each gave)

| Source | URL | Gave |
|---|---|---|
| Official Pokémon news | https://www.pokemon.com/us/news/pokemon-tcg-pocket-deluxe-pack-mega-coming-soon | date/time, "every ♦♦♦♦" reissue, new art + parallel foil, 4-card packs, events incl. Mega Garchomp ex Drop Event |
| Limitless set index | https://pocket.limitlesstcg.com/cards | lists sets through B4a (110 cards, 27 Aug 26); no B4b entry |
| Limitless B4b | https://pocket.limitlesstcg.com/cards/B4b | HTTP 404 on 2026-09-26 |
| Limitless A4b | https://pocket.limitlesstcg.com/cards/A4b | A4b = 379 cards, 30 Sep 25 |
| pokemon-zone B4b | https://www.pokemon-zone.com/sets/b4b/ | "only reprints", 12 spoiler cards (10 set + 2 promo), events, parallel foil for ◊◊◊ and lower |
| pokemon-zone A4b | https://www.pokemon-zone.com/sets/a4b/ | A4b structure: 353 ◊ + 23 ☆ + 1 ♛ + 2 ✵ = 379 |
| pokemon-zone schedule | https://www.pokemon-zone.com/schedule/upcoming/ | B4b Sep 29, C1 Oct 28, 2026 |
| Serebii B4b | https://www.serebii.net/tcgpocket/deluxepackmega/ | set list table still empty; 13 preview cards; says "some new cards and alternate arts" (loose wording; contradicted by GameWith and official) |
| Serebii A4b | https://www.serebii.net/tcgpocket/deluxepackex/ | 379 = 353 normal + 26 secret |
| GameWith list (JP) | https://gamewith.jp/pokemon-tcg-pocket/578648 | full Japanese text of all 10 new-art cards, the 13 parallel-foil cards, "no new-performance cards", B4a excluded, ♦4 guaranteed |
| GameWith card (JP) | https://gamewith.jp/pokemon-tcg-pocket/578652 | Mega Garchomp ex: Stage 2, Dragon, Mega ex, HP 220, Falling Edge, discard 2 random Energy; Promo-B Vol. 13 |
| pokemon-zone spoiler image | https://media.pokemon-zone.com/spoilers/images/Deluxe-Pack-Mega-Mega-Garchomp-ex-Promo-B.webp | card image read in browser: HP 220, Falling Edge **190**, "Discard 2 random Energy from this Pokémon." |
| Game8 | https://game8.co/games/Pokemon-TCG-Pocket/archives/625370 | rarities of the 10 new-art cards (five Mega ex ☆☆, Copycat/Elesa ☆☆, Meloetta/Eevee/Fidough ☆) |
| TheGamer | https://www.thegamer.com/pokemon-tcg-pocket-deluxe-pack-mega-every-card-confirmed/ | ten named ◊◊◊◊ ex returning; ◊◊◊ Roaring Moon, Chingling; ◊◊ Charmeleon, Dragonair, Arena of Antiquity, Ancient Booster Energy Capsule |
| Dexerto | https://www.dexerto.com/pokemon/pokemon-tcg-pocket-deluxe-pack-mega-cards-set-3412237/ | count not confirmed; collector-oriented |
| Nintendo Life | https://www.nintendolife.com/news/2026/09/pokemon-tcg-pockets-next-expansion-has-a-guaranteed-rare-in-every-pack | reissued cards sort into their original expansion in the app |
| Insider Gaming | https://insider-gaming.com/pokemon-tcg-pockets-new-deluxe-pack-mega-set-brings-b-series-to-a-close/ | primarily reprints; full list not yet out |
| Pokémon GO Hub | https://pokemongohub.net/post/tcg-pocket/pokemon-tcg-pocket-deluxe-pack-mega-announced/ | "reprint collection, not containing new cards" |
| PocketMonsters.net | https://pocketmonsters.net/news/9563 | same as official; no Mega Garchomp ex stats |
| NoisyPixel | https://noisypixel.net/pokemon-tcg-pocket-deluxe-pack-mega-community-decks/ | Sep 29 through Oct 28; Drop Event mid-to-late October |
| ptcgpocket.gg | https://ptcgpocket.gg/b4b/ | Sep 30 01:00 UTC; no list |
| Blocked for automated reading | https://www.pokebeach.com/2026/09/deluxe-pack-mega-annual-special-set-to-release-in-pocket (403), https://www.sportskeeda.com/pokemon/pokemon-tcg-pocket-deluxe-pack-mega-b4b-all-revealed-cards-types-rarities (405), https://bulbagarden.net/threads/...311660/ (403) | search snippets only |

Local files: `lib/deckgym-database.json` (via `python lib/card.py`), `engine/database.json`, `engine/src/bin/card_enum_generator.rs`,
`engine/src/actions/apply_trainer_action.rs`, `engine/src/actions/effect_mechanic_map.rs`, `engine/src/hooks/core.rs`,
`engine/src/move_generation/mod.rs`, `engine/src/stadiums.rs`, `engine/UPSTREAM.md` (all under `C:\Users\dacz8\Projects\Pocket Deck Sim\PocketDeckSim\`).

## Card table

Set numbers: **none published yet** for any B4b card (all "B4b ???"). Fill from https://pocket.limitlesstcg.com/cards/B4b on release.
Printed text is quoted from the fork database (`python lib/card.py`), which matches the Japanese text on GameWith for every
new-art card. "Engine" says where the fork already implements the mechanic; "novelty" is whether anything new must be built.

### A. New-artwork reprints (10 cards; confirmed by GameWith text, Game8 rarities, pokemon-zone images)

| Card | B4b no. | Rarity | New or reprint | Reprint of | Printed text (fork database) | Engine | Novelty |
|---|---|---|---|---|---|---|---|
| Mega Charizard X ex | ??? | ☆☆ | reprint, new art | B2b 009 (alts B2b 076, 111) | Fire, Stage 2 (Charmeleon), HP 220, weak Water, retreat 2. [RRR] Raging Blaze 100: "If this Pokémon's remaining HP is 110 or less, this attack does 80 more damage." | mechanic present (B2b) | none |
| Mega Venusaur ex | ??? | ☆☆ | reprint, new art | B1a 004 (alts B1a 076, 083) | Grass, Stage 2 (Ivysaur), HP 240, weak Fire, retreat 4. [GGCC] Critical Bloom 120: "Your opponent's Active Pokémon is now Poisoned and Asleep." | `engine/src/actions/apply_attack_action.rs:3150` | none |
| Mega Altaria ex | ??? | ☆☆ | reprint, new art | B1 102 (alts B1 259, 286, B3a 107) | Psychic, Stage 1 (Swablu), HP 190, weak Metal, retreat 1. [PP] Mega Harmony 40: "This attack does 30 more damage for each of your Benched Pokémon." | present (B1; k3 table deck) | none |
| Mega Gardevoir ex | ??? | ☆☆ | reprint, new art | B2 066 (alts B2 185, 203, B4 227) | Psychic, Stage 2 (Kirlia), HP 210, weak Darkness, retreat 1. [PP] Fantasia Force 110: "Take 3 [P] Energy from your Energy Zone and attach it to your [P] Pokémon in any way you like." | present (B2) | none |
| Mega Lucario ex | ??? | ☆☆ | reprint, new art | B3 081 (alts B3 184, 204) | Fighting, Stage 1 (Riolu), HP 190, weak Psychic, retreat 1. [FF] Fighting Pulse 90: "If this Pokémon has at least 1 extra [F] Energy attached, this attack does 50 more damage." | present (B3; `players/value_functions.rs:2154`) | none |
| Meloetta | ??? | ☆ | reprint, new art | B2 070 (alts B2 233, P-B 050) | Psychic, Basic, HP 70, weak Darkness, retreat 1. Ability Strange Singing: "At the beginning of your turn, if this Pokémon is in the Active Spot, put a random [P] Pokémon from your deck into your hand." [PP] Psyshot 50. | present (`players/expectiminimax_player.rs:1728`) | none. Not the Fighting Meloetta B3 089 (GameWith text: 超タイプ, ふしぎなうたごえ, HP 70) |
| Eevee | ??? | ☆ | reprint, new art | B1 184 (alts P-B 011, 054) | Colorless, Basic, HP 50, weak Fighting, retreat 1. Ability Boosted Evolution: "As long as this Pokémon is in the Active Spot, it can evolve during your first turn or the turn you play it." [C] Stampede 10. | `engine/src/move_generation/mod.rs:190-205` | none. Pinned by GameWith (HP 50, ブーストしんか, ふむ 10); not any of the other 10 B-series Eevees |
| Fidough | ??? | ☆ | reprint, new art | B3b 034 | Psychic, Basic, HP 40, weak Metal, retreat 0. [CC] Puppy Pile 20×: "Reveal all of your Pokémon in play and in your hand that have the Puppy Pile attack, and this attack does 20 damage for each Pokémon you revealed in this way." | `engine/src/actions/effect_mechanic_map.rs:3330`, `attacks/mechanic.rs:878` | none. Not Fidough B2a 046 (Rear Kick); GameWith: HP 40, こいぬまみれ |
| Copycat | ??? | ☆☆ | reprint, new art | B1 225 (alt B1 270) | Supporter: "Shuffle your hand into your deck. Draw a card for each card in your opponent's hand." | `apply_trainer_action.rs:236`, `move_generation_trainer.rs:239` | none |
| Elesa | ??? | ☆☆ | reprint, new art | B3b 066 (alt B3b 083) | Supporter: "Return all Pokémon Tools attached to each Pokémon (both yours and your opponent's) to their owner's hand." | `apply_trainer_action.rs:304`, `move_generation_trainer.rs:321` | none |

### B. Parallel-foil ("mirror") reprints (13 cards per GameWith; same art and text as the original, special shine)

Where a name has more than one B-series printing, which printing gets the foil is **unverified** until the list is out.

| Card | B4b no. | Rarity | New or reprint | Candidate printing(s) | Printed text (fork database) | Engine | Novelty |
|---|---|---|---|---|---|---|---|
| Charmeleon | ??? | ◊◊ (TheGamer) | reprint, parallel foil | B1a 012 or B2b 008 (**unverified**; GameWith expects one Charizard line, likely the B2b one that evolves into Mega Charizard X) | Both: Ability Ignition: "Once during your turn, when you play this Pokémon from your hand to evolve 1 of your Pokémon, you may take a [R] Energy from your Energy Zone and attach it to your Active [R] Pokémon." B1a: [RRC] Steady Firebreathing 50; B2b: [RR] Slash 40 | present (both printings in `database.rs`) | none |
| Chingling | ??? | ◊◊◊ (TheGamer) | reprint, parallel foil | B1 109 (only B print) | Psychic, Basic, HP 30, retreat 0. [-] Jingly Noise 10: "During your opponent's next turn, they can't play any Item cards from their hand." | present | none |
| Dragonair | ??? | ◊◊ (TheGamer) | reprint, parallel foil | B2b 052 or B4 117 (**unverified**) | B2b: [C] Sky's Blessing: "Take a [W] and a [L] Energy from your Energy Zone and attach them to this Pokémon." B4: Ability Dragon's Blessing: "Once during your turn, if this Pokémon is on your Bench, you may attach an Energy from your discard pile to your Active [N] Pokémon." [CC] Draconic Whip 40 | present (`players/value_functions.rs:146` Dragon's Blessing class) | none |
| Roaring Moon | ??? | ◊◊◊ (TheGamer) | reprint, parallel foil | B3a 047 (alt B3a 109) | Darkness, Basic, HP 100, weak Grass, retreat 1. Ability Ancient Roar: "Once during your turn, when you put this Pokémon from your hand onto your Bench, you may switch out your opponent's Active Pokémon to the Bench. (Your opponent chooses the new Active Pokémon.)" [DDC] Wind of Darkness 70 | `engine/src/hooks/core.rs:344` | none |
| Arena of Antiquity | ??? | ◊◊ (TheGamer) | reprint, parallel foil | B3 154 | Stadium: "Attacks used by each [F] Pokémon in play (both yours and your opponent's) do +20 damage to the opponent's Active Pokémon ex." | `engine/src/stadiums.rs:143` | none |
| Ancient Booster Energy Capsule | ??? | ◊◊ (TheGamer) | reprint, parallel foil | B3a 069 | Tool: "The Ancient Pokémon this card is attached to gets +40 HP." | present (B3a) | none |
| Celebi | ??? | unverified | reprint, parallel foil | B3 004 (alts B3 233, P-B 079) | Grass, Basic, HP 70, weak Fire, retreat 1. Ability Time Recall: "Each of your evolved Pokémon can use any attack from its previous Evolutions. (You still need the necessary Energy to use each attack.)" [CC] Smack 30 | `abilities/mechanic.rs:707`, `move_generation/attacks.rs:176` | none |
| Victini | ??? | unverified | reprint, parallel foil | B3 025 (alt P-B 049) | Fire, Basic, HP 70, weak Water, retreat 1. Ability Victory Star: "Once during your turn, after you flip any coins for an attack of 1 of your [R] Pokémon, you may ignore all results of those coin flips and begin flipping those coins again. You can't use more than 1 Victory Star Ability each turn." [RC] V-Flame 40 | `actions/apply_action.rs:183-355` (note `card_validation.rs:97`: confusion/attacker-side coin gates bypass the reroll pending rule verification) | none new; existing caveat stands |
| Baxcalibur | ??? | unverified | reprint, parallel foil | B2a 036 (alt B2a 130) | Water, Stage 2 (Arctibax), HP 140, weak Metal, retreat 3. Ability Ice Maker: "Once during your turn, you may take a [W] Energy from your Energy Zone and attach it to the [W] Pokémon in the Active Spot." [WWW] Buster Tail 90 | present (B2a) | none |
| Raichu | ??? | unverified | reprint, parallel foil | B2b 023, B3b 022 or B4 050 (**unverified**) | B2b: [LL] Thunder 90, "This Pokémon also does 30 damage to itself." B3b: [LL] Mach Bolt 70. B4: Ability Evoshock (coin flip on evolve, Paralyze) + [LC] Electro Ball 50 | present (`abilities/mechanic.rs:512` Evoshock) | none |
| Bombirdier | ??? | unverified | reprint, parallel foil | B2a 071 or B3 115 (**unverified**) | B2a: [CCC] Fly 70 (coin; heads = protection next turn). B3: Ability Villainous Delivery: "As long as this Pokémon is on your Bench, your Active [D] Pokémon's Retreat Cost is 1 less." [D] Dark Cutter 30 | present (both in `database.rs`) | none |
| Aegislash | ??? | unverified | reprint, parallel foil | B1 172 or B2 120 (**unverified**) | B1: Ability Cursed Metal: "Attacks used by your [P] Pokémon and [M] Pokémon do +30 damage to your opponent's Active Pokémon." [MCC] Slicing Blade 70. B2: [MMM] Superb Shield 80, "-80 damage from your opponent's Pokémon ex next turn" | `hooks/core.rs:1162` (Superb Shield), `effects.rs:102` | none |
| Haxorus | ??? | unverified | reprint, parallel foil | B2b 056 (alts B2b 110, P-B 045) | Dragon, Stage 2 (Fraxure), HP 150, retreat 2. [FMC] Frenzied Blade 50: "This attack does 20 more damage for each Benched Pokémon (both yours and your opponent's)." | present (B2b) | none |

Note: a WebFetch summary of the GameWith page listed "Happiny" among the foils; the page itself does not (Happiny is B4a, which
is excluded). Ignore that artefact.

### C. ◊◊◊◊ ex reissues (official: "every ♦♦♦♦ card" from B1..B4)

Ten named so far (TheGamer, Serebii): Mega Gengar ex (B2b 039), Mega Lopunny ex (B1a 042), Mega Blaziken ex (B1 036),
Mega Diancie ex (B3b 032), Mega Rayquaza ex (B4 120), Miraidon ex (B3a 019), Greninja ex (B1 073), Meowscarada ex (B2a 003),
Vaporeon ex (B3 037), Teal Mask Ogerpon ex (B2 017). All plain reprints, same text, all already in the fork database and engine.

Full expected pool, the 70 distinct ◊◊◊◊ cards of B1..B4 in `lib/deckgym-database.json` (B4b numbers unknown; **membership of
each one is unverified** until the list is published, but the official wording is "every"):
Alolan Ninetales ex, Armarouge ex, Bellibolt ex, Blacephalon ex, Chien-Pao ex, Corviknight ex, Crustle ex, Dedenne ex,
Dragalge ex, Flutter Mane ex, Flygon ex, Gholdengo ex, Gigalith ex, Greninja ex, Hisuian Zoroark ex, Hitmonchan ex, Hoopa ex,
Indeedee ex, Iron Bundle ex, Jolteon ex, Koraidon ex, Magnezone ex, Mega Absol ex, Mega Altaria ex, Mega Ampharos ex,
Mega Audino ex, Mega Blastoise ex, Mega Blaziken ex, Mega Camerupt ex, Mega Charizard X ex, Mega Charizard Y ex,
Mega Diancie ex, Mega Gallade ex, Mega Gardevoir ex, Mega Gengar ex, Mega Gyarados ex, Mega Kangaskhan ex, Mega Lopunny ex,
Mega Lucario ex, Mega Manectric ex, Mega Mawile ex, Mega Metagross ex, Mega Pinsir ex, Mega Rayquaza ex, Mega Sableye ex,
Mega Sceptile ex, Mega Scizor ex, Mega Sharpedo ex, Mega Slowbro ex, Mega Steelix ex, Mega Swampert ex, Mega Venusaur ex,
Melmetal ex, Meowscarada ex, Milotic ex, Mimikyu ex, Miraidon ex, Rapidash ex, Rotom ex, Swanna ex, Tauros ex,
Teal Mask Ogerpon ex, Terapagos ex, Toxtricity ex, Typhlosion ex, Vaporeon ex, Vespiquen ex, Wailord ex, Whimsicott ex, Zoroark ex.

GameWith also expects the pre-evolutions of those ex to be included (◊, ◊◊ reprints), as A4b did. Which ones, and how many
◊/◊◊/◊◊◊ non-ex reprints: **unverified**.

### D. Promo cards tied to the B4b event cycle (NOT in the B4b set)

| Card | Where | New or reprint | What is known | Engine | Novelty |
|---|---|---|---|---|---|
| **Mega Garchomp ex** | Promo-B Series Vol. 13, Mega Garchomp ex Drop Event, mid-to-late October 2026 (official page; pokemon-zone; GameWith 578652) | **genuinely new** (not in fork database: `python lib/card.py "Mega Garchomp ex"` = 0 printings) | Stage 2 (from Garchomp line: Gible, Gabite, Garchomp per GameWith), Dragon type, Mega Evolution ex, **HP 220**. One attack, **Falling Edge, 190 damage**, text "Discard 2 random Energy from this Pokémon." (read from the pokemon-zone card image; GameWith's card box says 180 but its prose says 190 for three Energy; the image shows 190, so 180 is a GameWith typo). Energy cost: three icons visible on the image, colours not readable at spoiler resolution; GameWith says 3 Energy. **Cost, weakness (Dragon: normally none) and retreat cost are unverified.** | attack text already exists verbatim on Giratina A2a 061 (Crisis Dive 120) and Rayquaza B4 119 (Dragon Impact 140); Mega ex rule (3 points) present since B1 | **no new mechanic**; needs a database entry, generator run and a mechanic-map registration reusing the existing discard-2-random-Energy attack |
| Charmander (Promo B) | Charmander and Drampa Wonder Pick event, mid-to-late October (pokemon-zone) | reprint presumed; text **unverified** | image only on pokemon-zone; no text published | four Charmander texts already in database (A1/A2b/B1a/B2b lines) | none expected |
| Drampa (Promo) | same event | reprint presumed; text **unverified** | none published | three Drampa texts in database (A3, A3b, B4 124) | none expected |

## What this means for plan item A5

1. **Data refresh only.** B4b adds new IDs whose text duplicates existing printings. The work is: add the B4b entries to
   `engine/database.json` (and the `lib/deckgym-database.json` copy), run `card_enum_generator` to regenerate `card_ids.rs`
   and `database.rs`, and add each new `CardId` as an alias next to its original in the mechanic maps
   (`effect_mechanic_map.rs`, `effect_ability_mechanic_map.rs`, `apply_trainer_action.rs`, `move_generation_trainer.rs`),
   the way B1 270 sits beside B1 225 for Copycat. Not done here (task says do not modify the engine).
2. **Acceptance stays as planned:** the k3 table must reproduce game for game on the eight B4a research decks
   (`rl/results/engine_identity_2026-09-25/`). Nothing in B4b changes any rule, so any drift would come from the refresh
   itself (for example anything that orders or hashes by `CardId` enum position after new variants are inserted). That is
   exactly what the identity replay is for.
3. **Card-effect pass:** the only new text is Mega Garchomp ex (Promo-B Vol. 13, October). It reuses an existing attack
   mechanic. Its cost/weakness/retreat must be taken from Limitless or the in-game card when it appears, not guessed.
4. **Deck relevance:** none of the ten new-art cards changes any deck's legality or play; they are the same cards. B4b is a
   collector set. Season B4b SP ranked (mid-to-late October) uses the same card pool as today plus, later, Mega Garchomp ex.
5. **Re-check on Sept 30:** pull https://pocket.limitlesstcg.com/cards/B4b for the numbered list and count; rerun the A4b-style
   script (all fields except id/rarity/booster_pack) to confirm 0 novel texts; fill the "???" numbers above.

## Unverified items (summary)

- Total B4b card count (no source has it; A4b precedent 379).
- B4b set numbers for every card.
- Which of the 70 B1..B4 ◊◊◊◊ cards, and which pre-evolutions and other ◊/◊◊/◊◊◊ cards, are included (official says "every ♦♦♦♦").
- Which printing carries the parallel foil for Charmeleon, Dragonair, Raichu, Bombirdier, Aegislash; rarities of the 7 foils TheGamer did not list.
- Mega Garchomp ex energy cost, weakness, retreat cost, and Promo-B number; "190" is from the spoiler image, "3 Energy" from GameWith prose.
- Charmander and Drampa promo texts.
- Serebii's phrase "some new cards": read as loose wording for new-art cards; it conflicts with the official page, pokemon-zone and GameWith's explicit statement.
