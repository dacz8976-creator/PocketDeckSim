# P2 evidence for questions 10 and 11 — PARTIAL (Oct 9, 2026)

**Status: partial, written in about an hour before Dustin leaves with the laptop. Text only: no build, no run, no video.** Everything about the engine below is from *reading* `main` (b77652d6), not from running it. What is still to do tonight (after 5 pm) is at the end.

Asked (coordinator, Oct 9): the cloud's P2 makes the "hit-back" of five attacks take Weakness. Two questions are left that are evidence, not votes:

- **(10)** Does an attack's hit-back count as *attack damage* for other cards: the attacker's own damage cuts, Disguise, Guts, Hala, Rescue Scarf, Lucky Egg, the attacker's own Rocky Helmet?
- **(11)** If the attack that hits the holder also knocks the holder to the Bench or devolves it, does the hit-back still happen?

## In plain words (for Dustin)

- **Hala cannot meet the hit-back at all.** Hala only protects during the opponent's next turn, and the hit-back always lands on the attacker's own turn, so the two never overlap. Decided by the card text.
- **Everything else in question 10 is open.** Not one recording or official ruling covers a hit-back landing on a Pokémon with a damage cut, Disguise, Guts, Rescue Scarf, Lucky Egg or Rocky Helmet. The card texts can be read either way ("damage from an attack" — is the hit-back that?). The engine today treats the hit-back as *plain damage that nothing interacts with* (except that P2 adds Weakness).
- **One recording would answer most of question 10:** a Pokémon with a flat "−20 damage from attacks" cut (for example Heavy Helmet) attacks a Pokémon carrying one of the five effects. If the cut applies to the hit-back, the game counts the hit-back as attack damage, and Disguise, Guts, Rescue Scarf, Lucky Egg and the attacker's Rocky Helmet very probably follow; if it does not, they probably do not. Each should still be confirmed once, but this is the cheapest first row.
- **Question 11:** the five attacks' effect sits on the Pokémon and, per the official ruling in `rules/06`, "effects on a Pokémon disappear once it returns to the Bench"; and the official Budew ruling says an attack's own effects happen before after-attack reactions. Put together, **no hit-back if the attack's own effect moves the holder to the Bench** — and the engine already agrees for the five attacks. That is an inference from two rulings, not a recording, so I list it as **open, leaning no**. **The engine looks wrong for Rocky Helmet and the Abilities** in the same case (it would still fire from the Bench); that needs one recording too.
- **Devolve:** only one distinct attack text in the database devolves the Defending Pokémon. The holder stays in the Active Spot, so nothing in the text removes the effect; I lean yes (the hit-back happens), but I have not read the engine's devolve path yet. Open.

## The five attacks (plain card text, `engine/database.json` on main)

| Attack | Card (set number) | Own damage | Text (identical wording, only the number changes) | Hit-back |
|---|---|---|---|---|
| Cursed Jewel | Mega Sableye ex (B3b 041; the Sableye review also names two-star prints B3b 081 and B3b 088, which I did not open) | 80 | "During your opponent's next turn, if this Pokémon is damaged by an attack, do **40** damage to the Attacking Pokémon." | 40 |
| Spike Armor | Alolan Sandslash (A3 039) | 20 | same, **40** | 40 |
| Bristling Spikes | Togedemaru (A3b 048, P-A 090) | 30 | same, **30** | 30 |
| Needle Lariat | Chesnaught (B2 010) | 80 | same, **80** | 80 |
| Shell Trap | Turtonator (B1 047) | 40 | same, **20** | 20 |

Two things the text does and does not say: it has **no "in the Active Spot" condition** (Rocky Helmet and the Abilities have one), and it says "damaged by an attack", not "knocked out".

## The interacting cards (plain card text)

