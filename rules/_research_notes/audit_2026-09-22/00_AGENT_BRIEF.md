# Brief for audit/research agents — Pokémon TCG Pocket engine (read this first)

## What this is
Pokémon **TCG Pocket** (the mobile game by Creatures/DeNA) — NOT the physical Pokémon TCG. Many physical-TCG rules
are wrong here (Bench is 3, Weakness is +20 flat, no Resistance, Confused tails = attack simply fails with no
self-damage, 3 points to win, ex = 2 points, Mega ex = 3, no Energy cards — an Energy Zone makes 1 Energy per turn,
first player draws on turn 1 but gets no Energy, no deck-out loss, hand limit 10, etc.). **Never flag something as a
bug because the physical TCG does it differently.**

The simulator is a Rust fork of deckgym. Its source (the "unified1" working tree the project runs) is at
`/home/claude/engine/src` and it **builds** (see "Probes" below). Card database: `/home/claude/engine/database.json`
(3,879 printings through set B4a). Don't modify anything under `/home/claude/engine/src`.

Rules reference (the standard to audit against), in `/mnt/user-data/uploads/Pocket Deck Lab/`:
- `RULES_FOR_AGENTS.md` — one-page summary. **Read it.**
- `rules/README.md` — the "rules most likely to be wrong in a simulator" list and the known engine bugs. **Read it.**
- `rules/01_game_structure.md`, `02_damage_knockouts_points.md`, `03_status_checkup_timing.md`,
  `04_actions_cards_effects.md`, `05_open_questions.md` — detail with evidence grades. Read the ones relevant to your area.
Grades: [OFFICIAL] in-app rules text / official FAQ / printed card text · [IN-GAME TEXT] game UI strings · [OBSERVED]
seen in the owner's recorded games · [DUSTIN] the owner's statement from play · [COMMUNITY] wikis/guides · [INFERRED].

## Evidence standard
A **bug** = the engine does something different from (a) the printed card text, or (b) a rule in the rules folder.
Quote the text/rule and its grade. If the real rule is unknown or the text is ambiguous, file it under
**"Rules questions"**, not as a bug. Say how sure you are:
- `VERIFIED-RUN` — you ran a probe test and quote its output;
- `VERIFIED-READ` — you read the code path end to end (cite file:line and quote the key lines);
- `PROBABLE` — strong reading but you didn't trace every branch;
- `UNSURE`.

## Already known — do not re-report (mention only if you find it has changed or is broader than stated)
1. Damage order: engine subtracts defender reductions (floored at 0) before adding Weakness (`hooks/core.rs` ~1705); official order is attack → attacker effects → Weakness → defender effects.
2. Win check: engine checks points first and calls "both ≥3" a tie even when one side has no Pokémon (`apply_action_helpers.rs` ~805). (Real rule partly open.)
3. Double-KO promotion goes by seat; real game: turn player (attacker) promotes first.
4. Playability: Gladion still blocked when named cards are gone (1.7.0 made it playable); Team Galactic Grunt, Cabbie, Pokémon Communication (deck half), Wallace and a Tool-searching Ability are blocked on *deck contents* (real rule: only blocked when what's visible shows it can't work; deck contents are hidden); Gladion/Clemont/Serena/Juliana have no empty-deck block.
5. Eevee (B1 184) Boosted Evolution lets every Pokémon evolve on turn 1 (should be only that Eevee).
6. Quick-Grow Extract and Wallace choose the target Pokémon at random (player should choose).
7. Asleep / Paralyzed / Confused don't replace each other (should: newest wins, only one at a time).
8. Lum Berry always resolves before Darkrai's Bad Dreams (should: turn player's end-of-turn effects first).
9. Caterpie (B3b 001) Quick Growth resolves after the Pokémon Checkup (should be before, as an end-of-turn effect).
10. Protective Poncho also blocks damage from your own attacks to your own Bench.
11. Fragrant Forest unusable when no Basic Grass Pokémon is left in the deck.
12. Pokémon Checkup handles players in seat order (should be: player whose turn just ended first).
13. Darkrai ex Nightmare Aura only fires on the manual Energy attachment, not on effect attachments from the Zone (probable).
14. Teal Mask Ogerpon ex Energized Leaves counts Energy cards, ignoring Serperior's Jungle Totem doubling (unsure).
15. Wallace reads printed HP instead of maximum HP (Giant Cape).

## Probes (running the engine)
The engine builds at `/home/claude/engine`. To test a suspicion, add a small integration test file
`/home/claude/engine/tests/zz_<yourname>_<topic>.rs` and run
`cd /home/claude/engine && cargo test --test zz_<yourname>_<topic> -- --nocapture 2>&1 | tail -40`.
Other agents share the build directory, so cargo may print "Blocking waiting for file lock" — just wait (use a
generous timeout, e.g. 600000 ms). Look at `tests/darkrai_bad_dreams_test.rs`, `tests/mechanics/*.rs` and
`src/test_support.rs` for helpers (`get_test_game_with_board`, `get_initialized_game`, `game.get_state_clone()`,
`state.set_board(...)`, `state.apply_status_condition(...)`, `game.set_state(...)`, `game.apply_action(&Action{..})`,
`state.generate_possible_actions()`, `PlayedCard::from_id(CardId::...)` with `.with_energy(vec![...])`). Card enum names
are in `src/card_ids.rs` (e.g. `A1035Charizard`). Use probes only where reading code leaves real doubt about a
High/Medium finding — they cost time. Print results with `println!` and make the test pass either way.

## Be economical
Several source files are huge (`src/actions/apply_attack_action.rs` 319 KB, `effect_mechanic_map.rs` 145 KB,
`apply_trainer_action.rs` 109 KB, `hooks/core.rs` 102 KB). **Grep for the handler you need** (`grep -n "Mechanic::Foo" -r src/`)
and read around it; don't read whole files.

## Report format
Write your full report to `/home/claude/work/reports/<yourname>.md`:
```
# <yourname> — <scope>
## Findings
### <ID> [High|Medium|Low] <short title>  (confidence)
- Card(s)/rule: ...
- Text/rule (grade, source): "..."
- Engine: file:line — what it does (quote 1–5 key lines)
- Example: concrete board situation and what happens vs. what should happen
- Impact: which decks/situations
## Rules questions (real rule unknown or text ambiguous)
## Checked and OK (one line each — this documents coverage)
```
Severity: High = changes game outcomes often for cards/decks that get simulated; Medium = changes outcomes in specific
situations/matchups; Low = rare or cosmetic. Your final message back to the coordinator: ≤250 words — counts by
severity, the top findings in one line each, and anything you couldn't finish.
