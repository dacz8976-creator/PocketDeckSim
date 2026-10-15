import json,hashlib,datetime
from pathlib import Path
P=Path(__file__).resolve().parent
def get(n):return json.loads((P/n).read_text(encoding='utf8'))
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def N(t):return 'N'+f'{t:07.3f}'.replace('.','p')
L=get('TURN_LEDGER.json');E=get('TURN_EVIDENCE.json');G=get('PAUSE_GAME.json');U=get('UNCERTAINTIES.json')
opening_limit='A Horsea zoom is present at 26/27s and the right Research slot is clipped at the edge. Its visible name/art plus inspected setup continuity support the five named slots; no ideal unzoomed five-card pre-placement view is retained.'
G['opening']['status']='observed_with_recording_limits';G['opening']['limit_reason']=opening_limit
G['opening']['evidence_ids']=[N(26),N(27),N(30)]
G['limits'].append(opening_limit)
r=L['turns'][0]
r['timing'].update(start_seconds=45,draw_animation_end_seconds=44.5,first_voluntary_move_seconds=46,end_after_resolution_seconds=54)
r['plays_in_order'][0]['timestamp_seconds']=46;r['plays_in_order'][0]['evidence_ids']=[N(45),N(46),N(47)]
for key in ['hand_at_start','owner_hand_start']:
    h=r[key];h['evidence_ids']=[N(44),N(45)];h['status']='observed_with_recording_limits';h['basis']='native normal draw reveal plus exposed four-card selection view before Research leaves hand'
    h['limit_reason']='No unzoomed four-card pre-play view: 44s has drawn Rare Candy zoom; 45s has selected Research zoom; 46s is after Research leaves hand.'
    for c in h['cards_left_to_right']:c['evidence_ids']=[N(44),N(45)];c['basis']=h['basis']
r['limits'].append('T1 +1/+3/+6 candidates are all after Research starts. N044/N045 qualify the four-card pre-play hand; they do not meet the ideal unzoomed criterion.')
r=L['turns'][2]
for key in ['hand_at_start','owner_hand_start']:
    h=r[key];h['evidence_ids']=[N(88)];h['basis']='observed clear unzoomed native six-card hand at88s'
    for c in h['cards_left_to_right']:c['evidence_ids']=[N(88)]
r['timing']['start_seconds']=88
L['turns'][4]['draws_and_searches'][2]['hand_count_before']=5
L['turns'][4]['draws_and_searches'][2]['hand_count_after_supporter_consumption_before_shuffle']=4
L['turns'][4]['draws_and_searches'][2]['hand_count_after_shuffle_before_draw']=0
L['turns'][4]['plays_in_order'][2]['nested_events_in_order'].insert(0,{'event':'Copycat consumed','hand_count_before_play':5,'hand_count_after_consumption':4})
L['turns'][6]['timing']['first_voluntary_move_seconds']=233
L['turns'][6]['plays_in_order'][0]['timestamp_seconds']=233;L['turns'][6]['plays_in_order'][0]['evidence_ids']=[N(233),N(234)]
L['turns'][8]['plays_in_order'][1]['prompt_text']='End your turn? A Supporter card can be used'
L['turns'][8]['plays_in_order'][1]['response']='OK'
L['turns'][8]['plays_in_order'][1]['nested_events_in_order']=[{'event':'offered Supporter warning','source_seconds':309,'evidence_ids':[N(309)],'response':'OK confirms attack while declining to use a Supporter'},{'event':'Stormy Prison attack resolves','source_seconds':312,'evidence_ids':[N(312)]}]
L['turns'][5]['plays_in_order'][2]['timestamp_seconds']=212;L['turns'][5]['plays_in_order'][2]['evidence_ids']=['D212p000',N(214)]
# Energy records explicitly follow actual retained frame phase, independent of row owner.
def ez(current,next_type,eid,reason=None):
    return {'this_turn':{'type':current,'count':1 if current else 0,'available':bool(current)},'next':{'type':next_type,'count':1 if next_type else None,'available':False},'basis':'Observed large current token and small next symbol in cited boundary frame','evidence_ids':[eid],'limit_reason':reason}
