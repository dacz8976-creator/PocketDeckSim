import json,hashlib,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
p=Path(__file__).resolve().parent.parent;o=p/'independent_sol'
names=['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
hashes=lambda:{n:hashlib.sha256((p/n).read_bytes()).hexdigest() for n in names}
before=hashes()
primary=json.loads((p/'REVIEW_PACKET_HASHES.json').read_text(encoding='utf-8'))
assert before=={f['file']:f['sha256'] for f in primary['files']},'Primary frozen hashes differ'
documents={n:json.loads((p/n).read_text(encoding='utf-8')) for n in names if n.endswith('.json')}
l=documents['TURN_LEDGER.json'];e=documents['TURN_EVIDENCE.json'];g=documents['PAUSE_GAME.json']
assert [t['turn_number'] for t in l['turns']]==list(range(1,17))
source_sha='d0a221cd236c620f467bbf34ad8078fd59c72323a7dca71a4af344f0489c6c7f'
assert l['source_sha256']==e['source_sha256']==g['sources'][0]['sha256']==source_sha
copycat=l['turns'][0]['draws_and_searches'][1]['cards_in_reveal_order']
assert [(x['name'],x['timestamp_seconds']) for x in copycat]==[('Rocky Helmet',58),('Professor’s Research',58.5),('Poké Ball',59.5),('Dragonair',60.5)]
assert l['turns'][2]['timing']['first_voluntary_move_seconds']>=119
assert [x['timestamp_seconds'] for x in l['turns'][2]['draws_and_searches'][1]['cards_in_reveal_order']]==[126,127]
assert 'Supporter' in json.dumps(l['turns'][10]['plays_in_order'])
assert l['turns'][10]['timing']['before_end_action_seconds']<=430
assert g['outcome']['owner_points']==2 and g['outcome']['opponent_points']==3 and g['outcome']['turns_played']==16
for t in l['turns']:
 for key in ['board_at_start','board_after']:
  for who in ['owner','opponent']:
   side=t[key][who]
   for c in ([side['active']] if side['active'] else [])+side['bench_in_position_order']:
    assert c['hp_max']-c['hp_now']==c['damage']
    assert sum(c['attached_energy']['by_type'].values())==c['attached_energy']['total']
validator=p.parents[1]/'BATCH_2026-10-11_NEW_PAUSE_GAMES/validate_packet.py'
r=subprocess.run([sys.executable,str(validator),str(p)],capture_output=True,text=True,encoding='utf-8')
(o/'VALIDATOR_FINAL.json').write_text(r.stdout,encoding='utf-8')
assert r.returncode==0,r.stdout+r.stderr
after=hashes();assert before==after,'Inputs changed during final validation'
receipt={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'reviewer':'/root/check_newest_030351','model':'gpt-6.1-sol','reasoning_effort':'high','source_video':'20261013_030351000_iOS.MP4','source_sha256':source_sha,'accepted':True,'required_repairs':[],'checked_file_sha256':after,'checked_files':names,'input_files_stable_during_final_validation':True,'structural_validator':'VALIDATOR_FINAL.json','bounded_independent_check_report':'SOURCE_CHECKS.md','rejected_inputs_receipt':'REJECTED_INPUT_RECEIPT.json','scope':'Read all eight final files and bounded native source checks of opening, ordinary T11 first action/hand/count/warning, draw/search order, fan counts, discard, consequential HP/Energy/points and terminal outcome. No second full video pass.','capture_status':'complete_with_recording_limits','limitations':['Full-battle coverage is primary16-turn account reconciled against all files, with selected source checks, not independently repeated full pass.','Initial live26deck catalog lacks QR; exact20 semantic filmed list is independently decoded; later saved live-list supplement remains lead task.','Hidden opponent identities, unavailable periodic discard views, qualified hand frames and exact printing/artwork/rarity remain recorded limits.','Requested seek seconds remain approximate; actual frame PTS unmeasured.'],'lead_acceptance':False}
receipt['checked_input_sha256']=after
(o/'CORRECTION_RECHECK.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(receipt,ensure_ascii=False,indent=2))
