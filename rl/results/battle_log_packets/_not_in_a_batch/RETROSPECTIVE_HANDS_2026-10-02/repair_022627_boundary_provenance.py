"""Qualify supported composite boundary states after independent Sol inspection."""
import hashlib
import json
import shutil
from pathlib import Path

BATCH=Path(__file__).resolve().parent
P=BATCH/'20260908_022627000'
SAVE=P/'before_independent_boundary_repair'
assert not SAVE.exists()
SAVE.mkdir()
names=['TURN_LEDGER.json','HAND_SUPPLEMENT.json','REVIEW_SUPPLEMENT.md','UNCERTAINTIES.json','SUBMISSION_AFTER_ASTRA_REPAIR.json']
for name in names:
    shutil.copy2(P/name,SAVE/name)

def read(name):
    return json.loads((P/name).read_text(encoding='utf-8-sig'))

def write(name,data):
    (P/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')

evidence=read('TURN_EVIDENCE.json')
frames={f['evidence_id']:f for f in evidence['frames']}
ledger=read('TURN_LEDGER.json')
specific={
    7:{'observations':[
        {'id':'F0304.00','phase':'Before Entrap in owner7','observed':'Skorupi Active60/D1; Mega Absol Bench170/E0.'},
        {'id':'F0339.30','phase':'Opponent8 after evolution and normal attachment, during Giant Cape reveal','observed':'Drapion Bench130/D1; Mega Absol Active120 with Darkness attached; Giant Cape reveal.'}],
       'derived_fields':{
           'opponent.active.name_and_position':'Mega Absol becomes Active through recorded Entrap after304;339.3 is later corroboration, not the exact end7 position image.',
           'opponent.active.hp_now_damage':'End7 HP120 and50damage derive from170 minus recorded Entrap50; later339.3 shows120 before Cape bonus resolves.',
           'opponent.active.attached_energy':'End7 E0 uses pre-Entrap Mega E0 at304 and no owner7 attachment to it; opponent8 Darkness belongs to the later turn and is not imported backward.',
           'opponent.active.tool_and_hp_max':'End7 has no Tool and maximum170; the Giant Cape play/+20 belongs to opponent8.',
           'opponent.bench_in_position_order':'Skorupi60/D1 is direct at304 while Active; its Bench placement at end7 follows the recorded Entrap switch.339.3 shows later evolution to Drapion, not end7 Skorupi.'}},
    9:{'observations':[
        {'id':'F0394.00','phase':'Opponent10 after first Deino bench','observed':'Drapion Active80/D1; Mega Absol Bench140/D1; Deino60 already Bench2.'}],
       'derived_fields':{
           'opponent.active.name_position_hp_energy':'Earlier end9 Drapion Active80/D1 combines recorded Entrap/switch chronology with394 later corroboration;394 is not an exact end9 still.',
           'opponent.bench_in_position_order':'End9 Mega Absol Bench140/D1 is corroborated later. First Deino is excluded from end9 because its recorded bench play occurs in opponent10; its absence is chronological reconstruction, not direct observation at394.'}},
    15:{'observations':[
        {'id':'F0602.00','phase':'Before owner15 Entrap, second Hypno Psychic attachment in flight','observed':'Drapion Active80/D3; Mega Absol Bench60/D1; Hydreigon Bench150/E0.'},
        {'id':'R0640.00','phase':'Opponent16 after second Deino bench, promotion and Roar','observed':'Hydreigon Active120/D3; Mega Absol Bench2 10/E0; Drapion Bench1 80/D3; second Deino Bench3 60/E0.'}],
       'derived_fields':{
           'opponent.active.name_and_position':'End15 Mega Absol Active is derived from recorded Entrap selecting it; neither602 nor640 directly shows that boundary position.',
           'opponent.active.hp_now_damage':'End15 Absol10 derives from60 at602 minus recorded Entrap50;640 corroborates10 after opponent16 retreat.',
           'opponent.active.attached_energy':'End15 AbsolD1 is visible before the switch at602 and remains until its opponent16 retreat payment;640 E0 is the later paid-retreat state, not end15.',
           'opponent.bench_drapion':'Drapion80/D3 is source-observed at602 Active and640 Bench; end15 Bench1 follows the Entrap switch.',
           'opponent.bench_hydreigon':'End15 Hydreigon150/E0 is observed before Entrap at602, with no intervening owner15 action affecting it.640 shows the later promotion/attachment/Roar120/D3 state.',
           'opponent.bench_membership':'Second Deino is excluded at end15 from recorded opponent16 bench chronology;640 includes it and is not an earlier absence image.'}},
    17:{'observations':[
        {'id':'F0681.00','phase':'Owner17 before Boost Dash','observed':'Hydreigon140/E0; Comfey50/P1 after the attachment.'}],
       'derived_fields':{
           'opponent.active.hp_now_damage':'End17 Hydreigon70 derives from140 at681 minus recorded Boost Dash70.681 directly supports140, not70; no uninspected682 endpoint is adopted as direct proof.',
           'owner.comfey.attached_energy':'ComfeyP1 is directly visible at681 before the attack and retained at the derived end17 boundary.'}},
}

def attribute_basis(row_number,phase):
    target='start' if phase=='board_at_start' else 'end'
    return {
        'identity_and_position':{'basis':'Source-observed identities; positions at this '+target+' boundary are derived from native states and recorded switch, bench, evolution and knockout chronology. A pooled reference is not proof that every listed card occupies this position in every cited image.'},
        'hp_now_and_damage':{'basis':'Boundary values combine readable native HP, recorded damage/healing/knockout events and accepted play account. When an anchor precedes an attack or follows a later turn, these values are derived for the represented boundary, not direct HP readings from that anchor.'},
        'hp_max':{'basis':'Printed source card maximum plus source-supported Tool bonus, as specified in hp_max_basis. A maximum modified by a Tool is derived from the printed values.'},
        'attached_energy':{'basis':'Typed native Energy endpoints plus recorded generation, attachments, transfers and retreat payments. The represented boundary can differ from the cited later/pre-input anchor; attachment input times and payment inputs remain qualified in plays_in_order.'},
        'tool':{'basis':'Named source Tool reveal/attachment and recorded removal chronology; boundary Tool state can be derived from the before/after observations.'},
        'special_conditions_and_active_effects':{'basis':'Recorded source applications, visible markers, printed conditions and duration/expiry chronology, evaluated at this represented boundary. No hidden event or card identity reconstructed.'},
        'represented_turn':row_number,'represented_phase':target,
    }

def refs_in(value):
    result=[]
    if isinstance(value,dict):
        for key,item in value.items():
            if key=='evidence_ids' and isinstance(item,list):
                result.extend(item)
            else:
                result.extend(refs_in(item))
    elif isinstance(value,list):
        for item in value:
            result.extend(refs_in(item))
    return result

for row in ledger['turns']:
    for phase in ['board_at_start','board_after']:
        board=row[phase]
        board['submitted_phase_preserved']=board.get('phase')
        board['phase']='Composite source-derived '+('start' if phase=='board_at_start' else 'end')+' boundary; native anchor phases are separate from the represented state.'
        board['boundary_basis']='Source-native observations reconciled with recorded actions and the inherited accepted play account. This is not a claim that one cited still directly shows the entire exact boundary. No recording gap or hidden card identity is reconstructed.'
        board['native_anchor_inventory']=[{'evidence_id':ref,'requested_source_seconds':frames[ref].get('requested_source_seconds'),'actual_frame_seconds_if_measured':frames[ref].get('actual_frame_seconds_if_measured'),'phase_limit':'Pooled source anchor; may precede the ending action or include later-turn actions. Exact phase is explicitly identified below for consequential cross-turn cases.'} for ref in dict.fromkeys(refs_in(board)) if ref in frames]
        if phase=='board_after' and row['turn_number'] in specific:
            board['specific_boundary_derivations']=specific[row['turn_number']]
        for side in ['owner','opponent']:
            subset=board[side]
            subset['submitted_status_preserved']=subset.get('status')
            subset['status']='inferred'
            subset['boundary_basis']='Composite boundary subset: direct observations and source-supported chronology are distinguished in each Pokémon attribute_basis and any specific_boundary_derivations.'
            subset['limit_reason']='Selected references can be from before resolution or from a later turn; they are source anchors, not a single exact boundary image.'
            for pokemon in [subset.get('active')]+(subset.get('bench_in_position_order') or []):
                if not isinstance(pokemon,dict):
                    continue
                pokemon['submitted_status_preserved']=pokemon.get('status')
                pokemon['status']='inferred'
                pokemon['attribute_basis']=attribute_basis(row['turn_number'],phase)
                pokemon['limit_reason']='Composite boundary attributes. Read source-observed anchor phases and source-derived boundary values separately; exact simultaneous native boundary observation is not asserted.'
    row['turn_evidence_ids']=list(dict.fromkeys((row.get('turn_evidence_ids') or [])+refs_in(row)))
ledger['boundary_provenance_repair']={'check':str(BATCH/'independent_ladder'/P.name/'SOURCE_CHECKS.json'),'board_objects_audited':36,'numeric_card_values_changed':False,'phase_and_attribute_qualifications_added':True,'specific_cross_turn_examples':[7,9,15,17],'whole_packet_repair_acceptance':'pending'}

hand=read('HAND_SUPPLEMENT.json')
rows={row['turn_number']:row for row in hand['target_rows']}
for turn,added in [(3,[103.0,105.0]),(5,[174.0])]:
    row=rows[turn]
    original=list(row['native_capture_times'])
    row['dense_and_initial_capture_times_preserved']=original
    row['native_capture_times']=sorted(set(original+added))
    lo,hi=row['draw_end_bracket']
    row['later_offset_candidates']=[{'requested_source_seconds':time,'evidence_id':f'F{time:07.2f}','actual_frame_seconds_if_measured':frames[f'F{time:07.2f}'].get('actual_frame_seconds_if_measured'),'offset_after_draw_bracket_seconds':[time-hi,time-lo],'phase':'Post-first-play view; hand may already have changed. This is not an unchanged intact starting-hand image.'} for time in added]
old_phrase='Retreat precedes +3 and evolution precedes +6'
new_phrase='Native593 is pre-switch with Cape Raticate still Active;596 is post-switch with Hypno evolution in progress'

def replace_stale(value):
    if isinstance(value,str):
        return value.replace(old_phrase,new_phrase)
    if isinstance(value,list):
        return [replace_stale(item) for item in value]
    if isinstance(value,dict):
        return {key:replace_stale(item) for key,item in value.items()}
    return value

hand=replace_stale(hand)
ledger=replace_stale(ledger)
write('HAND_SUPPLEMENT.json',hand)
write('TURN_LEDGER.json',ledger)
text=(P/'REVIEW_SUPPLEMENT.md').read_text(encoding='utf-8-sig')
old='Start snapshots include normal generation after the draw or failed draw; end snapshots precede next-turn generation.'
new='The represented start/end boundaries are composite source-derived states, with direct native observations and recorded action chronology kept separate. Selected anchor frames can precede attacks or include subsequent-turn actions; they do not directly show every boundary attribute simultaneously. TURN_LEDGER records per-Pokémon attribute_basis, each anchor inventory and explicit cross-turn derivations for end7,9,15,17. Energy Zone boundary values also keep their generation/attachment derivation limits.'
assert old in text
text=text.replace(old,new)
text+='\nIndependent boundary qualification: End7 uses304 before Entrap and339.3 during opponent8; end9 uses394 after Deino was already Benched; end15 uses602 before Entrap and640 after opponent16 development; end17 Hydreigon70 derives from681 HP140 minus recorded Boost Dash70. Those are supported represented boundary values, not direct readings of a single cited still. Turn15 hand timing now distinguishes593 pre-switch from596 post-switch/evolution. Retained103/105/174 candidate times are listed as post-play offset views, separately from the initial hand anchors.\n'
(P/'REVIEW_SUPPLEMENT.md').write_text(text,encoding='utf-8')
uncertain=read('UNCERTAINTIES.json')
uncertain['independent_boundary_qualifications']={'board_objects':36,'specific_end_cases':specific,'hand_timing_correction':new_phrase,'added_existing_offset_candidates':{'turn3':[103,105],'turn5':[174]},'new_video_reads':0,'new_extraction':0}
write('UNCERTAINTIES.json',uncertain)
submission=read('SUBMISSION_AFTER_ASTRA_REPAIR.json')
submission['independent_boundary_repair']={'preserved_previous_submission':str(SAVE/'SUBMISSION_AFTER_ASTRA_REPAIR.json'),'modified_file_sha256':{name:hashlib.sha256((P/name).read_bytes()).hexdigest() for name in names[:4]},'whole_packet_repair_acceptance':'pending'}
write('SUBMISSION_AFTER_BOUNDARY_REPAIR.json',submission)
print(json.dumps({'repaired':P.name,'board_objects_qualified':36,'card_values_changed':False,'new_images':0,'new_video_reads':0,'independent_repair_acceptance':'pending'}))
