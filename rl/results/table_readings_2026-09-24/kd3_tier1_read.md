# kd3 tier-1 read at 0c0e7f9 (the commit its table runs at), Sept 25

**In plain words: kd3's code is sound enough to read its table.**
- It leaves k3, kp3 and kq3 exactly as they were.
- It reads only what a player can see.
- It does what its amended spec says, and it can't crash or run away in cost.
- There is one real defect, in which attacks skip a coin flip, and it can't touch the table.
- There is one behaviour worth knowing when the table is read: how kd prices Bench snipers, which affects the Lucario, Blaziken and Sceptile rows.

**How this read was done:**
- It was done in the laptop session, by one agent reading the code and running probe positions in scratch copies of the engine. Nothing in the repo was changed.
- It was first done at 5ae7490, then extended to 0c0e7f9 when the cloud's table started there (68117fa).
- It supersedes the laptop's 45a8030 check.
- File references are at 0c0e7f9:
  - VF = `engine/src/players/value_functions.rs`
  - CORE = `engine/src/hooks/core.rs`
  - AAA = `engine/src/actions/apply_attack_action.rs`
  - AA = `engine/src/actions/apply_action.rs`

## 1. k3, kp3 and kq3 are untouched from 97ca8f4 to 0c0e7f9: verified

The engine diff touches three files:
- **value_functions.rs:** only kd's own functions (VF:942-1220), imports, documentation and tests. `calculate_turns_until_opponent_wins_damage_aware` (VF:773-910) is unchanged.
- **core.rs:** `DefenderHit`, `persistent_defender_damage` and tests. `modify_damage` is untouched.
- **hooks/mod.rs:** one re-export.

The shared code still gives the same results:
- Every new function is called only from kd.
- The flattened threat pick (VF:798-828) chooses the same (damage, missing, slot) as the old per-slot and across-slot minimum, in the same order.
- The replays agree:
  - The cloud: k3 14,000 of 14,000 at 97ca8f4.
  - The laptop: a kp3 spot replay on a 0c0e7f9 build, 1,500 of 1,500 identical including the move hash (`../kd_mixed_rows_2026-09-25/`).

## 2. No hidden information: verified

What kd reads:
- The victims: card facts, HP and damage, Tools, the Disguise flag, and "no Abilities" effects.
- Board-wide conditions: Power of Alchemy; Arceus, GUARD Unown or a second Falinks; and the defender's current Active.
- The stadium, the owner's points, and whether the victim's Bench has a damaged Pokémon.
- The attackers' attack text.

Hands and decks are read only through `evolution_targets`, for the evaluating player's own side (VF:808).

## 3. The amended spec is implemented as written: verified

- **Fallback attacker:** VF:1183-1220. The Energy is counted once per Pokémon (VF:1045-1049). It returns "never" only when nothing can damage the victim.
- **Promotion order:** the defender's longest over every order (VF:994-1016).
- **Reach:** VF:1166.
- **Bench damage:** no Weakness, and Poncho and Shell Shield prevent it (CORE:1625-1640). Intimidating Fang comes from the current Active.
- **Defender bonuses:** only for hits on the Active (VF:1120-1148), matching the engine at AAA:4527-4614.

Checked against the engine's own damage code:
- **Bench spill: matches** (VF:1093-1117 against AAA:787-805, 4152).
- **The Ability bonus: matches** (VF:1142 against AAA:4195-4204).
- **No coin for direct damage: a defect, partly matching.**
  - The engine flips a coin-flip damage Ability's coin only on its main attack path (AAA:178-216). Any attack whose damage is queued as a separate damage step (AA:475 → 704-738) skips the coin.
  - kd exempts only the three DirectDamage effects (CORE:1641-1651).
  - Other attacks that skip the coin include Diving Icicles (Chien-Pao ex), Volcarona's discard-then-damage, Tapu Lele's per-Energy damage, and Chase Order's no-discard branch.
  - Example: Diving Icicles into an Active Togekiss does 130 in the engine, but kd prices it at 65.
  - **Table impact: none.** No Pokémon in the eight research decks has a coin-flip damage Ability.

## 4. The review's one-attacker gap: closed

A victim gets "never" only when nothing the owner has can damage it where it is (VF:1214, 1001, 967-986).

Probe positions, turns to win:

| Position | k | kd | By the rules |
|---|---:|---:|---:|
| Oricorio Active v Mewtwo ex (threat) + benched Weedle | 2 | 4 | 4 ✓ |
| Riolu Active, Oricorio benched, same attackers | 4 | 5 | 5 ✓ |
| Oricorio Active, two Treecko benched, owner at 1 point, Mewtwo ex + Heatmor | 4 | 4 | 4 ✓ |
| Same Bench v Garchomp ex's Linear Attack (can hit any Pokémon) | 4 | never | 4 ✗ |
| Treecko Active; Oricorio with Poncho + Treecko benched; owner at 1 point; Mewtwo ex + Heatmor | 4 | never | 4 ✗ |
| Vespiquen ex Active, Combee benched v Heatmor (Active) + Charmander | 7 | 5 | 4 ✗ |
| Same, owner's slots swapped | 7 | 4 | 4 ✓ |
| Two Vespiquen ex v Hitmonlee + Riolu | 10 | 9 | 8 ✗ |
| Two Vespiquen ex v Riolu alone | 28 | 8 | 8 ✓ |

What the misses mean:
- **The two "never" rows are the known limits that 8004222 states.** They can't occur with the eight decks: every table sniper damages Shuckle ex on the Bench, and Chien-Pao's 130 damages every table Active.
- **The other two misses follow the approved rule, but they are not best play.** When a Bench-only sniper is the main threat, benched victims are priced by sniping even when the Active attacker is faster. Then two things go wrong:
  - Powering the sniper can lengthen kd's count by a turn.
  - The result can depend on the owner's slot order.
- **For the reading:** Lucario (Hitmonlee), Blaziken (Heatmor) and Sceptile (Grovyle) run snipers that can become the main threat. kd may misprice those rows slightly, and may lean toward attaching Energy to the sniper. Read any change in those rows with this in mind.

## 5. No panic, loop or cost blow-up: verified

- There are at most 6 promotion orders, and each victim is priced once per clock call.
- Attackers are built once per call.
- There is no underflow in the missing-Energy subtraction, since the threat is the minimum of the same list.
- A debug build at 0c0e7f9, with overflow checks on, passes all 42 kd tests and the probes.
- A kd3-v-kp3 run of 14,000 games on the 5ae7490 build completed with no panic. It was stopped before being used, when 8004222 changed kd.

## What this changes

- **Nothing before the table.** kd3's code is registered, and its table has started at 0c0e7f9.
- **The coin defect** is for the cloud's list. It needs no kd3 change, since it can't affect the table decks.
- **The sniper-pricing behaviour and the two known limits** are written into kd3's reading as limits.
- **A fix to the sniper pricing would be a spec change and a new code**, not part of kd3.
