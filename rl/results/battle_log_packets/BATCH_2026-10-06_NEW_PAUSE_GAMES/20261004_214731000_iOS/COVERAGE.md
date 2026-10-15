# Source and protocol coverage

Source: `20261004_214731000_iOS.MP4`, frozen binding `SOURCE.json`. One recorded game, reviewed from 0 to 374.945 seconds. Reviewer `/root/pause_20261004_214731000_iOS`; independent acceptance pending.

| Interval | Coverage |
|---|---|
| 0-24.5 s | Matchmaking, CloutDemon identity, owner Dacz8976 and turn order |
| 24.5-38 s | Five opening slots, Caterpie Active placement, opponent Mega Rayquaza ex setup |
| 38-91 s | Opponent turn 1, public cards and concealed draws, automatic Quick Growth |
| 92-143 s | Owner turn 2, first play, all draws/searches, attachments, attack and Helmet |
| 144-181 s | Opponent turn 3, evolution, Research draw count, attachment and ending |
| 182-223 s | Owner turn 4, evolutions, Forest search, Pop Heads return, attachment and attack |
| 225-240 s | Opponent turn 5, attachment, Cyclizar, Mega Burst discard/damage |
| 241-298 s | Owner turn 6, both Pop uses, retreat payment, attachment, shuffle/replacement, three Trail draws and poison |
| 298-329 s | Opponent turn 7, discard Energy recovery, zone attachment, tool, poison and paralysis recovery |
| 329-355 s | Owner turn 8, Quick-Grow Extract, Energy, terminal attack, healing and Helmet |
| 355-374.945 s | Terminal animation and complete victory results |

No game turn is omitted. Boundary animation overlaps are documented in the row timings; 223-225 seconds is the owner attack resolution into opponent turn 5, not an uncovered play interval. The turn count agrees with the result screen.

Required deliverables are present: source binding, assignment, prose, coverage, summary, uncertainties, opening record, deck-version limit, eight-row turn ledger, frame manifest and native source evidence. No template rows remain. One row represents each owner and opponent turn.

Opening is captured before Active placement. Each owner turn has a localized normal draw, all three draw-offset candidates, selected intact pre-play hand, and pre-attack ending view. Original 1170 by 2532 frames and full-width bottom-fifth/top crops are retained with crop bounds. Sparse overview sheets do not supply the required hand record.

Owner draw/search identities are captured individually, including both Research cards, both Forest finds, Poké Ball's Shelmet, all three Hiking Trail draws, and Quick-Grow Extract's direct evolution. No Copycat is played by the owner. Opponent Copycat and other concealed additions have known visible counts and unknown faces.

Both boards, HP/max HP/damage, attached typed Energy, Tools, conditions, stadium, points, bench positions and both Energy Zone lines are represented at start/end boundaries. Opponent start fans are counted from native top evidence. Public action order includes repeat Pop and its coin outcomes, paid retreat and the explicit Forest Yes choice. No unshown prompt is called a decline.

Inspected-source limits: neither full discard pile is opened; the filmed deck is absent from the nine initial live-list snapshots and no QR appears in this source; exact queue/card printing identifiers and measured frame PTS are not exposed. These are recording or source-binding limits, not invented cards or missing game review. Capture supplement status is `complete_with_recording_limits`. Full battle first pass is submitted for independent acceptance.
