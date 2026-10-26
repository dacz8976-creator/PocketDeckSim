# Ladder Field: what to pull from each ranked game

You read reviews of Dustin's ranked Pokémon TCG Pocket games. For each game, you write one record about the OPPONENT's deck, using only what the game showed.

## Inputs, per game, in your batch file
- `ladder_opp_text` and `ladder_note`: the Ladder Log entry.
- `review_files`: the full written review(s), REVIEW.md. Read every one listed for the game. A game split across two recordings has two.
- `structured_files`: SUMMARY.json and LADDER_ENTRY.json, when the review folder has them.

Read ONLY the files your batch lists. Do not open any other folder. In particular, never open anything under `exam_v2`, `exam`, `run3`, `answers`, `references` or `labels`.

## Rules
- **Only what was shown.** List a card only if the review says it was seen in that game: played, shown on the board, revealed, or attacked with. Never add cards the opponent "probably" had. Never guess a list from the archetype.
- **Exact card names** as the game prints them, for example "Mega Absol ex", "Team Rocket's Weezing ex", "Alolan Muk", "Oricorio". Keep "ex", "Mega" and owner prefixes like "Team Rocket's" and "Alolan". Don't list Trainer cards in `opp_pokemon_seen`.
- **Energy types** are the OPPONENT's: types they attached, or that their Energy Zone showed. Use only Grass, Fire, Water, Lightning, Psychic, Fighting, Darkness, Metal. Colorless is not an Energy you can attach, so never list it. If the review names no opponent Energy at all, give an empty list. Don't infer Energy from the Pokémon's type here; the aggregator does that separately.
- **Main attacker:** the one Pokémon the opponent's deck was clearly built around. Usually it's the one that did most of their damage or took their points, preferring a Mega ex or ex if it attacked. Give null if the game was too short to tell.
- **Partner:** the second most important opponent Pokémon, either a second attacker or a key Ability or support Pokémon. Give null if none stands out.
- **Plan**, exactly one of:
  - `basic_aggro`: wins mainly with Basic Pokémon (often ex) attacking from early turns;
  - `evolution_setup`: wins mainly with an evolved attacker (Stage 1, Stage 2 or Mega ex) that needs setup turns;
  - `status_control`: the main plan is Special Conditions, retreat lock, Energy denial or hand disruption;
  - `spread_bench`: the main plan is damage to the Bench or many Pokémon;
  - `stall_wall`: the main plan is healing, damage reduction or a high-HP wall;
  - `unclear`: too little shown to tell.
- **Who went first:** "dustin", "opponent" or "unknown".
- **How it ended:** "points", "no_pokemon" (a side had no Pokémon left), "deck_out", "concede_dustin", "concede_opponent" or "unknown".
- **Confidence:**
  - `high` when the review clearly shows the core and Energy;
  - `medium` when partly shown;
  - `low` when very little was shown (for example, a 2-turn game).
- **Remark:** 140 characters at most, facts only. For example, "Mega Absol ex took all 3 points; Weezing ex poisoned from turn 4."

## Output
Write a JSON Lines file with one line per game in your batch, in batch order, to the output path you were given. Each line has exactly these keys:

```
{"game_key": "...", "opp_pokemon_seen": ["..."], "opp_main_attacker": "..."|null, "opp_partner": "..."|null,
 "opp_energy_seen": ["Darkness"], "opp_energy_evidence": "short quote or turn reference", "plan": "...",
 "went_first": "...", "turns": <global turns as an integer, or null>, "end": "...", "confidence": "...", "remark": "..."}
```

When done, check that the file has exactly one valid JSON line per game in your batch, with every key present. Then reply with:
- the line count;
- the number of games with an empty `opp_energy_seen`;
- any game whose review contradicts its Ladder Log entry about the opponent's Pokémon or the result, as one line each.
