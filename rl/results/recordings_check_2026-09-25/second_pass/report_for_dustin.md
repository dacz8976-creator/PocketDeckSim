# Second pass over your recorded battles

## 1. What was read
- The first pass read only REVIEW.md and RESEARCH_HANDOFF.md for each battle. That was about 30% of the trusted review text (486 KB of 1,666 KB).
- This pass read everything else in the accepted review folders. That was 317 files, and none were missing.
- It also covered two battles the first pass skipped: SweetGameBuddy, and the partial Luckycad Xatu review.
- Gemini transcripts were left out on purpose. Gemini is the AI video reader. Its whole-video method failed our checks.

## 2. What was new
- This pass found 443 new observations. 134 of them repeated the first pass and were dropped. That left 204 new claims.
- Each claim was checked against the engine (the simulator's rules code):
  - **193** match what the engine does.
  - **5** seemed to disagree with the engine. All 5 fell apart (see section 4).
  - **3** can't be settled from the footage:
    - Does Sightseer show its find to the opponent? Only your screen was recorded.
    - Did Team Rocket's Rattata retreat for free with no helper card? Its printed cost is 1, and the start of that turn is cut off.
    - What did Galarian Perrserker's Dig Up find?
  - **3** are things the engine doesn't model: the damage number shown on screen, conceding, and zooming in on a card. None of them changes a game result.
- One side finding: the engine lets the A2b 111 Poke Ball be played with an empty deck. The P-A 005 printing is blocked, which is what the rules say. This isn't on the known-bug list.

## 3. Confirmed mismatches
None. No claim showed the engine playing a rule differently from the real game. Nothing here calls for an engine change.

## 4. Mismatches that fell apart
Three separate checks rejected each one.
- **Energy on Turn 1** (Pikachu in 031901, Riolu in SweetGameBuddy): the frames show no Energy on either Active. The reviews misread the turn.
- **Poke Ball sometimes shows the opponent's find:** in every "shown" case, the opponent benched that Basic right afterward. The found card always went to hand face-down.
- **Lisia put two Zubat straight onto the Bench:** the review said "added, then benched," which is two steps. The card puts them in your hand.
- **Frenzied Blade paid with 2 Energy, plus a lock on attacking next turn:** the in-game card at 04:21 shows the cost as Fighting, Metal, Colorless. The review missed Haxorus's third Energy. There is no lock.
- **Legendary Pulse drew before the promotion:** the frames show the promotion came first, which is the engine's order.
  - Side note: the engine does that Pulse draw one step late, after the next player's opening draw. No game result seems to change.

## 5. Corrections to the first pass
The fuller files correct 56 things the first pass took from REVIEW.md.
- **Rules were stated too broadly.**
  - Training Area's +10 is only for Stage 1 attackers hitting the Active.
  - Elegant Cape's +30 HP only counts on Stage 1 holders.
  - Small Balloon only helps Basics.
  - Jasmine's -50 works during the opponent's next turn, not the turn you play it.
  - Scorching Interruption's -30 protects Gouging Fire itself. It isn't a penalty on "the next attack."
  - Lightning Accelerator counts the attacker's own points.
  - Primeval Law only stops evolving the opponent's Active.
- **The wrong kind of effect.**
  - Turbo Shark, Darkness Claw and Cursed Jewel are attacks, not Abilities or Tools.
  - Boosted Evolution isn't an attack.
  - Mega Burning's and Soul Shot's discards happen as effects after the damage. They aren't costs.
- **"Seen" was really "guessed."**
  - In 004344 and 145205, most items rated "seen" came from the Gemini outline. Only a few moments were checked by hand.
  - Also downgraded: Luxury Coin's once-per-turn limit, the Securely Sheltered Heads, the Hand Kinesis hand sizes, whether Air Crash removes one Energy or all of them, whether Protective Poncho blocked anything, and the 133834 win (no result screen).
  - Rocky Helmet only fired on Knock Outs in these recordings. So they don't prove either "fires on any hit" or "fires only on a Knock Out."
- **Wrong details.**
  - 023151's timestamps were off.
  - 010316's Weakness turns were swapped.
  - The capped Watch Over heal was the 8th use, not the last.
  - The Mega Sharpedo ex that retreated for free on T13 had no Cape. Its printed retreat cost is 0.
  - Kirlia had 20 HP, not 50.
  - Nightmare Aura also fired on T6.
  - There was a third Rare Candy, on T15.
  - Giovanni never boosted an attack.
  - The screen stops at 3 points. So "2 to 3" after an ex Knock Out was really 2 + 2.
  - Lucky Ice Pop on Heads goes back to your hand, not into the deck.

## 6. Open questions worth recording
Only 2 of the 37 open questions need a new recording. The rest are settled by card text, or only need a frame check of footage you already have.
- **Victini's Victory Star while Confused.** The card lets you redo the coin flips for an attack. The engine turns it off completely when the attacker is Confused. That is probably wrong, at least for the attack's own coins.
  - *What to capture:* Victini in play, and your Confused Fire Active using a coin-flip attack.
  - Does the game offer Victory Star (a) on the Confusion flip itself?
  - Does it offer it (b) on the attack's own coins, after the Confusion flip lands Heads?
  - The opponent has to Confuse you, so this needs a friend battle or luck. Low priority.
- **Two Sitrus Berries on one Revavroom.** Is the half-HP check done again after the first Berry heals? The engine assumes yes, but nobody has confirmed it.
  - *What to capture:* Revavroom (120 HP) holding two Berries, at 40–60 HP when a turn ends.
  - If one Berry heals and the other stays attached, the game checks again.
  - If both heal and both are discarded, it checks only once.
  - A Solo battle is enough. Low priority, since none of your decks use this.

Two small asks:
- rules/README item 4 cites 004344 for Poison Barb firing on a Knock Out. That part of 004344 comes only from Gemini. The Luckycad recording (02:59–03:10) shows it properly and would be a better source.
- Was 152812 a Solo match or PvP?
