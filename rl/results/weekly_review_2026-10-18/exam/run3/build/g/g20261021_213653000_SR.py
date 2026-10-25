from v2_helpers import P, B
D = 'v2deck_4fa967805c'; G = '20261021_213653000_SR'
CV = 'Carvanha B4 034'; MS = 'Mega Sharpedo ex B4 035'; WM = 'Wailmer B4 036'; WL = 'Wailord B1 057'; BT = 'Baltoy A3a 030'
CL = 'Claydol A3a 031'; PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"; CY = 'Cyrus A2 150'; HH = 'Heavy Helmet B1 219'
CC = 'Copycat B1 225'; EC = 'Elegant Cape B3b 065'; WA = 'Wallace B3b 068'
# opponent (printings by convention 3: the first cards.py lists among those matching what the review shows)
RA = "Team Rocket's Rattata B4a 058"; RX = "Team Rocket's Raticate ex B4a 059"; VU = 'Alolan Vulpix A3 040'; NX = 'Alolan Ninetales ex B2 029'
oPR = "Professor's Research A4b 373"
TA = {"card": "Training Area B2 153", "owner": 1}
AP = "opponent's list unknown; opponent's hand size from the visible plays"
TR = "the opponent's Professor's Research printing is not shown; the first-listed printing (A4b 373) is used"
AM_RA = "Opponent Team Rocket's Rattata printing: B4a 058 is the only one listed (HP 40, Ambush)"
AM_VU = 'Opponent Alolan Vulpix printing chosen by name and HP (60) only (no attack shown); A3 040, A3 162, B2 028, B4 204 and P-B 032 match'
AM_NX = ('Opponent Alolan Ninetales ex printing chosen by HP (150) and attack title (Binding Snow); B2 029, B2 182, B2 196 and B4 225 '
         'match')
AM_RX = ("Opponent Team Rocket's Raticate ex printing chosen by HP (120) and Ability title (Thieving Incisors); B4a 059, B4a 084 and "
         "B4a 093 match")
AM_TR = "Opponent's discarded Professor's Research: printing not shown; A4b 373 listed"
NOZ = "NoEnergyFromZoneToActive"


def binding(p, tc):
    p['turn_effects'] = [{"turn": tc, "effect": NOZ}]
    return p


