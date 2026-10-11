# Rules switch 2, step 8c: the record (the laptop session, Oct 11)

Every changed game of `../handoff_8c.tsv` (1,133: step 8b 89, step 9 1,044; steps 7c and 8 had none), decided by PLAN.md section 6's
rule with the tools of `../tools_8c.tsv` in tools_8c/README.md's order, at their pinned blobs (checked by `s2_8c_run.sh` before it
started). No agents; one program run per block on the laptop (nice 19), 15:03-15:53 UTC.

## Result

| block | rows | on the board | lookahead, both halves | unexplained by the tools | revert check |
|---|---:|---:|---:|---:|---|
| A: 8b, pairings 32-37, seed block 23,100,000,000 | 25 | 4 | 21 | 0 | 21 of 21 |
| B: 8b, pairings 40-46, seed block 23,300,000,000 | 64 | 49 | 15 | 0 | 15 of 15 |
| C: 9, B2e's named rows, seed block 21,106,000,000 | 1,044 | 458 | 585 | 1 | 585 of 585 |
| total | 1,133 | 511 | 621 | 1 | 621 of 621 reproduced |

- **Fingerprints:** every trace reproduced its row's old and new move fingerprints (0 problems in all three runs).
- **Golden checks:** 0 mismatches; no explaining counter without one.
- **Negative controls:** 20 (8 in A, 8 in B, 4 in C), each found nothing (`control_clean` = `nothing_found`).
- **CONDITION 3** (111 games, only an off-gate counter fired): 110 lookahead with both halves and the revert check; 1 by hand trace below.
- **The category `none`** (1 game, 8b k3: no counter fired at all): lookahead, both halves, revert reproduced.
- **8b against the cloud:** the cloud's own classification of its 8b rows (31380294, `classify_check_8b/classify_8c_out/verdicts.tsv`:
  25 games, pairings 35 and 37) and this run's are the same 25 games with the same verdict, first differing tick and kind
  (`cmp_8b_cloud.txt`). Pairings 40-46 are new to sitting 2.
- **The revert check** (`revert/`): for every lookahead game, the candidate with the game's own gate(s) off for that one decision chose
  the official engine's move with the same candidate list and scores, and so did every gate off together. Gates: Trap Territory (G6)
  586 games, the seven sites (G1 + G2) 31, return damage (P2) 4. No root held an attack continuation.

## The one game the tools left: step 9, km3, pairing 34 (Whimsicott v Sceptile), deal 449

First difference at tick 68 (turn 8): same board, same 4 offered moves; the official engine plays the Stadium (UseStadium, 367.8),
the candidate plays Professor's Research (10,819.1; 358.8 on the official engine). The probe found nothing inside the search at tick 68
(the tools' verdict: UNEXPLAINED). The hand trace (`hand_9_34_449/`, `hand_9_34_449.sh`, the same score dumps):

- **The gate, alone:** Trap Territory's gate off (`--revert g6`) gives the official choice and all four scores exactly; every other gate
  off alone (p2, g1-g5, g7-g11, g1+g2) keeps the candidate's choice; every gate off gives the official choice and scores.
- **The condition, inside the bot's search:** the candidate's principal line for Professor's Research (`p_tree.txt`) is: draw, evolve
  the Benched Spinarak into the deck's second Ariados, then Grass Knot ("30 more damage for each Energy in your opponent's Active
  Pokemon's Retreat Cost"), and the opponent must promote (a Knock Out). With two Ariados the new rule counts Trap Territory twice, so
  the Retreat Cost is one higher and Grass Knot does 30 more; the official engine's line is the same moves without the Knock Out.

So the cause is round 2's Trap Territory rule, found in the search by a hand trace rather than by the probe. Whether that hand trace
stands in for the probe's half is a judgment call: it is counted `judgment 1` in `../8c_RESULT.txt`, and the pin waits for Dustin's
word on it (`../8c_DECISION.md`).

## How it was run, and two corrections on the way

- `s2_8c_run.sh`: the builds (official engine 8626a35 and the candidate 08a9b3ae, vs_trace each; coin_probe_v2 on the candidate with
  test-utils and its `r2_counter_fns.rs` from P's coin script, blob 306f1f69; self-test 46 checks and 3 frame checks, 0 failures), the
  hand-off adapter, the split by seed block (`classify_8c.py` takes one seed base and keys games by bot, pairing and deal, and step 9's
  pairings 32-39 share numbers with 8b's), classify_8c.py per block, revert_8c.py over the 621 lookahead games. Program sha256s are in
  `builds.txt`, inputs in `inputs.sha256`.
- **Correction 1:** the first start stopped at the probe's build: coin_probe_v2.rs includes `r2_counter_fns.rs`, which its build recipe
  writes with `instrument_scan.py --emit-fns`. Added; the two finished builds were kept.
- **Correction 2:** the first revert check built the two score dumps on plain engine copies, so they printed no candidates and all 621
  games were FAIL (process), with every move as expected. `s2_8c_dump.sh` builds them as run_revert_gates.sh does (each in its own engine
  copy patched with b77652d6's print-only dg_patch.py): 621 of 621. `revert/` is that second run.
