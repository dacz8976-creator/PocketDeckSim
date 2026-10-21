# Full battle review: 20260930_161633000_iOS.MP4

**Current status: completed full-battle review accepted by the lead; original archived unchanged in `Reviewed`. Excluded from Ladder Log.**

Reviewer: sol_auto_161633000, fresh Sol review, 2026-09-30. Scope: the single battle from setup through turns 1-9 and the terminal defeat screen. This is a source-grounded visual review, not an exact engine replay. Root retains acceptance, logging, indexing, and source-moving responsibility.

Source binding: SOURCE.json registers 169.925 seconds, 306539344 bytes, SHA-256 `0795e24efb0f71c3461d23b5860a736a30755cf2071a3047eb4b90a731193a79`. Frames were extracted from that exact named source. This reviewer relied on the registered integrity event rather than performing a separate hash pass.

Outcome: owner Dacz8976 loses, 0-3. The computer's third one-point knockout is followed by an explicit **Defeat...** screen at 169.00-169.50s. The named opponent deck is **Mega Manectric ex & Bellibolt ex Deck (Deluxe Pack: Mega)**. Mega Manectric ex does not enter the visible field; its presence in the opponent deck's label does not establish its location or printing during play.

Mode: owner testimony establishes autopilot against the computer. The green checked Auto control is visible from 10.50s through the game, with no observed disabling action. The terminal opponent deck label independently supports a computer deck encounter. **Ladder eligible: false. No Ladder Log write.**

## Evidence method

All seven overview sheets were inspected, covering 57 samples at 3-second intervals from 1.50 through 169.50s. Targeted native-resolution source frames supplement card reveals, draws, searches, evolution, HP/tool changes, coins, damage, promotions, and terminal evidence. Labels on overview sheets are fps sampling midpoints; action windows below are approximate bounds, not frame-accurate onset claims. Target filenames specify exact requested seeks. Meaningful stable states, rather than animation counters, control HP and score reconciliation.

## Visible card versions and information boundaries

Owner: Riolu, 60 HP, Fighting Fist 10+, costing one Fighting Energy; visible text adds 30 damage when the opponent's Active is a Pokemon ex. Drilbur A, 60 HP, **Scratch 10**, one Colorless attack cost; Drilbur B, 60 HP, **Headbutt Bounce 30**, two Colorless attack cost. Both have Grass +20 weakness and one Colorless retreat cost. These are different versions and are tracked separately. Opening hand also shows two Garchomp ex with Linear Attack / Dragon Claw and Gabite, 80 HP, Sharp Scythe 30. Later Mega Lucario ex, 190 HP, Fighting Pulse 90+, is drawn. None of those evolution cards is played. No Gible is revealed. The full owner deck and unrevealed draw order remain unknown.

Opponent: Tadbulb, 50 HP, Charge; Helioptile, 60 HP, Jumping Kick; Heliolisk, 80 HP, Electrospark 40; Pikachu, 60 HP, Growl; Raichu, 100 HP, Evoshock / Electro Ball 50; Bellibolt ex, 160 printed HP, High-Voltage Cannon 70+, two Lightning attack cost. Bellibolt's visible text grants an additional 70 damage with four or more Lightning Energy **in play**. The observed attacks remain 70. The cape-art Tool visibly grants Stage 1 Pokemon +30 HP; its exact title is not read confidently and is retained as unknown. It increases Bellibolt's remaining HP from 130 to 160 while preserving existing damage, implying a 190 maximum under its shown effect.

Owner Poke Ball is played. Lucky Ice Pop is drawn and remains in hand; its healing and return-to-hand coin interaction are not executed. Arena of Antiquity is drawn and remains in hand; its printed Fighting-Pokemon damage bonus is not executed. Opponent Poke Ball, Professor's Research, the +30 HP Tool, and Electric Generator are visibly used. No Stadium enters the field. Opponent face-down cards remain unknown. No status condition is successfully applied, and no voluntary retreat or switch occurs; the two owner Active replacements are forced post-KO promotions.

## Full timeline and stable states

