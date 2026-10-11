# Rules switch 2, step 8c: the one game that needs Dustin's word

8c checked all 1,133 games that came out differently under the rules update. 1,132 are explained by the rule's own tools. One needs a
judgment call, and the pin waits for Dustin's word on it (PLAN.md section 6).

**The game:** Whimsicott (held-out deck) v Sceptile, km3 on both sides, step 9, pairing 34, deal 449. On turn 8, from the same position,
the old engine's bot plays its Stadium and the new engine's bot plays Professor's Research. Same winner and same points.

**Why it changed (the hand trace, `8c/README.md` and `8c/hand_9_34_449/`):** the new rule makes two Ariados' Trap Territory count twice.
In the bot's planning, Professor's Research can draw the deck's second Ariados; it evolves the Benched Spinarak, and Grass Knot (30 more
damage for each Energy in the opponent's Retreat Cost) then Knocks Out the opponent's Active, which it would not under the old rule.
Turning off only the Trap Territory change brings back the old engine's choice and every score exactly; turning off any other change does
not.

**The judgment call:** the rule asks for the probe tool to find the cause inside the bot's planning. Here the probe found nothing, and
the hand trace above found it instead. Recommended: accept the hand trace (the cause is the intended Trap Territory rule).

**Dustin's word** (in the laptop session's chat, Oct 11 2026, about 16:20 UTC, verbatim): Yes the hand trace is good
