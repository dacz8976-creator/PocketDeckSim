# Review C vs Review X: g1 (Dacz8976/Dustin vs Ryze)

Review X's final word is `codex/REVIEW.md` as amended by `FINDINGS.json`, `UNCERTAINTIES.json`, `COVERAGE.md`, `QR_ID.json` and `LEAD_ACCEPTANCE.json`. No correction file changes any game fact. The lead acceptance is a plain PASS.

**Where they agree (no dispute):**
- Ryze went first.
- Dustin's opening hand: Elegant Cape, Wallace, Cabbie, Carvanha, Mega Gyarados ex.
- Dustin's Energy is Water.
- Every attack, its damage and the HP before and after:
  - Turbo Shark: 70 each time.
  - Rapid Smashers: 1 heads, 1 tails, 90, Confused.
  - Sharp Fang: 30.
  - Splash: 10.
  - Quick Straight: 50 ×3.
- The four Knock Outs and points: 1-0, 1-1, 1-2, 3-2.
- Dustin wins on points on global turn 12. Damage done 320. Rank 970 → 971.
- The opponent Pokémon: Buneary ×2, Mega Lopunny ex, Hitmonchan ex.
- The opponent Trainers: Serena, Copycat, X Speed, Professor's Research, Arena of Antiquity.

## Disagreements

| Turn | Item | C says | X says | Frames show | Frames | Verdict |
|---|---|---|---|---|---|---|
| G3 Ryze | Order: Fighting Energy vs evolution to Mega Lopunny ex | Energy on Buneary first (86–89 s), then evolved (90–91 s) | Evolved first (90–92 s), then attached Fighting (93–94 s) | Energy still in Zone at 87/89/92 s; Mega Lopunny ex in play at 92 s with no Energy; Energy on it at 94 s | t_0087, t_0089, t_0092, t_0094 | **X right** |
| G6 Dustin | Cards drawn by Copycat | Poké Ball, Mega Gyarados ex, Magikarp | Mega Gyarados ex, **two** Poké Balls, Magikarp | Cards revealed one by one: Poké Ball 170 s, Gyarados 171.5 s; hand at 173 s is exactly those 3, with Magikarp | t_0170, t_0171.5 (half), t_0173 | **C right** |
| G6 Dustin | Poké Ball plays | One Poké Ball, no effect; Magikarp came from Copycat | First Poké Ball (170 s) got Magikarp, second found nothing | Magikarp already in hand at 173 s before any Poké Ball play; no-target message 177 s; one Poké Ball in discard at 180 s | t_0173, t_0177, t_0180 | **C right** |
| G7 Ryze | When the Fighting Energy went on Hitmonchan ex | After X Speed + retreat, onto the Active Hitmonchan ex (222–225 s) | Onto the benched Hitmonchan ex at 212–213 s, before X Speed | Energy still in Zone at 212, 214, 222 s (X Speed already in discard at 222 s); on Active Hitmonchan ex at 225 s | t_0212, t_0214, t_0222, t_0225 | **C right** |
| G12 Dustin | Final Turbo Shark bench Energy / Gyarados final count | 4th Water attached to Mega Gyarados ex (4 at 346 s) | Gyarados ends with 3 Water; no further attachment | 3 Water at 337 s, 4 Water at 346 s | t_0337, t_0346 | **C right** |

Counts: C right 4, X right 1, both wrong 0, unsettled 0.

## Only C (confirmed by frames)
- Ryze's Energy Zone is Fighting (t_0087, t_0212).
- Ryze's opening Active Buneary, the one Knocked Out on turn 2, is a full-art card (in Ryze's discard at t_0087).
- At the end of G6, Dustin's hand is only Mega Gyarados ex (t_0180).

## Only X (confirmed by frames)
- Dustin's opening Carvanha is the Aqua Jet (10) version. The one Lisia found is the Sharp Fang (30) version (t_0029, t_0173).
- Buneary's attack is Double Kick, 20× (t_0087).
- Quick Straight's damage isn't affected by Weakness (t_0222).
- Magikarp's attack is Expert Splasher, 10+ (t_0173).
- Mega Gyarados ex's attack is Mega Blaster, 140 (t_0171.5).

No claim made by only one review is contradicted by the frames. Each review's errors are in the disagreement table above.

## Which review to rely on
**Review C is more reliable for this game.** The two reviews agree on every attack, damage number, Knock Out and the score, so either one gives the right result.

Where they disagree on a sequence, the frames side with C four times out of five:
- **Turn 6 (X's biggest error):** X invents a second Poké Ball and has a Poké Ball fetching Magikarp. In the frames, Magikarp came from Copycat, and the only Poké Ball played did nothing.
- **Turn 7:** X puts the Fighting Energy on the benched Hitmonchan ex before X Speed. In the frames it was attached after the retreat.
- **Turn 12:** X undercounts Mega Gyarados ex's final Energy at 3 instead of 4.

C's only error is the order of Energy and evolution on turn 3, which has no effect on the game. X adds some useful card-text details (attack names, the Aqua Jet vs Sharp Fang Carvanha versions). But a player rebuilding the turn sequence, or Dustin's hand and resources, should trust C.