boundaries={
1:((45,'N045p000',1,None,None,'Lightning','owner Research selection, after normal draw'),(54,'N054p000',1,None,None,'Lightning','owner end button, before turn2 generation')),
2:((60,'N060p000',2,None,'Lightning','Water','settled opponent turn2, after draw and generation, before first play'),(82,'N082p000',2,None,None,'Water','Crackly Toss resolved, before turn3')),
3:((88,'N088p000',3,'Water',None,'Water','settled owner turn3, after draw and Energy generation, before first play'),(107,'N107p000',3,None,None,'Water','owner end turn, before turn4 generation')),
4:((112,'D112p000',4,None,'Water','Lightning','settled opponent turn4 before evolution; reduced frame used only for board'),(132,'D132p000',4,None,None,'Lightning','Crackly Toss resolved; no effect; before turn5')),
5:((136,'N136p000',5,'Water',None,'Lightning','normal Poké Ball draw resolved; pre-play hand'),(190,'N190p000',6,None,'Lightning',None,'post-Pichu knockout and Dragonair promotion; next turn6 Energy is generating; small next token unreadable during glare')),
6:((194,'N194p000',6,None,'Lightning','Water','settled opponent turn6 before May'),(229,'N229p000',7,None,None,'Water','first Draco Meteor/KO resolved; turn7 banner before owner generation')),
7:((232,'N232p000',7,'Water',None,'Water','normal Hiking Trail draw/owner Energy generation before first play'),(270,'N270p000',8,None,None,'Water','attack, Stadium draw and checkups resolved; turn8 banner before opponent generation')),
8:((272,'N272p000',8,None,'Water','Lightning','opponent turn8 generation after normal draw, before attachment'),(301,'N301p000',9,None,None,'Lightning','second Draco Meteor, Horsea KO and Poison resolved; turn9 before owner normal draw')),
9:((304,'N304p000',9,'Water',None,'Lightning','settled owner turn9 normal draw and Energy generation'),(324,'N324p000',10,None,None,'Lightning','Dragonite knockout and Dratini replacement resolved; turn10 banner before generation')),
10:((328,'N328p000',10,None,'Lightning','Lightning','settled opponent turn10 before attachment'),(348,'N348p000',11,None,None,'Lightning','Slam two tails/zero damage resolved; turn11 banner before owner draw/generation')),
11:((351,'N351p000',11,'Water',None,'Lightning','owner turn11 normal draw and Energy generation resolved, no voluntary play'),(353,'N353p000',11,'Water',None,'Lightning','concession; no owner action; final battlefield'))
}
for row in L['turns']:
    n=row['turn_number']
    for key,values in zip(['board_at_start','board_after'],boundaries[n]):
        t,ref,display,oc,pc,pn,phase=values;b=row[key];b['turn_number_displayed']=display;b['phase']=phase;b['timestamp_seconds']=t;b['evidence_ids']=[ref]
        for player,current,nexttyp in [('owner',oc,'Water'),('opponent',pc,pn)]:
            b[player]['energy_zone']=ez(current,nexttyp,ref,'Small next icon is unreadable during generation glare.' if nexttyp is None else None);b[player]['evidence_ids']=[ref]
            for mon in [b[player]['active']]+b[player]['bench_in_position_order']:mon['evidence_ids']=[ref]
    row['timing']['start_seconds']=boundaries[n][0][0];row['timing']['end_after_resolution_seconds']=boundaries[n][1][0]
    row['turn_evidence_ids']=[boundaries[n][0][1],boundaries[n][1][1]]
    if n%2==0:
        row['hand_at_start']['count']=None;row['hand_at_start']['basis']='opponent faces hidden; exact acting-hand count not separately asserted'
        row['hand_at_start']['evidence_ids']=[boundaries[n][0][1]];row['hand_at_start']['limit_reason']='Required observed opponent fan counts are preserved independently at owner-turn starts. No arithmetic count substitutes for a fan.'
    if n==5:
        row['limits'].append('End boundary uses190s after Dragonair replacement; turn6 banner/generation has begun, but no opponent voluntary move yet. Small opponent next symbol remains unreadable until194s.')
