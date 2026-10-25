from v2_helpers import P, B
D = 'v2deck_4fa967805c'; G = '20261022_000850000_SR'
BA = 'Baltoy A3a 030'; CD = 'Claydol A3a 031'; WD = 'Wailord B1 057'; CV = 'Carvanha B4 034'; MS = 'Mega Sharpedo ex B4 035'
WM = 'Wailmer B4 036'; PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"; CY = 'Cyrus A2 150'; HH = 'Heavy Helmet B1 219'
CC = 'Copycat B1 225'; EC = 'Elegant Cape B3b 065'; WA = 'Wallace B3b 068'
# opponent's cards (printing: the first cards.py lists among those matching the shown facts)
O_IG = 'Igglybuff A4a 059'; O_EV = 'Eevee B1 184'; O_ES = 'Espeon B3a 020'; O_SW = 'Swablu B1 196'; O_DK = 'Darkrai B2b 040'
O_MA = 'Mega Altaria ex B1 102'; O_SB = 'Small Balloon B3b 064'
O_PB = 'Poké Ball A2b 111'; O_CC = 'Copycat B1 225'; O_PR = "Professor's Research A4b 373"; O_SA = 'Sabrina A1 225'
TA = {"card": "Training Area B2 153", "owner": 1}
AP = "opponent's list unknown; opponent's hand size from the visible plays"
AP_TR = "the opponent's Trainer printings (Poke Ball, Copycat, Professor's Research, Sabrina) are not shown, the first listed printings are used"
AMB_SW = 'Opponent Swablu printing chosen by HP (50) and attack title (Sing); B1 196 and B3a 102 match'
AMB_EV = 'Opponent Eevee printing chosen by HP (50) and Ability title (Boosted Evolution); B1 184, P-B 011 and P-B 054 match'
AMB_DK = 'Opponent Darkrai printing chosen by HP (100) and Ability title (Bad Dreams); only B2b 040 matches'
AMB_SB = ("Opponent Tool on the first Igglybuff: its title was not read; its shown effect (Retreat Cost 1 less) is Small Balloon's; "
          "B3b 064 and B3b 106 match")

