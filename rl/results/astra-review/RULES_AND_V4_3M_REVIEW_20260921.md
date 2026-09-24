# Rules findings and Run 4 at 3M
September 21, 2026. Targeted review of the two reported engine discrepancies, their applicability to Run 4, evidence labels in the new rules reference, and the latest saved checkpoint. This is not a complete re-audit of every rule or card. No source, rules document, installed package, or running job was changed.

**Recommendation: continue Run 4 with its frozen engine and original stopping/pass rules. Keep the engine-rules corrections on a separate list.** The confirmed damage-order defect reproduces in the exact add-on, but its trigger is absent from this frozen deck pool. The simultaneous-win issue is reachable in principle and remains a game-fidelity caveat whose frequency and official rule have not been established.

## 1. Confirmed engine damage-order defect
The official damage FAQ puts Weakness before effects on the defender. Its own example is 50 damage doubled by Bounded Field, followed by a 20-point reduction, giving 80.
Source: https://app-ptcgpt.pokemon-support.com/hc/en-us/articles/57286049312665-How-do-I-calculate-damage-for-Pok%C3%A9mon-that-have-Weakness-or-effects-applied

In deckgym-fork-s193/src/hooks/core.rs:1705-1718, reductions are subtracted and clamped before Weakness. This is an engine defect, rather than an add-on legal-action-list mismatch.

I reproduced it using the exact 0.6.0 binary identified by the running job:
- Varoom A2b 055 uses its 10-damage Metal attack on Metal-weak Frigibax P-B 037.
- Without Stiffen: expected 30, actual 30.
- After Frigibax uses Stiffen (-20 damage received): expected 10, actual 20.
- The engine's counterfactual damage hook also reports 20 in the shielded case.
- Both cases use legal 20-card temporary decks and ordinary actions, without editing game state. Seed, deck contents and action traces are saved in the companion JSON.

Binary SHA-256: 797c211f007bceec7288b111c398ef63c898c1eb40447292494b0feb18c62ab1.
The wheel hash remains 348278b5858b4c436863fb949bdbb6b02362601545b89d4d9ce951ae7d0b7606.

### Applicability to this run
Static inspection of all five pool lists and their card mechanics found:
- Frigibax P-B 037 is the only true defender-side flat reducer. Its Weakness is Metal.
- The pool has Fire, Fighting, Darkness, Psychic, Colorless and Water attackers, with no Metal attacker, attack-copy or type-change route.
- Bounded Field is absent.
- Bonsly's Teary Attack reduces the opposing Pokemon's attacks; it is an attacker-side debuff and should not be conflated with Frigibax's defender-side reduction.
- Protective Poncho prevents bench damage, where Weakness does not apply.
- Neither held-out list adds a relevant trigger.

Thus this specific confirmed defect is not a supported explanation for the current Weezing/Suicune deficits. This is a static reachability conclusion, not an exhaustive claim that the engine has no other relevant damage defects. Fix and regression-test the general damage rule separately before relying on broader decks; do not change the active run's wheel midway.

## 2. Simultaneous win conditions: credible, still source-qualified
The source at src/actions/apply_action_helpers.rs:804-827 checks both players' points before remaining Pokemon, exactly as the new reference says.

Community sources describe counting satisfied win conditions instead. That would change some simultaneous endings. The reviewed official FAQs do not establish that rule, so it should remain labeled community-supported until an official rule or retained in-game case settles it.
Sources: https://www.pokemon-zone.com/articles/how-to-play-pokemon-tcg-pocket/
https://www.dexerto.com/pokemon/pokemon-tcg-pocket-players-discover-unfair-rules-for-tying-games-3015305/

Rocky Helmet in Blaziken and Hoopa ex's self-damage in Weezing make simultaneous knockouts possible in the actual pool. I have not measured affected outcomes or established that the rare disputed ending occurred. Shared engine behavior preserves internal comparison, but does not by itself make the results faithful to the real game. Do not call the full rules implementation certified.

## 3. Two documentation corrections
- RULES_FOR_AGENTS.md:72 is wrong about Mega Lucario ex evolving from Lucario. The pinned engine database already has Riolu as its pre-evolution and Combusken for Mega Blaziken ex. This documentation error is not an engine evolution bug.
- rules/README.md:30-31 overstates the support for the entire Checkup sequence. The official FAQ establishes whose end-of-turn card effects resolve first. It does not establish the full player/condition/Ability/KO order inside Checkup. The detailed rules files correctly distinguish community-supported order from unresolved Ability placement and KO timing; the summary should preserve those distinctions.
Official end-of-turn source: https://app-ptcgpt.pokemon-support.com/hc/en-us/articles/57285887108377-If-both-players-have-cards-in-play-with-effects-that-happen-at-the-end-of-each-turn-in-what-order-are-the-effects-applied

No videos were re-reviewed in this check, and the reference's other observed claims were not independently recertified.

## 4. Latest Run 4 result
The latest saved checkpoint when inspected was 3,000,000 games, saved at 05:14 local time, beyond the pasted 2.5M update. The job's saved status is RUNNING. Both scheduled floors are behind it.

| Network | Average margin over k3 | Change since 2.5M |
|---|---:|---:|
| Blaziken | +1.075 pp | -3.700 pp |
| Lucario | +7.900 pp | +0.500 pp |
| Weezing | -11.950 pp | -1.000 pp |
| Altaria | +10.250 pp | -0.025 pp |
| Suicune | -15.825 pp | +3.425 pp |

All 20,000 latest checkpoint win outcomes were recounted. Their paired comparison with the prior 20,000 matched by seed, matchup and seat, and the paired-only counts match state.json. Overall margin is -1.71 pp.

At this checkpoint:
- Blaziken vs Lucario is +3.9 pp, below the required +10.
- All four designated at-least-k3 matchups are above zero.
- 10 of 20 matchups are below -5 pp: all four Weezing matchups, all four Suicune matchups, Blaziken vs Altaria (-16.0), and Lucario vs Blaziken (-8.6).
- Altaria is above k3 in all four matchups.
- Lucario, Weezing and Altaria meet the current plateau rule. Blaziken and Suicune do not, so the normal stopping rule has not fired.
- The final evaluation can select earlier checkpoints per network; the last checkpoint is not automatically the final lineup. Even the best evaluated Weezing and Suicune checkpoints so far still have substantial matchup deficits. Their confirmation games have not yet been played.

The large recoveries and reversals describe real changes on these fixed evaluation seeds. They do not establish the cause of the oscillation. No extra opponent-adaptation experiment was run.

One correction to Opus's phrasing: independent confirmation reduces the risk of selecting a lucky checkpoint; it cannot make a chance pass impossible. Up to two candidates per network can also be compared on the confirmation set. Keep the predeclared gate, and report uncertainty without claiming it eliminates luck.

## Follow-through
Leave the active run unchanged. Give Opus the reproducible damage defect as an engine issue, preserve the simultaneous-win case as provisional, correct the two documentation statements, and assess the final run against the existing per-matchup rules. No extra training or rule changes were authorized or performed in this review.
