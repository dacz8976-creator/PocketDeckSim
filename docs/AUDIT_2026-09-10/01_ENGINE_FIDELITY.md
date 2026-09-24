# 01 — Engine fidelity: what the simulator actually does, and what that does to every ranking

Tags: **[V]** verified by reading the cited file or by executing code; **[I]** inferred; **[U]** uncertain. All paths are relative to `C:\Users\dacz8\Projects\Pocket Deck Lab\deckgym-fork-s193\` unless stated. Line numbers are from the tree as it sat on disk on 2026-09-10 (source mtimes through 2026-09-08 04:41Z, `Cargo.toml` version `0.1.0-pdl.eval18`).

## 1. Reproducible probe (run this yourself)

I compiled the fork exactly as it sits on disk and ran a 3-question integration test, then ran the identical test against upstream `bcollazo/deckgym-core` at commit `fda48391` (2026-08-30). Full source is in Appendix A; output:

```
FORK (dev checkout, eval18 era):
PROBE1 status=none      attack_actions_offered=1 retreat_actions_offered=1
PROBE1 status=Asleep    attack_actions_offered=1 retreat_actions_offered=1   <- should be 0 / 0
PROBE1 status=Paralyzed attack_actions_offered=1 retreat_actions_offered=1   <- should be 0 / 0
PROBE2 paralyzed_before_end_turn=true  paralyzed_at_start_of_victim_turn=false  <- should be true
PROBE3 confused: 60 attacks, 29 succeeded, 31 failed, 0 self-damage  <- CORRECT for Pocket

