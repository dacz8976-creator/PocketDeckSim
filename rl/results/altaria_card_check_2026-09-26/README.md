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
3. **Confirmed on footage the same night: after an end-of-turn or Checkup knockout, Pocket asks for the new Active BEFORE the next turn starts and before its draw. The engine does it after.**
   - **The engine:** `trigger_promotion_or_declare_winner` puts the Promote frame under the next turn's DrawCard (`state/mod.rs` 1401-1423, 1206-1207). So the next player draws and sees that turn's Energy before choosing the replacement. The engine's own repair note aimed for "promotion without starting the next turn early".
   - **The footage:** four recorded end-of-turn knockouts (`promotion_timing.json`), each read frame by frame and independently re-checked (4 of 4 agree). In all four the knocked-out player moved next.
     - `20260908_004344` (Poison at the Checkup; Dustin's own draw is visible): "Please choose a Pokémon to switch in" at 208.7 s, Raticate ex in the Active Spot at 211.3 s, "Your turn / Current turn: 7" at 212.7 s, the draw at 214.3 s.
     - `20260908_190933` (Bad Dreams): promotion done 166.0-166.5 s, turn banner 166.7 s, the opponent's face-down draw 168.3 s.
     - `20260908_232955` (Burn): Mega Diancie ex settled 151.5 s, banner 151.6 s, draw 153.1 s.
     - `20260908_234514` (Burn): promotion 180.0-181.7 s, banner 182.8 s, draw 184.3 s.
     - Two other candidates ended the game, so there was no promotion.
     - Caveat: this is the order the phone shows; the server could in principle resolve it differently. It holds in all four cases, whether the promotion is Dustin's or the opponent's.
   - **Effect:** the engine gives the promoting player extra information (their draw and that turn's Energy) before they choose. That slightly favours opponents of Bad Dreams, Poison, Burn and Deceptive Needle decks: Altaria, Weezing, Hydreigon and Blaziken among the table decks.
   - **Unlike deviations 1 and 2, this one reaches table games** (Fable's note, Sept 26): any end-of-turn or Checkup knockout that leaves a choice of replacement. So its repair must have the identity replay read for which games change, not assumed unchanged. It goes to the cloud's repair list via Dustin.

**Open, ambiguous in Pocket, left as they are:**
- Copycat when the opponent holds 0 cards, or when it is your only card and your deck is empty: the engine allows both.
- Poké Ball's random pick, per copy (the engine) or per name (rules/05 #24): the wording favours per copy.
- Training Area adds nothing to a 0-damage attack. The engine agrees with the community ruling for Giovanni.

**Also noted (search, not rules):** a choice frame, such as Sabrina's opponent-chooses switch or any targeted card, costs one of the search's three own-turn actions. This is the search-length item already on the later-candidates list (`../trainer_audit_2026-09-25/README.md`). It applies to both sides and is not specific to Altaria.
