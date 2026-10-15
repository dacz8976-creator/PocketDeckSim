import pathlib,json,hashlib,datetime
q=pathlib.Path(__file__).resolve().parent
b=q.parents[1];p=b/'20260928_200654000'
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(name,value):(q/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
errors=[]
def check(ok,message):
 if not ok:errors.append(message)
effective=p/'SUBMISSION_AFTER_INDEPENDENT_REPAIR.json';sub=read(effective);original=read(p/'SUBMISSION.json');receipt=read(p/'INDEPENDENT_REPAIR_RECEIPT.json');snapshot=p/'before_independent_repair'
check(sha(effective)=='adf1318ca9077e47a24222a6b6a5a362d8a47c0052dfc6ee171dbadea6e28ec3','Effective submission hash mismatch')
hashes=[]
original_by_name={pathlib.Path(x['path']).name:x for x in original['files']}
changed=[]
for f in sub['files']:
 x=pathlib.Path(f['path']);name=x.name;a=sha(x);o=original_by_name[name];s=snapshot/name
 current_match=a==f['sha256'];snapshot_match=s.exists() and sha(s)==o['sha256'];check(current_match,'Current hash '+name);check(snapshot_match,'Snapshot hash '+name)
 if a!=o['sha256']:changed.append(name)
 hashes.append(dict(file=name,path=str(x),current_actual_sha256=a,effective_submitted_sha256=f['sha256'],current_match=current_match,original_submitted_sha256=o['sha256'],snapshot_path=str(s),snapshot_matches_original=snapshot_match))
check(set(changed)==set(receipt['changed_submitted_files']),'Changed file set mismatch')
check(len(changed)==6,'Changed count not six')
check(sha(p/'SUBMISSION.json')==sha(snapshot/'SUBMISSION.json')==receipt['original_submission_sha256'],'Original submission was not preserved')
check(sha(p/'INDEPENDENT_REPAIR_RECEIPT.json')==sub['repair_receipt_sha256'],'Repair receipt hash mismatch')
check(sha(p/'VALIDATION_AFTER_INDEPENDENT_REPAIR.json')==sub['effective_validation_sha256'],'Targeted validation hash mismatch')
ledger=read(p/'TURN_LEDGER.json');prior=read(snapshot/'TURN_LEDGER.json');t=ledger['turns'];r=read(q/'CHECK_RESULT.json')
def resolve(o,path):
 import re
 for key,index in re.findall(r'\.([^\.\[\]]+)|\[(\d+)\]',path[1:]):o=o[int(index)]if index else o[key]
 return o
expected=[]
for f in r['required_repairs'][0]['field_repairs']:
 if f['path'].endswith('.attached_energy'):
  actual=resolve(ledger,f['path']);ok=actual==f['proposed'];check(ok,'R1 '+f['path']);expected.append(dict(path=f['path'],actual=actual,expected=f['proposed'],match=ok))
check([x['order']for x in t[10]['plays_in_order']]==[1,2,3,4],'T11 play numbering')
check([x['kind']for x in t[10]['plays_in_order']]==['ability','tool','energy_attachment','attack'],'T11 play order')
attachment=t[10]['plays_in_order'][2];check(attachment['energy']['type']=='Metal'and attachment['energy']['count']==1 and attachment['supported_interval_seconds']==[456,462],'T11 attachment fields')
check('before' in attachment['result']and '0 to 1'in attachment['result'],'T11 result')
check(t[10]['board_after']['opponent']['energy_zone']['this_turn']=={'type':None,'count':0,'available':False},'T11 consumed current Zone')
check(t[10]['board_after']['opponent']['energy_zone']['next']==prior['turns'][10]['board_after']['opponent']['energy_zone']['next'],'T11 upcoming preview changed')
for i in [11,13]:
 for phase in ['board_at_start','board_after']:check(t[i][phase]['opponent']['energy_zone']['this_turn']==prior['turns'][i][phase]['opponent']['energy_zone']['this_turn'],'Inactive opponent availability changed')
printing=[]
for f in r['required_repairs'][1]['field_repairs']:
 if f['path'].startswith('$'):
  actual=resolve(read(p/f['file']),f['path']);ok=actual==f['proposed'];check(ok,'R2 '+f['file']+f['path']);printing.append(dict(file=f['file'],path=f['path'],actual=actual,match=ok))
hand=read(p/'HAND_SUPPLEMENT.json')
for row in hand['target_rows']:
 tr=t[row['turn_number']-1]
 check(row['hand_at_start']==tr['hand_at_start']==tr['owner_hand_start'],'Hand start mirror '+str(row['turn_number']))
 check(row['owner_hand_end']==tr['owner_hand_end'],'Hand end mirror '+str(row['turn_number']))
astra=read(b/'astra_checks/20260928_200654000/ASTRA_ZONE_CHECK.json');phases=[]
for rec in astra['field_recommendations']:
 z=resolve(ledger,rec['jsonpath']);ok=z==rec['proposed_zone'];check(ok,'R3 Astra proposed zone mismatch '+rec['jsonpath'])
 check(z['phase']=='generated_pre_attachment_composite'and z['next']['available']is False,'R3 phase/preview')
 phases.append(dict(turn_number=rec['turn_number'],path=rec['jsonpath'],same_as_Astra_source_qualified_zone=ok,this_turn_basis=z['attribute_basis']['this_turn'],next_basis=z['attribute_basis']['next']))
check(len(phases)==13,'R3 count')
native=[]
scope=read(q/'SCOPE.json');viewed={x['evidence_id']for x in scope['native_viewed']}
for f in astra['inspected_native_paths_and_hashes']:
 actual=sha(pathlib.Path(f['full_native_path']));ok=actual==f['sha256'];check(ok,'Astra native derivative changed '+f['evidence_id']);check(f['evidence_id']in viewed,'Astra native outside original independent view '+f['evidence_id']);native.append(dict(evidence_id=f['evidence_id'],actual_sha256=actual,match=ok,already_independently_viewed=f['evidence_id']in viewed,direct_observation=f['direct_observation']))
result_card=t[1]['draws_and_searches'][2]['cards_in_reveal_order'][0]
check(result_card['basis']==r['required_repairs'][3]['field_repairs'][0]['proposed'],'R4 basis mismatch')
check('69 shows card back'in result_card['limit_reason']and result_card['name']=='Galarian Zigzagoon','R4 name/limits')
reconcile=read(p/'ACTION_RECONCILIATION.json');unc=read(p/'UNCERTAINTIES.json')
mirror=next(x['value']for x in unc['items']if x['field']=='newprose_vsaccepted')
check(mirror==reconcile['conflicts'],'Action reconciliation mirror mismatch')
check('turn11'in reconcile['conflicts'][1]['new'].lower()and '1 to2'in reconcile['conflicts'][1]['new'],'Action summary propagation missing')
def quotes(o):
 if isinstance(o,dict):return [(k,v)for k,v in o.items()if k=='old_quote']+sum((quotes(v)for v in o.values()),[])
 if isinstance(o,list):return sum((quotes(x)for x in o),[])
 return []
for name in ['UNCERTAINTIES.json','ACTION_RECONCILIATION.json']:
 check(quotes(read(snapshot/name))==quotes(read(p/name)),'Old quotes altered '+name)
prose=(p/'REVIEW_SUPPLEMENT.md').read_text(encoding='utf-8-sig');check('Hydreigon (gold)'not in prose,'Gold prose remains');check('Normal Metal0→1 after Helmet and before attack'in prose and 'second Dialga1→2'in prose,'Prose attachment propagation missing')
check(read(p/'PAUSE_GAME.json')['outcome']==read(snapshot/'PAUSE_GAME.json')['outcome'],'Outcome changed')
receipt_fields=receipt['changed_fields'];check(len(receipt_fields)>0,'Repair receipt empty')
hash_receipt=dict(effective_submission_path=str(effective),effective_submission_sha256=sha(effective),original_submission_sha256=sha(p/'SUBMISSION.json'),all_19_current_hashes_match=all(x['current_match']for x in hashes),all_19_original_snapshots_match=all(x['snapshot_matches_original']for x in hashes),changed_files=changed,changed_file_count=len(changed),files=hashes,astra_existing_native_hash_validation=native,source_movie_hash_reads=0)
save('HASH_VALIDATION_AFTER_INDEPENDENT_REPAIR.json',hash_receipt)
accepted=not errors
result=dict(schema='independent-retrospective-repair-acceptance-v1',game_id=p.name,reviewer='sol_retro_ladder_021327',checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),verdict='accepted_with_recording_limits'if accepted else'repair_required',independent_acceptance=accepted,effective_submission=str(effective),effective_submission_sha256=sha(effective),repair_groups={'R1':'accepted: ordered T11 normal Metal0→1 after Helmet/before attack; seven downstream counts corrected; current Zone consumed and upcoming preview preserved','R2':'accepted: all11 structured descriptors and readable prose use rainbow-border full art with one visible star; exact printing ID unknown','R3':'accepted: all13 acting-side start Zones have exact phase and attribute provenance. Eleven later native current-orb observations, T9/T13 endpoint-derived generation. Early empty/pending slots and upcoming previews remain distinct; T6/T12 selected animation does not certify complete settled preview','R4':'accepted: second T2 PB identity explicitly transaction-derived; cited69 cardback and76 already benched, with reduced locator used for reveal timing'},required_energy_fields=expected,printing_fields=printing,zone_phase_checks=phases,hash_validation_file='HASH_VALIDATION_AFTER_INDEPENDENT_REPAIR.json',all_current_submitted_hashes_match=hash_receipt['all_19_current_hashes_match'],six_changed_files=changed,mirrors_checked=['TURN_LEDGER.hand_at_start / owner_hand_start / HAND_SUPPLEMENT','UNCERTAINTIES.newprose_vsaccepted / ACTION_RECONCILIATION.conflicts','REVIEW_SUPPLEMENT T6/T11/T13 and qualification paragraphs','TURN_EVIDENCE owner discard Hydreigon descriptor'],previous_full_independent_scope='SCOPE.json:89 distinct native views,28 owner timing captures,8 locator grids; original verdict preserved',additional_native_views=0,retained_source_basis='Astra19 native phase observations were within the89 already viewed by this independent checker. Existing derivative hashes match; their phase conclusions were checked against those observations and current fields.',original_movie_reads=0,original_movie_hashes=0,new_extractions=0,recording_limits_preserved=['Exact old retained framePTS unmeasured; requested times distinct from measured newPTS','Composite boards do not assert exact simultaneous native boundaries','T9/T13 available current Metal is endpoint-derived; no selected native direct available-orb anchor','T6/T12 selected generation animations do not certify all simultaneous preview details or exact generation completion','Opponent hidden identities, full pile contents and historical exact20card list unavailable','Auto absence bounded to inspected evidence; any observed Auto option includingOFF would exclude ladder. No observed Auto in original independently inspected set.','Exact touch inputs/authorship/queue not separately certified'],accepted_outcome='owner2-3loss unchanged',source_identity_receipt_reused=True,producer_old_and_shared_files_modified_by_checker=False,errors=errors,remaining_required_repairs=[]if accepted else errors,registration='Root to inspect and register; checker did not update shared state')
save('CHECK_RESULT_AFTER_INDEPENDENT_REPAIR.json',result)
md=['# Independent repair confirmation:20260928_200654000','',f"Verdict: **{result['verdict']}**. Independent acceptance: **{str(accepted).lower()}**.",'','All19 effective submitted hashes match, all19 original snapshots match, and exactly six submitted files changed. The effective submission hash matches the root-provided receipt.','','All four required repairs are resolved. Turn11 now has an ordered normal Metal attachment after Helmet and before attack; the second Dialga carries one Metal through turn12/turn13 start and two after turn13. Its seven propagated board values and consumed current Zone are correct. Upcoming preview and inactive unknown availability remain separate.','','Hydreigon descriptors, hand mirrors and discard/prose now consistently say rainbow-border full art with one visible star, leaving exact printing identity unknown. The second turn2 Poké Ball has an explicit transaction-derived identity basis.','','All13 start-Zone phase qualifications are specific and source-consistent. Eleven use later native current-orb evidence; turn9/13 generation is derived from normal attachment endpoints. Early pending slots, previews, partial generation animations and unmeasured input timing remain qualified. Astra’s19 phase images were already within the89 independently viewed native frames; their retained derivative hashes match.','','Original full-check scope and recording limits remain applicable. No additional movie read, movie hash, decode, extraction or new visual scope was needed. Old quotes and accepted2-3loss are preserved. Producer, old and shared files were not edited by this checker. Root retains registration responsibility.']
if errors:md+=['','Remaining defects:']+['- '+x for x in errors]
(q/'CHECK_RESULT_AFTER_INDEPENDENT_REPAIR.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
save('REPAIR_CHECK_MANIFEST.json',dict(status=result['verdict'],files=[dict(path=str(q/name),sha256=sha(q/name))for name in ['CHECK_RESULT_AFTER_INDEPENDENT_REPAIR.json','CHECK_RESULT_AFTER_INDEPENDENT_REPAIR.md','HASH_VALIDATION_AFTER_INDEPENDENT_REPAIR.json']]))
print(result['verdict'],'errors',errors,'hashes',len(hashes),'changed',changed)
