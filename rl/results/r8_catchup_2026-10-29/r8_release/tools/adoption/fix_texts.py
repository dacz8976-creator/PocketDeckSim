"""Assemble adopt_r8_texts.json from the six reviewed drafts (workflow wf_f2ba0a62-59d), applying the verifiers' accepted fixes.
Every replacement asserts its fragment occurs exactly once in the draft text it edits."""
import json, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'drafts')
ld = lambda g: json.load(open(os.path.join(D, f'{g}.draft.json'), encoding='utf-8'))
def rep(t, a, b, what):
    n = t.count(a)
    assert n == 1, f'{what}: fragment occurs {n} times: {a[:80]!r}'
    return t.replace(a, b)

RN = '`rl/results/r8_catchup_2026-10-29/RELEASE_NOTES.md`'
# ---- START_HERE and CLAUDE.md ----------------------------------------------------------------------------------------------
sc = ld('start_claude')
e = sc['edits']
assert [x['path'] for x in e] == ['START_HERE.md', 'CLAUDE.md', 'CLAUDE.md']
t = e[0]['new']
t = rep(t, f'and the rule fixes in {RN} §10)', f'and the rule rows R8-10a to R8-10e and item 11 ({RN} §2))', 'SH rule rows')
t = rep(t, 'C1, SP1 and P-C cards, dual-type Pokémon', 'C1, SP1 and P-C cards (205 of their 260 printings at first), dual-type Pokémon', 'SH 205')
t = rep(t, 'so all 260 C1, SP1 and P-C printings now play (256 Complete, 4 RulesUnverified) and no real printing is refused any more,',
        'so all 260 C1, SP1 and P-C printings now play (256 Complete, 4 RulesUnverified) and the official programs refuse no real printing any more,', 'SH refuse')
t = rep(t, "after kx3's replay check on it (`rl/strength/README.md`);",
        "after kx3's replay check on it (`rl/strength/README.md`); until then it refuses a deck that holds one of the 55 printings main-affe56e could not play;", 'SH slow')
e[0]['new'] = t
CLAUDE_HEAD = """- The official engine program is `rl/engine-2026-11-04/deckgym` (since @@PIN_SHORT@@; @@NAME@@: main-affe56e's engine plus
  R8: upstream's card code through #439, so all 260 Dual Fusion C1, SP1 and P-C printings now play (256 Complete,
  4 RulesUnverified) and the official programs refuse no real printing any more (the card-support refusal stays in the
  code for a card the engine cannot play); the bot-protocol adapter (`deckgym simulate --players proto,...`, opt-in
  `pdl_*` keys); the rule rows R8-10a to R8-10e and item 11 (`rl/results/r8_catchup_2026-10-29/RELEASE_NOTES.md` §2);
  `engine/src/players/` changed for the adapter and the new cards; `rl/engine-2026-11-04/README.md`). The slow report
  stays kx3 on main-affe56e until its re-pin onto @@NAME@@'s engine, after kx3's replay check on it
  (`rl/strength/README.md`): say so when you hand one over. Until then it refuses (exit 2) a deck that holds one of the
  55 printings main-affe56e could not play; one made before Oct 29 ran on an older engine. The working pilot is km3, on both
"""
t = e[1]['new']
cut = t.index('  sides of the screen and the floor.')
e[1]['new'] = CLAUDE_HEAD + t[cut:]
assert e[1]['new'].count('The working pilot is km3') == 1 and 'rule fixes' not in e[1]['new']

# ---- the manifest's field texts ----------------------------------------------------------------------------------------------
mf = ld('manifest')['fields']
mf['goldfish_note'] = rep(mf['goldfish_note'], 'so it refuses no real deck; the check stays in the code.',
                          'so it refuses no deck made of printings in the card list; the check stays in the code.', 'gf note')
