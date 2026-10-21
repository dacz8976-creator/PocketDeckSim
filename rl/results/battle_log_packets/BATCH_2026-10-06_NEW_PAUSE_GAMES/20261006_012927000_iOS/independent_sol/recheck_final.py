import pathlib,json,hashlib,datetime,os,copy
P=pathlib.Path(__file__).resolve().parent.parent
C=P/'game_02';B=P.parent
N=['SOURCE.json','REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
backup=P/'original_before_final_independent'
history=[]
for q,sub in [(P,'parent'),(C,'game_02')]:
 old=read(q/'independent_sol/CHECK_RESULT.rejected_R1_R3.json')
 assert old['accepted'] is False
 for name,digest in old['checked_input_sha256'].items():
  f=backup/sub/name;assert sha(f)==digest,(f,'preserved input mismatch')
  history.append({'path':os.path.relpath(f,P).replace('\\','/'),'sha256':digest,'matches_frozen_rejection':True})
 for name in ['DECK_EDIT_LEDGER.json','CORRECTION_LEDGER.json','HANDOFF.md']:
  f=backup/sub/name
  if f.exists():
   key=os.path.relpath(q/name,q).replace('\\','/')
   digest=old['supplemental_checked_input_sha256'].get(key)
   if digest:
    assert sha(f)==digest;history.append({'path':os.path.relpath(f,P).replace('\\','/'),'sha256':digest,'matches_frozen_rejection':True})
edited=read(B/'EDITED_DECK_ENTRY.json')['decks'][0]
oldedit=read(backup/'EDITED_DECK_ENTRY.json')['decks'][0]
assert sha(backup/'EDITED_DECK_ENTRY.json')==read(P/'independent_sol/CHECK_RESULT.rejected_R1_R3.json')['supplemental_checked_input_sha256']['../EDITED_DECK_ENTRY.json']
assert edited['cards_in_display_order']==oldedit['cards_in_display_order']
assert edited['energy_configuration']==['Water'] and oldedit['energy_configuration']==['Darkness']
identity={'cards':[(c['entity_kind'],c['entity_id'],c['count']) for c in edited['cards_in_display_order']],'energy':['Water']}
digest=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()
assert edited['semantic_identity_sha256']==digest and edited['id']=='filmed-edit-'+digest[:12]
assert edited['id']=='filmed-edit-2c58f9b081c7'
assert sum(c['count'] for c in edited['cards_in_display_order'])==20
assert len(edited['card_slots'])==20 and all(c['printing'] is None for c in edited['cards_in_display_order'])
for f in edited['native_final_views']: assert sha(pathlib.Path(f['path']))==f['image_sha256']
edit=read(P/'DECK_EDIT_LEDGER.json');deck=read(C/'DECK_USED.json')
assert edit['final_energy_configuration']==deck['source_energy_configuration']==['Water']
assert edit['staged_edited_deck_id']==deck['staged_edited_deck_id']==edited['id']
assert (C/deck['staged_edited_deck_file']).resolve()==(B/'EDITED_DECK_ENTRY.json').resolve()
assert 'transient Water' not in json.dumps(edit) and 'Water only' in edit['energy_edits'][3]['observation']
pl=read(P/'TURN_LEDGER.json');cl=read(C/'TURN_LEDGER.json')
originaldeck=read(P/'DECK_USED.json')
assert originaldeck==read(backup/'parent/DECK_USED.json')
for row in cl['turns']:
 for field in ['board_at_start','board_after']:
  assert row[field]['owner']['energy_zone']['next']['type']=='Water'
copycat=cl['turns'][0]['draws_and_searches'][2]
assert [c['timestamp_seconds'] for c in copycat['cards_in_reveal_order']]==[674,675,676,677]
assert ['Ball' in copycat['cards_in_reveal_order'][0]['name'],'Meowth' in copycat['cards_in_reveal_order'][1]['name'],'Lucky Ice Pop' in copycat['cards_in_reveal_order'][2]['name'],'Cyrus' in copycat['cards_in_reveal_order'][3]['name']]==[True]*4
play=cl['turns'][0]['plays_in_order'][2]
assert play['input_interval_seconds']==[667,668] and play['card_reveal_timestamp_seconds']==668 and play['returned_hand_timestamp_seconds']==670
row=cl['turns'][1]
assert row['hand_at_start']['count']==row['opponent_hand_at_owner_turn_start']['count']==5
assert row['board_at_start']['opponent']['energy_zone']['this_turn']=={'type':'Lightning','count':1,'available':True}
assert row['draws_and_searches'][0]['displayed_draw_result_window_seconds']==[690,692]
assert row['automatic_events_in_order'][0]['observed_window_seconds']==[690,692]
assert row['draws_and_searches'][1]['displayed_draw_result_window_seconds']==[696,698]
assert all(c['name'] is None and c['timestamp_seconds'] is None for c in row['draws_and_searches'][1]['cards_in_reveal_order'])
assert row['plays_in_order'][1]['card_reveal_timestamp_seconds']==700 and row['plays_in_order'][1]['coin_animation_timestamp_seconds']==702
assert pl['turns'][1]['plays_in_order'][0]['input_interval_seconds']==[55,56]
assert pl['turns'][1]['plays_in_order'][0]['timestamp_seconds']==58
frozen13=read(P/'FINAL_INDEPENDENT_CORRECTIONS.json')['frozen13_unchanged_sha256']
assert sha(B/'NEW_DECK_ENTRIES.json')==frozen13
for q,sub in [(P,'parent'),(C,'game_02')]:
 assert read(q/'ROOT_FINAL_REPAIR_STRUCTURE_CHECK.json')['structural_pass'] is True
 before=read(backup/sub/'TURN_EVIDENCE.json')['frames'];after=read(q/'TURN_EVIDENCE.json')['frames']
 assert len(before)==len(after)
 for a,b in zip(before,after):
  aa=copy.deepcopy(a);bb=copy.deepcopy(b);aa.pop('observation',None);bb.pop('observation',None)
  assert aa==bb,'Native/crop binding unexpectedly changed'
views=[]
times={'':[55,55.5,56,58,596,597,599,600,620,621,622],'game_02':[656,667,668,670,674,675,676,677,690,692,694,696,698,700,702,704,708,710,718]}
for sub,ts in times.items():
 q=P/sub;frames={f['requested_source_seconds']:f for f in read(q/'TURN_EVIDENCE.json')['frames']}
 for t in ts:
  f=frames[t];fp=(q/f['full_frame_path']).resolve()
  views.append({'packet':sub or '.','evidence_id':f['evidence_id'],'requested_source_seconds':t,'actual_pts':None,'full_frame_path':str(fp),'full_frame_sha256':sha(fp),'source_video':f['source_video'],'source_sha256':f['source_sha256'],'view_method':'Prior independent native inspection plus narrow repair recheck using retained source-bound native views/contact sheets. No new extraction.'})
findings=[{'id':'R1','resolved':True,'finding':'596 explicitly selects Water; final saved droplet and child next previews match Water. Original game1 configuration and frozen13 remain unchanged. Water semantic identity recomputed and all staged references agree.'},{'id':'R2','resolved':True,'finding':'Copycat consumption667-668, face668, returned3 at670; four reveals Ball674/TRMeowth675/Pop676/Cyrus677 now agree with native evidence.'},{'id':'R3','resolved':True,'finding':'Opponent settled five-back fan/current Lightning692; draw/generation690-692 and combined hidden Research696-698 with names/individual times null. OrderPad face700/coin702/tails704 now separated.'}]
created=datetime.datetime.now(datetime.timezone.utc).isoformat()
common=[P/'DECK_EDIT_LEDGER.json',P/'CORRECTION_LEDGER.json',P/'FINAL_INDEPENDENT_CORRECTIONS.json',P/'RELATED_GAME_PACKETS.json',P/'HANDOFF.md',P/'RECORDING_METADATA.json',B/'EDITED_DECK_ENTRY.json',B/'EDITED_DECK_ENTRY.md',B/'PAUSE_EDITED_DECK_IMPORT.json',B/'NEW_DECK_ENTRIES.json',P/'qr_intake/QR_DECODE_0001.00.json',P/'qr_intake/t0001.00.png',pathlib.Path(r'C:\Users\dacz8\Projects\Pocket Deck Lab\s216_card_catalog_v1.json')]
for q,sub in [(P,''),(C,'game_02')]:
 o=q/'independent_sol';previous=read(o/'CHECK_RESULT.rejected_R1_R3.json')
 vi=read(o/'VIEWED_EVIDENCE.json')
 for v in vi['views']: assert sha(pathlib.Path(v['full_frame_path']))==v['full_frame_sha256']
 if not (o/'VIEWED_EVIDENCE.before_final_recheck.json').exists(): (o/'VIEWED_EVIDENCE.before_final_recheck.json').write_bytes((o/'VIEWED_EVIDENCE.json').read_bytes())
 recheck={'created_utc':created,'accepted':True,'required_repairs':[],'remaining_repairs':[],'resolved_findings':findings,'views':views,'preserved_initial_inputs':history,'edited_identity':edited['id'],'frozen13_sha256':frozen13,'scope':'Narrow R1-R3 recheck; combines retained initial independent bounded inspection of both games, entire edit binding and source ending. No new whole-game1 pass or media rehash.'}
 vi.setdefault('repair_rechecks',[]).append(recheck);save(o/'VIEWED_EVIDENCE.json',vi)
 other=C if q==P else P
 supplements=common+[o/'VIEWED_EVIDENCE.json',o/'STRUCTURAL_CHECK.json',o/'CHECK_RESULT.rejected_water_mismatch.json',o/'CHECK_RESULT.rejected_R1_R3.json',q/'ROOT_FINAL_REPAIR_STRUCTURE_CHECK.json']+[other/n for n in N]
 result=copy.deepcopy(previous)
 result.update(accepted=True,status='accepted_after_frozen_R1_R3_recheck',created_utc=created,checked_input_sha256={n:sha(q/n) for n in N},supplemental_checked_input_sha256={os.path.relpath(f,q).replace('\\','/'):sha(f) for f in supplements},required_repairs=[],remaining_repairs=[],resolved_findings=findings,all_source_segments_verified=True,required_source_game_count=2,verified_source_game_count=2,source_segment_verification=[{'segment':'game1','seconds':[0,420],'basis':'Retained initial independent bounded opening/ordinary turns/selected hands/searches/retreat/terminal inspection plus full worker coverage.'},{'segment':'continuous edited deck binding','seconds':[420,622],'basis':'Retained independent variant/count/edit inspection; corrected Water596 through Save621/queue622; exact semantic20 and catalog mappings.'},{'segment':'game2 and source ending','seconds':[622,719.001667],'basis':'Entire tiny game2 retained independent native inspection, corrected event sequence, explicit concession708-710 and Victory718/source ending.'}],preserved_initial_inputs=history,edited_semantic_identity=edited['id'],recheck_scope=recheck['scope'],prior_frozen_rejection='CHECK_RESULT.rejected_R1_R3.json')
 result['supported_conclusions']=[s.replace('Final Energy must be Water.','Final Energy is verified Water.') for s in result['supported_conclusions']]
 save(o/'CORRECTION_RECHECK.json',result);save(o/'CHECK_RESULT.json',result)
 print(sub or 'parent','accepted',len(result['checked_input_sha256']),'current canonical hashes',len(result['supplemental_checked_input_sha256']),'supplemental hashes')
print('Resolved all three findings;',len(history),'frozen input hashes matched;',len(views),'narrow source references; frozen13 unchanged')
