import json, subprocess, sys
from pathlib import Path
P=Path(__file__).resolve().parent
def read(p,n):return json.loads((p/n).read_text(encoding='utf-8-sig'))
def write(p,n,v):(p/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n' if isinstance(v,(dict,list)) else v,encoding='utf-8')
def refs(*ts):return ['f'+f'{t:07.2f}'.replace('.','_') for t in ts]
V=read(P,'SOURCE.json')['video_basename'];H=read(P,'SOURCE.json')['sha256']
edits=[]
def entry(lo,hi,before,after,changes,evidence,obs):
    edits.append({'order':len(edits)+1,'source_interval_seconds':[lo,hi],'source_video':V,'displayed_deck_count_before':before,'displayed_deck_count_after':after,'changes_by_semantic_variant':changes,'evidence_ids':refs(*evidence),'observation':obs,'input_timing_limit':'UI/reveal interval establishes the change; exact touch time and ordering inside multi-change intervals remain unknown.'})
def change(name,delta):return {'name_and_variant':name,'count_delta':delta}
entry(422,428,20,19,[change('Silvally [Brave Buddies]',-1)],[422,426,428],'Original deck20; ordinary Brave Buddies quantity falls from2 to1.')
entry(428,442,19,19,[change('Silvally [Brave Buddies]',-1),change('Silvally [Gold Breaker]',1)],[428,440,442,444],'Type: Null/related-card browsing precedes replacement. Gold Breaker face at440 is unselected;442 top deck has one Gold Breaker, no original Brave Buddies, count19. Order of add/remove within interval unknown.')
entry(444,460,19,20,[change('Silvally [Brave Buddies]',1)],[446,450,458,460],'Related-art browsing;458 explicitly shows alternate Brave Buddies50+ selected1/2.460 deck20 contains one Gold Breaker and one Brave Buddies.')
entry(478,498,20,19,[change('Persian [Shadow Claw]',-1)],[478,482,494,498],'Shiny Shadow Claw printing changes selected1/1 to0/1.498 completed deck19 retains the other ordinary Shadow Claw Persian.')
entry(530,536,19,21,[change('Team Rocket’s Persian [Dangerous Rogue]',2)],[532,534,536],'Dangerous Rogue card0/2 before addition, selected2/2 at536; deck21. Both original Meowth and remaining Shadow Claw Persian still visible.')
entry(536,538,21,19,[change('Meowth [Carefree Steps / Feelin’ Fine]',-1),change('Meowth [Pay Day]',-1)],[536,538],'Both original Meowth slots removed from deck row, with remaining ordinary Persian and both TR Persian still visible. Relative removal order inside interval unknown.')
entry(538,540,19,18,[change('Persian [Shadow Claw]',-1)],[538,540],'Last ordinary Persian disappears; two Dangerous Rogue remain.')
entry(546,548,18,19,[change('Team Rocket’s Meowth [Scratch]',1)],[546,548],'First Scratch Meowth added, selected1/2 and deck19.')
entry(550,552,19,20,[change('Team Rocket’s Meowth [Scratch]',1)],[550,552,554],'Second Scratch Meowth added, selected2/2 and deck20. Temporary blank row slot during animation is not asserted as a trainer removal.')
entry(560,562,20,18,[change('Terapagos ex [Prism Impact]',-2)],[558,560,562,564],'Both Terapagos slots disappear from the deck row; deck18. Scroll still shows both Type: Null and Gold Breaker/Brave Buddies pair.')
entry(578,580,18,19,[change('Soothing Shore',1)],[578,580,582],'Soothing Shore unselected then selected1/2, count19.')
entry(586,588,19,20,[change('Soothing Shore',1)],[586,588],'Selected2/2; two Soothing Shore in final trainer row, count20.')
deck=read(P/'game_02','DECK_USED.json')
ledger={'schema':'pause-games/deck-edit-v1','source_video':V,'source_sha256':H,'source_interval_seconds':[420,622],'initial_deck_proof':'DECK_USED.json source QR semantic20, continuously returned to New deck6 editor after game1','new_qr_observed':False,'edits':edits,'inspection_intervals_without_semantic_change':[{'interval':[430,440],'content':'Type: Null and related Silvally inspection'},{'interval':[462,478],'content':'Meowth/Persian variant inspection'},{'interval':[498,530],'content':'Persian/Meowth inspection and Persian filter'},{'interval':[542,546],'content':'Meowth filter'},{'interval':[554,560],'content':'Deck-row scroll'},{'interval':[564,578],'content':'Deck-row scroll and Stadium filter'},{'interval':[602,620],'content':'Supporter filter/collection scroll; included Research/Copycat quantities and deck20 remain unchanged'}],'unchanged_semantic_counts_supported_by_continuity':{'Snorlax ex':1,'Type: Null [Quick Blow]':2,'Poké Ball':2,'Lucky Ice Pop':2,'Field Blower':1,'Professor’s Research':2,'Cyrus':1,'Copycat':1},'unchanged_trainer_evidence_ids':refs(536,554,558,566,588,608,618),'final_source_counts_by_name_and_variant':deck['source_counts_by_name_and_variant'],'final_card_count':20,'final_list_status':'exact_semantic20_observed_edited_source_bound','final_energy_configuration':['Darkness'],'energy_edits':[{'interval':[590,592],'observation':'Grass, Darkness and Metal configured initially.','evidence_ids':refs(590,592)},{'interval':[592,598],'observation':'Energy dialog selection changes;594 warning states type not included in deck;596 temporarily shows Water alone selected. Exact intervening button sequence is not asserted.','evidence_ids':refs(594,596,598)},{'interval':[598,600],'observation':'Dialog closes; saved-deck page shows Darkness alone.','evidence_ids':refs(600)},{'interval':[620,622],'observation':'Final New deck6 page20/20 Darkness only; continuous Save and event queue selection into second game.','evidence_ids':refs(620,622)}],'final_binding_evidence_ids':refs(588,590,600,618,620,622,630,644,654),'limits':['Semantic versions and counts established by original exact QR plus filmed edits, printed rule names, quantities, deck rows and final count. Exact within-cluster touch order remains unknown.','New semantic IDs require registry mapping; none guessed.','No new QR or live Pause Games list observed. Exact artwork is not asserted for all cards.']}
write(P,'DECK_EDIT_LEDGER.json',ledger)
# Clear prose with the same observations already reviewed in native source frames.
write(P,'REVIEW.md',f'''# Source review: two games

The original source is preserved. Full review covers 0–719.001667 seconds: QR and deck selection, all 11 turns of game 1, results, the continuous deck-edit interlude, all 2 turns of game 2, Victory and the filmed ending. Embedded recording metadata establishes October 5 as the local match date.

Game 1: Dacz8976 goes second against ElPapa and loses. The original five cards are Poké Ball, Cyrus, Poké Ball, Meowth Carefree Steps and Persian Shadow Claw. Meowth uses Feelin’ Fine twice. Type: Null evolves to Brave Buddies Silvally; Pay Day Meowth evolves to Persian. Garchomp evolves through Rare Candy, then receives Fighting and Wally’s Colorless Energy. Land Crush knocks out Meowth and Persian for one point each. Field Blower removes Protective Poncho. Rainbow Cave regenerates the owner’s current Energy as Metal. Lucky Ice Pop heals Terapagos 10 and returns on heads. Terapagos retreats by discarding Grass and Metal; its Bench state has zero Energy. Snorlax replaces it and receives Metal. Happiny’s Chubby Cheer +20 and Cynthia +50 produce final Land Crush 190. Snorlax reaches HP 0, is removed and awards two points. The UI displays its three-point cap, then Defeat. Terminal owner Active is empty.

Game 2: Dacz8976 goes first against たこ and wins by concession. Opening: Team Rocket’s Persian, Poké Ball, Snorlax ex, Copycat and Lucky Ice Pop. Snorlax is Active. Normal draw is Gold Breaker Silvally. Two Poké Balls find Team Rocket’s Meowth and Type: Null. Copycat draws, in order, Poké Ball, Lucky Ice Pop, Team Rocket’s Meowth and Cyrus. Two Meowth and Type: Null fill Bench. Owner ends with Lucky Ice Pop and Cyrus, without Energy or attack. Opponent uses Research and Order Pad, whose tails produces no search, then concedes. Victory shows 2 turns and 0/0 points.

The game 2 exact semantic 20 is established by continuous filmed edits of the original QR-bound list, named quantity and deck-row changes, final 20/20, Darkness-only Save and continuous queue selection. DECK_EDIT_LEDGER.json preserves transient Water selection and unknown within-cluster touch order. No new QR is claimed.

TURN_LEDGER.json retains each turn, ordered actions, named arrivals, both boards and Energy Zones. TURN_EVIDENCE.json retains native evidence and exact crop bounds. Turn 9 opponent fan transitions are not forced to match inferred play arithmetic: completed fan 3 at 294 and fan 2 at 334/339 are separate observations. Hidden cards and remote inputs remain unknown. No complete discard window was filmed. No live Pause Games exact-list snapshot or external save is claimed. Independent acceptance remains pending for both packets.
''')
write(P/'game_02','REVIEW.md','''# Game 2 review

This is the second game in 20261006_012927000_iOS.MP4, source-local 622–719.001667 seconds. Opening, all 2 turns, concession and Victory are covered. Dacz8976 goes first against たこ and wins by explicit opponent concession at 710. Victory at 718 shows 2 turns and 0/0 points.

The deck is New deck 6 after the continuous 420–622 edit interval, with Darkness only. Parent DECK_EDIT_LEDGER.json establishes a distinct edited semantic 20; no new QR is claimed. The five-card hand at 644 precedes Snorlax placement at 646. Normal draw is Silvally Gold Breaker. First Poké Ball finds Team Rocket’s Meowth, placed right Bench. Copycat shuffles remaining cards and draws Poké Ball, Lucky Ice Pop, Team Rocket’s Meowth and Cyrus in order. Second Meowth goes left Bench; second Poké Ball finds Type: Null, placed middle Bench. Owner ends with Lucky Ice Pop and Cyrus, with no first-turn Energy. Opponent’s hidden draw, Research arrivals, Order Pad tails and concession are separate. No search follows tails. No attack or Energy attachment is observed; Lightning remains available at terminal.

No in-battle Auto control or full discard window is observed. Hidden opponent identities remain unknown. Worker claims neither a live exact-list snapshot nor external save. Independent acceptance is pending. Parent carries whole-source coverage and the edit ledger.
''')
validator=P.parent/'validate_packet.py'
for p in (P,P/'game_02'):
    r=subprocess.run([sys.executable,str(validator),str(p)],capture_output=True,text=True,encoding='utf-8')
    receipt=json.loads(r.stdout);write(p,'STRUCTURAL_VALIDATION.json',receipt)
    print(json.dumps(receipt,ensure_ascii=False))
