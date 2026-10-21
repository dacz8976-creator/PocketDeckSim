# The held-out exam of m32 and m64: Dustin's decision (Oct 14)

The fixed rule recommended m64 (`READING.md`). Astra's review accepted m64 as the next slow deck tester after its current-engine
check. Dustin decided, relayed by Fable on Oct 14, verbatim:

> "I don't know. It's so slow and barely maybe better. Keep frozen kx3 for routine screening and use m64 selectively on deck questions I
> care about. The next development round should target the actual mistakes: passing up knockouts, exposing unprepared attackers, and
> failing to build the Bench. Unless we can actually show the drastically slower deck is better predictor of which decks will be good in
> real life, I'm not sure it's worth it, but also I guess we can try to make it better?"

**What follows from it:**
1. **No slow-report pin change.** The frozen kx3 stays the screener and the default deck tester. Every report keeps its pilot.
2. **m64 is a tester on request,** for deck questions Dustin cares about.
   - Its current-engine replay check (`../m64_on_rules2_2026-10/SPEC.md`) is finished at low priority, so m64 is usable the day he asks.
   - A report with m64 is run through a small pin-safe option or by documented hand steps, never by moving the pin.
3. **The next development round targets the mistakes Dustin named:**
   - passing up knockouts (the Kingambit case; the attack rule, tested both ways);
   - exposing unprepared attackers;
   - failing to build the Bench (the setup-deck gap the exam left unresolved);
   - plus the Kangaskhan corrections as decided (`../kangaskhan_pricing_2026-10-13/DECISION.md`).

   The design note is the laptop's to draft and Fable's to audit before anything is built.
4. **A validation plan:** does any bot's panel number (km3, the frozen kx3, m64) predict his real ladder results this season? The Ladder
   Log is the data. The plan says what sample size would show anything, so he can decide whether to log every game.
