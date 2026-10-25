from v2_helpers import P, B
D = 'v2deck_5469f7747f'; G = '20261020_034501000_SR'
GR80 = 'Alolan Grimer B2 096'; MK = 'Alolan Muk B2 097'; MKX = 'Alolan Muk ex A3 111'; DN = 'Deceptive Needle B4 148'
PBR = 'Poison Barb A3 146'; RC = 'Rare Candy A3 144'
SK = 'Skarmory A2 111'; CO = 'Cosmog A3 085'; RH = 'Rocky Helmet A2 148'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
AMB_SK = 'Opponent Active Skarmory printing chosen by HP (80) and attack (Metal Arms); A2 111 and P-A 039 match'
AMB_CO = 'Opponent Cosmog printing chosen by HP (60) only; A3 085, A3 171, A4b 180, A4b 181 and P-A 067 match'
POS = [
P(G, 1, 1, [0, 0],
  dict(hand=[MK, DN, PBR, PBR, MKX], disc=[], dene='', board=[B(GR80, 80)], ko=0),
  dict(hand_count=3, disc=[], dene='', board=[B(SK, 80), B(CO, 60)], ko=0),
  ['Play:Poison Barb', 'Tool:Poison Barb@0', 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's Cosmog printing is chosen by HP (60) only",
  ambiguous=[AMB_SK, AMB_CO],
  notes="Global 1 = his 1st turn (he went first). '22-35s: Setup': opening five Alolan Muk, Alolan Grimer 80 (Pound), Deceptive Needle, "
        "two Poison Barb; Grimer Active alone -> 4 in hand. Opponent: Skarmory 80 (Metal Arms) Active, Cosmog 60 Bench, three cards in "
        "hand after setup (stated). 'Owner turn1 (global1)': draws Alolan Muk ex -> 5; Needle inspected only; Poison Barb to Grimer; no "
        "Energy (first player), no attack."),
P(G, 3, 2, [0, 0],
  dict(hand=[MK, DN, PBR, MKX, RC], disc=[], dene='', board=[B(GR80, 80, tool=PBR)], ko=0),
  dict(hand_count=3, disc=['Poké Ball A2b 111', "Professor's Research A4b 373"], dene='',
       board=[B(SK, 80, tool=RH), B(CO, 60, 'M'), B(SK, 80)], ko=0),
  ['Attach:1Darkness@0 zone', 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's Cosmog and Benched Skarmory printings are chosen by HP only; the opponent's Trainer printings (Poké "
            "Ball, Professor's Research, Rocky Helmet) are not shown (the first listed printings are used); the opponent's hidden Poké "
            "Ball is counted as finding a Basic (the review's stated end-of-turn hand of three agrees)",
  ambiguous=[AMB_SK, AMB_CO,
             'Opponent Benched Skarmory printing chosen by HP (80) only; A2 111 and P-A 039 match',
             'Opponent Rocky Helmet printing not shown; A2 148 used (A2 148, A4b 322 and A4b 323 match)',
             "Opponent's Poké Ball in the discard: printing not shown; A2b 111 used (A2b 111 and P-A 005 match)",
             "Opponent's Professor's Research in the discard: printing not shown; A4b 373 used (A4b 373 and P-A 007 match)"],
  notes="Global 3 = his 2nd turn. Hand after global 1: Alolan Muk, Needle, Poison Barb, Alolan Muk ex; 'Owner turn2 (global3)': draws "
        "Rare Candy -> 5 (the review lists the same five in hand). Opponent 'global2': draw (4), Metal to benched Cosmog, Poke Ball "
        "(hidden; +1), Professor's Research (+2 -1), Rocky Helmet to the Active Skarmory, bench second Skarmory -> three in hand (the "
        "review says so). Bench order: Cosmog (setup) then the second Skarmory. His move: Darkness to Grimer, end turn (no attack)."),
]
