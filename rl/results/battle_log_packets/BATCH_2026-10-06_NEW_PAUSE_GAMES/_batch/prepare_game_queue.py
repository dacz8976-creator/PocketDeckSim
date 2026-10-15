"""Stage only lead-accepted human results; live saving remains a separate verified action."""
import json
from datetime import datetime,timezone
from pathlib import Path
from batch_packet_scope import game_packets, result_value
B=Path(__file__).resolve().parent
selected=json.loads((B/'OWNER_CONTEXT.json').read_text(encoding='utf-8'))['selected_sources']
deck_defs=json.loads((B/'NEW_DECK_ENTRIES.json').read_text(encoding='utf-8'))['decks']
qr_by_source={d['source_video']:d for d in deck_defs}
edited_path=B/'EDITED_DECK_ENTRY.json'
edited_defs=json.loads(edited_path.read_text(encoding='utf-8'))['decks'] if edited_path.exists() else []
edited_by_game={(d['source_video'],d['game_number_in_source']):d for d in edited_defs}
accepted=[];excluded=[];pending=[]
# Explicit opponent messages, including710s in game2 of the multi-game source.
confirmed_concessions={('20261004_215749000_iOS.MP4',1),('20261005_031138000_iOS.MP4',1),('20261005_034953000_iOS.MP4',1),('20261006_012927000_iOS.MP4',2),('20261006_012140000_iOS.MP4',1)}
qualified_candidates={
    '20261004_214518000_iOS.MP4':'20261004_213625000_iOS.MP4',
    '20261004_214731000_iOS.MP4':'20261004_213625000_iOS.MP4',
    '20261005_034229000_iOS.MP4':'20261005_033529000_iOS.MP4',
    '20261006_012140000_iOS.MP4':'20261005_183108000_iOS.MP4',
}
def read(p,name):
    path=p/name
    return json.loads(path.read_text(encoding='utf-8-sig')) if path.exists() else {}
def board_names(turns,player):
    names=[]
    for t in turns:
        for key in ['board_at_start','board_after']:
            board=t.get(key,{}).get(player,{})
            mons=[board.get('active')]+board.get('bench_in_position_order',[])
            for mon in mons:
                name=mon.get('name') if isinstance(mon,dict) else None
                if name and str(name).strip().lower() not in {'none','empty','visibly_empty','null'} and name not in names:names.append(name)
    return names
