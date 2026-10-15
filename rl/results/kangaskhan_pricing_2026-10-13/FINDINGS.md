# Mega Kangaskhan ex's Double-Punching Family: how the engine and the bots price it (Oct 13-14)

Dustin's observation (Oct 13, watching Sonnet's session): the bot seems to price the attack at 80 when it hits twice for 120.
Investigated by a multi-agent workflow on the laptop:
- four lenses: the engine, km3 scoring its own attack, the forecasts and kx3, and the evidence in the outputs;
- each key finding was checked by an adversarial verifier, and a synthesis was written;
- the repository was read only.

The synthesis follows as written. Its scratch builds (/home/dacz8976/kanga_refute_vf, kanga_diag_1b119d13) are laptop-only.

Verdict: Dustin is right about the bots, but not about the game engine. The engine deals 80 then 40. km3 prices the attack at 80 in two places: its forecast of the opponent's Kangaskhan, and its scoring of its own attack when that attack is the third action of a line it searches. Both kx3 commits inherit the same pricing. In game 010837 no decision changes. Synthetic positions show it can change choices.

### 1. Does the real engine deal 80 then 40? Yes (verified)
- `engine/src/actions/apply_attack_action.rs:2272-2290` (dispatched at `:678-679`) deals the attack's own damage, `fixed_damage` 80 (`database.rs:56448`). It then queues a 40 hit at the bottom of the stack: `queued_attack_damage_choice(...,40,...)` at `:2285`, `insert(0)` at `:2288`. That hit is a plain `ApplyDamage` (`:365-369`), or `ApplyQueuedAttackDamage` when an opponent's Pokémon has a coin-flip damage Ability (`:354-363`).
- Each punch gets its own damage changes (`apply_action_helpers.rs:537-570`, `hooks/core.rs:1834+`):
  - Red: 100 + 60.
  - Heavy Helmet: 60 + 20.
  - Weakness never applies to Kangaskhan's own punches, because no card has Colorless Weakness.
- If the first 80 Knocks Out the Active, the opponent promotes first and the 40 hits the new Active (`state/mod.rs:1417-1439`). If that Knock Out ends the game, there is no second punch.
- These files are byte-identical in the pinned engine (c045ede, `rl/engine-2026-10-12/deckgym`), on main, and in both kx3 commits.
- Evidence:
  - The engine tests pass: `mega_kangaskhan_double_punching_family_test.rs:22-56` and `:59-108`.
  - A direct `-vvv` run of the pinned engine (`scratchpad/kanga/v_engine/sim_err.txt`) shows "Dealt 80", then `ApplyDamage (40)`, then "Dealt 40".
  - Real game 010837:
    - Regigigas 150→70→30.
    - Next attack: the first 80 Knocked Out Regigigas, Glimmet was promoted, and the 40 took it 60→20 (`TURN_LEDGER.json` turns[5] and [7]).
  - Rules switch 2 changed only the coin flips on the second punch, never the 40.

### 2. Which bot paths price it below 120

**Established (verified):**

- **(c) Forecast of the opponent's Kangaskhan, km3: 80 per attack.**
  - Cause: the damage estimator `estimated_attack_damage_ex` (`value_functions.rs:2240-2521`) has no case for this attack and falls back to `_ => fixed` at `:2519`.
  - The threat clock reads that 80: the damage step at `:1754-1760`, inside `kt_clock_stadium` (`:1743-1835`). Hits are counted by `kt_hits` as hp/80 rounded up (`:1888-1896`), via `kt_clocks` (`:1902-1918`, wired in at `:736-737` and `:901-902`). Each extra turn on the clock is worth 100 points (`:56`).
  - This clock is km3's only forecast of the opponent's attack:
    - km3 never searches the opponent's turn (opponent_ply 0, `players/mod.rs:706`).
    - km3's check for a certain loss next turn rejects this attack as an unsupported mechanic (`public_reply.rs:459-480`).
  - Measured, clock against real attacks needed:

    | Target | Clock says | Real |
    |---|---|---|
    | 180-HP ex | 3 | 2 |
    | Alolan Muk (110 HP) | 2 | 1 |
    | Glimmora (90 HP) | 2 | 1 |
    | Kingambit + Glimmora + Muk | 6 | 4 |
    | Game 010837, turn 9 board | 3 | 2 |

  - In score sweeps the clock steps between 80 and 90 HP, not between 120 and 130.
  - Damage cuts are taken once per attack, not once per punch (seen in code). Against a Heavy Helmet holder the clock counts 60 per attack where the engine does 80. The measured jumps at 60→70 and 120→130 come from the evidence lens and were not separately verified.
