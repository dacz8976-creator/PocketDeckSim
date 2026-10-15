import json, hashlib, subprocess
from datetime import datetime, timezone
from pathlib import Path

p=Path(__file__).resolve().parent.parent
d=p/'independent_sol'
def read(n): return json.loads((p/n).read_text(encoding='utf-8-sig'))
f=read('REVIEW_PACKET_HASHES.json')
s=read('SOURCE.json')
expected_source='7394580c71facb269a7c6703e890ff1eb360ffd509875eb09d03343f43b4fe7a'
assert f['source_sha256']==s['sha256']==expected_source
hashes={n:hashlib.sha256((p/n).read_bytes()).hexdigest() for n in f['files']}
assert len(hashes)==8 and hashes==f['files']
old=json.loads((d/'CHECK_RESULT.json').read_text(encoding='utf-8'))
assert old['accepted'] is False
for n,h in old['checked_input_sha256'].items():
    assert hashlib.sha256((d/'rejected_original_8'/n).read_bytes()).hexdigest()==h
l=read('TURN_LEDGER.json');e=read('TURN_EVIDENCE.json')
cards=l['turns'][0]['draws_and_searches'][2]['cards_in_reveal_order']
assert [(c['name'],c['timestamp_seconds'],c['evidence_ids']) for c in cards]==[("Professor's Research",66.0,['n66_00']),("Professor's Research",67.0,['n67_00']),('Heavy Helmet',68.0,['n68_00']),('Lucky Ice Pop',68.5,['n68_50'])]
assert l['turns'][0]['draws_and_searches'][2]['timestamp_seconds']==66
t3=l['turns'][2]
assert t3['timing']['before_end_action_seconds']==167.5
assert t3['owner_hand_end']['evidence_ids']==['n167_50']
assert t3['owner_hand_end']['count']==5
assert 'n168_50' not in json.dumps(t3['board_after'])
assert 'n167_50' in json.dumps(t3['board_after'])
frames={x['evidence_id']:x for x in e['frames']}
assert frames['n167_50']['role']=='before_end_hand' and frames['n167_50']['unzoomed'] is True
assert frames['n168_50']['role']=='native_terminal_error' and frames['n168_50']['unzoomed'] is False
assert frames['n69_50']['role']=='native_post_Copycat_settled_hand'
assert 'clipped' in read('PAUSE_GAME.json')['opening']['cards_left_to_right'][0]['basis']
py=r'C:/Users/dacz8/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
v=p.parent.parent/'BATCH_2026-10-11_NEW_PAUSE_GAMES'/'validate_packet.py'
out=subprocess.run([py,'-X','utf8',str(v),str(p)],capture_output=True,text=True,encoding='utf-8',check=True)
validation=json.loads(out.stdout)
assert validation['structural_pass'] and validation['turn_rows']==3 and validation['issues']==[]
# Confirm there was no mutation during the correction check.
assert {n:hashlib.sha256((p/n).read_bytes()).hexdigest() for n in f['files']}==hashes
result={
 'accepted':True,
 'checked_utc':datetime.now(timezone.utc).isoformat(),
 'checker':'/root/check_remaining_015011',
 'review_model':'gpt-6.1-sol',
 'reasoning_effort':'high',
 'source_video':s['video_basename'],
 'source_sha256':expected_source,
 'checked_input_sha256':hashes,
 'checked_input_file_count':8,
 'frozen_utc':f['frozen_utc'],
 'stable_against_frozen_hashes':True,
 'required_repairs':[],
 'resolved_repairs':['R1','R2'],
 'scope':'Narrow R1/R2 correction recheck plus all eight current hashes and validator. Uses native frames directly viewed during prior bounded check; no second whole-source pass.',
 'prior_rejection':'independent_sol/CHECK_RESULT.json',
 'rejected_originals_preserved':True,
 'source_findings':[
  'R1 resolved consistently in revised prose, ledger and frame roles: first Research66.00, second67.00, Helmet68.00, Pop68.50. All are observed reveal sample anchors;69.50 is settledhand only.',
  'R2 resolved: final clear turn3 hand and board at167.50/n167_50, fivecards and unusedDarkness.168.50 explicitly terminalerror/blurred, not finalclear evidence.',
  'OpeningCopycat name-label clipping qualified; artwork binding corroborated by named43.50.',
  'Prior bounded-source findings remain valid: human vs coke, ownerfirst,3turns,0-0points,0damage, win for opponent-return failure; exact20 historical QR/log match with fresh_live_readback=false.',
  'Recording limits preserved. Local semantic acceptance does not establish current external log save/readback or archival.'
 ],
 'structural_validation':validation
}
(d/'CORRECTION_RECHECK.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'accepted':True,'required_repairs':[],'stable_eight':True,'validator':validation,'receipt':str(d/'CORRECTION_RECHECK.json')},indent=2))
