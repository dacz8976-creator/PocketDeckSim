from pathlib import Path
import json,hashlib,datetime
p=Path(__file__).parent
sha='f9c112be78ea4a2f0c8c72b8b47d529fad49001efde34780b3562f4c8a69441b'
prefix='first | Kingambit first attack own turn 8; Glimmora own turn 2; Regigigas/Alolan Muk no attack | opponent points at first attack: Kingambit 2, Glimmora 0; Regigigas/Alolan Muk N/A'
summary={
 'source_filename':'20261016_024253000_iOS.MP4','source_sha256':sha,
 'source_bytes':1613329420,'source_duration_seconds':863.128333,
 'reviewer':'/root/ladder_024253','model':'gpt-6.1-sol','reasoning_effort':'high',
 'match_count':1,'battle_complete':True,'primary_review_complete':True,
 'match_date':'2026-10-15','source_creation_utc':'2026-10-16T02:42:53Z',
 'source_creation_local':'2026-10-15T21:42:53-05:00',
 'owner_identifier':'Dacz8976','opponent_identifier':'暗黑掌門人','outcome':'win',
 'mode':'ranked ladder; Master Ball rank confirmed on result screen',
 'Auto':{'visible_control_or_option':False,'observed_enabled':False,'owner_choices_by_auto_observed':False,'classification':'human ladder eligible'},
 'auto_visible':False,'computer_battle':False,
 'first_or_second':'first','owner_turns':10,'terminal_global_turn':19,'terminalglobalturn':19,
 'final_points':{'owner':3,'opponent':2},'damage_done_displayed':540,
 'rank_result':{'rank':'Master Ball','points':776,'points_gained':1},
 'visible_owner_core':['Glimmet','Glimmora (90 HP, Shattering Crystal, Venomous Hit 30)','Pawniard','Kingambit (140 HP, Overlord\u2019s Blade 60+)','Regigigas','Alolan Grimer','Alolan Muk (110 HP, Power of Alchemy; not ex)'],
 'visible_opponent_core':['Mega Rayquaza ex (two revealed, 180 HP, Mega Burst 50x)','Dratini','Dragonair (80 HP, Dragon\u2019s Blessing)','Gouging Fire (two revealed, 110 HP, Scorching Interruption 100)'],
 'exact_full_decks_known':False,
 'first_attacks':[
  {'core':'Kingambit','attacked':True,'owner_turn':8,'global_turn':15,'source_seconds':691,'opponent_points':2,'attack':'Overlord\u2019s Blade','damage_displayed':150,'target':'first Gouging Fire 150 HP; KO'},
  {'core':'Glimmora','attacked':True,'owner_turn':2,'global_turn':3,'source_seconds':158,'opponent_points':0,'attack':'Venomous Hit','damage_displayed':30,'target':'Mega Rayquaza ex; poisoned'},
  {'core':'Regigigas','attacked':False,'owner_turn':None,'global_turn':None,'opponent_points':None,'note':'no attack / opp N/A'},
  {'core':'Alolan Muk','attacked':False,'owner_turn':None,'global_turn':None,'opponent_points':None,'note':'no attack / opp N/A'}],
 'exact_three_item_note_prefix':prefix,
 'decisive_result_evidence':[
  {'file':'evidence/native/t0839.00.jpg','fact':'Kingambit survives Mega Burst at 10 HP with Heavy Helmet; score2-2'},
  {'file':'evidence/native/t0842.00.jpg','fact':'owner final attack selected,180; King10HP; deck empty'},
  {'file':'evidence/native/t0846.00.jpg','fact':'180 damage hits180HP Mega Rayquaza ex'},
  {'file':'evidence/native/t0860.00.jpg','fact':'Victory, first,19turns,3-2,540damage'},
  {'file':'evidence/turnscan/contact_15.jpg','fact':'Victory and MasterBall776points,+1'}],
 'external_write_performed':False,'shared_completion_registered':False,'source_moved':False,
 'remaining':'independent acceptance and lead completion/log/archive workflow',
 'coverage':{'full_source_start':0,'full_source_end':863.128333,'all_global_turns':list(range(1,20)),'unreviewed_battle_intervals':[]},
 'limitations':['Hidden hand and exact full deck lists remain unknown.','Short Energy-selection animations are described using visible end states; no hidden draw identities invented.','Turn-boundary timestamps approximate; native image timestamps are exact requested source offsets.']
}
(p/'SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
uncertainties={
 'source_filename':summary['source_filename'],'source_sha256':sha,
 'material_outcome_uncertainties':[],
 'unreviewed_intervals':[],
 'unknowns':[
 {'topic':'full_decks_and_hidden_information','status':'unknown','description':'No complete 20-card deck-list view; hidden opponent hand/search identities not guessed.'},
 {'topic':'fine_energy_animation_order','status':'bounded','description':'Several opponent Rainbow Cave/Dragonair interactions occur between sampled views; the actual accumulated Energy, attacks, discards and HP transitions were reconciled. No different outcome or missing turn implied.'},
 {'topic':'exact_turn_boundary_seconds','status':'approximate','description':'Review table intervals delimit phases approximately. Native frames retain exact requested offsets.'}
 ],
 'resolved':[
 'First/19turns/3-2/540 damage explicitly confirmed on native860.',
 'Owner core support is Alolan Muk110, not ex; Power of Alchemy affects Basic Pokemon only.',
 'Opponent support is Dragonair80, not Froslass or Oricorio.',
 'Glimmora KO Heads denied a point but still supplies one of three KO counts for Kingambit180.',
 'Heavy Helmet reduced final150 MegaBurst to130, leaving Kingambit10HP.',
 'First Kingambit attack own8/global15 at opponent2; first Glimmora own2/global3 at opponent0.'
 ]
}
(p/'UNCERTAINTIES.json').write_text(json.dumps(uncertainties,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Freeze only primary-review-owned files and intake identity/assignment files.
rootnames={'SOURCE.json','PROBE.json','ASSIGNMENT.json','LOCAL_METADATA.json','REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','make_partial_sheets.py','write_summary_freeze.py'}
files={}
for f in sorted(p.rglob('*')):
 if not f.is_file():continue
 rel=f.relative_to(p).as_posix()
 if rel.startswith('evidence/') or (len(f.relative_to(p).parts)==1 and f.name in rootnames):
  files[rel]=hashlib.sha256(f.read_bytes()).hexdigest()
manifest={'source_filename':summary['source_filename'],'source_sha256':sha,'reviewer':summary['reviewer'],'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'algorithm':'SHA-256','files':files,'excludes':['manifest itself','independent_sol/**','lead acceptance/completion/external log/archive files','intake download checks and shared registration receipt']}
(p/'REVIEW_PACKET_HASHES.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert len(prefix.split('|'))==3
assert all(hashlib.sha256((p/k).read_bytes()).hexdigest()==v for k,v in files.items())
print(f'Frozen {len(files)} primary files; firstattack prefix has3items; manifest reload verifies.')
