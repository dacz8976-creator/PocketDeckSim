import json,copy
from pathlib import Path
from datetime import datetime,timezone
B=Path(__file__).resolve().parent
root=B.parents[2]
old=root/'Recording_QA/20260908_012720_v7_review/final_packet'
templates=root/'Review_Log/templates/pause_games'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,v):(B/n).write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf-8')
src=read(old/'SOURCE.json'); inherited=read(B/'INHERITED_TURNS.json'); receipt=read(B/'ROOT_SOURCE_VERIFICATION.json')
source={'video_basename':src['filename'],'sha256':src['sha256'].lower(),'source_json':str(old/'SOURCE.json')}
ref={'schema':'retrospective-source-reference-v1','source':source,'current_path':receipt['current_path'],'bytes':src['bytes'],'duration_seconds':src['duration_seconds'],'root_verification_receipt':str(B/'ROOT_SOURCE_VERIFICATION.json'),'verification_status':receipt['status'],'worker_duplicate_hash_reads':0,'accepted_review':str(old/'REVIEW.md'),'accepted_status':'Reviewed','accepted_outcome':'Owner win, displayed3-2, Victory','preservation':'Original source, historical accepted packet, shared events/index and external logs unchanged'}
save('SOURCE_REFERENCE.json',ref)
obs=read(B/'OBSERVATIONS.json') if (B/'OBSERVATIONS.json').exists() else {'status':'incomplete_review','opening':None,'turns':{}}
ledger=read(templates/'TURN_LEDGER.template.json'); row_template=ledger['turns'][0]
ledger.update(is_template=False,game_id=B.name,sources=[source],turns=[],limits=[])
for rec in inherited['rows']:
    t=rec['turn_number'];row=copy.deepcopy(row_template)
    row.update(turn_number=t,who_played='owner' if t%2==0 else 'opponent',source_video=src['filename'])
    row['accepted_prose_provenance']={'file':str(old/'REVIEW.md'),'line':rec['accepted_source_line'],'basis':rec['basis'],'verbatim_section':rec['verbatim_accepted_section']}
    row['limits']=['Fresh field capture incomplete until draw/action/boundary inspection is saved.']
    extra=obs['turns'].get(str(t),{})
    row.update(extra)
    ledger['turns'].append(row)
ledger['capture_status']=obs['status'];save('TURN_LEDGER.json',ledger)
game=read(templates/'PAUSE_GAME.template.json');game.update(is_template=False,game_id=B.name,review_date=datetime.now(timezone.utc).isoformat(),sources=[source],destination=None,deck_name='Historical Ogerpon / Whimsicott visible core',capture_status=obs['status'],battle_review_status='Reviewed; accepted full review preserved',outcome={'basis':'inherited_accepted_review','result':'owner_win','displayed_score':[3,2]},limits=obs.get('limits',[]),lead_checked=False)
if obs.get('opening'):game['opening']=obs['opening']
game['packet_files'].update(prose='REVIEW_SUPPLEMENT.md',coverage=str(old/'COVERAGE.md'))
save('PAUSE_GAME.json',game)
deck=read(templates/'DECK_USED.template.json');deck.update(is_template=False,game_id=B.name,sources=[source],deck_name_in_log=None,source_url=None,captured_at=None,log_list_version=None,cards_in_log_order=None,counts_by_name_and_variant=None,energy_configuration_from_log=None,actual_card_count=None,capture_source_text_or_image=str(B.parent/'DECK_LOG_CAPTURE.txt'),game_version_binding_basis='Selected historical ladder game; batch log snapshots contain Shark Tempo and Wailord decks only. No corresponding historical20-card list supplied.',conflicts_with_filmed_cards=None,exact_list_status='unavailable_historical_version',limit_reason='Current Pause Games snapshot does not provide this historical Ogerpon/Whimsicott20-card deck; no current list substituted.',visible_core=['Teal Mask Ogerpon ex','Cottonee','Whimsicott ex','Ariados','Spinarak'])
save('DECK_USED.json',deck)
hands={'schema':'retrospective-hand-supplement-v1','is_template':False,'game_id':B.name,'target_turn_numbers':[2,4,6,8,10,12],'sources':[source],'capture_status':obs['status'],'target_rows':[]}
for r in ledger['turns']:
    if r['who_played']=='owner':hands['target_rows'].append({k:r[k] for k in ['turn_number','timing','owner_hand_start','draws_and_searches','owner_hand_end','opponent_hand_at_owner_turn_start','limits']})
save('HAND_SUPPLEMENT.json',hands)
print('wrote packet scaffold',len(ledger['turns']))