- **The same 80 prices km3's own Kangaskhan in its clock on the opponent** (`:1912-1913`). An 81-120 HP target counts as 2 attacks.
- **(b) km3 scoring its own attack, in its search:**
  - **Priced right (120)** when the attack is the 1st or 2nd action of a searched line.
  - **Priced at 80** when it is the 3rd action:
    - The root searches at depth max_depth−1 = 2 (`expectiminimax_player.rs:323`).
    - The plain `ApplyDamage` frame is not in the free list at `:633-642`.
    - The same-depth list at `:663-673` matches only `ApplyQueuedAttackDamage | ChooseRandomEvolutionTarget` (I read this).
    - The depth-0 leaf therefore scores the board before the 40 lands (`:800-905`, `static_eval` at `:905`).
  - Numbers:

    | Position | 3rd-action score at the root | One step later |
    |---|---|---|
    | VK_110 (Place:Pawniard) | 1691.0 | 11781.1 (the Knock Out was missed) |
    | A3_130 | 1651 | 1731 |
    | VM_110 | Retreat-to-Kangaskhan 1791; root picked Attach@1 at 2771 | Retreat 11881.1 |

  - Exception: if an opponent's coin-Ability Pokémon is in play, the second punch is the queued type and is priced even as the 3rd action (VK_110_coin: 11630.1).
  - After the first punch Knocks Out, the 40 on the promoted Pokémon is also missed at depth 0 (A3_80: 11781.1 against 11861.1).
- **kx3, frozen cd20a97a and candidate 9a0bc5ac:**
  - `value_functions.rs` (blob 09c556ea) and `expectiminimax_player.rs` (blob 4f5cb880) are identical on main and both commits.
  - So kx3's proposed move (km3's move) and every km3 decision inside its play-outs, on both sides, carry (b) and (c).
  - The play-out results themselves run the real engine, so they count the full 120.

**Unconfirmed (code read only, or not adversarially verified):**

- **kx3's move cap:** this is the step that keeps 12 candidate moves. It applies a single action, `game.apply_action(a)`, then scores km's static value (cd20a97a `playout_player.rs:540-541`; 9a0bc5ac `:1103-1104`).
  - I read this code myself. Scored this way, the Attack still has the 40 waiting on the stack.
  - Diagnostic values: 1717 against 100000 when the 40 would Knock Out a 110-HP Muk.
  - It only matters with more than 12 distinct moves when km3's own pick is something else. km3's move is always kept.
- kx3's other decision rules (noise rule z, skip bar _zs, attack bar _za, close-call extension _m, tie-breaks) use no damage estimate. Lens claim, not verified.
- `best_attack_value_ex` also gives 80, but km3 runs with value_aware=false, so it is not a km3 path.
- Display only: the position runner's plan output stops at the Promote after a first-punch Knock Out, so the 40 isn't listed.

**Priced correctly:**
- The real engine.
- km3's own attack as the 1st or 2nd action.
- Any line where the opponent has a coin-Ability Pokémon in play.
- kx3's play-out results.
- public_reply refuses the attack rather than mispricing it.

### 3. What Dustin most likely saw
- No written output in `rl/results/pause_games_new_2026-10-13/` (first read or v2) prints 80 for Kangaskhan (verified search).
- The 80s in those files are other things:
  - Overlord's Blade at a knock-out count of 0 (60 + 20 Weakness; `POSITION_TABLE.md:17` in both folders).
  - "gap 80" (`POSITION_TABLE.md:56`).
- Sonnet's session ("Opus agents progress") showed the `lib/card.py` line `[CCC] Double-Punching Family 80 - This attack is used twice in a row...`. That printed 80 is most likely the number he saw.
- His conclusion is still right. km3's scores in `v2/runs_km3/err_KW-261013_010837000-t05`, `-t07` and `-t09.txt` were computed with Kangaskhan at 80. Example: t09 Retreat:1 = -9339.133, reproduced exactly.

### 4. How it can change decisions
- **(c), the biggest effect:**
  - Any of km3's Pokémon with 81-120 HP is judged to survive the opponent Kangaskhan's next attack. Example: a 110-HP Alolan Muk counts as 2 attacks when it is really 1.
  - The opponent's win looks 1-2 turns further away, worth 100-200 points.
  - A certain loss next turn is never recognised. Kingambit at 100 HP reads as 2 turns from losing when it is 1.
  - Counterfactual: a scratch build with the +40 fix, `/home/dacz8976/kanga_refute_vf` with `KANGA_FIX=1`.
    - On the 8 real 010837 positions × 12 seeds: 0 plan changes. Scores shift a flat −100 at t03-t09.
    - In a 125-variant HP sweep: 27 plans change, all at t11. 17 change where the Heavy Helmet goes. Example: t11-s0-h60, Helmet on Kingambit 63.4 against Muk −46.6 without the fix; Muk −46.6 against Kingambit −136.6 with it.
