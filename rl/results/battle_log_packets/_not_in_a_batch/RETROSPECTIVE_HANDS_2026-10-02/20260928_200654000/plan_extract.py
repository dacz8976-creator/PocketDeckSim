import json
from pathlib import Path
B=Path(__file__).parent
times=[10,16,33,46,54,55,57,60,69,76,85,93,94,139,141,143,146,152,199,201,203,206,214,250,264,280,283,285,286,288,304,321,328,373,398,400,402,405,413,422,452,465,467,469,472,489,497,547,550,552,555,564]
plan={'new_native_cap':60,'planned_requested_source_seconds':times,'purpose':'Opening five; rank/control anchors; public finds and named Research draws; actual draw-end offsets; pre-attack boundaries; omitted Leaf/Tool/no-target prompt; opened discard; board Energy and controls. Reuse prior 93 bound natives first.','draw_end_locator_estimates':{'2':54,'4':140,'6':200,'8':282,'10':399,'12':466,'14':549},'timing_limits':'1fps source locator estimates; refine using selected native snapshots and actual measuredPTS. Later +3/+6 candidates can contain fast plays and cannot replace selected preplay view.','requested_vs_decoded':'Requested seconds separate from FFmpeg copyts showinfo measuredPTS.','source_identity_receipt':'ROOT_SOURCE_VERIFICATION.json','original_worker_identity_reads':0}
(B/'EXTRACTION_PLAN.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
old=B.parent/'20260908_022627000'/'extract_native.py'
s=old.read_text().replace("B/'SOURCE_VERIFICATION.json'","B/'ROOT_SOURCE_VERIFICATION.json'")
(B/'extract_native.py').write_text(s,encoding='utf-8')
(B/'LOCATOR_SCAN.json').write_text(json.dumps({'status':'visually_inspected','source_sha256':'d4d0dd51f309c05abcdb6b1f04a75c036ca3e59b4abee3f6ce542b2d56149fd6','locator_preprocessing':'LOCATOR_PREPROCESSING.json','sampling_rate_fps':1,'inspected_nominal_seconds':[0,594],'inspected_grids':30,'sample_count':595,'use':'Locate turn banners, public draws, controls, panels and prompts only. No reduced-grid hand identity transcription.','observed_opened_discard_intervals_seconds':[[469,472]],'warning_or_no_target_locator_intervals':[[371,374]],'limits':'Each second sampled, not continuous frame-by-frame screening. Subsecond events and obscured text can be missed; nominal sampling phase and actualPTS not certified in preprocessed grids. Native refs settle fields.'},indent=2),encoding='utf-8')
print('planned',len(times))
