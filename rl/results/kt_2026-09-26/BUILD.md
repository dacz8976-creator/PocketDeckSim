Decision this informs: kt's tables (kt3, then kta3, ktb3 and ktc3, on the table's deals) and their reading by the laptop under rule v2 and the reserve route (README "FOOTPRINT AND ROUTES"). This note records the build they run on. Build commit 43cef0b: the official engine (main 83e17ae) plus kt's code (ed81c8b; 92c4563 restores two files' Windows line endings; 43cef0b adds the review's tests). The scan at 43cef0b has sha256 d63f66b47bf76aed8ec38f93511cb0b339deca770d8e20528aa6c70b391de21f.

Seeds: the identity checks use the table's deals only (72,000,000 + pairing × 10,000 + i, even i = first-named deck in seat 0).

# kt: the build (Sept 27)

## Dustin's go-ahead

- **Sept 27: build kt now, as registered, with Bench Poncho left for its own amendment later.** The laptop recommended the same: "kt go ahead as registered while holding Bench Poncho for a separate amendment". That settles section 8, item 2 (kt's registration) for the build.
- Nothing in the registration changed. No kt table game has been played; the tables wait for Dustin's word.

## Protective Poncho: not covered (a named gap)

The laptop asked whether kt's Tool valuation covers Protective Poncho. **It doesn't.**

- **What kt does with it.** The registration gives Poncho 0 on both sides, on the Active or the Bench (switch 2).
  - The reason there: kp's clock only counts hits on the Active. Counting hits on the Bench is kd's "reach" change. kd3's readings tie Lucario's drop to how kd's clock chose a Bench-only sniper (Hitmonlee) as the main threat (`../kd_2026-09-25/README.md`, line 137). Bench-hit pricing is left for a later candidate of its own.
  - In the code, the only scoring that reads Poncho is kd's Bench-hit path (`persistent_defender_damage` with `DefenderHit::Benched`, used by kd's clock). kd's features are off in kt.
- **What that means in play.**
  - The flat +10 for any Tool on the Active is gone, so kt no longer puts Poncho on the Active, where it does nothing. The Trainer audit found 492 of 494 Ponchos there (`../trainer_audit_2026-09-25/README.md`).
  - But a Tool worth 0 still costs a card from hand (the hand-size term, weight 1). So kt stops playing Poncho altogether, even on the Bench, where it works. The registration predicts this: Lucario's Poncho plays fall from 68% of offered turns to near 0.
- **Dustin's own play.** The blind quiz found Dustin plays free, no-downside Tools first, Poncho twice: "Protective poncho on a bench riolu has no downsides" (`../blind_quiz_2026-09-25/RESULTS.md`). kt won't make that play. kt also doesn't change the order in which the bot plays cards within a turn.
- **Adding it** needs a dated amendment before any kt game, or a later candidate. Nothing was added.

## What was built

- **Four codes, each switch behind its own `EvalFeatures` flag** (`engine/src/players/value_functions.rs`):

  | code | switch 1 (`defender_cuts`) | switch 2 (`tool_by_holder`) | switch 3 (`counter_damage`) |
  |---|---|---|---|
  | `kt<N>` | on | on | on |
  | `kta<N>` | on | | |
  | `ktb<N>` | | on | |
  | `ktc<N>` | | | on |

  - All four are kp<N> otherwise: k's blind search, PublicPricingPlayer, kp's evaluator. kq's, kd's, kpr's, koa's and kpf's features are off.
  - With every switch off, each is kp. A test checks the flags; another checks the values on played positions (below).
