# F1: a copied second punch after Rocky Helmet (the cloud, Oct 10)

Reader one's EQUIVALENCE F1. Commits on `claude/coin-prevention-round2`:
- f601abcb: the test, `g2_copied_second_punch_waits_for_the_copiers_promotion_after_rocky_helmet`.
- c7a25df4: the fix, G2's queued-hit promotion arm in `state/mod.rs`. This is the new P.
- fc6307c0: the suite at P, `suite_at_P.txt`, 2,103 passed and 0 failed.

## The official engine's order (the laptop's ask)

The F1 test hard-codes what it expects: the promotion first, then 120 damage. On its own it doesn't show what the official
engine does, so the test's play body was traced without its asserts.

`f1_trace.rs` is a scratch integration test, not part of the engine:
- **The board:** Mew ex with 3 Psychic and 20 HP left, plus Bulbasaur, against Mega Kangaskhan ex with Rocky Helmet, plus Meowth.
- **The play:** Mew ex copies Double-Punching Family. After that, at each step it takes Bulbasaur's promotion when that is
  offered, else the first choice, as the test does.
- **The output:** for each step, the actor and the kinds of choices offered, then the damage to the opponent's Active.

It ran over seeds 0-4 in two places:
- the official engine, 8626a35 (`trace_official_8626a35.txt`);
- P = c7a25df4 with G1 and G2 off, `with_plain_hit_coin(false, || with_queued_site_coin(false, ..))`, which is what the test's
  `seven_sites(false, ..)` does (`trace_c7a25df4_g1g2_off.txt`).

**The two traces are identical, byte for byte.** On every seed:
1. the first punch;
2. Rocky Helmet's two `ResolveAttackRetaliation` steps, which Knock Out Mew ex;
3. `Promote` (Bulbasaur);
4. the second punch, as a plain `ApplyDamage`.

The damage is 120 every time. So the official engine also promotes first, and the test's expected values are the official
engine's.

## Which call failed before the fix

`tests_before_fix.log` had one test with both calls in it. Here the test at f601abcb (before the fix) is split into two
tests (`tests_before_fix_split.diff`), and the run is in `tests_before_fix_split.log`:
- the switches-off call (`..._after_rocky_helmet`) passes;
- the switches-on call (`g2_copied_second_punch_switches_on`) fails. At seed 0 the queued second punch is offered before the
  promotion, and the test's own assert, "the second punch waits for Mew's player's new Active", stops it before
  `modify_damage` would panic on the empty Active.

The split exists only in this scratch run. The committed test is unchanged.
