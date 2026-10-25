from v2_helpers import P, B
D = 'v2deck_4fa967805c'; G = '20261021_204724000_SR'
CV = 'Carvanha B4 034'; MS = 'Mega Sharpedo ex B4 035'; WM = 'Wailmer B4 036'; WL = 'Wailord B1 057'; BT = 'Baltoy A3a 030'
CL = 'Claydol A3a 031'; PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"; CY = 'Cyrus A2 150'; HH = 'Heavy Helmet B1 219'
CC = 'Copycat B1 225'; EC = 'Elegant Cape B3b 065'
# opponent (printings by convention 3: the first cards.py lists among those matching what the review shows)
TO = 'Torchic B1 033'; MB = 'Mega Blaziken ex B1 036'; CS = 'Castform Sunny Form B3 024'
oPB = 'Poké Ball A2b 111'; oPR = "Professor's Research A4b 373"; oRC = 'Rare Candy A3 144'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
TR = ("the opponent's Trainer printings are not shown; the first-listed printings are used (Poké Ball A2b 111, Professor's Research "
      "A4b 373, Rare Candy A3 144)")
AM_TO = 'Opponent Torchic printing chosen by name and HP (60) only (no attack shown); B1 033, B3 206 and P-B 007 match'
AM_MB = 'Opponent Mega Blaziken ex printing chosen by HP (210) and attack title (Mega Burning); B1 036, B1 254, B1 284 and B3 226 match'
AM_CS = 'Opponent Castform Sunny Form printing chosen by HP (70) and attack title (Sunny Scorching); B3 024 and P-B 057 match'
AM_TR = "Opponent's discarded Trainers: printings not shown; Poké Ball A2b 111, Professor's Research A4b 373, Rare Candy A3 144 listed"
# global 2: Rare Candy is not played until global 3, so the t2 texts name only the Trainers in the discard then (verifier, Oct 25)
TR2 = ("the opponent's Trainer printings are not shown; the first-listed printings are used (Poké Ball A2b 111, Professor's Research "
       "A4b 373)")