for name in selected:
    p=B/Path(name).stem;lead=read(p,'LEAD_ACCEPTANCE.json')
    if not lead.get('accepted'):
        pending.append({'source_video':name,'reason':'Full source review, independent check or root acceptance unfinished.'});continue
    source_packet=p
    units=game_packets(source_packet)
    for game_number,p in enumerate(units,1):
        assert read(p,'LEAD_ACCEPTANCE.json').get('accepted') is True, str(p)
        source=read(p,'SOURCE.json');summary=read(p,'SUMMARY.json');game=read(p,'PAUSE_GAME.json');deck=read(p,'DECK_USED.json')
        auto_seen=any(summary.get(key) is True for key in ['auto_control_observed','auto_option_seen','auto_control_seen','auto_control_visible'])
        computer_label=summary.get('computer_battle') is True or 'computer' in str(summary.get('classification',summary.get('mode',''))).lower()
        if auto_seen or computer_label:
            excluded.append({'source_video':name,'game_number_in_source':game_number,'game_count_in_source':len(units),'game_id':game.get('game_id'),'packet':str(p),'reason':'Computer battle under owner Auto-control rule; locally reviewed only.'});continue
        turns=read(p,'TURN_LEDGER.json').get('turns',[])
        result=result_value(summary)
        assert result in ['win','loss'],(name,result)
        outcome=game.get('outcome',{})
        outcome_text=outcome.get('basis',str(outcome)) if isinstance(outcome,dict) else str(outcome)
        opponent=summary.get('opponent',game.get('opponent')) or (outcome.get('opponent') if isinstance(outcome,dict) else None)
        assert opponent, (name,'Missing source-established opponent')
        concession=(name,game_number) in confirmed_concessions and result=='win'
        first=('first' if turns[0].get('who_played')=='owner' else 'second') if turns and turns[0].get('turn_number')==1 else None
        if name=='20261004_214518000_iOS.MP4':first='first' # Explicit final result55s, independently checked.
        qr=qr_by_source.get(name) if game_number==1 else None
        edited=edited_by_game.get((name,game_number))
        exact_deck=qr or edited
        candidate=qr_by_source.get(qualified_candidates.get(name)) if not qr and game_number==1 else None
        own_core=summary.get('owner_visible_core',summary.get('visible_deck_core',board_names(turns,'owner')))
        if not own_core and not turns:
            own_core=[game.get('opening',{}).get('selected_active',{}).get('name')]
            own_core=[n for n in own_core if n]
        notes=[f'Source: {name}.',f'Game {game_number} of {len(units)} in this source; game ID: {game.get("game_id")}.',f'Review packet: {p.as_posix()}.',f'Opponent: {opponent}.',
            f'Result evidence: {outcome_text}.',f'Recorded turns: {len(turns)}.']
        if qr:notes.append('Filmed QR version continuously bound by source review; newly prepared live deck entry still awaits saved readback.')
        elif edited:notes.append('Exact20 version established by the continuous filmed edit and final saved list, independently accepted with this game. Separate filmed-edit definition prepared; no revised QR was filmed and live deck saving still awaits readback.')
        else:notes.append('Exact 20-card game version is unverified; preserve the packet visible core and qualified earlier QR candidate rather than claim a proven deck version.')
        if not turns:notes.append('Setup-only Victory: zero turns and zero damage. Connection warning visible; exact termination cause unknown.')
        notes.append('Full hand/turn/board evidence and recording limits retained in the packet. No owner fun or competition ratings supplied.')
        accepted.append({'source_video':name,'source_sha256':source['sha256'],'game_id':game.get('game_id'),'game_number_in_source':game_number,'game_count_in_source':len(units),'packet':str(p),
            'date':read(p,'RECORDING_METADATA.json').get('match_date_local'),'opponent':opponent,
            'owner_result':result,'artifact_result_choice':'concession' if concession else result,'went':first,
            'turn_count':len(turns),'visible_owner_core':own_core,'visible_opponent_core':summary.get('opponent_visible_core',board_names(turns,'opponent')),
            'prepared_QR_deck_id':qr['id'] if qr else None,'prepared_QR_deck_name':qr['deck_name'] if qr else None,
            'prepared_deck_id':exact_deck['id'] if exact_deck else None,'prepared_deck_name':exact_deck['deck_name'] if exact_deck else None,
            'exact_deck_evidence_type':'filmed_QR' if qr else 'continuous_filmed_edit' if edited else None,
            'qualified_candidate_QR_deck_id':candidate['id'] if candidate else None,
            'qualified_candidate_QR_deck_name':candidate['deck_name'] if candidate else None,
            'candidate_basis':'Same visible core and earlier filmed QR; the gap between sources leaves unrecorded deck edits unknown.' if candidate else None,
            'exact_game_deck_binding':bool(exact_deck),'deck_selection_note':'Source-bound filmed QR' if qr else 'Source-bound continuous filmed edit and final saved20-card list' if edited else 'Needs a qualified candidate choice; exact version remains uncertain.',
            'source_outcome':outcome,'note':' '.join(notes),'fun_rating':None,'competition_rating':None,'consistency_rating':None,'playability_rating':None,
            'external_saved':False,'duplicate_check_required_before_save':True,'duplicate_identity_fields':['source_video','game_number_in_source','game_id'],'review_accepted':True})
doc={'prepared_utc':datetime.now(timezone.utc).isoformat(),'destination':'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd',
    'scope':'Lead-accepted human results only. No live save is claimed. Recheck current artifact by exact source filename immediately before each save. For a multi-game filename, compare game number and game ID too; the same filename may legitimately supply distinct battles.',
    'accepted_game_entries':accepted,'excluded_computer_sources':excluded,'review_pending_sources':pending}
(B/'PREPARED_GAME_QUEUE.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'accepted_human_entries':len(accepted),'excluded_computer_sources':len(excluded),'review_pending':len(pending)}))
