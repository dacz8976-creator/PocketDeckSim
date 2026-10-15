import pathlib,json,hashlib,datetime
p=pathlib.Path(__file__).resolve().parent.parent;out=p/'independent_sol'
prior=json.loads((out/'CORRECTION_RECHECK_20261012T235549Z.json').read_text())
hashes={n:hashlib.sha256((p/n).read_bytes()).hexdigest() for n in prior['checked_input_sha256']}
assert hashes==json.loads((p/'REVIEW_PACKET_HASHES.json').read_text())['review_files_sha256']
assert {n for n,h in hashes.items() if prior['checked_input_sha256'][n]!=h}=={'SUMMARY.json','TURN_LEDGER.json'}
def diff(a,b,path=''):
    if type(a)!=type(b):return [(path,a,b)]
    if isinstance(a,dict):return sum((diff(a.get(k),b.get(k),path+'/'+k) for k in (a.keys()|b.keys())),[])
    if isinstance(a,list):
        if len(a)!=len(b):return [(path,a,b)]
        return sum((diff(x,y,path+'/'+str(i)) for i,(x,y) in enumerate(zip(a,b))),[])
    return [] if a==b else [(path,a,b)]
changes={n:diff(json.loads((p/'before_second_independent_repairs_20261012T235813Z'/n).read_text()),json.loads((p/n).read_text())) for n in ['SUMMARY.json','TURN_LEDGER.json']}
(out/'final_narrow_diff.json').write_text(json.dumps(changes,indent=2),encoding='utf8')
allowed=['/turns/2/board_at_start/owner/energy_zone/later_within_turn_observation','/turns/8/board_at_start/owner/energy_zone','/turns/18/plays_in_order/0','/turns/12/board_at_start/owner/energy_zone/later_within_turn_observation/next/visibility']
assert all(any(path.startswith(x) for x in allowed) for path,_,_ in changes['TURN_LEDGER.json'])
assert all(path.startswith('/second_independent_repairs') for path,_,_ in changes['SUMMARY.json'])
ledger=json.loads((p/'TURN_LEDGER.json').read_text())
for zone in [ledger['turns'][2]['board_at_start']['owner']['energy_zone']['later_within_turn_observation'],ledger['turns'][8]['board_at_start']['owner']['energy_zone']]:
    assert all(zone['next'][k] is None for k in ['type','count','available'])
    assert zone.get('limit_reason')
assert ledger['turns'][18]['plays_in_order'][0]['evidence_ids']==['f722_00','f732_00']
assert ledger['turns'][18]['hand_at_start']['evidence_ids']==['f722_00']
now=datetime.datetime.now(datetime.timezone.utc);stamp=now.strftime('%Y%m%dT%H%M%SZ')
result={'accepted':True,'reviewer':'/root/check_203719','checked_at_utc':now.isoformat(),'source_video':'20261012_203719000_iOS.MP4','source_sha256':'e85ac056e49ababe79fbd0388e8b132f3cc984a5deb445390a2f4df7b0137869','required_repairs':[],'accepted_input_sha256':hashes,'packet_unchanged_during_final_check':True,'scope':'Final bounded correction recheck, cumulative with the initial independent source audit and the dated second correction audit. No material repair remains in inspected acceptance scope.','checks_completed':['Only SUMMARY.json and TURN_LEDGER.json changed; their diffs are limited to the three requested narrow repairs plus supported T13 later-preview visibility metadata.','T3 later next marker at107.5 and T9 start next marker at358 now unknown with explicit native visibility limits. This agrees with the previously inspected retained and independently extracted views.','Native t0732.00.jpg visibly shows three Darkness on bench-right Kingambit. T19 action includes this later resulting-board proof while preserving f722_00 hand/start evidence and distinguishing action time from observation time.','Original R1/R2 and additional T17/T19/T21 hand repairs remain supported from the preceding correction audit.','All other six final file hashes are unchanged from the dated second audit.','Final eight-file hashes exactly match REVIEW_PACKET_HASHES.json.'],'preserved_rejection_receipts':['CHECK_RESULT.json','CORRECTION_RECHECK_20261012T235549Z.json'],'supporting_records':['INDEPENDENT_CHECK.md','CORRECTION_RECHECK_20261012T235549Z.md','final_narrow_diff.json'],'capture_status':'complete_with_recording_limits','recording_limits_retained':['Hidden opponent identities and overlap fan ranges.','Discard piles not opened.','Live Pause Games exact deck absent; verified filmed QR separately sourced.','T14 no-target trigger uncertain.','T20 effective retreat-cost explanation unfilmed.','Approximate source seeks and explicitly unavailable transient Energy preview views.'],'external_write_performed':False,'shared_registration_performed':False,'source_move_performed':False}
assert hashes=={n:hashlib.sha256((p/n).read_bytes()).hexdigest() for n in hashes}
data=json.dumps(result,indent=2)
(out/'CORRECTION_RECHECK.json').write_text(data,encoding='utf8')
(out/f'CORRECTION_RECHECK_ACCEPTED_{stamp}.json').write_text(data,encoding='utf8')
(out/'CORRECTION_RECHECK_ACCEPTED.md').write_text(f'''# Independent correction recheck accepted

Reviewer: /root/check_203719. Checked {now.isoformat()}. Source: 20261012_203719000_iOS.MP4. Source SHA-256: e85ac056e49ababe79fbd0388e8b132f3cc984a5deb445390a2f4df7b0137869.

The three remaining narrow repairs are supported. Turn 3 at 107.5 s and turn 9 at 358 s now keep their absent next Energy previews unknown, with explicit visibility limits. Turn 19 retains its empty start-hand frame at 722 s and separately cites the 732 s resulting board, which visibly shows three Darkness Energy on bench-right Kingambit. The packet distinguishes the approximate attachment action from the later observation.

Only SUMMARY.json and TURN_LEDGER.json changed after the dated second rejection. I checked their complete structural diffs; changes are limited to those repairs plus supported turn 13 later-preview visibility metadata. The other six file hashes remain unchanged. All eight final hashes match REVIEW_PACKET_HASHES.json and are frozen in the accepted CORRECTION_RECHECK.json, with no changes during this final check.

This acceptance is cumulative with the bounded source audit and the preceding correction audit, including native opening/action/hand views, all 42 start/end boundary Zone pairs, named owner draw/search reconciliation and the concession ending. The supported turn 13 hand and additional turn 17/19/21 timing corrections remain intact. No material repair remains in the inspected scope. Capture status remains complete_with_recording_limits. Source-hidden facts and the missing exact live-log list remain explicitly limited.

CHECK_RESULT.json and CORRECTION_RECHECK_20261012T235549Z.json preserve both rejected submissions. This independent acceptance does not perform root's shared registration, external game entry or archival work.
''',encoding='utf8')
print(json.dumps({'accepted':True,'required_repairs':[],'accepted_input_sha256':hashes,'dated_receipt':f'CORRECTION_RECHECK_ACCEPTED_{stamp}.json'},indent=2))