| Window | Phase | Source-grounded actions and resulting state |
|---|---|---|
| 0-18s | Setup | Empty board, initial coin animation, cards dealt, and Active Pokemon revealed. Opponent Tadbulb 50; owner Riolu 60. Both Benches empty and score 0-0. At 13.50-16.50s Riolu's Fighting advantage over Tadbulb is displayed. Owner opening hand shows two Garchomp ex, Poke Ball, Gabite. The setup coin's final face is not confidently established, but subsequent turn order establishes the computer goes first. Auto checked by 10.50s. |
| 18-25.50s | Opponent turn 1 | Opponent uses Poke Ball and establishes Helioptile 60 on left Bench. Tadbulb remains Active 50 with no attached Energy visible. No damaging attack or HP change occurs. Owner turn 2 banner at 25.50s anchors the handoff. |
| 25.50-43.50s | Owner turn 2 | At 27.00s the ordinary turn draw reveals **Headbutt Bounce Drilbur B**. Owner plays Poke Ball, which retrieves the different **Scratch Drilbur A** (33.00s reveal; 36.00s search animation). Drilbur A is placed on right Bench at 60 HP by 39.00s. One Fighting Energy is attached to Riolu. Riolu uses Fighting Fist (40.50s banner); Tadbulb goes 50 to 20 by 43.50s. Reconciliation: 10 base +20 weakness =30; no ex bonus against ordinary Tadbulb. Riolu stays 60 with one Fighting; Drilbur A stays 60 with none; Drilbur B remains in hand. Score 0-0. |
| 43.50-69s | Opponent turn 3 | Helioptile evolves to Heliolisk 80 (46.50-48.00s). Professor's Research is used (51.00s discard evidence), with hand replenishment visible by 55.50s. Pikachu 60 joins center Bench by 56.00s. Active Tadbulb evolves to Bellibolt ex (58.50-59.00s), carrying 30 damage: 160 printed HP less 30 =130 remaining. One Lightning Energy is attached by 64.00s. Cape-art Tool attaches at 65.00-66.00s; on-screen effect says Stage 1 Pokemon get +30 HP. Settled remaining HP becomes160 at67.50-69.00s. No attack damage occurs in this turn; Bellibolt has only one Lightning visible. Owner Riolu60/one Fighting and Bench Drilbur A60 remain unchanged. Score0-0. |
| 69-80s | Owner turn 4 | Lucky Ice Pop is the new turn draw (70.50s popup and 72.00s hand). It is retained, with no heal or coin. Second generated Fighting Energy is attached to **benched Drilbur A**, giving it one; Riolu retains one (74.00s). Riolu's Fighting Fist deals **60** with the Weakness label at76.50-77.00s: 10 base +30 against ex +20 weakness. Bellibolt160 to100 by79.50-80.00s; Tool remains attached. Both owner Pokemon stay60. Score0-0. |
| 80-109.50s | Opponent turn 5 and first KO | Pikachu evolves to Raichu100 and triggers Evoshock (82.50-83.00s). Its displayed coin condition would paralyze on heads; targeted87.00s shows the emerging Tails result, and no paralysis appears on Riolu at88.00s. Opponent uses **Electric Generator**, whose displayed coin condition would attach Lightning to a benched Lightning Pokemon on heads; 93.00s explicitly shows **Tails**, so no attachment from that effect. Ordinary Energy attachment supplies Bellibolt's second Lightning by95.00s. High-Voltage Cannon is named at96.00s, deals70 at97.50s, and KOs Riolu60. Riolu is removed by100.50s; opponent receives point1 at103.50s. Scratch Drilbur A is promoted (106.50s), retaining its one Fighting Energy. Bench now empty. Bellibolt100, two Lightning, +30HP Tool; Heliolisk80 and Raichu100 on Bench with no Energy visible yet. Score owner0, opponent1. |
| 109.50-124.50s | Owner turn 6 | Owner turn6 shown at109.50-110.00s. Mega Lucario ex is drawn and held (113.00s). Headbutt Bounce Drilbur B is finally **played** from hand to right Bench (116.00-117.00s),60HP. The new Fighting Energy is attached to Drilbur B, giving it one by119.00s; Active Scratch Drilbur A retains one. Active Scratch attacks for30 including weakness, supported by100 to70 BelliboltHP transition at121.50-125.00s. This is Scratch10 +20 weakness, not Headbutt Bounce and not a Bench ability. Both Drilbur remain60. Lucky Ice Pop and evolution cards remain held. Score0-1. |
| 124.50-141s | Opponent turn 7 and second KO | Opponent turn begins with Bellibolt70/two Lightning. New ordinary Lightning Energy goes to benched Raichu by126.00s; Bellibolt still has two. High-Voltage Cannon banner at127.50s precedes KO of Active Scratch Drilbur A60. Settled0HP shown130.50s; opponent point2 at133.50s. Headbutt Bounce Drilbur B is promoted from right Bench by139.50-141.00s with its one Fighting Energy. Bench empties again. Bellibolt70 and Tool persist; Heliolisk80, Raichu100/oneLightning. Score0-2. |
| 141-151.50s | Owner turn 8 | Arena of Antiquity is drawn (144.00s). It remains in the owner's hand through terminal; no Stadium is played. Second Fighting Energy attaches to Active Drilbur B by147.00s, satisfying its two-Colorless attack cost. Headbutt Bounce is named at148.50s and deals50 total including20weakness, leaving Bellibolt70 to20 by151.50s. Owner Drilbur B60/twoFighting, empty Bench. Score0-2. |
| 151.50-163.50s | Opponent turn 9 and third KO | Bellibolt20/twoLightning, Tool; Raichu100/oneLightning and Heliolisk80. No new attached Energy is established in the sampled stable board before the attack. Bellibolt's High-Voltage Cannon banner155.00s and visible70damage at157.00s KO Drilbur B. The momentary50HP animation counter is not a settled survival state;157.50s shows0HP. Opponent gains third point at160.50s. Owner earned no points, and there are no owner Pokemon left. |
| 163.50-169.925s | Terminal | Board fades163.50s, loading166.50s, explicit Defeat at169.00-169.50s with computer deck name. Riolu is displayed as Card of the Game in169.50s overview. No second battle begins in the supplied source. |