AM_TR2 = "Opponent's discarded Trainers: printings not shown; Poké Ball A2b 111 and Professor's Research A4b 373 listed"
POS = [
P(G, 2, 1, [0, 0],
  dict(hand=[EC, MS, CL, WM], disc=[], dene='', board=[B(CV, 50), B(BT, 60)], ko=0),
  dict(hand_count=4, disc=[oPB, oPR], dene='', board=[B(TO, 60), B(TO, 60), B(CS, 70)], ko=0),
  ['Place:Wailmer@2', 'Attach:1Water@0 zone', 'Attack:Sharp Fang'],
  D, None,
  approx=AP + "; the opponent's hand count (4) counts the global-1 Poké Ball as finding the Torchic it benched; " + TR2,
  ambiguous=[AM_TO, AM_CS, AM_TR2],
  notes="Global 2 = his 1st turn (he went second). Review 0-38: opening five Carvanha, Elegant Cape, Mega Sharpedo ex, Baltoy, Claydol; "
        "Carvanha Active (50), Baltoy Bench (60) -> hand Cape, Sharpedo, Claydol. 70-87: draws Wailmer -> 4 cards. Opponent 39-69: "
        "Torchic Active; 5-1 = 4, draw 5, Poke Ball (-1 +1 Torchic) 5, bench Torchic 4, Professor's Research (-1 +2) 5, bench Castform "
        "Sunny Form 4. Bench order: Torchic (54-56) then Castform (68). No Energy, no attack. His move 70-87 in order: bench Wailmer "
        "(after the draw at 72), Water to Active Carvanha 80-81, Sharp Fang 85-87 (Torchic 60 to 10)."),
P(G, 4, 2, [0, 0],
  dict(hand=[EC, MS, CL, PR], disc=[], dene='', board=[B(CV, 50, 'W'), B(BT, 60), B(WM, 100)], ko=0),
  dict(hand_count=4, disc=[oPB, oPR, oPR, oRC], dene='', board=[B(TO, 10), B(MB, 210, 'R', behind=[TO]), B(CS, 70)], ko=0),
  ["Play:Professor's Research", 'Play:Poké Ball', 'Place:Carvanha@3', 'Evolve:Claydol@1', 'Evolve:Mega Sharpedo ex@0',
   'Play:Elegant Cape', 'Tool:Elegant Cape@0', 'Attach:1Water@2 zone', 'Attack:Turbo Shark', 'Attach:1Water@2 fx'],
  D, None,
  approx=AP + "; " + TR + "; the Mega Blaziken ex was put on the Benched Torchic by Rare Candy, so only a Torchic is under it",
  ambiguous=[AM_TO, AM_MB, AM_CS, AM_TR],
  draws={0: [PB, MS], 1: [CV]},
  notes="Global 4 = his 2nd turn. His hand after global 2: Cape, Mega Sharpedo ex, Claydol; 119-192 draws Professor's Research -> 4. "
        "Board: Active Carvanha 50 with one Water, Bench Baltoy 60, Wailmer 100 (benched global 2 -> slot 2). Opponent 88-118: hidden "
        "draw (4->5), Professor's Research (-1 +2 = 6), Rare Candy + Mega Blaziken ex onto the Benched Torchic (-2 = 4), Fire attached "
        "to the Benched Mega Blaziken ex; Active Torchic 10 HP; Castform 70. His move 119-192 in time order: Professor's Research "
        "123-126 (Poke Ball and the 2nd Mega Sharpedo ex), Poke Ball 130-134 (Carvanha), bench Carvanha 137-140 (slot 3), Baltoy -> "
        "Claydol 142-144, Active Carvanha -> Mega Sharpedo ex and Elegant Cape 156-160, manual Water to Wailmer 160.5, Turbo Shark "
        "164-169 (KO Torchic; the zone Water goes to Wailmer, native 168.8)."),
P(G, 6, 3, [1, 0],
  dict(hand=[MS, PR], disc=[PR, PB], dene='', board=[B(MS, 190, 'W', tool=EC, behind=[CV]), B(CL, 100, behind=[BT]), B(WM, 100, 'WW'),
                                                     B(CV, 50)], ko=0),
  dict(hand_count=5, disc=[oPB, oPR, oPR, oRC, TO], dene='', board=[B(CS, 70, 'R'), B(MB, 210, 'R', behind=[TO])], ko=1),
  ["Play:Professor's Research", 'Evolve:Wailord@2', 'Evolve:Mega Sharpedo ex@3', 'Attach:1Water@2 zone', 'Attack:Turbo Shark', 'Attach:1Water@2 fx'],
  D, None,
  approx=AP + "; " + TR,
  ambiguous=[AM_TO, AM_MB, AM_CS, AM_TR],
  draws={0: [WL, CC]},
  notes="Global 6 = his 3rd turn. His hand after global 4: the 2nd Mega Sharpedo ex only (Cape, Sharpedo, Claydol, Research + Poke "
        "Ball, Sharpedo; - Research, Poke Ball, Carvanha placed, Claydol, Sharpedo, Cape); 209-254 draws the 2nd Professor's Research "
        "-> 2 cards. Discard: Research, Poke Ball. Board: Active Mega Sharpedo ex 220 (Cape) with one Water, 30 from Sunny Scorching "
        "(193-208) -> 190; Bench Claydol 100, Wailmer 100 with two Water (manual + Turbo Shark), Carvanha 50. Opponent: Torchic KO'd "
        "global 4 (score 1-0), Castform promoted (191); 193-208 hidden draw (4->5), Fire to Castform, Sunny Scorching 30, no burn (no "
        "Stadium). Mega Blaziken ex 210 one Fire. His move 209-254: Research 211-215 (Wailord, Copycat), Wailmer -> Wailord 219-221, "
        "Benched Carvanha -> 2nd Mega Sharpedo ex 222-226, manual Water to Wailord 234.5 (three Water), Turbo Shark 238-243 (KO "
        "Castform; the zone Water to Wailord, native 242.5)."),
P(G, 8, 4, [2, 0],
  dict(hand=[CC, WL], disc=[PR, PB, PR], dene='', board=[B(MS, 50, 'W', tool=EC, cond=['Burned'], behind=[CV]), B(CL, 100, behind=[BT]),
                                                        B(WL, 200, 'WWWW', behind=[WM]), B(MS, 190, behind=[CV])], ko=0),
  dict(hand_count=6, disc=[oPB, oPR, oPR, oRC, TO, CS], dene='RR', board=[B(MB, 210, 'R', behind=[TO])], ko=2),
  ['Retreat:2', 'Play:Copycat', 'Play:Poké Ball', 'Play:Heavy Helmet', 'Tool:Heavy Helmet@0', 'Play:Elegant Cape', 'Tool:Elegant Cape@3',
   'Attach:1Water@0 zone', 'Attack:Whale Pump'],
  D, None,
  approx=AP + "; " + TR + "; the opponent's discarded Energy counts Castform's Fire and the Fire Mega Burning discarded",
  ambiguous=[AM_TO, AM_MB, AM_CS, AM_TR],
  draws={1: ['-' + WL, WM, PB, EC, CY, WL, HH], 2: []},
  notes="Global 8 = his 4th turn. His hand after global 6: Copycat (Sharpedo, Research + Wailord, Copycat; - Research, Wailord, "
        "Sharpedo); 278-322 draws the 2nd Wailord (280) -> 2 cards. Discard: Research, Poke Ball, Research. Board after global 6: "
        "Active Mega Sharpedo ex 190 (Cape, one Water), Bench Claydol 100, Wailord 200 four Water (slot 2), 2nd Mega Sharpedo ex 190 no "
        "Energy (slot 3). Opponent 251-277: Castform KO'd (2-0), Mega Blaziken ex promoted (sole Pokemon); hidden draw (5->6), 2nd Fire, "
        "Mega Burning 120 (Sharpedo 190->70), one Fire discarded, Burned; checkup 20 -> 50, tails, still Burned. His move 278-322: "
        "retreat the burned Sharpedo (retreat cost 0, its Water stays) for Wailord 284 (Bench slot 2 comes in), Copycat 289-299 "
        "(opponent hand 6: Wailmer, Poke Ball, Elegant Cape, Cyrus, Wailord, Heavy Helmet; his 1-card hand, Wailord, shuffled in), "
        "Poke Ball 302-304 finds nothing, Heavy Helmet to Wailord 305-309, Elegant Cape to the 2nd Sharpedo 310-315 (slot 3: the "
        "retreated Sharpedo took slot 2), manual 5th Water to Wailord 316, Whale Pump 319-322."),
]
