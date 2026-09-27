Decision this informs: kph's reading by the laptop (REGISTRATION.md section 5: footprint first, then the mechanism check, the Rayquaza traces and the 45 cells). This note records the build it reads. Build commit 7e7d864: the official engine's source (main 83e17ae) plus the player code built since on this branch (kt, kog, kph; each checked by identity runs), `cargo build --release --example legality_scan` (the `--pairs` option is in it), scan sha256 41a65af46bc8a42824f19dbfdc0ddbaaab2700c2c2305ff7f85cc38b97aac67d.

Seeds: the identity checks use the table's deals only (72,000,000 + pairing × 10,000 + i, i < 40, even i = first-named deck in seat 0).

# kph: the build (Sept 27)

## What was built

- **Base: kpg** (kp + F as built at 9bffbda). The composed pilot (kog: kp3 + koa's switch A + F; `../kog_2026-09-27/BUILD.md`) has passed its identity checks, but its composition check also needs the laptop's 45-cell table, which hasn't run. So kph is built on kpg, as the registration says for that case. R′ on kog is one more preset when the laptop wants it, with the composed-base identities of section 4.
- **Codes** (`EvalFeatures` flags in `players/value_functions.rs`; codes in `players/mod.rs`):

  | code | F | R | fix A (`evolution_steps`) | fix B (`zone_to_bench`) |
  |---|---|---|---|---|
  | `kph<N>` | on | on | on | on |
  | `kpha<N>` (diagnostic: A only) | on | on | on | |
  | `kphb<N>` (diagnostic: B only) | on | on | | on |
  | `kpf<N>` (kph with A and B off) | on | on | | |
  | `kpg<N>` (kph with R off) | on | | | |

  - **Parser:** `kpha`, `kphb` and `kph` are parsed with `kpf` and `kpg`, before `kp` and `k`; `kpha` and `kphb` come before `kph`. No existing code starts with "kph". Tests: kph3, KPH5, kpha3, kphb3 parse; kph, kphx, kpha and kphc3 are rejected; kpf3, kpg3, kpr3 and kp3 parse as before.
- **R** is kpr's projection exactly as in kpf (its horizons and amendment 5). Two refactors, checked by the identity runs:
  - The turn list became its own function (`projection_turns`), so fix B reads the same turns.
  - `pokemon_online_score` now takes its parts from `online_yardstick`: the target card's stage, the yardstick's cost and the missing Energy. The arithmetic is the same.

### Fix A: evolution steps in the projected readiness

- Only in the projected branch of `calculate_active_pokemon_online_score` (now `calculate_active_pokemon_online_score_ex`), through a separate function, `evolution_aware_online_score`. `pokemon_online_score` is unchanged, since kq's bench score also calls it.
- The target is the card `pokemon_online_score` already measures against: the highest evolution in the owner's deck and hand, or the card itself. steps = target stage − the Active's stage, saturating.
- An attack costing nothing reads 1.0, the existing early return.
- **steps > 0:** clamp((total − missing − steps) / total, 0, 1) on R's projected Active. The score is the larger of that and the unprojected reading (kp's).
- **steps = 0:** R's projected reading exactly, with no max.
- On the opponent's side `public_only` hides the deck and hand, so the target is the card itself and steps = 0: A never changes the opponent's reading. A test checks this with a Mega Altaria ex hidden behind the opponent's Swablu.
- **Setup.** Nothing is projected during setup (turn 0), so there A equals R and kp.

### Fix B: the Zone Energy to a Pokémon that can reach the Active

- The clock with a horizon is min(clock with no projection, clock with the Active projected as R does, and, when the Active can retreat, the minimum over benched s of the clock with s given the Zone Energy only) (`calculate_turns_until_opponent_wins_projected`).
- The scan's projection parameter is widened to (horizon, slot, Zone-only) (`Projection`; kpr's is `Projection::active`, slot 0 with R's full projection).
- **What s gets** (`projected_zone_energy`): exactly the Zone terms of R's turn list, with the same running test (`end_turn_scored_before_it` included). That is this turn's `current` while the side's turn is running, and next turn's `next` as R's horizon has it.
  - No `NoEnergyFromZoneToActive` check: it blocks only the Active.
  - No Ability Energy and no discard-pile Energy.
  - Nothing at setup.
