from v2_helpers import P, B
D = 'v2deck_5309993874'; G = '20261021_020059000_SR'
HO = 'Hoopa ex B4 103'; DN = 'Deceptive Needle B4 148'; FB = 'Field Blower B3 147'; CC = 'Copycat B1 225'
KO = "Team Rocket's Koffing B4a 042"; WZ = "Team Rocket's Weezing ex B4a 043"; BT = 'Baltoy A3a 030'
PR = "Professor's Research P-A 007"; PB = 'Poké Ball P-A 005'; XS = 'X Speed P-A 002'; GZ = "Team Rocket's Goo-zooka B4a 068"
CY = 'Cyrus A2 150'; AG = 'Alolan Grimer A3 110'; AM = 'Alolan Muk B2 097'; PBB = 'Poison Barb A3 146'
EN = 'Entei ex A4a 010'; MCY = 'Mega Charizard Y ex B1a 014'; CE = 'Charmeleon B1a 012'; CM = 'Charmander A1 033'
CV = 'Clear Veil B4 149'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
POS = [
P(G, 8, 4, [0, 1],
  dict(hand=[FB, CC], disc=[PR, PB, XS, GZ, AG, AM, PBB, CY], dene='D', board=[B(HO, 90, 'DD', tool=DN)], ko=1),
  dict(hand_count=3, disc=['Lucky Ice Pop B2 145', 'Cyrus A2 150', 'Flame Patch B1 217', 'Flame Patch B1 217'], dene='',
       board=[B(EN, 140, 'RR'), B(EN, 90, 'RR', tool=CV), B(MCY, 160, behind=[CE, CM])], ko=0),
  ['Attach:1Darkness@0 zone', 'Play:Field Blower', 'DiscardToolFromPokemon{player:1,in_play_idx:1,tool_idx:0}', 'Play:Copycat',
   "Place:Team Rocket's Koffing@1", 'Place:Baltoy@2', 'Attack:Dynamite Punch'],
  D, None,
  approx=AP + "; the opponent's Trainer printings (Lucky Ice Pop, Cyrus, Flame Patch) are not shown, the printing cards.py lists "
            "first is used; the Charmeleon and Charmander under Mega Charizard Y ex: Charmeleon chosen by HP (80) and Ability title "
            "(Ignition), Charmander by HP (60) only; the opponent's Bench order (original Entei ex, then Mega Charizard Y ex) follows "
            "the slots through Cyrus on global turn 6 and the retreat on global turn 7 (the review does not give left and right)",
  ambiguous=['Opponent Entei ex printings chosen by HP (140), Ability title (Legendary Pulse) and attack title (Blazing Beatdown); '
             'A4a 010, A4a 079, A4a 087, B2a 126 and P-A 110 match; the two Entei ex have different art',
             'Opponent Mega Charizard Y ex printing chosen by HP (220) and attack title (Crimson Dive); B1a 014, B1a 077, B1a 087 and '
             'B4a 105 match',
             'Opponent Charmeleon under Mega Charizard Y ex: printing chosen by HP (80) and Ability title (Ignition); B1a 012, B2b 008, '
             'B2b 092 and P-B 020 match',
             'Opponent Charmander under Mega Charizard Y ex: its attack was not shown; printing chosen by HP (60) only'],
  draws={3: [KO, WZ, BT]},
  notes="Global 8 = his 4th turn (opponent went first). One review of the whole battle in both clips (CLIPS.json; the two REVIEW.md "
        "differ only in line 1). His hand: the review does not list the opening five; from the plays, opening = Alolan Grimer (Active), "
        "Professor's Research, Deceptive Needle, Team Rocket's Goo-zooka, Cyrus. Global 2: draw Poison Barb, Research (X Speed, Poke "
        "Ball), Poke Ball (Hoopa ex) -> Hoopa benched, Needle on Hoopa, Barb on Grimer, Darkness on Grimer; X Speed held. Global 4: draw "
        "Alolan Muk, X Speed, retreat Grimer (its one Darkness discarded), Muk on Grimer, Darkness to Hoopa, Goo-zooka, Shadow Bullet. "
        "Global 5: Muk KO'd (Grimer, Muk, Poison Barb to discard; score 0-1). Global 6: draw Field Blower, Darkness to Hoopa (2), Cyrus, "
        "Shadow Bullet; Field Blower held. Global 7: Blazing Beatdown 60, Hoopa 150 -> 90. Global 8: draw Copycat -> hand Field Blower, "
        "Copycat ('Play Copycat with an otherwise empty hand'). Opponent at the clip boundary (clip01 348s, before his attack): second "
        "Entei ex 140 with two Fire Active; Mega Charizard Y 160 no Energy and original Entei 90 two Fire with Clear Veil on the Bench; "
        "three-card hand (Copycat drew 3). Opp hand check: 3 after setup, global 1 +1 -Veil +Pulse = 4; global 3 +1 -Charmeleon +Pulse = "
        "5; global 5 +1 -Entei -Ice Pop +Ice Pop -Ice Pop -Mega -Cyrus +Pulse = 3; global 7 +1 -2 Flame Patch +Pulse = 3. Opp discard: "
        "Lucky Ice Pop (tails), Cyrus, 2 Flame Patch; the 2 Fire discarded by Mega's retreat were reattached by Flame Patch. Bench slots: "
        "setup Charmander slot 1; 2nd Entei slot 2 (global 5); Cyrus (global 6) swaps Mega and original Entei (Entei to slot 1); Mega "
        "retreats (global 7) into slot 2. His move, 'Global turn 8' in order: Darkness to Hoopa, Field Blower on the original Entei's "
        "Clear Veil, Copycat (Team Rocket's Koffing, Team Rocket's Weezing ex, Baltoy), bench Koffing then Baltoy, Dynamite Punch "
        "(clip02)."),
]
