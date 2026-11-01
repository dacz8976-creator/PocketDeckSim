# R8 catch-up: census copy

R8 (branch `laptop/r8-catchup-2026-10-29`) adds Ability mechanic variants to the engine. The registered opening Active
census (`rl/results/opening_active_census_2026-09-26/`) classifies every variant in its `census.py`'s `VARIANT_CLASS`,
but that folder is never edited (coordinator-088 Q7). This folder holds R8's own copy instead.

- `census.py`: a copy of `rl/results/opening_active_census_2026-09-26/census.py`.
  - Source sha256: `e2d82ad9f6980c7baaa9523384c47bbb913804fa9d7ac46ad4db0ce4328050b7`.
  - Last commit that touched the source: `fb124297b93e8b8cee77f15000bf9249c081b5cd`.
  - R8's changes: a provenance comment block at the top, and one `VARIANT_CLASS` entry,
    `'FlipMoreCoinsForNamedAttack': ('anywhere', False, 'board')` (R8-04b, Raboot's Jumping Coach, C1 023 / C1 137),
    the class `engine/src/players/opening_class.rs` gives it. Nothing else differs, so `census.json`'s `generated`
    label still reads as the source's.
  - R8-05a adds `'ReduceDamageToYourTypeWhileInPlay': ('anywhere', False, 'board')` (Melmetal's Metal Scrum) and reruns it.
  - R8-05c adds `'PutRandomNamedFromDeckOnBenchOnEvolve': ('evolve', False, 'board')` (Frogadier's Sudden Duplication) and reruns it.
  - It sits at the source's depth (`rl/results/<folder>/census.py`), so its `ROOT` still resolves to the repo root.
- `census.json`: this copy's own output, written next to it by one run from the repo root
  (`python3 -I -B rl/results/r8_catchup_2026-10-29/census.py`, R8-04b).
- `engine/src/players/opening_class.rs` cites this copy for `VARIANT_CLASS`.

Later R8 commits that add an Ability variant update this copy (its `VARIANT_CLASS`, its comment block and this README)
and rerun it, not the registered folder.
