# core_turn — core game flow and action legality

Scope: deck legality, setup, turn structure, first-turn rules, draw step, Energy Zone, Bench,
evolution, retreat, Supporters/Items/Tools/Stadiums, attacking, turn limit, Knock Outs/points,
winning/losing, promotion. Files: `src/game.rs`, `src/state/mod.rs`, `src/deck.rs`,
`src/card_validation.rs`, `src/move_generation/mod.rs`, `src/move_generation/attacks.rs`,
`src/hooks/retreat.rs`, `src/actions/apply_action.rs`, `src/actions/apply_action_helpers.rs`,
`src/state/energy.rs`, `src/tools.rs`, `src/stadiums.rs`.

Rules reference: `/mnt/user-data/uploads/Pocket Deck Lab/rules/` (01, 02, 03, 04, 05) and
`RULES_FOR_AGENTS.md`, read in full before this audit.

## Findings

### CT-1 [Medium] Deck legality is never enforced on the path that actually runs simulations (VERIFIED-READ)
- Rule: "20 cards. At most 2 copies of any card name... At least one Basic Pokémon... 1 to 3 Energy
  types." — `RULES_FOR_AGENTS.md` [IN-GAME TEXT], `rules/01_game_structure.md` §1.
- Engine: `Deck::is_valid()` (`src/deck.rs:93-116`) checks card count, ≥1 Basic, and ≤2 copies per
  name — but never checks the 1–3 declared Energy-type range at all (no check on
  `self.energy_types.len()` anywhere in `deck.rs`, confirmed by grep across the file). More
  importantly, `is_valid()` is **never called** on the path that actually plays games:
  `Game::new` (`src/game.rs:138-153`) takes each `Player`'s deck and calls
  `State::initialize(&deck_a, &deck_b, &mut rng)` directly, no validation. `simulate.rs:89-90` and
  every deck-loading site in `python_bindings.rs` (`:368`, `:706-709`, `:804-807`) call
  `Deck::from_file` and hand the result straight to a game — no `is_valid()` call anywhere in
  either file. Only `cli_preflight.rs:230` (`full_deck_problem`), `optimize.rs:275` and
  `bin/temp_deck_generator.rs:33` call it, and those are auxiliary tools, not the simulation
  entrypoints.
- Compounding risk: `Deck::shuffle(true, ...)` (`src/deck.rs:129-147`) does
  `matching.pop().expect("Decks must have at least 1 basic")` (`:138`) — a deck with **zero**
  Basics doesn't fail gracefully, it **panics** the whole run.
- Example: a 21-card decklist, a decklist with 3 copies of a card, or a decklist whose declared
  Pokémon span 4 distinct Energy types will load and simulate without warning through
  `simulate.rs`/`python_bindings.rs`; a decklist with 0 Basics crashes the process.
- Impact: any candidate decklist fed straight into a simulation run (rather than through
  `cli_preflight`) gets no legality feedback — a typo'd or miscounted decklist silently produces
  simulation output (or a panic) instead of an error naming the problem.

### CT-2 [Medium] Retreat never lets the player choose which Energy is discarded (VERIFIED-READ)
- Rule: "Discard 1 Energy from your Active Pokémon for each Colorless Energy symbol... The
  discarded Energy can be of any type... you choose which Benched Pokémon becomes Active. The
  player also picks *which* Energy when there is a choice (the game opens a 'Discard' Energy
  picker)." — `rules/04_actions_cards_effects.md` §2 [OFFICIAL for the switch, INFERRED for the
  Energy-choice part, consistent with the UI].
- Engine: `apply_retreat` (`src/actions/apply_action.rs:1368-1418`) contains its own admission:
  ```
  1381:        // TODO: Maybe give option to user to select which energy to discard
  1382:
  1383:        // Some energies are worth more than others... For now decide the ordering
  1384:        // that keeps as much Grass energy as possible (since possibly worth more).
  ```
  It sorts the Active's attached Energy so Grass energy is discarded last, then pops from the back
  until the (reduced) retreat cost is paid (`:1386-1408`). The player/bot is never offered a choice
  of which attached Energy types to keep.
