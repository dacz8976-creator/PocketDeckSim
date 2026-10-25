from v2_helpers import P, B
D = 'v2deck_06ee642b71'; G = '20261019_223400000_SR'
HO = 'Hoopa ex B4 103'; BA = 'Baltoy A3a 030'; CL = 'Claydol A3a 031'; KO = "Team Rocket's Koffing B4a 042"
WZ = "Team Rocket's Weezing ex B4a 043"; MS = 'Mega Sableye ex B3b 041'; AG = 'Alolan Grimer A3 110'
PR = "Professor's Research P-A 007"; PB = 'Poké Ball P-A 005'; GZ = "Team Rocket's Goo-zooka B4a 068"; CY = 'Cyrus A2 150'
# opponent's cards (printing: the first cards.py lists among those matching every shown fact)
MO = 'Moltres ex A1 047'; VI = 'Victini B3 025'; RC = 'Rainbow Cave B4 155'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
AMB_MO = 'Opponent Moltres ex printing chosen by HP (140) and attack title (Inferno Dance); A1 047, A1 255, A1 274, A3b 103, A4b 067 and P-A 025 match'
AMB_VI = 'Opponent Victini printing chosen by HP (70) and Ability title (Victory Star); B3 025 and P-B 049 match'
POS = [
P(G, 1, 1, [0, 0],
  dict(hand=[GZ, PR, PB, MS], disc=[], dene='', board=[B(HO, 150), B(BA, 60)], ko=0),
  dict(hand_count=4, disc=[], dene='', board=[B(MO, 140)], ko=0),
  ['Play:Poké Ball', "Place:Team Rocket's Koffing@2", "Play:Professor's Research", 'EndTurn'],
  D, None,
  approx=AP,
  ambiguous=[AMB_MO],
  draws={0: [KO], 2: [PR, CL]},
  notes="Global 1 = his 1st turn (he went first; no Energy). '21-41 Coin/setup' row: opening five Goo-zooka, Hoopa ex, Professor's "
        "Research, Baltoy, Poke Ball; Hoopa ex Active 150, Baltoy benched 60 -> hand Goo-zooka, Research, Poke Ball. Opponent: Moltres "
        "ex 140 Active, empty Bench; hand 5-1 = 4 (no draw yet). '42-63 Global 1' row: draw Mega Sableye ex -> 4 cards. His move in the "
        "review's order: Poke Ball (reveals Team Rocket's Koffing), Koffing benched 'at right' (@2, the lowest empty slot after Baltoy "
        "in slot 1), Professor's Research (draws the 2nd Research and Claydol), no Energy, no attack, end."),
P(G, 3, 2, [0, 0],
  dict(hand=[GZ, MS, PR, CL, WZ], disc=[PB, PR], dene='', board=[B(HO, 150), B(BA, 60), B(KO, 60)], ko=0),
  dict(hand_count=3, disc=[], dene='', board=[B(MO, 140, 'R'), B(VI, 70)], ko=0, zone='R'),
  ['Evolve:Claydol@1', "Play:Professor's Research", 'Place:Alolan Grimer@3', "Evolve:Team Rocket's Weezing ex@2", 'Ability@2',
   "Play:Team Rocket's Goo-zooka", 'Attach:1Darkness@0 zone', 'Attack:Shadow Bullet'],
  D, None, stadium={"card": RC, "owner": 1},
  approx=AP + "; the opponent's next Energy read as Fire from the review's 'The zone remains Fire' (global 2)",
  ambiguous=[AMB_MO, AMB_VI],
  draws={1: [AG, CY]},
  notes="Global 3 = his 2nd turn. Hand after global 1: Goo-zooka, Mega Sableye ex, Professor's Research, Claydol; '103-110' row: draw "
        "Team Rocket's Weezing ex -> 5 cards. Board: Hoopa 150 Active, Bench Baltoy 60 (left), Koffing 60 (right). Discard: Poke Ball, "
        "Research. Opponent, '64-83' and '84-102' rows: hand 4, draw 5, Victini benched (-1) 4, Rainbow Cave played (-1) 3 ('Three "
        "opponent hand backs remain'), Stadium used, one Fire to Moltres; Inferno Dance 0 heads after the Victory Star reflip; no "
        "damage. His move in the review's order: Baltoy -> Claydol (@1), 2nd Professor's Research (draws Alolan Grimer, Cyrus), Grimer "
        "benched 'into center' (compacted Bench: lowest empty slot @3), Koffing (@2) -> Weezing ex with Boiler Smog accepted "
        "(Ability@2: Moltres Poisoned and Burned), Goo-zooka, Darkness to Hoopa, Shadow Bullet (30 Moltres, 20 to Victini, the only "
        "Benched target, so no target label)."),
]
