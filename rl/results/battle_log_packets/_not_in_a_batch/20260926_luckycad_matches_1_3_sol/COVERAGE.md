# Coverage and evidence index

Source seconds are original video time. The prepared `phone_overview/t_000001.jpg` is second 0, so add one to a cited second for the frame filename. All `contacts_20s/contact_001.jpg` through `contact_048.jpg` were visually scanned in sequence. Full-resolution phone frames listed in `SOURCE.json` were checked at the event points below. The original mp4 remains in place and its SHA-256 was verified this session.

| Interval | Coverage | Boundary and direct anchors |
|---|---|
| 00:00-00:12 | Intro/deck overlay and match 1 setup | `contact_001`; `phone_overview/t_000009.jpg` (00:08 setup) |
| 00:13-03:49 | Match 1, Mattis, all visible turns 1-7 | `contact_001`-`contact_012`; native 00:55, 01:05, 01:56, 02:39, 03:18, 03:40, 03:47 |
| 03:50-03:59 | Match 1 victory and match 2 pairing/setup | `contact_012`; 03:51 Victory, 03:54 versus, 03:57 going second |
| 04:00-09:44 | Match 2, あんむ, all visible turns 1-12 | `contact_013`-`contact_030`; native 04:10, 04:36, 05:00, 05:09, 05:26, 06:05, 06:54, 08:08, 08:31, 08:43, 09:07, 09:25, 09:28-09:41 |
| 09:45-09:59 | Match 2 victory and match 3 pairing/setup | `contact_030`; 09:45 Victory, 09:48 WeePee versus, 09:52 opening setup |
| 10:00-15:35 | Match 3, WeePee, all visible turns 1-14 | `contact_031`-`contact_047`; native 10:03, 10:34, 10:48, 11:18, 11:56, 12:17, 12:47, 13:11, 13:33, 13:55, 14:38, 14:56, 15:15, 15:21, 15:31 |
| 15:36-15:59 | Match 3 victory and match 4 setup | `contact_047`-`contact_048`; 15:35 Victory, 15:38 next versus, 15:41 next going first. Match 4 is outside this packet. |

No gameplay jump or edited-out turn is apparent inside these three matches in the 1 fps contact sequence. This does not rule out a subsecond cut or an action completed wholly between sampled frames. Overlays and animations occasionally hide card text; the REVIEW labels those details as uncertain rather than filling them from game rules. The native crop visibly holds the entire battle board, including top and bottom point tracks, Active and Bench rows, hand, discard, energy zone and timer. The source sidebars contain deck artwork and webcam, not battle actions.

## Terminal reconciliation

| Match | Before terminal event | Terminal evidence | Result |
|---|---|---|---|
| 1 | Player 0, Mattis 1; poisoned Mega Lucario ex at 180 HP, Xatu 80 HP | 03:30 Will, 03:35 guaranteed heads, 03:38 Life Drain, 03:41 target 10 HP, 03:42 Poison KO, 03:47 `+3 points!`, 03:51 Victory | Player 3, Mattis 1 |
| 2 | Player 2, あんむ 2; Mega Charizard X ex with Giant Cape at 230 HP, Poisoned and Burned; Xatu 40 HP | 09:20 Will, 09:24 heads, 09:29 Life Drain leaves 10 HP, 09:31 Burned 20 reaches 0, 09:34 burn check heads, 09:40 `+3 points!`, 09:45 Victory | Player 3, あんむ 2 |
| 3 | Player 2, WeePee 2; Indeedee ex at 120 HP and Poisoned, Xatu 80 HP | 15:12 Will, 15:21 heads, 15:22 Life Drain, 15:24 target 10 HP, 15:26 Poison 10 KO, 15:31 `+2 points!`, 15:35 Victory | Player reaches win threshold, WeePee 2 |

Note: In match 2, Burn is the directly displayed finishing 20-damage checkpoint; a subsequent heads flip removes Burn even though the card is already at 0 and leaving play. Calling Poison the terminal cause would be incorrect. Match 1 and 3 have the Poison 10 finish.

## Limits for independent review

- Match 2's first Farfetch'd is full art but has 60 HP, directly readable in the 04:09 card popup (`phone_overview/t_000250.jpg`); the second also has 60 HP. Both award one point. The brief tool/attack sequence at 04:25-04:45 includes a status coin and attachment, but the exact order of every item is hard to recover from contact sheets; see REVIEW.
- Match 2 at 07:17-07:23: Life Drain is visibly used against a Poisoned 30 HP Farfetch'd, with a tails-like coin outcome and no HP set-to-10 effect. The coin face should be checked from original video if used for simulator validation.
- Match 3's two Magmar knockouts, Indeedee ex's healing, and the change between Xatu and Magmar depend on brief overlays; REVIEW records the visible before/after and avoids attributing an unseen card or Energy attachment.
- Exact Energy icons are cited where readable. A 1 fps visual pass cannot establish every animation substep, hidden hand/deck state, or every attachment if it completes between frames.