- Example: an Active holding one Fire and one Water Energy with a 1-Colorless retreat cost —
  a real player could choose to keep either type; the engine always discards non-Grass energy
  first by this fixed rule, so which type survives is decided by a hard-coded heuristic, not the
  player.
- Impact: any deck that runs mixed Energy types on a single attacker and cares which type stays
  attached after a partial retreat (to keep an attack payable on the Bench, or feed
  from-discard-energy effects with a specific type). Grass decks are unaffected (the heuristic
  favors them by construction); everyone else gets an undocumented, unchosen outcome.

### CT-3 [Medium] No limit on how many Stadium cards can be *played* in one turn (VERIFIED-READ)
- Rule: "One Stadium play per turn ... separate from the Supporter limit ('You can't use any more
  Stadium cards this turn')." — `rules/04_actions_cards_effects.md` §6 Stadiums table, row 1
  [IN-GAME TEXT]; README item 13.
- Engine: `can_play_stadium` (`src/move_generation/move_generation_trainer.rs:370-395`) only
  blocks playing a Stadium with the **same name** as the one already active (`:372-376`); it
  never checks a play-count. `generate_possible_trainer_actions`
  (`src/move_generation/move_generation_trainer.rs:36-58`) gates Supporters via
  `can_play_support` and Items via `can_play_item`, but has no equivalent gate for
  `TrainerType::Stadium`. The field named `has_used_stadium` (`src/state/mod.rs:323`) is not a
  play counter at all — it tracks whether the player has used the *active Stadium's own granted
  ability* this turn (Mesagoza's coin flip, Rainbow Cave, Kid's Room, Area Zero, Arcade — see
  `src/stadiums.rs:99,172,190,208,222,239` and every write site in
  `src/actions/apply_stadium_action.rs`). Nothing in the codebase counts "a Stadium card was
  played from hand this turn."
- Example: a deck carrying two differently-named Stadiums (e.g. one disruptive, one beneficial)
  can play both in the same turn — discard the opponent's Stadium with the first play, then
  immediately establish their own with the second — which the real game's "You can't use any more
  Stadium cards this turn" message forbids.
- Impact: any deck running 2+ distinct Stadium cards; lets a player both deny an opposing Stadium
  and set up their own (or stack two of their own effects) in a single turn instead of over two.

### CT-4 [Low] `Place` action generation targets the Active slot for hand cards outside setup (PROBABLE, not run)
- Rule: outside setup, a Basic (or Fossil) Pokémon can only be placed on the **Bench**; the Active
  Spot is filled only at setup or by choosing a Benched Pokémon to promote after a Knock Out — never
  by playing a card from hand directly into an empty Active Spot.
- Engine: `generate_hand_actions`'s Basic-Pokémon branch
  (`src/move_generation/mod.rs:176-186`) iterates every empty `in_play_pokemon` slot including
  index 0 (Active), not just the Bench:
  ```
  176	            Card::Pokemon(pokemon_card) => {
  177	                // Basic pokemons can be placed in empty Active or Bench slots
  178	                if pokemon_card.stage == 0 {
  179	                    state.in_play_pokemon[current_player]
  180	                        .iter()
  181	                        .enumerate()
  182	                        .for_each(|(i, x)| {
  183	                            if x.is_none() {
  ...
  ```
  `can_place_fossil` (`src/move_generation/move_generation_trainer.rs:952-968`) does the same for
  Fossils (its sibling `can_play_fossil` at `:337-353`, which correctly restricts to Bench-only
  slots with `*i > 0`, is dead code — the live Fossil dispatch at
  `trainer_move_generation_implementation` lines 82-83 calls `can_place_fossil`, not
  `can_play_fossil`, so the bench-only version is never reached).
