# Dustin's decision on the Double-Punching Family pricing (Oct 14, verbatim)

> **I'd fold it into the next pilot round and leave the current exam untouched.** This is a real bot-evaluation defect, even though it
> didn't change the eight recorded turns.
>
> After reading the findings and code, I'd amend the proposed fix in two ways:
>
> 1. **The one-line "add 40" forecast is incomplete.** The punches need separate damage adjustments. Against Heavy Helmet, the engine
>    does **60 + 20 = 80**. Adding 40 and subtracting the reduction once would forecast **100**, introducing the opposite error. Include a
>    test where that difference changes whether the defender survives. [Forecast code](engine/src/players/value_functions.rs:1787)
>
> 2. **The proposed search fix is broader than Kangaskhan.** Other attacks create the same single queued-damage action. Making those
>    actions resolve before scoring could be a useful general correction, but the claim that it affects "only Kangaskhan and copies" is
>    incorrect. Either scope it explicitly or test representative other attacks as part of the shared search fix. [Queued-damage
>    helper](engine/src/actions/apply_attack_action.rs:345)
>
> One useful distinction: **kx3's actual play-outs already include both punches.** The defects affect the judgment used to propose and
> play moves inside those simulations, rather than making every simulated outcome miss 40 damage.
>
> So my recommendation is: **next round, separately testable corrections, a new named pilot, and accurate scope.** No need to launch
> another immediate workstream.

## What this fixes for the next pilot round's design

These sit beside the skip rule's two-way gate, recorded in `../strength_2026-10-08_kx3_combined/HAND_CHECK_SKIPS_laptop.md`.
- **Nothing starts now.** The running exam, the slow reports and the position study keep their pinned builds.
- **The forecast correction:**
  - It prices each punch separately: the first punch's 80 and the second's 40, each with its own damage changes (Heavy Helmet: 60 + 20).
    It is not a flat +40.
  - It needs a test where the two forecasts disagree on whether the defender survives.
- **The search correction (the queued damage at the depth limit):**
  - It is a shared change. It reaches every attack that queues one plain damage action through `queued_attack_damage_choice`, not only
    Kangaskhan.
  - Its scope is either stated explicitly or tested on representative other attacks.
- **The two corrections are separately testable.** They ship as a new named pilot on a branch, not as an edit to the pinned km3. The
  self-check digests can't tell fixed from unfixed (their decks have no Kangaskhan), so the program and the pilot name carry the
  difference.
- **The scope note:** kx3's play-outs already count both punches. The defect is in the judgment that proposes and plays moves inside
  them.