- **Switch 1: the defender's temporary cuts and damage-cut Tools, in the threat clock (both sides).**
  - Two new engine hooks in `hooks/core.rs`, next to `persistent_defender_damage`:
    - `temporary_defender_reduction(state, victim owner, victim, attacker, attack, turn)`: the turn effects registered for that turn (Jasmine, Cheren, Blue: their scope and only-from-ex conditions), the victim's own `ReducedDamage` and `ReducedDamageFromEx` still live on that turn (Stiffen, Steel Wing), and Metal Core Barrier only on the holder's opponent's next turn (the engine discards it at the end of that turn, hit or not).
    - `permanent_tool_reduction(state, victim owner, victim, attack)`: Heavy Helmet (at the current Retreat Cost, as the Active) and Steel Apron, as `persistent_defender_damage` takes them off.
  - **The timing is the clock's own.** f = the turn the clock already puts the threat's first hit on: its next turn, plus two turns per missing Energy after the first attach, from the clock's own missing count, whatever the threat's slot. This is kq's `first_attack_turn` arithmetic, now its own function (`owner_next_turn`, `first_attack_turn_number`) so a Benched threat uses it too.
  - **The hits.** The clock's first hit does damage − temporary − permanent; every later hit does damage − permanent, for each victim. Hits to a knockout: `ko_turns_after_first_attack(hp, first, later)`, or kp's ceil(hp / damage) when the two are equal.
  - Weakness is not taken over (kd's term). Where the victim is Weak, the engine's cut lands on a bigger number than the clock's estimate, so kt under-counts the cut there.
- **Switch 2: the flat +10 for a Tool on the Active is 0 (both sides).** Every other term is unchanged, so a Tool counts only through what already reads it: HP Capes through HP, Balloon and Boat through the own Active's Retreat Cost, damage cuts through switch 1, Rocky Helmet through switch 3.
- **Switch 3: damage back to the attacker, in the holder's own clock (both sides).**
  - c = `get_counterattack_damage` of the holder H, the side's Active: Rocky Helmet, `Counterattack` (Spike Armor) and `CounterattackDamage` Abilities.
  - T, the other side's Active, loses c × k HP in our clock, and our hits on it are counted again once. k = min(n_ours − 1 + s, n_theirs):
    - n_ours is our clock's hits on T and n_theirs the other clock's hits on H, both without the cut;
    - s = 1 if T's owner is to move (T attacks first), else 0.
  - Only when T is both the other side's threat in its own clock and our clock's first victim. A Benched threat hasn't hit H.
  - Poison Barb is not in this candidate.
- **Parser** (`players/mod.rs`): `kta`, `ktb` and `ktc` before `kt`, and all four before `k`. No existing code starts with "kt": before the change, "kt3" fell into k's branch and was rejected. `kt13` is depth 13; `kt1a`, `kt`, `kta` and `ktd3` are rejected.

## Choices the registration left to the build

Each is the plainest reading, stated so the reading can judge it. None adds a parameter.
- **"Never."** A victim that no hit after the first can damage (a Heavy Helmet against a 20) makes the clock 30, kp's own "no Pokémon can deal damage" number. kp doesn't cap finite clocks at 30, so neither does kt: a finite clock over 30 can outrank "never", in kp's clock as in kt's. Games end in a tie after turn 30. The review found one case (three Snorlax with Heavy Helmet against Pidgey is 39); no table list carries Heavy Helmet.
- **f for a threat one Energy short.** kp's clock counts each missing Energy as a turn before the first hit; kq's arithmetic, which the registration names ("first_attack_turn is extended ... to any slot"), lets an Energy attached on the threat's turn be used the same turn, as Pocket allows. kt follows kq's: a threat 1 Energy short with this turn's Energy still in the Zone meets a cut live on its next turn.
- **The first hit** is the clock's first victim's: the Active, or the first benched victim when there is no Active.
- **An attack whose text ignores effects on the opponent's Active** (Sawk's Brick Break, Morgrem's False Surrender) gets no temporary or permanent cut, as in `modify_damage` and `persistent_defender_damage`.
- **The threat's form.** Only-from-ex conditions read the form the clock's threat attacks as (kd's `kd_attacker`). Forms are read only for the evaluating player's own threats, so nothing of the opponent's hand or deck is read.
- **Switch 3's s** is "T's owner is to move and can still attack this turn", the same test kq's timing uses. The cut is 0 when either hit count is infinite (switch 1's "never"), and k is floored at 0.
- **Switch 3 counts c on every one of the k hits**, as registered. Two cases where the engine does less, neither in the table lists: Spike Armor's `Counterattack` lasts one opponent turn; and a hit cut to 0 fires no Rocky Helmet ("if ... damaged").
- **The `status-clock` diagnostic build** (not the official one) adds its Sleep and Paralysis delay to the clock but not to f.
- **Speed.** A Pokémon with no Tool attached skips the Tool checks. Otherwise the Tool checks are the engine's own (`has_tool`, `tool_count`); timing.txt decides whether they must be rewritten before the table (registration step 4).

## Engine code shared with other bots

Each change below runs for every bot, so the identity replays check it:
- `get_turn_effect_damage_reduction` takes a turn. `modify_damage` passes the current one, which is what it read before.
- Metal Core Barrier's check is its own function (`metal_core_barrier_reduction`), called by `modify_damage`'s stage as before.
- The clock's threat scan is its own function (`threat_candidates`), read by kp's clock and kt's. The `status-clock` diagnostic's extra turns moved into `status_clock_turns` (0 in every normal build).
- kq's first-attack timing is `owner_next_turn` and `first_attack_turn_number`, called by kq's `first_attack_turn` with the same numbers.
- `extract_features` takes an optional clock, given only by kt, kta and ktc.

## Tests

- **The hooks, pinned to the engine** (`hooks/core.rs`, `temporary_defender_reduction_tests`):
  - for the current turn, `temporary_defender_reduction` equals `modify_damage`'s own card-effect, turn-effect and Barrier stages, and what `modify_damage` takes off: a ReducedDamage effect, ReducedDamageFromEx against an ex and not otherwise, Blue's all-Pokémon cut, the only-from-ex cut, a named scope on and off its names, a typed cut on and off its type, the Barrier on a [M] holder and not otherwise, and all of them at once;
  - for later turns: a 1-turn effect is live this turn and the next, not after; a turn effect only on the turns it is registered for; the Barrier only on the holder's opponent's next turn, whoever is to move;
  - an attack that ignores effects on the opponent's Active gets no cut, as in `modify_damage`;
  - `permanent_tool_reduction` equals what `persistent_defender_damage` takes off for Heavy Helmet (Retreat Cost 3 and 1) and Steel Apron ([M] and not), and leaves the Barrier to switch 1's temporary part.
- **The switches in the clock and the score** (`players/value_functions.rs`, `kt_tests`):
  - a cut live on the threat's first attack turn softens the first hit only (Snorlax at 100 HP against 50s: 2 hits become 3), and not when the threat is 2 Energy short or the effect is gone by then; only the clock's first victim gets it;
  - the Barrier on the holder's opponent's next turn, with either player to move, and not for a threat that attacks later;
  - Steel Apron on every hit, per victim; Heavy Helmet against a 20 is "never" (30);
  - a Benched threat timed by its own missing count;
  - Rocky Helmet: 40 off with the holder to move, 60 with the threat to move, capped at the hits that knock the holder out (20); nothing for a Benched threat or without counter-damage; the opponent's Helmet cuts in the opponent's clock;
  - switch 2 drops exactly the flat term (10 from each side), and kta and ktc keep it;
  - the presets: each code sets its switches only, and no other preset sets them.
- **Against kp on played positions.** 12 random games over four pairings of the table lists: at every position, kt's clock with switch 1 off equals kp's clock exactly, for both sides and both zone permissions; and wherever nothing kt reads is on the board (no Tool, no cut effect, no counter-damage), kt, kta, ktb and ktc equal kp's value exactly.
- **The parser**: kta3, ktb3, ktc3, kt3, KT3 and kt13 parse; kt1a, kt, kta and ktd3 are rejected; t3, k3, kq3, kd3, kpr3 and kpf3 are unchanged.
- **From the review (43cef0b):** with no Active, the first benched victim takes the cut; an evolved threat is judged as the form it attacks as (an only-from-ex cut applies to Mega Altaria ex, not to its Swablu); an attack that ignores effects on the opponent's Active gets no cut in the clock (Sawk's Brick Break); switch 3's s is 0 when the threat's owner has already attacked this turn.
- **Full suite:** 1,963 passed, 0 failed (16 new). Clippy reports nothing in the new code.

## Everything after the last full replay (the kt-only diff)

The last full replay is the official engine's (main 83e17ae; k3 and kp3 14,000 of 14,000 against af8489f's references, the laptop's check). Since then `engine/` has two commits, both kt's: ed81c8b (the code) and 92c4563 (line endings only). `git diff 83e17ae 92c4563 -- engine/` touches four files:

| file | change | runs for |
|---|---|---|
| `hooks/core.rs` | the two new hooks and their tests | kt, kta (switch 1) |
| | `get_turn_effect_damage_reduction`'s turn; the Barrier's own function | every bot (identity) |
| `hooks/mod.rs` | exports the two hooks | none |
| `players/mod.rs` | the four codes, their parser branch, their player arm, parser tests | kt codes only |
| `players/value_functions.rs` | the presets and four value functions; kt's clock, `kt_clocks`, `counter_cut`; the switch 2 weight; tests | kt codes only |
| | `threat_candidates`, `status_clock_turns`, `owner_next_turn`, `first_attack_turn_number`; `extract_features`' optional clock | every bot (identity) |

## Identity at the build (registration step 3)

**kq3's reference.** No kq3 table existed at the official engine (the Sept 26 replays ran kq3 on 40 deals only), so the official program (`rl/engine-2026-09-27/legality_scan`, e6ab9a9d) played kq3's 14,000 table games first (`identity/official_kq3_500.jsonl`).
- It ran clean (no rule findings). Its first 40 deals equal the Sept 26 kq3 reference (`../rules09_fixes_2026-09-26/af8489f_kq3_40.jsonl`) in moves and choices, 1,120 of 1,120 (840 in pairings 0-20, 280 in 21-27).
- **Pairings 21-27 were lost and re-run.** The run's output for them went to a deleted file: while it ran, a `git stash` (to rebuild the scan without the review's tests) swapped the file under it. Each game is fixed by its seed, so the official program played pairings 21-27 again with `--pairings 21,...,27`, and the two parts are joined. The first part's `.txt` summary stops at pairing 20; the second part has its own.

