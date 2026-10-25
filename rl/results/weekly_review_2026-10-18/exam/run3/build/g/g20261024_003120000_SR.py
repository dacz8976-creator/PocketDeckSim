from v2_helpers import P, B
D = 'v2deck_995ac0891e'; G = '20261024_003120000_SR'
SQ = 'Squirtle P-A 033'; OR = 'Oricorio A3 066'; EI = 'Eiscue B1 080'; WT = 'Wartortle B1a 018'
PB = 'Poké Ball P-A 005'; LI = 'Lillie A3 155'; LP = 'Lucky Ice Pop B2 145'; CY = 'Cyrus A2 150'; PL = 'Parasol Lady B3 152'
CP = 'Chien-Pao ex B2a 037'; MW = 'Meowth B2 124'; CV = 'Carvanha B4 034'; MS = 'Mega Sharpedo ex B4 035'
GC = 'Giant Cape A2 147'; EC = 'Elegant Cape B3b 065'; OPR = "Professor's Research A4b 373"
AP = "opponent's list unknown; opponent's hand size from the visible plays"
AMB = ['Opponent Chien-Pao ex printing chosen by HP (130 before Giant Cape) and attack title (Icicle); B2a 037, B2a 102, B2a 112 and '
       'P-B 041 match',
       "Opponent Meowth printing chosen by HP (50) and Ability title (Carefree Steps); B2 124 and B2 204 match",
       'Opponent Giant Cape printing not shown; A2 147, A4b 320 and A4b 321 match',
       "Opponent Professor's Research printing in the discard not shown; A4b 373 used (P-A 007 also matches)"]
AMB_CV = ['Opponent Carvanha printing chosen by HP (50) only (its attack was not shown); B4 034 and P-B 081 match']
AMB_MS = ['Opponent Mega Sharpedo ex printing chosen by HP (190 before Elegant Cape) and attack title (Turbo Shark); B4 035, B4 182 '
          'and B4 196 match']


def pop_tails(v):
    # Lucky Ice Pop: heals 20 on the Active Eiscue (50 -> 70); coin tails, the Pop goes to the discard
    v['me']['board'][0]['hp'] = 70
    v['me']['discard'] = list(v['me']['discard']) + [LP]


POS = [
P(G, 3, 2, [0, 0],
  dict(hand=[PL, LI, WT, WT, CY], disc=[PB], dene='', board=[B(EI, 80), B(EI, 80)], ko=0),
  dict(hand_count=4, disc=[OPR], dene='', board=[B(CP, 150, 'W', tool=GC), B(MW, 50)], ko=0),
  ['Attach:1Water@0 zone', 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's Professor's Research printing is not shown (first listed printing used)",
  ambiguous=AMB,
  notes="Global 3 = his 2nd turn (he went first). Setup: Eiscue 80 Active; opening five Eiscue, Parasol Lady, Lillie, Poke Ball, "
        "Wartortle -> 4 in hand. Global 1: draws the 2nd Wartortle, Poke Ball finds the 2nd Eiscue, benched -> hand Parasol Lady, "
        "Lillie, two Wartortle. Global 3: draws Cyrus -> 5. Opponent: Chien-Pao ex Active; global 2 Research, Water to Chien-Pao, "
        "Meowth 50 benched, Giant Cape (130 -> 150), Icicle 0 (Ice Face). Hand 5 - 1 = 4, draw 5, Research 6, Meowth 5, Cape 4. Move "
        "(global 3 section): Water to Active Eiscue, no Supporter, no attack."),
P(G, 5, 3, [0, 0],
  dict(hand=[PL, LI, WT, WT, CY, OR], disc=[PB], dene='', board=[B(EI, 80, 'W'), B(EI, 80)], ko=0),
  dict(hand_count=4, disc=[OPR, OPR], dene='', board=[B(CP, 150, 'WW', tool=GC), B(MW, 50), B(CV, 50, tool=EC)], ko=0),
  ['Place:Oricorio@2', 'Attach:1Water@0 zone', 'Attack:Ram'],
  D, None,
  approx=AP + "; the opponent's Professor's Research printings are not shown (first listed printing used); the opponent's Bench order "
            "(Meowth, Carvanha) is the order benched",
  ambiguous=AMB + AMB_CV,
  notes="Global 5 = his 3rd turn. Hand after global 3: Parasol Lady, Lillie, two Wartortle, Cyrus; draws Oricorio -> 6. Global 4: 2nd "
        "Water to Chien-Pao, Research, Carvanha 50 benched, Elegant Cape on Carvanha (no HP change on a Basic), Icicle 0. Opponent hand 4 "
        "+ 1 + 1 - Carvanha - Cape = 4. Move (global 5 section): bench Oricorio 129-133 (@2), Parasol Lady targeting opened and "
        "cancelled at 138 (no play, not a label), Water to Active Eiscue 139-140, Ram 143-145 (Chien-Pao 150 -> 100)."),
P(G, 7, 4, [0, 0],
  dict(hand=[PL, LI, WT, WT, CY, LP], disc=[PB], dene='', board=[B(EI, 50, 'WW'), B(EI, 80), B(OR, 70)], ko=0),
  dict(hand_count=4, disc=[OPR, OPR], dene='W',
       board=[B(MS, 220, 'W', tool=EC, behind=[CV]), B(MW, 50), B(CP, 100, 'WW', tool=GC)], ko=0),
  ['Play:Lucky Ice Pop', 'Attach:1Water@1 zone', 'Attack:Ram'],
  D, None,
  approx=AP + "; the opponent's Bench order (Meowth, Chien-Pao ex) assumes the retreating Chien-Pao took the Bench spot Mega Sharpedo "
            "left; the opponent's Professor's Research printings are not shown (first listed printing used)",
  ambiguous=AMB + AMB_CV + AMB_MS,
  draws={0: []}, vpatch=pop_tails,
  notes="Global 7 = his 4th turn. Hand after global 5: Parasol Lady, Lillie, two Wartortle, Cyrus; draws Lucky Ice Pop -> 6. Global 6: "
        "Water to Carvanha, Carvanha -> Mega Sharpedo ex (Elegant Cape 190 -> 220), Chien-Pao 100 retreats (one of its two Water), "
        "Sharpedo promoted, Turbo Shark 70 - Ice Face 40 = 30 (Eiscue 80 -> 50) and a zone Water to the benched Chien-Pao (2 Water by "
        "163 s). Opponent hand 4 + 1 - Sharpedo = 4. Move (global 7 section): Lucky Ice Pop 180-188 heals Eiscue 50 -> 70, tails, "
        "discarded (coin patch), Water to the benched 2nd Eiscue (@1) 197-198, Ram 203-205 (Sharpedo 220 -> 170)."),
]