UPSTREAM (bcollazo/deckgym-core HEAD 2026-08-30): PROBE1 and PROBE2 identical; PROBE3 27 succeeded / 33 failed / 0 self-damage (same conclusion).
```

Rules reference used (Pocket-specific, pokemon-zone.com "How to play" guide, special-conditions section; corroborated by Codex's own `ALTARIA_RULES_POLICY_SCREEN.md`):
- Asleep: cannot attack or retreat; owner flips at each Checkup, heads recovers.
- Paralyzed: cannot attack or retreat; recovers at the Checkup **after its owner's next turn** (i.e., it costs the victim one full turn).
- Confused: on attack, flip; tails = attack does not happen, turn ends. **No self-damage in Pocket** (the 30-to-self is the physical TCG rule).
- Asleep/Paralyzed/Confused are mutually exclusive; the newest replaces the others. Poison and Burn stack with anything.

## 2. Findings, with code

### 2.1 Asleep / Paralyzed Pokémon can attack — [V]
`src/move_generation/attacks.rs:14-76` (`generate_attack_actions`) checks Fossil (`:19`), `CardEffect::CannotAttack` (`:24-30`), Seal of Antiquity (`:34`), per-attack restrictions, usage conditions, and energy cost. It never calls `is_asleep()` or `is_paralyzed()`. `Game::play_tick` (`src/game.rs:200`) consumes this menu unfiltered. No execution-time check exists in `apply_action.rs` or `apply_attack_action.rs` either (grep for `is_asleep|is_paralyzed` across `src/` finds only checkup collection, conditional-damage lookups, and cure logic).

### 2.2 Asleep / Paralyzed Pokémon can retreat — [V]
`src/hooks/retreat.rs:15-25` (`can_retreat`) checks `has_retreated`, `CardEffect::NoRetreat`, and Fossil. Nothing else.

### 2.3 Paralysis is cleared one Checkup too early — [V]
`src/actions/apply_action_helpers.rs:304-310` clears every paralyzed Pokémon unconditionally at every Checkup. There is no duration field anywhere in `PlayedCard` (`src/state/played_card.rs:49-58` stores five independent bools). Sequence: A paralyzes B's Active during A's turn → A ends turn → Checkup runs before `advance_turn` (`:88-134`, `src/state/mod.rs:1180`) → B's Active is un-paralyzed → B's turn starts free. Probe 2 shows exactly this. Combined with 2.1/2.2, **Paralysis has zero mechanical effect on legality in this engine.** Sleep's timing is correct (a Checkup flip immediately is right for Pocket), but because of 2.1/2.2 it is also non-blocking.

### 2.4 Asleep / Paralyzed / Confused are not mutually exclusive — [V]
`State::apply_status_condition` (`src/state/mod.rs:1125-1177`) handles immunities then calls `set_status_raw` (`played_card.rs:411-424`), which just sets one bool. Nothing clears a conflicting member of the trio. Codex's Sept 8 inventory (`qualification/RULES_AND_COVERAGE.md`) lists this as an "unfixed exclusive-condition replacement gap." Lower impact than 2.1–2.3 but real.

### 2.5 Confusion — correct for Pocket — [V]
`src/actions/attack_outcome.rs:471-488` (`prepend_nullifying_coin_gate`): 50% no-op, 50% normal attack; no self-damage. That matches Pocket. (A Sonnet scout flagged this as a bug using the physical-TCG rule; I checked two Pocket-specific sources and rejected the finding.)

### 2.6 What is correct — [V]
Poison 10 / Burn 20-then-flip per Checkup, both actives, official order Poison→Burn→Sleep→Paralysis (`apply_action_helpers.rs:244-310`); turn-by-turn Poison test exists (`src/game.rs:474-513`). Status cleared on retreat/bench (`apply_action_helpers.rs:893-903`) and on evolution (`apply_action.rs:1442-1481`). First player cannot attach Energy-Zone energy on turn 1 (structural, `state/mod.rs:748-770`). No evolution on either player's first turn (`is_users_first_turn`, `state/mod.rs:1221`).

## 3. Provenance — this bug predates the project [V]

Codex's `Boss Folder/competitive-deck-study-2026-09-08/round-robin-checkpoint/reports/diagnostics/STATUS_BUG_PROVENANCE.md` did a read-only git-object audit: the attack-generator entry path blames to upstream's initial commit `ca79e6ac` (2025-03-17) and the retreat predicate to `55d80b90` (2025-03-29); byte-identical in s120 (installed runtime, Aug 19) and s197. My compile of upstream HEAD (2026-08-30) confirms it is still there upstream. **deckgym.com's public rankings therefore carry the same defect [I].** Upstreaming the fix is a real contribution and is small: Codex's `status1/SOURCE_CHANGES.json` lists four source files (`apply_action.rs`, `hooks/mod.rs`, `hooks/retreat.rs`, `move_generation/attacks.rs`) plus one test file and two fixtures.

## 4. The fix exists and is not in the code you run [V]

- `status1` (Sept 8, 19:31Z file time): shared status predicate gating attack generation and retreat; 5 focused tests; 1,748 tests pass (`status1/README.md`).
- `paralysis1` (Sept 8, 21:09Z file time): corrected Paralysis lifecycle; 1,760 tests pass (`paralysis1/VALIDATION.json`).
- `competitive-deck-study-2026-09-08/README.md:16`: "The shared development checkout and historical installed runtime were not replaced by these isolated candidates."
- The dev checkout I compiled has source mtimes ending 2026-09-08 04:41Z — before either candidate — and fails the probe. The installed runtime is s120k (`project_manifest.json`). So today there are at least four "engines": installed s120k (buggy), dev checkout eval18/19 (buggy), `status1` binary, `paralysis1` binary, none committed to git since 2026-08-22 (`deckgym-fork-s193/.git/logs/HEAD`; `RECOVERY_ASSESSMENT_2026-09-07.md:21-27` reports 461 of 465 tracked files modified, uncommitted).

## 5. Measured impact — it is not a rounding error [V]

Codex's paired before/after (identical lists, seeds, `k3`), `status1-study/analysis/STATUS_COMPARISON.md`:

| Sample | eval18 (buggy) | status1 (Sleep fixed) |
|---|---:|---:|
| Altaria/Espeon, 448 appearances | 153-294-1 (34.2%) | 204-243-1 (45.5%) |
| Altaria/Espeon, fresh 56 | 16-40-0 (28.6%) | 24-32-0 (42.9%) |
| altaria vs weezing (64 games) | 21.9% | 43.8% |
| altaria vs blaziken (64 games) | 43.8% | 59.4% |

Eleven points on a deck's aggregate, twenty-two on a matchup, from one rule. Every deck whose plan touches Sleep (Swablu/Altaria, Hypno lines, Igglybuff, Musharna, Snorlax walls, anything with "Asleep" in its text) or Paralysis (Electric attackers, Galvantula, Raichu Evoshock) was simulated with that axis switched off, on both sides of the table, in every historical ranking. Note the sign is not predictable: Weezing *lost* 3 points because its opponents stopped illegally attacking through Sleep.

## 6. The bot, and why the gap is bigger than rules [V/I]

- `k3` (default since §120/§132) uses a non-leaking `public_*` value function; the `e<N>` family is "deliberately left leaky: every historical ranking in this lab was produced with it" (`tests/value_function_hidden_info_test.rs:1-11` for the leak description, `:83-86` for the quote, which names `baseline_value_function`; written at §40, early Aug). meta4–meta6 rankings (e2/e3 bots) were therefore produced under hidden-information leakage [V]. meta7 ran `p3,p3` (`claims/done/meta7-baseline.claim:3`) and meta8's pilot is not stated in the files I read — whether those were leak-free at that date is [U]. meta9 used `k3` on s120k (non-leaky bot, buggy rules) [V].
- All single-value-function families are built with `opponent_ply: 0` (`src/players/mod.rs:314-385`) — the default bot searches its own turn only and never models the opponent's reply. This was finding E6 of `Boss Folder/ENGINE_AUDIT.md` (Sept 5) and remains open. [V]
- `players/mcts_player.rs` is 6 KB; the Claude ledger (§25) established the "m" bot was flat Monte Carlo, not MCTS, and far weaker than `e2`. [V, ledger]
- The ledger's own §74 shows the bot cannot pilot the Dragonair family at all (~20 pt under-rating) — a pilot-skill bias that no rules fix addresses. [V, ledger]

## 7. Simulator vs. reality — three independent measurements [V]

| When / source | What was compared | Result |
|---|---|---|
| Claude era §44 (`HANDOFF.md`) | 27 archetypes vs ~5,704 real trainerhill tournament games | correlation +0.14; wrong favored side 16/27 (59%); mean residual +16.5 pts (sim too high) |
| Claude era §43-E (`HANDOFF.md`) | 93 matchup cells vs the same tournament matrix | r ≈ 0.11; MAE 20.7 pts; wrong winner 45/93 (48%); sim spread 2.1× real (22.9 vs 10.7) |
| Codex 2026-09-08 (`EXTERNAL_GAP_UPDATE.md`, recomputed by me) | 8 top B4a archetypes, 28 cells, vs 900 real Limitless BO1 games | matchup r = 0.50 (eval18) / 0.56 (status1); MAE 15.5 pp; favored side correct 20/28; 6 cells off by ≥20 pp; **deck-level Spearman 0.21 / 0.23** (tie-corrected; Altaria and Vespiquen tie at 45.5 under status1) |

Deck-level aggregates from the Codex table (mean over 7 opponents):

| Deck | Real (Limitless) | Sim eval18 | Sim status1 |
|---|---:|---:|---:|
| blaziken | 60.5 | 64.5 | 62.3 |
| vespiquen | 53.5 | 46.0 | 45.5 |
| sceptile | 53.4 | 58.9 | 57.4 |
| hydreigon | 51.0 | 37.3 | 35.0 |
| altaria | 50.5 | 34.2 | 45.5 |
| lucario | 48.6 | 59.2 | 58.7 |
| suicune | 41.4 | 60.7 | 59.4 |
| weezing | 41.1 | 39.3 | 36.2 |

Caveats, in fairness: the external side is archetype-pooled over many exact lists and pilots of mixed skill, a partial 36-event BO1 cache, median n=28 per cell (sampling sd ≈ 9 pp on its own). But 15.5 pp MAE is well above that noise, and the deck-level ordering failure (Suicune +19, Hydreigon −14, Lucario +10) is not noise. **Conclusion: the simulator cannot currently be used to rank decks against each other.** It can, at best, compare two versions of the *same* deck under the *same* pilot.

## 8. Test coverage — the failure mode that let this live for six months [V]

The fork has hundreds of tests (Codex reports 1,748 passing). I found **zero** tests in fork or upstream asserting that an Asleep or Paralyzed Pokémon is denied its attack or retreat, and zero asserting Paralysis survives the first Checkup. Every status test asserts the *flag* (`assert!(state.get_active(1).is_paralyzed())`) and stops. `tests/mechanics/confusion_test.rs:144-190` defines failure as "opponent HP unchanged" and never inspects the attacker — it would pass either rule. The Poison turn-by-turn test (`src/game.rs:474-513`) shows the team knew how to write the right kind of test and simply never wrote it for Sleep/Paralysis. This is the "tests check the flag, not the effect" pattern; the conformance suite in file 03 is the gate.

## 9. What every historical number is worth

- meta4–meta6 (`e`-family, Sleep/Paralysis off): hidden-info leak plus rules defect. Not usable as rankings. [V] meta7–meta8 (`p3` and unrecorded): rules defect certain, leak status [U]. Not usable as rankings either way.
- meta9 (`k3`, s120k): non-leaky bot, rules defect still present, one-ply search. Directional at best; the ledger's own calibration track (`sim-spread-calibration`, §156–§163) found every arm's slope off by 2–5× against target 1.00. [V, ledger]
- eval18 panel (Codex, Sept 8): same rules defect; corrected in `status1` only for Altaria's sake; full corrected panel never run. [V]
- Any A/B where the swapped cards involve Sleep/Paralysis or where the opponent does: invalid. Same-shell A/Bs on unrelated cards: directionally informative only; the project's own most rigorous A/B (Xatu X Speed→Potion) flipped sign between its 576-game pilot and its 2,112-game replication (`deck-question-refresh-2026-09-08/RESULTS_BRIEF.md`). [V]

---

## Appendix A — probe source (drop into `tests/audit_status_probe.rs`, run `cargo test --test audit_status_probe -- --nocapture`)

```rust
//! Audit probe (2026-09-10). Each test passes on purpose so the output is visible.
use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    models::{EnergyType, PlayedCard, StatusCondition},
    test_support::get_initialized_game,
};

