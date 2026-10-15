# Coverage Checklist: 20260921_145205000_iOS.MP4

## Gemini first pass

- [x] Pre-Match / Setup (00:00-00:30)
- [x] Turn 1: Dacz8976 (00:30-00:54)
- [x] Turn 2: AI Opponent (00:55-01:23)
- [x] Turn 3: Dacz8976 (01:24-01:58)
- [x] Turn 4: AI Opponent (01:59-02:31)
- [x] Turn 5: Dacz8976 (02:32-03:02)
- [x] Turn 6: AI Opponent (03:03-03:16)
- [x] Turn 7: Dacz8976 (03:17-04:10)
- [x] Match termination / results screen (04:08-04:10)

## Bounded independent Sol verification

- [x] 02:32-02:40: exact ordering of Pokemon Communication inspection, Cabbie play and failure, and Darkness Energy generation/attachment. Adjacent frames through 02:41.3 were used only to finish the attachment already beginning at the interval boundary.
- [x] 03:38-04:02: both Pokemon Communication uses independently traced from the card returned to the deck through the card added to hand and the resulting visible hand.
- [x] 03:29-03:31 adjacent context: the Lucky Ice Pop that rolled Heads was tracked back to the hand and immediately replayed; no second copy appeared.

## Scope statement

The complete battle account outside those bounded checks remains attributed to the Gemini first pass. The Sol verifier confirmed source identity, performed the listed dense-frame checks, integrated the corrections, and completed the lead acceptance check. This packet does not claim that Sol independently reviewed every frame or the entire video.

No gameplay coverage placeholder remains in the packet.
