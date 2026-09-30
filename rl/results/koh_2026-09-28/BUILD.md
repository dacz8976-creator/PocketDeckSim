Decision this informs: kph's registered reading on the composed base (`../kph_2026-09-27/REGISTRATION.md` section 2, with amendment 1): R′ read against kog3 on the 45 cells, by the laptop. kog passed its composition check on Sept 28 (`../kog_composition_2026-09-27/READING.md`, 5bca434), so kph at 7e7d864 is not run. This note records the build. Build commit bd2907f: the official engine's source (main 83e17ae) plus the player code on this branch (kt, kog, kph, koh) and kt's refactor of the rules files `hooks/core.rs` and `hooks/mod.rs` (ed81c8b; accepted by the Sept 28 engine switch, `../engine_switch_2026-09-28/README.md`; bd2907f's `engine/` equals the official 233bced's), `cargo build --release --example legality_scan` (the `--pairs` option is in it), scan sha256 c84ead95202e7e200313e37f78ceabb184937ab46f366bd5c570d0470a5010cb.

Seeds: the identity checks use the table's deals only (72,000,000 + pairing × 10,000 + i, even i = first-named deck in seat 0).

# koh: kog + R′ (build, Sept 28)

## What was built

- **`koh<N>` = kog<N> + R′.** It is kph's `EvalFeatures` with koa's switch A added (`EvalFeatures::KOH`):
  - switch A (`opening_first_turn_active`), koa's opening, exactly as in kog;
  - F (`fuel_credit`), kpg's credit, exactly as in kog;
  - R (`projected_readiness`), kpr's projection as in kpf;
  - fixes A (`evolution_steps`) and B (`zone_to_bench`), exactly as built for kph at 7e7d864 (`../kph_2026-09-27/BUILD.md`), with amendment 1's reading of "already retreated".
  - No other change. No code of kph's changed.
- **Parser:** `koh` is parsed with koa, kob, kor and kog, before `k<N>`. No existing code starts with "koh". Tests: koh3 and KOH5 parse; koh and kohx are rejected; kog3 and kph3 parse as before.
- **How the parts compose.**
  - Switch A is read only in the setup evaluation. There nothing is projected (turn 0), so R, A and B read as kp there, and B has no clock to act on.
  - F, R, A and B act only after setup.
  - So koh's value is koa's while the opponent's setup is masked, and kph's everywhere else.
- **Diagnostics.** kph's A-only and B-only codes (kpha, kphb) stay on kpg. Composed versions weren't asked for; they would be one preset each if the reading needs attribution.

## Tests

- `koh_tests::koh_is_kog_with_r_prime_and_reads_as_its_parts`:
  - **R′ off** (R, A and B): koh's preset is kog's.
  - **A and B off:** koh's preset is kog + R (kpf's with switch A).
  - **On values,** on every position of 12 random games (Altaria v Blaziken, Lucario v Vespiquen, Altaria v Lucario, Vespiquen v Hydreigon), from each player's own view:
    - koh = koa while the opponent's setup is masked, and koh = kph after it;
    - koh with A and B off (kog + R) = koa in setup, and kpf after it. There is no code for kog + R, so this is its identity check.
- The parser test above.
- **Full suite:** 1,975 passed, 0 failed.

## Identity (agreed with the laptop, Sept 27-28)

**Every check passes** (`run_identity.sh`, `identity.py`, `identity_check.txt`). All runs are at bd2907f, on the table's deals. A game is equal when its moves, choices, openings and result all are.

| check | reference | result |
|---|---|---|
| kog3 (koh with R′ off), all 500 deals | the cloud's kog3 table, `../kog_2026-09-27/a823b6d_kog3_500.jsonl` (the laptop's `table_kog3` equals it) | 14,000 of 14,000; clean |
| kog + R (koh with A and B off) | no code of its own: checked on values (tests above) | koa's value in setup and kpf's after it, on every position tested |
| k3, first 40 deals | `../rules09_fixes_2026-09-26/af8489f_k3_500.jsonl` | 1,120 of 1,120; clean |
| kp3, first 40 deals | `af8489f_kp3_500.jsonl` | 1,120 of 1,120; clean |
| koh3 smoke, first 40 deals | — | 1,120 games; clean |

- The smoke's changed games aren't counted here. The laptop reads the footprint first, against kog3 on the 45 cells.
- The base reading is kph's, as registered, with kog3 as the base: the laptop's `table_kog3` and `new17_kog3`, and koh3's mixed rows against kog3.

## Files

- `run_identity.sh`, `identity.py`, `identity_check.txt`, `timing.txt`.
- The raw outputs: `bd2907f_kog3_500`, `bd2907f_{k3,kp3,koh3}_40` (`.jsonl` and `.txt`).
