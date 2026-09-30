# The laptop's tier-1 second read of build B (Sept 30)

**What was read:** B = 1f6319e (km on kta), `git diff ec7e1a8 1f6319e -- engine/`, against km's registration and its Amendment 1 (3aed736). Read before the laptop built B, as Amendment 1 (g) step 4 asks.

**How:** two independent Opus readers, read-only (no build, no game):
- one against the spec: N2's bonus, the clock, both sides, the flag, the parser, the tests;
- one checking that kta, kog and every other preset are exactly as at ec7e1a8 with the flag off.

A third agent tried to refute the one finding that wasn't a note.

## Verdict: no blocker, no code finding

- **N2 does what the text says.**
  - The bonus covers Training Area (+10 for a Stage 1 attacker) and Arena of Antiquity (+20 for an [F] attacker hitting an ex). Both texts were checked with `lib/card.py`.
  - The threat is still picked on unbonused damage.
  - The bonus goes in before the cuts, as `modify_damage` applies it: the first hit is (damage + bonus) − (permanent + temporary), and each later hit is (damage + bonus) − permanent, floored at 0.
  - Both of `kt_clocks`' calls get the flag.
  - The evolved form is used only for the bot's own threat.
  - N2 opens no new path to hidden information.
- **With the flag off, B is ec7e1a8.**
  - The `kt_clock` → `kt_clock_stadium` change keeps the argument order, the types and the casts. With `false` it short-circuits before any new code.
  - `EvalFeatures` has no `Default`. The four full presets set the flag to false, every other preset spreads from one of them, and only `KM` sets it true.
  - `km` in the parser only catches codes that failed to parse before.
  - `public_pricing_player.rs` changes are test code only.
  - `engine/UPSTREAM.md` is not read by any build.
- **The one SHOULD_FIX was a timing gate, not code.** When it was read, the cloud's identity items 1-3 and 5 weren't in yet, so the laptop's games had to wait for them. They passed at 53fc5a1 (08:59 UTC), and the laptop's games started after that.

## Notes (none gate)

1. **No test would fail if N2 didn't reach the bot's own survival clock.**
   - `kt_clocks` passes the flag to both calls (`value_functions.rs:1911-1913`). That was checked by eye, and by the cloud's scratch diagnostic `review_note_a_diagnostic.rs`: under KM with Training Area, mine and theirs are 2 and 2, against kta's 3 and 3.
   - Suggested as a test in a later build.
2. **Two behaviours are right in the code but have no test:**
   - the threat is picked on unbonused damage (`:1762`);
   - each benched victim's own ex status is used (`:1829`).
3. **A simplification for km's reading to name:** for attacks that can roll 0 damage (coin flips), the clock adds the full bonus to the expected damage. The engine adds no bonus to a 0-damage roll.
   - Marowak ex's Bonemerang under Arena against an ex: the clock prices 100 a hit, where the engine's expectation is 95.
   - Kirlia's Double Spin under Training Area: 40 against 37.5.
   - This is within the registered formula.
4. **kt3, ktb3 and ktc3 at B carry no identity claim** (Amendment 1 (d) item 6). This read is not identity for them.

The full reader outputs are in the laptop session's workflow `wf_712be10c-378`.