**The identity checks** (`identity/run_identity.sh`, `identity/compare.py`, `identity/identity_check.txt`), all at 43cef0b (scan d63f66b4…), on the table's deals. **Every check passes.**

| check | result |
|---|---|
| k3, all 500 deals, vs `af8489f_k3_500` | equal in moves, choices, openings and results: 14,000 of 14,000; clean |
| kp3, all 500 deals, vs `af8489f_kp3_500` | 14,000 of 14,000; clean |
| kq3, all 500 deals, vs the official program's `official_kq3_500` | 14,000 of 14,000; clean |
| kd3, 40 deals, vs `af8489f_kd3_40` | 1,120 of 1,120; clean |
| kpr3, 40 deals, vs `af8489f_kpr3_40` | 1,120 of 1,120; clean |
| kp3, 40 deals (the timing run), vs `af8489f_kp3_500` | 1,120 of 1,120; clean |

**Timing** (registration step 4): kt3's 40-deal run took 221 s against kp3's 210 s on the same quiet machine, 1.05×, inside the 1.25× budget. The Tool checks stay as they are.

**Smokes** (40 deals, all 28 pairings; every run clean). Games whose choices differ from kp3's on the same deals. This is a preview only; the footprint is measured on the tables and read first.

| code | choices differ from kp3 | where |
|---|---|---|
| kt3 | 736 of 1,120 (65.7%) | every cell |
| kta3 (switch 1) | 16 (1.4%) | only Suicune's cells (Stiffen), as registered |
| ktb3 (switch 2) | 747 (66.7%) | every cell |
| ktc3 (switch 3) | 98 (8.8%) | only Blaziken's cells (Rocky Helmet), as registered |

No kt table game has been played. The tables wait for Dustin's word, which also depends on which pilot kt is read against: the registration is re-issued if the pilot changes from kp3.

## Files

- `identity/`: `run_identity.sh`, `compare.py`, `identity_check.txt`, `timing.txt`; the raw outputs `43cef0b_{k3,kp3,kq3}_500`, `43cef0b_{kp3,kt3,kta3,ktb3,ktc3,kd3,kpr3}_40` and `official_kq3_500` (with its pairings 21-27 summary).