b = mf['built']
b = rep(b, "in the clean worktree /home/dacz8976/lane_r8_w at", "in the clean worktree /home/dacz8976/lane_r8_w (cargo in its engine/) at", 'built wt')
b = rep(b, "(rl/results/r8_catchup_2026-10-29/lane/lane_r8.sh).", "(rl/results/r8_catchup_2026-10-29/lane/lane_r8.sh; @@REC@@/logs/lane_R/build_R.log, times in lane_r.log).", 'built log')
i = b.index('@@REC@@/RAN_SHA256.txt shows')
b = b[:i] + ("@@REC@@/RAN_SHA256.txt shows by sha256 that these are the programs the official build made, equal to Lane N's "
             "(48dec4f5, the same engine tree, whose checks are cited), that the official build's 18 replays ran exactly these programs, "
             "that each floor piece ran this deckgym (the floor ran in the laptop's main checkout, whose then-official goldfish, "
             "rl/engine-2026-10-21/goldfish, sha256 db52d3de..., made the coverage files, as for R6's floor2S: @@REC@@/RUN_CONTEXT.txt; "
             "@@NAME@@'s goldfish, run the same way on the 11 floor decks, gives byte-equal coverage: "
             "@@REC@@/logs/floor_recheck_R8/GOLDFISH_R8_COVERAGE.txt), and that the self-checks ran the recorded builds (strength_L for "
             "km3, strength_K8 for kx3).")
mf['built'] = b
ie = mf['identity_evidence']
ie = rep(ie, 'the five programs built from 543dad00 have', 'the five programs built from 543dad00 (deckgym, legality_scan, goldfish, card_status, card_enum_generator) have', 'ie five')
ie = rep(ie, '(km3 81b572198c04d5d1, on R8\'s km3 build; kx3 31d638dbc818b0fa)', "(km3 81b572198c04d5d1 on strength_L, R8's km3 build; kx3 31d638dbc818b0fa on strength_K8)", 'ie sc')
ie = rep(ie, "engine/src/players/: 4 files (mod.rs and protocol_player.rs, new: the protocol adapter's player; opening_class.rs: the new Ability variants' opening class; weighted_random_player.rs: changed for the adapter and the new cards).",
         "engine/src/players/: 4 files (protocol_player.rs, new: the protocol adapter's player; mod.rs, which registers it; opening_class.rs: the new Ability variants' opening class; weighted_random_player.rs: changed for the new cards); Cargo.lock and Cargo.toml unchanged.", 'ie players')
mf['identity_evidence'] = ie
p = mf['purpose']
p = rep(p, 'exists only in a build with the test-utils feature', 'is read only in a build with the test-utils feature', 'purpose tu')
p = rep(p, 'until its re-pin on @@NAME@@, after its kx3 replay check', "until its re-pin onto @@NAME@@'s engine, after its kx3 replay check", 'purpose repin')
p = rep(p, 'until then that program does not play the 55 printings main-affe56e did not play, which the official programs now play.',
        "until then that program refuses (exit 2, the card-support message, after the slow report's registration) a deck that holds one of the 55 printings main-affe56e did not play, which the official programs now play (rl/strength/README.md, \"Unsupported cards\").", 'purpose refuse')
mf['purpose'] = p

# ---- the pointers and the new folder's README --------------------------------------------------------------------------------
pt = ld('pointers')
pe = pt['edits']
pe[2]['new'] = rep(pe[2]['new'], 'all 260 Dual Fusion printings played', 'all 260 C1, SP1 and P-C printings played', 'mp label')
pe[2]['new'] = rep(pe[2]['new'], "(none until the slow report's re-pin on @@NAME@@; it stays kx3 on main-affe56e until then)",
                   "(none until the slow report's re-pin onto @@NAME@@'s engine; it stays kx3 on main-affe56e until then)", 'mp comment')
rd = pt['new_files'][0]['content']
rd = rep(rd, "  - **The rule rows R8-10a to R8-10e and item 11** (4c948025).",
         "  - **The rule rows R8-10a to R8-10e** (R8-10a tests only; RELEASE_NOTES.md §2) **and item 11** (4c948025: every in-play type check now reads the in-play type, closing the Urshifu gap in `../engine-2026-10-29/README.md`'s known limits).", 'rd rows')
rd = rep(rd, "The suite: 2,633 passed, 0 failed, 0 ignored.", "The suite (Lane N, cited under Evidence): 2,633 passed, 0 failed, 0 ignored.", 'rd suite')
rd = rep(rd, "`mod.rs` and `protocol_player.rs` (new; the protocol adapter's player),", "`protocol_player.rs` (new: the protocol adapter's player), `mod.rs` (which registers it),", 'rd mod')
rd = rep(rd, "its checks are cited (coordinator-151):", "its checks are cited (coordinator-151; the five programs: deckgym, legality_scan, goldfish, card_status, card_enum_generator):", 'rd five')
rd = rep(rd, "km3 81b572198c04d5d1, kx3 31d638dbc818b0fa, equal to the pin's texts.", "km3 81b572198c04d5d1 (on strength_L, R8's km3 build) and kx3 31d638dbc818b0fa (on K8's program), equal to the pin's texts.", 'rd sc')
rd = rep(rd, "That engine does not play the 55 printings R8 adds, so until the re-pin the pinned program refuses a deck that holds one of them while the official programs play it (`rl/strength/README.md`).",
         "That engine does not play the 55 C1, SP1 and P-C printings main-affe56e left unimplemented (R8 plays all 260), so until the re-pin a slow report of a deck holding one of them registers and then stops with the pinned program's card-support message (exit 2), while the official programs play it (`rl/strength/README.md`, \"Unsupported cards\").", 'rd refuse')
