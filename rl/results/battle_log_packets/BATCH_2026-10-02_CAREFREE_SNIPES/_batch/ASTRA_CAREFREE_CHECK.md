# Carefree Steps bench-snipe evidence check

Finding: The inspected frames support that benched Meowth's Carefree Steps triggers for Heatmor's Tongue Whip, flips a coin, and prevents the 30 attack damage on the shown heads result. The ability banner explicitly names Carefree Steps; this prevention flip is not identified as Victory Star.

Evidence, relative to Recording_QA/20261002_161342000_iOS_rule_sol/evidence/:

- t0086.00.jpg: The damage-target prompt is visible. Meowth is benched with 50 HP; Heatmor's Tongue Whip text specifies 30 damage to an opposing Benched Pokemon.
- t0087.00.jpg: Meowth glows and the ability banner reads "Carefree Steps."
- t0089.00.jpg: The coin prompt says to flip for attack damage and prevent that damage on heads.
- t0091.00.jpg: The result explicitly reads "Heads!"
- t0094.00.jpg: A shield effect surrounds Meowth, which retains 50 HP.

This is direct evidence for the filmed Tongue Whip example of a snipe hitting benched Meowth. Linear Attack is another user-supplied example of the class being investigated, not an attack verified in these frames. This check does not establish tails behavior, an empirical probability, or every snipe variant.

Code comparison is conditional on the owner's report: official main-d363ba8 is said to omit the coin for queued snipes, while repair B, which is not pinned, is said to add it. The observed trigger and heads prevention support the reported repair behavior over the reported no-coin behavior for this example. Neither the running engine nor built-code provenance was inspected, so this is not a verification of current source or deployed behavior. No inference is made about missing actions across a recording cut.

Scope: Five supplied frames inspected only. No full battle review, simulator changes, or external logging.
