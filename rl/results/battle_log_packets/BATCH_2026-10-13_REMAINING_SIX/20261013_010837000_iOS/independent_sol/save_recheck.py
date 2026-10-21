import hashlib, json
from pathlib import Path
from datetime import datetime, timezone

p=Path(__file__).resolve().parent.parent
out=p/'independent_sol'
freeze=json.loads((p/'REVIEW_PACKET_HASHES.json').read_text(encoding='utf-8'))
checked={n:hashlib.sha256((p/n).read_bytes()).hexdigest() for n in freeze['files']}
assert checked==freeze['files'], 'Eight hashes changed'
assert freeze['revision']==2
docs={n:json.loads((p/n).read_text(encoding='utf-8')) if n.endswith('.json') else (p/n).read_text(encoding='utf-8') for n in checked}
turns=docs['TURN_LEDGER.json']['turns']
byturn={t['turn_number']:t for t in turns}
assert len(turns)==15
research=[g for g in byturn[1]['draws_and_searches'] if g['kind']=='supporter_draw'][0]['cards_in_reveal_order']
assert [(x['name'],x['timestamp_seconds']) for x in research]==[('Rare Candy',69),('Glimmet',70)]
t5=byturn[5]['plays_in_order']
assert [(x['card_name'],x['hand_count_after']) for x in t5[:2]]==[('Alolan Muk',2),('Glimmet',1)]
assert byturn[5]['timing']['first_voluntary_move_seconds']==202
for n,dest in [(5,'Pawniard'),(7,'Glimmet'),(9,'Kingambit'),(11,'Alolan Muk'),(13,'Kingambit')]:
    a=[x for x in byturn[n]['plays_in_order'] if x['kind']=='energy_attachment'][0]
    assert a['target']==a['energy']['destination']==dest,(n,a)
assert byturn[11]['plays_in_order'][0]['card_name']=='Heavy Helmet'

def energy(board):
    owner=board['owner']
    mons=[owner['active'],*owner['bench_in_position_order']]
    return {m['name']:m['attached_energy']['by_type'].get('Darkness',0) for m in mons}
after={
5:{'Regigigas':0,'Pawniard':1,'Glimmet':0,'Alolan Muk':0},
6:{'Regigigas':0,'Pawniard':1,'Glimmet':0,'Alolan Muk':0},
7:{'Regigigas':0,'Kingambit':1,'Glimmet':1,'Alolan Muk':0},
8:{'Glimmet':1,'Kingambit':1,'Alolan Muk':0},
9:{'Glimmet':1,'Kingambit':2,'Alolan Muk':0},
10:{'Glimmet':1,'Kingambit':2,'Alolan Muk':0},
11:{'Glimmet':1,'Kingambit':2,'Alolan Muk':1},
12:{'Kingambit':2,'Alolan Muk':1},
13:{'Kingambit':3,'Alolan Muk':1},
14:{'Kingambit':3,'Alolan Muk':1},
15:{'Kingambit':3,'Alolan Muk':1},
}
for n,expected in after.items():
    assert energy(byturn[n]['board_after'])==expected,(n,'after',energy(byturn[n]['board_after']))
    if n>5:
        assert energy(byturn[n]['board_at_start'])==after[n-1],(n,'start',energy(byturn[n]['board_at_start']))
original=json.loads((out/'CHECK_RESULT.json').read_text(encoding='utf-8'))
for name,h in original['checked_input_sha256'].items():
    assert hashlib.sha256((out/'rejected_8_v1'/name).read_bytes()).hexdigest()==h,'Original rejection changed'
result={
 'schema':'pause_games_independent_correction_recheck_v1',
 'checked_utc':datetime.now(timezone.utc).isoformat(),
 'reviewer':'/root/check_remaining_010837',
 'model_effort':'Sol/high',
 'source_video':freeze['source_video'],
 'source_sha256':freeze['source_sha256'],
 'packet_revision':2,
 'scope':'Narrow R1-R3 correction recheck plus all eight revised hashes; prior bounded source checks remain in CHECK_RESULT.json. No duplicate full battle pass.',
 'checked_input_sha256':checked,
 'all_eight_stable':True,
 'accepted':True,
 'required_repairs':[],
 'supersedes_rejection_for_current_bytes':'CHECK_RESULT.json',
 'original_rejected_eight_preserved_and_hash_verified':'rejected_8_v1',
 'observations':[
  {'repair':'R1','accepted':True,'detail':'Research individual arrival order now Rare Candy69 then Glimmet70;68 correctly has no arrival. Ledger/prose/evidence agree with previously inspected source frames.'},
  {'repair':'R2','accepted':True,'detail':'Turn5 firstMuk202/evolution204-206, then Glimmet208; observed hand3->2->1. Firstmove timing and candidate suitability corrected.'},
  {'repair':'R3','accepted':True,'detail':'T5Darkness toPawniard;T7Kingambit inherits1 and newDarkness toGlimmet;T9Darkness toKingambit2;T11Helmet first thenDarkness toMuk1;T13Kingambit3. Native243/246 directly inspected confirms retainedKingambit1 and Glimmet attachment effect. Native372/377 directly inspected confirms Helmet first,Kingambit2 unchanged,Muk0->1,Glimmet1. All affected start/end owner typedEnergy states T5-15 verified in current ledger and coherent with original bounded source anchors214/274/297/303/397/402/428/434.'},
 ],
 'structural_validation':json.loads((p/'STRUCTURAL_VALIDATION.json').read_text(encoding='utf-8')),
 'unchanged_material_findings':'Opening, Copycat/search arrivals, Seal restriction, Glimmora no-point, Lucky Ice Pop healing/coins, mixedEnergy theft,180damage and timeoutVictory remain supported by prior bounded direct source checks.',
 'limits':['Fresh live external log save/readback still pending root and not certified here.','Original full battle visual review remains first-pass reviewer scope; this is independent bounded acceptance.','Historical exact20 QR binding is retained with explicit live/artwork limits.'],
}
assert {n:hashlib.sha256((p/n).read_bytes()).hexdigest() for n in checked}==checked,'Eight changed during check'
(out/'CORRECTION_RECHECK.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'accepted':True,'stable_all8':True,'original_rejection_preserved':True,'result':str(out/'CORRECTION_RECHECK.json')}))
