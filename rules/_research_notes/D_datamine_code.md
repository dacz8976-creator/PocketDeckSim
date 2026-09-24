# D — Datamines, extracted game code/data, and open-source simulators

Research pass: 2026-09-21. Scope: publicly available datamines/dumps/simulators only (no APK download, no decompiling performed).

---

## 1. Official Pokémon Support FAQs (OFFICIAL — highest authority found)

Not a datamine, but public, official, and directly answers several QUESTIONS.md items. Worth treating as ground truth over anything else in this doc when they conflict.

### Battle Rules FAQ
URL: https://support.pokemon.com/hc/en-us/articles/38906248102292-Pok%C3%A9mon-TCG-Pocket-Battle-Rules-FAQ
Last updated (per page): **May 12, 2026**. Current relative to ruleset (rules change rarely; card pool is now B4a but this is a rules FAQ, not a card list, so it should still be valid).

Facts (grade **OFFICIAL**):
- "If no Energy symbol is displayed to the left of the attack name on a card, then it is an attack that can be used without any Energy attached to the Pokémon." (energy-free attacks — relevant to Q5/first-turn attack legality)
- "Points are gotten only when an opponent's Pokémon is Knocked Out" — effects that merely *discard* a Pokémon (not KO it) do not award points. Directly relevant to Q12/Q20.
- Jolteon ex's Electromagnetic Wall only triggers on Energy attached **from the Energy Zone**, not from the Discard Pile or other transfer effects — confirms the game engine distinguishes "attach from Energy Zone" as a distinct event type from other energy-attachment effects (relevant to Q46).
- Buzzwole ex's Big Beat "once per turn" restriction resets if it returns to the Bench and comes back — i.e., the once-per-turn flag is tracked per time-in-Active-spot-this-turn, not truly "once per turn globally" for that ability text (relevant to Q34).
- Scizor's Gale Thrust bonus requires moving from Bench to Active **during the same turn** it attacks.
- Prank Spinner reveals only one card (chosen from either player's hand) and shuffles it into its owner's deck — clarifies a specific card, not general hidden-info rule (Q41/Q43 adjacent).

Notably, this FAQ explicitly does **not** cover deck construction, opening hand, first-turn restrictions, hand limits, turn timers, Checkup order, Weakness mechanics, evolution/retreat rules — it only clarifies specific confusing card interactions. For the foundational ruleset it says: *"Please find more information about Pokémon TCG Pocket's game rules in Tips or by tapping the question mark button displayed at the top-right part of various screens of the app."* — i.e., the authoritative full rules text lives **in-app** (Tips / "?" button), not on the public web. That in-app text was not accessible to this research pass; a hands-on session (see §6) could screenshot/OCR it without needing any decompilation.

### Gameplay FAQ
URL: https://support.pokemon.com/hc/en-us/articles/30330309361172-Pok%C3%A9mon-TCG-Pocket-Gameplay-FAQ

Facts (grade **OFFICIAL**):
- Disconnection handling: **"If you disconnect during versus matches, you can rejoin the match within around 120 seconds. If you cannot reconnect by then, you will lose the match."** — Strong indirect evidence of server-side match state (see §5).
- Ties: **"If your game ends in a tie, your ranked match points will not increase or decrease. However, your win streak points will be reset."** (relevant to Q14/Q15 — draws don't move Ranked rating, but do reset streak bonuses.)
- Rental decks cannot be used in versus (PvP) battles.
- Again defers to in-app "?" button / Tips for core rules text.

---

## 2. bcollazo/deckgym-core (Rust) — the main open-source simulator

URL: https://github.com/bcollazo/deckgym-core
Cloned locally to `/home/claude/rr/scratch_D/deckgym-core` (depth 1) and grepped/read directly.

- **Last commit: 2026-09-17** (4 days before this research pass) — actively, heavily maintained. 1,429+ commits.
- **Card coverage: 3,340 / 3,761 cards implemented (88.8%)** per README badge.
- **Confirmed current through set B4a**: `src/card_ids.rs` contains `B4a001Volbeat`, `B4a007TeamRocketsMoltresEx`, etc. — matches the project's card pool ceiling.
- It is what powers deckgym.com (a real deckbuilding/simulation site used by players), not a toy project.
- **No citations to Limitless or "verified against real game" language anywhere in the repo** (grepped for "limitless", "verified", "real game", "confirmed", "bulbapedia" — no hits in rule-implementation context). Every rule below is graded **SIMULATOR-DOC**, not SIMULATOR-EVIDENCED — it's the contributors' best interpretation of card text + community consensus, encoded as passing unit tests, not sourced from the real client or Limitless data.
- The repo has an extensive test suite specifically targeting rule-ORDER questions (exactly the QUESTIONS.md items), e.g. `tests/pokemon_checkup_test.rs`, `tests/mechanics/end_of_turn_knockout_ordering_test.rs`, `tests/tools/raikou_rocky_helmet_order_test.rs`, `tests/mechanics/confusion_test.rs`, `tests/mechanics/retreat_test.rs`, `tests/mechanics/basic_knockout_happy_paths_test.rs`. This is the single best "someone already thought hard about the ordering questions" resource found.

### Concrete rule facts extracted from source (all SIMULATOR-DOC)

**Hand limit (Q8):** `src/state/mod.rs`, `maybe_draw_card()`:
```rust
fn test_maybe_draw_card_respects_10_card_hand_limit() {
    ... for _ in 0..10 { state.maybe_draw_card(0); }
    assert_eq!(state.hands[0].len(), 10);
    // 11th draw should be a no-op
    state.maybe_draw_card(0);
    assert_eq!(state.hands[0].len(), 10);
    assert_eq!(state.decks[0].cards.len(), 10); // card stays in deck, not discarded
}
```
Hand limit = **10**, and a draw that would exceed it is simply **skipped** (the card stays in the deck) — not drawn-then-discarded.

**Turn cap / draw (Q10):** `src/state/mod.rs`, `advance_turn()`:
```rust
self.turn_count += 1;
if self.turn_count > 30 {
    self.winner = Some(GameOutcome::Tie);
    return;
}
```
Turn cap of **30 turns → automatic Tie**. `test_advance_turn_declares_tie_after_turn_30` confirms.

**First-turn window (Q5):** `is_users_first_turn(&self) -> bool { self.turn_count <= 2 }` — turns 1 and 2 (i.e. each player's very first turn) are both treated as "first turn" for restriction purposes.

**Energy Zone at game start (Q6):** `State::initialize()`:
```rust
// Pre-populate each player's `next` energy. On turn 1, neither player has rotated yet,
// so both keep `current = None`. The player going second's queue will rotate at turn 2,
// promoting `next` into `current`; the player going first's queue rotates at turn 3.
state.energy_zone[0].next = Some(roll_energy(&state.decks[0], rng));
state.energy_zone[1].next = Some(roll_energy(&state.decks[1], rng));
```
Both players get a **"next" energy preview generated at game start**, before Turn 1 (matches Q43 — next-energy is public to both from the start). Neither player has a **usable/current** energy on their own Turn 1 in this model — first attachable energy shows up at the start of the *second* turn overall (player 2's turn 1) and the player-1-going-first player doesn't get a usable energy until their second turn (turn 3 overall). This is a specific, testable claim worth validating against real gameplay footage.

**Damage calculation order (Q16/Q17) — the single most useful find.** `src/hooks/core.rs`, damage-calc function:
```rust
let pre_weakness = (base_damage
    + ability_damage_increase
    + increased_turn_effect_modifiers
    + increased_attack_specific_modifiers
    + increased_vulnerability_modifiers
    + type_boost_bonus
    + stadium_damage_bonus
    + future_booster_damage_bonus)
    .saturating_sub(                      // <-- floors at 0 HERE, before Weakness
        reduced_card_effect_modifiers
            + reduced_turn_effect_modifiers
            + heavy_helmet_reduction
            + metal_core_barrier_reduction
            + steel_apron_reduction
            + intimidating_fang_reduction
            + ability_damage_reduction,
    );
let final_damage = match weakness_application {
    WeaknessApplication::None => pre_weakness,
    WeaknessApplication::Flat(amount) => pre_weakness + amount,   // +20, ADDED AFTER reductions
    WeaknessApplication::Double => pre_weakness * 2,              // Bounded Field stadium: doubles everything
};
```
deckgym's modeled order is: **base + attacker-side increases → subtract defender-side reductions (floored at 0 via `saturating_sub`) → THEN add Weakness (+20) on top.** Consequence baked into this model: **Weakness still applies (adds +20) even when the pre-weakness net damage has already been reduced to exactly 0** by defender-side reduction — because the floor-at-0 happens before Weakness is added, not after. This is a direct, testable answer to Q16's "is Weakness applied before or after reductions" question — but it is the *simulator's* modeling choice, not a confirmed real-game fact (no citation given).

**Weakness and Bench (Q17):** `get_weakness_application()` takes `is_active_to_active: bool` and returns `WeaknessApplication::None` immediately if `!is_active_to_active`. In this model, **Weakness never applies to bench-hitting damage** (spread/snipe attacks), only Active-vs-Active. Also: `type_boost_bonus`, `future_booster_damage_bonus`, and `stadium_damage_bonus` are likewise gated to `is_active_to_active` only — i.e. several attacker-side bonuses are modeled as Active-only too, while defender-side reductions (Heavy/Metal-Core/Steel Apron/ability reduction) generally still apply regardless.

**Checkup / KO timing (Q11/Q20/Q21):** `tests/mechanics/end_of_turn_knockout_ordering_test.rs` encodes the claim that **all Checkup-phase effects (burn damage AND heal-during-checkup abilities like Garganacl's Blessed Salt) apply first, and the Knock-Out check only happens after the full checkup batch resolves** — not immediately after each individual effect. Comment: *"The knockout check must not run until all of these checkup effects have applied, not immediately after burn's damage alone."* Also confirms **Knocking out a Mega ex awards 3 points** and that reaching 3 points **immediately ends the game** (short-circuits any pending promotion).

**Retreat clears Confusion (Q23/Q24/Q31):** `tests/mechanics/confusion_test.rs`, `test_confusion_cleared_on_retreat` — retreating (or being switched) to Bench removes Confused status in this model. Retreat also discards the chosen Energy to the discard pile (`tests/mechanics/retreat_test.rs`).

**Rocky Helmet vs. Knock Out / promotion order (Q21):** `tests/tools/raikou_rocky_helmet_order_test.rs` — models the sequence as: attacker deals damage → defender's Rocky Helmet retaliation is queued as part of the SAME damage-application step (not a separate later trigger) → if that retaliation KOs the attacker, the attacker's controller is then forced to `Activate` (choose a promotion) before the turn can end. It also has a specific regression test that a Pokémon (Jumpluff ex) that forces a bench-switch on itself still **takes Rocky Helmet retaliation damage even though it's the one switching**, confirming retaliation is tied to "was damaged by an attack," not "is currently Active when checkup runs."

Because none of this is cited to real gameplay evidence, treat every fact above as **SIMULATOR-DOC**: a plausible, tested, internally-consistent model built by a large community of contributors (many recent PRs from named contributors implementing specific card mechanics), but not proof of the real app's behavior. It is, however, the best available structured hypothesis set to validate against Dustin's ladder games or Limitless-observed interactions.

---

## 3. Structured card-data repos (text/metadata only — no effect-timing enums found)

Several public repos publish PTCGP card data as JSON, scraped from in-app data or official sites, not IL2CPP dumps:
- https://github.com/flibustier/pokemon-tcg-pocket-database — "complete cards and sets JSON database." Fields found in README: set/number/name/rarity/image, element type, stage, HP, retreat cost, weakness, set metadata (multilingual), rarity/pull-rate tables. **No structured effect/attack-logic fields, no effect-ID enums, no timing constants.** No stated update date or explicit B4a confirmation in the README.
- https://github.com/PocketDecks/pokemon-tcg-pocket-cards — versioned JSON on npm, deck-builder numbers, scraping/validation tooling. Same category (card text, not engine logic).
- https://github.com/hugoburguete/pokemon-tcg-pocket-card-database, https://github.com/chase-9234/pokemon-tcg-pocket-cards — similar card-database repos, not independently verified in this pass.

Grade: **COMMUNITY** (scraped/curated card text). None of these expose battle-engine internals (no Checkup order, no damage-stage enums, no timers). They would help confirm card TEXT (already available locally per the task brief) but not RULE ORDERING.

---

## 4. RaenonX-PokemonTCGP — an actual APK-datamining toolchain (mostly private)

URL: https://github.com/RaenonX-PokemonTCGP

This GitHub org publicly lists a repo called **`pokemon-tcgp-apk-dumper`** (C#) described as extracting data from the game's APK for datamining, plus `pokemon-tcgp-aladin-index` (an index of extracted game data) and CI tooling. The org's own note states **"most of the repositories are private"** — i.e., the actual extracted master-data repo and the site/API that presumably serves it are not public. This confirms datamining of PTCGP does happen and is tooled (someone has a working APK→structured-data pipeline), but the *output* (which would include effect IDs/timing enums, if it captures them) is not publicly accessible. Grade: **DATAMINE (tooling confirmed public; extracted data confirmed private)**.

---

## 5. Client-side vs. server-side battle logic

No definitive public statement (dev blog, interview, or datamine) was found that says explicitly "battle logic runs on the server" or "runs on the client." Evidence gathered, in order of strength:

- **OFFICIAL, indirect but fairly strong**: the Gameplay FAQ's disconnect handling — *"you can rejoin the match within around 120 seconds. If you cannot reconnect by then, you will lose the match."* A match that can be *rejoined* mid-battle after a full disconnect, with a defined timeout that resolves the game (a loss), strongly implies the **authoritative match state is held on a server** (or at least synced/validated there), not purely peer-to-peer or fully client-local — otherwise a disconnected client would have no state to rejoin. This is the best evidence found either way.
- **COMMUNITY, weak**: cheat/mod articles (Pocket Tactics, hackerbot.net "mod APK" listings advertising things like speed hacks) show that *some* client-side manipulation is possible and gets flagged by anti-cheat/data-tampering detection (per Pokémon Company's own warning quoted by Pocket Tactics: "data tampering, real money trading, and other behaviors that violate the Terms of Use"). This is consistent with either architecture (client-authoritative games get memory-edited; server-authoritative games get their *client display/inputs* tampered and flagged) and does not resolve the question on its own.
- No teardown, blog post, or datamine specifically documenting the network protocol, RPC calls, or a server/client split for turn resolution was found in this pass (see §"protobuf/grpc" search — no public proto definitions exist for PTCGP, unlike e.g. Pokémon GO's POGOProtos).

**Conclusion: most likely server-mediated/server-authoritative for ranked/versus PvP** (based on the reconnect-window fact), but this is inference from one FAQ sentence, not confirmed. Genuinely open.

---

## 6. What a hands-on code read would require, and its likely yield

Not attempted (out of scope), but concretely, to go further than this doc:

1. **Static IL2CPP dump** (would answer rule *code paths*, e.g. `Checkup`, `Battle*`, `Effect*` class/method names and any timing enum, but only if logic is compiled into the client at all):
   - Requires: the APK/IPA itself (explicitly excluded from this task), `Il2CppDumper` (github.com/Perfare/Il2CppDumper) or `Il2CppInspector` to produce `dump.cs` + metadata from `libil2cpp.so` + `global-metadata.dat`.
   - Unity/IL2CPP metadata is *not* encrypted by default in most titles, but many live-service mobile games (PTCGP included, going by RaenonX's dedicated "apk-dumper" tool rather than a stock dumper) apply extra obfuscation/packing on top of stock IL2CPP, which is why a purpose-built dumper exists for this game specifically rather than people just running the generic tool.
   - **Yield is capped by architecture**: if battle resolution is genuinely server-authoritative (per §5), the *client* IL2CPP may only contain UI/presentation logic, request-building, and client-side prediction/validation — the actual Checkup-order/damage-order code could live entirely server-side and be invisible to any client dump. This is the single biggest reason a client dump might disappoint despite the effort.
   - Class/method names (`Battle*`, `Effect*`, `Checkup*`) would still be very informative even as just a dependency graph/enum list, independent of full decompilation quality.

2. **Network capture** (would answer client-vs-server directly, and possibly show a serialized turn-result/effect-log that reveals ordering, without needing any code dump):
   - Requires: a rooted/jailbroken device or an MITM proxy (mitmproxy/Charles) with a trusted cert installed on the device or via SSL-pinning bypass (e.g., Frida script) since most live-service games pin certificates.
   - If PvP battles are server-computed, packet captures of a real match could reveal an ordered effect/event log (e.g., "Checkup: apply poison P1, apply poison P2, apply burn P1, apply burn P2, resolve KOs") straight from the wire, which would be the most direct evidence available short of source code.
   - This is more legally/ethically gray than a static dump and explicitly not something to do without the owner's sign-off; flagging it here only as the theoretically highest-yield hands-on option.

3. **In-app "Tips" / "?" text**: the official Battle Rules FAQ explicitly points to in-app help text as the canonical rules reference. This requires **no reverse engineering at all** — just opening the app and reading/screenshotting the Tips screens and the "?" buttons on Setup/Checkup/Attack screens. This is by far the lowest-effort, lowest-risk, highest-authority option and should probably be done before any code-level approach.

---

## 7. Open questions after this pass

- No public PTCGP-specific IL2CPP dump repository or proto/gRPC definition set was located (unlike some other live-service titles). If one exists it is not indexed by GitHub search under the obvious names.
- `frankiesardo/openpocket` ("deterministic rules and browser AI") appeared in search results but returns 404 as of 2026-09-21 — likely deleted, renamed, or made private since being indexed; could not be evaluated.
- deckgym-core's issue tracker could not be queried in this environment (GitHub API access to this repo is disabled for the session's default credentials); its issues/PR discussions might contain real-game evidence for specific rules (e.g., bug reports saying "this doesn't match the real app") that a maintainer or the owner with GitHub access could check directly at https://github.com/bcollazo/deckgym-core/issues.
- The in-app "Tips" screens (pointed to by the official FAQ as the canonical rules source) were not accessible from this research environment — reading them requires the actual app.
- Whether battle logic is client- or server-side remains an inference (from the reconnect-window FAQ line), not a confirmed fact.
