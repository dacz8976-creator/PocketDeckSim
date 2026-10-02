# Does the bot value Turbo Shark's Energy on the Bench? (a code read, Oct 2)

Dustin, Oct 2 (laptop chat, verbatim): "sharpedo is good because it gives the bench pokemon energy. Not sure if the bot treats that as a proper reward".

This is a read-only code read by a laptop Opus subagent, of main 9e139e65 (`engine/src/players` is the same as the pinned engine's). No game was played and nothing was changed.

## Bottom line

**Yes, km3 undervalues Energy on the Bench, by about a factor of 3 to 5.**
- The bot only counts an Energy on a Benched Pokémon as "this Pokémon is a bit sturdier". It never counts it as "a second attacker will be ready a turn sooner".
- Alolan Vulpix, the Bench target draft A's plan wants, is the worst case. The bot prices it by Vulpix's own weak attack (Gnaw [W]), not by Alolan Ninetales ex's Binding Snow [WW].

## How km3 scores Bench Energy

km3 is kog's scoring with kt switch 1 and N2 (`value_functions.rs:476, 482, 488`). Its Bench-readiness term is weighted 0 (kq's; lines 813-819 never run).
- **The HP × Energy term** (`value_functions.rs:877, 2128-2141, 2607-2620`): each Pokémon is worth its HP left × (Energy toward its own priciest attack + 1). Benched Pokémon count fully.

  | Benched Pokémon | each [W] adds | up to |
  |---|---:|---|
  | Alolan Ninetales ex | +150 | 2 Energy |
  | Lapras | +110 | 3 Energy |
  | Mega Sharpedo ex | +190 | the first only |
  | Alolan Vulpix (priced against Gnaw, not Binding Snow) | +60 | the first only |
  | Carvanha | +50 | the first only |

- **Readiness** (weight 500, `value_functions.rs:884-892, 2664`): this reads the Active only. The same Energy on an Active Ninetales ex is worth +150 + 250 = 400, against 150 on the Bench. On an Active Vulpix it's 310, against 60 on the Bench.
- **The damage clock** (100 a turn; `value_functions.rs:1761-1765, 1317-1370`): it picks one threat from all your Pokémon, Bench included, and ignores the cost of getting it into the Active Spot. Bench Energy only moves the clock when it makes that Pokémon the best threat. A ready backup attacker is never counted.
- k3 works the same way (`players/mod.rs:542-550`, `value_functions.rs:1206-1215`).

## How the search handles Turbo Shark

- Turbo Shark puts one Attach choice per Benched Water Pokémon on the stack, with no option to decline (`actions/apply_attack_action.rs:2452-2471`). So arming is automatic whenever there's a target: 912 of 955 Turbo Sharks in the test.
- The target pick is an ordinary search step (`expectiminimax_player.rs:323, 940-960`). When Turbo Shark is the third action of a line, the pick falls past the depth limit, and the line is scored mid-attack with the Bench Energy missing (`:833, 905`).
- Whatever the line, an armed Benched Pokémon shows up only through the static score at the leaf.

## What the test's games show (`RESULTS.md`, `games/`)

- With 2 or more Benched targets (747 cases), the Energy went to:

  | target | times |
  |---|---:|
  | Alolan Ninetales ex | 321 |
  | Lapras | 209 |
  | Alolan Vulpix | 114 |
  | Mega Sharpedo ex | 69 |
  | Carvanha | 34 |

  That's the HP × Energy order.
- From Mega Sharpedo ex's first evolution on (2,849 own turns), the attacks were: Binding Snow 1,237, Turbo Shark 955, Surf 209, others 47, no attack 401.

## The smallest changes that would fix it (not made; Dustin's call)

- **Turn on kq's Bench-readiness term for km** (weight 250; it measures a Benched Pokémon against its highest evolution, `value_functions.rs:3099-3135`). A [W] on a Benched Vulpix would then add +125, for half of Binding Snow. That's one new setting plus a player code, so it would be a new bot candidate under the usual procedure. kq3 was not adopted (`rl/RUN5.md:457`), and "the kq/kv bench-credit line" is on RUN5's "Not doing" list (`:558`).
- **Make the Turbo Shark target pick free in the search,** as queued damage already is (`expectiminimax_player.rs:663-717`), so the third-action blind spot goes away.
