Decision this informs: whether kq's benched-attacker readiness term explains Vespiquen's drop under kq3 by taxing Chase Order discards of Combee. It doesn't: kq3 discards Combee as often as kp3 does (12.7% of choices against 13.1%). What moves is which ex gets discarded: fewer Shuckle ex, more Teal Mask Ogerpon ex. legality_scan built at b7c0ace (kq code as at ba20dd8; b7c0ace only adds the counter).

Seeds: the table's deals only. 72,000,000 + pairing × 10,000 + i, i < 500, even i = first-named deck in seat 0.

# Chase Order discards, kp3 v kq3 (Sept 25)

Chase Order (Vespiquen ex, [G][G] 70) lets the attacker discard one of its Benched Basic [G] Pokémon for +70. The Vespiquen list has three such Basics: Combee, Shuckle ex and Teal Mask Ogerpon ex. Under kq's definition all three are benched attackers: each has an attack that costs Energy and does damage.

The seven Vespiquen pairings (5, 11, 16, 20, 23, 25, 27) were replayed with a counter added to legality_scan. Every game is identical, move for move, to its table game: kp3 3,500 of 3,500 against `../public_pricing_2026-09-25/kp3_500_*.jsonl`, and kq3 3,500 of 3,500 against `../kq_2026-09-25/kq3_500.jsonl`.

| | kp3 | kq3 | kq3 − kp3 (95% range) |
|---|---:|---:|---:|
| games with a Chase Order choice | 2,083 | 1,879 | |
| choices | 3,510 | 3,135 | |
| discarded any (share of choices) | 67.5% | 67.0% | −0.6 (−3.0, +1.6) |
| discarded Combee | 13.1% | 12.7% | −0.4 (−1.9, +1.3) |
| discarded Shuckle ex | 41.6% | 36.8% | −4.8 (−7.0, −2.6) |
| discarded Teal Mask Ogerpon ex | 12.9% | 17.4% | +4.5 (+3.0, +6.1) |

The ranges come from resampling whole games, because choices within one game go together.

What this shows:

- **The hypothesis doesn't hold.** kq3 is as willing as kp3 to discard Combee, so the bench term isn't taxing that discard.
- **The shift is between the two ex Basics.** kq3 keeps Shuckle ex more and discards Ogerpon ex more. A discard gives the opponent no points, so this is purely about which benched attacker the pilot values keeping.
- **kq3 reaches Chase Order less often** (3,135 choices against 3,510). That fits Vespiquen's lower kq3 score (42.2 against kp3's 45.8). Its opponents are the ones kq helped (see `../kq_2026-09-25/README.md`), so fewer of Vespiquen's games get to its attack.
- **Caveat:** the two bots play different games from the same deals, so these are shares over different positions, not paired choices. The counter records what was discarded, not which Basics were on the Bench at the time, so a share mixes what was available with what was chosen.

## Files

- `{kp3,kq3}_vespiquen.{txt,jsonl}`: the replays. Each game line has a `chase_order` field: {offered, discarded, names}.
- `run_chase_order.sh`: the commands. `tally_chase_order.py`: the checks and the table above. `timing.txt`: wall times.