- Why this is probably not exploitable: setup itself is safe (`generate_possible_trainer_actions`
  returns nothing for any Trainer card, Fossils included, while `state.turn_count == 0`, so Fossils
  can never fill the setup Active — confirmed, see Checked-and-OK). Outside setup, every code path
  that can empty the Active Spot (KOs via `handle_knockouts`, `apply_discard_fossil`,
  `ReturnPokemonToHand`, trainer-driven switches) calls
  `state.trigger_promotion_or_declare_winner(...)` (`src/state/mod.rs:1355-1404`), which inserts a
  dedicated `Promote` choice set into `move_generation_stack`; since
  `generate_possible_actions` short-circuits to `move_generation_stack.last()` before ever reaching
  `generate_hand_actions` (`src/move_generation/mod.rs:42-52`), the "place from hand into slot 0"
  branch should be unreachable while `state.in_play_pokemon[player][0]` is `None` mid-game.
- Impact if ever reachable: a Fossil (which can never retreat and would otherwise never be a valid
  Active-from-hand play) or a plain Basic could fill the Active Spot bypassing the "owner chooses
  which Benched Pokémon promotes" step. I did not find a live path that hits this and did not spend
  a probe confirming it further; flagging it as a correctness smell worth a guard clause
  (`i != 0` in both places) rather than a demonstrated bug.

## Rules questions (real rule unknown or text ambiguous)

### RQ-1: Pokémon Checkup Knock Outs are finalized immediately per condition, not deferred to the end of the whole Checkup (VERIFIED-RUN)
This is exactly the test `rules/05_open_questions.md` #4 asks for ("an undamaged Burned or
Poisoned Pokémon of your own with Garganacl (Blessed Salt, heal 10) in play... Poisoned: 0 vs
10"), and the true rule is explicitly marked open there. I ran it:

- Engine: `apply_pokemon_checkup` (`src/actions/apply_action_helpers.rs:237-324`) processes the
  Poisoned loop first (`:247-261`), calling `handle_damage` for each Poisoned Pokémon, which
  internally calls `handle_knockouts` (`src/actions/apply_action_helpers.rs:487-505`) — this
  finalizes the Knock Out (discard, points, promotion) **immediately**, inside the Poison loop,
  before the Burn loop, the Sleep/Paralysis loops, or `apply_blessed_salt_checkup_healing`
  (`:336-352`, which runs last) ever execute. The code's own comment at `:330-335` states the
  authors chose this order deliberately: "It runs after the checkup damage so that a Pokémon left
  on 0 HP by Poison or Snowy Terrain is already Knocked Out and gone — healing cannot rescue it —
  matching the official checkup order" — but the rules folder treats that same question as
  [UNRESOLVED], leaning (from the literal "at the end of Pokémon Checkup" wording) toward the
  opposite conclusion.
- Probe (`tests/zz_coreturn_checkup_blessed_salt.rs`, board: Caterpie 50 HP damaged to 10 HP
  remaining and Poisoned, Garganacl on the same Bench):
  ```
  Before EndTurn: player0 active remaining HP = 10
  After Checkup: player0 active still in play = false
  Points: [0, 1]
  ```
  Confirms: the Poisoned Caterpie is Knocked Out by the 10 poison damage and gone before Blessed
  Salt's heal-10 ever runs, regardless of Garganacl being in play on the same side.
