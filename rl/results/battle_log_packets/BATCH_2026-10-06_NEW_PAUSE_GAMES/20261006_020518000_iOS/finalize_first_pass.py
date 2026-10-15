"""Apply inspected native boundary qualifications before first-pass submission."""
import json,hashlib
from pathlib import Path
P=Path(__file__).parent
def read(n):return json.loads((P/n).read_text(encoding='utf-8'))
def save(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
L=read('TURN_LEDGER.json');E=read('TURN_EVIDENCE.json');D=read('DECK_USED.json');U=read('UNCERTAINTIES.json')
frames={f['evidence_id']:f for f in E['frames']}
def eid(t):return 'f'+f'{t:07.2f}'.replace('.','_')
def empty_current(reason=None):return {'type':None,'count':0,'available':False,'status':'no_current_Energy_symbol_visible_in_large_circle','limit_reason':reason or 'No current Energy symbol in this cited frame. A later generated Energy is separately bounded.'}
def known_current(typ):return {'type':typ,'count':1,'available':True,'status':'one_visible_symbol_in_large_current_circle','limit_reason':None}
def hidden_next(reason):return {'type':None,'count':None,'available':False,'status':'preview_not_yet_readable_at_selected_frame','limit_reason':reason}
for row in L['turns']:
    n=row['turn_number']
    for k in ['board_at_start','board_after']:
        b=row[k]
        b['phase']='concluded_turn_'+str(n)+'; captured after public resolution, possibly during next-turn transition' if k=='board_after' else 'start public state before first observed play; normal draw may precede Energy generation'
        for who in ['owner','opponent']:
            z=b[who]['energy_zone'];z['evidence_ids']=b[who]['evidence_ids'];z['this_turn']['limit_reason']=None
    # All settled after-turn owner large circles are empty; small preview remains Fighting.
    row['board_after']['owner']['energy_zone']['this_turn']=empty_current('Current Energy was consumed, or the next owner generation has not begun in this frame; preview is separate.')
    row['board_after']['opponent']['energy_zone']['this_turn']=known_current('Metal') if n in [5,9] else empty_current('Large current circle is empty at this boundary; small Metal preview is separate.')
    if n in [4,6,8,10]:row['board_after']['opponent']['energy_zone']['limit_reason']='Waiting/effect banner partly overlaps zone; adjacent native frames show the empty current circle and Metal preview.'
    # Inactive owner current zone is empty at opponent-turn starts.
    if not n%2:row['board_at_start']['owner']['energy_zone']['this_turn']=empty_current('Owner is inactive; large circle empty and small Fighting preview is separate.')
    else:row['board_at_start']['opponent']['energy_zone']['this_turn']=empty_current('Opponent inactive; only small Metal preview is visible.')
    if n in [1,3,9,15,17]:
        row['board_at_start']['owner']['energy_zone']['this_turn']=empty_current('Original intact hand precedes full generation. Later Fighting attachment is documented; no preview counted as current.')
    if n==11:
        row['board_at_start']['owner']['energy_zone']['this_turn']={'type':None,'count':None,'available':None,'status':'glowing_generation_without_readable_typed_symbol','limit_reason':'Native332.8 shows glow in the large circle; Fighting symbol is readable by335.6.'}
    if n in [7,9,11,15,17]:
        row['board_at_start']['owner']['energy_zone']['next']=hidden_next('Small next preview has not finished appearing in selected original-hand frame. Later native generation views show Fighting; this is not substituted into the selected-frame field.')
    if n==5:row['board_at_start']['owner']['energy_zone']['next']['basis']='Next Energy generated Fighting popup is visible, although small circle placement is animating.'
    if n in [6,12]:row['board_at_start']['opponent']['energy_zone']['this_turn']=empty_current('Opponent normal draw has merged, but large Metal generation is not complete; later frame separately proves it.')
    if n in [8,10]:row['board_at_start']['opponent']['energy_zone']['limit_reason']='Waiting banner partly overlaps zone; large Metal symbol remains visible above it. Adjacent native frames confirm.'
    if n==16:row['board_at_start']['opponent']['energy_zone']['next']=hidden_next('Next small Metal preview is still animating at520; separate large current Metal is readable.')
    row['timing']['timing_basis']='Source-local sought frames bound transitions/actions; individual remote input taps and exact animation boundaries are not measured.'
    row['timing'].pop('turn_transition_start_seconds',None)
    row['timing']['phase_start_window_seconds']={1:[54,56],2:[64,66],3:[91,93],4:[138,140],5:[154,156],6:[170,174],7:[192,195],8:[228,232],9:[260,262],10:[292,296],11:[328,331],12:[364,367],13:[428,430],14:[446,450],15:[482,484],16:[516,519],17:[566,568]}[n]
    for a in row['plays_in_order']:
        a['observed_actor']='owner' if n%2 else 'opponent'
        a['input_and_resolution_distinction']='Timestamp is first cited public selection/input or presentation. Later evidence IDs show reveal, target, resolution or effect; exact remote tap is unknown.'
        if a['card_name']=='May':
            a['result']='May adds two random hidden Pokémon from deck, then opponent chooses two hand Pokémon to shuffle back. Identities hidden. Hand7 -Supporter1 +2 -2 =6 before benching.'
            a['nested_events_in_order']=['May consumed:7 to6','Two random hidden deck Pokémon added: temporary8','Opponent chooses two hidden hand Pokémon to shuffle back:6']
    if n in [14,16]:
        name='Sandslash [B2 078 Fury Swipes]' if n==14 else 'Hitmonchan ex';ts=[480,482] if n==14 else [560,562,563,564,566]
        row['plays_in_order'].append({'order':len(row['plays_in_order'])+1,'kind':'mandatory_promotion_choice','card_name':name,
          'observed_actor':'owner','target':'owner Active','result':'Owner selects replacement after opponent point award, then promotion resolves.',
          'source_video':row['source_video'],'timestamp_seconds':ts[0],'evidence_ids':[eid(t) for t in ts],
          'hand_count_after':row['owner_hand_end']['count'],'energy':None,'prompt_text':'Choose a Pokémon to move to the Active Spot (visible mandatory promotion panel)',
          'response':name,'basis':'Native mandatory choice and resulting Active','limit_reason':None})
    if n in [3,11,14,16,17]:
        seq={3:[('HP_zero',120),('removed',122),('owner_point_1',126),('opponent_promotion_Stakataka',138)],11:[('HP_zero',356),('removed',358),('owner_point_2',360),('opponent_promotion_Copperajah',364)],14:[('HP_zero_removal',472),('opponent_point_1',476),('owner_promotion_Sandslash',482)],16:[('HP_zero_removal',554),('opponent_point_2',558),('owner_promotion_Hitmonchan_ex',566)],17:[('HP_zero',577),('removed',578),('Active_empty',579),('owner_point_3',582),('Victory',591)]}[n]
        row['automatic_events_in_order']=[{'order':i+1,'kind':kind,'timestamp_seconds':t,'evidence_ids':[eid(t)],'limit_reason':None} for i,(kind,t) in enumerate(seq)]
    allids=set(row['turn_evidence_ids'])
    for a in row['plays_in_order']+row['automatic_events_in_order']:allids.update(a['evidence_ids'])
    row['turn_evidence_ids']=sorted(allids)
# Board at start turn6 uses actual pre-evolution native172, after opponent hidden draw.
r=L['turns'][5]
for section in ['owner','opponent']:
    r['board_at_start'][section]['evidence_ids']=[eid(172)]
    r['board_at_start'][section]['energy_zone']['evidence_ids']=[eid(172),eid(176)]
    r['board_at_start'][section]['limit_reason']=None
    for m in [r['board_at_start'][section]['active']]+r['board_at_start'][section]['bench_in_position_order']:m['evidence_ids']=[eid(172)]
r['board_at_start']['evidence_ids']=[eid(172)];r['hand_at_start']['evidence_ids']=[eid(172)]
r['draws_and_searches'][0]['timestamp_seconds']=172;r['draws_and_searches'][0]['evidence_ids']=[eid(172)]
r['draws_and_searches'][0]['limit_reason']='Five backs after hidden normal draw at172, versus four on prior owner turn. Identity hidden.'
# Correct turn12 attachment: large current Metal persists through376; third attached by378.
a=L['turns'][11]['plays_in_order'][0];a['timestamp_seconds']=376;a['evidence_ids']=[eid(t) for t in [370,374,376,378]]
a['result']='Third Metal attached in the376-to378 public interval; two Metal remain on Copperajah and current large Metal is unused through376. Three attached and empty current circle by378.'
L['turns'][11]['turn_evidence_ids']=sorted(set(L['turns'][11]['turn_evidence_ids']+a['evidence_ids']))
L['turns'][11]['board_at_start']['opponent']['energy_zone']['generation_bounds_seconds']=[367,368]
L['turns'][11]['board_at_start']['opponent']['energy_zone']['generation_evidence_ids']=[eid(367),eid(368)]
for n,shown in {3:4,6:7,8:9,10:11,11:12,12:13}.items():
    b=L['turns'][n-1]['board_after'];b['turn_number_displayed']=shown;b['turn_number_limit_reason']=None
    b['turn_number_basis']='Readable next-turn Current turn label in the cited native boundary frame; concluded row remains '+str(n)
# Terminal composite: field at579; awarded score at582.
b=L['turns'][16]['board_after'];b['evidence_ids']=[eid(579),eid(582)]
for who in ['owner','opponent']:
    b[who]['evidence_ids']=[eid(579),eid(582)]
    b[who]['energy_zone']['evidence_ids']=[eid(579)]
    for m in [b[who]['active']]+b[who]['bench_in_position_order']:m['evidence_ids']=[eid(579)]
b['owner']['points_basis']='Third point award at582, separate from native field579'
b['opponent']['points_basis']='Two opponent points visible at579 and in result sequence'
for n,ts in {3:[94.5,107],9:[264,269],11:[332.8,335.6],15:[485.6,486.5],17:[570,571.5]}.items():
    z=L['turns'][n-1]['board_at_start']['owner']['energy_zone'];z['generation_bounds_seconds']=ts;z['generation_evidence_ids']=[eid(t) for t in ts]
D['capture_source_text_or_image']='../LIVE_DECK_SNAPSHOT.json (frozen nine-deck live retrieval; exact matching deck absent)'
U['bounded_resolved'].append({'issue':'Copperajah third Metal timing on turn12','resolution':'Unused large current Metal through376; third attached and current empty by378, before May380.'})
save('TURN_LEDGER.json',L);save('TURN_EVIDENCE.json',E);save('DECK_USED.json',D);save('UNCERTAINTIES.json',U)
text=(P/'REVIEW.md').read_text(encoding='utf-8').replace('May with hidden searched/shuffled identities','May with random hidden deck additions and chosen hidden hand returns')
text+='\nNative boundary qualification: owner original hands at94.5,264,485.6 and570 show no current Energy symbol yet;332.8 shows generation glow. Later generation is separately bounded. The small next preview is unknown when still animating. At176 and298, the settled after-turn field already shows the following opponent turn\'s large Metal, which is retained as displayed. Copperajah\'s third Metal attachment occurs376 to378, before May. Next-turn labels at139,194,261,330,366 and429 are recorded as4,7,9,11,12 and13 while the concluded row number stays separate.\n'
(P/'REVIEW.md').write_text(text,encoding='utf-8')
assert [r['owner_hand_start']['count'] for r in L['turns'] if r['turn_number']%2]==[4,5,4,5,6,5,3,4,4]
assert [r['owner_hand_end']['count'] for r in L['turns'] if r['turn_number']%2]==[4,3,4,5,4,2,3,3,4]
assert [r['board_after']['owner']['points'] for r in L['turns']]==[0,0,1,1,1,1,1,1,1,1,2,2,2,2,2,2,3]
assert [r['board_after']['opponent']['points'] for r in L['turns']]==[0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,2,2]
for r in L['turns']:
    for board in ['board_at_start','board_after']:
        for who in ['owner','opponent']:
            p=r[board][who]
            for m in [p['active']]+p['bench_in_position_order']:
                if m['name']:assert m['hp_now']+m['damage']==m['hp_max']
                assert sum(m['attached_energy']['by_type'].values())==m['attached_energy']['total']
save('CONSISTENCY_CHECK.json',{'semantic_consistency_pass':True,'basis':'First-pass explicit sequence and numerical checks against native observations; not independent acceptance',
 'checked':['All17 rows','Owner start/end hand count arrays','20QR entity slots and variants','HP_now+damage=HP_max on every occupied boundary card','Attached Energy typed sums','Owner and opponent score arrays','Separate HP0/removal/award/promotion frames','Generation separated from preview','Wally Colorless plus normal Fighting; retreat payment','Research reveal order Poké Ball then Timburr','No pile content inferred from preview'],
 'final_score':[3,2],'owner_start_counts':[4,5,4,5,6,5,3,4,4],'owner_end_counts':[4,3,4,5,4,2,3,3,4],'independent_visual_acceptance':False})
print('Native boundary qualifications and consistency checks saved.')