| Card | Text |
|---|---|
| Disguise (Mimikyu ex, B2 073) | "When this Pokémon is first damaged by an attack after coming into play, prevent that damage." |
| Guts (Conkeldurr A3 096; Ursaluna has the same Ability, second entry not opened) | "If this Pokémon would be Knocked Out by damage from an attack, flip a coin. If heads, this Pokémon is not Knocked Out, and its remaining HP becomes 10." |
| Hala (B1 222, Supporter) | "During your opponent's next turn, if your Hariyama or Crabominable would be Knocked Out by damage from an attack, it is not Knocked Out and its remaining HP becomes 10." |
| Rescue Scarf (A4 155, Tool) | "If the Pokémon this card is attached to is Knocked Out by damage from an attack from your opponent's Pokémon, put it into your hand instead of the discard pile." |
| Lucky Egg (B3 148, Tool) | "If the Pokémon this card is attached to is Knocked Out by damage from an attack from your opponent's Pokémon, draw cards until you have 5 cards in your hand." |
| Rocky Helmet (A2 148, Tool) | "If the Pokémon this card is attached to is in the Active Spot and is damaged by an attack from your opponent's Pokémon, do 20 damage to the Attacking Pokémon." |
| Damage cuts (many; Heavy Helmet B1 219 is the Tool one) | "This Pokémon takes −20 damage from attacks." (other values: −10, −30; some limited to attacks from certain types or "from your opponent's Pokémon") |

## What the engine does today (`main` b77652d6, read, not run)

1. **Order inside one attack** (`engine/src/actions/attack_outcome.rs`, `into_mutation`, lines 198-282): the attack's own pre-effect → damage with all modifiers (`handle_damage_only`, :216) → Hala-style survival (`apply_survive_knockout_turn_effects`, :229) → a "reaction frame" holding references to the damaged Pokémon (:237-248) → the attack's own post-effect, e.g. a switch (:252) → **the hit-back** (`handle_attack_retaliation`, :268) → knockouts (:279).
2. **The hit-back is applied as raw damage** (`engine/src/actions/apply_action_helpers.rs:614-633`): `counter_damage = get_counterattack_damage(...)` (:622) and then `attacker.apply_damage(counter_damage)` (:625). It does **not** go through `modify_damage` (`engine/src/hooks/core.rs:1819`, where damage cuts and Weakness are applied) or through the Disguise check (`checkapply_prevent_first_attack`, fn at :446, called only from `handle_damage_only` at :576). So **no damage cut, no Disguise, no Guts flip, no Weakness today** on any hit-back.
3. **What counts as a hit-back** (`engine/src/hooks/counterattack.rs:13-36`): Rocky Helmet (:15-17, *no* Active-Spot check there), the temporary `CardEffect::Counterattack` that the five attacks set (:19-27; set in `engine/src/actions/effect_mechanic_map.rs` at :529 (20), :538 (30), :547 (40), :2540 (80)), and Abilities (:29-33).
4. **Rescue Scarf, Lucky Egg**: Rescue Scarf needs `attacking_ref.0 != ko_receiver` (`apply_action_helpers.rs:808-812`); when the *attacker* is knocked out by the hit-back the attacker is the turn player, so the test fails and the Pokémon goes to the discard pile. Lucky Egg needs `is_opponent_attack` (`hooks/core.rs:2485-2493`), the same way. Both are "no" today. (`hooks/core.rs:2373-2374` says it in a comment for the Ability case: "no Weakness, no counterattack in return, and no Rescue Scarf".)
5. **Guts** flips only for damage dealt inside the attack (`apply_action_helpers.rs:476` `guts_would_flip`, `apply_attack_action.rs:345`, `attack_outcome.rs:681-705`); the hit-back never reaches it, so a Guts attacker simply dies.
6. **Hala** (`apply_action_helpers.rs:916-941`): runs for the player that played it, and only on that player's own Pokémon; see "Hala" below for why it cannot meet a hit-back.
7. **Switch and devolve** (`apply_action_helpers.rs:960-987`, `apply_activate`): when a Pokémon is moved to the Bench the reaction frame's references are **remapped to follow the damaged Pokémon** (:963-977) and the Pokémon sent to the Bench gets `clear_status_and_effects()` (:981). So if the attack's own effect switches the holder out, the five attacks' temporary `Counterattack` effect is gone before the hit-back resolves, if `clear_status_and_effects` empties that effect list (to be confirmed; then no hit-back from them — the same result as the official-ruling inference), but a Rocky Helmet or an Ability on that Pokémon is **still read** at its new Bench slot, and `get_counterattack_damage` does not check "in the Active Spot", so they would still fire. I have not run this.
8. **P2 on the cloud branch** (`origin/claude/coin-prevention-round2`, not on main): `handle_attack_retaliation` adds a Weakness extra for the five attacks only (`attack_counterattack_damage(target) > 0`, attacker must be the Active Pokémon) and still ends in `attacker.apply_damage(counter_damage + weakness_extra)`. So **P2 changes none of the behaviours above** except Weakness.

## What is on record

