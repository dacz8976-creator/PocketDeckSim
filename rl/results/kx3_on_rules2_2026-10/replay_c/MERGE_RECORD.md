# Merge record: kx3_replay_rules2_c

**COMPLETE**: 20 of 20 expected games merged; 0 problem(s).

- Manifest: `/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kx3_on_rules2_2026-10/replay_c/manifest.json`, sha256 `2219f8ff75b3d8097c2e8d18c2e213b682c13f8208f7ce20ad14aedcdf35310b`.
- Registered program sha256: `76df495bef0b057fd28b4991dce76d3e3e1772667694161c945f17364f9c4e08`; engine: laptop/kx3-on-rules2 cd20a97a2e76897fae9883389cee4bf7ce5b3d97 engine tree 4ebb30a94173: the frozen kx3's players (d513e37b) on main-c045ede's engine (rules switch 2), built on the laptop Oct 12 with rl/strength/build.sh (harness bf9c5d68); self-checks km3 81b572198c04d5d1 and kx3 31d638dbc818b0fa, equal to the slow-report pin's; repo commit: e12342cd17f3c154cf8f4a1ca8a74c670552ebec.
- Pilot kx3 against reference km3; seed base 24420070000, pair stride 10000.
- Engine tree checked against: 4ebb30a941737d16b80adddbd1466761e0670e63.
- The merged games.jsonl holds each kept game's line as its worker wrote it, in the harness's job order.
- A worker with a problem of kind stamp, manifest, program, engine, stamp after play, seal, decks contributes no game (column Merged).

| Worker | Slice (--only-deck) | Games | Merged | Stamped | Program sha256 | Manifest sha256 | Engine tree |
|---|---|---:|---|---|---|---|---|
| R1 | 10-xatu-oricorio-tr-weezing | 20 | yes | 2026-10-13T10:43:43Z | `f492d55e8f768c3dbcb9138cfdc0093171156e621bb2e6e0c0999b22b62f7d5c` | `2219f8ff75b3d8097c2e8d18c2e213b682c13f8208f7ce20ad14aedcdf35310b` | 4ebb30a941737d16b80adddbd1466761e0670e63 |

## Notes

- **engine tree** worker None: the engine tree 4ebb30a941737d16b80adddbd1466761e0670e63 is named on the merge command (the registration's own: None)
- **rebuilt** worker R1: program sha256 f492d55e8f76, not the registration's 76df495bef0b: a rebuild, accepted because its replayed self-checks equal the manifest's (km3, kx3)

## Problems

None: every expected game appears exactly once, with its registered inputs, from a worker on this manifest, program, engine tree and deck files, stamped before it played and sealed after.