for f in E['frames']:
    if f['evidence_id']==N(26):f['unzoomed']=False;f['suitability_or_limit']=opening_limit
    if f['evidence_id'] in [N(46),N(48),N(51)]:
        f['draw_animation_end_seconds']=44.5;f['offset_after_draw_seconds']=f['requested_source_seconds']-44.5;f['selected_for_start_hand']=False;f['before_first_play']=False
        f['role']='draw_relative_candidate';f['observation']='T1 candidate after Research has begun; three retained hand cards are visible before its two draws.';f['suitability_or_limit']='Not a pre-play hand; Research has left hand.'
    if f['evidence_id']==N(45):
        f.update(role='qualified_selected_preplay_hand',turn_number=1,who_played='owner',draw_animation_end_seconds=44.5,selected_for_start_hand=True,before_first_play=True,unzoomed=False,hand_spread=True,observation='Four-card hand before Research consumption, with selected Research zoom; combined with normal Rare Candy draw reveal N044.',suitability_or_limit='No ideal unzoomed pre-play hand view is retained.')
    if f['evidence_id']==N(89):
        f['selected_for_start_hand']=False;f['unzoomed']=False;f['suitability_or_limit']='Seadra selected with zoom; use clear unzoomed N088 instead.';f['role']='draw_relative_candidate'
    if f['evidence_id']==N(88):f.update(role='selected_preplay_hand',turn_number=3,who_played='owner',draw_animation_end_seconds=86,offset_after_draw_seconds=2,selected_for_start_hand=True,before_first_play=True,unzoomed=True,hand_spread=True,observation='Clear unzoomed six-card owner hand before first play.',suitability_or_limit=None)
    if f['evidence_id']==N(233):f['before_first_play']=False;f['suitability_or_limit']='Hiking Trail has left hand at the first play.'
