from v2_helpers import P, B
D = 'v2deck_589bb9927a'; G = '20261023_215109000_SR'
SQ = 'Squirtle P-A 033'; OR = 'Oricorio A3 066'; EI = 'Eiscue B1 080'; WT = 'Wartortle B1a 018'; MB = 'Mega Blastoise ex B1a 020'
PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"; LI = 'Lillie A3 155'; CC = 'Copycat B1 225'; LP = 'Lucky Ice Pop B2 145'
SS = 'Soothing Shore B4 154'; CY = 'Cyrus A2 150'; PL = 'Parasol Lady B3 152'
DK = 'Darkrai ex A2 110'; BO = 'Bombirdier B3 115'; ZU = 'Zorua A4a 049'; ZX = 'Zoroark ex B3 106'; GC = 'Giant Cape A2 147'
NE = 'Deceptive Needle B4 148'; OPB = 'Poké Ball A2b 111'; OCC = 'Copycat B1 225'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
AMB = ['Opponent Darkrai ex printing chosen by HP (140) and Ability title (Nightmare Aura); A2 110, A2 187, A2 202, A4b 245, A4b 378 '
       'and P-A 042 match',
       'Opponent Bombirdier printing chosen by HP (70); B3 115 and B3 234 match',
       'Opponent Zorua printing chosen by HP (60) only (its attack was not shown); A4a 049, B2b 043, B2b 102, B3 105, B3 174 and P-A 105 '
       'match',
       'Opponent Giant Cape printing not shown; A2 147, A4b 320 and A4b 321 match',
       'Opponent Trainer printings in the discard not shown: Poké Ball A2b 111 used (P-A 005 also matches), Copycat B1 225 used '
       '(B1 270 also matches)']
AMB_ZX = ['Opponent Zoroark ex printing chosen by HP (150) only (its attack was not yet shown); B3 106, B3 186, B3 199 and B4 230 '
          'match']
SHORE = {"card": SS, "owner": 0}


def pop_tails(v):
    # Lucky Ice Pop: heals 20 on the Active Oricorio (30 -> 50); coin tails, the Pop goes to the discard
    v['me']['board'][0]['hp'] = 50
    v['me']['discard'] = list(v['me']['discard']) + [LP]


