# The chance-ending stratum (PREREG_RUN3 section 5), fixed before any run 3 row

- **The rule** (section 5: "counted as `../run1/RESULTS_run1.md` counted them"): a point is chance-ending when an accepted line of it (the key or an acceptable line) reaches a plan that frozen-7's plan lister ends at a chance event (`plan_end` = `chance`). A plan the lister ends at the opponent's choice (Sabrina, a promotion) is not chance-ending (addendum 5, R1).
- **The check that this is run 1's count:**
  - `check_lister_v2.py` on run 2's own frozen inputs (`run2/live-20261021T2000Z/in/`, with v1.6's generic `notes` and `approximate_reason` taken out; frozen-7's judge code reads neither) gives **33 of the 49 primary points**;
  - that is RESULTS_run1's "At 33 of the 49 primary points, the accepted plan ends at a chance event".
  - v1.6's recorded segments alone give 31, because they don't know the lister's Raticate and Sabrina stops.
  - No bot played: the lister only lists plans.
- **Run 3:** from the frozen assembly's lister report (`assembly_final/lister_report.json`, the frozen references), **168 of the 258 primary points**: `stratum_chance_run3.txt`.
- **Pooled:** run 2's 33 plus run 3's 168, **201 points**: `stratum_chance_pooled.txt`.
- In both runs the key line alone gives the same sets as "any accepted line".
- **How it is reported:** with its interval and no verdict, for run 3 alone (0.95) and pooled (0.975), through `pool_runs.py --stratum`.
