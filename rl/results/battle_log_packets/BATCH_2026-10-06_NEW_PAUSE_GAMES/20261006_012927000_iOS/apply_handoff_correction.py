import copy,json,sys,subprocess
from pathlib import Path
from PIL import Image
P=Path(__file__).resolve().parent
def rd(p,n):return json.loads((p/n).read_text(encoding='utf-8'))
def wr(p,n,v):(p/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n' if isinstance(v,(dict,list)) else v,encoding='utf-8')
def ref(t):return 'f'+f'{t:07.2f}'.replace('.','_')
for p in [P,P/'game_02']:
    ledger=rd(p,'TURN_LEDGER.json')
    for row in ledger['turns']:
        for play in row['plays_in_order']:
            play['input_interval_seconds']=None
            play['input_timing_limit']='Exact remote input unavailable.' if row['who_played']=='opponent' and play['kind']!='replacement_selection' else 'Exact touch time was not measured; cited frame locates observed selection/display/resolution only.'
            play['display_or_resolution_timestamp_seconds']=play['timestamp_seconds']
    if p==P:
        row=ledger['turns'][-1]
        for a in row['automatic_events_in_order']:
            if a['kind']=='removal':a.update({'timestamp_seconds':393,'evidence_ids':[ref(393)],'basis':'First retained frame with visibly empty owner Active; Snorlax now in discard top preview.'})
        row['automatic_events_in_order'].insert(2,{'kind':'removal_animation','target':'Snorlax ex','timestamp_seconds':392,'evidence_ids':[ref(392)],'basis':'Snorlax still shrinking in Active; not yet an empty position.'})
        b=row['board_after'];b['phase']='Terminal composite: last readable settled board393.5; point award/display396 and Defeat398 separately establish outcome. HP and Energy are not read from blurred overlays.'
        b['evidence_ids']=[ref(393),ref(393.5),ref(396)]
        for owner in ['owner','opponent']:
            side=b[owner];side['evidence_ids']=[ref(393.5)];side['energy_zone']['evidence_ids']=[ref(393.5)]
            side['points_evidence_ids']=[ref(396)] if owner=='opponent' else [ref(393.5)]
            for mon in [side['active']]+side['bench_in_position_order']:mon['evidence_ids']=[ref(393.5)]
        b['owner']['active']['evidence_ids']=[ref(393),ref(393.5)]
        b['opponent']['energy_zone']['next']={'type':'Water','count':1,'available':False}
        b['opponent']['energy_zone']['limit_reason']=None
        row['owner_hand_end']['evidence_ids']=[ref(393.5)]
        row['turn_evidence_ids'] +=[ref(393),ref(393.5)]
    else:
        row=ledger['turns'][0];row['timing']['first_voluntary_move_seconds']=657
        row['timing']['first_voluntary_input_interval_seconds']=[656,657]
        a=row['plays_in_order'][0]
        a.update({'timestamp_seconds':657,'input_interval_seconds':[656,657],'input_timing_limit':'Intact five-card hand656, Ball consumed and handfour657. Exact touch bounded by those frames.','display_or_resolution_timestamp_seconds':658,'card_reveal_timestamp_seconds':658,'search_reveal_timestamp_seconds':660,'evidence_ids':[ref(656),ref(657),ref(658),ref(660)],'result':'Poké Ball consumed656–657, face-up Ball display658, Team Rocket’s Meowth search reveal660, then hand arrival/placement.'})
        d=row['draws_and_searches'][1];d.update({'timestamp_seconds':660,'evidence_ids':[ref(660),ref(662)],'reveal_timestamp_seconds':660,'hand_arrival_evidence_ids':[ref(662)]});d['cards_in_reveal_order'][0].update({'timestamp_seconds':660,'evidence_ids':[ref(660)]})
        row['turn_evidence_ids'] +=[ref(656),ref(657),ref(658),ref(660)]
        ev=rd(p,'TURN_EVIDENCE.json')
        for f in ev['frames']:
            if f.get('turn_number')==1 and f.get('who_played')=='owner':
                f['before_first_play']=f['requested_source_seconds']<657
                if f['requested_source_seconds']>=657 and not f['selected_for_start_hand']:f['suitability_or_limit']='Ball already consumed by657; cannot be an intact start hand.'
        wr(p,'TURN_EVIDENCE.json',ev)
    wr(p,'TURN_LEDGER.json',ledger)
ev=rd(P,'TURN_EVIDENCE.json');ids={f['evidence_id'] for f in ev['frames']}
for t in [393,393.5,397]:
    if ref(t) in ids:continue
    item=copy.deepcopy(ev['frames'][0]);item.update({'evidence_id':ref(t),'role':'terminal_phase_reconciliation','turn_number':11,'who_played':'opponent','requested_source_seconds':t,'draw_animation_end_seconds':None,'offset_after_draw_seconds':None,'full_frame_path':'native/'+f't{t:07.2f}.jpg','selected_for_start_hand':False,'before_first_play':False,'unzoomed':True if t==393.5 else None,'hand_spread':None,'observation':'393 first empty Active;393.5 last readable board;397 separate point award overlay.','suitability_or_limit':'Do not read HP or Energy from blurred point/result overlays.'})
    for key,bounds,suffix in [('bottom_crop',[0,2025,1170,2532],'bottom'),('top_crop',[0,0,1170,700],'top')]:
        path='crops/'+ref(t)+'_'+suffix+'.png'
        with Image.open(P/item['full_frame_path']) as im:im.crop(bounds).save(P/path)
        item[key]={'path':path,'pixel_bounds_x0_y0_x1_y1':bounds}
    ev['frames'].append(item)
ev['frames'].sort(key=lambda f:f['requested_source_seconds']);wr(P,'TURN_EVIDENCE.json',ev)
cor=rd(P,'CORRECTION_LEDGER.json');cor['corrections'] +=[{'field':'game2 first Poké Ball phase','initial_read':'First play658, search662','resolved_read':'Ball consumed656–657, displayed658, TR Meowth revealed660;657 offset is postconsumption','evidence_ids':[ref(656),ref(657),ref(658),ref(660)],'status':'resolved'},{'field':'final Snorlax removal phase','initial_read':'392 fully removed','resolved_read':'392 removal animation;393 first empty Active;393.5 readable board,396 award2,398 Defeat separate','evidence_ids':[ref(392),ref(393),ref(393.5),ref(396),ref(398)],'status':'resolved'}];wr(P,'CORRECTION_LEDGER.json',cor)
for name in ['REVIEW.md','HANDOFF.md']:
    path=P/name;text=path.read_text(encoding='utf-8');text=text.replace('is removed and awards two points','is removed by 393 and awards two points').replace('removed392','removal animation392, empty Active393, readable board393.5').replace('first Poké Ball658–664','first Poké Ball consumed656–657, displayed658, search660–664');path.write_text(text,encoding='utf-8')
for p in [P,P/'game_02']:
    receipt=json.loads(subprocess.run([sys.executable,str(P.parent/'validate_packet.py'),str(p)],capture_output=True,text=True,encoding='utf-8').stdout);wr(p,'STRUCTURAL_VALIDATION.json',receipt);assert receipt['structural_pass'];print(json.dumps(receipt))
    worker=rd(p,'WORKER_VALIDATION.json');worker['post_handoff_corrections']={'structural_pass':True,'input_and_reveal_phases_separated':True,'game2_first_consumption_interval':[656,657],'last_readable_game1_board_seconds':393.5,'first_empty_owner_active_seconds':393};worker['native_frames']=len(rd(p,'TURN_EVIDENCE.json')['frames']);wr(p,'WORKER_VALIDATION.json',worker)
