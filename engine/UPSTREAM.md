# Engine and upstream merge notes

Upstream: `https://github.com/bcollazo/deckgym-core.git` (`upstream`). Fetched main: `fda48391a4747c7d9085e6a95520b731cee0b546` (2026-08-30). Divergence / merge-base: `8b40f55d889b89634467cca7da153114789ffdf4` (2026-07-30). The accumulated Aug22-and-later fork tree, including B4a, is preserved as `12938ca` on `engine/unified-2026-09-09`.

The upstream-based single commit `79ba7ebd65d822afb8dac7acfb54ffa02ddb7cf4` on `upstream/status-restrictions` is prepared against the fetched upstream main for a PR; it uses upstream State::apply_status_condition for the fixture (the fork builder helper is unavailable upstream). Its equivalent in the qualified canonical engine is the standalone commit `1c4a05835e937ddbd13dacf60493077b73a4fea1` (**fix: disallow attacks and retreats while asleep or paralyzed**, 74 added lines across five files) contains the restriction and a plain test for upstream submission. Historical replay fixtures remain in the separate integration commit. No PR has been published. Other status lifecycle/forecast changes remain separate.

Known merge-conflict areas (semantic changes, beyond the preserved CRLF churn):
- `src/game.rs`: fork decision randomness, forecasts, state adoption and terminal/turn handling.
- `src/players/`: fork observations, public reply checking, K search/evaluation and player factory; preserve these when importing card logic.
- `src/observation.rs`: fork-only hidden-information boundary and public effect forecasting, including Boiler Smog.
- `src/actions/effect_mechanic_map.rs` and `src/actions/effect_ability_mechanic_map.rs`: fork card registrations and mechanic dispatch; merge new upstream entries instead of replacing either map.
- Also check status-related `src/hooks/{mod,retreat}.rs`, `src/move_generation/attacks.rs`, `src/actions/{apply_action,apply_action_helpers}.rs`, and their regression tests when importing shared engine changes.

Before each new-set merge: `git fetch upstream`; inspect `git diff --ignore-space-at-eol --stat upstream/main HEAD -- src tests` and `git diff --ignore-space-at-eol upstream/main HEAD -- <file>`. Import upstream card commits with their tests and reconcile these conflict areas; this is not approval to discard fork behavior or reimplement already available upstream cards.

Five B4a printings remain **RulesUnverified** (not missing dispatch):
- **B4a018 Hisuian Basculegion:** Checkup points are provisionally assigned to the outgoing turn for “last turn”; old midgame saves lack prior point history (cards8 qualifications).
- **B4a069 Team Rocket’s Researcher:** uncapped actual coin sampling; transfers beyond ten cards and a final shuffle even with zero heads/no eligible card remain unobserved; exact search has a 4096-successor limit (cards7/cards8).
- **B4a085 Team Rocket’s Researcher:** same mechanic and qualifications as B4a069; alternate printing is not separate rules evidence.
- **B4a051 Gholdengo:** cards7 implements Keep/Reroll of a whole Trainer batch; cards8 retains unverified coin visibility, Stadium activator eligibility and Penny-versus-Portrait attribution; unbounded visible batches stay unpriced. The later video shows an evolve-before-Lucky-Ice-Pop opportunity, not a guaranteed rescue or resolution of those rules.
- **B4a109 Gholdengo:** crown printing identified in the public-attack-threat video; evolving before the first Pop would offer Luxury Coin, but replacement heads is unknown and a post-hoc Buzzwole reply remains possible; retain the same cards7/cards8 qualifications as B4a051.

Sources: [cards7](../Boss%20Folder/card-support-luxury-coin-2026-09-05/README.md), [cards8 qualifications](../Boss%20Folder/card-support-misty-geometric-2026-09-06/RULES_AND_LIMITATIONS.md), [accepted threat-benchmark video review](../Boss%20Folder/public-attack-threat-benchmark-2026-09-07/video-review/REVIEW.md). The video was reused, not reviewed again. These five statuses are unchanged by engine consolidation.
