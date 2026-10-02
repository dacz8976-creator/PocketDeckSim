# Step 8c: the five unexplained lookahead games, a code read (laptop Opus subagent, Oct 1 night)

Read-only. The question, the coordinator's: can repair B change a k3/km3 search value with no counter the probes look for? Inputs:
- the candidate 5a18d31 (and the old engine/ tree 9c84fef);
- the probes `coin_probe.rs`, `coin_lookahead.py` and `vs_probe.rs`;
- Sonnet's 8c result (sonnet/trace-8c 37b49dd, `trace_8c_sonnet/diag7.txt`) and its traces.

No game was played for this note. Two checks at the end would settle it.

## Bottom line

**B explains all five, through a path neither probe reaches.**
- It isn't the four forecast wraps, and it isn't the value function. It's the queued snipe frame.
- When every Pokémon a snipe can target has a coin Ability, B queues every choice as `ApplyQueuedAttackDamage`. That makes a "pure" frame, which k3/km3 resolve without spending a ply, even at depth 0 (`expectiminimax_player.rs:663-717`, before the depth check at `:800`).
- Under the old engine the same frame was a plain `ApplyDamage`, an ordinary move. At a leaf, the bot scored the state before the damage, so the snipe counted for nothing.
- The probes stop at the turn boundary, and a Promote happens on the opponent's turn.

## 1. What the probes detect, and what they don't

**`coin_probe.rs`:**
- It only expands states where the mover is to act (155-158) and follows only successors with the same `current_player` and `turn_count` (196). It never applies EndTurn (194).
- Chance is 12 samples per move, with a 60,000-node cap.
- QUEUED (160-179): an offered `ApplyQueuedAttackDamage` at a coin-Ability Pokémon on the mover's opponent's side, where the attack's mechanic isn't AlsoChoiceBenchDamage.
- CUT (168-190): the mover's Attack or queued choice whose forecast loses branches when a Bastiodon or Goodra is swapped for a Bulbasaur (75-92).
- Every applied move counts as a ply (199).

**What it doesn't look at:**
- (a) Anything past a turn boundary. That includes the forced EndTurn the bots resolve for free (`expectiminimax_player.rs:630-657`; every Attack sets end_turn_pending, `apply_action_helpers.rs:1103-1108`). So a Promote is never followed into the mover's own next turn.
- (b) The bots' free steps: pure frames, including ChooseRandomEvolutionTarget, promotion frames and Victory Star. Counting them as plies overstates the depth.
- (c) The opponent's attacks. k3/km3 don't search them either (opponent_ply 0), and the public-reply check refuses any board with an Ability Pokémon (`public_reply.rs:639-646`).
- (d) Anything the value function reads.

**`vs_probe.rs`** only checks the Victory Star confusion-first gate, under the same turn rule (95), so it can't see B.

## 2. Where B changes what k3/km3 read

- **P1, queued frames.** `queued_attack_damage_choice` (`apply_attack_action.rs:281`) is used by the direct-damage helpers (`push_direct_damage_choices` 2899, old 2768; the discard-then-snipe helper 2968, old 2827; others) and Chase Order (`apply_action.rs:1305`). It has two effects:
  - (i) A new chance node: `apply_defender_damage_prevention_if_needed` (229, old 178) and `split_with_damage_prevention` (`attack_outcome.rs:621`) turn "full damage, probability 1" into 50/50.
  - (ii) Frame purity: the bots resolve a pure frame before the depth check. An old `ApplyDamage` frame reaching depth 0 got the static value of the pre-damage state.
  - **Effect (ii) is the one that matters in these five games.**
- **P2, Goodra/Bastiodon cut after Weakness.** The new `retain` plus `heads_coin_cuts` (`attack_outcome.rs:655-668`) replaces the old filter_map (584), and the cut comes off in `modify_damage` (`hooks/core.rs:2058-2074`). Branches and probabilities are unchanged. Heads damage differs only with Weakness or a damage bonus.
- **P3, the four forecast wraps** (`attack_outcome.rs:716, 810, 920, 1004`). They change something only if a branch carries a heads cut and the same target also has Guts, point denial or attacker knockout. `expected_damage_to` (981) is called only from tests.
- **P4, the per-thread value.** It is non-empty only inside `with_heads_coin_cuts` (45-56), and the value function never runs inside it.
  - `value_functions.rs` never reads the coin Abilities.
  - `persistent_defender_damage` is read only with kd's flag on (425-428, 1220).
  - k uses no extra features; km is kog + kt switch 1 + N2 (476-488).
- **P5, the search's random numbers.** The seed is the same for each decision (`game.rs:220-232`). Extra branches can shift later sampled outcomes, but only downstream of P1 or P2.

## 3. The five games

Boards are from Sonnet's traces. The mover is the side whose Active was just Knocked Out. Its search runs:
1. Promote (ply 1);
2. the forced EndTurn (free);
3. DrawCard (ply 2);
4. the attack (ply 3, depth 0);
5. the snipe frame (free when pure).

Every R trace offers that attack right after the draw.

