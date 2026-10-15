# Rule test review: ordinary Poison replaces modified Poison

Reviewer: `sol_rule_192632` (Sol); review date: 2026-09-29 America/Chicago. Scope: entire supplied 5:55.828 recording, with dense review of the consequential poison sequence. This is an explicitly labeled **RULE TEST**, excluded from ladder results and strategy grading. Source identity is in [SOURCE.json](SOURCE.json); time references below are elapsed video time, with a few seconds of animation tolerance. The on-screen mode at the end is `vs. Random Battle (Advanced)`. The Auto button is off through the decisive sequence; it appears on near the end. No PvP claim follows from that button.

## Finding

The footage **supports the reported reset in this game**. Toxapex's Severe Poison first makes Gliscor take a 40 damage poison tick, from 100 to 60 HP. Poison Barb is attached to Toxapex when Gliscor attacks and knocks it out. The game then explicitly announces `Gliscor is now Poisoned` again. At the next observed poison tick, Gliscor goes from 60 to 50 HP, a 10 damage tick. The ordering and HP values support fresh ordinary Poison replacing the modified 40 damage Poison. This is a source observation, not independent verification of the simulator implementation or a general official ruling.

| Elapsed time | Source observation | Retained evidence |
|---|---|---|
| 02:26-02:30 | Poison Barb is selected and attached to the owner's Active Toxapex at 30 HP. The card says that when the attached Active Pokemon is damaged by an attack from the opponent's Pokemon, the attacking Pokemon is now Poisoned. Gliscor is opposing Active at 100 HP. | `evidence/poison_146s.jpg`, `evidence/poison_150s.jpg` |
| 02:32-02:36 | Toxapex uses Severe Poison. Its visible text calls for 40 damage rather than the usual amount. The game announces `Gliscor is now Poisoned`. | `evidence/poison_152s.jpg`, `evidence/poison_156s.jpg` |
| 02:38 | Gliscor displays the enhanced poison icon and is at 60 HP, down from 100 with no attack damage from Severe Poison. This is the 40 damage checkup. | `evidence/poison_158s.jpg`, `evidence/poison_160s.jpg` |
| 02:48-02:54 | Gliscor uses Sharp Fang against Poison Barb Toxapex, dropping it from 30 to 0 HP. After the hit, the game **again** announces `Gliscor is now Poisoned`; Gliscor remains at 60 HP at that moment. Poison Barb is the supported source of this fresh ordinary Poison because its exact trigger condition is visible and no other owner poison action occurs in this interval. | `evidence/poison_168s.jpg`, `evidence/poison_170s.jpg`, `evidence/poison_174s.jpg` |
| 03:02-03:04 | Gliscor still shows Poison and drops from 60 to 50 HP as the next turn begins. The change is 10, not 40. | `evidence/poison_182s.jpg`, `evidence/poison_184s.jpg` |

## Whole clip account

| Elapsed time | Observed phase |
|---|---|
| 00:00-00:25 | App loads into a battle. Owner is shown going first and sets Mareanie Active; opponent begins with Gligar. |
| 00:25-01:00 | The early turns bring in Gligar and Hitmontop on the opponent's side. The owner shows Lucky Ice Pop and Shroodle. Mareanie is damaged and later healed by Lucky Ice Pop. |
| 01:00-02:00 | The owner evolves Mareanie into Toxapex, adds bench Pokemon, and the opponent develops Gligar toward Gliscor. Professor's Research and other Trainers appear. |
| 02:00-02:32 | Gliscor is Active. Toxapex is damaged to 30 HP. Team Rocket's Goo-zooka imposes an extra retreat cost for the opponent's next turn. The owner attaches Poison Barb to Toxapex. |
| 02:32-03:04 | Decisive 40 damage Severe Poison, Sharp Fang knockout of Barb Toxapex, fresh Poison announcement, then 10 damage poison tick as detailed above. Opponent takes the first point. |
| 03:04-04:00 | Grafaiai replaces Toxapex. Gliscor's poisoned state continues, with later 10 HP steps visible. Owner develops another Toxapex and places another Poison Barb on a Benched Pokemon. |
| 04:00-04:35 | Gliscor leaves Active around 04:15 and the game announces recovery from Poison. Opponent's Mamoswine develops. Hitmontop becomes Active, while the owner's Grafaiai is knocked out. Opponent reaches two points. |
| 04:35-05:10 | Owner's Toxapex becomes Active and uses Severe Poison on Hitmontop. Hitmontop later uses Piercing Spin, damaging Active Toxapex and a Benched Grafaiai carrying Poison Barb. Hitmontop was **already** under enhanced Poison before this attack, so its later 40 damage knockout does not independently establish whether the Benched Tool re-applied Poison. Owner gains one point. |
| 05:10-05:56 | Mamoswine becomes Active. The owner uses Grafaiai's Poison Coating but the displayed coin is tails; Toxapex subsequently uses Severe Poison, and Mamoswine shows enhanced Poison with a 40 HP reduction (160 to 120). Mamoswine attacks and takes the third point. The result screen says `Defeat`, `vs. Random Battle (Advanced)`, 14 turns, owner two points and opponent three. |

## Limits and distinctions

- The user supplied the intended rule and reported the simulator code path separately: a fresh ordinary Poison resets a modified 40 damage Poison to the usual 10. That is user testimony about the engine, not a claim derived from this video.
- The main Gliscor sequence is strong evidence for the behavior in the displayed game because it contains the 40 tick, a second Poison announcement after the Tool trigger, and the following 10 tick. The recording does not expose an internal poison counter or code state.
- The later Hitmontop/Benched Poison Barb contact is **not** an independent reset test. The Barb's printed trigger refers to the attached **Active** Pokemon, while the damaged Grafaiai is Benched; no fresh status popup is established in that interval. Hitmontop was already severely poisoned and its 40 HP loss therefore cannot resolve a replacement question.
- Opponent hand, full deck lists, and any hidden choices remain unknown. The terminal `Damage done 0` statistic is preserved as displayed; it does not negate the observed poison damage. The clip is excluded from ladder totals.

