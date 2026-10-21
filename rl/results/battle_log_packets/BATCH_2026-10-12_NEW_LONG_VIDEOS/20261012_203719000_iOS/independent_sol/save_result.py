import pathlib,json,hashlib,datetime
p=pathlib.Path(__file__).resolve().parent.parent
out=p/'independent_sol'
hashes=json.loads((out/'initial_hashes.json').read_text())
now={n:hashlib.sha256((p/n).read_bytes()).hexdigest() for n in hashes}
assert hashes==now,'Packet changed during audit'
repairs=[
 {'id':'R1','turn':13,'seconds':[467.5,468,469],'finding':'Selected f468_00 is not a clean three-card hand before a play. Retained and independently re-extracted 468 s both show Glimmet detached from the fan and moving over the middle bench, with only Glimmora and Lucky Ice Pop remaining in the bottom hand. The ledger calls this three-card starting hand and the evidence calls it pre-play.','required_change':'Inspect the draw-to-placement interval, retain an earlier native full frame plus crops showing all three cards in the hand before Glimmet selection/placement, and bind the starting hand and board to the correct frame. Correct first-move timing or explicitly describe the selected-card transition. Do not label the current 468 s view an unzoomed pre-play hand.'},
 {'id':'R2','turn':3,'seconds':[107.2,149,150,152],'finding':'TURN_LEDGER board_at_start owner energy_zone this_turn is Darkness count 1 available true citing f107_20, but that native frame and fresh source seek show an empty generated slot. At 149 s the full Darkness generated slot is visibly present; the attachment then resolves around 150 to 152 s.','required_change':'Separate the starting hand frame from a native start-boundary Energy Zone frame after generation and before first play, or explicitly preserve the animation/visibility limit. Bind an observed count and availability to evidence that actually shows them. Apply the same empty-slot semantics consistently, including T1 where the declared null-when-empty policy conflicts with Darkness count 0.'}
]
result={'accepted':False,'reviewer':'/root/check_203719','source_video':'20261012_203719000_iOS.MP4','source_sha256':'e85ac056e49ababe79fbd0388e8b132f3cc984a5deb445390a2f4df7b0137869','checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'required_repairs':repairs,'checked_input_sha256':hashes,'packet_unchanged_during_check':True,'fresh_source_frames':['fresh_107.20.jpg','fresh_468.00.jpg','fresh_790.00.jpg'],'scope':'Bounded independent semantic audit, not a second full-source decode. Rejected on selected ordinary-turn hand evidence and board-boundary evidence before completion.'}
(out/'CHECK_RESULT.json').write_text(json.dumps(result,indent=2),encoding='utf8')
report='''# Independent check: rejected pending targeted repairs

Reviewer: /root/check_203719. Source: 20261012_203719000_iOS.MP4. SHA-256: e85ac056e49ababe79fbd0388e8b132f3cc984a5deb445390a2f4df7b0137869.

Read START_HERE_VIDEO_REVIEW.md, Review_Log/README.md, PAUSE_GAMES_REVIEW_PROTOCOL.md and its assignment. Audited all eight final packet files without editing them. The receipt freezes all eight SHA-256 values and confirms no changes during this audit. This was a bounded independent semantic check using retained native frames and three new source seeks, with one decoder thread. The original 1.5 GB video was not rehashed or fully decoded again.

Two source-evidence defects prevent acceptance:

1. Turn 13, 467.5 to 469 s: f468_00 and fresh_468.00.jpg show Glimmet detached from the bottom hand and held over the middle Bench. Only Glimmora and Lucky Ice Pop remain in the bottom fan. This does not satisfy the selected clean three-card hand before the first play. Retain an earlier native frame and crops between the normal Lucky Ice Pop draw and Glimmet selection, bind the hand and board to it, and reconcile the first-play timing.
2. Turn 3, 107.2 s: f107_20 and fresh_107.20.jpg show an empty generated owner Energy slot while the starting board claims one available Darkness Energy from that same frame. A later 149 s native view clearly shows the full generated slot, followed by the attachment around 150 to 152 s. The current hand view can remain useful for names but requires separate actual start-boundary Zone evidence or an explicit animation/visibility limit. The declared empty-slot policy should also be applied consistently to turn 1.

The repaired turn 3 action order is supported by the sampled sequence: Poké Ball first, then Glimmet bench and Alolan Muk evolution, Copycat, Mesagoza and its search, then Darkness to Regigigas near the turn end. The prose does not retain the earlier Energy-first error. Opening five-card identities and Regigigas Active are supported by 28 to 34 s native evidence. Research and search sequences are represented individually: turn 1 Research Glimmora/Poké Ball and Ball Alolan Grimer; turn 3 Ball Glimmet, Copycat Mesagoza/Glimmora and Mesagoza Glimmet; turn 5 Research Ilima/Kingambit. Owner hand counts reconcile through the recorded returns, benching and evolutions, subject to the defective turn 13 selected-hand evidence.

The packet has 21 ordered rows and end-to-end coverage intervals with no claimed gaps. Sampled retained sequences support Ilima saving and rebenching Regigigas, Cyrus bringing it back, its knockout and point 1, the three returned Ice Pops on turn 15, poison knockout, both Glimmora exchanges and final Kingambit promotion. Fresh source 790 s explicitly confirms opponent concession. The result screen at 800.5 s supports Victory, 21 turns and 150 damage. These supported facts do not override the hand/Zone capture defects above.

The documented limits are appropriate: exact live-log deck snapshot absent, filmed QR has separate provenance; unopened discards; overlapping opponent fan ranges; turn 14 uncertain no-target trigger; turn 20 unfilmed effective retreat-cost explanation; approximate seek timestamps. No hidden identity or rules explanation should be invented to fill those limits.

The audit stopped at the material rejection, as assigned. Recheck the corrected packet, including all eight new frozen hashes, before acceptance. Root remains responsible for lead acceptance, shared registration, external entries and archival.
'''
(out/'INDEPENDENT_CHECK.md').write_text(report,encoding='utf8')
print(json.dumps({'accepted':False,'required_repairs':len(repairs),'checked_input_sha256':hashes},indent=2))