fn board(status: Option<StatusCondition>) -> deckgym::Game<'static> {
    let mut game = get_initialized_game(7);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![
            PlayedCard::from_id(CardId::A1035Charizard).with_energy(vec![
                EnergyType::Fire, EnergyType::Fire, EnergyType::Fire, EnergyType::Fire,
            ]),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
        vec![
            PlayedCard::from_id(CardId::A1053Squirtle),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
    );
    if let Some(s) = status { state.apply_status_condition(0, 0, s); }
    state.turn_count = 3;
    state.current_player = 0;
    game.set_state(state);
    game
}

fn count_actions(game: &deckgym::Game<'static>) -> (usize, usize, bool, bool) {
    let state = game.get_state_clone();
    let (_actor, actions) = state.generate_possible_actions();
    let attacks = actions.iter().filter(|a| matches!(a.action, SimpleAction::Attack(_))).count();
    let retreats = actions.iter().filter(|a| matches!(a.action, SimpleAction::Retreat(_))).count();
    let active = state.get_active(0);
    (attacks, retreats, active.is_asleep(), active.is_paralyzed())
}

#[test]
fn probe_1_can_asleep_or_paralyzed_active_attack_or_retreat() {
    for (label, status) in [("none", None), ("Asleep", Some(StatusCondition::Asleep)), ("Paralyzed", Some(StatusCondition::Paralyzed))] {
        let (attacks, retreats, asleep, paralyzed) = count_actions(&board(status));
        println!("PROBE1 status={label:<9} asleep_flag={asleep} paralyzed_flag={paralyzed} attack_actions_offered={attacks} retreat_actions_offered={retreats}");
    }
}

