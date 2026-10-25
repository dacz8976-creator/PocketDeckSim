from v2_helpers import P, B
D = 'v2deck_d5e2757125'; G = '20261020_032424000_SR'
GR80 = 'Alolan Grimer B2 096'; GR70 = 'Alolan Grimer A3 110'; MK = 'Alolan Muk B2 097'; PR = "Professor's Research P-A 007"
PBR = 'Poison Barb A3 146'; DN = 'Deceptive Needle B4 148'; WZ = "Team Rocket's Weezing ex B4a 043"; KO = "Team Rocket's Koffing B4a 042"
BA = 'Baltoy A3a 030'; CL = 'Claydol A3a 031'; GT = 'Glimmet B3a 044'; GA = 'Glimmora B3a 045'; PB = 'Poké Ball P-A 005'; CC = 'Copycat B1 225'
EV = 'Eevee B1 184'; JO = 'Jolteon ex B1 081'; RA = "Team Rocket's Rattata B4a 058"; CAPE = 'Elegant Cape B3b 065'
OCC = 'Copycat B1 225'; PCL = 'Pokémon Center Lady A2b 070'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
AMB_EV = 'Opponent Eevee printing chosen by HP (50) and Ability title (Boosted Evolution); B1 184, P-B 011 and P-B 054 match'
AMB_JO = 'Opponent Jolteon ex printing chosen by HP (140), Ability (Electromagnetic Wall) and attack (Mach Bolt); B1 081, B1 257, B1 276 and B3 228 match'
AMB_CC = "Opponent's Copycat in the discard: printing not shown; B1 225 used (B1 225 and B1 270 match)"
AMB_PCL = "Opponent's Pokémon Center Lady in the discard: printing not shown; A2b 070 used (A2b 070 and A2b 089 match)"
AP_TR = "; the opponent's Trainer printings in the discard are not shown (the first listed printings are used)"
AP_BENCH = ("; Bench order follows the review's left-to-right listing of each board (the review lists the opponent's Bench as Rattata, "
            "Rattata, Eevee and his as Baltoy, Glimmet, Koffing/Weezing ex, not in the order they were benched)")
