# Pokémon TCG Pocket (ポケポケ) Rules Research — web_grey report
Date of research: 2026-09-22. All sources are about the mobile game "Pokémon TCG Pocket" / "ポケポケ" unless explicitly noted as physical-TCG (and flagged as such / excluded from answers).

---

## Q1. Simultaneous finishes

### (a) Last Pokémon takes the 3rd point via attack but is KO'd in the same exchange (recoil/Rocky Helmet)
**Answer: WIN for the player who reached 3 points, unless the opponent *also* reaches 3 points in the same exchange.** Reaching point-count is evaluated independently of what happens to your own Pokémon.

> "相打ちで片方が3ポイントに到達し、もう一方が到達していない場合、3ポイントのプレイヤーが勝利" — torecataru.com, "ポケポケの対戦で相打ちによる引き分け条件完全解説" (https://www.torecataru.com/?p=447), n.d. (accessed 2026-09-22)
[COMMUNITY]

> "If you knock out opponent's Pokemon and reach 3 points, you win—even if your attacking Pokemon takes recoil damage." — summarized from Game8 JP win/tie conditions page (https://game8.jp/pokemon-tcg-pocket/650664)
[COMMUNITY]

### (b) Both players reach 3 points at the same time, with Pokémon left on both sides
**Answer: TIE**, confirmed by multiple independent Japanese guide sites and an English community writeup (Dexerto), with Reddit-cited real-game evidence.

> "両者が同時に3ポイントに到達" results in a draw ("引き分け"), UNLESS one player has no Pokémon remaining, in which case that player loses instead. — poke-memo.com, "ポケポケの引き分け完全ガイド" (https://www.poke-memo.com/pokepoke-hikiwake/), n.d.
[COMMUNITY]

> "If a Pokemon Pocket match ends with both Pokemon being knocked out and they still have Pokemon on the Bench (or none), then it's declared a tie... if one player has at least a single Pokemon [on] the Bench and the other doesn't, then they're declared the winner, regardless of who inflicted the final blow." — Dexerto, "Pokemon TCG Pocket players discover unfair rules for tying games" (https://www.dexerto.com/pokemon/pokemon-tcg-pocket-players-discover-unfair-rules-for-tying-games-3015305/), n.d.
[COMMUNITY, cites Reddit user "I won a game where my opponent also scored 3 points" as real-game evidence → borderline COMMUNITY-TESTED]

**Important nuance (both sub-questions a & b combine into one real rule):** the tie-breaker is NOT "both hit 3 points" alone — it's "can you promote a benched Pokémon?" If both players can still promote a Pokémon after the mutual KO, it's a tie; if only one can, that player wins even if both hit 3 points. This is stated directly by Pokémon Zone (fan site, not official Pokémon Company, but a widely-used Pocket reference):

> "If both players have a Pokémon on their bench that they can promote, the game ends in a tie. If one player has no benched Pokémon left to promote, their opponent fulfills two win conditions to their one, and thus, their opponent wins the game." — Pokémon Zone, "How to play Pokémon TCG Pocket?" (https://www.pokemon-zone.com/articles/how-to-play-pokemon-tcg-pocket/), n.d.
[COMMUNITY]

### (c) KOs during Pokémon Checkup that finish the game for both players
Same mechanic as (b): during Checkup, if both actives are KO'd simultaneously (e.g., mutual poison/burn), the "can you promote?" rule decides. A dedicated Pocket-specific guide states the promotion-choice order explicitly (see Q11 below), which is the same event.

**No official Pokémon Company / DeNA statement was found for any part of Q1** — everything above is [COMMUNITY], with the Dexerto piece citing an actual Reddit game result as evidence, which is closer to [COMMUNITY-TESTED]. No source directly contradicted this "promote-ability decides ties" rule, so confidence is reasonably high despite no OFFICIAL grade being available.

---

## Q2. Checkup order: Special Condition damage vs. "during Checkup" Abilities (Garganacl/Flygon ex/Glaceon ex)

**Unresolved for Pocket specifically.** I could not find a Pocket-specific source naming Garganacl (ガルガンチル), Flygon ex (フライゴンex), or Glaceon ex (グレイシアex) together with an explicit Checkup-order ruling. Physical-TCG sources exist but per your instructions do not apply unless a Pocket source confirms them — none did, so I report them only as background, clearly flagged as NOT Pocket-confirmed:

> [Physical TCG, NOT Pocket-confirmed] "①特殊状態の確認 → ②特性・トレーナーズ効果 → ③きぜつ確認" (order: 1. Special Condition confirmation, 2. Abilities/Trainer effects, 3. Faint confirmation); "このうち、重複する可能性がないのは、「ねむり」と「マヒ」だ" (Sleep and Paralysis can't co-occur); when multiple own-side effects trigger simultaneously, "効果を受けることとなる者が任意で決めることができる" (the affected player chooses the order); "ポケモンチェックはお互いが同時に行うこととなる" (Checkup happens for both players simultaneously). — wirolabo2.net, "ポケカ「ポケモンチェック」についてわかりやすく解説" (https://wirolabo2.net/pokemon-card-game-pokemon-check/), n.d. — **explicitly confirmed by WebFetch analysis to be about the physical card game, not Pocket.**
[COMMUNITY — physical TCG only, unconfirmed for Pocket]

I tried gamewith.jp's dedicated Pocket "ポケモンチェックのルールまとめ" page (https://gamewith.jp/pokemon-tcg-pocket/488816) but it returned a 403 error and could not be read. Repeated Japanese-language searches combining specific card names (ガルガンチル/しおづけ, フライゴンex/すなのけらい, グレイシアex/ゆきどけのだいち) with "順番"/"どちらが先" turned up no dedicated discussion thread or ruling. **Verdict: unresolved** — no Pocket-specific source found despite trying multiple phrasings and all three example cards individually.

---

## Q3. Turn limit

**Answer: 30 turns for PvP, with at least one conflicting community claim that it's universally 30 (including Solo).**

> "The Battle Rules confirms it: Games in Pokemon TCG Pocket can last a maximum of 30 turns. If you reach the limit, the duel ends in a tie." — TrustYourPilot (X/Twitter), quoting the in-game Battle Rules text (https://x.com/TrustYourPilot1/status/1849485951099408686), Oct 2024
[COMMUNITY-TESTED — quotes the game's own in-app rules text, closest thing to OFFICIAL found]

> "だれかと" (vs. real player) mode: 30 turns total = forced draw. "ひとりで" (Solo) mode: 50 turns = draw. Turns are counted per player (each player's turn counts separately) — i.e., "30 turns" means 30 total turns split across both players, not 30 turns each. — Game8 JP, "勝利条件まとめ・引き分けの条件" (https://game8.jp/pokemon-tcg-pocket/650664), n.d.
[COMMUNITY]

**However**, a Yahoo Chiebukuro answer directly disputes the 30-vs-50 split:
> Q: "ポケポケのフレバトで最大ターンを調べたら30-50ターンと出てきたのですが" (I looked up the max turns for free-battle and got 30-50 turns) A: "ポケポケのターン上限は30ターンですよ。その情報元が間違ってます。" (The turn limit is 30. That source is wrong.) — Yahoo!知恵袋 (https://detail.chiebukuro.yahoo.co.jp/qa/question_detail/q14308499649), n.d.
[SINGLE — one anonymous answer, contradicts Game8]

**Conflicting evidence reported as-is.** Neither source addresses precisely how the limit "ends" (immediately vs. after that turn's Checkup) or whether a Checkup KO after turn 30 can still resolve into a win — **unresolved**. Ranked vs. casual difference: no source found distinguishing Ranked specifically; the only mode split found is PvP (だれかと) vs. Solo (ひとりで), not Ranked vs. casual PvP — **unresolved** whether Ranked itself differs from unranked PvP.

---

## Q4. Hand full (10 cards)

**Answer: Confirmed for the draw/Professor's Research case; the "returned card disappears" case is unresolved.**

> "ポケポケでは手札を最大10枚まで所持することができます" (max hand is 10 cards); "手札に既に10枚カードがある場合、11枚目以降はデッキから引くことができなくなります" (at 10 cards, you simply can't draw beyond); "手札が10枚ある場合、デッキから一番上のカードをトラッシュすることはありません。単純にカードを引けなくなるだけ" (the top deck card is NOT trashed — the draw is simply skipped); "「博士の研究」などを使っても11枚以上持つことはできない" (even Professor's Research can't push you over 10). — Game8 JP, "手札上限はある？" (https://game8.jp/pokemon-tcg-pocket/650710), n.d.
[COMMUNITY]

This directly implies **Professor's Research CAN be played at 10 cards in hand** (it discards itself and gives you +2 draws, but any draws beyond 10 are simply not received — the card is not "unplayable" due to hand size). No source explicitly says "yes you can play it at 10," but the mechanic described (draws are just capped/skipped, not blocked or discarded from the top) supports this reading. [COMMUNITY, inferred]

**Unresolved:** what happens when an effect (Ilima/Koga returning an evolved Pokémon to hand, Lucky Ice Pop-style effects) would *return a card to hand* while hand is already at 10. No source addressed this specific scenario (return-to-hand, not draw). Searches in Japanese for Ilima (イリマ)/Koga (コルニ) + "手札10枚" + "消える/戻せない" returned no discussion of this edge case.

---

## Q5. Weakness when attacker-side debuff would reduce damage to 0

**Partial answer, order of operations confirmed; the exact 0-damage edge case is unresolved.**

> "最終的な与えたダメージに20加算する" (add 20 to final damage dealt — Weakness is a flat +20, not ×2). Example given: "バリヤードで攻撃後、10(ワザのダメージ)+20(弱点)-20(ワザの効果)+毒となり、最終的には10ダメージと毒のダメージ10の合計20ダメージ受けることになります" (After attacking with [an ability like] Barrierd: 10 base + 20 weakness − 20 [debuff] = 10 final damage, plus 10 poison damage = 20 total). — GameWith, "弱点の効果とタイプ相性・計算方法" (https://gamewith.jp/pokemon-tcg-pocket/466440), n.d.
[COMMUNITY]

This example shows the calculation ORDER is: **base damage → +20 weakness → then flat debuffs subtracted**, i.e., weakness is added into the total *before* a damage-reducing debuff is applied, not skipped. In the example the result is still >0 (10 damage), so it does not directly prove what happens if the post-weakness, post-debuff result would be exactly 0 or negative. The same source separately states weakness does NOT apply when "ダメージがないワザを使った" (the attack itself deals 0 base damage) or "コイン投げがすべてウラで0ダメージだった" (all coin flips whiff for 0) — but those are cases where the attack's *own* damage is 0 before weakness, not cases where a debuff reduces an otherwise-nonzero attack to 0 after weakness is figured in.

**Verdict: unresolved for the exact edge case asked** (debuff makes the post-weakness total exactly 0), but the calculation-order evidence suggests weakness is "added" as part of the math regardless, which weakly supports "yes, weakness is still applied/counted" rather than being skipped. [COMMUNITY, inferred, not conclusive]

---

## Q6. Random selection uniformity (Poké Ball) and Energy Zone randomness / coin flips

### Poké Ball: uniform over cards vs. uniform over names
**Unresolved — no direct test or statement found**, despite multiple search attempts in English and Japanese (including Reddit-style and Qiita statistical-analysis searches). One tangentially relevant Qiita article on Pocket's probability distributions (hypergeometric/binomial/multinomial mechanics for cards like Professor's Research, Pikachu ex, Dragonite) treats deck contents as individual card objects drawn "without replacement," which is weak circumstantial support for "uniform per physical card" (so 2 copies of Riolu + 1 Hitmonlee → 2/3 Riolu) rather than per unique name, but this article never discusses Poké Ball itself. — Qiita, "ポケポケに登場する確率分布" (https://qiita.com/Isaka-code/items/bbca509d857925c3669a), n.d. [COMMUNITY, not directly on-topic — inference only]

### Energy Zone randomness with 2–3 types
**Claimed uniform/independent, but no empirical test found (only the stated design intent).**
> "複数のエネルギーを設定した場合、その供給は完全にランダムで行われ、確率は均等に割り振られます" (with multiple types set, supply is fully random and evenly distributed); 2 types → 50%/50%; 3 types → ~33% each. — kodakphotoprinter.jp, "ポケポケのエネルギーに関する仕様" (https://kodakphotoprinter.jp/472/), n.d.
[COMMUNITY — states intended design, explicitly NOT backed by empirical testing in that article]

### Coin flip fairness
**Community-tested, and result leans "fair within normal statistical variance."**
> "有志による複数の検証データによると、コインのオモテが出る確率は50%に非常に近いものの、わずかに下回る傾向が見られます。例えば、数百回規模の試行で48.4%といった結果が報告されています。" (Multiple independent community tests show heads-probability very close to 50%, slightly under; e.g. one test of several hundred trials reported ~48.4%.) Conclusion: "プログラム上の確率設定が50%から大きく逸脱しているわけではない" (the programmed odds are not significantly off from 50%); the "feels rigged" perception is attributed to negativity bias, not real skew. — poke-memo.com, "ポケポケのコインがおかしい？確率の偏りや仕様、不具合を徹底解説" (https://www.poke-memo.com/pokepoke-coin-okashii/), n.d.
[COMMUNITY-TESTED — cites actual multi-hundred-trial data, though I could not independently pull the raw source]

A separate widely-referenced English data point — a player who tracked 299 real coin flips (Gamerant, "Pokemon TCG Pocket Player Tracks Last 299 Coin Flips and Shares the Results") — exists but the article was blocked by robots.txt and could not be fetched; only the headline is confirmed to exist. [reference only, not independently verified — treat as unconfirmed pointer]

---

## Q7. Opening hand mechanism for guaranteed Basic

**Answer: Community-tested with real statistical methodology; two independent testers, results point toward "redraw/replace" logic over "fixed Basic + 4 random," but they don't fully agree with each other on which exact variant.**

**Test 1 (machapin, Qiita):** Ran 2,000 automated battles (1,000 per deck) via pyautogui + OpenCV on BlueStacks, hypothesis-tested three candidate mechanics with Z-tests:
- Logic 1: draw 1 Basic first, then 4 random from full deck
- Logic 2: draw 5, if no Basic redraw all 5 (mulligan-style)
- Logic 3: draw 5, if no Basic present, swap ONE card for a Basic

> "山札から5枚引き、その中にたねポケが含まれなかった場合、うち1枚をたねポケ1枚と入れ替える" — concluded Logic 3 is correct; p-values for Logic 3 (18.46%, 90.77%) were consistent with observed data, while Logic 1 (~10⁻²⁸%) and Logic 2 (~10⁻⁶%) were essentially rejected. — Qiita, machapin, "初期手札の「たねポケが1枚以上含まれる」ロジックを「統計的仮説検定」で徹底検証" (https://qiita.com/machapin/items/a4d3b09d1b369c123e85), n.d.
[COMMUNITY-TESTED — real automated data collection + statistical hypothesis testing]

**Test 2 (Davoi, Qiita):** 120 real matches with a deck of exactly 2 Basic Pokémon (Magikarp/コイキング):
> "コイキング（たねポケ）を2枚同時に引いた回数は10回で、確率としては10 ÷ 120で8%となった。" (Both basics drawn together 8% of the time.) Compared against theoretical: Logic 1 → 21.1%, Logic 2 → 11.8%, Logic 3 → 5.2%. The observed 8% sits between Logic 2 and 3, ruling out Logic 1 but not cleanly distinguishing 2 vs 3. — Qiita, Davoi, "初手たねポケ1枚確定ってどういうロジック？" (https://qiita.com/Davoi/items/8e6393f6833c9492da4e), n.d.
[COMMUNITY-TESTED — real data, smaller sample, inconclusive between two candidate mechanics]

**Verdict:** Both independent, real in-game statistical tests agree the mechanic is NOT "fixed Basic + 4 random" (Logic 1) — it's some form of "deal 5, then fix it up if no Basic," most likely closer to Logic 3 (single-card swap) per the larger/more rigorous study, though this isn't unanimous. No official/datamine confirmation found. [COMMUNITY-TESTED, with the two tests partially disagreeing]

---

## Q8. Retreat: energy choice, and Switch effects vs. retreat while Asleep/Paralyzed

**Energy choice: unresolved — no Pocket source specifies whether the player picks which Energy type/card to discard for retreat cost when multiple types are attached.** (One English forum thread on this exact question, community.pokemon.com/discussion/4705, turned out to be about Pokémon TCG *Live*, not Pocket, and was discarded as off-topic.)

**Retreat while Asleep/Paralyzed: confirmed blocked.**
> "バトル場のポケモンが「ねむり」「マヒ」になっていると、逃げることができません" (If the Active Pokémon is Asleep or Paralyzed, you cannot retreat). — gamewith.jp, "逃げるやり方とメリット" (https://gamewith.jp/pokemon-tcg-pocket/466442), n.d.
[COMMUNITY]

> "マヒの特殊状態のポケモンは、1ターンの間技と逃げるが使えません" (A Paralyzed Pokémon cannot attack or retreat for one turn). — altema.jp, マヒ page (https://altema.jp/pokemoncardpocket/mahi), n.d.
[COMMUNITY]

**Switch effects (Supporter cards like Natsume/Erika-type "switch the opponent's or your Active") vs. retreat while Asleep/Paralyzed: partially answered.** altema states such Supporter-driven switches (not "retreat") CAN move an Asleep/Paralyzed Pokémon out and this also cures the condition — but the article hedges that it only names one such card and doesn't fully confirm the general rule:
> "ベンチと入れ替えると回復可能です...マヒ状態ではにげられません" / "バトル場を動かせる現在実装されているカードでは[ナツメ]しかない" (Only [Natsume] can move the Active Pokémon out via effect at present). — altema.jp, マヒ page, n.d.
[COMMUNITY, limited — confirms Switch-type effects bypass the Asleep/Paralyzed retreat lock and cure the condition, but only one example card was found/cited]

---

## Q9. Stadium replacement — whose discard pile?

**Unresolved.** Despite multiple Japanese-language search passes (combining スタジアム + 上書き/トラッシュ + 誰の/公式), no Pocket-specific source explicitly stated whose discard pile a replaced Stadium card goes to. Adjacent sources found were either about the physical TCG (nanjakorya.com, explicitly confirmed off-topic on fetch) or about Pokémon TCG *Live*, not Pocket (community.pokemon.com/discussion/5832, confirmed off-topic on fetch — that thread was about Path to the Peak locking stadium replacement in TCG Live, not about discard-pile ownership, and not about Pocket at all). No answer found.

---

## Q10. "Once during your turn" Abilities — reuse after leaving and returning, or after evolving

**Unresolved for Pocket specifically; only a same-mechanic physical-TCG-adjacent data point found.**

> Q: "パオジアンEXの特性「わななくれいき」は...自分の番に１回使えると書いてありますが、毎ターン使ってもいいということですか？" A: "毎ターン使う事が出来ます。それと、パオジアンexが2体いて、1体目のパオジアンexがわななくれいきを使用した後、いれかえやにげるなどで違うもう1体がバトル場に出てきた時にはそのパオジアンexもわななくれいきを使用する事が出来ます。" (Yes, usable every turn. Also: if you have two copies and the first uses the ability then is switched out, when a *different, second copy* comes into the Active position, that second copy can also use it that same turn.) — Yahoo!知恵袋 (https://detail.chiebukuro.yahoo.co.jp/qa/question_detail/q11295494326), n.d.
[SINGLE — one Q&A answer, and it's ambiguous whether this is physical TCG or Pocket (Chien-Pao ex exists in both); it also only confirms the "different copy" case, NOT "the same physical card leaving and coming back," nor the "evolves into a new stage" case]

This only weakly supports the general TCG principle that "once per turn" is tracked per individual card-object, so a *different* copy is unrestricted — it does not confirm what happens if the *same* card leaves the field and returns, or evolves (which would also become a technically "new" card object in most Pokémon TCG rulesets, but this was not confirmed for Pocket). **No Pocket-specific ruling or community test found for either the same-card-returns or the evolves-into-new-card scenario.**

---

## Q11. Promotion order when BOTH Actives are KO'd during Pokémon Checkup

**Answer found, single guide source, fairly specific.**

> When both actives are KO'd simultaneously during Checkup, "次に番が来るプレイヤーが最初にバトル場に出すポケモンを選び、その後ターンを終えたばかりのプレイヤーがバトル場に出すポケモンを選びます" (the player whose turn is coming up NEXT chooses their replacement Active first; then the player who just finished their turn chooses). — gamepedia.jp, "ポケポケ ポケモンチェックとは？同時にきぜつした場合や引き分けになる条件も解説" (https://gamepedia.jp/pokemon-tcgp/archives/4981), n.d.
[COMMUNITY — single guide site, not independently corroborated elsewhere; no official confirmation found]

This is somewhat counter-intuitive (the player about to act picks first, not the player who just ended their turn), so I'd flag it for independent verification/testing before relying on it, but no contradicting source was found either.

---

## Q12. Rulings for cards A2b–B4a (pokemon-zone rulings articles + Japanese Q&A compilations)

**Premise confirmed, but no replacement source found — largely unresolved.**

Pokémon Zone did publish "Rulings and Card Interactions" articles for early sets:
- "Mythical Island: Rulings and Card Interactions" (A1a) — https://www.pokemon-zone.com/articles/mythical-island-rulings-interactions/
- "Space-Time Smackdown: Rulings and Card Interactions" (A2) — https://www.pokemon-zone.com/articles/space-time-smackdown-rulings-interactions/
- "Triumphant Light: Rulings and Card Interactions" (A2a) — https://www.pokemon-zone.com/articles/triumphant-light-rulings-interactions/

I searched specifically for equivalent articles on every later set (A3 Celestial Guardians, A3a Extradimensional Crisis, A4 Wisdom of Sea and Sky, A4a Secluded Springs, and the later "B"-numbered sets B1/B1a, B2, B3/B3a, B4a) and **found no "Rulings and Card Interactions" article for any set after A2a** — search results for those sets returned only card-list and first-impressions articles, never a rulings piece. This is consistent with (confirms) your premise that Pokémon Zone stopped after A1a/A2/A2a.

**I could not find a replacement compilation** — no Japanese "裁定" or "効果の処理" Q&A compilation specifically for ポケポケ (as opposed to the physical TCG, which has extensive official 裁定/Q&A resources at pokemon-card.com that do NOT apply to Pocket) turned up despite several search variations (5ch/したらば-style summary searches, "みんな間違えてる ルール," "効果 処理 わかりにくい," general Yahoo Chiebukuro sweeps). Community sites (Game8 JP, GameWith, Altema) have per-card pages and per-status/mechanic explainer pages, but I found no dedicated "flagged as confusing, here's the ruling" compilation for A2b–B4a cards specifically.

**Verdict: unresolved.** No list of specific card rulings for A2b–B4a could be assembled from available sources within budget. This is a gap — if Dustin/Astra have specific card names in mind that were flagged as confusing, a follow-up search per-card (in Japanese, targeting each card's exact ability/attack name + 裁定 or 質問) would likely be more productive than a general sweep.

---

## Summary of grades used
- Q1: [COMMUNITY] / [COMMUNITY-TESTED]-adjacent (Reddit-cited real result) — tie/win logic reasonably well established, no OFFICIAL source
- Q2: unresolved for Pocket (only physical-TCG analog found, explicitly flagged as not applicable)
- Q3: [COMMUNITY-TESTED] (in-app text quoted) but conflicting [SINGLE] source disputes the Solo/PvP split; ends-immediately-vs-after-Checkup unresolved; Ranked-vs-casual unresolved
- Q4: [COMMUNITY] for draw-cap/Professor's Research; return-to-hand-when-full unresolved
- Q5: [COMMUNITY] for calc order; exact 0-damage edge case unresolved
- Q6: Poké Ball weighting unresolved; Energy Zone uniformity [COMMUNITY] (design claim, untested); coin flips [COMMUNITY-TESTED]
- Q7: [COMMUNITY-TESTED] — two independent real statistical tests, mostly but not fully agreeing
- Q8: retreat energy choice unresolved; Asleep/Paralyzed retreat block [COMMUNITY]; Switch-effect bypass [COMMUNITY, limited]
- Q9: unresolved
- Q10: [SINGLE], ambiguous game version, doesn't fully answer the question
- Q11: [COMMUNITY], single source, not corroborated
- Q12: premise confirmed (no pokemon-zone rulings articles after A2a), but no replacement source found — unresolved
