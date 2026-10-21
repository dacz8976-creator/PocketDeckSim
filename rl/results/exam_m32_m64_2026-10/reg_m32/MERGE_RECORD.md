# Merge record: kx3_exam_m32

**COMPLETE**: 1056 of 1056 expected games merged; 0 problem(s).

- Manifest: `/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/exam_m32_m64_2026-10/reg_m32/manifest.json`, sha256 `110c0c93d7b35520e3b577cec8061ace3f13197e4bc225c9f6fcaf85363d6aed`.
- Registered program sha256: `f5a6ae95051c0c673d45a6a8be9d6d840827a97bbb2feaaa0fccb4cbb8076b58`; engine: claude/playout-pilot 172cbe9ce0f2cb7946b489422b56d3fce5ca6219 engine tree 69a5a4419da2 (kx3 with the Tool rule, the skip bar and close calls as fixed after the laptop's reviews; ties join a running extension but never start one), built on the laptop Oct 8 with rl/strength/build.sh (main's harness source bf9c5d6814007f1f); gate 1 here: km3 240/240 v the official program, km3 81b572198c04d5d1, the lab form kx3_r2_c3_lab_tools_zs3_m64 8c1244aec5c8419d as in the cloud's gate 1, suite passed with 0 failed; at 54209409 the same build steps gave the frozen code 31d638dbc818b0fa and the Tool code c426e4c860e836ed (the code with every new suffix off is unchanged); KX_EXTRA_LISTS unset; this program predates rules switch 2 (the official program since Oct 12 is rl/engine-2026-10-12): the exam runs on the Oct 5 exam's rules on purpose, so that its games pair with the frozen kx3's (PLAN.md); repo commit: 1352203e70ce5d684a41dec6fac8df2b57e4c30e.
- Pilot kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m32 against reference km3; seed base 24500000000, pair stride 10000.
- Engine tree checked against: 69a5a4419da2.
- The merged games.jsonl holds each kept game's line as its worker wrote it, in the harness's job order.
- A worker with a problem of kind stamp, manifest, program, engine, stamp after play, seal, decks contributes no game (column Merged).

| Worker | Slice (--only-deck) | Games | Merged | Stamped | Program sha256 | Manifest sha256 | Engine tree |
|---|---|---:|---|---|---|---|---|
| E1 | 02-arceus-crobat, 11-archaludon-haxorus-dragonair | 192 | yes | 2026-10-14T00:28:26Z | `7e8cc544899fcb45d0de711d62b18aa0987c4ab0cf767e2cbca7b59766cf3d7a` | `110c0c93d7b35520e3b577cec8061ace3f13197e4bc225c9f6fcaf85363d6aed` | 69a5a4419da24f368eb7daa6946a711564485f61 |
| E2 | 04-absol-hoopa-darkrai, 08-garchomp-toolbox, 14-comfey-raticate-hypno | 288 | yes | 2026-10-14T00:25:48Z | `7e8cc544899fcb45d0de711d62b18aa0987c4ab0cf767e2cbca7b59766cf3d7a` | `110c0c93d7b35520e3b577cec8061ace3f13197e4bc225c9f6fcaf85363d6aed` | 69a5a4419da24f368eb7daa6946a711564485f61 |
| E3 | 07-skarmory-stall, 13-a-ninetales-raticate, draft-D-entei-grimhound | 288 | yes | 2026-10-13T23:29:47Z | `7e8cc544899fcb45d0de711d62b18aa0987c4ab0cf767e2cbca7b59766cf3d7a` | `110c0c93d7b35520e3b577cec8061ace3f13197e4bc225c9f6fcaf85363d6aed` | 69a5a4419da24f368eb7daa6946a711564485f61 |
| E4 | 12-ariados-whimsicott-ogerpon, 15-jolteon-oricorio-raticate, draft-C-meowstic-hatterene-v2 | 288 | yes | 2026-10-14T00:25:25Z | `7e8cc544899fcb45d0de711d62b18aa0987c4ab0cf767e2cbca7b59766cf3d7a` | `110c0c93d7b35520e3b577cec8061ace3f13197e4bc225c9f6fcaf85363d6aed` | 69a5a4419da24f368eb7daa6946a711564485f61 |

## Notes

- **rebuilt** worker E1: program sha256 7e8cc544899f, not the registration's f5a6ae95051c: a rebuild, accepted because its replayed self-checks equal the manifest's (km3, kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m32)
- **rebuilt** worker E2: program sha256 7e8cc544899f, not the registration's f5a6ae95051c: a rebuild, accepted because its replayed self-checks equal the manifest's (km3, kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m32)
- **rebuilt** worker E3: program sha256 7e8cc544899f, not the registration's f5a6ae95051c: a rebuild, accepted because its replayed self-checks equal the manifest's (km3, kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m32)
- **rebuilt** worker E4: program sha256 7e8cc544899f, not the registration's f5a6ae95051c: a rebuild, accepted because its replayed self-checks equal the manifest's (km3, kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m32)

## Problems

None: every expected game appears exactly once, with its registered inputs, from a worker on this manifest, program, engine tree and deck files, stamped before it played and sealed after.
