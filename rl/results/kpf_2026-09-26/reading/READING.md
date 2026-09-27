# kpf's reading (registration section 6), Sept 27

**All games are at kpf's build (9bffbda). Its `engine/` equals the official release's source (main-83e17ae, `rl/engine-2026-09-27/`), so this reading is on the official engine against official baselines (`../../scoreboard_v3_2026-09-27/`).**

## In plain words

- **kpf is far more accurate overall, but the adoption rule says "do not adopt"** because of vetoes.
  - Over the 45 scoreboard cells, its real error is 12.5, against kp3's 15.5 (development half).
  - The paired ΔMSE interval is entirely below zero: −84.2, from −149.9 to −21.3.
  - Its mixed rows show kpf's own side playing worse beyond noise in three cells (Altaria v Suicune, Blaziken v Lucario, Lucario v Suicune) and two decks (Altaria, Vespiquen). Those are kpr's side effects on the table decks, the ones that failed kpr3 on Sept 26.
  - Under the Sept 26 rule, "not adopted" is provisional until the coverage decks are read.
- **The coverage decks favour kpf.**
  - **Held-out archetypes (B2e):** no held-out deck moves more than 2 points further from Limitless, and 5 of 6 move closer (`heldout_check.md`).
    - Charizard Y: 44 → 53, real 49.
    - Hoopa/Absol: 57 → 47, real 50.
  - **Scizor coverage row:** panel average 34 (kp3 32), real 32 on very few matches (`scizor_row.md`).
- **The two parts separately:**
  - **R alone (kpr3)** is almost the same as kpf: real error 12.5, ΔMSE −84.7, with the same vetoes firing (its mixed rows weren't run).
  - **F alone (kpg3)**, the discard-Energy credit, is a clean improvement: real error 15.5 → 14.0, ΔMSE −43.2 (−62.2 to −26.5), and **no veto fires**. By the rule it reads "adopt", pending the held-out check, which wasn't run for kpg3.
  - But the registration made kpg a diagnostic, never adopted. Whether to register it as a candidate is Dustin's call.
- **Open causes, as registered:** Hydreigon's overshoot, and now the three vetoed cells. Altaria/Greninja's gap is still undiagnosed.

## Files

- `score45_{kpf3,kpr3,kpg3}_vs_kp3.txt`: score.py on the 45 cells (`score45.py`; its logic untouched), rules v2. kpf3's reading uses its mixed rows (`mixed_{table,new17}_kpf3_{first,second}.jsonl`).
- `heldout_check.md` (`heldout_check.py`): B2e's 48 archetype pairings under kp3 and kpf3 against Limitless pooled (development beside). Dustin's files (48-95) are reported, never counted.
- `scizor_row.md` (`scizor_row.py`): the coverage row. It became runnable once the promotion repair was in the build, which removes Bullet Slugger's false +50.
- `trace_rayquaza_v_lucario_{kp3,kpr3,kpg3,kpf3}.txt` (`run_traces.sh`): the trace diagnostics and the hoarding check (section 9).
- Runs: `run_kpf_reading.sh`, `run_kpf_mixed.sh`, `STATUS.txt`; identity against the cloud's build in `identity_check.txt` (1,120 of 1,120 for k3 and kp3).
