# Japanese-Language Sources Research — Pokémon TCG Pocket (ポケポケ) Rules

Scope: Japanese-language sources only (official JP site/help, Game8, AppMedia, GameWith, 神ゲー攻略, altema, wikiwiki, X/Twitter 検証 posts quoted in articles). Answering QUESTIONS.md.

Grades: OFFICIAL (official JP page) / OFFICIAL-QUOTED (official JP text quoted by third party) / OBSERVED (a verification post/video showing the behaviour) / COMMUNITY (community consensus, no direct evidence) / MEMORY-UNVERIFIED (my own training data, not sourced this session — do not trust).

Work in progress — appending as research proceeds.

---

## Findings by question number


### Q1 — Deck construction, energy type declaration
No JP source found specifying a limit on the number of Energy types (1–3) a deck may declare, or restrictions on declaring unused types. (Not found this session.)

### Q2 — Opening hand guarantee / mulligan
Grade: OFFICIAL-QUOTED (via GameWith, matches official mechanics widely repeated)
Source: https://gamewith.jp/pokemon-tcg-pocket/462758
JP: "ポケポケでは、最初の手札5枚で必ずたねポケモンが1枚以上引けるようになっています"
EN: "In Pocket, your opening hand of 5 is guaranteed to include at least one Basic Pokémon."
No explicit mention of *how* it's guaranteed (redraw vs forced-include) or of a mulligan process — consistent with community understanding that the app silently re-shuffles/re-deals until a Basic is present, but no source states the exact mechanism. No opponent-reveal-of-mulligan mechanic (unlike physical TCG) was found.

### Q3 — Setup: Active + Bench simultaneous/face-down
Grade: COMMUNITY (GameWith)
Source: https://gamewith.jp/pokemon-tcg-pocket/462758
Setup sequence described: coin flip → draw 5 → place 1 Basic face-down as Active → optionally place up to 3 Basics on Bench (face-down) → reveal simultaneously. No source found on a setup time limit specifically.

### Q4 — Who goes first
Grade: OFFICIAL-QUOTED / COMMUNITY
Source: https://game8.jp/pokemon-tcg-pocket/650690
JP: "先攻と後攻はコイントスでランダムに決まります"
EN: "First/second player is decided randomly by a coin toss." Outcome cannot be chosen/controlled. No JP source found describing whether the flip result is shown before or after setup, or Ranked-specific differences.

### Q5 — First-turn restrictions
Grade: OFFICIAL-QUOTED (Game8/GameWith, consistent across sources)
Sources: https://game8.jp/pokemon-tcg-pocket/650690 , https://gamewith.jp/pokemon-tcg-pocket/462758 , https://game8.jp/pokemon-tcg-pocket/650545
- P1 (先攻) gets NO Energy Zone energy on turn 1: "先攻は1ターン目にエネルギーゾーンが使えない" / "先行1ターン目にはエネルギーが出現しない". Card effects that attach energy (e.g. Misty/カスミ) still work on turn 1 for P1.
- Evolution banned turn 1 for BOTH players: "1ターン目は先攻・後攻ともに進化をさせることはできません"
- Attacking: P1 CAN attack turn 1 if it has energy via a card effect or a 0-cost attack (app differs from physical: "physical: 攻撃できない (cannot attack) / App: 攻撃できる (can attack)" per Game8 650545).
- Supporter: not explicitly restricted to non-turn-1 in any JP source found — comparison page (650545) implies Supporters are usable turn 1 for both, consistent with English official FAQ found by another agent. No JP source explicitly confirms retreat-turn-1 rules.

### Q6 — Energy Zone
Grade: COMMUNITY (GameWith + independent blog, consistent)
Sources: https://gamewith.jp/pokemon-tcg-pocket/462758 , https://kodakphotoprinter.jp/472/
- Energy generation timing: "ターンの初めに、エネルギーが1個増える" / "毎ターン開始時にエネルギーゾーンにエネルギーが1つ供給されます" — generated at the START of the turn.
- P1 turn 1: NO energy is generated at all ("先行1ターン目にはエネルギーが出現しない").
- With multiple declared types: "複数のエネルギーを設定した場合、その供給は完全にランダムで行われ、確率は均等に割り振られます" — uniformly random, equal probability per declared type each turn (independent draws implied, not explicitly stated as independent across turns).
- No JP source found explicitly confirming whether the "next energy" preview is visible to the opponent, or whether unattached Energy Zone energy is discarded at end of turn.

### Q7 — Energy attachment
Not directly covered by JP sources found this session beyond "once per turn from the Energy Zone" being implicit in all rule summaries. No explicit JP confirmation found on attaching to a Pokémon played the same turn.