#[test]
fn probe_2_paralysis_duration() {
    let mut game = get_initialized_game(11);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![PlayedCard::from_id(CardId::A1035Charizard), PlayedCard::from_id(CardId::A1033Charmander)],
        vec![
            PlayedCard::from_id(CardId::A1053Squirtle).with_energy(vec![EnergyType::Water, EnergyType::Water]),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
    );
    state.apply_status_condition(1, 0, StatusCondition::Paralyzed);
    state.turn_count = 3;
    state.current_player = 0;
    game.set_state(state);
    let before = game.get_state_clone().get_active(1).is_paralyzed();
    game.apply_action(&Action { actor: 0, action: SimpleAction::EndTurn, is_stack: false });
    let after = game.get_state_clone();
    println!("PROBE2 paralyzed_before_end_turn={before} current_player_after={} paralyzed_at_start_of_victim_turn={}", after.current_player, after.get_active(1).is_paralyzed());
}

#[test]
fn probe_3_confusion_tails_self_damage() {
    let (mut self_dmg, mut fail_no_dmg, mut success) = (0, 0, 0);
    for seed in 0..60u64 {
        let mut game = get_initialized_game(seed);
        let mut state = game.get_state_clone();
        state.set_board(
            vec![
                PlayedCard::from_id(CardId::A1035Charizard).with_energy(vec![EnergyType::Fire; 4]),
                PlayedCard::from_id(CardId::A1033Charmander),
            ],
            vec![PlayedCard::from_id(CardId::A1033Charmander), PlayedCard::from_id(CardId::A1001Bulbasaur)],
        );
        state.apply_status_condition(0, 0, StatusCondition::Confused);
        state.turn_count = 3;
        state.current_player = 0;
        game.set_state(state);
        let hp0 = game.get_state_clone().get_active(0).get_remaining_hp();
        let def0 = game.get_state_clone().get_active(1).get_remaining_hp();
        game.apply_action(&Action { actor: 0, action: deckgym::test_support::attack_action(CardId::A1035Charizard, 0), is_stack: false });
        let s = game.get_state_clone();
        let def = s.in_play_pokemon[1][0].as_ref().map(|p| p.get_remaining_hp()).unwrap_or(0);
        if def < def0 || s.in_play_pokemon[1][0].is_none() || s.winner.is_some() { success += 1; }
        else if s.get_active(0).get_remaining_hp() < hp0 { self_dmg += 1; } else { fail_no_dmg += 1; }
    }
    println!("PROBE3 confused_attacks=60 succeeded={success} failed_with_self_damage={self_dmg} failed_with_NO_self_damage={fail_no_dmg}");
}
```

Expected after a correct fix: PROBE1 Asleep/Paralyzed → 0 attacks, 0 retreats; PROBE2 → `paralyzed_at_start_of_victim_turn=true`; PROBE3 unchanged (already correct).