POS = [
P(G, 1, 1, [0, 0],
  dict(hand=[MK, PR, PBR, DN, WZ], disc=[], dene='', board=[B(GR80, 80)], ko=0),
  dict(hand_count=3, disc=[], dene='', board=[B(EV, 50), B(EV, 50)], ko=0),
  ["Play:Professor's Research", 'Place:Baltoy@1', 'Play:Poison Barb', 'Tool:Poison Barb@0', 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's Eevee printings are chosen by HP (50) and the Boosted Evolution Ability (seen on the Active Eevee on "
            "global 2); the Benched Eevee's text is not shown",
  ambiguous=[AMB_EV],
  draws={0: [BA, PR]},
  notes="Global 1 = his 1st turn (he went first). '0-3s ... 22-44s': opening five Alolan Grimer 80, Alolan Muk, Professor's Research, "
        "Poison Barb, Deceptive Needle; Grimer 80 (B2 096) Active alone -> 4 in hand. 'Global1 (owner1)': draws Team Rocket's Weezing ex "
        "-> 5; Professor's Research draws Baltoy and the second Research; bench Baltoy 60 (slot 1); Poison Barb to the Active Grimer; no "
        "Energy (first player), no attack. Order as the review gives it. Opponent: Eevee 50 Active, Eevee 50 Bench, opening 5 - 2 = 3 cards. "
        "The hand after this turn (Muk, Needle, Weezing ex, Research) = 4 matches the opponent's Copycat drawing 4 on global 2."),
P(G, 3, 2, [0, 0],
  dict(hand=[MK, DN, WZ, PR, KO], disc=[PR], dene='', board=[B(GR80, 80, tool=PBR), B(BA, 60)], ko=0),
  dict(hand_count=3, disc=[OCC], dene='', board=[B(JO, 140, 'L', behind=[EV]), B(RA, 40), B(EV, 50)], ko=0),
  ["Place:Team Rocket's Koffing@2", "Play:Professor's Research", 'Play:Poké Ball', 'Place:Glimmet@3', 'Evolve:Alolan Muk@0',
   'Attach:1Darkness@3 zone', 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's Eevee printings are chosen by HP (50) and the Boosted Evolution Ability" + AP_TR + AP_BENCH,
  ambiguous=[AMB_EV, AMB_JO, AMB_CC],
  draws={1: [GT, PB], 2: [GT]},
  notes="Global 3 = his 2nd turn. Hand after global 1: Alolan Muk, Needle, Weezing ex, Professor's Research; 'Global3 (owner2)': draws "
        "Team Rocket's Koffing -> 5. Opponent 'Global2': draw (3+1=4), bench Team Rocket's Rattata 40 (3), Copycat (shuffle 2, draw 4 = his "
        "hand) = 4, active Eevee -> Jolteon ex 140 (3), one Lightning. Review's resulting board lists the Bench as Rattata40/Eevee50 (used "
        "as the left-to-right order). His move in the review's order: bench Koffing, Professor's Research (Glimmet + Poke Ball), Poke Ball "
        "(second Glimmet), bench one Glimmet, evolve Active Grimer 80 into Alolan Muk, Darkness to the benched Glimmet (Electromagnetic "
        "Wall 20). Place labels use the lowest empty slot (convention 1): Koffing @2, Glimmet @3; the review's resulting board lists the "
        "Bench as Baltoy, Glimmet, Koffing, so the game showed Glimmet left of Koffing."),
P(G, 5, 3, [0, 0],
  dict(hand=[DN, WZ, GT, PB], disc=[PR, PR, PB], dene='',
       board=[B(MK, 30, tool=PBR, behind=[GR80]), B(BA, 60), B(GT, 40, 'D'), B(KO, 60)], ko=0),
  dict(hand_count=2, disc=[OCC], dene='',
       board=[B(JO, 160, 'LL', tool=CAPE, cond=['Poisoned'], behind=[EV]), B(RA, 40), B(RA, 40), B(EV, 50)], ko=0),
  ['Play:Poké Ball', "Evolve:Team Rocket's Weezing ex@3", 'Ability@3', 'Attach:1Darkness@1 zone', 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's Eevee printings are chosen by HP (50) and the Boosted Evolution Ability" + AP_TR + AP_BENCH,
  ambiguous=[AMB_EV, AMB_JO, AMB_CC],
  draws={0: [GR70]},
  notes="Global 5 = his 3rd turn. Hand after global 3: Needle, Weezing ex, the second Glimmet; 'Global5 (owner3)': draws Poke Ball -> 4. "
        "Board after global 3/4: Muk 30 (Mach Bolt 80) with Barb, no Energy; Bench Baltoy 60, Glimmet 40 with one Darkness, Koffing 60, "
        "in the review's listed order (Baltoy, Glimmet, Koffing). Opponent 'Global4': draw (3+1=4), second Lightning to Jolteon, bench second "
        "Rattata (3), Elegant Cape (2) -> Jolteon 170 max, Mach Bolt, Poison Barb poisons Jolteon, checkup 170 -> 160. His move in the "
        "review's order: Poke Ball (Alolan Grimer 70 = A3 110), Koffing (slot 3) -> Weezing ex, Boiler Smog (Poisoned and Burned), "
        "Darkness to Baltoy (slot 1; Wall 20), no attack; Bench full, so Glimmet and Grimer stay in hand."),
P(G, 7, 4, [0, 1],
  dict(hand=[DN, GT, GR70, CC], disc=[PR, PR, PB, PB, MK, GR80, PBR], dene='',
       board=[B(GT, 40, 'D'), B(BA, 40, 'D'), B(WZ, 140, behind=[KO])], ko=1),
  dict(hand_count=2, disc=[OCC, PCL], dene='',
       board=[B(JO, 150, 'LL', tool=CAPE, cond=['Poisoned'], behind=[EV]), B(RA, 40), B(RA, 40), B(EV, 50, 'L')], ko=0),
  ['Place:Glimmet@3', 'Play:Deceptive Needle', 'Tool:Deceptive Needle@0', 'Play:Copycat', 'Evolve:Claydol@1', 'Evolve:Glimmora@0',
   'Attach:1Darkness@3 zone', 'Attack:Venomous Hit'],
  D, None,
  approx=AP + "; the opponent's Eevee printings are chosen by HP (50) and the Boosted Evolution Ability" + AP_TR + AP_BENCH,
  ambiguous=[AMB_EV, AMB_JO, AMB_CC, AMB_PCL],
  draws={3: ['-' + GR70, GA, CL]},
  notes="Global 7 = his 4th turn. Hand after global 5: Needle, Glimmet, Alolan Grimer 70; 'Global7 (owner4)': draws Copycat -> 4. Opponent "
        "'Global6': draw (2+1=3), Lightning to benched Eevee, Pokemon Center Lady (2) heals Jolteon 130 -> 160 and cures, Mach Bolt KOs "
        "Muk 30 (1 point), Barb re-poisons, checkup 160 -> 150; he promotes Glimmet 40 (one Darkness). His discard: 2 Research, 2 Poke "
        "Ball, Muk + Grimer 80 + Poison Barb (no Energy on Muk). Board as the review lists it: Glimmet 40 Active, Bench Baltoy 40 (one "
        "Darkness), Weezing ex 140 (compacted). His move in the review's order: bench second Glimmet (lowest empty slot @3; the game put it "
        "in the vacated middle spot: the review lists Claydol, second Glimmet, Weezing after the turn), Needle to the Active Glimmet, "
        "Copycat (Grimer 70 shuffled away; opponent's hand 2 -> draws Glimmora and Claydol), Baltoy -> Claydol, Active Glimmet -> "
        "Glimmora, Darkness to the second Glimmet (slot 3; Wall 20), Venomous Hit."),
P(G, 9, 5, [0, 2],
  dict(hand=[GA], disc=[PR, PR, PB, PB, MK, GR80, PBR, CC, GA, GT, DN], dene='',
       board=[B(GT, 40, 'D'), B(CL, 80, 'D', behind=[BA]), B(WZ, 140, behind=[KO])], ko=2),
  dict(hand_count=2, disc=[OCC, PCL], dene='L',
       board=[B("Team Rocket's Raticate ex B4a 059", 120, 'LD', behind=[RA]), B(JO, 100, 'L', tool=CAPE, behind=[EV]), B(RA, 40),
              B(EV, 50, 'L')], ko=0),
  ['Evolve:Glimmora@0', 'Attach:1Darkness@2 zone', 'Attack:Venomous Hit'],
  D, None,
  approx=AP + "; the opponent's Eevee printings are chosen by HP (50) and the Boosted Evolution Ability" + AP_TR + AP_BENCH,
  ambiguous=[AMB_EV, AMB_JO, AMB_CC, AMB_PCL,
             "Opponent Team Rocket's Raticate ex printing chosen by HP (120), Ability (Thieving Incisors) and attack (Boost Dash); "
             "B4a 059, B4a 084 and B4a 093 match"],
  notes="Global 9 = his 5th turn. Hand after global 7: empty (Glimmet benched, Needle attached, Grimer shuffled away by Copycat, Glimmora "
        "and Claydol played); 'Global9 (owner5)': draws the second Glimmora -> 1 card. Opponent 'Global8': draw (2+1=3), Jolteon retreats "
        "(one Lightning discarded, Poison gone), Rattata promoted and evolved into Raticate ex (2), Thieving Incisors moves Glimmora's "
        "Darkness to Raticate, Lightning attached, Boost Dash 70 KOs Glimmora 70 (Shattering Crystal tails, 2nd point); he promotes the "
        "second Glimmet 40 (one Darkness). Glimmora + Glimmet + Needle to his discard, no Energy (its Darkness was moved). Board: Bench "
        "Claydol 80 (one Darkness), Weezing ex 140. Opponent Bench as the review lists it: Jolteon 100 (one Lightning, Cape), Rattata 40, "
        "Eevee 50 (one Lightning). His move: Glimmet -> Glimmora, Darkness to Weezing ex (slot 2; Jolteon benched, no Wall), Venomous Hit."),
]
