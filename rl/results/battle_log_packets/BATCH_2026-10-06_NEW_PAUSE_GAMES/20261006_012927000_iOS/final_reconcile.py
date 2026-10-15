import copy,json,subprocess,sys
from pathlib import Path
from PIL import Image
P=Path(__file__).resolve().parent
def rd(p,n):return json.loads((p/n).read_text(encoding='utf-8-sig'))
def wr(p,n,v):(p/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n' if isinstance(v,(dict,list)) else v,encoding='utf-8')
def ref(t):return 'f'+f'{t:07.2f}'.replace('.','_')
for p,lo,hi in [(P,0,622),(P/'game_02',622,720)]:
    ev=rd(p,'TURN_EVIDENCE.json');ids={f['evidence_id'] for f in ev['frames']};prototype=ev['frames'][0]
    for f in sorted((P/'native').glob('t*.jpg')):
        t=float(f.stem[1:]);eid=ref(t)
        if not lo<=t<=hi or eid in ids:continue
        item=copy.deepcopy(prototype)
        item.update({'evidence_id':eid,'role':'retained_native_source_frame','turn_number':None,'who_played':None,'draw_animation_end_seconds':None,'requested_source_seconds':t,'offset_after_draw_seconds':None,'full_frame_path':'native/'+f.name if p==P else '../native/'+f.name,'selected_for_start_hand':False,'before_first_play':None,'unzoomed':None,'hand_spread':None,'observation':'Additional bounded native phase reconciliation.','suitability_or_limit':'See turn/edit ledger for actual phase observation.'})
        for key,bounds in [('bottom_crop',[0,2025,1170,2532]),('top_crop',[0,0,1170,700])]:
            path='crops/'+eid+('_bottom.png' if key=='bottom_crop' else '_top.png')
            with Image.open(f) as im:im.crop(bounds).save(p/path)
            item[key]={'path':path,'pixel_bounds_x0_y0_x1_y1':bounds}
        ev['frames'].append(item)
    ev['frames'].sort(key=lambda f:f['requested_source_seconds'])
    wr(p,'TURN_EVIDENCE.json',ev)
le=rd(P,'TURN_LEDGER.json');le['turns'][5]['timing']['before_end_action_seconds']=226.3
le['turns'][5]['plays_in_order'][-1]['timestamp_seconds']=226.6
le['turns'][5]['plays_in_order'][-1]['evidence_ids']=[ref(226.3),ref(226.6),ref(228)]
le['turns'][5]['plays_in_order'][-1]['result']='End Turn button visible226.3, disappears226.6; next-turn banner228. No attack or Supporter played; no separate confirmation prompt established in these retained frames.'
le['turns'][6]['board_at_start']['displayed_turn_banner']={'number':7,'evidence_ids':[ref(228)],'scope':'Literal transient banner at228, separate from after-draw view.'}
le['turns'][10]['board_at_start']['displayed_turn_banner']={'number':11,'evidence_ids':[ref(369)],'scope':'Literal transient banner at369, separate from after-draw view.'}
wr(P,'TURN_LEDGER.json',le)
p=P/'game_02';le2=rd(p,'TURN_LEDGER.json')
le2['turns'][0]['board_at_start']['displayed_turn_banner']['evidence_ids']=[ref(653)]
le2['turns'][0]['limits'].append('Before-end687 is still a Type: Null placement zoom, with the end hand visible; full board resolves688. It is not labeled an unzoomed complete board capture.')
le2['turns'][1]['hand_at_start']['count']=None
le2['turns'][1]['hand_at_start']['limit_reason']='Selected692/694 is the moving normal draw. Five after draw is supported by the hidden arrival sequence, but a completed five-back start fan is not asserted at these frames.'
le2['turns'][1]['opponent_hand_at_owner_turn_start'].update({'count':None,'supported_range':[4,5],'limit_reason':'Moving normal-draw card; no completed postdraw fan asserted at694.'})
wr(p,'TURN_LEDGER.json',le2)
de=rd(p,'DECK_USED.json');de['staged_edited_deck_id']='filmed-edit-cee45d5d45cb';de['staged_edited_deck_file']='../EDITED_DECK_ENTRY.json';de['independent_binding_acceptance']='pending';wr(p,'DECK_USED.json',de)
ed=rd(P,'DECK_EDIT_LEDGER.json');ed['edits'][5]['evidence_ids'] +=[ref(537)];ed['edits'][5]['observation']='Carefree Steps Meowth disappears first, count20 at537; Pay Day Meowth then disappears, count19 at538. Relative order is now established by bounded native537.'
ed['edits'][6]['evidence_ids'] +=[ref(539)]
ed['edits'][9]['evidence_ids'] +=[ref(561)];ed['edits'][9]['observation']='One Terapagos remains at561 with count19; second disappears at562 with count18. Both removed individually; final Type: Null and Gold Breaker/Brave Buddies pair remains.'
ed['energy_edits'][1]['evidence_ids'] +=[ref(595),ref(597)]
ed['energy_edits'][2]['observation']='Deck-box popup597 and deck page599/600 show Darkness alone after transient Water selection.';ed['energy_edits'][2]['evidence_ids'] +=[ref(597),ref(599)]
ed['energy_edits'][3]['evidence_ids'] +=[ref(621)];ed['staged_edited_deck_id']='filmed-edit-cee45d5d45cb';wr(P,'DECK_EDIT_LEDGER.json',ed)
ev=rd(P,'TURN_EVIDENCE.json')
for f in ev['frames']:
    if f['evidence_id']==ref(226.3):f.update({'role':'before_end','turn_number':6,'who_played':'owner','before_first_play':False,'observation':'End Turn available; owner hand Persian/Lucky Ice Pop, Grass attached to Terapagos, current zone empty and nextMetal. Actual pre-End board.'})
    if f['evidence_id']==ref(227):f.update({'role':'after_end_resolution','observation':'End button disappeared; no claim this is before End selection.'})
wr(P,'TURN_EVIDENCE.json',ev)
wr(P,'COVERAGE.md',f'''# Whole-source coverage

Source SHA256: {rd(P,'SOURCE.json')['sha256']}

Full first pass covers 0–719.001667 seconds and both games, including the uninterrupted 420–622 deck-edit interlude. Overview sheets serve as locators. Native source frames establish actual openings, draws and searches, plays, prompts, Energy, HP, removals, points and results. All 11 game 1 turns and all 2 game 2 turns have separate structured rows.

0–38: QR, original New deck 6, Save, queue, ElPapa and the owner’s original five-card opening before Active placement. 38–398: all game 1 turns through Defeat. 398–420: result and event return. 420–622: named version inspections, every observed deck change, Energy selection and final 20/20 Save. 622–649: second queue and original opening. 649–710: both game 2 turns through concession. 710–719.001667: Victory and ending.

Owner draws retain end+1/+3/+6 candidates plus dense selected native preplay views and before-end evidence. Selected hands are 55, 121, 217, 277, 334 and 656. First-turn current Energy is absent. Current circles at 55/121/217 are empty or generation-pending, independently resolved by later 56/122/218. Fixed offsets that occur after an action or in zoom are labeled unsuitable for start hands. Turn 6’s actual before-End view is 226.3. Game 2’s before-End 687 still shows the placement zoom; hand is readable, with complete board at 688. No full discard windows are filmed; top-card previews remain partial.

Source-local seek targets are retained; exact decoded PTS and remote opponent touch timing were not measured. The child uses the same original SHA and timestamps. Neither packet claims an external save. Both require independent acceptance before the one original can be archived.
''')
wr(p,'COVERAGE.md',f'''# Game 2 coverage

Source-local interval 622–719.001667, original SHA {rd(P,'SOURCE.json')['sha256']}. Parent covers the full source and 420–622 interlude. Child covers queue, opponent たこ, five-card opening at 644 before Snorlax placement at 646, literal turn-1 banner at 653, both actual turns, concession at 710, Victory at 718 and ending.

Native hand 656 is intact before the first Poké Ball selection near 658. Draw-end+1/+3/+6 and before-End 687 are retained; before-End is a placement zoom and is labeled accordingly, with full board 688. Opponent fan 4 at owner turn start is literal. Opponent normal draw is moving at 692/694; completed start count is not invented from that transition. Research’s two hidden arrivals and Order Pad tails are separately retained. No full discard window exists. Original deck QR plus continuous filmed editing establishes the separate source semantic 20; live-log capture is still unavailable to worker.
''')
summary=rd(P,'SUMMARY.json');summary['whole_source_reviewed']=True;wr(P,'SUMMARY.json',summary)
unc=rd(P,'UNCERTAINTIES.json');unc['uncertainties'] += [{'id':'opponent-turn9-fan-phase','status':'recording_limit','impact':'Literal completed fans3 at294 and2 at334/339 retained; transitional postplay counts unknown. No invented hidden extra action.'}];wr(P,'UNCERTAINTIES.json',unc)
unc=rd(P/'game_02','UNCERTAINTIES.json');unc['uncertainties'] += [{'id':'before-end-placement-zoom','status':'recording_limit','impact':'687 retains actual end hand during Type: Null placement zoom; full resolved board688. No complete unzoomed pre-End claim.'},{'id':'moving-opponent-normal-draw','status':'recording_limit','impact':'692/694 normal-draw card is moving. Completed literal start fan count not asserted.'}];wr(P/'game_02','UNCERTAINTIES.json',unc)
for p in (P,P/'game_02'):
    r=subprocess.run([sys.executable,str(P.parent/'validate_packet.py'),str(p)],capture_output=True,text=True,encoding='utf-8')
    receipt=json.loads(r.stdout);wr(p,'STRUCTURAL_VALIDATION.json',receipt);print(json.dumps(receipt,ensure_ascii=False))
    assert receipt['structural_pass']
    rows=rd(p,'TURN_LEDGER.json')['turns'];frames=rd(p,'TURN_EVIDENCE.json')['frames'];fids={x['evidence_id'] for x in frames}
    checks={'contiguous_turn_rows': [x['turn_number'] for x in rows]==list(range(1,len(rows)+1)),'five_opening_cards':len(rd(p,'PAUSE_GAME.json')['opening']['cards_left_to_right'])==5,'each_owner_has_offsets':all(all(ref(x['timing']['draw_animation_end_seconds']+off) in fids for off in (1,3,6)) for x in rows if x['who_played']=='owner'),'each_owner_selected_preplay':all(any(f['selected_for_start_hand'] and f['turn_number']==x['turn_number'] and f['before_first_play'] for f in frames) for x in rows if x['who_played']=='owner'),'all_plays_numbered':all([a['order'] for a in x['plays_in_order']]==list(range(1,len(x['plays_in_order'])+1)) for x in rows),'no_live_save_claim':rd(p,'PAUSE_GAME.json')['external_saved'] is False,'source_exact20':sum(c['count'] for c in rd(p,'DECK_USED.json').get('source_counts_by_semantic_entity',rd(p,'DECK_USED.json').get('source_counts_by_name_and_variant',[])))==20}
    if p==P:
        checks.update({'retreat_payment_typed':rows[9]['plays_in_order'][3]['energy']['retreat_payment_by_type']=={'Grass':1,'Metal':1},'terapagos_bench_zero_after_retreat':rows[9]['board_after']['owner']['bench_in_position_order'][1]['attached_energy']['total']==0,'terminal_active_removed':rows[-1]['board_after']['owner']['active']['status']=='visibly_empty','whole_source_end':rd(p,'SUMMARY.json')['whole_source_coverage']['end_seconds']==rd(p,'SOURCE.json')['duration_seconds']})
    else:checks['opponent_name_unicode']=rd(p,'SUMMARY.json')['opponent']=='たこ'
    assert all(checks.values()),checks
    wr(p,'WORKER_VALIDATION.json',{'worker_pass':True,'checks':checks,'turn_rows':len(rows),'native_frames':len(frames),'independent_acceptance':False,'limits':'Worker reconciliation and structural gates do not substitute for independent acceptance.'})
