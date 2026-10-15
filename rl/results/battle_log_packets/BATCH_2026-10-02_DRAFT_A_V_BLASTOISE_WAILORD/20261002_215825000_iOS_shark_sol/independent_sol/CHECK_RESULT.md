# Independent Sol check: rejected frozen submission

Reviewer: /root/ind_drafta_manual3; gpt-6.1-sol, high.
Source: 20261002_215825000_iOS.MP4; SHA256 61fb9e041b4efa4ad31181c0cb89d94b38ad13f2bf194a48b8f606b24afb107c.
SUBMISSION.json SHA256: 61a76f93cb887d2ac414ae19404963a004acec61ff874fa98634741d52ce69ef.

All19 manifest files match. All135 fullframes,270 lossless crops,135 measured firstPTS and360 locator sample hashes match. All18 timeline grids plus setup preview were independently inspected; all9 fresh owner starts, all36 scheduled rows/35 unique bottom+top pairs, named Research/Ball/Copycat transactions, full turn sequence, inventory/copy minima, actors and four guide files were checked. No new movie decode/hash or capture.

Supported: manual computer battle, AutoOFF, owner wins3-0, went second,18turns,580damage. No owner opponent-turn choice occurs. Exact20 supplied deck remains separate from visually observed inventory.

D1 requires correcting native center-reveal references in TURN_LEDGER.json /turns/3/draws_and_searches/1/cards_in_reveal_order:
- Elegant Cape: requested 97.2s, measured 97.2017s, F0097.20.
- Lucky Ice Pop: requested 98.0s, measured 98.0017s, F0098.00.
- Cyrus: requested 99.0s, measured 99.0017s, F0099.00.
- Misty: requested 100.0s, measured 100.002s, F0100.00.
- Mega Sharpedo ex: requested 101.0s, measured 101.002s, F0101.00.

Matching SEEN_CARD_INVENTORY.json occurrences: /inventory/3/occurrences/0 Sharpedo; /inventory/9/occurrences/0 Cyrus; /inventory/11/occurrences/0 Cape; /inventory/12/occurrences/2 IcePop. Misty /inventory/5/occurrences/1 is alreadycorrect. F0101.50 can remain as completed-hand corroboration with that context. Names/order/counts do not change.

D2 requires visibility qualifications in TURN_LEDGER.json and GUIDE_UPDATE_SUPPLEMENT.json:
- T6: requested 143.5s, measured 143.515s (F0143.50). Water symbol visible in the glowing current orb during generation animation; smaller preview is not settled/legible at the selected boundary.
  Affected: /turns/5/board_at_start/owner/energy_zone and /owner_turn_start_observations/2/fresh_both_boards/owner/energy_zone.
  Later F0144.50, requested 144.5s/measured 144.515s: Visible current Water and interaction at144.5 establish later current availability; do not claim settled small preview here.
- T12: requested 243.5s, measured 243.512s (F0243.50). Current circle is visibly empty and already correctly labeled generation pending; no settled smaller preview is visible at the selected boundary.
  Affected: /turns/11/board_at_start/owner/energy_zone and /owner_turn_start_observations/5/fresh_both_boards/owner/energy_zone.
  Later F0244.50, requested 244.5s/measured 244.512s: Settled current Water and smaller Water preview at244.5.
- T18: requested 337.8s, measured 337.803s (F0337.80). Water symbol visible in the glowing current orb during generation animation; next Energy animation is over the board and a settled smaller preview cannot be read.
  Affected: /turns/17/board_at_start/owner/energy_zone and /owner_turn_start_observations/8/fresh_both_boards/owner/energy_zone.
  Later F0339.50, requested 339.5s/measured 339.503s: Unused-Energy warning explicitly establishes later Energy availability. F338.50 attack enlargement obscures orb and is not the availability proof.

T8 and T14 current pending labels and visible Water previews are alreadycorrect. T12 current pending label is alreadycorrect. T6/T18 keep visible current Water count1; exact readiness may be null during animation. Do not replace visible Water with zero. Next preview at T6/T12/T18 requires null/readability limit at selected boundary, with later confirmation kept separately.

No additional coverage gaps were found. Source limits: concealed opponent draws, unopened discard piles, hidden underlying evolution faces, printing IDs and subsecond physical inputs remain unverified. Full details, exact19hashmap, all actually inspected image paths and correction fields are in CHECK_RESULT.json.

The exact frozen submission is rejected pending guarded root repairs and a separately frozen effective recheck.