POS = [
P(G, 3, 2, [0, 0],
  dict(hand=[PL, LP, SS, WT, CY], disc=[], dene='', board=[B(OR, 50), B(EI, 80)], ko=0),
  dict(hand_count=3, disc=[OPB, OCC], dene='', board=[B(DK, 160, 'D', tool=GC), B(BO, 70), B(ZU, 60)], ko=0),
  ['Play:Soothing Shore', 'Attach:1Water@0 zone', 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's hand (3) counts its global-2 Copycat as drawing 4 (his hand then held 4) and its Poke Ball as +1 "
            "(Bombirdier was benched from it); the opponent's Trainer printings (Poke Ball, Copycat) are not shown, the first listed are used",
  ambiguous=AMB,
  notes="Global 3 = his 2nd turn (he went first). Global 1 line: Oricorio Active, Eiscue benched, ends with a 4-card hand (Parasol "
        "Lady, Lucky Ice Pop, Soothing Shore, Wartortle); global 3 line: draws Cyrus -> 5. Global 2: Poke Ball, Bombirdier benched, Giant "
        "Cape on Darkrai ex (160), Copycat, Zorua benched, Darkness to Darkrai, Nightmare Aura 20 -> Oricorio 50. Opponent hand: 5 - "
        "Darkrai = 4, draw 5, Poke Ball (-1 +1) 5, Bombirdier 4, Cape 3, Copycat (-1, redraw 4 = his hand) 4, Zorua 3. Move (global 3 "
        "line): Soothing Shore 106-109, Water to Oricorio 110-112, no attack."),
P(G, 5, 3, [0, 0],
  dict(hand=[PL, LP, WT, CY, CC], disc=[], dene='', board=[B(OR, 30, 'W'), B(EI, 80)], ko=0),
  dict(hand_count=1, disc=[OPB, OCC], dene='D',
       board=[B(BO, 70, 'D', tool=NE), B(DK, 160, '', tool=GC), B(ZX, 150, behind=[ZU]), B(ZU, 60)], ko=0),
  ['Play:Lucky Ice Pop', 'Attach:1Water@1 zone', 'EndTurn'],
  D, None, stadium=SHORE,
  approx=AP + "; the opponent's Bench order (Darkrai ex, Zoroark ex, Zorua) assumes Darkrai took the Bench spot Bombirdier left and "
            "the 2nd Zorua the next free spot; the opponent's Trainer printings (Poke Ball, Copycat) are not shown, the first listed are used",
  ambiguous=AMB + AMB_ZX,
  draws={0: []}, vpatch=pop_tails,
  notes="Global 5 = his 3rd turn. Hand after global 3: Parasol Lady, Lucky Ice Pop, Wartortle, Cyrus; draws Copycat -> 5. Oricorio: "
        "Shore end of global 3 50 -> 70; global 4 Dark Cutter 30 -> 40, Needle 10 -> 30; one Water. Global 4: Needle on benched "
        "Bombirdier, Zorua -> Zoroark ex, 2nd Zorua benched, Darkrai retreats (its one Darkness) to Bombirdier, Darkness to Bombirdier. "
        "Opponent hand 3 + 1 - Needle - Zoroark ex - Zorua = 1. Move (global 5 line): Lucky Ice Pop 161-165 heals Oricorio 30 -> 50, "
        "coin tails (Pop discarded: draws {0: []} and the coin patch sets Oricorio 50 and the Pop in the discard), Water to benched "
        "Eiscue 170-173, ends (declines the Supporter)."),
P(G, 7, 4, [0, 0],
  dict(hand=[PL, WT, WT, CY, CC], disc=[LP], dene='', board=[B(OR, 10, 'W'), B(EI, 80, 'W')], ko=0),
  dict(hand_count=4, disc=[OPB, OCC, OCC, OPB], dene='D',
       board=[B(BO, 70, 'D', tool=NE), B(DK, 160, 'D', tool=GC), B(ZX, 150, behind=[ZU]), B(ZU, 60)], ko=0),
  ['Attach:1Water@1 zone', 'Play:Copycat', 'Place:Squirtle@2', 'Retreat:1', 'Attack:Ram'],
  D, None, stadium=SHORE,
  approx=AP + "; the opponent's global-6 Poke Ball is counted +1 (a hidden Basic kept in hand, per the review) and its Copycat as "
            "drawing 4 (his hand then held 4); the opponent's Bench order as on the previous turn; the opponent's Trainer printings "
            "are not shown, the first listed are used",
  ambiguous=AMB + AMB_ZX,
  draws={1: ['-' + PL, '-' + WT, '-' + WT, '-' + CY, CC, SQ, WT, MB]},
  notes="Global 7 = his 4th turn. Hand after global 5: Parasol Lady, Wartortle, Cyrus, Copycat; draws Wartortle -> 5. Oricorio: Shore "
        "50 -> 70 end of global 5; global 6 Nightmare Aura 20 -> 50, Dark Cutter 30 -> 20, Needle 10 -> 10. Opponent global 6: Copycat "
        "(redraws 4 = his hand), Poke Ball (hidden Basic, not benched), Darkness to benched Darkrai. Opponent hand 1 + 1 - 1 -> 4, Poke "
        "Ball 4; his Copycat draws exactly 4 (Copycat, Squirtle, Wartortle, Mega Blastoise ex). Move (global 7 line, in order): Water to "
        "benched Eiscue 222, Copycat 225 (Parasol Lady, two Wartortle, Cyrus shuffled away), Squirtle benched 235-237 (lowest empty "
        "slot @2), Oricorio retreats paying its Water 248-250 (Eiscue @1 comes in), Ram 254-256 (Bombirdier 70 -> 20)."),
]