- **Qualifying** (`bench_can_reach_active`), read from the board, the same rule for both sides with no Switch or X Speed assumed:
  - **Payment:** the Active's board Retreat Cost, `get_board_retreat_cost_for_player` (without this turn's discounts), is at most the Energy attached to it. A cost of 0 always passes.
  - **Not blocked:** kq's retreat block (Asleep or Paralyzed, `NoRetreat`, a Fossil).
  - **Already retreated:** see the choice below.
  - With no Active (a promotion pending), any benched Pokémon can be the next Active, so B applies.
- Qualifying depends on the Active only, so all benched Pokémon qualify or none do.
- Both sides, each at its own horizon: the own side through its next turn, the opponent's at its next attack. The opponent's side reads only its board.

### One choice the registration's wording left open: "already retreated"

The registration: "when the credited attack is this turn (the side's turn is running), also require `!state.has_retreated`." The build reads "the credited attack is this turn" as "the turn list holds this turn only". That is the opponent's side at its next attack while its turn is running, which is the usual leaf.

On the own side, read through its next turn, the list holds this turn and next turn while the turn is running. The attack can then be next turn, after a retreat then, which this turn's retreat doesn't rule out. So `has_retreated` doesn't block it there.

This is what makes the registration's two Q10 boards come out as written, mid-turn, the way the position arose (X Speed played, a retreat made):
- Shuckle ex with no Energy is not credited, because its board cost of 1 is unpaid.
- Shuckle ex holding a [G] is credited, although `has_retreated` is true.

Read literally ("the side's turn is running"), the positive control would not be credited mid-turn. If the laptop prefers the literal reading, it is a one-line change, `attack_this_turn = running`.


## Tests (REGISTRATION.md section 4)

Each constructed board states its timing: mid-turn (the side to move, its turn running), or the leaf after player 0's EndTurn (player 1 to move, its turn running).

| test | board and timing | result |
|---|---|---|
| A, steps = 0 | on played positions (12 random games, 4 pairings), both players, both horizons, both zone permissions | A = R exactly wherever there is no step |
| A, steps > 0 | same | A never below the unprojected reading |
| Swablu | mid-turn; Swablu with [P], [P] in this turn's Zone; Mega Altaria ex ([P][P]) the deck's only evolution | unprojected 0.5, R 1.0, A 0.5 |
| Bare Riolu | Riolu B3 079 with nothing; Mega Lucario ex ([F][F]) the deck's only evolution; [F] now and next. The yardstick is [F][F], as the registration assumed | after EndTurn: R 0.5, A 0. Mid-turn: R 1.0, A 0.5 |
| B, never slower | kpr's test (`the_clock_never_gets_slower_for_the_projection`) with a B case: Deino with nothing (cost 1 unpaid), Deino holding a [D], and an empty Bench; and on played positions | Deino with nothing: 3, as R. Deino holding [D]: R 7, B 2. Empty Bench: R. On played positions B is never slower than R, and equal to it with an empty Bench |
| B, opponent | the usual leaf: player 1's Bonsly (cost 0) in front, Bulbasaur with [G] benched, [G] in its Zone | the Active and the benched Bulbasaur each get one [G]; the opponent's clock on Snorlax 13 → 4; with a retreat already made this turn, not credited (13) |
| Dustin's Q01 | after EndTurn: Bonsly (cost 0) and Mega Lucario ex with [F], [F] next, against Bulbasaur | keep and swap both read 1 under kph; under R, keep 7 and swap 1 |
| Dustin's Q10 | mid-turn: Shuckle ex in front with nothing, Vespiquen ex benched with [G], [G] now and next, X Speed's turn effect, `has_retreated` true | this turn's cost 0 (X Speed), board cost 1, unpaid: not credited, the clock is R's |
| Positive control | the same board, Shuckle ex holding a [G] | credited: 1 hit, faster than R |
| F on | mid-turn: Bonsly in front, Charmander benched, [R][R] in the discard pile, Flame Patch in hand (F live) | with nothing in the Zone B gives nothing, so kphb = kpf's value; with [R] in the Zone B gives exactly that [R], and the pile F reads is untouched |
| Opponent board-only | after EndTurn: the opponent's Swablu with [P] and Bulbasaur with [G] benched; Mega Altaria ex, Ivysaur or Squirtle hidden in its hand or deck | kph's value is the same whatever is hidden |
| Switches | presets and played positions | kph with A and B off is kpf's preset; A only is kpha's, B only kphb's; with R off, kph's value is kpg's on every played position |
| Parser | | kph3, KPH5, kpha3, kphb3 parse; kph, kphx, kpha, kphc3 rejected; kpf3, kpg3, kpr3, kp3 unchanged |

**Full suite:** 1,974 passed, 0 failed (10 new tests, and the B case added to kpr's test).