POS = [
P(G, 1, 1, [0, 0],
  dict(hand=[CC, PB, MS, HH, WM], disc=[], dene='', board=[B(WM, 100)], ko=0),
  dict(hand_count=4, disc=[], dene='', board=[B(RA, 40)], ko=0),
  ['Place:Wailmer@1', 'Play:Poké Ball', 'Place:Carvanha@2', 'Play:Heavy Helmet', 'Tool:Heavy Helmet@1', 'Play:Copycat',
   'Play:Elegant Cape', 'Tool:Elegant Cape@0', 'Play:Elegant Cape', 'Tool:Elegant Cape@2', 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's hand count (4) is the opening five less the Active Rattata (no Bench at setup, no draw yet)",
  ambiguous=[AM_RA],
  draws={1: [CV], 5: ['-' + MS, MS, EC, EC, CV]},
  notes="Global 1 = his 1st turn (he went first). Review 'Opening and setup, 0-41s': opening five Wailmer, Copycat, Poke Ball, Mega "
        "Sharpedo ex, Heavy Helmet; Wailmer Active, no Bench -> 4 in hand; opponent Team Rocket's Rattata 40 Active. Row '1 / owner1' "
        "42-93: draws Wailmer -> 5. His move in the review's time order: bench Wailmer (slot 1), Poke Ball 59-62 (Carvanha), bench "
        "Carvanha 64-66 (slot 2), Heavy Helmet 69-72 on the Benched Wailmer, Copycat 74-78 (his remaining hand, Mega Sharpedo ex, "
        "shuffled in; draws 4 = opponent's 4: Mega Sharpedo ex, two Elegant Cape, Carvanha), Capes 82-92 on Active Wailmer and on "
        "Carvanha (the review lists Active first; the order of the two is not given), no Energy (first turn), no attack."),
P(G, 3, 2, [0, 0],
  dict(hand=[MS, CV, CL], disc=[PB, CC], dene='', board=[B(WM, 60, tool=EC), B(WM, 100, tool=HH), B(CV, 50, tool=EC)], ko=0),
  dict(hand_count=5, disc=[oPR], dene='', board=[B(RA, 40, 'W'), B(VU, 60)], ko=0),
  ['Evolve:Mega Sharpedo ex@2', 'Attach:1Water@2 zone', 'EndTurn'],
  D, None,
  approx=AP + "; " + TR,
  ambiguous=[AM_RA, AM_VU, AM_TR],
  notes="Global 3 = his 2nd turn. His hand after global 1: Mega Sharpedo ex, Carvanha (Copycat's four less the two Capes); row "
        "'3 / owner2' 124-141 draws Claydol (126s) -> 3. Discard Poke Ball, Copycat. Board: Active Wailmer 100-40 = 60 with Cape, "
        "Bench Wailmer 100 Helmet (slot 1), Carvanha 50 Cape (slot 2). Opponent row '2 / opponent1' 94-123: draw (4->5), Water to "
        "Rattata, Professor's Research (6), Alolan Vulpix benched (5), Ambush heads 40. His move: Carvanha -> Mega Sharpedo ex "
        "128-132 (220 with Cape), first Water to it 135-140, no attack."),
P(G, 5, 3, [0, 0],
  dict(hand=[CV, CL, PR], disc=[PB, CC], dene='',
       board=[B(WM, 40, tool=EC), B(WM, 100, tool=HH), B(MS, 220, 'W', tool=EC, behind=[CV])], ko=0),
  dict(hand_count=5, disc=[oPR], dene='', board=[B(RA, 40, 'W'), B(NX, 150, 'W', behind=[VU])], ko=0),
  ["Play:Professor's Research", 'Play:Poké Ball', 'Place:Baltoy@3', 'Evolve:Wailord@0', 'Attach:1Water@1 zone', 'EndTurn'],
  D, None,
  approx=AP + "; " + TR,
  ambiguous=[AM_RA, AM_VU, AM_NX, AM_TR],
  draws={0: [PB, WL], 1: [BT]},
  notes="Global 5 = his 3rd turn. His hand after global 3: Carvanha, Claydol; row '5 / owner3' 174-201 draws Professor's Research "
        "(176s) -> 3. Board: Active Wailmer 60-20 = 40 Cape; Bench Wailmer 100 Helmet, Mega Sharpedo ex 220 Cape one Water. Opponent "
        "row '4 / opponent2' 142-173: draw (5->6), Vulpix -> Alolan Ninetales ex 150 (5), Water to it, Ambush tails 20. His move in "
        "the review's time order: Research 179-183 (Poke Ball, Wailord), Poke Ball 185-188 (Baltoy), bench Baltoy 190-193 (slot 3), "
        "Active Wailmer -> Wailord 196-198 (230-60 = 170), Water 199-201 to the Benched Wailmer (slot 1); no attack."),
binding(P(G, 7, 4, [0, 0],
  dict(hand=[CV, CL, MS], disc=[PB, CC, PR, PB], dene='',
       board=[B(WL, 80, tool=EC, behind=[WM]), B(WM, 100, 'W', tool=HH), B(MS, 220, 'W', tool=EC, behind=[CV]), B(BT, 60)], ko=0),
  dict(hand_count=4, disc=[oPR], dene='W', board=[B(NX, 150, 'WW', behind=[VU]), B(RA, 40), B(RA, 40)], ko=0),
  ['Evolve:Claydol@3', 'Attach:1Water@1 zone', 'EndTurn'],
  D, None, stadium=TA,
  approx=AP + "; " + TR + "; the Training Area printing is the first listed (B2 153)",
  ambiguous=[AM_RA, AM_VU, AM_NX, AM_TR],
  notes="Global 7 = his 4th turn. His hand after global 5: Carvanha, Claydol (Research, Poke Ball played; Baltoy placed; Wailord "
        "evolved); row '7 / owner4' 246-261 draws the 2nd Mega Sharpedo ex -> 3. Discard Poke Ball, Copycat, Research, Poke Ball. "
        "Board: Wailord 170-90 = 80 Cape; Wailmer 100 Helmet one Water; Sharpedo 220 one Water; Baltoy 60. Opponent row '6 / "
        "opponent3' 202-245: draw (5->6), 2nd Rattata benched (5), 2nd Water to Ninetales, Rattata retreats (its Water discarded), "
        "Ninetales promoted, Training Area (4), Binding Snow 80+10 = 90 with its next-turn restriction (turn effect "
        "NoEnergyFromZoneToActive, native 242s). The two Benched Rattata (40, no Energy) are identical. His move: Baltoy -> Claydol "
        "251-254, 2nd Water to the Benched Wailmer 255-258; no attack."), 7),
binding(P(G, 9, 5, [0, 1],
  dict(hand=[CV, MS, WA], disc=[PB, CC, PR, PB, WL, WM, EC], dene='',
       board=[B(MS, 220, 'W', tool=EC, behind=[CV]), B(WM, 100, 'WW', tool=HH), B(CL, 100, behind=[BT])], ko=1),
  dict(hand_count=5, disc=[oPR], dene='W', board=[B(NX, 150, 'WW', behind=[VU]), B(RA, 40, 'W'), B(RA, 40)], ko=0),
  ['Place:Carvanha@3', 'Play:Wallace', 'ChooseRandomEvolutionTarget', 'Attach:1Water@3 zone', 'Attack:Turbo Shark', 'Attach:1Water@1 fx'],
  D, None, stadium=TA, draws={1: []},
  approx=AP + "; " + TR + "; the Training Area printing is the first listed (B2 153); which Benched Rattata holds the Water is not "
            "given (listed first); his Bench is compacted (Wailmer, Claydol) after the Benched Mega Sharpedo ex was promoted",
  ambiguous=[AM_RA, AM_VU, AM_NX, AM_TR],
  notes="Global 9 = his 5th turn. His hand after global 7: Carvanha, Mega Sharpedo ex; row '9 / owner5' 290-320 draws Wallace "
        "(292s) -> 3. Row '8 / opponent4' 262-289: draw (4->5), Water to the Benched Rattata that later evolves, Binding Snow 90 KOs "
        "Wailord 80 (opponent +1, score 0-1); its Cape, Wailmer and Wailord go to his discard; he promotes the Cape Sharpedo 220 "
        "with one Water. Binding Snow's restriction applies to this turn. His Bench compacted: Wailmer two Water Helmet (slot 1), "
        "Claydol (slot 2). His move in the review's time order: bench the 2nd Carvanha 294-296 (slot 3), Wallace 298-302 targets "
        "Carvanha with no eligible card left in the deck (no evolution), Water 303-311 to Carvanha, Turbo Shark 314-317 (70+10 = 80, "
        "Ninetales 150->70), its zone Water to the Benched Wailmer (2->3 by 320s)."), 9),
binding(P(G, 11, 6, [0, 1],
  dict(hand=[MS, CY], disc=[PB, CC, PR, PB, WL, WM, EC, WA], dene='',
       board=[B(MS, 130, tool=EC, behind=[CV]), B(WM, 100, 'WWW', tool=HH), B(CL, 100, behind=[BT]), B(CV, 50, 'W')], ko=1),
  dict(hand_count=5, disc=[oPR], dene='W', board=[B(NX, 70, 'WW', behind=[VU]), B(RX, 120, 'WW', behind=[RA]), B(RA, 40, 'W')], ko=0),
  ['Evolve:Mega Sharpedo ex@3', 'Attach:1Water@3 zone', 'Retreat:3', 'Attack:Turbo Shark'],
  D, None, stadium=TA,
  approx=AP + "; " + TR + "; the Training Area printing is the first listed (B2 153); the Raticate ex's Energy (two Water: the "
            "Rattata's Water from global 8 and the Water moved by Thieving Incisors) and the order of the opponent's Bench are read "
            "from the review's account of global 10",
  ambiguous=[AM_RA, AM_VU, AM_NX, AM_RX, AM_TR],
  notes="Global 11 = his 6th turn. His hand after global 9: Mega Sharpedo ex (Carvanha placed, Wallace played); row '11 / owner6' "
        "356-383 draws Cyrus (357s) -> 2. Discard gains Wallace. Board: Sharpedo 220-90 = 130 with no Energy (Thieving Incisors moved "
        "its one Water); Wailmer three Water Helmet; Claydol 100; Carvanha 50 one Water. Opponent row '10 / opponent5' 321-355: draw "
        "(5->6), the Water Rattata -> Team Rocket's Raticate ex 120 (5), Thieving Incisors moves the Water, Water on the other Rattata, "
        "Binding Snow 90 renews the restriction. Ninetales 70 two Water. His move 356-383: Carvanha -> 2nd Mega Sharpedo ex 359-363 "
        "(slot 3, keeps the Water), Water 368-369 to it, free retreat 370-374 (slot 3 comes in), Turbo Shark 377-380 (Ninetales "
        "70->0); the opponent conceded at 381-382 before the KO and the attack's Energy effect resolved, so the line ends at the "
        "attack."), 11),
]
