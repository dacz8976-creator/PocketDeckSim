# Step 8c: the games that need a judgment (Dustin's)

Each is a lookahead difference (the same state and the same offered moves on both engines, a different choice) with no reach counter in its window, where vs_probe finds nothing and coin_probe finds repair B's queued coin-path choice only at the leaf: offered after 3 of the mover's moves, in a mixed frame (plain ApplyDamage choices beside it), which the bot never applies at ply 3. So the repaired code is in the tree only as an unpriced leaf; whether that counts as the mechanic acting is the judgment (coin_lookahead.py's NEEDS A JUDGMENT).

None.
