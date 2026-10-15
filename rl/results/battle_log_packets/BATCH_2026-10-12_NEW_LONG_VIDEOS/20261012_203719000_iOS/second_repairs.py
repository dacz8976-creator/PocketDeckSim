import json, hashlib
from pathlib import Path

p = Path(__file__).parent
z = p / 'zone_observations.py'
s = z.read_text(encoding='utf-8')
prefix, rest = s.split('OWNER_START=', 1)
line, suffix = rest.split('\n', 1)
values = eval(line)
assert values[8] == ('Darkness', 'Darkness')
values[8] = ('Darkness', None)
z.write_text(prefix + 'OWNER_START=' + repr(values) + '\n' + suffix + "\nLIMITS[('start',9,'owner')]='At 358 s, the current Darkness token is visible during generation animation, but the small next marker is absent or obscured. Its type, count and availability remain unknown.'\n", encoding='utf-8')

b = p / 'build_packet.py'
s = b.read_text(encoding='utf-8')
old = "next={'type':'Darkness','count':1,'available':None},evidence_ids=[eid(dt)]"
new = "next={'type':None if turn==3 else 'Darkness','count':None if turn==3 else 1,'available':None,'visibility':'absent_or_obscured' if turn==3 else 'visible_preview_icon'},limit_reason='At 107.5 s, the current Darkness token is visible but the small next marker is absent or obscured. No next type, count or availability is inferred.' if turn==3 else None,evidence_ids=[eid(dt)]"
assert s.count(old) == 1
s = s.replace(old, new)
old = "  if k=='energy_attachment':item['energy']="
new = "  if n==19 and i==1:\n   retain(732);item['evidence_ids']=[eid(722),eid(732)];item['result_observed_at_source_seconds']=732;item['basis']='Attachment action at about 723 s, with preplay board at 722 s and resulting board at 732 s clearly showing three Darkness on Kingambit. The 732 s observation is later than the attachment, not its exact resolution timestamp.'\n  if k=='energy_attachment':item['energy']="
assert s.count(old) == 1
s = s.replace(old,new)
old = "save('SUMMARY.json',summary)"
new = "summary['second_independent_repairs']=dict(prior_files='before_second_independent_repairs_20261012T235813Z',turn_3_later_next='Null at 107.5 s; small marker absent or obscured',turn_9_start_next='Null at 358 s; small marker absent or obscured',turn_19_attachment_proof=['f722_00','f732_00'],supported_hands_actions_outcome_unchanged=True)\n" + old
assert s.count(old) == 1
b.write_text(s.replace(old,new), encoding='utf-8')

notes = p / 'INDEPENDENT_REPAIR_NOTES.md'
with notes.open('a', encoding='utf-8') as f:
 f.write('\nSecond recheck repairs: The current eight files and their hashes were preserved in `before_second_independent_repairs_20261012T235813Z`. The next Energy type, count and availability are now null at the turn 3 later observation, 107.5 seconds, and turn 9 start, 358 seconds. Both frames show the current Darkness token but no readable small next marker. Turn 19 attachment retains the 722-second preplay view and adds native f732_00, whose resulting board clearly shows three Darkness icons on Kingambit. The action remains approximately 723 seconds; 732 seconds is explicitly a later observation, not an exact resolution time. No supported hand, other action, hidden identity or outcome was changed.\n')
print('Three narrow repairs applied to persistent builder and notes.')
