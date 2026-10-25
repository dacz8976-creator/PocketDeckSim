from v2_helpers import P, B
D = 'v2deck_4fa967805c'; G = '20261021_224410000_SR'
CV = 'Carvanha B4 034'; MS = 'Mega Sharpedo ex B4 035'; WM = 'Wailmer B4 036'; WL = 'Wailord B1 057'; BT = 'Baltoy A3a 030'
CL = 'Claydol A3a 031'; PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"; CY = 'Cyrus A2 150'; HH = 'Heavy Helmet B1 219'
CC = 'Copycat B1 225'; EC = 'Elegant Cape B3b 065'; WA = 'Wallace B3b 068'
# opponent (printings by convention 3: the first cards.py lists among those matching what the review shows)
TK = 'Treecko B3 005'; GV = 'Grovyle B3 006'; SC = 'Mega Sceptile ex B3 008'; LC = 'Leaf Cape A3 147'
oPR = "Professor's Research A4b 373"; LIP = 'Lucky Ice Pop B2 145'; PCL = 'Pokémon Center Lady A2b 070'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
TR = ("the opponent's Trainer printings are not shown; the first-listed printings are used (Professor's Research A4b 373, Leaf Cape "
      "A3 147, Lucky Ice Pop B2 145, Pokémon Center Lady A2b 070)")
AM_TK = 'Opponent Treecko printing chosen by HP (60) and attack title (Pound); B3 005, B3 156 and P-B 061 match'
AM_GV = 'Opponent Grovyle printing chosen by name and HP (80) only (no attack shown); B3 006 and B3 157 match'
AM_SC = 'Opponent Mega Sceptile ex printing chosen by HP (210) and attack title (Terminating Tail); B3 008, B3 180, B3 194 and P-B 087 match'
AM_TR = ("Opponent's Trainers: printings not shown; Professor's Research A4b 373, Leaf Cape A3 147, Lucky Ice Pop B2 145 and "
         "Pokémon Center Lady A2b 070 listed")
# verifier (Oct 25): Lucky Ice Pop is first played on global 4 and Pokémon Center Lady on global 8, so t3, t5 and t7 name only the Trainers
# seen by then
TR3 = ("the opponent's Trainer printings are not shown; the first-listed printings are used (Professor's Research A4b 373, Leaf Cape "
       "A3 147)")
AM_TR3 = "Opponent's Trainers: printings not shown; Professor's Research A4b 373 and Leaf Cape A3 147 listed"
TR5 = ("the opponent's Trainer printings are not shown; the first-listed printings are used (Professor's Research A4b 373, Leaf Cape "
       "A3 147, Lucky Ice Pop B2 145)")
AM_TR5 = "Opponent's Trainers: printings not shown; Professor's Research A4b 373, Leaf Cape A3 147 and Lucky Ice Pop B2 145 listed"
# coordinator-048, 4 (Oct 25): the note on his Benched Mega Sharpedo ex's Water is removed after a frame check (two independent Sonnet
# checks agree, high confidence): ScreenRecording_10-21-2026 17-44-10_1.mp4 shows one Water on the Active Mega Sharpedo ex before the
# global-7 retreat (230-237.9 s), no Energy discard step (only the switch-in prompt, 236-237.9 s), and one Water on it on the Bench from
# 241.7 s and at the starts of globals 9, 11 and 13 (285.5-287, 309-311, 359-361 s). The review's "the retreat paid that Water" is not taken.
RET = ("; his Benched Mega Sharpedo ex keeps its one Water through the global-7 retreat (Retreat Cost 0): the recording's frames show one "
       "Water on it before the retreat, no Energy discard, and one Water at the starts of globals 9, 11 and 13 (note 048 frame check); the "
       "review's 'the retreat paid that Water' is not taken")


def wallace_ms(v):
    # the review: Wallace put Mega Sharpedo ex onto the Active Carvanha (no damage). The variant starts at the start of the turn and
    # still plays the Cape (labels 0-1), so the patched Active carries no Tool yet (190; the Cape then makes it 220)
    v['me']['board'][0] = B(MS, 190, behind=[CV])


