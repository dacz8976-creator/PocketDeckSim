from v2_helpers import P, B
D = 'v2deck_4fa967805c'; G = '20261021_032324000_SR'
BT = 'Baltoy A3a 030'; WM = 'Wailmer B4 036'; CV = 'Carvanha B4 034'; PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"
EC = 'Elegant Cape B3b 065'; WA = 'Wallace B3b 068'; HH = 'Heavy Helmet B1 219'; CC = 'Copycat B1 225'
OR = 'Oricorio A3 066'; MM = 'Magnemite A1 097'; MT = 'Magneton A1 098'; ZE = 'Zeraora A3a 021'
OPB = 'Poké Ball A2b 111'; OPR = "Professor's Research A4b 373"
AP = "opponent's list unknown; opponent's hand size from the visible plays"
OTR = "the opponent's Trainer printings (Poké Ball, Professor's Research) are not shown; the printing cards.py lists first is used"
AMB_OR = ('Opponent Oricorio printing chosen by HP (70), Ability title (Safeguard) and attack title (Zzzap); A3 066, A3 165, A4b 146, '
          'A4b 147 and B1 303 match')
AMB_ZE = ('Opponent Zeraora printing chosen by HP (90), Ability title (Thunderclap Flash) and attack title (Lightning Claw); A3a 021, '
          'A4b 149, A4b 150, B1 304 and P-A 074 match')
POS = [
P(G, 2, 1, [0, 0],
  dict(hand=[EC, WA, PR, PB, HH], disc=[], dene='', board=[B(BT, 60)], ko=0),
  dict(hand_count=4, disc=[OPB, OPR], dene='', board=[B(OR, 70), B(MM, 60), B(ZE, 90, 'L')], ko=0),
  ['Play:Poké Ball', 'Place:Wailmer@1', 'Play:Heavy Helmet', 'Tool:Heavy Helmet@1', "Play:Professor's Research", 'Attach:1Water@0 zone',
   'Play:Elegant Cape', 'Tool:Elegant Cape@0', 'EndTurn'],
  D, None,
  approx=AP + "; " + OTR + "; the opponent's Poké Ball on global turn 1 is counted +1 card (its result is hidden); the Magnemite "
            "printing is chosen by HP (60) only (its attack was not shown)",
  ambiguous=[AMB_OR, 'Opponent Magnemite: its attack was not shown; printing chosen by HP (60) only', AMB_ZE],
  draws={0: [WM], 4: [EC, CC]},
  notes="Global 2 = his 1st turn (he went second). One review of the whole battle in both clips (CLIPS.json; the REVIEW.md files "
        "differ only in the 'Primary source' line). 'Clip07 31-51s setup': opening five Elegant Cape, Wallace, Baltoy, Professor's "
        "Research, Poke Ball; Baltoy 60 Active, no Bench -> 4. 'Global2': draw Heavy Helmet -> 5. Opponent: Oricorio 70 Active, "
        "Magnemite 60 Bench (5 - 2 = 3); 'Global1': draw (4), Poke Ball (hidden, 4 -> 5 counting +1), Professor's Research (6), "
        "Zeraora 90 benched (... = 4 at the end: 3 +1 draw, -1 +1 Poke Ball, -1 +2 Research, -1 Zeraora), Thunderclap Flash -> Zeraora "
        "one Lightning. His move in the review's order: Poke Ball (Wailmer), Wailmer benched (@1), Heavy Helmet on Wailmer, "
        "Professor's Research (Elegant Cape, Copycat; Copycat held), Water to Baltoy, Elegant Cape on Baltoy, end."),
P(G, 4, 2, [0, 0],
  dict(hand=[WA, EC, CC, PB], disc=[PB, PR], dene='', board=[B(BT, 60, 'W', tool=EC), B(WM, 100, tool=HH)], ko=0),
  dict(hand_count=4, disc=[OPB, OPR], dene='', board=[B(OR, 70, 'L'), B(MT, 80, 'L', behind=[MM]), B(ZE, 90, 'L')], ko=0),
  ['Play:Poké Ball', 'Place:Carvanha@2', 'Play:Wallace', 'ChooseRandomEvolutionTarget', 'Play:Elegant Cape', 'Tool:Elegant Cape@2',
   'Attach:1Water@0 zone', 'Attack:Spinning Attack'],
  D, None,
  approx=AP + "; " + OTR + "; the Magnemite under Magneton: printing chosen by HP (60) only",
  ambiguous=[AMB_OR, 'Opponent Magneton printing chosen by HP (80), Ability title (Volt Charge) and attack title (Spinning Attack); '
             'A1 098, A4 218, A4b 135 and A4b 136 match', 'Opponent Magnemite under Magneton: its attack was not shown; printing '
             'chosen by HP (60) only', AMB_ZE],
  draws={0: [CV], 2: []},
  notes="Global 4 = his 2nd turn. Hand after global 2: Wallace, Elegant Cape (the 2nd, from Research), Copycat. 'Global4': draw 2nd "
        "Poke Ball -> 4 ('Owner hand Copycat; deck8' after the turn's plays checks out). Board: Baltoy 60 with one Water and Cape; "
        "Wailmer 100 with Heavy Helmet. Opponent 'Global3': draw (5), Magnemite -> Magneton (4), Volt Charge Lightning to Magneton, "
        "Lightning to Oricorio; each of Oricorio, Zeraora, Magneton has one Lightning; no attack. His move in the review's order: "
        "Poke Ball (Carvanha 50), Carvanha benched (@2), Wallace on that Carvanha -> Mega Sharpedo ex 190, Elegant Cape on the Mega "
        "(220), 2nd Water to Baltoy, Spinning Attack (50 with Weakness into Oricorio; clip07 ends during the attack, clip08 0 s shows "
        "Oricorio 20). Wallace's only eligible target is the Carvanha (Wailmer has 100 HP, Baltoy is Fighting): the label is "
        "'ChooseRandomEvolutionTarget' without arguments (scratch/b3/t_wallace2.py). draws {2: []}; no vpatch (the Cape label is "
        "the same on Carvanha or Mega, and a Mega put on the board up front would block the variant's Place)."),
]