## Mechanic reconciliation and decisions

The complete damage ledger is consistent: Tadbulb takes30; the damage persists into Bellibolt ex (130 remaining), the Tool adds30 remainingHP (160), then Riolu60, ScratchDrilbur30, and HeadbuttDrilbur50 leave Bellibolt100,70,20. Bellibolt makes three70-damage attacks against60HP basics for exactly three one-point KOs. No ex or Mega owner Pokemon enters play, so no two- or three-point KO award is claimed. Owner Energy development is one on Riolu, then one on ScratchDrilbur, then one and later a second on HeadbuttDrilbur. Each KO discards the previous Active; none of its Energy transfers to its successor.

The visible loss is associated with a hand full of evolution cards that never develop onto the board, while60HP basics face repeat70damage. Mega Lucario ex arrives only after its Riolu predecessor is KO'd. This identifies a revealed development problem in this particular game; it does not establish the full deck composition or bot policy reason.

At turn8, held Arena of Antiquity visibly says attacks by Fighting Pokemon do20more to opposing Active Pokemon ex. Drilbur B is Fighting, Bellibolt ex has70 remaining before the attack, and the actual attack deals50. **Conditional alternative:** if Arena could be played before this attack and its printed effect applied, Headbutt Bounce would reach70 and KO the70-HP Bellibolt ex for two points. The interaction was not exercised, and this is a source-text prediction, not a verified engine result or a claim of eventual victory. It would improve the immediate exchange under those visible conditions, but hidden information and subsequent turns prevent projecting the battle outcome. No engine defect is proved by this recording.

## Limits

See UNCERTAINTIES.json. Exact Tool title, initial coin face, unrevealed deck/hand contents, and untested Arena/Lucky Ice Pop interactions remain unknown. Transient notifications obscure parts of the upper UI in turns6/9, but adjacent stable board, attack, KO, and score anchors resolve the meaningful transitions. Source audio was not transcribed. Every visible battle phase is covered; the review does not claim every animation frame was inspected.


## Astra consultation and lead clarification

Astra independently checked the Stadium eligibility and conditional immediate knockout against retained source frames. Arena applies to Fighting Pokemon, represented by the fist symbol. Drilbur satisfies that condition; the conditional 70-damage prediction remains valid as a printed-text inference. The alternative was not executed and does not establish an eventual win or engine behavior. See `ASTRA_CHECK.md` and `LEAD_CORRECTION.md`.


## Lead completion

Accepted as a completed full-battle review after the source checks documented in `LEAD_ACCEPTANCE.json`. The unchanged original is archived in `Reviewed`; matching before/after SHA-256 is recorded in `MOVE_RECEIPT.20260930_161633000_iOS.MP4.json`. No Ladder Log entry was created.


## Post-acceptance wording and status check

The accepted review has received a targeted wording/status follow-up. See [the correction record](POST_ACCEPTANCE_CORRECTIONS.md) for exact changes, preserved history and result-display limits. Outcome, score, source identity and Ladder exclusion are unchanged.