| game | the mover's Bench | the snipe and its target | old promoted | R promoted |
|---|---|---|---|---|
| k3 p4 i7 t95 | Grovyle (2 Energy), Butterfree | Slicing Snipe: one queued choice at the opponent's only Benched Pokémon, Meowth (its Active Garchomp has Mach Stealth); R prices a 50% knockout (50 into 50 HP) | Butterfree | Grovyle |
| km3 p4 i7 t84 | the same | the same | Butterfree | Grovyle |
| km3 p4 i360 t57 | Caterpie, Grovyle (2 Energy) | the same, Meowth the only Benched Pokémon | Caterpie | Grovyle |
| km3 p1 i399 t81 | Torchic, Torchic, Heatmor (1 Energy) | Tongue Whip: two queued choices (two Benched Meowths) | Torchic | Heatmor |
| km3 p21 i310 t87 | Suicune ex (1 Energy), Chien-Pao ex (3 Energy) | Diving Icicles: two queued choices (the opponent's whole board is two Hisuian Goodras; the Active has 50 HP); R prices 130 on tails and 50 on heads, a knockout either way unless Heavy Helmet; old priced the Energy discard with no damage | Suicune ex | Chien-Pao ex (it attacked at t90, exactly ply 3) |

The four forecast wraps never fire in these games: none of these decks has Guts, point denial or attacker knockout.

## 4. Verdicts, and the checks that settle them

- **P1:** can change a search value with no probe counter. This is the probe's blind spot, and it explains all five games.
- **P2:** can, but only with Weakness or a damage bonus. Inert here.
- **P3:** cannot here.
- **P4:** cannot, for k3/km3.
- **P5:** cannot on its own.

**Checks:**
- (a) Make coin_probe apply the bots' free steps without counting a ply: forced end-of-turn frames, pure frames and promotion frames. Drop the turn_count test at line 196 and stop when the opponent is to act. It should then report QUEUED at ply 3, pure, inside the search, for all five.
- (b) **The decisive one.** On the tick-k state, compare `score_candidates` (`expectiminimax_player.rs:247`) for each Promote on R, and on R with `queued_attack_damage_choice` forced to return `ApplyDamage`. The old choice should come back.
- (c) An exact counter at `expectiminimax_player.rs:677`, for a resolved pure frame holding an `ApplyQueuedAttackDamage`, would replace the replay probe for this case.

**The judgment game (km3 p4 i106 t82)** isn't a Promote, but the probe's "at the leaf" is probably a miscount from 1(b):
- The old line was Quick-Grow Extract, then ChooseRandomEvolutionTarget, then Slicing Snipe, then a mixed frame (Garchomp and two Meowths).
- The bot spends no ply on the evolution frame, so the snipe is ply 2 and the queued choice at a Meowth is played at ply 3, inside the search.
- To confirm, check whether the probe's printed path for i106 contains ChooseRandomEvolutionTarget.

## Confirmed (Sonnet, sonnet/trace-8c 2e581c1, `trace_8c_sonnet/UNEXPLAINED_ANALYSIS.md` and `dumps/`)

**Check (b), run.** A print-only patch of the search, in scratch copies of old and R (nothing in the repository), printed the root scores at tick k for every candidate, on three builds:
- old;
- R;
- R-revert: R with `queued_attack_damage_choice` returning a plain `ApplyDamage` for that one decision, set by an environment switch after the replay.

**The result.** In all 5 lookahead games and the judgment game, exactly one candidate's score differs between old and R. R-revert reproduces old's scores for every candidate, and old's choice. The forecast wraps, the sampled draws and the full-prevention change are all still on in R-revert, so none of them accounts for any of the six.

| game | the moved candidate's score: old → R |
|---|---|
| k3 p4 i7 | 10,964.2 → 55,342.6 |
| km3 p1 i399 | 9,585.7 → 9,600.7 |
| km3 p4 i7 | 10,608.2 → 55,114.6 |
| km3 p4 i360 | −594.4 → 4,440.65 |
| km3 p21 i310 | 10,553.4 → 100,000.0 (a win) |
| km3 p4 i106 (Quick-Grow Extract) | −9,773.3 → −14,873.35 (two coin branches) |

**Check (a), done the bots' way.** Instead of rewriting coin_probe, the instrumented search printed "queued coin-target frame ... depth_left=0" under the moved candidate and no other, in all 5:
- Meowth at slot 3 after Slicing Snipe in p4 i7 (both bots) and i360;
- Meowth at slot 2 after Tongue Whip in p1 i399;
- Hisuian Goodra at slot 0 after Diving Icicles in p21 i310.

That is QUEUED at ply 3, in a pure frame resolved for free.

**i106.** coin_probe's printed path is Play Quick-Grow Extract; ChooseRandomEvolutionTarget; Attack (Slicing Snipe). The free step was counted as a ply. In the bots' own count, the queued choice (a mixed frame of 3 choices) is applied at ply 3, and R's search prices both coin branches. It is a CONDITION 3 row with the same cause as the 5.

## A note for the reader

Effect P1 (ii) is a change in what the bots see at the edge of their search, not in the game's rules: a snipe into a coin-Ability target is now resolved at the leaf, with its coin. It exists only where repair B's queued coin path exists, so by the plan's mechanic check it is B acting in lookahead (the gate inside the search depth). That holds once the probe counts plies as the bots do. It is still worth saying plainly to Dustin, together with check (b)'s result.
