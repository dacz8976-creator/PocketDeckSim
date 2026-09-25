Decision this informs: how to read the Vespiquen deck-gap veto on kp3 (and b3n1). kp3 doesn't pilot Vespiquen worse: it pilots it slightly better. The veto fires because kp3 improves Vespiquen's opponents more than it improves Vespiquen, so it says Vespiquen's under-rating has another cause. Engine commit c7cb688 (legality_scan built at 150a305).

Seeds: the table's deals only. 72,000,000 + pairing × 10,000 + i, i < 500, even i = first-named deck in seat 0.

# Vespiquen's seven cells under four pilotings, Sept 25

These are the same deals as the whole tables. The k3 v k3 row is `../per_game_table_2026-09-25/k3_500.jsonl`, and the kp3 v kp3 row is `../public_pricing_2026-09-25/kp3_500_*.jsonl`. The two mixed rows are new, with kp3 on one side only.

Vespiquen's score, %, with the paired change from k3 v k3 (95% range from per-deal differences):

| cell | Limitless | k3 v k3 | kp3 v kp3 | kp3 Vespiquen v k3 opponent | k3 Vespiquen v kp3 opponent |
|---|---:|---:|---:|---:|---:|
| v Altaria | 61.2 | 57.4 | 52.6 (−4.8 ± 4.9) | 59.0 (+1.6 ± 4.1) | 47.6 (−9.8 ± 4.4) |
| v Blaziken | 18.6 | 20.5 | 18.6 (−1.9 ± 4.2) | 24.0 (+3.5 ± 3.2) | 15.2 (−5.3 ± 3.8) |
| v Hydreigon | 61.6 | 69.2 | 59.0 (−10.2 ± 5.4) | 73.8 (+4.6 ± 4.3) | 57.6 (−11.6 ± 4.8) |
| v Lucario | 30.7 | 35.8 | 31.8 (−4.0 ± 4.9) | 38.2 (+2.4 ± 3.6) | 28.4 (−7.4 ± 4.2) |
| v Sceptile | 66.9 | 33.4 | 35.6 (+2.2 ± 4.5) | 36.2 (+2.8 ± 3.8) | 31.2 (−2.2 ± 3.5) |
| v Suicune | 73.0 | 49.6 | 57.0 (+7.4 ± 4.6) | 56.0 (+6.4 ± 4.0) | 52.4 (+2.8 ± 3.5) |
| v Weezing | 83.5 | 70.9 | 65.9 (−5.0 ± 4.8) | 70.2 (−0.7 ± 3.8) | 65.4 (−5.5 ± 3.9) |
| **all 7 (3,500 deals)** | 56.5 | **48.1** | **45.8 (−2.3 ± 1.8)** | **51.1 (+2.9 ± 1.5)** | **42.5 (−5.6 ± 1.5)** |

What this shows:

- **kp3 helps Vespiquen's own play.** With only Vespiquen's pilot switched, it gains 2.9 points, and it gains or holds in six of the seven cells.
- **kp3 helps its opponents more.** With only the opponent's pilot switched, Vespiquen loses 5.6 points. The biggest drops are against the decks with the most to price: Hydreigon (−11.6: Darkness Claw and Copycat), Altaria (−9.8), Lucario (−7.4), Weezing (−5.5: Mars and Copycat) and Blaziken (−5.3).
- Vespiquen's only card that needs pricing is Copycat, so it gains less from pricing than most decks do. With both sides switched, the difference is what's left over: −2.3.
- **This is the mirror of Hydreigon.** Hydreigon's gain was its own pilot (+15.0), with its opponents slightly better (−3.1); see `../per_game_table_2026-09-25/README.md`. For Vespiquen, the loss is its opponents' improvement.
- **So the veto says Vespiquen's under-rating has another cause, not that kp3 is wrong.** Vespiquen sits 8.4 points under Limitless with k3, and 10.7 with kp3. Its biggest misses are v Sceptile (33.4 against 66.9) and v Weezing (70.9 against 83.5), and pricing barely moves either. The B5 fixes (the kq tier: next-attack reduction and benched-attacker readiness) are the next candidates to test there.

## Files

- `mixed_vesp-kp3_{second,first}.{txt,jsonl}`: kp3 pilots Vespiquen. "second" = pairings 5, 11, 16, 20, 23, 25, where Vespiquen is second-named; "first" = pairing 27.
- `mixed_vesp-k3_{second,first}.{txt,jsonl}`: k3 pilots Vespiquen and kp3 the opponent.
- `run_vespiquen_mixed.sh`: the commands. `mixed_rows_vespiquen.py`: the readout above. `timing.txt`: wall times.
- No game broke a rule.
