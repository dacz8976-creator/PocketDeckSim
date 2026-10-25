from v2_helpers import P, B
D = 'v2deck_4fa967805c'; G = '20261021_030939000_SR'
CV = 'Carvanha B4 034'; MSH = 'Mega Sharpedo ex B4 035'; WL = 'Wailord B1 057'; PB = 'Poké Ball P-A 005'; CC = 'Copycat B1 225'
EC = 'Elegant Cape B3b 065'; WA = 'Wallace B3b 068'
SL = 'Slugma A2 025'
AP = "opponent's list unknown; opponent's hand size from the visible plays"


def evolve_active(v):
    """Wallace's random evolution as the review shows it: Active Carvanha -> Mega Sharpedo ex 190 (native 77 s)."""
    v['me']['board'][0] = B(MSH, 190, behind=[CV])


POS = [
P(G, 2, 1, [0, 0],
  dict(hand=[CC, EC, WA, PB, WL], disc=[], dene='', board=[B(CV, 50)], ko=0),
  dict(hand_count=4, disc=['Poké Ball A2b 111', 'Poké Ball A2b 111'], dene='', board=[B(SL, 70)], ko=0, zone='R'),
  ['Play:Poké Ball', 'Place:Carvanha@1', 'Play:Wallace', 'ChooseRandomEvolutionTarget{in_play_idx:0,energy_type:Water}',
   'Attach:1Water@0 zone', 'Attack:Turbo Shark'],
  D, None,
  approx=AP + "; the opponent's first Poké Ball on global turn 1 put a hidden card into the hand (counted +1); the second found "
            "nothing (no +1); the opponent's Poké Ball printing is not shown, the printing cards.py lists first is used; the "
            "opponent's next Energy (Fire) is the Energy type the review shows for the opponent on global turn 1",
  ambiguous=['Opponent Slugma printing chosen by HP (70) and attack title (Flare); A2 025 is the only match'],
  draws={0: [CV], 2: []}, vpatch=evolve_active,
  notes="Global 2 = his 1st turn (he went second). 'Deck and opening': opening five Copycat, Elegant Cape, Carvanha, Wallace, Poke "
        "Ball; Carvanha Active, empty Bench -> 4 in hand. Table row 60-63: draw Wailord -> 5. Opponent: lone Slugma 70 (Flare 20), "
        "empty Bench; rows 42-59: draw (hidden), Poke Ball #1 fetched a card-back (+1), Poke Ball #2 'no cards in the deck that can be "
        "the target' (+0); no Bench, no Energy. Opp hand: 5 - 1 = 4, draw 5, Poke Ball 5, Poke Ball 4. 'Fire is shown as its Energy "
        "type' (row 42-47) -> zone R. His move, rows 64-88 in time order: Poke Ball (Carvanha, ~67 s), Carvanha benched (right Bench "
        "slot in the game; @1, the lowest empty slot, here), Wallace on the Active Carvanha -> Mega Sharpedo ex 190 (native 74.5-77 "
        "s), Water to the Active (native 81 s), Turbo Shark 90 (row 85-88). The engine's single-option bench attach after Turbo Shark "
        "('Attach:1Water@1 fx') is applied by the tool and is not in force; the opponent conceded right after the damage (row "
        "89-91). Wallace's chance step: draws {2: []} (nothing to the hand) and the vpatch puts Mega Sharpedo ex on Carvanha; "
        "ChooseRandomEvolutionTarget label from scratch/b3/t_wallace.py."),
]
