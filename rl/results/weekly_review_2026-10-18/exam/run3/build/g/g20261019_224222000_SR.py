from v2_helpers import P, B
D = 'v2deck_06ee642b71'; G = '20261019_224222000_SR'
HO = 'Hoopa ex B4 103'; AG = 'Alolan Grimer A3 110'; DK = 'Darkrai ex A2 110'; MS = 'Mega Sableye ex B3b 041'
WZ = "Team Rocket's Weezing ex B4a 043"; KO = "Team Rocket's Koffing B4a 042"; BA = 'Baltoy A3a 030'; CL = 'Claydol A3a 031'
CY = 'Cyrus A2 150'; FB = 'Field Blower B3 147'; PB = 'Poké Ball P-A 005'; GZ = "Team Rocket's Goo-zooka B4a 068"; CC = 'Copycat B1 225'
# opponent's cards (printing: the first cards.py lists among those matching every shown fact)
EV = 'Eevee B1 184'; ES = 'Espeon B3a 020'; ODK = 'Darkrai B2b 040'; SW = 'Swablu A4a 064'; MA = 'Mega Altaria ex B1 102'
OSB = 'Small Balloon B3b 064'; OPB = 'Poké Ball A2b 111'; OCC = 'Copycat B1 225'; OPR = "Professor's Research A4b 373"; OSA = 'Sabrina A1 225'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
A_EV = 'Opponent Eevee printing chosen by HP (50) and Ability title (Boosted Evolution); B1 184, P-B 011 and P-B 054 match'
A_DK = 'Opponent Darkrai printing chosen by HP (100) and Ability title (Bad Dreams); B2b 040 is the only match'
A_SW = 'Opponent Swablu: its attack was not shown; printing chosen by HP (50) only (the 50-HP Swablu printings have Peck, Sing, Fury Attack or Find a Friend)'
A_ES = 'Opponent Espeon printing chosen by HP (90) and attack title (Hypnoblast); B3a 020 is the only match'
A_SB = "Opponent's Small Balloon printing not shown; B3b 064 and B3b 106 match"
A_PB = "Opponent's Poké Ball printing not shown; A2b 111 and P-A 005 match"
A_CC = "Opponent's Copycat printing not shown; B1 225 and B1 270 match"
A_PR = "Opponent's Professor's Research printing not shown; A4b 373 and P-A 007 match"
A_MA = 'Opponent Mega Altaria ex printing chosen by HP (190) and attack title (Mega Harmony); B1 102, B1 259, B1 286 and B3a 107 match'
A_SA = "Opponent's Sabrina printing not shown; A1 225, A1 272, A4b 338 and A4b 339 match"
A_EV2 = "Opponent's second Eevee (benched on global 2): its HP, Ability and attack were not shown; it is given the first Eevee's printing (B1 184, 50 HP)"
AP_EV2 = "; the second Eevee's HP and attack were not shown: it is given the first Eevee's printing B1 184 (50 HP; by name alone the first-listed would be A1 206, 60 HP)"
POS = [
P(G, 1, 1, [0, 0],
  dict(hand=[CY, FB, DK, MS], disc=[], dene='', board=[B(HO, 150), B(AG, 70)], ko=0),
  dict(hand_count=3, disc=[], dene='', board=[B(EV, 50), B(ODK, 100)], ko=0),
  ['Place:Darkrai ex@2', 'EndTurn'],
  D, None,
  approx=AP,
  ambiguous=[A_EV, A_DK],
  notes="Global 1 = his 1st turn (he went first; no Energy). 'Opening/setup0-38s': opening five Hoopa ex, Alolan Grimer, Cyrus, Field "
        "Blower, Darkrai ex; Hoopa Active, Grimer benched -> hand Cyrus, Field Blower, Darkrai ex. Opponent: Eevee 50 Active (Boosted "
        "Evolution), non-ex Darkrai 100 on the Bench; hand 5-2 = 3 (no draw yet). Row '1/owner': draw Mega Sableye ex -> 4 cards; bench "
        "Darkrai ex beside Grimer (@2), no Energy, no attack."),
P(G, 3, 2, [0, 0],
  dict(hand=[CY, FB, MS, WZ], disc=[], dene='', board=[B(HO, 90), B(AG, 70), B(DK, 140)], ko=0),
  dict(hand_count=0, disc=[OPB], dene='', board=[B(ES, 90, 'P', behind=[EV]), B(ODK, 100), B(SW, 50, tool=OSB), B(EV, 50)], ko=0),
  ['Play:Field Blower', 'Attach:1Darkness@0 zone', 'Attack:Shadow Bullet'],
  D, None,
  approx=AP + "; the opponent's Bench is listed in the order benched (Darkrai at setup, then Swablu, then the 2nd Eevee); the hand "
              "count assumes the Poke Ball found a Basic (the 2nd Eevee benched after it)" + AP_EV2,
  ambiguous=[A_ES, A_EV, A_EV2, A_DK, A_SW, A_SB, A_PB],
  notes="Global 3 = his 2nd turn. Hand after global 1: Cyrus, Field Blower, Mega Sableye ex; row '3/owner': draw Team Rocket's Weezing "
        "ex -> 4 cards (Darkrai ex benched beside Grimer: Bench Grimer, Darkrai ex). Row '2/opponent': hand 3, draw 4, Swablu benched (-1) 3, Poke Ball (-1 +1) 3, 2nd Eevee benched (-1) 2, Active "
        "Eevee -> Espeon 90 (-1) 1 with one Psychic, Small Balloon on Swablu (-1) 0; Hypnoblast 40 (Hoopa 150 -> 110, Asleep), Bad "
        "Dreams 20 (-> 90), Sleep coin heads: Hoopa awake. His move in the review's order: Field Blower on Swablu's Small Balloon (the "
        "only Tool in play and no Stadium, so the engine applies the single choice itself: no target label), "
        "Darkness to Hoopa, Shadow Bullet (50 to Espeon with Weakness, 20 to the benched Darkrai, opponent Bench slot 1). The engine "
        "offers the Bench target only as ApplyQueuedAttackDamage labels, which convention 5 forbids writing, so the line ends at the "
        "attack."),
P(G, 5, 3, [0, 0],
  dict(hand=[CY, MS, WZ, CL], disc=[FB], dene='', board=[B(HO, 30, 'D', cond=['Asleep']), B(AG, 70), B(DK, 140)], ko=0),
  dict(hand_count=3, disc=[OPB, OSB, OCC, OPB], dene='', board=[B(ES, 40, 'P', behind=[EV]), B(ODK, 80, 'P'), B(SW, 50), B(EV, 50)], ko=0),
  ['Attach:1Darkness@2 zone', 'Place:Mega Sableye ex@3', 'Play:Cyrus', 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's Bench in the order benched; the hand count assumes the global-4 Copycat drew 3 (his hand was 3) and the "
              "Poke Ball found a Basic kept in the hand" + AP_EV2,
  ambiguous=[A_ES, A_EV, A_EV2, A_DK, A_SW, A_SB, A_PB, A_CC],
  notes="Global 5 = his 3rd turn. Hand after global 3: Cyrus, Mega Sableye ex, Weezing ex; row '5/owner': draw Claydol -> 4 cards. "
        "Discard Field Blower. Row '4/opponent': hand 0, draw 1, Copycat (-1, draws 3 = his 3-card hand) 3, Poke Ball (-1 +1) 3; Psychic "
        "to the benched Darkrai; Hypnoblast 40 (Hoopa 90 -> 50, Asleep), Bad Dreams 20 (-> 30), Sleep coin tails: Hoopa still Asleep. "
        "Opponent discard: Poke Ball, Small Balloon (his Field Blower), Copycat, Poke Ball. Espeon 40 (Shadow Bullet), Darkrai 80. His "
        "move in the review's order: Darkness to benched Darkrai ex (@2; Nightmare Aura 20, Espeon 20), Mega Sableye ex benched (@3), "
        "Cyrus switching in the damaged Darkrai (the only damaged Benched Pokemon, so no target label), end without attacking (Hoopa "
        "Asleep)."),
P(G, 7, 4, [0, 2],
  dict(hand=[WZ, CL, PB], disc=[FB, CY, HO], dene='D', board=[B(MS, 170), B(AG, 70), B(DK, 140, 'D')], ko=1),
  dict(hand_count=4, disc=[OPB, OSB, OCC, OPB, OPR], dene='',
       board=[B(ODK, 80, 'PP'), B(SW, 50), B(ES, 90, behind=[EV]), B(ES, 20, 'P', behind=[EV])], ko=0),
  ['Play:Poké Ball', 'Place:Baltoy@3', 'Attach:1Darkness@0 zone', 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's Bench in the order benched (Swablu, the 2nd Eevee now Espeon, then the first Espeon, switched to the "
              "Bench by Cyrus on global 5)",
  ambiguous=[A_ES, A_EV, A_DK, A_SW, A_SB, A_PB, A_CC, A_PR],
  draws={0: [BA]},
  notes="Global 7 = his 4th turn. Hand after global 5: Weezing ex, Claydol; row '7/owner': draw Poke Ball -> 3 cards. Row '6/opponent': "
        "hand 3, draw 4, Professor's Research (-1 +2) 5, 2nd Psychic to the Active Darkrai, 2nd Eevee -> Espeon 90 (-1) 4, no attack; "
        "Bad Dreams 20 KOs Hoopa ex (10), opponent +2; he promoted Mega Sableye ex 170 (Starting Plains not in play: 170). Discard: "
        "Field Blower, Cyrus, Hoopa ex, one Darkness. His Bench: Grimer 70, Darkrai ex 140 with one Darkness (order benched). His move "
        "in the review's order: Poke Ball (reveals Baltoy), Baltoy benched (@3), Darkness to Mega Sableye ex, end (no attack)."),
P(G, 9, 5, [0, 2],
  dict(hand=[WZ, CL, GZ], disc=[FB, CY, HO, PB], dene='D', board=[B(MS, 170, 'D'), B(AG, 70), B(DK, 140, 'D'), B(BA, 60)], ko=1),
  dict(hand_count=4, disc=[OPB, OSB, OCC, OPB, OPR], dene='',
       board=[B(ODK, 80, 'PP'), B(MA, 190, 'P', behind=[SW]), B(ES, 90, behind=[EV]), B(ES, 20, 'P', behind=[EV])], ko=0),
  ['Evolve:Claydol@3', 'Attach:1Darkness@0 zone', 'Attack:Cursed Jewel'],
  D, None,
  approx=AP + "; the opponent's Bench in the order benched, as on global 7",
  ambiguous=[A_MA, A_ES, A_EV, A_DK, A_SW, A_SB, A_PB, A_CC, A_PR],
  notes="Global 9 = his 5th turn. Hand after global 7: Weezing ex, Claydol; row '9/owner': draw Team Rocket's Goo-zooka -> 3 cards. "
        "Row '8/opponent': hand 4, draw 5, Swablu -> Mega Altaria ex 190 (-1) 4, one Psychic to the benched Mega Altaria, Darkrai (two "
        "Psychic) does not attack. His move in the review's order: Baltoy (@3) -> Claydol, 2nd Darkness to Mega Sableye ex, Cursed "
        "Jewel 80 KOs the non-ex Darkrai 80 (+1); the attack ends the turn."),
P(G, 11, 6, [1, 2],
  dict(hand=[WZ, GZ, KO], disc=[FB, CY, HO, PB], dene='D',
       board=[B(DK, 10, 'D'), B(AG, 70), B(CL, 100, behind=[BA]), B(MS, 170, 'DD')], ko=1),
  dict(hand_count=3, disc=[OPB, OSB, OCC, OPB, OPR, ODK, OSA], dene='PP',
       board=[B(MA, 190, 'PP', behind=[SW]), B(ES, 90, behind=[EV]), B(ES, 20, 'P', behind=[EV]), B(SW, 50)], ko=1),
  ['Attach:1Darkness@0 zone', 'Retreat:3', "Play:Team Rocket's Goo-zooka", 'Attack:Cursed Jewel'],
  D, None,
  approx=AP + "; Benches listed in the order benched (his Mega Sableye ex moved to the Bench by Sabrina on global 10 is listed last); "
              "the review says the retreat paid one Darkness, but Darkrai ex's Retreat Cost is 2 (the engine pays 2)",
  ambiguous=[A_MA, A_ES, A_EV, A_SW, A_SB, A_PB, A_CC, A_PR, A_SA],
  notes="Global 11 = his 6th turn. Hand after global 9: Weezing ex, Goo-zooka; row '11/owner': draw Team Rocket's Koffing -> 3 cards. "
        "Row '9/owner': Darkrai (opponent) KO'd -> opponent discard Darkrai, PP; opponent promoted Mega Altaria ex 190. Row "
        "'10/opponent': hand 4, draw 5, 2nd Swablu benched (-1) 4, Sabrina (-1) 3; he chose Darkrai ex (one Darkness) as the new "
        "Active, Mega Sableye ex (two Darkness) to the Bench; 2nd Psychic to Mega Altaria; Mega Harmony 130 (Darkrai 140 -> 10). His "
        "Bench in the order benched: Grimer, Claydol, Mega Sableye ex (slot 3). His move in the review's order: Darkness to Active "
        "Darkrai (Nightmare Aura 20, Mega Altaria 170), retreat Darkrai into Mega Sableye ex (Retreat:3; the review says 'pay1Darkness' "
        "but the card's Retreat Cost is 2 and the engine pays 2), Goo-zooka, Cursed Jewel 80 (Mega Altaria 90)."),
P(G, 13, 7, [1, 2],
  dict(hand=[WZ, KO, CC], disc=[FB, CY, HO, PB, GZ], dene='DDD',
       board=[B(MS, 40, 'DD'), B(AG, 70), B(CL, 100, behind=[BA]), B(DK, 10)], ko=1),
  dict(hand_count=4, disc=[OPB, OSB, OCC, OPB, OPR, ODK, OSA], dene='PP',
       board=[B(MA, 50, 'PP', behind=[SW]), B(ES, 90, 'P', behind=[EV]), B(ES, 20, 'P', behind=[EV]), B(SW, 50)], ko=1),
  ['Attach:1Darkness@3 zone', 'Attack:Cursed Jewel'],
  D, None,
  approx=AP + "; Benches listed in the order benched (his Darkrai ex, moved to the Bench by the global-11 retreat, is listed last); "
              "Darkrai ex's Energy set to none and the discard to three Darkness on the card's Retreat Cost 2 (the review says the "
              "global-11 retreat paid one Darkness and that Darkrai holds two Darkness after this turn's attachment, which would leave "
              "it one Darkness here and two in the discard)",
  ambiguous=[A_MA, A_ES, A_EV, A_SW, A_SB, A_PB, A_CC, A_PR, A_SA],
  notes="Global 13 = his 7th turn. Hand after global 11: Weezing ex, Koffing; row '13/owner': draw Copycat -> 3 cards (kept). Discard "
        "adds Goo-zooka and the retreat's Darkness. Row '12/opponent': hand 3, draw 4, Psychic to the undamaged benched Espeon, Mega "
        "Harmony 130 (Mega Sableye 170 -> 40), Cursed Jewel's 40 back (Mega Altaria 90 -> 50); no Supporter. Darkrai ex: three "
        "Nightmare Aura attachments in the game (globals 5, 11, 13); the global-11 retreat is read as paying the card's cost of 2, so it "
        "starts this turn with no Energy (the review's 'pay1Darkness' and final 'Darkrai ex10/140,2Darkness' conflict with Retreat "
        "Cost 2). His move in the review's order: Darkness to benched Darkrai ex (@3; Aura 20, Mega Altaria 30), Cursed Jewel 80 KOs "
        "Mega Altaria ex (+3), game over."),
]