### Q8 — Draw / hand limit
Grade: OFFICIAL-QUOTED (Game8, clear and specific)
Source: https://game8.jp/pokemon-tcg-pocket/650710
JP: "ポケポケでは手札を最大10枚まで所持することができます。" / "手札に既に10枚カードがある場合、11枚目以降はデッキから引くことができなくなります。" / "手札が10枚ある場合、デッキから一番上のカードをトラッシュすることはありません。単純にカードを引けなくなるだけ"
EN: Hand max is 10. If hand already has 10, you simply CANNOT draw further cards (the draw is skipped/blocked) — the top deck card is NOT discarded. This directly answers Q8: draw is skipped, not capped-and-discarded.
Deck-out: Grade OFFICIAL-QUOTED, source https://game8.jp/pokemon-tcg-pocket/651087 : "ポケポケでは対戦中にデッキ残数が0枚になっても負けにはなりません。" — No draw, no loss, game continues normally. Confirms Q15 also.

### Q9 — Order of actions / after attack
No specific JP source found beyond general structure (attach energy, play Pokémon, Trainers, evolve, Abilities, retreat — in any order — then attack ends the turn). GameWith (462758) lists the action phase as free-order before the single attack. No source found on anything usable after attacking.

### Q10 — Timers / turn cap
Grade: OFFICIAL-QUOTED (Game8, specific numbers)
Source: https://game8.jp/pokemon-tcg-pocket/650664
JP: "相手プレイヤーの持ち時間20分が切れたら試合が強制終了となり、勝利となります" — each player has a 20-minute time bank; if the OPPONENT's time expires, you win (forced match end).
JP: "お互いのターンが30ターン経過すると強制引き分けになります" — after 30 total turns (versus matches) the match is forced to a draw. Solo/AI battles: 50-turn cap mentioned by same source family (see Q49).
No JP source found on a per-turn (as opposed to total bank) time limit distinct from the 20-minute total bank.

### Q11 — Pokémon Checkup order
Grade: OFFICIAL-QUOTED / COMMUNITY (Game8, cross-checked with GameWith/Altema — consistent)
Source: https://game8.jp/pokemon-tcg-pocket/650844
Processing order confirmed: poison (どく) → burn (やけど) → sleep (ねむり) → paralysis (まひ), and it explicitly processes "お互いのバトルポケモンの特殊状態の処理" (BOTH players' Active Pokémon's conditions), regardless of whose turn it is — i.e., Checkup is not player-specific, it's a single shared step between turns that checks both active Pokémon together. No JP source found detailing KO-during-Checkup point/promotion specifics beyond the general simultaneous-KO material under Q14.

### Q12 — Points
Grade: OFFICIAL-QUOTED (Game8/GameWith, and independent confirmation)
- Regular Pokémon KO = 1 point; ex Pokémon KO = 2 points: "ポケモンexを倒した場合は2ポイント獲得できる"
- Mega Evolution ex KO = 3 points, confirmed via https://game8.jp/pokemon-tcg-pocket/710998 : "倒されると一度に3ポイント取られてしまう" (being defeated costs the owner's opponent... i.e. opponent gains 3 points at once).
- First to 3 points wins: "先に3ポイント獲得した方が勝利"

### Q13 — Loss when no Pokémon in play
Grade: OFFICIAL-QUOTED (GameWith)
JP: "自分の場にポケモンが1匹もいなくなったプレイヤーは敗北" — a player with zero Pokémon in play loses, independent of point count. No explicit JP source on exact timing (immediate vs. end-of-Checkup) found, but phrasing implies it is checked as a standing state, likely immediately when it becomes true (consistent with "opponent's field empty = win" listed as a distinct, immediately-resolving win condition on Game8 650664).