- **The hit-back takes Weakness (Cursed Jewel only):** `rules/02_damage_knockouts_points.md:60`: [OBSERVED 183108 @308 and @386, Oct 5] Cursed Jewel did 60 to a Darkness-weak Houndstone, twice; Dustin Oct 6: "I know it is the case for sableye. It is from an attack the return damage is done, not from an ability." Codex review accepted Oct 6 22:52 UTC (`Pocket Deck Lab/Boss Folder/rules-return-damage-2026-10-06/`). The other four attacks rest on the same wording; none of them has a recording of the hit-back in the notes I searched.
- **Tool and Ability return damage stays flat** (same row; Rocky Helmet 215749; Automated Combat, Oct 6 recording `20261006_220700000_iOS`, five hits, RULE_FINDING.md). These are *not* the five attacks.
- **Which sources "−X from attacks", Disguise, Safeguard and the like ignore** (`rules/02:80-90`): Poison/Burn, Ability damage, Tool damage (Rocky Helmet) and Ability retaliation (Rough Skin): all "no", with [OFFICIAL] Mimikyu ex FAQ for Tool damage. **The table has no row for an attack-borne hit-back; that is exactly the gap.**
- **Retaliation still fires when the holder is knocked out by the attack:** `rules/02:122` (Rocky Helmet ×4, Zangoose, Iron Jugulis). All with the holder in the Active Spot. Battle 225430: Rocky Helmet's hit-back knocked out the attacker, "each player receives one point" (`rules/01:108`); I did not find whether that attacker held Rescue Scarf or Lucky Egg.
- **Sableye video** (`Boss Folder/video-mechanics-flygon-sableye-2026-09-07/sableye-video/EVIDENCE.md`): a direct Cursed Jewel knockout; the game ended right after, so **no hit-back event** and no interaction is shown there (its own "Limits" section says so).
- **Official rulings that bear on question 11** (`rules/06_sources.md:90`, `rules/02:119-124`): JA Detailed Battle FAQ 57281556361113 (Cursed Prose): "effects on a Pokémon disappear once it returns to the Bench"; JA FAQ 57286218211225 (Budew's Prickly Powder): the attack's own effects come before after-attack Abilities; JA Support article 41083304332057 (Grapploct Knock Back): a Pokémon moved to the Bench by the attack and lethally damaged is Knocked Out *on the Bench*. **No official ruling in `rules/06` mentions a hit-back and Disguise, Guts, Scarf, Egg, damage cuts or Rocky Helmet.**
- **Recordings not found:** I did not find the "Battle Logs/Reviewed" or "Recording_QA" folders at depth 4 under `C:\Users\dacz8\Projects` (the Oct 6 note says the original is "archived in Battle Logs/Reviewed", probably outside Projects/OneDrive). I searched the Boss Folder review text (md/txt) for the five attack names: at least 40 files mention them, I read 3 (RULE_FINDING.md, sableye EVIDENCE.md, and the attack lines of the bot-counterattack review, which is about bot code, not games). The rest are mostly "pending review" lists and READMEs; they are to be read tonight.

## Question 10: verdict per sub-case

| Sub-case | Card text says | Engine today | On record | Verdict | What to record |
|---|---|---|---|---|---|
| Attacker's own damage cut | "takes −X damage from attacks": the hit-back is "part of the attack" (it takes Weakness, observed), so it plausibly is damage from an attack; but Weakness evidence does not decide a *card's* wording | not applied (:625 bypasses `modify_damage`) | none | **OPEN** | **Row A (first):** the attacker holds Heavy Helmet (or has a flat "−20 from attacks" Ability) and attacks a holder of Cursed Jewel / Spike Armor / Bristling Spikes / Needle Lariat / Shell Trap. Read the attacker's HP before and after the hit-back (printed amount minus the cut = cut applies). |
| Disguise (Mimikyu ex, intact) | "first damaged by an attack ... prevent that damage" | not checked | none | **OPEN** | **Row B:** an intact Mimikyu ex attacks a holder of one of the five effects. Does the hit-back happen, and is the Disguise used up? |
| Guts (Conkeldurr, Ursaluna) | "would be Knocked Out by damage from an attack, flip a coin..." | no flip, the attacker dies | none | **OPEN** | **Row C:** a Guts Pokémon whose HP is at or below the hit-back attacks a holder (a coin flip appears, or it just dies). |
| Hala | "During your opponent's next turn ..." | not reachable | n/a | **DECIDED BY PLAIN TEXT: they cannot meet.** The hit-back lands on the *attacker's own turn*; Hala protects *its player's* Pokémon only during the *opponent's* turn. For the same player to have both, Hala would have to be active on its own player's turn, which its text excludes. | none |
| Rescue Scarf | "Knocked Out by damage from an attack from your opponent's Pokémon" | no (attacker is the turn player) | none (225430 not checked for Scarf) | **OPEN** | **Row D:** an attacker holding Rescue Scarf is knocked out by a hit-back (try the attack-borne one *and* Rocky Helmet): card to the hand or the discard pile? |
| Lucky Egg | same wording as Rescue Scarf | no | none | **OPEN** (same as D) | In the same recording: does the player draw to 5? |
| The attacker's own Rocky Helmet | "in the Active Spot and is damaged by an attack from your opponent's Pokémon" | no chain (flat damage only) | Ability/Tool retaliation does not trigger a second one ([COMMUNITY], `rules/02:85`), but that is Rough Skin, not the five attacks | **OPEN** (for the five attacks) | **Row E:** a Rocky Helmet holder attacks a Spike Armor holder; does the Sandslash side take 20 back from the helmet? |

Grouping: if Row A shows the cut **applies**, the hit-back counts as attack damage and B, C, D, E very probably follow (still worth one confirmation each); if it **does not apply**, they very probably all fail the same way and the engine's "flat, no interaction" is right, except Weakness.

## Question 11: verdict per sub-case

| Sub-case | Card text / rulings | Engine today | Verdict | What to record |
|---|---|---|---|---|
| The attack's own effect moves the holder to the Bench (e.g. any "switch out your opponent's Active Pokémon" attack), five attacks | "if this Pokémon is damaged": already damaged; but "effects on a Pokémon disappear once it returns to the Bench" and attack effects come before reactions | no hit-back (effect cleared, `apply_action_helpers.rs:981`) | **OPEN, leaning no hit-back** (inference from two rulings, never observed) | **Row F:** a holder of Cursed Jewel / Spike Armor etc. is hit by an attack that also switches it out (Grapploct's Knock Back is the known one). Does the attacker take the hit-back? |
| Same, holder carries Rocky Helmet or an Ability retaliation | "in the Active Spot and is damaged": true at damage time, false after the move | would **still fire** from the Bench (:622, no Active check) | **OPEN, engine probably wrong if reactions are judged after the effects** | **Row G:** the same attack into a Rocky Helmet holder and an Ability holder (Rough Skin family). |
| Lethal damage plus the move (holder KO'd on the Bench) | Grapploct ruling: KO happens on the Bench | frame is remapped to the Bench slot, hit-back follows the same path as above | **OPEN** | in Rows F and G, make one of the hits lethal |
| Devolve (one distinct attack text in the database, `engine/database.json:33460`; owner not looked up) | holder stays Active; nothing removes the effect | not read | **OPEN, leaning yes** | **Row H:** devolve a holder of one of the five effects and check whether the hit-back follows. First read the engine's devolve path. |

## Not done yet (tonight, after 5 pm; all reading)

1. Read the rest of the Boss Folder review text that names the five attacks (the other 37 or more files, mostly "pending review" lists and READMEs), and look for any case with a damage cut, Disguise, Guts, Rescue Scarf, Lucky Egg or Rocky Helmet on the *attacker's* side.
2. Find "Battle Logs/Reviewed" and "Recording_QA" (outside `Projects`?) and search their review text, not the video.
3. Check battle 225430's reviewed text for the attacker's Tool (Rescue Scarf? Lucky Egg?).
4. Read the engine's devolve path, and `clear_status_and_effects` to confirm that it empties `CardEffect::Counterattack`.
5. Open the second Guts entry (Ursaluna) and the two-star Sableye prints, in case their text differs.
6. Put Rows A to H into the shot list in the usual format once Dustin has seen this.

## Sources read (main b77652d6 unless stated)

`engine/database.json` (card texts), `engine/src/actions/attack_outcome.rs`, `apply_action_helpers.rs`, `engine/src/hooks/counterattack.rs`, `hooks/core.rs`, `rules/01`, `02`, `04`, `05`, `06`, `07` (search hits), `origin/claude/coin-prevention-round2` (diff of `apply_action_helpers.rs`, commit list), `Pocket Deck Lab/Boss Folder/rules-return-damage-2026-10-06/.../RULE_FINDING.md`, `.../video-mechanics-flygon-sableye-2026-09-07/sableye-video/EVIDENCE.md`.
