from v2_helpers import P, B
D = 'v2deck_06ee642b71'; G = '20261020_001714000_SR'
KO = "Team Rocket's Koffing B4a 042"; CL = 'Claydol A3a 031'; PR = "Professor's Research P-A 007"; DN = 'Deceptive Needle B4 148'
SP = 'Starting Plains B2 154'; GZ = "Team Rocket's Goo-zooka B4a 068"; HO = 'Hoopa ex B4 103'
HT = 'Hitmontop A4 102'; R70 = 'Riolu A2b 042'; R60 = 'Riolu A2 091'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
POS = [
P(G, 2, 1, [0, 0],
  dict(hand=[CL, PR, DN, SP, GZ], disc=[], dene='', board=[B(KO, 60)], ko=0),
  dict(hand_count=3, disc=["Professor's Research A4b 373", 'Poké Ball A2b 111', 'X Speed P-A 002'], dene='',
       board=[B(HT, 80), B(R70, 70), B(R60, 60)], ko=0),
  ["Play:Professor's Research", 'Place:Hoopa ex@1', 'Play:Deceptive Needle', 'Tool:Deceptive Needle@1', 'Attach:1Darkness@0 zone',
   'Attack:Reverse Thrust', 'Activate:0@1'],
  D, None,
  approx=AP + "; the opponent's two Riolu printings are chosen by HP only (70 and 60; no attack shown); the opponent's Trainer printings "
            "in the discard (Professor's Research, Poké Ball) are not shown (the first listed printings are used); the opponent's Bench "
            "order is Riolu 70 (benched first) then Riolu 60 (retreated into the Bench spot Hitmontop left)",
  ambiguous=['Opponent Riolu (70 HP) printing chosen by HP only; A2b 042, A2b 104, A4b 210, A4b 211 and P-A 059 have 70 HP',
             'Opponent Riolu (60 HP) printing chosen by HP only; A2 091, B3 079 and B3 169 have 60 HP',
             "Opponent's Professor's Research in the discard: printing not shown; A4b 373 used (A4b 373 and P-A 007 match)",
             "Opponent's Poké Ball in the discard: printing not shown; A2b 111 used (A2b 111 and P-A 005 match)"],
  draws={0: [HO, PR]},
  notes="Global 2 = his 1st turn (he went second). '0-34s: Opening/setup': Koffing Active (60), Claydol, Professor's Research, Deceptive "
        "Needle, Starting Plains in hand, no Bench. '74-112s: Global 2, owner 1': draws Goo-zooka -> 5 cards. Opponent '35-73s: Global 1': "
        "Riolu 60 Active; opening 5 - 1 = 4, draw 5, bench Riolu 70 (4), Professor's Research -1 +2 (5), Poke Ball -1 +1 Hitmontop (5), bench "
        "Hitmontop (4), X Speed (3), retreat Riolu 60 into Hitmontop (X Speed: no Energy paid); no Energy (first player). Hitmontop 80 with "
        "Piercing Spin (global 3) = A4 102. His move in the review's order: Professor's Research (draws two; Hoopa ex visible and benched "
        "86-88s; the second card is not named, but the only other draw before global 4's Professor's Research is global 4's own draw "
        "(Copycat), so the second Research must have come here: draws = Hoopa ex + Professor's Research), Hoopa benched (slot 1), Needle "
        "to Hoopa 90-92s, Darkness to Koffing, Reverse Thrust ~100-104s (10 to Hitmontop, switches Koffing with Hoopa: the engine asks the "
        "switch target after the attack, its one legal choice 'Activate:0@1' = Hoopa in slot 1, written per convention 5)."),
]
