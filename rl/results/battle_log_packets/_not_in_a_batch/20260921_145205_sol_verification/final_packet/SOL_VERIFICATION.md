# Bounded Independent Sol Verification

## Disposition

- Interval 1, 02:32-02:40: **PASS with required corrections integrated**.
- Interval 2, 03:38-04:02: **PASS**.
- Final disposition: **COMPLETE and independently accepted**.

This was a bounded independent verification, not an independent frame-by-frame review of the entire recording.

## Timestamped evidence

| Time | Evidence | Finding |
|---|---|---|
| 02:31.9 | `frames/02-31.900-darkness-energy-available.jpg` | At the start of Turn 5, a Darkness Energy is already generated and available in the player's Energy Zone. |
| 02:34.0-02:35.3 | `frames/02-34.000-pokemon-communication-inspected.jpg`; `frames/02-35.250-pokemon-communication-remains-in-hand.jpg` | Pokemon Communication is enlarged/inspected, then returns to the hand. It is not played and produces no failure message. |
| 02:36.0-02:37.3 | `frames/02-36.000-cabbie-selected.jpg` | Cabbie is selected and played. Its text searches for a random Stadium card. |
| 02:38.9 | `frames/02-38.900-cabbie-no-target.jpg` | The visible message, "There are no cards in the deck that can be the target of the effect," is Cabbie's failed Stadium search. |
| 02:40.6-02:41.3 | `frames/02-40.800-darkness-energy-attachment.jpg`; `frames/02-41.300-darkness-energy-attached.jpg` | The already-generated Darkness Energy is attached to Active Mega Sharpedo EX after Cabbie's failure. The animation begins just after 02:40 and settles by about 02:41.3. |
| 03:29.5 | `frames/03-29.500-lucky-ice-pop-heads.jpg` | Lucky Ice Pop's first flip is Heads, so that card returns to hand. |
| 03:30.8 | `frames/03-30.750-same-lucky-ice-pop-replayed.jpg` | The returned on-screen Lucky Ice Pop is immediately selected again. No second copy enters or appears in hand. |
| 03:40.8 | `frames/03-40.750-first-communication-played.jpg` | First Pokemon Communication is played. |
| 03:46.8 | `frames/03-46.750-first-communication-mega-sharpedo-out.jpg` | Mega Sharpedo EX, 190 HP, is the confirmed hand card shuffled into the deck. Gyarados ex was inspected earlier but was not the final selection. |
| 03:48.0 | `frames/03-48.000-first-communication-gyarados-in.jpg` | Regular Gyarados, 130 HP with Wild Swing, is selected from the deck and added to hand. |
| 03:50.3 | `frames/03-50.250-first-resulting-hand.jpg` | Resulting five-card hand: Cabbie, remaining Pokemon Communication, Gyarados ex, Wallace, and regular Gyarados (130 HP). |
| 03:52.8 | `frames/03-52.750-second-communication-played.jpg` | The remaining Pokemon Communication is played. |
| 03:55.5 | `frames/03-55.500-second-communication-gyarados-ex-out.jpg` | Gyarados ex, 180 HP, is the confirmed hand card shuffled into the deck. |
| 03:57.0 | `frames/03-57.000-second-communication-mega-sharpedo-in.jpg` | Mega Sharpedo EX, 190 HP, is selected from the deck and added to hand. |
| 03:58.0 | `frames/03-58.000-second-resulting-hand.jpg` | Resulting four-card hand: Cabbie, Wallace, regular Gyarados (130 HP), and Mega Sharpedo EX (190 HP). |

## Corrections applied to the Gemini packet

1. Removed the claim that Pokemon Communication was played and caused a no-target message at about 02:35. It was only inspected and remained in hand.
2. Assigned the 02:38.9 no-target message to Cabbie, whose Stadium search failed.
3. Corrected the Turn 5 order: Darkness Energy was generated and available by 02:31.9; Pokemon Communication was inspected; Cabbie was played and failed; then the Darkness Energy was attached at about 02:40.6-02:41.3.
4. Added the exact input card, output card, and resulting visible hand for each Pokemon Communication use.
5. Confirmed that the Lucky Ice Pop preceding the interval was the same on-screen card replayed after Heads, not a second copy.
6. Corrected the retaliatory damage wording everywhere: Rocky Helmet caused Mega Sharpedo EX to fall from 190 to 170 HP, then Destiny Burst caused 170 to 100 HP.
7. Removed the `/mnt/c/...` duplicate from `historical_paths`; it was only an alternate representation of the native Windows path.
8. Replaced all pending/partial placeholders with the completed verification status and preserved separate Gemini-first-pass and Sol-verification attribution.
9. Rephrased the concession math so it does not claim a displayed four-point score. A knockout of Mega Sharpedo EX would award three points and therefore immediately satisfy the three-point win condition from the opponent's existing one point.

## Acceptance basis

The Gemini draft supplied the full-battle first pass. The Sol verifier treated it as untrusted, matched the source to the expected SHA-256 before inspection, checked the requested action-dense intervals independently, reconciled every discovered conflict, and confirmed that the corrected packet has no unresolved placeholders. The acceptance is independent for the bounded verification and lead disposition, not a claim of a second full-video review.
