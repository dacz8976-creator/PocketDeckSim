from v2_helpers import P, B
D = 'v2deck_03c584b95c'; G = '20261017_150114000_SR'
HO = 'Hoopa ex B4 103'; NI = 'Nihilego A3a 042'; DN = 'Deceptive Needle B4 148'; PR = "Professor's Research P-A 007"
CY = 'Cyrus A2 150'; GA = 'Glimmora B3a 045'; CL = 'Claydol A3a 031'
CM = 'Charmander A2b 008'; CE = 'Charmeleon B1a 012'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
POS = [
P(G, 2, 1, [0, 0],
  dict(hand=[PR, HO, CY, GA, DN], disc=[], dene='', board=[B(HO, 150)], ko=0),
  dict(hand_count=6, disc=['Poké Ball A2b 111', "Professor's Research A4b 373", 'Poké Ball A2b 111'], dene='',
       board=[B(CM, 60)], ko=0),
  ["Play:Professor's Research", 'Play:Deceptive Needle', 'Tool:Deceptive Needle@0', 'Place:Nihilego@1', 'Attach:1Darkness@0 zone',
   'Attack:Shadow Bullet'],
  D, None,
  approx=AP + "; the opponent's hand count (6) assumes each of the opponent's two Poké Balls on global turn 1 put a Basic into the hand "
            "(the review says only that the results were hidden); the opponent's Trainer printings (Poké Ball, Professor's Research) are "
            "not shown, the first printing cards.py lists is used (convention 3)",
  ambiguous=['Opponent Charmander printing chosen by HP (60) and attack title (Combustion); A2b 008 and A2b 099 match',
             "Opponent's Poké Ball printing not shown; A2b 111 and P-A 005 match",
             "Opponent's Professor's Research printing not shown; A4b 373 and P-A 007 match"],
  draws={0: [NI, DN]},
  notes="Global 2 = his 1st turn (he went second). Setup row 27-35: opening five Professor's Research, two Hoopa ex, Cyrus, Glimmora; "
        "one Hoopa ex Active, none benched, so 4 in hand. Row 64-70: natural draw Deceptive Needle -> hand of 5. Opponent: row 27-35 lone "
        "Charmander 60 (Combustion 20), no Bench; row 36-63: opening 5 - Active = 4, draw 5, Poke Ball (-1 +1), Professor's Research "
        "(-1 +2), Poke Ball (-1 +1) = 6; no Energy attached. His move, rows 64-93 in time order: Professor's Research ~68s (draws "
        "Nihilego and the 2nd Deceptive Needle, order of the two not established, UNCERTAINTIES 'Research owner draw order'), Needle to "
        "Active Hoopa ~75s, Nihilego benched ~78s, Darkness from the zone to Active Hoopa ~81-83s, Shadow Bullet ~87.5s (no opponent "
        "Bench, so no bench target). Nihilego went to the visual right Bench spot; the engine's lowest empty slot (@1) is used, since "
        "the position format compacts the Bench (a None entry crashes pg_legal, a 'slot' key is ignored: scratch/b0/t_slots.py)."),
P(G, 4, 2, [0, 0],
  dict(hand=[HO, CY, GA, DN, CL], disc=[PR], dene='', board=[B(HO, 150, 'D', tool=DN), B(NI, 70)], ko=0),
  dict(hand_count=1, disc=['Poké Ball A2b 111', "Professor's Research A4b 373", 'Poké Ball A2b 111', 'Copycat B1 225', 'Potion P-A 001'],
       dene='', board=[B(CE, 60, 'RR', behind=[CM]), B(CM, 60)], ko=0),
  ['Place:Hoopa ex@2', 'Attach:1Darkness@0 zone', 'Attack:Shadow Bullet'],
  D, None,
  approx=AP + "; the opponent's Trainer printings (Poké Ball, Professor's Research, Copycat, Potion) are not shown, the first "
            "printing cards.py lists is used (convention 3); the Benched Charmander's attack was not shown: it is given the "
            "Combustion printing of the first Charmander (by HP alone the first-listed would be A1 033, Ember); Bench slots are compacted (the review has Nihilego benched at the right and the "
            "2nd Hoopa at the left; the position format holds no empty slot, so Nihilego is slot 1 and the 2nd Hoopa goes to slot 2)",
  ambiguous=['Opponent Charmeleon printing chosen by HP (80), Ability title (Ignition) and attack title (Steady Firebreathing); '
             'B1a 012 and P-B 020 match',
             'Opponent Charmander under Charmeleon: printing chosen by HP (60) and attack title (Combustion); A2b 008 and A2b 099 match',
             'Opponent Benched Charmander: its attack was not shown; it is given the printing of the Charmander under Charmeleon '
             '(A2b 008, Combustion); the 60-HP Charmander printings have Ember, Combustion or Bite',
             "Opponent's Poké Ball printing not shown; A2b 111 and P-A 005 match",
             "Opponent's Professor's Research printing not shown; A4b 373 and P-A 007 match",
             "Opponent's Copycat printing not shown; B1 225 and B1 270 match"],
  notes="Global 4 = his 2nd turn. His hand: after global 2 he holds the 2nd Hoopa ex, Cyrus, Glimmora, the 2nd Needle (row 71-84 "
        "'Owner holds ...'); row 135-147 natural draw Claydol -> 5 cards. Board after global 2: Active Hoopa 150 with one Darkness and "
        "Needle, Nihilego 70 on the Bench (row 85-93). Discard: Professor's Research. Opponent, rows 94-134: Charmander 60-30 (Shadow "
        "Bullet) -10 (Needle) = 20; evolved to Charmeleon 80 max with 40 damage = 40; Potion +20 = 60; two Fire (regular attachment + "
        "Ignition); second Charmander 60 benched. Opponent hand: 6 after global 1, draw 7, Copycat (-1, shuffle, draw 4 = his 4-card "
        "hand) = 4, Charmeleon, Charmander, Potion played = 1. His move, rows 135-159 in time order: bench 2nd Hoopa ex ~140-142s (at "
        "left; compacted Bench, so slot 2 after Nihilego in slot 1), Darkness from the zone to Active Hoopa ~146s, Shadow Bullet ~152s "
        "(30 to Charmeleon, 20 to the only Benched Charmander; no target label: the engine asked none with one Benched target)."),
]
