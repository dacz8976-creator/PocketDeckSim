Decision this informs: whether kp3's setup evaluation gets the opening-Active term (koa, registered Sept 26: `../opening_active_census_2026-09-26/REGISTRATION.md` on main). This folder is the build's identity check (section 4), done before any koa table; the laptop runs the table, reads the footprint first, then the mixed rows and the reading. Engine: koa's build commit 9af40c8 (engine src = e935f42, the repaired engine; scan example af8489f, sha256 dec080ff1db5f58d31e2bb896045f0d9029932b84626681b788e0c002a3e480a).

Seeds: the table's deals only, 72,000,000 + pairing × 10,000 + i (i < 500 for k3 and kp3, i < 40 for kq3, kd3 and koa3), even i = first-named deck in seat 0.

# koa: identity checks at the build (Sept 26)

## The result, plainly

**Every check passes.** koa's code changes nothing but the opening Active, and only Altaria's.

- **k3 and kp3** replay the repaired engine's table move for move: 14,000 of 14,000 games each. Moves, choices, openings and results all equal `../rules09_fixes_2026-09-26/af8489f_{k3,kp3}_500.jsonl`, the new references.
- **kq3 and kd3** (40 deals per pairing, the kpr practice) equal the repaired engine's spot references: 1,120 of 1,120 each.
- **Switch off = kp3.** kp3 at 9af40c8 runs the new code path with every switch off, and it equals kp3 at the repaired engine.
- **The setup-only property, on the first 40 deals of every pairing** (1,120 games):
  - koa3 opens differently from kp3 in 73 games (6.5%), all of them Altaria's opening:
    - Darkrai → Eevee: 41;
    - Swablu → Eevee: 32.
  - No other deck's opening changed.
  - In the 1,047 games where both openings match kp3's, koa3's game equals kp3's move for move. No leak past turn 0.
- **Against the registration's predictions** (section 5; the whole table decides them, these are a first look):
  - Footprint predicted 6.0%; this sample shows 6.5%.
  - Altaria's openings changed in 73 of its 280 games (26.1%). The registered range is 22.6 to 25.4% over its 3,500 table games; a 280-game sample has a standard error of about 2.6 points, so this is within noise.
  - The transitions are the two registered ones, in about the registered proportions (Darkrai → Eevee 14.5 : Swablu → Eevee 9.5).
  - The results of the 73 changed games aren't read here; the table and the mixed rows read them.

## What was checked, from the registration's section 4

| check | result | file |
|---|---|---|
| k3 replays the table (14,000) | equal, 14,000 of 14,000 | `identity_k3_500.*` |
| kp3 replays the table (14,000) | equal, 14,000 of 14,000 | `identity_kp3_500.*` |
| kq3 spot replay (40 per pairing) | equal, 1,120 of 1,120 | `identity_kq3_40.*` |
| kd3 spot replay (40 per pairing) | equal, 1,120 of 1,120 | `identity_kd3_40.*` |
| every switch off = kp3 | kp3 at 9af40c8 above | |
| setup-only property | 0 of 1,047 unchanged-opening games differ | `identity_koa3_40.*`, `identity_check.txt` |
| unit tests (hand table, no-Espeon hand, phrase test, class counts, parser) | pass; full suite 1,935 passed | 9af40c8's commit message |
| mixed-row identity (every deck but Altaria plays kp3's games) | for the laptop's rows | |

- **The base.** The references are the repaired engine's. It changes table games through the promotion-timing and Legendary Pulse repairs (`../rules09_fixes_2026-09-26/`). Per section 4's second bullet:
  - kp3's table and its mixed-row references are regenerated at that engine first: `af8489f_kp3_500.jsonl` is kp3's regenerated table;
  - scoreboard v2's kp3 row is re-scored on it by the laptop;
  - koa's footprint and (b), (c) and (d) are read against those files.
- **The per-game openings.** Every table file from af8489f's scan on carries `"openings": [first-named deck, second]`, the per-game counter section 7 asks for, and a `"decisions"` fingerprint beside `"moves"`.

## What the laptop runs next

1. koa3's table: 28 pairings × 500 on the table's deals, built from 9af40c8.
2. The footprint first: the share of the 14,000 games whose moves differ from `af8489f_kp3_500.jsonl`. Under 15% (predicted 6.0%), the reserve route; 15% or more, the ordinary rule. It is fixed by that number before anything else is read.
3. The mixed rows: koa on Altaria, kp3 on the opponent, and the reverse; the kob and kor diagnostics; amendment 1's held-out rows (B2e's rows regenerated at this engine first).

## Files

- `run_identity.sh`: the command. `timing.txt`: wall times (on a machine shared with the repair replays).
- `identity_{k3,kp3}_500.{jsonl,txt}`, `identity_{kq3,kd3,koa3}_40.{jsonl,txt}`: the raw outputs.
- `identity_check.txt`: the comparison printed above.
