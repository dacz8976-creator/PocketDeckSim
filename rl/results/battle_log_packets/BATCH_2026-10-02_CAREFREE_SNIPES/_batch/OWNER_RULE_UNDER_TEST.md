# Owner-specified rule under test

Dustin supplied two files, 20261002_161001000_iOS.MP4 and 20261002_161342000_iOS.MP4, as two parts of one computer battle interrupted by a recording cut. These are rules tests, excluded from Pause Games and Ladder Log.

Quoted simulator description supplied by owner:

> Today (official engine, main-d363ba8): no coin. A snipe's damage is delivered as a separate damage step that never flips the defender's coin, so Linear Attack always does 50 to Meowth and Tongue Whip always 30 (rules/09, 'Open engine bugs': coin-flip damage Abilities never flip for damage dealt through a queued choice). After the rules switch (repair B, not pinned yet): the coin flips for these attacks and heads prevents the damage (apply_attack_action.rs, queued_attack_damage_choice; test carefree_steps_flips_for_a_direct_damage_snipe). The same change covers Absol's Leap Over and Team Rocket's Hypno's Entrap.

This is the owner's provided prediction and code-reference context, not an independently verified current engine snapshot. Review the actual targeted attacks, selected defender, coin prompt/result, HP before/after, and interruptions. Do not generalize from the observed attacks to unfilmed Absol or Hypno cases. No simulator edits, repair pinning, fixture ingestion, or training are authorized by this review request.

Owner clarification during review: "The test was to show a 'snipe' attack on a benched Meowth. Linear Attack and Tongue Whip are just examples of 'snipe' attacks." Treat Tongue Whip as the filmed example of the intended class interaction. The absence of another example is not a missing requested test.