### Q14 — Simultaneous win conditions / draw
Grade: OFFICIAL-QUOTED (Game8/GameWith consistent)
JP: "お互いのポイントが3ポイントに到達した場合は引き分けとなります" — draw if both hit 3 points simultaneously.
JP: "両者の場にポケモンがいなくなる" → draw when both players simultaneously have zero Pokémon in play.
This directly confirms: no sudden death, no tiebreak-by-current-player — true simultaneous double-win/loss conditions produce a draw. (Matches Q14's "draw?" hypothesis.)
Note: a related community/verification page exists on simultaneous-KO promotion order (pokecabook.com/archives/34253, title: "お互いのバトルポケモンが同時にきぜつしたとき、どちらが先にバトル場にポケモンを出しますか？") but the fetch was blocked (403) — flagged as unresolved, worth re-attempting. CAUTION: that source's URL/phrasing uses physical-TCG terms so it may describe the paper game, not Pocket — needs verification before use.

### Q15 — Deck-out, concede/disconnect
Grade: OFFICIAL-QUOTED (Game8)
Confirmed deck-out is NOT a loss (see Q8 section). No JP source found this session on concede/disconnect handling specifically.

### Q16 — Damage calculation order
Grade: OBSERVED (community verification blog, technical and specific) + OFFICIAL-QUOTED (GameWith numeric confirmation)
Sources: https://gamewith.jp/pokemon-tcg-pocket/466440 (via WebFetch synopsis), https://did2memo.net/2024/12/23/pokemon-tcg-pocket-sakaki/
- Weakness formula: "最終的な与えたダメージに20加算する" — flat +20 added to final damage.
- Worked order example from GameWith: "10(ワザのダメージ)+20(弱点)-20(ワザの効果)" — i.e., base damage, THEN weakness (+20), THEN reduction effects (−X) are subtracted AFTER weakness. This is a direct, explicit order confirmation: Weakness is applied BEFORE defender-side reduction, not after.
- Weakness does NOT apply when the attack's damage is 0, when the attack "fails," when all coin flips are tails, or to damage from status conditions (poison etc.) — i.e., Weakness requires nonzero attack damage to exist first.
- Attacker-side flat modifiers (e.g. Sakaki/Giovanni's "+10"): apply strictly to "ワザ" (attack) damage against the opponent's ACTIVE Pokémon only — confirmed via did2memo.net's detailed breakdown of cases where the +10 does NOT apply (ability/特性 damage, bench-targeted portions of multi-target attacks, and 0-damage attacks). This confirms attacker modifiers are attack-scoped and Active-target-scoped, feeding directly into Q17/Q19.

### Q17 — Weakness/reduction on Bench
Grade: OFFICIAL-QUOTED (GameWith) + OBSERVED (did2memo.net)
JP (GameWith): weakness explicitly listed as invalid "ベンチのポケモンにダメージを与えた" (when the damage is dealt to a Benched Pokémon) — CONFIRMS Weakness does NOT apply to Bench damage from an attack.
JP (did2memo.net): Sakaki's/Giovanni's "相手のバトルポケモンへのダメージを+10する" is worded as Active-only, and multi-target attacks like Zebraika's Thunder Arrow that also hit Bench get NO bonus on the Bench-damage portion — supporting that attacker-side flat bonuses, like Weakness, are Active-target-only. No explicit JP source found on whether a Benched Pokémon's own damage-reduction effects (its own Ability, e.g.) still apply to bench damage it takes — likely yes since these are defender-side and not weakness-gated, but unconfirmed.

### Q18 — "Prevent all damage" vs "prevent all effects of attacks"
Not found in JP sources this session — no direct treatment located. Flagged unresolved.

### Q19 — Damage vs "damage from attacks"
Grade: OBSERVED (did2memo.net)
JP: "つまり、「特性」でダメージを与える場合、「ワザ」ではないため" (i.e., since Ability damage is not "attack" damage, [the attack-only bonus] does not apply). This confirms the general principle that Pocket's engine distinguishes "ワザ (attack) damage" from "特性 (Ability) damage" as separate categories for the purposes of effects that reference "attack damage" specifically — supporting the hypothesis in Q19 that Rocky-Helmet-style/ability damage and poison/burn are NOT counted as "damage from attacks" for reduction effects worded that way. No JP source directly testing a "−X damage from attacks" reduction card against poison/burn/Rocky-Helmet-style damage was found — inference only, not a direct test.

### Q20 — Knock Out timing / multiple KOs
No direct JP source found this session on whether multiple simultaneous KOs (Active+Bench from one attack) both award points, or the exact recoil-KO point attribution. Flagged unresolved (see Q14 note on the blocked pokecabook.com article, which may be relevant if it can be re-fetched).

### Q21 — "When damaged by an attack" retaliation vs KO
Not found in JP sources this session (Rocky Helmet / Gotsu Gotsu Metto ゴツゴツメット timing vs. simultaneous KO). Search located card-list pages only, not a rules breakdown; flagged unresolved for further searching.


### Q22 — Special condition exact values/timing
Grade: OFFICIAL-QUOTED / COMMUNITY (Game8 650844, GameWith 462758, hp-no-game-no-life.com — all consistent)
- Poison: 10 damage per Checkup, both turns (no flip, unconditional, stacks with Burn).
- Burn: 20 damage per Checkup, then a coin flip — heads cures.
- Sleep: coin flip at Checkup — heads wakes. Blocks attacks and retreat.
- Paralysis: blocks attacks and retreat; recovers automatically (no coin flip) once the owner's next turn's Checkup passes — no source found stating an exact "until end of owner's next turn" phrase, but all sources agree it is unconditional/automatic recovery (distinguishing it from Sleep/Burn's coin-flip recovery).
- Confusion: coin flip on attack attempt; tails = attack fails, turn ends. CONFIRMED NO SELF-DAMAGE on tails (see Q22/contradiction note below) — this is a Pocket-specific deviation from the physical TCG.

### Q23 — Which conditions coexist
Grade: OFFICIAL-QUOTED (Altema, jyoutai page)
JP: "どくとやけどと重複可能" — Poison and Burn CAN coexist with each other and with the sleep/paralysis/confusion trio.
JP: sleep/paralysis/confusion are mutually exclusive and "上書可能" (a new one overwrites the old) — only one of {Sleep, Paralysis, Confusion} can apply at a time, but either can combine with Poison and/or Burn simultaneously. This confirms Q23 fully: yes, a Pokémon CAN be simultaneously Poisoned AND Burned (and additionally Asleep/Paralyzed/Confused).

### Q24 — Abilities/retreat/switching while affected
Grade: COMMUNITY (hp-no-game-no-life.com, cross-referenced; note some source material was for physical TCG and excluded)
- No JP source found this session explicitly stating whether Abilities can be used while Asleep/Paralyzed/Confused; by omission (only attacks+retreat are called out as blocked for Sleep/Paralysis, and only attacks for Confusion), the implication across all sources is Abilities are NOT blocked by any special condition in Pocket. This is an inference from silence, not a direct statement — flagged as needing a direct verification post.
- Being switched out by Trainer/effect while Asleep/Paralyzed: CONFIRMED possible and this is itself a cure method (see Q25). Retreat while Confused: not blocked (only Sleep/Paralysis block retreat) — Confused Pokémon CAN retreat.

### Q25 — What removes conditions
Grade: OFFICIAL-QUOTED / COMMUNITY (Altema jyoutai + hp-no-game-no-life.com, consistent)
- Retreat / switching to Bench: cures Sleep, Confusion (and implicitly Paralysis, since Bench Pokémon aren't checked) — JP: "ベンチのポケモンと交換すると回復可能"
- Evolution: cures ALL special conditions — JP: "バトルポケモンが進化すると回復"
- Specific cards/abilities/Items: can cure any condition per card text.
- Sleep: additionally curable by its own Checkup coin flip (heads).
- Burn: additionally curable by its own Checkup coin flip (heads).
- Paralysis: per hp-no-game-no-life.com, listed cures are "進化する、特定の特性、グッズによって治せる" (evolution, specific Abilities, Items) — notably NOT a Checkup coin flip (paralysis has no flip; it clears unconditionally with time instead, per Q22).
- No explicit JP statement found on whether HP-healing (e.g. Potion) by itself removes conditions (expected: no, unless the card also says so) — unresolved, inference only.

### Q26 — Poison damage modifiers (Nihilego-style)
Not resolved this session — could not locate a Pocket-specific JP source on stacking behavior of "poison damage +10"-style effects, or whether they apply to all opponent Pokémon or only the currently-poisoned Active. Flagged unresolved; WebSearch budget was exhausted before this could be chased further (GameWith's どく card-list page also 403'd on later fetch attempts).

### Q27 — Sleep flip timing
Grade: COMMUNITY (hp-no-game-no-life.com) — direct and clear
JP (exact quote, <15 words): "直前のポケモンチェック時に、コイン投げて表が出たら回復する"
EN: "[Sleep clears if,] at the immediately-preceding Pokémon Checkup, a coin flip comes up heads."
This CONFIRMS Q27's hypothesis: the sleep-cure flip happens at the Checkup that occurs right before the affected Pokémon's own turn would start (i.e., the very next Checkup after being put to sleep), giving the victim a chance to wake up before it would need to act. Since Checkup happens after every turn (processing both active Pokémon regardless of whose turn is next, per Q11), a Pokémon put to sleep during the opponent's turn is checked at the very next Checkup — which is the one immediately preceding its own upcoming turn.

### Q28 — Evolution restrictions
Grade: OFFICIAL-QUOTED (Rare Candy's own printed card text, plus GameWith/Game8 turn-1 rule)
- Confirmed: no evolving on either player's first turn ("1ターン目は先攻・後攻ともに進化をさせることはできません", see Q5).
- Confirmed via the OFFICIAL Rare Candy (ふしぎなアメ) card text itself (grade OFFICIAL — this is printed card text, quoted by Game8): "（最初の自分の番や、出したばかりのポケモンには使えない。）" — "(Cannot be used on your own first turn, or on a Pokémon that was just put into play.)" This is the general "can't evolve a Pokémon the turn it entered play" restriction, confirmed to also gate Rare Candy specifically (contradicts a separate blog's imprecise paraphrase claiming Rare Candy has no turn-1/just-played restriction — the actual card text says otherwise; the blog was likely describing "can Rare Candy on turn 2" for a Basic played turn 1, not an exception to the restriction).
- No JP source found on "twice in one turn on the same Pokémon" or whether Active and Bench can both evolve in the same turn (though nothing suggests either is restricted beyond the standard once-per-Pokémon/turn-placed rules).

### Q29 — What carries over / resets on evolution
Grade: OFFICIAL-QUOTED / COMMUNITY (Altema jyoutai, GameWith, Game8 tool page)
- Damage: carries over (standard, universally assumed/confirmed by all condition-clearing language which only discusses conditions, not damage reset).
- Special Conditions: ALL removed on evolution ("バトルポケモンが進化すると回復" — see Q25).
- Tools: remain attached through evolution — JP (Game8 665689): "番が終わったり、『にげる』や進化をしても、トラッシュしません" (Tools are not discarded at end of turn, on retreat, or on evolution).
- Energy: carries over (implicit/standard; not directly quoted this session).
- No JP source found on whether evolving resets Ability once-per-turn usage restrictions, or on whether attack-inflicted effects like "can't attack next turn" persist through evolution — flagged unresolved.

### Q30 — Rare Candy / Mega Evolution ex
Grade: OFFICIAL (printed card text, via Game8)
Rare Candy exact text: "自分の手札から2進化ポケモンを1枚選び、そのポケモンへと進化する自分の場のたねポケモンにのせ、1進化をとばして進化させる。（最初の自分の番や、出したばかりのポケモンには使えない。）"
EN: Choose a Stage 2 Pokémon from hand, place it on a Basic Pokémon in play, evolving it and skipping Stage 1. Cannot be used on your own first turn or on a Pokémon just put into play.
Mega Evolution ex: Grade OBSERVED/COMMUNITY (Game8 710998) — evolves like a normal evolution from the previous stage ("通常の進化と同じように、1段階前のポケモンからメガシンカすることができます"); being Knocked Out gives the opponent 3 points at once. NO JP source found stating a physical-TCG-style "Mega Evolving ends your turn" rule for Pocket — its absence from every rules-comparison page found (which do call out other differences explicitly) is suggestive that no such restriction exists in Pocket, but this is not a direct confirmation. No JP source found on a Mega-specific deck limit distinct from the normal 2-copies-per-name rule.

### Q31 — Retreat mechanics
Grade: OFFICIAL-QUOTED (GameWith 466442, altema/toreca-hack for status blocking)
- JP: "「にげる」を使うにはカードの「にげる」に書かれているマーク数のエネルギーを、バトルポケモンから[トラッシュする]" — retreat discards the Energy amount shown on the card, from the Active Pokémon (owner controls which specific attached Energy is discarded — not explicitly stated but implied by "から" [from the Active] with no further specification; no source explicitly confirms player choice of WHICH energy when multiple types are attached).
- Retreat-cost reduction: confirmed via Tool card "スピーダー" (Speeder): "「スピーダー」を使うことで、必要なエネルギーを1個減らすことができます" (reduces retreat cost by 1).
- Blocked while Asleep/Paralyzed: CONFIRMED — "バトル場のポケモンが「ねむり」「マヒ」になっていると、逃げることができません"
- Switch effects vs. retreat: NOT resolved directly — GameWith's retreat page acknowledges forced-switch effects exist from attacks/Abilities/Supporters ("ワザや特性、サポートカードにはベンチとの交代を強制されるものがあります") but does not state whether they count as "retreat" (and thus cost Energy / are blocked by Sleep-Paralysis / limited to once per turn) or are a separate free action. Given Sabrina's (サブリナ) effect works by forcing an opponent's Active↔Bench swap with no Energy cost mentioned, these Trainer-forced switches are almost certainly NOT the same action as a manual retreat (no Energy discard) — but no source explicitly states they bypass the Sleep/Paralysis block. Flagged as needing direct verification.

### Q32 — Promotion after KO
Not resolved with a Pocket-specific source this session. The best-candidate community article (pokecabook.com/archives/34253) on simultaneous-KO promotion order returned HTTP 403 on every fetch attempt and its title uses physical-TCG-style phrasing ("サイド"-adjacent conventions), so it cannot be confirmed as Pocket-specific even if it had loaded. Flagged unresolved.

### Q33 — Effects ending when Active moves to Bench
No JP source found this session beyond the general fact that switching to Bench cures special conditions (Q25). Attack-granted effects like "no damage next turn" ending on retreat were not directly tested in any source found. Flagged unresolved.

### Q34 — "Once during your turn" Ability scope
Not resolved this session with a direct JP source (the general once-per-turn Ability language appears throughout card text summaries, but no source tested whether it's per-instance, whether Bench-Ability use counts, or whether evolving resets the counter). Flagged unresolved — note the earlier (English-track) finding that Buzzwole ex's attack-repeat restriction resets on returning to Bench is suggestive but is an attack-restriction, not an Ability, and is card-specific.

### Q35 — Same-name Ability stacking
Not resolved this session. No JP source found.

### Q36 — Triggered Ability timing
Not resolved this session with a direct general-rule source. Card-specific examples exist in bulk (e.g. "when played from hand," "when Knocked Out") but no rules article enumerating general trigger-timing rules was found in JP this session.

### Q37 — Supporters: one per turn, unplayable cards
Grade: COMMUNITY (Yahoo Chiebukuro Q&A, corroborated logic)
Relevant finding: Supporters can become legitimately unusable/greyed-out due to UNMET TARGET CONDITIONS, not just the once-per-turn limit — e.g., a healing Supporter cannot be used if no eligible (damaged, matching-type) Pokémon exists, and a bench-targeting Supporter cannot be used if the opponent has no Benched Pokémon. This confirms the game's UI DOES block genuinely unplayable Trainer cards rather than allowing a "no-op" play. (One respondent in the same thread noted occasional evolution/Supporter-timing bugs, e.g. being able to evolve on the very first turn of the player going second in rare cases — unverified single report, not corroborated elsewhere; treat as MEMORY-UNVERIFIED-adjacent community anecdote, not a confirmed rule.)

### Q38 — Tools
Grade: OFFICIAL-QUOTED (Game8 665689)
- One per Pokémon: "ポケモンのどうぐは、1匹に1枚までしかつけられず"
- Cannot be moved/removed once attached: "つけたら張り替え・回収はできません"
- Discarded when the Pokémon leaves play other than normal survival: e.g. when a Pokémon with a Tool returns to hand via an effect, the Tool is NOT recovered with it — "ポケモンのどうぐは回収できず、そのままトラッシュされてしまいます" (the Tool cannot be recovered and is simply discarded) — implies Tools ARE discarded specifically when the Pokémon itself leaves play (KO'd, returned to hand, etc.), consistent with the general rule that Pokémon-attached cards go to the trash when the Pokémon does.
- Tools persist through end of turn, retreat, and evolution (do NOT fall off then): "番が終わったり、『にげる』や進化をしても、トラッシュしません"
- HP-boosting Tool examples found: 大きなマント (+20 max HP), リーフマント (+30 max HP for Grass types). No JP source found directly testing what happens if an HP-boosting Tool is removed (e.g. by an opponent's Tool-removal effect) while damage taken already exceeds the reduced (post-removal) max HP — i.e., whether this causes an immediate KO. Flagged unresolved.

### Q39 — Stadiums
Not resolved with a Pocket-specific source this session. General TCG stadium mechanics (one in play; symmetric effects) were found via https://game8.jp/pokemon-tcg-pocket/758158 : "場に出ているあいだは双方のプレイヤーに効果が及ぶため" (while in play, the effect reaches BOTH players — CONFIRMS Stadium effects in Pocket are symmetric). But same-name replacement, per-turn limits, and where a replaced Stadium goes were NOT found in a Pocket-specific JP source this session. Flagged unresolved.

### Q40 — Fossils
Grade: MIXED — CAUTION: primary fossil-rule source found (pokesiyu.com/nazonokaseki-rule) uses physical-TCG-only terminology (サイド/prize cards, 山札-search card names like Nest Ball) and is almost certainly describing the PHYSICAL TCG's Mystery Fossil, NOT Pocket — downgraded to context-only, not usable as a Pocket citation.
Pocket-specific finding, Grade: COMMUNITY (game8.jp/pokemon-tcg-pocket/647110 user comment): "化石のカードはたねポケモンとして扱われる。ベンチに置いた場合「チラチーノ」のわざ「ともだちのわ」等でベンチにいるポケモンの数としてカウントされる。" — CONFIRMS Fossils count as Basic (たね) Pokémon and count toward Bench-Pokémon-count effects (e.g. Cinccino's "Circle of Friends"), but do NOT satisfy type-specific requirements (e.g. an Electric-type-only ability like Pikachu ex's). No Pocket-specific JP source found this session on: opening-hand guarantee interaction, Poké Ball/search-card eligibility, retreat-inability, discard timing, setup placement, or KO point value. Flagged unresolved for those specifics — the physical-game source suggests (but does NOT confirm for Pocket) "can't retreat," "discard any time on your turn," and "KO gives 1 point," consistent with general community understanding, but treat these three as MEMORY-UNVERIFIED/COMMUNITY-inference only until a Pocket-specific source is found.

### Q41 — Search/draw reveal
Not resolved with a direct Pocket-specific JP source this session (GameWith's Monster Ball page 403'd on fetch). Flagged unresolved.

### Q42 — Supporter targeting specifics
Grade: COMMUNITY (Lemon8 blog on Sabrina/サブリナ)
JP: "サブリナの効果は"相手のバトルポケモンをベンチと入れ替える"タイプ" — Sabrina's effect is a forced Active↔Bench swap of the OPPONENT's Pokémon.
On the "face-down" (未確認/裏向き) info question: "情報が公開されていない（裏向き・未確認）要素は基本的にそのまま扱われ、サブリナ自体は"入れ替えを強制する"だけで、裏向きの情報を無理に見せたり確定させたりするカードではない" — CONFIRMS Sabrina does NOT reveal any hidden information; it purely forces a swap, and the player using it does not get to see which Bench Pokémon they're swapping in (they choose blind, or per some implementations the opponent chooses which one comes up — the blog's exact wording implies the OPPONENT's choice is preserved/hidden, meaning the effect forces a swap without the Sabrina-user dictating WHICH bench Pokémon replaces the Active). This partially confirms Q42's "Sabrina — opponent chooses new Active?" hypothesis, though the blog's phrasing is about information-hiding rather than an explicit statement of who clicks/chooses in the UI — worth a follow-up verification post. No JP source found this session on Cyrus/Guzma/Iono/Mars/Red-Card-equivalent Pocket cards' exact targeting rules.

### Q43 — Public information
Not directly resolved with a dedicated JP source this session, though it is implicit throughout every rules summary that opponent's discard pile, remaining deck count, and current point total are shown in the UI (all rules articles reference "相手の場," "ポイント," etc. as visible game state). No explicit JP statement found on whether the opponent's Energy Zone (current + next) is visible, or whether opponent's hand SIZE (not contents) is shown. Flagged unresolved.

### Q44 — Coin flips
Grade: OBSERVED (ITmedia verification article, methodologically explicit)
Source: https://www.itmedia.co.jp/news/articles/2411/13/news156.html — a journalist ran Misty's (カスミ) coin-flip attack 100 times to test whether Pocket's coin flips are truly 50/50, motivated by community rumors of a "guaranteed heads" exploit. The article explicitly caveats: "厳密な統計処理は行っていないため、この先については参考程度に読んでほしい" (no rigorous statistical treatment was performed; treat the following as reference only) — the full numeric result was on a page the fetch tool could not retrieve (multi-page article, page 2/3 content not returned), so the exact heads/tails count is NOT captured in this research; however, the widespread community conclusion (corroborated by many "ガセ/デマ" debunking articles found in search, e.g. wixoss.blog.jp on the "coin flip always shows heads" bug being confirmed FALSE/a rumor) is that flips are genuinely random and the "always-heads" trick does not work. Grade this specific 50/50-independence claim as COMMUNITY rather than OBSERVED given the missing numeric payoff. No JP source found this session directly testing "flip until tails" unbounded-flip mechanics.

### Q45 — Copy-attack effects (Mew ex Genome Hack / ゲノムハック)
Grade: COMMUNITY (hakase-seikatsu.blog, detailed and specific)
JP: "相手のバトルポケモンのワザをコピーできる「ゲノムハック」というワザ" — copies the opponent's ACTIVE Pokémon's attack.
JP: "本来必要なエネルギーの種類や数に関係なく、どんなワザでも無色エネルギー3個で使える" — CONFIRMS the copied attack's own Energy cost/type requirements are IGNORED; Mew ex uses its own fixed cost (3 Colorless) regardless of what the original attack required.
Additional confirmed edge cases:
- If the copied attack has a cost like "discard N [Type] Energy," it checks MEW EX's own attached Energy (not the original attacker's) for whether/how much it can discard.
- If the copied attack references "the Bench" (count/target), it uses MEW EX's OWN Bench, not the original attacker's opponent's bench context.
- Recoil-damage attacks still deal recoil TO MEW EX itself when copied.
- Mew ex CANNOT copy another Pokémon's copy-attack (no double-copying): "相手ポケモンのコピーワザをコピーすることもできません"
This is a detailed, internally consistent community analysis; treated as COMMUNITY (not OBSERVED) since no explicit coin-flip/screenshot verification was cited, but the specificity and consistency across the source suggest high reliability.

### Q46 — Energy Zone effect-attachment vs. manual attachment
Not resolved with a direct JP source this session confirming whether card-effect attachments FROM the Energy Zone consume/block the once-per-turn manual attachment. (The English-track finding on Jolteon ex's "Electromagnetic Wall" — noted in A_official.md — is suggestive that the engine treats "any attachment sourced from the Energy Zone" as one bucket, but that doesn't resolve whether it shares a single per-turn allowance with manual attachment.) Flagged unresolved.

### Q47 — "During opponent's next turn" effects when source leaves play
Not resolved this session. No JP source found testing this specifically.

### Q48 — Effects needing a nonexistent target
Not resolved this session with a direct source, though the Q37 finding (UI blocks Supporters with unmet target conditions, e.g. a bench-switch Supporter when the opponent has no Bench Pokémon) strongly suggests the same UI-blocking behavior would apply to switch-type Trainer effects generally — i.e., the card likely cannot be played at all if its target doesn't exist, rather than being playable with no effect. Inference only, not a direct confirmation for attack effects specifically (e.g., an attack that includes a forced-switch clause when the target's bench is empty).

### Q49 — Ranked vs. casual vs. event vs. solo/AI differences
Grade: COMMUNITY (GameWith/Game8, partial)
Confirmed: Solo (AI) battles use a 50-turn forced-draw cap vs. 30 turns in versus (PvP) matches — see Q10. Ranked-specific: in Beginner Rank, losses do not reduce Rank Points ("「ビギナーランク」では負けてもポイントの減少がない"); matchmaking is rank-based. No JP source found this session on Ranked vs. casual differences in TIMERS, or on event-battle-specific rule differences. Flagged unresolved for those specifics.

### Q50 — Official rule changes / card behaviour fixes since launch
See dedicated section below.


---

## Official JP notices on card behaviour/bugs, with dates

1. **2025-07-30 — Ranked match point adjustment.** Game8's update log (game8.jp/pokemon-tcg-pocket/650515) lists a July 30, 2025 change reducing Rank Points lost on defeat ("敗北時のポイント減少" adjustment). This is a SYSTEM/rule change to the ranked ladder's point economy, not a specific card fix. Grade: OFFICIAL-QUOTED (secondary summary of official patch notes; original patch-note page not independently fetched this session).

2. **2025-07-30 and 2025-08-08 — Ho-Oh ex (★3) / Lugia ex (★3) illustration notices.** Official account @PokemonTCGP_JP posted an apology ("お詫びとお知らせ") on 2025-07-30 and a follow-up ("イラストのアップデートについて") on 2025-08-08 about these Immersive-rarity cards being shipped with placeholder/blank artwork after the wrong production reference was given to an illustrator. IMPORTANT: this is an ART/production bug, NOT a gameplay or card-effect bug — flagged here for completeness per the task's instruction to log official bug notices, but it has no rules relevance. Grade: OFFICIAL (news coverage of the official tweets — direct tweet fetch was blocked by robots.txt; date derived from the tweet's Snowflake ID, not directly read from the tweet text).

3. **~2025-10-03 — Pack-opening-points expiration description error.** Official account tweet: "「ハイクラスパックex」を含む全ての拡張パックのパック開封ポイントについては、拡張パックの提供期間が終了した場合でもポイントは消失せず、カードとの交換も可能です。アプリ内の「ゲームのヒント」の説明に誤りがございましたため、今後修正を予定しております。" EN: "For all expansion packs including High-Class Pack ex, pack-opening points do NOT expire when a pack's availability period ends, and can still be exchanged for cards. There was an error in the in-app 'Game Tips' description [saying otherwise], which will be corrected." This is an official correction of an in-app RULES-TEXT error (not gameplay logic), confirming actual behavior overrides the (wrong) in-app text. Grade: OFFICIAL-QUOTED (tweet text captured via search snippet; date derived from Snowflake ID, day precision only — not independently re-verified by opening the tweet).

4. **Undated (pre-existing, ongoing) — Sakaki (Giovanni)'s "+10" damage bonus scope.** Not a single dated announcement, but a widely-cited community deep-dive (did2memo.net, dated 2024-12-23) explaining/confirming the card's actual (and apparently non-obvious to many players) behavior: the +10 bonus applies to attack (ワザ) damage against the opponent's ACTIVE Pokémon only — never to Ability (特性) damage, never to the Bench-damage portion of a multi-target attack, and never when the base attack damage is 0. This reads as accurate-to-design behavior rather than a "bug that got fixed," but is included here because it is exactly the kind of non-obvious card-behavior clarification the task asked to capture. Grade: OBSERVED/COMMUNITY.

No other official (@PokemonTCGP_JP or pokemontcgpocket.com/ja/news) notices specifically about a CARD EFFECT bug or rules-engine bug (e.g. "an Ability was not triggering as intended and has been fixed") were found this session — this is very likely an incompleteness of search coverage (WebSearch budget was exhausted mid-session; the official news list page also repeatedly failed to load via WebFetch due to redirect loops) rather than confirmation that no such notices exist. This is the single most important gap to close in follow-up research for Q50.

## Other edge cases found (not in the original question list)

- **Rare Candy's printed restriction clause** ("cannot be used on your own first turn, or on a Pokémon just put into play") is stated explicitly ON THE CARD ITSELF in Pocket, rather than being left to a general rule players must infer — useful confirmation that Pocket tends to restate global restrictions on individual card text where they're relevant.
- **Giovanni/Sakaki's damage bonus is attack-only and Active-target-only**, and explicitly does NOT apply to: Ability damage, the Bench-hit portion of a multi-target attack, or an attack that deals 0 damage. This is a template for how ALL "opponent's Active Pokémon +X damage"-style Supporter/Tool effects likely behave, and should be checked against the simulator's handling of any similar effect.
- **Mew ex's Genome Hack (ゲノムハック)** copies an opponent's attack for a fixed 3 Colorless Energy regardless of the original cost, but costs/counts referenced BY the copied attack's text (Energy to discard, Bench-count, recoil target) all resolve against MEW EX's own board state, not the original attacker's. It also cannot copy another Pokémon's own copy-attack (no chaining).
- **Fossils count as Basic Pokémon for Bench-count-based effects** (e.g. Cinccino's Circle of Friends) but do NOT satisfy type-specific requirements (e.g. an Electric-only Ability), since Fossils have no type.
- **Supporter cards can be genuinely unplayable/greyed out** due to unmet target conditions (no valid target, e.g. a healing Supporter when nothing is damaged, or a bench-effect Supporter when the opponent's Bench is empty) — the UI does not allow playing a Supporter that would simply do nothing.
- **Sabrina (サブリナ)'s forced switch does not reveal hidden/face-down information** — it is purely a forced Active↔Bench swap and does not let the user see or select which of the opponent's face-down/unconfirmed Bench Pokémon comes up.
- **Weakness invalidation list is broader than just "Bench damage"**: per GameWith's weakness page, Weakness also does not apply when (a) the attack deals 0 damage, (b) the attack "fails" outright, (c) all coin flips for a variable-damage attack come up tails, or (d) the damage source is a status condition (poison, etc.) rather than an attack. This is a fuller list than the raw question anticipated and should be checked item-by-item against the simulator.
- **Deck-out is unconditionally safe in Pocket** — there is no equivalent of physical TCG's Loss-by-empty-deck at all, at any point, confirmed by an explicit Game8 statement rather than just "no draw."