- **(b):**
  - Lines like set up, set up, then attack with Kangaskhan are underpriced by 40 damage, or by a whole Knock Out.
  - That biases km3's root choice toward other attackers or shorter lines (VM_110 picked the Seismic Toss line at the root).
  - In all 10 test positions km3 still made the Knock Out, because it searches again after each action. No wrong final turn has been shown.
  - The own-side clock undervalues charging or keeping its Kangaskhan against 81-120 HP targets.
- **Who it touches:**
  - km3, the pinned pilot.
  - Frozen kx3 and the candidate, through km3.
  - Not the engine.
- **Exposure:** only games with a Mega Kangaskhan ex in play. A grep finds no deck list under `decks/` containing it; it appears only in panel ladder notes, `engine/example_decks/swampert-kanga-ninetails.txt` and Dustin's pause-game positions. So screen, floor, scoreboard, exam and slow-report numbers on those decks are not affected.

### 5. Fix options and costs
- **A. Forecast (fixes the main effect):**
  - Code: add `Mechanic::MegaKangaskhanExDoublePunchingFamily => fixed + 40.0` before `value_functions.rs:2519`. One line; already prototyped in `kanga_refute_vf`.
  - Fuller version: handle the punches separately in the clock's hit count (`kt_clock_stadium`'s `hits_on`, `:1787-1800`). That means taking cuts off each punch (Helmet 60 + 20) and carrying the 40 onto the next victim. Roughly 30-60 lines.
  - Tests to pin it:
    - `estimated_attack_damage_ex` = 120 for B2 127.
    - `kt_clocks`: 110-HP Muk → 1 hit, 180-HP ex → 2, Helmeted Kingambit (140) → 2.
    - The t09 board's clock total = 2.
  - The existing diagnostic build `/home/dacz8976/kanga_diag_1b119d13` already has the setup for these tests.
- **B. Search gap:**
  - Code: in `expectiminimax_player.rs:663-673`, also accept a one-element frame `[ApplyDamage { is_from_active_attack: true, .. }]`.
  - Test: a sibling of `depth_zero_prices_mandatory_queued_attack_damage` (`:1260-1287`) for the plain form, where the leaf is −200 not −240. Plus a km3 root check on VK_110: Place:Pawniard ≈ 11781, not 1691.
  - Alternative: always queue the punch as `ApplyQueuedAttackDamage` at `apply_attack_action.rs:2285`. That edits the pinned engine and switch 2's coin path, so I would not take it.
  - Scope caution: other attacks also queue damage through `queued_attack_damage_choice` (`:3056`, `:3095`, `:3133`, `:4095`, `:4586`, `:4736`, `:6727`, mostly target choices). Whether they have the same gap at the last searched step is unchecked. Keeping the match to the one-element frame keeps the change limited to Kangaskhan, and to copies of its attack.
- **C. kx3 cap (optional):** resolve the forced and queued steps before scoring at cd20a97a `:540` / 9a0bc5ac `:1103`. It matters only above 12 moves.
- **Pinned identities:**
  - The self-check digests (km3 `81b572198c04d5d1`, kx3 `31d638dbc818b0fa`) come from 12 self-play games of t-altaria against t-suicune (`rl/strength/src/main.rs:147-170`, `slow_report.py:885`, `decks.json:24,29`). Neither deck has Mega Kangaskhan ex.
  - So A, or B kept to Kangaskhan, should leave both digests unchanged. That also means the digest cannot tell fixed from unfixed; the program sha256 and the pilot name must carry the difference.
  - A broader B could change the digests. Re-run the self-check to know.
- **Running studies:** they are bound to their binaries' sha256:
  - exam m32/m64: f5a6ae95 (172cbe9c)
  - slow reports: 5011e227
  - pause-game runner `pg_pos_F_cond`: 5c4859949a88a28b

  They keep running untouched if nothing is rebuilt in place. A fix should ship as a new named preset on a branch, not as an edit to km3. Changing or adopting the pinned pilot is Dustin's call.

The only file I added is the read-only script `C:\Users\dacz8\AppData\Local\Temp\claude\C--Users-dacz8-Projects\1b119d13-736d-4588-ba63-0e9ef1756970\scratchpad\kanga\synth_cap.sh`, which reads the kx3 cap code with `git show`. The repository was not changed.
