from v2_helpers import P, B
D = 'v2deck_06ee642b71'; G = '20261020_000857000_SR'
MS = 'Mega Sableye ex B3b 041'; DK = 'Darkrai ex A2 110'; KO = "Team Rocket's Koffing B4a 042"; WZ = "Team Rocket's Weezing ex B4a 043"
CC = 'Copycat B1 225'; MK = 'Alolan Muk B2 097'; GR = 'Alolan Grimer A3 110'; PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"
GZ = "Team Rocket's Goo-zooka B4a 068"; CY = 'Cyrus A2 150'; SP = 'Starting Plains B2 154'
DR = 'Drampa B4 124'; DT = 'Dratini A3b 051'; OPR = "Professor's Research A4b 373"
AP = "opponent's list unknown; opponent's hand size from the visible plays"
AMB_DT = 'Opponent Dratini printing chosen by HP (60) only (no attack shown); A3b 051, A4b 267, A4b 268, B2b 051, B2b 105 and B4 116 have 60 HP'
POS = [
P(G, 1, 1, [0, 0],
  dict(hand=[CC, DK, MK, WZ], disc=[], dene='', board=[B(MS, 170), B(KO, 60)], ko=0),
  dict(hand_count=3, disc=[], dene='', board=[B(DR, 100), B(DT, 60)], ko=0),
  ['Place:Darkrai ex@2', 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's Dratini printing is chosen by HP (60) only",
  ambiguous=[AMB_DT],
  notes="Global 1 = his 1st turn (he went first). '0-40s: Opening and setup': opening five Copycat, Darkrai ex, Alolan Muk, Team Rocket's "
        "Koffing, Mega Sableye ex; Mega Sableye ex Active, Koffing benched -> 3 in hand. '41-53s: Global 1 / owner 1': draws Team Rocket's "
        "Weezing ex -> 4 cards; benches Darkrai ex (Bench slot 2 after Koffing in slot 1), no Energy (first player), no Trainer, no attack, "
        "ends turn. Opponent: Drampa Active (100 HP), Dratini Bench (60 HP), opening 5 - 2 placed = 3 cards (the second player has not "
        "drawn yet). Drampa printing: Power Blast (global 4) = B4 124, the only Power Blast Drampa."),
P(G, 3, 2, [0, 0],
  dict(hand=[CC, MK, WZ, PB], disc=[], dene='', board=[B(MS, 170), B(KO, 60), B(DK, 140)], ko=0),
  dict(hand_count=5, disc=[OPR], dene='', board=[B(DR, 100, 'L'), B(DT, 60)], ko=0),
  ['Play:Poké Ball', "Evolve:Team Rocket's Weezing ex@1", 'Ability@1', 'Play:Copycat', 'Attach:1Darkness@0 zone', 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's Dratini printing is chosen by HP (60) only; the opponent's Professor's Research printing in the discard is "
            "not shown (the first listed printing is used)",
  ambiguous=[AMB_DT, "Opponent's Professor's Research in the discard: printing not shown; A4b 373 used (A4b 373 and P-A 007 match)"],
  draws={0: [GR], 3: ['-' + MK, '-' + GR, GZ, PR, CY, SP, MK]},
  notes="Global 3 = his 2nd turn. Hand after global 1: Copycat, Alolan Muk, Weezing ex; '70-120s: Global 3 / owner 2': draws Poke Ball "
        "-> 4 cards. Board: Mega Sableye 170 Active, Koffing 60 slot 1, Darkrai 140 slot 2, no Energy. Opponent '54-69s: Global 2': "
        "hidden draw (3+1=4), Lightning to Drampa, Professor's Research (-1 +2) = 5 cards; Drampa 100, Dratini 60. His move in the "
        "review's order: Poke Ball (reveals Alolan Grimer), Weezing ex onto Koffing 83-85s, Boiler Smog 86-91s (Drampa Poisoned and "
        "Burned), Copycat 95-100s (hand Alolan Muk + Alolan Grimer shuffled away; opponent's hand 5 -> draws 5: Goo-zooka, Professor's "
        "Research, Cyrus, Starting Plains, Alolan Muk, which matches the hand used on global 5 and 7), Darkness to Active Mega Sableye "
        "108-110s, no attack, ends turn."),
]
