import json, hashlib, subprocess
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parent.parent
ev=json.loads((root/'TURN_EVIDENCE.json').read_text(encoding='utf-8-sig'))
ledger=json.loads((root/'TURN_LEDGER.json').read_text(encoding='utf-8-sig'))
source=json.loads((root/'SOURCE.json').read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''): h.update(b)
 return h.hexdigest()
video=Path(source['source_path_at_review']);s0=video.stat();vsha=sha(video);s1=video.stat()
assert vsha==source['sha256'] and s0.st_size==s1.st_size==source['bytes'] and s0.st_mtime_ns==s1.st_mtime_ns
bound=[]
for sec in [30,177,375]:
 out=root/'independent_sol'/f'source_check_{sec}.jpg'
 subprocess.run([r'C:\Program Files\MiniTool Screen Recorder\FFmpeg\ffmpeg.exe','-hide_banner','-loglevel','error','-threads','2','-ss',str(sec),'-i',str(video),'-frames:v','1','-q:v','2','-y',str(out)],check=True)
 retained=root/'turn_evidence'/f't{sec:07.2f}.jpg'
 assert sha(out)==sha(retained)
 bound.append({'seconds':sec,'independent_decode':out.name,'retained_frame':str(retained.relative_to(root)),'sha256':sha(out),'byte_identical':True})
ids={f['evidence_id'] for f in ev['frames']}
assert len(ids)==len(ev['frames'])
for f in ev['frames']:
 assert f['source_sha256']==vsha and f['source_video']==source['video_basename']
 assert 0<=f['requested_source_seconds']<=source['duration_seconds']
 for path,size in [(f['full_frame_path'],(1170,2532)),(f['bottom_crop']['path'],(1170,507)),(f['top_crop']['path'],(1170,620))]:
  with Image.open(root/path) as im: assert im.size==size,(path,im.size)
 assert f['bottom_crop']['pixel_bounds_x0_y0_x1_y1']==[0,2025,1170,2532]
def walk(obj):
 if isinstance(obj,dict):
  for k,v in obj.items():
   if k=='evidence_ids': assert all(x in ids for x in v),v
   walk(v)
 elif isinstance(obj,list):
  for v in obj:walk(v)
walk(ledger)
assert [t['turn_number'] for t in ledger['turns']]==list(range(1,12))
for t in ledger['turns']:
 assert [a['order'] for a in t['plays_in_order']]==list(range(1,len(t['plays_in_order'])+1))
 for key in ['board_at_start','board_after']:
  b=t[key]
  for who in ['owner','opponent']:
   z=b[who]['energy_zone'];assert 'this_turn' in z and 'next' in z
   for mon in ([b[who]['active']] if b[who]['active'] else [])+b[who]['bench_in_position_order']:
    for req in ['hp_now','hp_max','damage','attached_energy','tool','special_conditions','active_effects']:assert req in mon
    assert mon['hp_max']-mon['damage']==mon['hp_now']
    assert sum(mon['attached_energy']['by_type'].values())==mon['attached_energy']['total']
 if t['who_played']=='owner':
  end=t['timing']['draw_animation_end_seconds']
  candidates=[f for f in ev['frames'] if f['turn_number']==t['turn_number']]
  for off in [1,3,6]:assert any(f['requested_source_seconds']==end+off and f['offset_after_draw_seconds']==off for f in candidates)
  assert any(f['selected_for_start_hand'] for f in candidates)
 print('TURN',t['turn_number'],'handend',t['owner_hand_end'],'score',t['board_after']['owner']['points'],t['board_after']['opponent']['points'])
deck=json.loads((root/'DECK_USED.json').read_text(encoding='utf-8-sig'));assert len(deck['cards_in_log_order'])==sum(x['count'] for x in deck['counts_by_name_and_variant'])==20
core=['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
hashes={name:sha(root/name) for name in core}
receipt={'source_sha256':vsha,'source_size':s1.st_size,'stable_during_hash':True,'native_bindings':bound,'frame_sets':len(ev['frames']),'structural_pass':True,'checked_input_sha256':hashes}
(root/'independent_sol'/'INTEGRITY_CHECK.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print('INTEGRITY',json.dumps(receipt))