rd = rep(rd, "(`../results/r8_catchup_2026-10-29/lane/lane_r8.sh`).", "(`../results/r8_catchup_2026-10-29/lane/lane_r8.sh`; `r8_release/logs/lane_R/build_R.log`; `r8_release/RAN_SHA256.txt` shows by sha256 that the replays and the floor ran these programs).", 'rd build log')
pt['new_files'][0]['content'] = rd

# ---- RUN5 -----------------------------------------------------------------------------------------------------------------------
r5 = ld('run5')['edits']
r5[0]['new'] = rep(r5[0]['new'], "and the floor re-check's 12 pieces (24,960 games) give games and coverage files byte-equal to main-affe56e's pages, each page equal apart from the engine path",
                   "and the floor re-check's 12 pieces (24,960 games) equal main-affe56e's pages: the 11 deck pieces' games and coverage files byte-equal, every page equal apart from the engine path", 'r5 floor0')
r5[0]['new'] = rep(r5[0]['new'], "and the bots' play on the new cards is unmeasured", "and the bots' play on the new cards has not been measured", 'r5 unmeasured')
r5[3]['new'] = rep(r5[3]['new'], "`/home/dacz8976/pincand_work/RR_R8_48dec4f5/strength/K8/strength` (sha256 @@KX8_SHA8@@…), both self-checks equal to the pin's texts.",
                   "`/home/dacz8976/pincand_work/RR_R8_48dec4f5/strength/K8/strength` (sha256 @@KX8_SHA8@@…): kx3's self-check on it (31d638dbc818b0fa) and km3's on R8's km3 build, strength_L (81b572198c04d5d1), equal the pin's texts.", 'r5 sc')
r5[3]['new'] = rep(r5[3]['new'], "Until that re-pin, the pinned program still refuses a deck that holds one of the 55 printings main-affe56e did not play (exit 2, the card-support message), while the official programs play it (`rl/strength/README.md`).",
                   "Until that re-pin, a slow report of a deck that holds one of the 55 printings main-affe56e did not play registers and then stops with the pinned program's card-support message (exit 2), while the official programs play the deck (`rl/strength/README.md`, \"Unsupported cards\").", 'r5 refuse')
r5[6]['new'] = rep(r5[6]['new'], "equal to main-affe56e's pages: games and coverage files byte-equal, each page equal apart from the engine path; R8's goldfish gives byte-equal coverage on the 11 floor decks;",
                   "equal to main-affe56e's pages: the 11 deck pieces' games and coverage files byte-equal, each page equal apart from the engine path; R8's goldfish gives coverage byte-equal to main-affe56e's on the 11 floor decks;", 'r5 floor6')
r5.append(dict(path='rl/RUN5.md', old="(205 of their 260 printings implemented; `deckgym simulate`, `optimize` and `goldfish` refuse a deck that holds one of the other 55)",
               new="(205 of their 260 printings implemented; its `deckgym simulate`, `optimize` and `goldfish` refused a deck that holds one of the other 55)",
               why="The kept main-affe56e clause in the status bullet, put in the past so it does not read as R8's behaviour (verifier NIT).", old_count_checked=1))
r5.append(dict(path='rl/RUN5.md', old="no re-baselining, kept at R6 by coordinator-072)", new="no re-baselining, kept at R6 by coordinator-072, and at @@NAME@@'s pin on the same words)",
               why="The yardstick's attribution covers R8's pin too (verifier NIT).", old_count_checked=1))

