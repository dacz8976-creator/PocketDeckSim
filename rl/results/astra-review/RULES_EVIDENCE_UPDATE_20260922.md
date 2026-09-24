# Rules evidence update, September 22, 2026

Astra review of the updated local rules documents and Dustin's supplied review summary. No recordings were reopened, no engine behavior was changed, and no training or crossplay was started or interrupted. The observations below retain the provenance of the rules agent's review; this is not a second frame-by-frame verification.

## Changes to the review queue

- Gladion is no longer supported only by the Japanese blog. The documented review of recording 152812, 04:27-04:30, shows a legal no-target play with both Silvally and their underlying Type: Null already in play. The same review records Brave Buddies receiving its Supporter bonus. This is a consequential legal-action omission: refusing the empty search also denies a useful attack setup. Review the repair for both legal availability and normal Supporter bookkeeping, including consuming the card, using the turn's Supporter allowance, and enabling Brave Buddies. Do not infer a separate bookkeeping bug from a move the engine currently refuses to offer.
- Upgrade the evidence specifically for Gladion. Grunt and Clemont retain their separate source qualifications; the Gladion footage does not test them. The empty-deck prohibition is recorded as Dustin's test/ruling, not something independently reverified here.
- Keep the last-Pokemon/third-point outcome and simultaneous third-point outcomes open. The observed order of point animations does not establish when the game internally checks victory. Do not implement either a loss or a win merely by choosing one interpretation of the Tips.
- Scope the claim about an incorrect tie carefully. The README's argument concerns both players reaching three with exactly one board empty under the two proposed interpretations. It does not establish that every case of both players reaching three must have a winner. The correct priority remains unresolved.
- Eevee's first-turn restriction and replacement among Sleep, Paralysis and Confusion already have card/rules support and engine findings. The proposed in-game checks would corroborate them; their absence does not erase that evidence or block reviewing those repairs. Damage order likewise has official support independent of the still-unreviewed probable Skarmory recording 155818.

The earlier repair priority remains unchanged. Keep unresolved victory priority separate from the already reproduced seat-based double-KO promotion behavior. Preserve Run 4 and crossplay as results of their identified simulator; review the repair batch before rerunning the k3 screen or choosing Run 5's pool.

## Documentation qualifications to carry forward

The current README's opening label "winning/ties/timers" under "Settled" is too broad given its own open victory cases. Checkup healing relative to Poison/Burn also remains open. In `04_actions_cards_effects.md`, the evolution table still labels Wallace on the first turn unresolved, while `05_open_questions.md` records it observed in 150630. Its named-search paragraph also retains a general "Easy to confirm in-game" line despite the Gladion confirmation. These are reconciliation items, not newly discovered engine bugs. The rules files were left unchanged in this review.

Thieving Machine's reveal, Elegant Cape on evolution, and the older reviews' retaliation/retreat observations are useful additional evidence. They do not close the remaining victory, healing, full-hand, or zero-damage Weakness questions. Recording 022627 remains in progress and 155818 unreviewed according to the supplied update.

Sources inspected: `rules/README.md`, `rules/04_actions_cards_effects.md`, `rules/05_open_questions.md`, `RULES_FOR_AGENTS.md`, and the September 21 Run 4 rules-exposure review. This note updates the evidence status of that review's items 6-7 without replacing its historical findings.
