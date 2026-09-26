# Altaria list card check (Sept 26, night)

**Why:** the simulator underrates Altaria by about 7 points against Limitless in every matchup, and no piloting or search change has closed the gap. The Altaria detector network's pre-set reading (`rl/runs/diag-altaria-lucario/PRESET_READING.md`) names "a card check of the Altaria list's texts in the engine" as the lead that remains if the network finds no piloting gain. This check was run while the network trained, before its reading, and is useful either way.

**How:** a code-reading workflow, with no simulations, against the official engine source (7fc6ccb; `engine/src` unchanged since).
- **Subjects:** 15 in all.
  - Each of the 13 cards in `decks/research/altaria.txt`, checked clause by clause against its `lib/card.py` text: damage, cost, HP, Weakness, Retreat, evolution, ex points, every effect clause, who chooses, timing, first-turn rules, and how it interacts with Sleep.
  - The Asleep rules the deck's sleep lock depends on.
  - Altaria's interactions with the other seven table lists.
- **Evidence:** each finding cites file and line, existing tests, the rules docs and Dustin's recorded battles.
- **Skeptics:** three independent skeptics tried to refute every finding that wasn't clean (24 skeptic reads). Full output: `card_check.json`.

**Result: no card in the Altaria list is implemented differently from its text in any way that changes a game on the 28-matchup table.**
- **Clean:** Mega Altaria ex, Eevee, Igglybuff, Professor's Research, Field Blower, Small Balloon, and the interactions with the other seven lists all came back matching on every clause.
- **Checked clause by clause, with Dustin's recordings behind the observable parts:**
  - Swablu's Sing, Espeon's Hypnoblast and Darkrai's Dark Slumber and Bad Dreams.
  - The Sleep coin at every Checkup, including the one right after Sleep is applied.
  - Bad Dreams resolving before the Checkup.
  - Evolving, retreating and Pokémon Center Lady curing Sleep; healing alone not curing it.
  - Attack and Retreat blocked while Asleep; Abilities, Items and evolving allowed.
  - Training Area's +10.
- **So the card and rules implementation is ruled out as the cause of Altaria's gap.** What remains is the pilot (the network's reading, tonight) and the population, as PRESET_READING says.

**Engine deviations found along the way.** Each was upheld 3 to 0 by the skeptics. None arises between the eight table lists. All go to the cloud's open-bugs list via Dustin.
1. **A 0-damage attack that targets the Active uses up Mimikyu ex's Disguise** ("When this Pokémon is first damaged by an attack..."). Sing is one example.
   - `handle_damage_only` checks Disguise before it checks for 0 damage (`actions/apply_action_helpers.rs` 430-458, 553-563).
   - This is engine-wide: it affects every 0-damage attack that has a damage target.
2. **Bad Dreams, which is Ability damage, is wrongly stopped by three "by attacks" protections.**
   - The three: PreventAllDamageAndEffects (Hide, Dig, Fly, Scrunch, Iron Defense...), PreventDamageFromBasic (Carracosta's Blocking Shell; Darkrai is a Basic) and PreventDamageIfLessOrEqual (Harden).
   - `modify_damage` applies them without checking `is_from_active_attack` (`hooks/core.rs` 1717-1734, 1887-1894).
   - Every card text behind them says "by attacks", and the rules docs (from the official Mimikyu ex FAQ) say Ability damage is not attack damage.
   - The one-turn protections are still active when Bad Dreams resolves at the end of the next turn.
3. **Likely deviation, unverified in Pocket:** when an end-of-turn effect or the Checkup knocks out an Active (Bad Dreams, Poison, Burn, Deceptive Needle), the engine lets the next player draw and see that turn's Energy before choosing the replacement.
   - The code: `trigger_promotion_or_declare_winner` puts the Promote frame under the next turn's DrawCard (`state/mod.rs` 1401-1423, 1206-1207).
   - The engine's own repair note aimed for "promotion without starting the next turn early".
   - If Pocket asks for the promotion first, the engine gives the promoting player extra information. That slightly favours opponents of Bad Dreams, Poison and Burn decks, Altaria included, though the size is unknown. A footage check is queued, to see which comes first in a recorded end-of-turn knockout.

**Open, ambiguous in Pocket, left as they are:**
- Copycat when the opponent holds 0 cards, or when it is your only card and your deck is empty: the engine allows both.
- Poké Ball's random pick, per copy (the engine) or per name (rules/05 #24): the wording favours per copy.
- Training Area adds nothing to a 0-damage attack. The engine agrees with the community ruling for Giovanni.

**Also noted (search, not rules):** a choice frame, such as Sabrina's opponent-chooses switch or any targeted card, costs one of the search's three own-turn actions. This is the search-length item already on the later-candidates list (`../trainer_audit_2026-09-25/README.md`). It applies to both sides and is not specific to Altaria.
