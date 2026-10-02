# Cross-check: the harness's km3 replays the official run game for game (Oct 2, 2026)

The laptop Opus asked for the check that closes the gap between "km3 equals itself in the harness" and "the harness's km3 is the pinned km3".

**What was compared.** The first chunk (`c00`, 50 deals) of each of the four seat files of `rl/results/draft_A_v_fire_2026-10-02/games/` (main d4e0cef9): draft A and deck 13, each against the Fire list (`rl/results/b2e_card_check_2026-09-26/decks/h-charizardy_entei.txt`), km3 on both sides, the list under test in seat 0 (seeds 23,200,000,000 + i) and in seat 1 (23,200,000,500 + i). That is 4 x 50 = **200 games**.

**How the seeding maps.** The official run calls `deckgym simulate --num 50 --players km3,km3 --seed S --seed-stream -p DECK0 DECK1` with `S = 23,200,000,000 + 500 x seat + 50 x chunk`, so game `j` of a call plays seed `S + j`, the list under test is the first deck in seat 0 and the second in seat 1. The harness plays deal `i` of the pair at position `p` with seed `seed_base + p x pair_stride + i` and, by default, the same seed in both seats. So each seat was run as its own manifest: a single deck and opponent (`p = 0`), `pair_stride` irrelevant, `seats = [seat]`, `seed_base = 23,200,000,000 + 500 x seat`, `deals = 50`, km3 as both pilot and reference. The deck files are the pinned ones (read from main's tree). Nothing else needed mapping: the first player comes from the seed in both (the coin in `State::initialize`), the harness's `points` are `[deck, opponent]` where the official `final_points` are `[seat 0, seat 1]` (swapped for the seat-1 files), and the harness's `plies` is the engine's tick count, the number the engine's own results file calls plies (every applied action, forced single moves included); `turns` is the final `turn_count`.

**Result: all 200 games match on every field.** Winner (including draws: none), final points, final turn, plies and who went first: 200 of 200 on each, and 200 of 200 on all five at once. Output of the comparison: `{'games': 200, 'winner': 200, 'points': 200, 'turns': 200, 'plies': 200, 'first': 200, 'all': 200}`.

So the harness's km3, built against main's `engine/` tree `38af8b0cc4f35fdccc647ed540a56ec8f5e6c1d5` (equal to the pinned release main-8626a35's), plays exactly the games the pinned `deckgym` program played in the official run. `crosscheck_script.sh` is the script that produced it.

Program: sha256 629e216ca350e33e6ec38bc4bcda96ba8348d92bfdb9a8909c24fb92e5ab9d25
