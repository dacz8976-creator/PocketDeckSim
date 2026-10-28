# Ultra Beast lane (ublane), the night of Oct 27 UTC: result summary

Commits on this branch (coordinator-054; Dustin: "fix all the ultra beast"): 99ecccaa (non-ex Buzzwole joins `ULTRA_BEAST_NAMES`, `tests/ultra_beast_list_test.rs`) and 248e3152 (Blacephalon ex, Guzzlord, Ultra Necrozma ex; all 50 tagged printings tested).
The lane ran after K21's launch line, nice 19, CARGO_TARGET_DIR ~/dual_target, `--locked --offline`. Its log, as written:

```
2026-10-27T02:05:36Z start: K21 launch 895783553936ba7075efd5a25dc9af1c9678f564; C: 29G free
2026-10-27T02:11:00Z commit 1, tests/ultra_beast_list_test.rs: rc=0 in 324 s: passed 5 failed 0 ignored 0 compile_errors 0
2026-10-27T02:32:18Z commit 2, the full suite: rc=0 in 1278 s: passed 2234 failed 0 ignored 0 compile_errors 0
test legacy_ability_logic_test::test_celesteela_ultra_thrusters_switches_ultra_beast ... ok
test damage_reduction_trainers_test::test_beast_wall_does_not_protect_non_ultra_beasts ... ok
test damage_reduction_trainers_test::test_beast_wall_protects_ultra_beasts ... ok
     Running tests/ultra_beast_list_test.rs (/home/dacz8976/dual_target/release/deps/ultra_beast_list_test-32dd681954c25637)
test test_non_ultra_beasts_are_still_refused ... ok
test test_lusamine_accepts_every_tagged_ultra_beast_printing ... ok
2026-10-27T02:32:21Z pushed laptop/dual-fusion-release-prep-2026-10-24 (248e31526b71752d2ef64a64f9be9517adbe8fc6)
2026-10-27T02:32:21Z lane_ub end: PASS (commit 1 test: passed 5 failed 0 ignored 0 compile_errors 0; suite at commit 2: passed 2234 failed 0 ignored 0 compile_errors 0)
```

Expected suite count 2,234 = base 2,228 (cc5d6e04) + 6 new tests. The coordinator checked origin itself: 248e3152 is the branch tip.