# ---- rl/strength/README.md --------------------------------------------------------------------------------------------------
sr = ld('strength_readme')['edits']
sr[0]['new'] = rep(sr[0]['new'], 'until its re-pin on @@NAME@@, see', "until its re-pin onto @@NAME@@'s engine, see", 'sr0')
sr[1]['new'] = rep(sr[1]['new'], "The pinned program still refuses them (exit 2, the card-support message; \"Unsupported cards\" above): `slow_report.py` registers the folder, the program then stops after the registration (with `--register-only`, at the first sitting), and the folder keeps its seed slot until it is removed.",
                   "The pinned program still refuses them (exit 2, the card-support message; \"Unsupported cards\" above), so a slow report of such a deck stops with the program's message after its registration (with `--register-only`, at its first sitting), and the registered folder keeps its seed slot until it is removed.", 'sr1 refuse')
sr[1]['new'] = rep(sr[1]['new'], "**Engine (since the slow report's Oct 29 re-pin):**", "**Engine (the pinned program since the slow report's Oct 29 re-pin):**", 'sr1 head')

# ---- the R8 release notes -----------------------------------------------------------------------------------------------------
rn = ld('release_notes')['edits']
rn.insert(0, dict(path='rl/results/r8_catchup_2026-10-29/RELEASE_NOTES.md', old='Every commit from `ebc97535` to the tip is in the adoption list (section 10).',
                  new='Every commit from `ebc97535` to the tip is in the adoption list (section 10), apart from the merge of main (c76ad922, Nov 4: main\'s two newer files, START_HERE.md and a weekly-review file; no engine or deck change).',
                  why='The tip now holds the merge of main, which section 10 does not list (verifier NIT).', old_count_checked=1))
t = rn[3]['new']
t = rep(t, '256 Complete and 4 RulesUnverified (C1 015 Ribombee, C1 051 Jigglypuff, C1 135, C1 184). No real printing is refused any more.',
        '256 Complete and 4 RulesUnverified (C1 015 Ribombee, C1 051 Jigglypuff, C1 135, C1 184). The official programs refuse no real printing any more.', 'rn plain')
t = rep(t, 'Until then, a slow report of a deck that holds one of the 55 printings main-affe56e could not play is refused by its pinned program, while the official programs play that deck.',
        "Until then, a slow report of a deck that holds one of the 55 printings main-affe56e could not play registers and then stops with its pinned program's card-support message (exit 2), while the official programs play that deck.", 'rn plain slow')
t = rep(t, '**Until the re-pin**, a slow report of a deck that holds one of the 55 printings main-affe56e could not play is refused by the pinned program (exit 2, the card-support message), while the official programs play that deck (`rl/strength/README.md`).',
        "**Until the re-pin**, a slow report of a deck that holds one of the 55 printings main-affe56e could not play registers and then stops with the pinned program's card-support message (exit 2), while the official programs play that deck (`rl/strength/README.md`, \"Unsupported cards\").", 'rn slow')
t = rep(t, '- **The harness source does not move.** It is c4f7da21… at affe56e8 and at S8, so the cloud `--program` route and the slow report\'s pin tests are not affected by this commit the way they were at R6.',
        "- **The harness source does not move.** It is c4f7da21… at affe56e8 and at S8 (the pin's hash), so, unlike at R6, no pin test turns red on main and the cloud `--program` route is not held back by this commit (the rl/strength modules give the same results before and after it: \"Checks of the adoption commit\" below).", 'rn harness')
t = rep(t, 'The five programs built from S8 have Lane N\'s sha256', 'The five programs built from S8 (deckgym, legality_scan, goldfish, card_status, card_enum_generator) have Lane N\'s sha256', 'rn five')
t = rep(t, '- The build record is `r8_release/` at @@RECORD8@@ (one parent, S8; it changes only that folder).', '- The build record is `r8_release/` at @@RECORD8@@ (one parent, S8; it changes only that folder), the commit this one sits on.', 'rn record')
rn[3]['new'] = t

# ---- round 2: the rendered-diff review (workflow wf_3f58ce05-9e4) ---------------------------------------------------------------
U55 = 'the 55 printings main-affe56e could not play'          # one wording everywhere
e[0]['new'] = rep(e[0]['new'], 'its reports name the engine they ran on, and those from before Oct 29 ran on older engines.',
                  'every slow report so far ran on main-affe56e or an older engine, and its pages say which.', 'SH r2 reports')
