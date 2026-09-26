Decision this informs: kpf's reading, on the 45 cells and B2e's 48 held-out pairings, which the laptop runs (REGISTRATION.md section 6). This note records the build it reads. Build commit 9bffbda: the repaired engine e935f42 plus koa's and kpf's player code; references af8489f. The scan at 9bffbda has sha256 518d3f6094072ccd3c8f54d2eeefad65783948700e0ba449b434e293603fc0a4.

Seeds: the identity checks use the table's deals only (72,000,000 + pairing × 10,000 + i, i < 40, even i = first-named deck in seat 0).

# kpf: the build (Sept 26)

## What was built

- **`kpf<N>` = kp<N> + R + F. `kpg<N>` = kp<N> + F only (diagnostic).** Each part is behind its own `EvalFeatures` flag: `projected_readiness` for R, `fuel_credit` for F.
  - kpf with F off is kpr; with R off it is kpg; with both off it is kp.
  - Code: `engine/src/players/fuel_credit.rs`, `players/value_functions.rs` (the presets, the value functions, the F term, and R's projection returning the discard it left) and `players/mod.rs` (the codes).
- **Part R** is kpr's `projected_active_energy` exactly as built at e09fb46, used where kpr uses it: the own Active through its next turn, the opponent's at its next attack.
  - **Amendment 5 (1981bb4) is included.** Dustin approved it on Sept 26 as covered by his option 2, after the check "what 1981bb4 changes, in one sentence".
  - The answer: it changes only when each side's projection is read (the opponent's Active at its very next attack, 9a35f54's own rule), and adds no source and no parameter. The laptop's reading of the commit says the same (main 7353c86, REGISTRATION.md §2).
  - The refactor adds a second return value, the discard-pile Energy the projection didn't use; kpr's own result is unchanged.
- **Part F**: 15 × min(E, 4) for each side (§117's pre-set constants), added to that side's value at the Pokémon-value weight (1.0).
  - E is that side's discard-pile Energy that R's projection didn't put on the Active (the whole pile with R off), counting only what its available recovery sources can move back.
  - Each side is read at the horizon R reads it at, so nothing counts twice.
- **Who can see what** (condition two):
  - **The own side:** a source in play, or among its own hand and deck, with a target other than the source's own holder, in play or among those cards, under its play conditions.
  - **The opponent's side:** only a source visible in play that can act as its text allows (holder position included), with a target in play. Its hand and deck are never read.
- **Parser:** `kpf` and `kpg` are parsed before `kp`. Before the change, "kpf3" fell into kp's branch and was rejected, so no existing code string parses differently. kp, kpr, kq, kd, koa/kob/kor, g<N> and b are unchanged, and there are tests.

## The recovery class, re-checked from every card text

A walk over every card in the database finds exactly the registration's six. The match is "from your discard pile" + "Energy" + "attach", in any Ability, attack or Trainer text. A looser scan ("discard pile" + "Energy" without "attach") found none either. `every_discard_energy_recovery_card_is_classified` fails on a new card with such a text until it is classified.

| card (printings) | effect code | Energy it moves | target | conditions |
|---|---|---|---|---|
| Dragonair B4 117 (Dragon's Blessing) | `AttachEnergyFromDiscardToActiveTypedFromBench { Dragon }` | any type; once a turn, so every Energy counts | the Active [N], never its holder | holder on the Bench (opponent's side) |
| Flareon ex A3b 009, 079, 087, A4b 066, B2 225 (Combust) | `AttachEnergyFromDiscardToSelfAndDamage { Fire, 20 }` | [R]; once a turn | itself | none |
| Flame Patch B1 217, 331 | text | one [R] per copy | your Active [R] Pokémon | none |
| Professor Sada B3a 072, 087 | text | one of each different type, up to 3 per copy (Dustin, Sept 26) | Ancient Pokémon (the engine's list) | none |
| Lusamine A3a 069, 083, A4b 350, 351, 375 | text | 2 of any type per copy | Ultra Beasts (the engine's list) | the owner's opponent has at least 1 point |
| Volkner A2 153, 193 | text | 2 [L] per copy | Electivire or Luxray | none |

- **No attack, Tool or Stadium recovers discard Energy today.** A Tool or Stadium in play would be read through the same text table.
- **Only B4 117 of Dragonair's printings has the Ability.**
- **How E is counted:**
  - The Abilities work again every turn, so they take every Energy of a type they move.
  - Each Trainer copy takes what one play moves: a typed card first, then Sada's different types (from the most plentiful types), then any type.

## Changes from the second read (9bffbda, after a87c451)

An independent second read against the registration confirmed:
- the identity of every existing tier;
- the parser;
- the no-double-count horizons;
- the six cards against their texts and the engine's play checks;
- that nothing is read from the opponent's hand or deck;
- the scan's default mode.

It found one error, fixed:
- **Dragon's Blessing counted its own holder as a target.** A Dragonair behind a non-Dragon Active, with no other Dragon, gave credit it can't use. Now an Ability's holder is never its own target (Combust's target is its holder).

It raised one question, answered by Dustin:
- **Professor Sada moves one Energy of each different type, up to 3.** Every Trainer source now counts per copy what one play moves.

It found two test gaps, now covered: kpf's opponent side with R on, and a recovery Trainer in the own deck.

## Tests

- **The credit on and off, each side:**
  - a source in play, in the own deck or hand, on the opponent's Bench or Active, or only in the opponent's deck or hand;
  - a Dragonair with no other Dragon.
- **Types, targets and play conditions:**
  - Flame Patch's [R];
  - Combust onto itself;
  - Lusamine's point;
  - per-copy amounts for Sada, Volkner and Flame Patch.
- **The cap:** 4 Energy, 60.
- **No double count with R:**
  - own side: kpf's credit is on what Dragon's Blessing's projection left, kpg's on the whole pile;
  - opponent's side with R on: −30 against kpg's −45.
- **The switches:** kpf with F off = kpr, with R off = kpg, both off = kp, on the value. These pin the flag wiring; the tests above pin the behaviour.
- **The class walk and the parser.**
- **Full suite:** 1,947 passed, 0 failed.

## The scan

- `rl/results/b2e_rows_2026-09-26/legality_scan_pairs.patch` (main) is applied to `engine/examples/legality_scan.rs`. It applied cleanly, with line offsets, over this branch's openings, decisions and counters.
- `--pairs <tsv> --seed-base <base> [--root ..] [--pairings ...]` plays the file's rows. Without `--pairs` the scan runs as before. In default mode 56 of 56 smoke games equal af8489f's kp3 in moves and decisions.
- `--pairs` ran kpf3 on the gauntlet file (`new_decks_run.tsv`, pairings 8 and 9, seed base 21,108,000,000).
- **The build: commit 9bffbda, `cargo build --release --example legality_scan`, sha256 518d3f6094072ccd3c8f54d2eeefad65783948700e0ba449b434e293603fc0a4.**

## Identity at the build (REGISTRATION.md section 5)

Filled in when `run_identity.sh` finishes.