E['scheduled_capture_limits'].append('T1 draw end about44.5s; retained46/48/51s are approximately+1.5/+3.5/+6.5 and all after Research begins. Four-card start uses explicitly qualified N044/N045 continuity.')
U['items'].extend([{'id':'opening_zoom','status':'recording_capture_limit','source_seconds':[26,27,30],'finding':opening_limit},{'id':'T1_hand_zoom','status':'recording_capture_limit','source_seconds':[44,45,46],'finding':L['turns'][0]['owner_hand_start']['limit_reason']}])
for n,d in [('TURN_LEDGER.json',L),('TURN_EVIDENCE.json',E),('PAUSE_GAME.json',G),('UNCERTAINTIES.json',U)]:put(n,d)
review='''# First visual review, awaiting independent acceptance

Source: 20261012_003458000_iOS.MP4. Reviewer: /root/pause_20261012_003458000_iOS, gpt-6.1-sol high. SHA-256: 399ef7e1be5545ca1284a7aedb9f6eea70abb5929ed7cbf2083d539dae64f413. SOURCE.json and ASSIGNMENT.json are preserved.

One continuous human match is recorded from the filmed deck QR and opponent search through all 11 turns and the opponent concession at 353-354 seconds. Dacz8976 wins against しじみ. Points are tied 2-2 when the opponent concedes. No Auto control is shown; the exact queue label is absent. The creation tag is 2026-10-12T00:34:58Z, which converts to October 11, 2026 at 19:34:58 CDT. The phone’s 7:34 display supports this local date and time.

The QR at 0 seconds exactly matches the freshly retrieved live Kingdra ex / Team Rocket’s Weezing ex code. DECK_USED.json saves the 20 log slots, including duplicates and the log’s variant labels, with Water Energy. QR membership is semantic; it does not establish artwork or rarity. Filmed hand names below come from exposed faces.

The five opening slots at 26-27 seconds are Horsea, Horsea, Copycat, Small Balloon and Professor’s Research, left to right. A Horsea zoom is present and the outer Research is clipped, so this is a qualified opening capture rather than an ideal unzoomed five-card view. The visible hand and inspected setup continuity support the names. The first, shiny Horsea is selected Active; the other, gold-art Horsea is benched. No redraw is shown.

| Turn | Player | Approximate source interval | Observed sequence |
|---|---|---|---|
| 1 | Owner | 41-55 s | Normal draw Rare Candy. Play Research, revealing Research then Seadra. End turn without Energy or attack. |
| 2 | Opponent | 55-83 s | Poké Ball with a hidden search result, bench Dratini, attach Lightning to Dratini, then Pichu’s Crackly Toss adds a second Lightning. |
| 3 | Owner | 83-108 s | Draw Weezing ex. Evolve Active Horsea to Seadra, attach Water, play Research revealing Weezing ex then Sabrina, attach Small Balloon to Seadra, end turn. |
| 4 | Opponent | 108-134 s | Evolve benched Dratini into Dragonair, attach Water, then Crackly Toss animates with no additional Energy or damage. Only Dragonair is benched; there is no eligible Basic target. |
| 5 | Owner | 134-185 s | Draw Poké Ball, search Koffing, bench it at right. Play Copycat, returning Rare Candy, two Weezing ex and Sabrina. Reveal Kingdra ex, Kingdra ex, Koffing, Sabrina and Weezing ex. Bench second Koffing in middle, evolve Active Seadra to Kingdra ex, attach second Water, then Stormy Prison knocks out Pichu. Owner leads 1-0. Dragonair is promoted. |
| 6 | Opponent | 185-229 s | May searches two hidden Pokémon and returns two hidden Pokémon. Attach Lightning to Dragonair, evolve it to Dragonite, bench Dratini, then Draco Meteor knocks out middle Koffing with 150 damage and damages right Koffing for 50, leaving 10 HP. Score 1-1. |
| 7 | Owner | 229-270 s | Draw Hiking Trail and play it. Evolve damaged right Koffing to Weezing ex at 90/140 HP; accept Boiler Smog, making Dragonite Poisoned and Burned. Attach Water to Horsea. Confirm Stormy Prison, accepting the offered Supporter warning and declining to use a Supporter. Deal 90 and impose the retreat block. Hiking Trail draws Rare Candy. Poison/Burn checkup deals 30, leaving Dragonite at 40 HP; Burn flips heads and clears. |
| 8 | Opponent | 270-300 s | Attach Water to Dratini. Draco Meteor puts 150 damage on Kingdra ex, leaving 20 HP, and 50 on Horsea, knocking it out. Opponent leads 2-1. Poison reduces Dragonite from 40 to 30 HP. |
| 9 | Owner | 300-324 s | Draw Rare Candy, attach Water to Weezing ex, confirm Stormy Prison after another offered Supporter warning. Dragonite is knocked out and points become 2-2. Dratini is promoted. |
| 10 | Opponent | 324-348 s | Attach Lightning to Dratini. Slam flips two tails at 342 s and displays zero damage at 346 s. Kingdra ex remains at 20 HP. |
| 11 | Owner | 348-355 s | Draw Weezing ex. Before any voluntary play, the opponent concedes at 353-354 s. |

The table maps to the 11 numbered TURN_LEDGER.json rows. Each row contains numbered voluntary actions, nested choices, individual draws/searches, both boards, points, Stadium, HP, typed Energy, Tools, conditions, bench positions and start/end Energy Zones. A boundary phase states when a turn banner or automatic generation has already begun; boundary fields are bound to the actual cited frame. The resolved Pichu replacement uses 190 s, when the next turn’s generation has begun. No opponent next-Energy identity is asserted during its glare.

Owner draw reveals are recorded individually: Rare Candy at 44 s; Research’s Research at 49 s and Seadra at 50 s; normal Weezing ex at 85 s; Research’s Weezing ex at 97 s and Sabrina at 98 s; normal Poké Ball at 136 s; searched Koffing at 140 s; Copycat’s five cards at 156/157/158/159/160 s; normal Hiking Trail at 232 s and its end draw Rare Candy at 262 s; normal Rare Candy at 302 s; normal Weezing ex at 350 s. Opponent searches and May returns stay hidden; later public plays do not identify their exact origin.

Ending hands reconcile without inventing card identities. T1 starts with four cards after the draw; Research uses one and draws two, leaving five. T3 starts with six; Seadra, Research and Small Balloon consume three and Research adds two, leaving five. T5 reaches five cards before Copycat; playing Copycat leaves four to shuffle, then five are drawn. Koffing and Kingdra consume two, leaving three. T7 starts with four; Hiking Trail and Weezing ex consume two, then the Stadium adds Rare Candy, leaving three. T9 adds a normal draw to those three, leaving four because attachments and attacks do not consume hand cards. T11 adds Weezing ex and ends at five. Final hand: Kingdra ex, Sabrina, Rare Candy, Rare Candy, Weezing ex.

Native owner-start opponent fan counts are 4/5/5/3/4/5 on T1/T3/T5/T7/T9/T11. They are read from distinct card-back edges in the top crops, separate from transaction arithmetic. Neither discard pile is opened anywhere in the footage. Face-up top discard cards do not establish a full pile inventory.

Capture limits are explicit. The opening has a zoom/edge limitation. T1 has no ideal unzoomed four-card pre-play frame: 44 s shows the drawn Rare Candy, 45 s shows the four-card hand with Research selected and zoomed, and 46 s is after Research leaves hand. T3 uses the clear unzoomed 88 s hand; 89 s has a Seadra zoom. T5 begins its Item play before the +1-second candidate, so the 136 s pre-play view is selected. T11 concession interrupts; later scheduled candidates are already post-concession. Reduced overview grids support action continuity only and never replace native hand captures.

Stormy Prison’s “Can’t retreat” at 260 s is the attack-effect notice, not a failed owner retreat. T4 Crackly Toss and T10 zero-heads Slam are preserved as no-effect actions. A win does not establish optimal strategy. The recording ends during the result transition rather than a full victory screen, but the explicit concession banner establishes the outcome. Independent acceptance, shared registration, external logging and archival remain pending lead work. No shared logs, external artifact, source location or simulator code were changed by this worker.
'''
(P/'REVIEW.md').write_text(review,encoding='utf8')
coverage='''# Source and capture coverage

One game, all 11 recorded turns, setup through concession and the final transition. The whole source was inspected using a bounded 4-second overview, 2-second opponent/action continuity frames and targeted native evidence. No second game or recording cut was found.

| Interval | Coverage |
|---|---|
| 0-20 s | Deck QR, opponent search and coin sequence |
| 20-41 s | Five-card opening, Active and Bench setup |
| 41-55 s | Turn 1 |
| 55-83 s | Turn 2 |
| 83-108 s | Turn 3 |
| 108-134 s | Turn 4 |
| 134-185 s | Turn 5, Copycat reveals and Pichu knockout |
| 185-229 s | Turn 6, Dragonite development and first Draco Meteor |
| 229-270 s | Turn 7, Weezing evolution, status effects and checkups |
| 270-300 s | Turn 8, second Draco Meteor and Horsea knockout |
| 300-324 s | Turn 9 and Dragonite knockout |
| 324-348 s | Turn 10 and two-tail Slam |
| 348-355 s | Turn 11 normal draw and opponent concession |
| 355-363.783 s | Result transition |

All owner normal draws, two Research sets, the Poké Ball search, all five Copycat reveals and the Hiking Trail end draw are named separately. Actions preserve the T4 no-effect attack, both offered Supporter warnings and T10 zero damage. Final hand and explicit concession are retained at native resolution. Both boards and Energy Zones use the actual evidence phase, including pre-generation empty states and replacement timing.

Normal draw ends approximately 44.5/86/136/232/303/351 s. Scheduled candidates: 46/48/51, 87/89/92, 137/139/142, 233/235/238, 304/306/309, 352/354/357 s. T1 offsets are approximately +1.5/+3.5/+6.5 s, all after Research begins. Qualified selected hand views: 44/45 continuity, 88, 136, 232, 304 and 351 s. Before ending action/attack/concession: 53, 106, 174, 254, 309 and 352 s. T1 and the five-card opening have explicit zoom limitations. T5 plays early; T11 is interrupted by concession.

Native frames are 1170×2532. Bottom crops are [0,2025,1170,2532]; top crops are [0,0,1170,600]. Every selected hand, ending hand and scheduled candidate has paired native crops. Reduced images are separately cataloged. No ideal unzoomed view is claimed when a zoom is present.

Inspected recording limits: exact queue label absent, opponent faces hidden, neither discard pile opened, QR artwork/rarity unknown, full result screen not reached. These are capture limits, not unreviewed intervals. First visual review is submitted; independent semantic acceptance is pending. The original source remains preserved.
'''
(P/'COVERAGE.md').write_text(coverage,encoding='utf8')
files=['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
put('FROZEN_FIRST_PASS_HASHES.json',{'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewer':'/root/pause_20261012_003458000_iOS','acceptance':'pending independent reviewer and lead','files':{n:hashlib.sha256((P/n).read_bytes()).hexdigest() for n in files},'source_sha256':G['sources'][0]['sha256']})
print('Repaired native phase alignment, hand qualifications, Copycat phases, warning and prose; refreshed frozen hashes.')