- Why this is a rules question and not a bug: `rules/03_status_checkup_timing.md` §5 step 4 quotes
  the official "Any Pokémon that has no HP remaining **at the end of** Pokémon Checkup is Knocked
  Out" and immediately flags the Blessed-Salt consequence as [INFERRED, not observed]; `05
  _open_questions.md` #4 lists the order between Special Conditions and Checkup Abilities as
  explicitly open. I'm not filing this as CONFIRMED-wrong because the real rule hasn't been
  observed in a game yet — but the engine's actual behavior (VERIFIED-RUN above) is the opposite of
  what the rules doc's own inference favors, so it's worth Dustin running exactly this in-game test
  (a Poisoned/Burned Garganacl-side Pokémon at exactly lethal Checkup damage) to settle it.
- Impact if the literal "at the end" reading is correct: every "During Pokémon Checkup, heal/do X"
  Ability (Garganacl's Blessed Salt, Glaceon ex's Snowy Terrain interacting with a heal, any future
  card in that family) resolves in the wrong order relative to Poison/Burn.

## Checked and OK

- Card-name distinctness for the 2-copy limit: `Card::get_name()` (`src/models/card.rs:160-166`)
  returns the database's exact printed name; spot-checked "Charizard" / "Charizard ex" / "Mega
  Charizard X ex" / "Mega Charizard Y ex" and "Weezing" / "Team Rocket's Weezing ex" in
  `database.json` — all distinct strings, so `is_valid()`'s per-name counter (where it does run)
  treats them correctly as different cards.
- Fossils cannot be placed during setup: `generate_possible_trainer_actions`
  (`src/move_generation/move_generation_trainer.rs:36-58`) returns no actions for *any* Trainer
  card, Fossils included, while `state.turn_count == 0` — so `can_place_fossil` (see CT-4) never
  fires during setup, and Fossils can't become the opening-hand's guaranteed Basic or an initial
  Bench placement.
- Opening hand / guaranteed Basic: `Deck::shuffle(true, ...)` (`src/deck.rs:129-147`) sets aside one
  random Basic to be drawn first, then shuffles the rest behind it; the 5-card opening hand is
  dealt by 5 plain `maybe_draw_card` calls (`src/state/mod.rs:748-770`), so the guaranteed Basic is
  always the first (or among the first five) drawn.
- Coin flip for who goes first is a fair 50/50: `state.current_player = rng.gen_range(0..2);`
  (`src/state/mod.rs:761`).
- Setup restricts the Active placement to one card, then Bench-only afterward:
  `generate_initial_setup_actions` (`src/move_generation/mod.rs:141-157`).
- First turn: P1 draws (`state.queue_draw_action` in the setup→turn-1 mutation,
  `src/actions/apply_action_helpers.rs:69-78`), gets no Energy (`State::initialize`,
  `src/state/mod.rs:748-770`, `current: None` never rotated until `advance_turn` runs at the
  turn-1→turn-2 transition), can play a Supporter (`can_play_support` has no turn-based
  restriction, `src/hooks/core.rs:652-671`), can attack if the cost is payable
  (`generate_attack_actions`, `src/move_generation/attacks.rs:13-79`, has no turn-count gate at
  all — 0-cost attacks are offered on turn 1), can retreat (no turn restriction in
  `can_retreat`). Neither player can evolve on their own first turn:
  `state.is_users_first_turn()` is `turn_count <= 2` (`src/state/mod.rs:1221-1223`), which covers
  both P1's turn (1) and P2's turn (2), and gates evolution in
  `src/move_generation/mod.rs:196-200`. P2 gets Energy on their first turn: `advance_turn`
  (`src/state/mod.rs:1180-1202`) calls `rotate_energy_zone` for the incoming player at every
  transition, including turn 1→2, so P2's `current` is populated by the time their first turn's
  actions are generated.
- Draw step / hand limit 10: `maybe_draw_card` (`src/state/mod.rs:806-826`) skips the draw and
  leaves the card in the deck when `hands[player].len() >= 10`. Multi-card draws
  (`SimpleAction::DrawCard { amount }`, `src/actions/apply_action.rs:728-732`) loop
  `maybe_draw_card` once per card, so a draw that crosses 10 mid-effect is partly skipped
  correctly. Empty deck: `Deck::draw()` returns `None` and `maybe_draw_card` just logs and returns
  — no loss condition anywhere tied to an empty deck (grepped `state/mod.rs` and
  `apply_action_helpers.rs`).
- Energy Zone: `current`/`next` model with P1's `current = None` on turn 1
  (`State::initialize`, `src/state/mod.rs:748-770`); `rotate_energy_zone`
  (`src/state/mod.rs:926-935`) promotes `next` → `current` and rolls a fresh `next` via
  `roll_energy` (`:1520-1525`, uniform `.choose(rng)` over the deck's declared types, independent
  each call); unused `current` is implicitly discarded since it's unconditionally overwritten the
  next time that player's zone rotates, and it's never reachable outside that player's own turn.
  Manual attach is available to Active or any Bench slot with no "played this turn" restriction
  (`src/move_generation/mod.rs:72-84`). Card-effect attachments from the Zone use
  `is_turn_energy: false` and so don't clear `energy_zone[actor].current`
  (`src/state/energy.rs:13-30`), leaving the once-per-turn manual attach action still available.
- Bench max 3, Basics benchable any time in the main phase: `in_play_pokemon` is a fixed
  `[Option<PlayedCard>; 4]` (index 0 = Active, 1-3 = Bench); `generate_hand_actions` offers a
  `Place` action for every empty slot with no additional timing gate beyond "it's your main
  phase" (see CT-4 for the Active-slot-index nuance, which doesn't affect the max-3 Bench count).
- Evolution: blocked on either player's first turn (`turn_count <= 2` gate,
  `src/move_generation/mod.rs:196-200`, known exception Eevee's Boosted Evolution, already
  reported); blocked on a Pokémon placed this turn (`!pokemon.played_this_turn` check,
  `:203-213`) and at most once per Pokémon per turn (same flag). Replaying a Pokémon returned to
  hand (Ilima/Koga) correctly resets the flag: `apply_place_card`
  (`src/actions/apply_action.rs:1027-1059`) always constructs a brand-new `PlayedCard` via
  `to_playable_card(card, true)` (`src/hooks/core.rs:89-101`), so `played_this_turn` is freshly
  `true` on every placement, whether it's the card's first time in play or a replay. Evolution
  keeps damage/Energy/Tools and clears Special Conditions and effects-of-attacks: `apply_evolve`
  (`src/actions/apply_action.rs:1460-1499`) copies `damage_counters`/`attached_energy`/
  `attached_tools` from the pre-evolution onto a fresh `PlayedCard` (whose status-condition fields
  and `effects` list default to none). Mega Evolving doesn't end the turn: Mega ex just goes
  through the same `Evolve`/`apply_evolve` path as any evolution, and the only thing that sets
  `state.end_turn_pending = true` anywhere in the engine (besides an AI lookahead helper in
  `players/expectiminimax_player.rs`) is `SimpleAction::Attack`
  (`src/actions/apply_action_helpers.rs:1020-1026`).
- Retreat: once per turn (`!state.has_retreated`, `src/hooks/retreat.rs:15-28`, reset every turn
  in `end_turn_maintenance`); blocked by Asleep/Paralyzed
  (`special_condition_blocks_attack_or_retreat`, `:32-34`), no Bench, not enough Energy (gated in
  move-generation), Fossil Active (`active.is_fossil()`, `:22`); the new Active is chosen by the
  player (one `Retreat(index)` action per Bench slot); retreat doesn't end the turn (only Attack
  sets `end_turn_pending`); switching effects (`Activate`/`Promote`, mapped to
  `apply_retreat(..., is_free: true)`, `src/actions/apply_action.rs:773-780`) skip the
  `has_retreated` flag and the Energy-discard step entirely, matching "switching isn't your
  retreat." (See CT-2 for the Energy-choice gap within paid retreats.)
- Supporters: one per turn on any turn including the first (`can_play_support`,
  `src/hooks/core.rs:652-671`, no turn-count exception); Items unlimited (`can_play_item`,
  `:673-680`, only blocked by an explicit lock effect); Tools one per Pokémon by default, two with
  Revavroom's Dual Customization (`tool_capacity`, `src/tools.rs:112-117`); a Tool stays attached
  until the Pokémon leaves play and then goes to the discard pile
  (`discard_from_play`, `src/state/mod.rs:1246-1258`, extends `discard_piles` with
  `attached_tools`).
- Stadiums: same name can't be played, a different name replaces either player's
  (`can_play_stadium`, `src/move_generation/move_generation_trainer.rs:370-395`;
  `set_active_stadium_for_player`, `src/state/mod.rs:580-588`), one in play (`active_stadium` is a
  single `Option<Card>`, not a collection). (See CT-3 for the missing one-*play*-per-turn limit.)
- Attacking ends the turn and nothing else is offered afterward: `end_turn_pending` is set only on
  `SimpleAction::Attack` (`src/actions/apply_action_helpers.rs:1020-1026`), and
  `generate_possible_actions` collapses to `[EndTurn]` once it's set and the move-generation stack
  is empty (`src/move_generation/mod.rs:56-63`) — any of the attack's own follow-up effects still
  resolve first via the stack, matching "the attack resolves completely, then nothing else." Attack
  cost: `contains_energy`/`energy_missing` (`src/hooks/core.rs:1933-1969`) matches typed
  requirements first, then lets *any* remaining attached Energy (of any type) pay Colorless
  symbols — correct Colorless-is-any-type semantics.
- Turn limit: `advance_turn` (`src/state/mod.rs:1180-1202`) increments `turn_count` and sets
  `GameOutcome::Tie` once it exceeds 30, counting both players' turns (incremented on every turn
  transition, matching the in-app "Current turn" counter). This only runs *after* the just-ended
  turn's Checkup has fully resolved (`finish_turn_after_checkup` calls it, and is itself called
  after `apply_pokemon_checkup`, `src/actions/apply_action_helpers.rs:114-129`), and the live
  mutation explicitly checks `if state.is_game_over() { return; }` both right after the Checkup
  and before ever calling `advance_turn` (`:116-126`), with the comment "A Checkup result ends the
  game before another turn or its abilities. In particular, advancing past turn 30 must not
  replace that result with Tie." So a Knock Out in turn 30's own Checkup (e.g. the winning point)
  correctly stands and is not overwritten by the turn-limit Tie.
- Knock Outs / points: `get_knockout_points` (`src/models/card.rs:204-216`) returns 1 for a
  regular Pokémon (including Fossils, which fall through to the `else` branch since they're never
  `is_mega`/`is_ex`), 2 for ex, 3 for Mega ex. Points are awarded to `(ko_receiver + 1) % 2` —
  the opponent of whoever *owns* the Knocked-Out Pokémon — independent of `attacking_ref`, so a
  self-inflicted KO on your own Bench still scores your opponent
  (`src/actions/apply_action_helpers.rs:687-707`). Multiple simultaneous KOs each score
  individually (the `loop { wave = get_knocked_out(state); ... }` structure,
  `:669-773`). Self-discarding a Fossil (`apply_discard_fossil`,
  `src/actions/apply_action.rs:1061-1069`) calls `discard_from_play` directly, never
  `handle_knockouts`/`award_points` — no points for a non-KO discard.
- Winning/ties: checked against known issue #2 (points-checked-before-empty-board,
  `src/actions/apply_action_helpers.rs:802-829`) — unchanged from what's already documented, not
  re-reporting.
- Promotion: owner chooses from the generated `Promote` action set
  (`trigger_promotion_or_declare_winner`, `src/state/mod.rs:1355-1404`); triggered immediately for
  any Active-slot Knock Out via the same `handle_knockouts` used for attack damage, Ability damage
  and HP-bonus removal (all funnel through `apply_common_action_suffix`'s catch-all
  `handle_knockouts` call, `src/actions/apply_action_helpers.rs:1003-1027`, or the specific
  callers listed under CT-4); a Bench Knock Out scores a point with **no** promotion call
  (`if ko_pokemon_idx != 0 { continue; }` before the `trigger_promotion_or_declare_winner` call,
  `:836-842`). Double-KO promotion order: unchanged from known issue #3 (goes by seat), not
  re-reporting.
- Pokémon Checkup internal order (Poisoned → Burned → Asleep → Paralyzed) matches the official
  order exactly (`apply_pokemon_checkup`, `src/actions/apply_action_helpers.rs:237-324`); Paralysis
  is only checked for the player whose turn just ended (`collect_checkup_targets`,
  `:205-235`, `player == state.current_player`), matching "recovers after its owner's next turn."
  (See RQ-1 for the one genuine open question inside this function.)

## Not finished / not probed further
- CT-4 (Fossil/Basic `Place` into an empty Active slot outside setup) is argued from reading, not
  from a probe; I judged it very likely dead code and didn't spend a probe confirming that no KO/
  removal path skips `trigger_promotion_or_declare_winner`.
- I did not re-verify the already-known damage-order bug (README item 1,
  `hooks/core.rs` ~1705) or the double-KO-by-seat bug (README item 3) — out of scope to re-check,
  not changed as far as this audit went.
- I did not audit `src/hooks/attacks/*`, `abilities/*`, or any specific card's Trainer/Ability
  implementation — that's other agents' scope per the brief.