POS = [
P(G, 2, 1, [0, 0],
  dict(hand=[WD, WD, PB, CD, EC], disc=[], dene='', board=[B(CV, 40)], ko=0),
  dict(hand_count=2, disc=[O_PB, O_CC], dene='', zone='P',
       board=[B(O_IG, 30, tool=O_SB), B(O_IG, 30), B(O_EV, 50), B(O_SW, 50)], ko=0),
  ['Play:Poké Ball', 'Place:Wailmer@1', 'Attach:1Water@0 zone', 'Attack:Sharp Fang'],
  D, None, stadium=TA,
  approx=AP + "; the opponent's Poke Ball is counted as +1 card (its result was hidden); " + AP_TR + "; the opponent's Tool is "
            "named from its shown effect (title not read); the opponent's next Energy is Psychic from the review's 'Opponent Energy is "
            "Psychic' at setup",
  ambiguous=[AMB_SB, AMB_EV, AMB_SW],
  draws={0: [WM]},
  notes="Global 2 = his 1st turn (he went second). Setup: opening five Carvanha, two Wailord, Poke Ball, Claydol; Carvanha Active, no "
        "Bench -> 4 in hand; draw Elegant Cape (global 2 row) -> 5. Global 1 row: Sleepy Lullaby 10 -> Carvanha 40, Asleep; checkup heads, "
        "awake. Opponent hand: 5 - 1 = 4, draw 5, Poke Ball (-1 +1) 5, 2nd Igglybuff benched 4, Training Area 3, balloon Tool 2, Copycat "
        "(-1, draw 4 = his 4-card hand) 4, Eevee and Swablu benched = 2. Bench order as benched: Igglybuff, Eevee, Swablu. Swablu's Sing "
        "and Eevee's Boosted Evolution come from the review's setup paragraph ('subsequently reveals'). His move in the review's order: "
        "Poke Ball (Wailmer, public), Wailmer benched, Water to Carvanha, Sharp Fang KOs the Active Igglybuff."),
P(G, 4, 2, [1, 0],
  dict(hand=[WD, WD, CD, EC, PR], disc=[PB], dene='', board=[B(CV, 10, 'W'), B(WM, 100)], ko=0),
  dict(hand_count=3, disc=[O_PB, O_CC, O_IG, O_SB, O_PB, O_PR], dene='', zone='P',
       board=[B(O_IG, 30), B(O_DK, 100), B(O_EV, 50, 'P'), B(O_SW, 50)], ko=1),
  ["Play:Professor's Research", 'Place:Wailmer@2', 'Place:Carvanha@3', 'Evolve:Wailord@1', 'Attach:1Water@2 zone', 'Play:Elegant Cape',
   'Tool:Elegant Cape@1', 'Attack:Sharp Fang'],
  D, None, stadium=TA,
  approx=AP + "; the opponent's Poke Balls are each counted as +1 card (results hidden); " + AP_TR + "; the opponent's Tool (in the "
            "discard) is named from its shown effect (title not read); the opponent's next Energy is Psychic from the review's setup",
  ambiguous=[AMB_SB, AMB_EV, AMB_SW, AMB_DK],
  draws={0: [CV, WM]},
  notes="Global 4 = his 2nd turn. Hand after global 2: two Wailord, Claydol, Elegant Cape; draw Professor's Research (186-188) -> 5. Board: "
        "Carvanha 40 - 10 (Lullaby) - 20 (Bad Dreams) = 10 with one Water, awake (checkup heads 183-184); Wailmer 100 Benched. Opponent "
        "global 3: 2 + draw 3, Psychic to Benched Eevee, Poke Ball (-1 +1) 3, Research (-1 +2) 4, Darkrai benched = 3. The 2nd Igglybuff "
        "was promoted after the KO; Darkrai took the vacated Bench spot (the first), so the Bench is Darkrai, Eevee, Swablu. His move in "
        "the review's order: Research (Carvanha, Wailmer), 2nd Wailmer and 2nd Carvanha benched (lowest empty slots @2 and @3; the game "
        "showed the 2nd Wailmer in the middle and the 2nd Carvanha at the left, the 1st Wailmer at the right), the older Wailmer (@1) to "
        "Wailord, Water to the newer Wailmer (@2), Cape to Wailord, Sharp Fang KOs Igglybuff."),
P(G, 6, 3, [2, 0],
  dict(hand=[WD, CD, PR], disc=[PB, PR], dene='',
       board=[B(WD, 140, tool=EC, cond=['Asleep'], behind=[WM]), B(CV, 50), B(WM, 100, 'W'), B(CV, 10, 'W')], ko=0),
  dict(hand_count=1, disc=[O_PB, O_CC, O_IG, O_SB, O_PB, O_PR, O_IG, O_SA], dene='P', zone='P',
       board=[B(O_ES, 90, 'P', behind=[O_EV]), B(O_DK, 100), B(O_DK, 100), B(O_SW, 50)], ko=2),
  ["Play:Professor's Research", 'Evolve:Wailord@2', 'Attach:1Water@2 zone', 'EndTurn'],
  D, None, stadium=TA,
  approx=AP + "; the opponent's Poke Balls are each counted as +1 card (results hidden); " + AP_TR + "; the opponent's Tool (in the "
            "discard) is named from its shown effect (title not read); the opponent's next Energy is Psychic from the review's setup; "
            "the opponent's Bench is listed in the order benched (Darkrai, 2nd Darkrai, then Swablu, moved to the Bench by its retreat)",
  ambiguous=[AMB_SB, AMB_EV, AMB_SW, AMB_DK,
             'Opponent Espeon printing chosen by HP (90) and attack title (Hypnoblast); only B3a 020 matches'],
  draws={0: [CC, WA]},
  notes="Global 6 = his 3rd turn. Hand after global 4: Wailord, Claydol; draw Professor's Research (289) -> 3. Global 5: Sabrina, he chose "
        "the Cape Wailord 230 (no Energy) Active; Hypnoblast 40 + Training Area 10 -> 180, Asleep; two Bad Dreams -> 140; tails, still "
        "Asleep. His Bench left to right as the review shows it: fresh Carvanha 50 (left), Wailmer with one Water (middle), the 10-HP "
        "Carvanha with one Water (right, Wailord's old spot). Discard: Poke Ball, Research. Opponent global 5: 3 + draw 4, Sabrina 3, 2nd "
        "Darkrai benched 2, Eevee -> Espeon 1, Psychic to Swablu, Swablu retreats (Psychic discarded), Espeon (one Psychic from global 3) "
        "Active = 1 in hand. His move in the review's order: Research (Copycat, Wallace), middle Wailmer -> Wailord, Water to it, pass."),
P(G, 8, 4, [2, 0],
  dict(hand=[CD, CC, WA, MS], disc=[PB, PR, PR], dene='',
       board=[B(WD, 10, tool=EC, cond=['Asleep'], behind=[WM]), B(CV, 50), B(WD, 200, 'WW', behind=[WM]), B(CV, 10, 'W')], ko=0),
  dict(hand_count=1, disc=[O_PB, O_CC, O_IG, O_SB, O_PB, O_PR, O_IG, O_SA], dene='P', zone='P',
       board=[B(O_ES, 90, 'P', behind=[O_EV]), B(O_DK, 100), B(O_DK, 100), B(O_MA, 190, 'P', behind=[O_SW])], ko=2),
  ['Play:Wallace', 'ChooseRandomEvolutionTarget{in_play_idx:1,energy_type:Water}', 'Evolve:Mega Sharpedo ex@3', 'Attach:1Water@2 zone',
   'EndTurn'],
  D, None, stadium=TA,
  approx=AP + "; the opponent's Poke Balls are each counted as +1 card (results hidden); " + AP_TR + "; the opponent's Tool (in the "
            "discard) is named from its shown effect (title not read); the opponent's next Energy is Psychic from the review's setup; "
            "the opponent's Bench is listed in the order benched",
  ambiguous=[AMB_SB, AMB_EV, AMB_SW, AMB_DK,
             'Opponent Espeon printing chosen by HP (90) and attack title (Hypnoblast); only B3a 020 matches',
             'Opponent Mega Altaria ex printing chosen by name and HP (190); B1 102, B1 259, B1 286 and B3a 107 match'],
  draws={0: []},
  vpatch=lambda v: v['me']['board'].__setitem__(1, B(MS, 190, behind=[CV])),
  notes="Global 8 = his 4th turn. Hand after global 6: Claydol, Copycat, Wallace; draw Mega Sharpedo ex (364) -> 4. Active Cape Wailord: "
        "140 - 40 (Bad Dreams at his global-6 checkup) = 100, heads (awake); global 7 Hypnoblast 50 -> 50 Asleep, Bad Dreams 40 -> 10, "
        "tails (Asleep). Bench left to right: Carvanha 50, Wailord 200 with two Water, Carvanha 10 with one Water. Discard: Poke Ball, two "
        "Research. Opponent global 7: 1 + draw 2, Swablu -> Mega Altaria ex (1), Psychic to Mega Altaria ex, Hypnoblast = 1. His move in "
        "the review's order (366-392): Wallace on the LEFT Carvanha (@1; random evolution -> Mega Sharpedo ex from the deck, variant "
        "patch), the drawn Mega Sharpedo ex onto the RIGHT damaged Carvanha (@3), third Water to the middle Wailord (@2), no attack."),
]
