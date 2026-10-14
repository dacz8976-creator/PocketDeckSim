from pathlib import Path
import json,hashlib,datetime
P=Path(__file__).resolve().parent
G=P.parents[1]/'20260908_022627000'
def rd(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def save(name,data):(P/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
new=rd(G/'TURN_LEDGER.json');old=rd(G/'before_independent_boundary_repair/TURN_LEDGER.json')
hand=rd(G/'HAND_SUPPLEMENT.json');oldhand=rd(G/'before_independent_boundary_repair/HAND_SUPPLEMENT.json')
ev=rd(G/'TURN_EVIDENCE.json');frames={f['evidence_id']:f for f in ev['frames']}
sub=rd(G/'SUBMISSION_AFTER_BOUNDARY_REPAIR.json')
overrides=sub['astra_reference_repair']['modified_file_sha256']|sub['independent_boundary_repair']['modified_file_sha256']
hashes=[]
for f in sub['files']:
 p=Path(f['path']); actual=hashlib.sha256(p.read_bytes()).hexdigest();expected=overrides.get(p.name,f['sha256']);hashes.append({'file':p.name,'effective_expected_sha256':expected,'actual_sha256':actual,'match':actual==expected})
assert all(f['match'] for f in hashes)
numeric_card_changes=[];qualifications=[];unknown_refs=[]
card_fields=['name','variant','bench_position','hp_now','hp_max','hp_max_basis','damage','attached_energy','tool','special_conditions','active_effects']
for r,prev in zip(new['turns'],old['turns']):
 assert r['turn_number']==prev['turn_number']
 for phase in ['board_at_start','board_after']:
  b,prior=r[phase],prev[phase]
  assert b['phase'].startswith('Composite source-derived')
  assert b.get('boundary_basis') and b.get('native_anchor_inventory')
  for side in ['owner','opponent']:
   q,z=b[side],prior[side]
   assert q['status']=='inferred' and q.get('boundary_basis')
   before=[z['active']]+z['bench_in_position_order'];after=[q['active']]+q['bench_in_position_order']
   assert len(before)==len(after)
   for index,(c,v) in enumerate(zip(after,before)):
    if c is None:assert v is None;continue
    assert c['status']=='inferred' and c.get('attribute_basis') and c.get('limit_reason')
    for k in card_fields:
     if c.get(k)!=v.get(k):numeric_card_changes.append({'turn':r['turn_number'],'phase':phase,'side':side,'slot':index,'field':k,'before':v.get(k),'after':c.get(k)})
   assert q['points']==z['points'];assert q['energy_zone']==z['energy_zone']
  qualifications.append({'turn':r['turn_number'],'boundary':phase,'qualified':True,'specific_derivations':b.get('specific_boundary_derivations')})
assert not numeric_card_changes
for r,v in zip(hand['target_rows'],oldhand['target_rows']):
 for k in ['owner_hand_start','owner_hand_end','normal_draw']:
  # Hand content stays exact; turn15 has only a stale phase qualification replaced.
  def clean(x):
   if isinstance(x,dict):return {k:clean(v) for k,v in x.items() if k!='limit_reason'}
   if isinstance(x,list):return [clean(v) for v in x]
   return x
  assert clean(r[k])==clean(v[k]),(r['turn_number'],k)
 for c in r.get('later_offset_candidates',[]):
  f=frames[c['evidence_id']];assert c['requested_source_seconds']==f['requested_source_seconds'];assert c['actual_frame_seconds_if_measured']==f['actual_frame_seconds_if_measured'];assert c['offset_after_draw_bracket_seconds']==f['offset_supported_range_seconds'];assert 'Post-first-play' in c['phase']
assert {103,105}<=set(hand['target_rows'][1]['native_capture_times'])
assert 174 in hand['target_rows'][2]['native_capture_times']
assert '593 is pre-switch' in hand['target_rows'][7]['limits']
assert '596 is post-switch' in hand['target_rows'][7]['limits']
assert 'Retreat precedes +3' not in json.dumps(hand) and 'Retreat precedes +3' not in json.dumps(new)
def walk(x,loc=''):
 if isinstance(x,dict):
  for k,v in x.items():
   if k=='evidence_ids':
    for ref in v or []:
     if ref not in frames:unknown_refs.append({'location':loc,'ref':ref})
   walk(v,loc+'.'+k)
 elif isinstance(x,list):
  for i,v in enumerate(x):walk(v,loc+f'[{i}]')
walk(new);walk(hand);assert not unknown_refs
assert all(new['turns'][n-1]['board_after'].get('specific_boundary_derivations') for n in [7,9,15,17])
prose=(G/'REVIEW_SUPPLEMENT.md').read_text(encoding='utf-8')
assert 'they do not directly show every boundary attribute simultaneously' in prose
result={'schema':'independent-retrospective-repair-acceptance-v1','game_id':'20260908_022627000','reviewer':'Sol /root/sol_retro_ladder_021327','producer':'different Sol /root/sol_retro_ladder_012720','status':'accepted_with_recording_limits','independent_acceptance':True,'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_sha256':rd(G/'SOURCE_REFERENCE.json')['sha256'],'accepted_submission':'SUBMISSION_AFTER_BOUNDARY_REPAIR.json','supersedes_decision_only':'SOURCE_CHECKS.json needs_repair; historical check preserved','scope':'Whole-packet18turn/9owner-hand acceptance after three bounded repairs; follows60-native independent check and six bounded Astra findings. No additional native views, original reads or extraction in this recheck.','repair_checks':[{'id':'BOUNDARY_PROVENANCE','status':'resolved','basis':'All36start/end board objects and every non-null Pokémon explicitly marked inferred/composite with per-attribute basis, pooled native-anchor inventories and boundary limits. Specific end7/9/15/17 derivations correctly separate observed304/339.3,394,602/640and681states from represented boundaries. The70HP Hydreigon end17 is explicit140minus accepted Boost Dash70, without682adopted as direct proof. Prose no longer asserts exact simultaneous boundary snapshots.'},{'id':'T15_HAND_PHASE','status':'resolved','basis':'Hand/ledger text identifies593as pre-switch and596as post-switch/evolution in progress, consistent with the native frames previously inspected. Target hand content is unchanged.'},{'id':'HAND_CANDIDATE_INVENTORY','status':'resolved','basis':'Existing103/105turn3and174turn5candidates are listed with exact requested times, producer-measuredPTS, actual offset ranges and post-play qualifications; dense preplay anchors remain separate.'}],'values_unchanged':{'all_board_numeric_card_tool_condition_values':True,'all_hand_and_draw_card_values':True,'energy_zone_values_and_qualifications':True,'inherited_old_prose_and_owner_loss':True},'frozen_file_checks':hashes,'board_qualifications':qualifications,'unknown_evidence_refs':unknown_refs,'remaining_required_repairs':[],'acceptance_limits':['Boundary boards are composite source-derived states, not every-attribute simultaneous native snapshots. Recorded accepted action chronology supplies some transitions and arithmetic. This qualification does not independently prove exact input times.','Acceptance retains prior60-native bounded inspection and27-native consequential Astra check, not an every-instant replay. Producer721reduced1fps locator screening was not repeated independently.','Opponent identities/piles hidden behind card backs or closed piles, exact historical20-card list and unsampled Settings remain unknown.','NoAutooptionseen in inspected anchors, including679menu; ladder is presumed, opponent type uncertain. Any visibleAutoevenOFFrequires computer classification and exclusion.','Native requested source times stay separate from producer-measuredPTS, with reusedPTSnull.','Outcome remains inherited accepted owner loss; terminal board implications are qualified because final overlay obscures settled board.'],'preservation':{'original_reads':0,'original_hashes':0,'new_extractions':0,'new_visual_native_views':0,'primary_packet_edits':0,'old_packet_edits':0,'registry_edits':0,'external_artifact_edits':0}}
save('SOURCE_CHECKS_REPAIR_ACCEPTANCE.json',result)
md='''# Repair acceptance: 20260908_022627000

**Accepted with recording limits.** The three required repairs are resolved. This acceptance applies to the full 18-turn supplement and 9 owner hand rows frozen in SUBMISSION_AFTER_BOUNDARY_REPAIR.json, following the previous 60-native independent check and bounded Astra findings.

All 36 start/end boards now identify composite, source-derived states. Per-Pokémon attributes and native anchor phases are separated, and the specific end-turn 7, 9, 15 and 17 derivations agree with previously inspected evidence and accepted action chronology. Numeric values, cards, Tools, conditions, hands and draws are unchanged. The end-turn 17 Hydreigon 70 HP is explicitly derived from observed 140 HP minus recorded Boost Dash damage, not claimed as a direct reading at 681 seconds.

Turn 15 now correctly identifies 593 seconds as pre-switch and 596 seconds as post-switch with evolution in progress. Turn 3 includes the retained 103/105-second candidates; turn 5 includes 174 seconds. Their requested times, producer-measured PTS, offset ranges and post-play qualifications match TURN_EVIDENCE.

All 15 effective frozen file hashes match. No required repair remains. The historical needs-repair report is preserved; this acceptance supersedes its decision.

The earlier limits remain: derived boundaries are not simultaneous native snapshots; hidden opponent cards and closed piles remain unknown; the exact historical 20-card list is unavailable; subsecond inputs and hidden Settings are not certified. No Auto option was visible in inspected native views, so ladder remains presumed with opponent type uncertain. The accepted owner loss and old packet remain unchanged.

This recheck used existing evidence knowledge and repaired fields. It added no native views, original reads, hashes or extractions and changed no primary, old packet, registry or external artifact.
'''
(P/'REPAIR_ACCEPTANCE.md').write_text(md,encoding='utf-8')
save('REPAIR_ACCEPTANCE_MANIFEST.json',{'status':'accepted_with_recording_limits','files':[{'path':str(P/n),'sha256':hashlib.sha256((P/n).read_bytes()).hexdigest()} for n in ['SOURCE_CHECKS_REPAIR_ACCEPTANCE.json','REPAIR_ACCEPTANCE.md']],'original_independent_manifest_preserved':'MANIFEST.json'})
print(json.dumps({'decision':result['status'],'frozen_hashes_match':len(hashes),'qualified_board_objects':len(qualifications),'numeric_card_changes':numeric_card_changes,'unknown_refs':unknown_refs}))
