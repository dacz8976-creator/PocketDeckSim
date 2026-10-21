# Wailord Energy alternatives: bounded rules check

Checked 2026-10-02 UTC. Scope: printed eligibility and tradeoffs only. No deck, artifact, media, simulator, index, or training changes. Dustin's report that the deck felt slow is owner testimony; none of these alternatives was tested by this check.

## Confirmed core requirements

Directly inspected the retained in-game deck screen from `20261002_020315000_iOS.MP4` at 00:01.500 [S1]. The configured artifact identifies playable versions as Wailmer B4 036, Wailord B1 057, Wailord ex B4 037, and Indeedee ex B1 121. The screen includes alternate artwork, so this check verifies the visible printed mechanics rather than independently reading every set number.

| Card | Printed requirement and relevant effect | Consequence |
|---|---|---|
| Wailmer, 100 HP | Wave Splash: three Water, 60 damage | Other Energy does not pay these Water requirements. |
| Wailord, 200 HP | Whale Pump: four Colorless, 60 plus 10 per Water Energy attached | Any Energy can pay the four-Colorless cost, but only Water adds damage. Four Water gives 100 damage; four non-Water gives 60, before other effects. |
| Wailord ex, 250 HP | Wondrous Waves: four Water, 100 damage; recovers from all Special Conditions | An exclusively non-Water supply cannot power this attack. The effect is recovery, not ongoing prevention of Special Conditions. |
| Indeedee ex, 130 HP, Psychic type | Psychic: two Psychic, 30 plus 30 for each Energy attached to the opponent's Active Pokémon. Watch Over heals 20 from your Active Pokémon once during your turn. | The attack requires Psychic Energy, not Colorless. Watch Over has no printed Energy requirement. Water-only can retain the healing role but does not power this attack. |

Changing Energy type alone does not reduce the number of attachments required for normal Wailord. It would need a useful acceleration engine or another concrete benefit to address the reported delay.

## Water acceleration eligibility

**Mega Sharpedo ex:** The retained enlarged card [S2] shows Stage 1 from Carvanha, 190 HP, free retreat, and Turbo Shark costing one Water. It does 70 damage and adds one Water from the Energy Zone to one Benched Water Pokémon. Benched Wailmer, Wailord, and Wailord ex qualify; Psychic-type Indeedee ex does not. It cannot accelerate an Active Wailord. The Mega rule awards three points when it is Knocked Out. This route keeps Wailord's Water scaling and the ex's attack requirements, but adds a Carvanha evolution line and requires attacking with Sharpedo before switching to Wailord. Improved pace and survival are untested.

**Misty:** The retained in-game resolution text [S3, 00:31.500 and 00:34.500] specifies choosing one Water Pokémon, flipping until tails, and adding one Water from the Energy Zone per heads to that Pokémon. Wailmer and both Wailords qualify, including when Active; Indeedee ex does not. The same retained example shows zero heads and no added Energy. Misty is therefore a legal acceleration hypothesis, not guaranteed acceleration. It is a Supporter and competes with the list's other Supporter plays. Official Pokémon strategy also describes its coin-flip reliance and single-target Energy allocation [S4].

## Alternate Energy: legal possibilities, not established fixes

- **Psychic:** Can pay normal Wailord's four Colorless and enable Indeedee ex's attack. Pure Psychic removes normal Wailord's Water damage bonus and cannot power this Wailmer or Wailord ex. It supplies no acceleration by itself. A mixed Water/Psychic version still has to solve both typed costs and has not been evaluated here.
- **Metal with Dialga ex:** A concrete legal mechanism exists. Pokémon's official Dialga strategy states that Metallic Turbo attaches two Metal Energy from the Energy Zone to one Benched Pokémon, without limiting that target to Metal type [S5]. Thus a Benched normal Wailord can receive the Metal and use it toward its Colorless cost. This needs Dialga's own setup, an attack turn, and a way to bring Wailord Active. Pure Metal leaves Whale Pump at its 60 base damage and cannot power either Wailord ex or Indeedee ex's attack. This is a different build hypothesis, not a simple repair of the entire observed core. Dialga's exact attack-cost icons were not independently inspected in this bounded check.

The most direct rules-compatible hypotheses for preserving the present attacking core are Misty and/or Mega Sharpedo ex with Water. That is an inference about compatibility, not a claim that either improves win rate or is the best deck. No full alternative list, collection availability, measured setup speed, or competitive comparison was established.

## Sources and limits

- **S1:** [Current native deck frame](../20261002_020315000_iOS_competitive_sol/native/t0001.50.jpg), individually inspected for the four core cards and Water-only setting.
- **S2:** [Retained Mega Sharpedo ex enlarged card](../20260921_150630_sol_verification/final_packet/frames/00-26.000-turn1-mega-sharpedo.jpg), from `20260921_150630000_iOS.MP4` at 00:26.000. Individually inspected for Turbo Shark, evolution, retreat, and Mega knockout rule.
- **S3:** [Retained Misty resolution sheet](../20260930_160256000_iOS_auto_sol/overview/sheet_02.jpg), from `20260930_160256000_iOS.MP4`, relevant panels 00:31.500 and 00:34.500. Inspected for the displayed effect and zero-heads resolution; this is an older source used only for rules evidence, not a new review or a result in this competitive batch.
- **S4:** [Official Pokémon: Mythical Island Top Cards](https://www.pokemon.com/uk/strategy/pokemon-tcg-pocket-mythical-island-top-cards), Misty discussion under Vaporeon.
- **S5:** [Official Pokémon: Dialga ex Deck List Strategy](https://www.pokemon.com/uk/features/pokemon-tcg-pocket-dialga-ex-deck-list-strategy), January 31, 2025, Metallic Turbo explanation. Retrieved through the web search index because direct page opening exposed an iframe shell.

Third-party card databases appeared during discovery but are not the authority for the conclusions above. No simulator-generated effect was used as rules authority. The current gameplay batch was not rereviewed here, and no testing establishes that a proposed variant fixes Dustin's experience.