t = e[1]['new']
t = rep(t, """  (`rl/strength/README.md`): say so when you hand one over. Until then it refuses (exit 2) a deck that holds one of the
  55 printings main-affe56e could not play; one made before Oct 29 ran on an older engine. The working pilot is km3, on both
""", """  (`rl/strength/README.md`); until then it refuses (exit 2) a deck that holds one of the 55 printings main-affe56e could
  not play. Every slow report so far ran on main-affe56e or an older engine: say which when you hand one over.
  The working pilot is km3, on both
""", 'CLAUDE r2')
t = rep(t, "hand one over.\n  The working pilot is km3, on both\n  sides of the screen and the floor.", "hand one over.\n  The working pilot is km3, on both sides of the screen and the floor.", 'CLAUDE r2 join')
e[1]['new'] = t
mf['identity_evidence'] = rep(mf['identity_evidence'], 'weighted_random_player.rs: changed for the new cards)', 'weighted_random_player.rs: changed for the adapter and the new cards)', 'ie r2 wrp')
mf['purpose'] = rep(mf['purpose'], 'one of the 55 printings main-affe56e did not play,', f'one of {U55},', 'purpose r2 55')
rd = pt['new_files'][0]['content']
rd = rep(rd, "`r8_release/RAN_SHA256.txt` shows by sha256 that the replays and the floor ran these programs)",
         "`r8_release/RAN_SHA256.txt` shows by sha256 that the official build's 18 replays ran these programs and that each floor piece ran this `deckgym`; the floor's coverage step ran the laptop checkout's then-official `rl/engine-2026-10-21/goldfish`, as for R6's floor2S, and R8's `goldfish` gives byte-equal coverage on the 11 floor decks)", 'rd r2 ran')
rd = rep(rd, "closing the Urshifu gap in `../engine-2026-10-29/README.md`'s known limits)",
         "so Urshifu's Double Type counts; Leaf Cape and the bots' type pricing stay on the printed type: RELEASE_NOTES.md §2 and §12 item 8)", 'rd r2 urshifu')
rd = rep(rd, "That engine does not play the 55 C1, SP1 and P-C printings main-affe56e left unimplemented (R8 plays all 260),",
         "main-affe56e's engine left 55 of the 260 C1, SP1 and P-C printings unimplemented (R8 plays all 260),", 'rd r2 circ')
pt['new_files'][0]['content'] = rd
r5[3]['new'] = rep(r5[3]['new'], 'one of the 55 printings main-affe56e did not play', f'one of {U55}', 'r5 r2 55')
r5[6]['new'] = rep(r5[6]['new'], "R8's goldfish gives coverage byte-equal to main-affe56e's on the 11 floor decks;", "R8's goldfish, run the same way on the 11 floor decks, gives byte-equal coverage;", 'r5 r2 gf')
sr[1]['new'] = rep(sr[1]['new'], 'main-affe56e (next paragraph)', "main-affe56e (the paragraph \"Engine (the pinned program since the slow report's Oct 29 re-pin)\" below)", 'sr r2 next')
sr[1]['new'] = rep(sr[1]['new'], 'one of the 55 printings main-affe56e refused**', f'one of {U55}**', 'sr r2 55')
rn[0]['new'] = rep(rn[0]['new'], 'Every commit from `ebc97535` to the tip is in the adoption list (section 10), apart from',
                   'Every commit from `ebc97535` to S8 (543dad00) is in the adoption list (section 10), apart from', 'rn r2 tip')
rn[0]['new'] = rep(rn[0]['new'], 'no engine or deck change).', 'no engine or deck change). After S8 come the build record and the adoption commit (section 13).', 'rn r2 after')
rn[2]['new'] = rep(rn[2]['new'], 'the adoption commit adds it (section 13).', 'the adoption commit adds it as a new bullet after line 15 (coordinator-155 §3; section 13).', 'rn r2 item9')
rn[3]['new'] = rep(rn[3]['new'], 'So the screen, the floor and the brew pages play every deck of real cards on @@NAME@@.',
                   'So the screen, the floor and the brew pages (goldfish) play every deck made of printings in the card list on @@NAME@@.', 'rn r2 every')

out = dict(schema='adopt_r8_texts v1', source='workflow wf_f2ba0a62-59d drafts with the verifiers\' accepted fixes (fix_texts.py)',
           start_here=[e[0]], claude=[e[1], e[2]], manifest_fields=mf, pointers=pe, new_dir_readme=pt['new_files'][0]['content'],
           run5=r5, strength_readme=sr, release_notes=rn)
json.dump(out, open(os.path.join(os.path.dirname(D), 'adopt_r8_texts.json'), 'w', encoding='utf-8', newline='\n'), indent=1, ensure_ascii=False)
print('written; edits:', {k: len(v) for k, v in out.items() if isinstance(v, list)})
