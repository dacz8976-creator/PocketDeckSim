# Merge record: kx3_think_m16_a

**COMPLETE**: 480 of 480 expected games merged; 0 problem(s).

- Manifest: `/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/thinking_time_2026-10/reg_m16_a/manifest.json`, sha256 `997a5273a3122d56eebf300b3a27872aaf3a62e0c83e6e109a34428397941612`.
- Registered program sha256: `f5a6ae95051c0c673d45a6a8be9d6d840827a97bbb2feaaa0fccb4cbb8076b58`; engine: claude/playout-pilot 172cbe9ce0f2cb7946b489422b56d3fce5ca6219 engine tree 69a5a4419da2 (kx3 with the Tool rule, the skip bar and close calls as fixed after the laptop's reviews; ties join a running extension but never start one), built on the laptop Oct 8 with rl/strength/build.sh (main's harness source bf9c5d6814007f1f); gate 1 here: km3 240/240 v the official program, km3 81b572198c04d5d1, the lab form kx3_r2_c3_lab_tools_zs3_m64 8c1244aec5c8419d as in the cloud's gate 1, suite passed with 0 failed; at 54209409 the same build steps gave the frozen code 31d638dbc818b0fa and the Tool code c426e4c860e836ed (the code with every new suffix off is unchanged); KX_EXTRA_LISTS unset; repo commit: 1b11c13cad709ebc4cd0185b97b1a1a78792c182.
- Pilot kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3 against reference km3; seed base 24400000000, pair stride 10000.
- Engine tree checked against: 69a5a4419da2.
- The merged games.jsonl holds each kept game's line as its worker wrote it, in the harness's job order.
- A worker with a problem of kind stamp, manifest, program, engine, stamp after play, seal, decks contributes no game (column Merged).

| Worker | Slice (--only-deck) | Games | Merged | Stamped | Program sha256 | Manifest sha256 | Engine tree |
|---|---|---:|---|---|---|---|---|
| W3 | 10-xatu-oricorio-tr-weezing | 160 | yes | 2026-10-12T12:10:07Z | `7e8cc544899fcb45d0de711d62b18aa0987c4ab0cf767e2cbca7b59766cf3d7a` | `997a5273a3122d56eebf300b3a27872aaf3a62e0c83e6e109a34428397941612` | 69a5a4419da24f368eb7daa6946a711564485f61 |
| W5 | 06-mega-blaziken-tournament-list | 160 | yes | 2026-10-13T00:11:25Z | `7e8cc544899fcb45d0de711d62b18aa0987c4ab0cf767e2cbca7b59766cf3d7a` | `997a5273a3122d56eebf300b3a27872aaf3a62e0c83e6e109a34428397941612` | 69a5a4419da24f368eb7daa6946a711564485f61 |
| W6 | 09-mega-manectric-heliolisk | 160 | yes | 2026-10-12T20:03:10Z | `7e8cc544899fcb45d0de711d62b18aa0987c4ab0cf767e2cbca7b59766cf3d7a` | `997a5273a3122d56eebf300b3a27872aaf3a62e0c83e6e109a34428397941612` | 69a5a4419da24f368eb7daa6946a711564485f61 |

## Notes

- **rebuilt** worker W3: program sha256 7e8cc544899f, not the registration's f5a6ae95051c: a rebuild, accepted because its replayed self-checks equal the manifest's (km3, kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3)
- **rebuilt** worker W5: program sha256 7e8cc544899f, not the registration's f5a6ae95051c: a rebuild, accepted because its replayed self-checks equal the manifest's (km3, kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3)
- **rebuilt** worker W6: program sha256 7e8cc544899f, not the registration's f5a6ae95051c: a rebuild, accepted because its replayed self-checks equal the manifest's (km3, kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3)

## Problems

None: every expected game appears exactly once, with its registered inputs, from a worker on this manifest, program, engine tree and deck files, stamped before it played and sealed after.
