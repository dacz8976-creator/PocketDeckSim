# Quick Growth diagnostic, Sept 24 (Claude Code, cloud)

Diagnostic only, never for a ranking. Why the simulator overrates Sceptile (rl/RUN5.md, update at the end of
the plan). All games k3 unless noted, rules4 engine built from `engine/` in this repo.

| File | What it is | Seeds |
|---|---|---|
| `quick_growth_switch.patch` | The one-line diagnostic build: `PDL_DIAG_NO_QUICK_GROWTH=1` switches Caterpie's Quick Growth off. Not in `engine/`. | — |
| `cells.py`, `cells_quick_growth_on_off.txt` | Sceptile's 7 cells, 400 games each (200 per seat): main engine, diagnostic build with the switch off (identical, as required), and Quick Growth off. Run: `python3 cells.py <engine> 400 "" <pairs>` or with `PDL_DIAG_NO_QUICK_GROWTH=1` as the third argument. | 81,000,000 + 10,000 × cell (+5,000 for the second seat) |
| `ends.py`, `sceptile_v_vespiquen_endings.txt` | 400 Sceptile v Vespiquen games: how each ended and which Pokémon were knocked out. | 72,230,000 and 72,230,500, 200 each (table deals reused) |
| `sceptile_v_vespiquen_seat_{a,b}_vv.log.gz` | Raw `-vv` logs of 200 Sceptile v Vespiquen games (attack counts, Chase Order discards, Quick Growth triggers). | 72,230,000 and 72,230,100, 100 each |
| `caterpie.py`, `caterpie_counterplay.txt` | How often Caterpie is knocked out before Quick Growth fires, by opponent, with k3 and with k5 opponents (Sceptile k3). | 20,000,000,000 + 100,000 × opponent (+50,000 for the second seat) |
| `table_replay_altaria_blaziken.csv` | Every game of the Sept 23 table's Altaria v Blaziken cell replayed in the cloud; the table's own 1,000 reproduce 58.3% exactly. | 72,000,000 – 72,000,999, both seatings |

The see-everything test's code and outputs belong to Opus's Cowork session and are not in this folder.
