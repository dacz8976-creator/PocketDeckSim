import json, shutil
from pathlib import Path
from datetime import datetime, timezone

B=Path(__file__).resolve().parent
P=B/'20260908_021327000'
files=['TURN_LEDGER.json','ASTRA_QUESTIONS.json','UNCERTAINTIES.json','REVIEW_SUPPLEMENT.md']
backup=P/'before_astra_flower_shield_repair'
assert not backup.exists(), 'Already repaired'
backup.mkdir()
for f in files: shutil.copy2(P/f,backup/f)

old='PrintedabilityrequiresPsychicattachedtoComfey. Comfeyhas0at83/188; protectionstartswhenEnergyattachedT8, evidenced267prevention.'
correct=('Printed Flower Shield protects each owner Pokemon that has Psychic Energy attached while Comfey is in play. '
 'Comfey itself has zero at83/188, but energized Drowzee and Raticate already show protection. '
 'Turn8 attaches Energy to Comfey and adds protection to Comfey itself; it does not start protection for all others. '
 'The old turn2 statement is supported for energized Drowzee, with the per-Pokemon Energy condition qualified.')

def strings(obj):
    if isinstance(obj, str):
        return obj.replace(old,correct).replace('Psychic 0 to 1; Flower Shield condition now met',
          'Psychic 0 to 1; Comfey itself now meets Flower Shield condition, while previously energized owner Pokemon were already protected').replace(
          'Cannot be affected by Special Conditions while Comfey has Psychic Energy attached',
          'Each owner Pokemon with Psychic Energy attached recovers from and cannot be affected by Special Conditions while Comfey is in play; Energy on Comfey is not required for protection of the others')
    if isinstance(obj,list): return [strings(v) for v in obj]
    if isinstance(obj,dict): return {k:strings(v) for k,v in obj.items()}
    return obj

ledger=strings(json.loads((P/'TURN_LEDGER.json').read_text(encoding='utf-8-sig')))
added=0
for row in ledger['turns']:
    for phase in ['board_at_start','board_after']:
        side=row[phase]['owner']
        pokes=[side['active']]+side.get('bench_in_position_order',[])
        if not any(p.get('name')=='Comfey' for p in pokes): continue
        side['board_effects']=[e for e in side.get('board_effects',[]) if not (isinstance(e,dict) and e.get('name')=='Flower Shield')]
        side['board_effects'].append({'name':'Flower Shield','source':'owner Comfey',
          'restriction':'Applies separately to each owner Pokemon with at least one attached Psychic Energy.',
          'basis':'Printed native Comfey ability f0188.00 plus source-bound board attachment counts.',
          'evidence_ids':['f0188.00'], 'status':'printed_condition_applied_to_observed_board'})
        for poke in pokes:
            effects=poke.setdefault('active_effects',[])
            effects[:]=[e for e in effects if not ((isinstance(e,str) and 'Flower Shield' in e) or (isinstance(e,dict) and e.get('name')=='Flower Shield'))]
            count=poke.get('attached_energy',{}).get('by_type',{}).get('Psychic')
            if isinstance(count,(int,float)) and count>=1:
                effects.append({'name':'Flower Shield','source':'owner Comfey',
                  'restriction':'This Pokemon recovers from and cannot be affected by Special Conditions while it has Psychic Energy attached and owner Comfey remains in play.',
                  'basis':'Printed native ability f0188.00; this board records attached Psychic Energy.',
                  'evidence_ids':sorted(set(['f0188.00']+poke.get('evidence_ids',[]))),
                  'status':'printed_condition_applied_to_observed_board'})
                added+=1
(P/'TURN_LEDGER.json').write_text(json.dumps(ledger,indent=2,ensure_ascii=False),encoding='utf-8')
for f in ['ASTRA_QUESTIONS.json','UNCERTAINTIES.json']:
    data=strings(json.loads((P/f).read_text(encoding='utf-8-sig')))
    def qualify(obj):
        if isinstance(obj,dict):
            if obj.get('id')=='C8':
                obj['historical_difference_type']='old_statement_supported_with_per_pokemon_condition; prior_new_draft_rejected'
                obj['status']='repaired_after_astra_check_pending_recheck'
            for v in obj.values(): qualify(v)
        elif isinstance(obj,list):
            for v in obj: qualify(v)
    qualify(data)
    (P/f).write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')
text=strings((P/'REVIEW_SUPPLEMENT.md').read_text(encoding='utf-8-sig'))
text+='\nAstra correction to the new draft: Flower Shield is conditional on Psychic Energy attached to each protected Pokemon. Comfey may protect energized teammates while Comfey itself has no Energy. Turn2 energized Drowzee is already protected; turn8 adds protection to Comfey itself. The historical turn2 statement is preserved and is supported with this per-Pokemon qualification. No attachment counts, card identities, HP or accepted outcome were changed by this correction.\n'
(P/'REVIEW_SUPPLEMENT.md').write_text(text,encoding='utf-8')
(P/'FLOWER_SHIELD_REPAIR_RECEIPT.json').write_text(json.dumps({'schema':'bounded-lead-astra-repair-v1',
 'utc':datetime.now(timezone.utc).isoformat(),'changed_files':files,'before_versions':str(backup),
 'new_original_reads':0,'new_frames':0,'per_pokemon_effect_entries':added,
 'old_packet_unchanged':True,'independent_recheck_pending':True},indent=2),encoding='utf-8')
print('Flower Shield repaired in four files; per-Pokemon effect entries:',added)