POS = [
P(G, 1, 1, [0, 0],
  dict(hand=[CY, EC, CL, WA, WL], disc=[], dene='', board=[B(CV, 50)], ko=0),
  dict(hand_count=4, disc=[], dene='', board=[B(TK, 60)], ko=0),
  ['Play:Elegant Cape', 'Tool:Elegant Cape@0', 'Play:Wallace', 'ChooseRandomEvolutionTarget', 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's hand count (4) is the opening five less the Active Treecko (no Bench at setup, no draw yet)",
  ambiguous=[AM_TK],
  draws={2: []}, vpatch=wallace_ms,
  notes="Global 1 = his 1st turn (he went first). Review '27-39s setup': opening five Carvanha, Cyrus, Elegant Cape, Claydol, "
        "Wallace; Carvanha 50 Active, no Bench -> 4 in hand; opponent Treecko 60 Active only (4 in hand). 'Global T1' 40-57s: draws "
        "Wailord -> 5. His move in the review's order: Elegant Cape on the Active Carvanha, Wallace selecting Carvanha (Mega Sharpedo "
        "ex, 220 with Cape; native 049.50s, 052.50s), no Energy (first turn), no attack, end. Variant: the random evolution is set "
        "by vpatch."),
P(G, 3, 2, [0, 0],
  dict(hand=[CY, CL, WL, CV], disc=[WA], dene='', board=[B(MS, 200, tool=EC, behind=[CV])], ko=0),
  dict(hand_count=3, disc=[oPR], dene='', board=[B(TK, 90, 'G', tool=LC), B(TK, 90, tool=LC)], ko=0),
  ['Place:Carvanha@1', 'Attach:1Water@0 zone', 'Attack:Turbo Shark', 'Attach:1Water@1 fx'],
  D, None,
  approx=AP + "; " + TR3,
  ambiguous=[AM_TK, AM_TR3],
  notes="Global 3 = his 2nd turn. His hand after global 1: Cyrus, Claydol, Wailord; 'Global T3' 89-103s draws the 2nd Carvanha -> 4. "
        "Discard Wallace. Board: Mega Sharpedo ex 220-20 = 200 with Cape, no Energy. Opponent 'Global T2' 58-88s: draw (4->5), "
        "Professor's Research (6), Leaf Cape on the Active Treecko (5), 2nd Treecko benched (4), Leaf Cape on it (3); both 90; Grass "
        "to the Active, Pound 20. His move in the review's order: bench Carvanha (slot 1), Water to the Active Sharpedo, Turbo Shark "
        "99-103s (Treecko 90->20), its zone Water to the Benched Carvanha (native 110)."),
P(G, 5, 3, [0, 0],
  dict(hand=[CY, CL, WL, PR], disc=[WA], dene='', board=[B(MS, 180, 'W', tool=EC, behind=[CV]), B(CV, 50, 'W')], ko=0),
  dict(hand_count=3, disc=[oPR, oPR, LIP], dene='', board=[B(TK, 60, 'G', tool=LC), B(GV, 110, 'G', tool=LC, behind=[TK])], ko=0),
  ["Play:Professor's Research", 'Play:Poké Ball', 'Place:Wailmer@2', 'Attach:1Water@2 zone', 'Attack:Turbo Shark', 'Attach:1Water@2 fx'],
  D, None,
  approx=AP + "; " + TR5,
  ambiguous=[AM_TK, AM_GV, AM_TR5],
  draws={0: [PR, PB], 1: [WM]},
  notes="Global 5 = his 3rd turn. His hand after global 3: Cyrus, Claydol, Wailord; 'Global T5' 144-178s draws Professor's Research "
        "-> 4. Board: Sharpedo 200-20 = 180, Cape, one Water; Carvanha 50 one Water (slot 1). Opponent 'Global T4' 104-143s: draw "
        "(3->4), Research (5), Lucky Ice Pop 20->40 heads back to hand, again 40->60 tails to discard (4), Grass to the Benched "
        "Treecko, it evolves to Grovyle 80+30 = 110 (3), Pound 20. His move in the review's order: Research (the 2nd Research and Poke "
        "Ball), Poke Ball (Wailmer), bench Wailmer (slot 2), manual Water to Wailmer (native 163), Turbo Shark KOs Treecko 60, its "
        "zone Water to Wailmer (two; native 171)."),
P(G, 7, 4, [1, 0],
  dict(hand=[CY, CL, WL, PR, WL], disc=[WA, PR, PB], dene='',
       board=[B(MS, 40, 'W', tool=EC, cond=['Poisoned'], behind=[CV]), B(CV, 50, 'W'), B(WM, 100, 'WW')], ko=0),
  dict(hand_count=3, disc=[oPR, oPR, LIP, TK, LC], dene='GG', board=[B(SC, 240, 'G', tool=LC, behind=[GV, TK])], ko=1),
  ['Evolve:Wailord@2', "Play:Professor's Research", 'Play:Poké Ball', 'Play:Heavy Helmet', 'Tool:Heavy Helmet@2', 'Retreat:1',
   'Attach:1Water@2 zone', 'Place:Wailmer@3', 'Attack:Sharp Fang'],
  D, None,
  approx=AP + "; " + TR5 + "; the opponent's discarded Energy counts the knocked-out Treecko's Grass and the Grass Terminating Tail "
            "discarded",
  ambiguous=[AM_TK, AM_GV, AM_SC, AM_TR5],
  draws={1: [HH, PB], 2: [WM]},
  notes="Global 7 = his 4th turn. His hand after global 5: Cyrus, Claydol, Wailord, the 2nd Research; 'Global T7' 198-252s draws the "
        "2nd Wailord -> 5. Discard Wallace, Research, Poke Ball. Score 1-0. Opponent 'Global T6' 179-197s: Grovyle promoted; draw "
        "(3->4), Grovyle -> Mega Sceptile ex 210+30 = 240 (3), 2nd Grass, Terminating Tail 130 (Sharpedo 180->50), one Grass "
        "discarded, Poisoned; checkup 10 -> 40. His move in the review's order: Wailmer -> Wailord (slot 2), Research (Heavy Helmet, "
        "Poke Ball), Poke Ball (the 2nd Wailmer), Helmet on Wailord, retreat the poisoned Sharpedo for Carvanha (slot 1 comes in; "
        "Retreat Cost 0, the review's 'paying its one Water' is not taken), 3rd Water to Wailord (native 243), bench the 2nd Wailmer "
        "(slot 3), Carvanha Sharp Fang 30 (240->210)."),
P(G, 9, 5, [1, 1],
  dict(hand=[CY, CL, WL, MS], disc=[WA, PR, PB, PR, PB, CV], dene='W',
       board=[B(WM, 100), B(MS, 40, 'W', tool=EC, behind=[CV]), B(WL, 200, 'WWW', tool=HH, behind=[WM])], ko=1),
  dict(hand_count=3, disc=[oPR, oPR, LIP, TK, LC, PCL], dene='GGG', board=[B(SC, 240, 'G', tool=LC, behind=[GV, TK])], ko=1),
  ['Evolve:Wailord@0', 'Attach:1Water@2 zone', 'EndTurn'],
  D, None,
  approx=AP + "; " + TR + RET + "; his Bench is compacted after the Bench Wailmer was promoted (Sharpedo, then Wailord)",
  ambiguous=[AM_TK, AM_GV, AM_SC, AM_TR],
  notes="Global 9 = his 5th turn. His hand after global 7: Cyrus, Claydol, Wailord (hand 5 - Wailord evolved - Research + Helmet, "
        "Poke Ball - Poke Ball + Wailmer - Helmet - Wailmer placed); 'Global T9' 285-294s draws the 2nd Mega Sharpedo ex -> 4. "
        "Opponent 'Global T8' 253-284s: draw (3->4), Pokemon Center Lady (210->240; 3), Grass, Terminating Tail 130 KOs Carvanha "
        "(score 1-1; Carvanha and its Water to his discard), one Grass discarded. He promotes the unpowered Wailmer (slot 3); the "
        "Bench is compacted: Sharpedo 40 (slot 1), Helmet Wailord 200 three Water (slot 2). His move: Active Wailmer -> Wailord 200, "
        "4th Water to the Benched Helmet Wailord, no attack (native 293)."),
P(G, 11, 6, [1, 1],
  dict(hand=[CY, CL, MS, CC], disc=[WA, PR, PB, PR, PB, CV], dene='W',
       board=[B(WL, 60, cond=['Poisoned'], behind=[WM]), B(MS, 40, 'W', tool=EC, behind=[CV]), B(WL, 200, 'WWWW', tool=HH, behind=[WM])],
       ko=1),
  dict(hand_count=4, disc=[oPR, oPR, LIP, TK, LC, PCL], dene='GGGG', board=[B(SC, 240, 'G', tool=LC, behind=[GV, TK])], ko=1),
  ['Play:Copycat', 'Place:Baltoy@3', 'Play:Elegant Cape', 'Tool:Elegant Cape@0', 'Attach:1Water@2 zone', 'EndTurn'],
  D, None,
  approx=AP + "; " + TR + RET,
  ambiguous=[AM_TK, AM_GV, AM_SC, AM_TR],
  draws={0: ['-' + CY, '-' + CL, '-' + MS, BT, CL, EC, MS]},
  notes="Global 11 = his 6th turn. His hand after global 9: Cyrus, Claydol, Mega Sharpedo ex; 'Global T11' 309-338s draws Copycat "
        "-> 4. Opponent 'Global T10' 295-308s: draw (3->4), Grass, Terminating Tail 130 (Wailord 200->70), Grass discarded, "
        "Poisoned; checkup 10 -> 60. His move in the review's order: Copycat (Cyrus, Claydol, Sharpedo shuffled in; draws 4 = "
        "opponent's 4: Baltoy, Claydol, Elegant Cape, Mega Sharpedo ex), bench Baltoy (slot 3), Cape on the Active Wailord (60->90), "
        "5th Water to the Benched Helmet Wailord, no attack. Deck check: before Copycat his deck held Baltoy and the 2nd Cape only."),
P(G, 13, 7, [1, 2],
  dict(hand=[CL, MS, CY], disc=[WA, PR, PB, PR, PB, CV, CC, WL, WM, EC], dene='W',
       board=[B(WL, 200, 'WWWWW', tool=HH, behind=[WM]), B(MS, 40, 'W', tool=EC, behind=[CV]), B(BT, 60)], ko=2),
  dict(hand_count=5, disc=[oPR, oPR, LIP, TK, LC, PCL], dene='GGGGG', board=[B(SC, 240, 'G', tool=LC, behind=[GV, TK])], ko=1),
  ['Attach:1Water@0 zone', 'Evolve:Claydol@2', 'Attack:Whale Pump'],
  D, None,
  approx=AP + "; " + TR + RET + "; his Bench is compacted after the Helmet Wailord was promoted (Sharpedo, then Baltoy)",
  ambiguous=[AM_TK, AM_GV, AM_SC, AM_TR],
  notes="Global 13 = his 7th turn. His hand after global 11: Claydol, Mega Sharpedo ex; 'Global T13' 359-373s draws Cyrus (the last "
        "card of his deck) -> 3. Opponent 'Global T12' 339-358s: draw (4->5), Grass, Terminating Tail 130 KOs the Cape Wailord 80 "
        "(score 1-2; Wailord, Wailmer, Cape to his discard), Grass discarded. He promotes the Helmet Wailord 200 five Water (slot 2); "
        "Bench compacted: Sharpedo 40 (slot 1), Baltoy 60 (slot 2). His move in the review's order: 6th Water to the Active Wailord, "
        "Baltoy -> Claydol (Heal Block), Whale Pump 120 (240->120)."),
]
