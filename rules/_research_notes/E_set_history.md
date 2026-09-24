# E — Set-by-set mechanics & rule-change history (Pokémon TCG Pocket)

Scope: mobile game Pokémon TCG Pocket (Creatures/DeNA), launch Oct 30 2024 through B4a (2026).
Grades: OFFICIAL (direct official page/announcement) / OFFICIAL-QUOTED (official text quoted by a secondary source) / COMMUNITY (fan-site/community, no official text) / MEMORY-UNVERIFIED (from training data, NOT a verified finding — flagged only, never used as a finding).

Work in progress — appending as research proceeds. Do not treat an absence of an entry as "nothing happened" — it may mean not yet researched.

---

## Status / TODO
- [x] Build set list with release dates (A1 → B4a + promos)
- [x] Identify new mechanic per set — every set A1–B4a individually checked via Bulbapedia set pages (all COMMUNITY grade)
- [x] Rules text for each new mechanic — see §2 (some thin due to WebSearch budget exhaustion mid-session; WebFetch continued to work)
- [x] Chronological errata/balance/rule-change list — see §3 (built mainly from Bulbapedia's official-app version-history table)
- [x] Physical-vs-Pocket behavior diffs — see §4
- **Session note: WebSearch tool hit its call budget (200/200) partway through research; all research after that point used WebFetch only (direct/guessed URLs), which still worked. Flagging in case some remaining gaps would have been closed by one more search.**

---

## (1) Set timeline table

Dates below: Bulbapedia per-set pages used as primary (each fetched directly this session); pokemon-zone.com/ptcgpocket.gg gave slightly different dates for several sets by a few days (noted as X/Y where they disagree with Bulbapedia). All COMMUNITY grade (Bulbapedia is a wiki, not primary-official) unless otherwise marked.

| Set code | Name | Release date | New mechanic(s) introduced |
|---|---|---|---|
| A1 | Genetic Apex | Oct 30, 2024 worldwide (NZ soft-launch Sep 26, 2024) | Launch/base rules; ex Pokémon (2 pts); **Fossils** (40 HP Basic-like Colorless, no retreat, no setup placement) |
| P-A | Promo-A | Oct 30, 2024 | Promo card pool (not researched beyond existence) |
| A1a | Mythical Island | Dec 17, 2024 | None found — cards-only expansion |
| A2 | Space-Time Smackdown | Jan 29/30, 2025 | **Pokémon Tool cards** AND **Burned + Confused Special Conditions** (both introduced together per Bulbapedia quote — see §2/§3; implies Poison/Sleep/Paralysis existed since A1 launch, not directly confirmed) |
| A2a | Triumphant Light | Feb 28, 2025 | **Link Abilities** — Abilities that activate only if Arceus/Arceus ex is also in play |
| A2b | Shining Revelry | Mar 26/27, 2025 | None found — Shiny-card/Gen IX debut, cards-only |
| A3 | Celestial Guardians | Apr 30, 2025 | None — confirmed cards-only (half-year-anniversary missions, no new mechanic) |
| A3a | Extradimensional Crisis | May 29, 2025 | **Ultra Beasts** — confirmed to be a **flavor/thematic category only, no functional rule or subtype tag** (Bulbapedia explicitly: standard type/rarity, "no special 'Ultra Beast' tag or mechanical distinction") |
| A3b | Eevee Grove | Jun 26, 2025 | None found — cards-only |
| A4 | Wisdom of Sea and Sky | Jul 30, 2025 | **Baby Pokémon** — Basic Pokémon, 30 HP, no Weakness, no Retreat Cost, energy-free attacks |
| A4a | Secluded Springs | Aug 26/28, 2025 | None found — cards-only |
| A4b | Deluxe Pack: ex | Sep 25/30, 2025 | **Parallel foil cards** (cosmetic rarity/print variant, not a gameplay rule); set is mostly reprints |
| B1 | Mega Rising | Oct 30/31, 2025 | **Mega Evolution ex** — 3 pts on KO (vs. 2 for normal ex); evolves from expected prior stage or is Basic-stage; turn-ending question UNRESOLVED (see §2) |
| B1a | Crimson Blaze | Dec 10/17, 2025 | None new — "continues" Mega Evolution ex (X/Y themed), no new mechanic |
| B2 | Fantastical Parade | Jan 29, 2026 | **Stadium cards** — one in play, symmetric effect, same-name replacement blocked, own-turn one-play limit |
| B2a | Paldean Wonders | Feb 18/26, 2026 | None new mechanically — notable only for reusing physical-TCG artwork for the first time (Regulation Mark G cards) |
| B2b | Mega Shine | Mar 17/26, 2026 | **Shiny Mega Evolution Pokémon ex** — new card variant, uses existing Mega ex rules, not a new mechanic |
| B3 | Pulsing Aura | Apr 22/28, 2026 | None battle-rule-relevant; **meta-game change**: Emblem tickets & Dex Missions removed game-wide, replaced by collection-count-based set emblems |
| B3a | Paradox Drive | May 20/28, 2026 | **Past / Future sub-categories** (Ancient/Future labels analogous to physical TCG's Paradox mechanic) — enable targeted Trainer-card synergies, not a standalone rule |
| B3b | Everyday Wonders | Jun 22/30, 2026 | None found — cards-only (106 cards, existing types) |
| B4 | Ruler of the Skies | Jul 30, 2026 | None new — more Mega ex + Dragon-type cards; **however the concurrent app update v1.7.0 (same date) carries real rule changes — see §3, not tied to card content itself** |
| B4a | Team Rocket's Ambition | Aug 26/27, 2026 | **"Owner's Pokémon"** — "Team Rocket's [Name]" card line; evolution restricted to same-owner pre-evolution only (single-sourced, NOT cross-confirmed — see §2) |
| P-B | Promo-B | "Coming soon" per one source as of research date | Not researched |

Sources for dates: [Pokémon Zone Sets list](https://www.pokemon-zone.com/sets/) (COMMUNITY), [ptcgpocket.gg/expansions](https://ptcgpocket.gg/expansions/) (COMMUNITY, some dates differ by a few days from Pokémon Zone — flagged above as X/Y), [Bulbapedia TCG Pocket page](https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_Trading_Card_Game_Pocket) (COMMUNITY/wiki, cites official sources for some).

---

## (2) Mechanic rules detail

### Fossils (Item cards played as Pokémon) — introduced A1 Genetic Apex (Oct 30, 2024)
Grade: COMMUNITY (Bulbapedia, corroborated by Game8 card pages e.g. Helix Fossil listed under Genetic Apex)
Source: https://bulbapedia.bulbagarden.net/wiki/Item_card_(TCG_Pocket)

- "They can be put into play as if they were Basic Pokémon with 40 HP" — Fossils = 40 HP Basic-like Pokémon (Colorless).
- Can be evolved into certain Pokémon cards (i.e., some Fossils have an evolution line, e.g. Old Amber → Aerodactyl).
- Fossil cards CAN have Energy attached to them.
- **Cannot retreat** while in the Active Spot.
- **Can be discarded at any point during the game without forfeiting a prize point** — i.e., discarding your own Fossil is free, no point penalty either way (consistent with official ruling that only KOs, not discards, award points — see A_official.md Q20 finding).
- **Cannot be placed in the Active Spot or Bench during initial setup** — "they do not count as Pokémon cards while in a player's hand" for setup purposes. This answers QUESTIONS.md Q40 in part: Fossils are NOT eligible for the guaranteed-Basic opening hand / setup placement despite counting as Basic Pokémon once in play.
- Needs verification: does a Fossil count as a "Basic Pokémon" for Poké Ball-style search effects? Not stated on this page — flag as OPEN.

### Pokémon Tool cards — introduced A2 Space-Time Smackdown (Jan 29/30, 2025)
Grade: COMMUNITY (Bulbapedia)
Source: https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_Tool_card_(TCG_Pocket)

- "Pokémon Tool cards are played by attaching them to a Benched or Active Pokémon."
- One-per-Pokémon limit: cannot attach a Tool "to a Pokémon that already has a Pokémon Tool card attached to it" (answers Q38: one Tool per Pokémon, confirmed).
- No limit on how many different Tool cards a player may play from hand in one turn ("as many... as they wish during their turn") — Tools are unlimited-per-turn like other Items, only Supporters are capped at one/turn.
- Removal: "it may only be removed by the effect of a card, such as another Trainer card or a Pokémon's attack or Ability" — i.e., no player-chosen voluntary detachment; only card effects move/remove Tools.
- On leaving play: Tools on a Pokémon that leaves play (e.g. Knocked Out) are discarded along with it ("typically discarded, as are those attached to a Knocked Out Pokémon").
- 26 Pokémon Tool cards existed as of this Bulbapedia snapshot (post-B-series, so cumulative count, not A2-only).

### Ultra Beasts — introduced A3a Extradimensional Crisis (May 29, 2025)
Grade: COMMUNITY (Bulbapedia set page, fetched directly — resolves the earlier open question)
- Ultra Beasts (Buzzwole, Pheromosa, Kartana, Xurkitree, Nihilego, Guzzlord, Poipole, Naganadel, Stakataka, Celesteela, etc.) were added as playable Pokémon in this set.
- **RESOLVED: Ultra Beast is a flavor/thematic category only — NOT a functional rule or subtype.** Bulbapedia confirms these cards "have standard type designations (Grass, Fire, Darkness, etc.) and rarity markers, with no special 'Ultra Beast' tag or mechanical distinction." No shared keyword, no deckbuilding restriction, no special rules text box tied to "Ultra Beast" as a category — they are ordinary Pokémon/Pokémon ex cards with Ultra Beast names/art.
- pokemon.com's own announcement pages remained inaccessible to WebFetch all session (Incapsula bot-protection on the whole domain) — noting the persistent domain failure once here rather than per-attempt.

### Burned and Confused Special Conditions — introduced A2 Space-Time Smackdown (Jan 29/30, 2025), together with Pokémon Tool cards
Grade: COMMUNITY (Bulbapedia set page, direct quote)
- Exact quote: "It also sees the introduction of Pokémon Tool cards to the game, as well as the **Burned and Confused Special Conditions**."
- This means Burn and Confusion did **not** exist at game launch (A1 Genetic Apex) — they were added ~3 months later. By implication, **Poison, Asleep, and Paralyzed were the only Special Conditions present at launch** (not directly confirmed by an explicit "these 3 existed at launch" source, but follows from A2 being the stated introduction point for the other two — flag the Poison/Sleep/Paralysis-at-launch claim as an INFERENCE, not a direct quote).
- **This directly matters for the simulator's rules-history scope**: any pre-A2 game state (Oct 30 2024 – Jan 29/30 2025) should not model Burn or Confusion at all; the "Sleep and Paralysis not working in engine" issue referenced in this project's own instructions is unrelated to this — this is about the real game not having the conditions yet, not an engine bug.
- Exact numeric values/timing for Burn (20/Checkup + coin flip) and Confused (flip on attack, tails=fail) are covered in Bulbapedia's "Differences from the TCG" paragraph already captured in §4 (Confused: no self-damage on tails in Pocket, unlike physical TCG) — no separate rules-text quote for the exact introduction wording (e.g. damage amounts) was captured from the A2 set page itself. OPEN for exact original wording if needed beyond current card-text research (this document's job is history, not current card text — QUESTIONS.md's own note says card text is available locally).

### Link Abilities — introduced A2a Triumphant Light (Feb 28, 2025)
Grade: COMMUNITY (Bulbapedia set page, direct quote)
- Exact quote: "Some of the Pokémon in the expansion feature special Abilities called Link Abilities, which are activated if the player has Arceus or Arceus ex in play."
- Functional mechanic: a Link Ability is a normal Ability with an added activation condition — requires Arceus or Arceus ex to also be in play (does not specify Active vs. Bench; likely "in play" means anywhere on the player's side, consistent with how most Abilities work, but not explicitly confirmed either way).
- Not a new rules-engine category so much as a new conditional-activation pattern for the existing Ability framework.

### Baby Pokémon — introduced A4 Wisdom of Sea and Sky (Jul 30, 2025)
Grade: COMMUNITY (Bulbapedia set page, direct quote)
- Exact quote: "The expansion introduces Baby Pokémon to the game, which were introduced to the core series in Generation II; these are depicted as Basic Pokémon with 30 HP, no Weaknesses or Retreat Costs, and attacks that require no Energy to use."
- Rules profile: Baby Pokémon are Basic Pokémon (count for the guaranteed-Basic opening hand / setup, unlike Fossils) with fixed 30 HP, **no Weakness** (so Weakness-based damage bonuses never apply to them), **0 Retreat Cost** (always retreat "free"), and their attacks cost **0 Energy**. This is a distinct statline template introduced this set, relevant to Q16/Q17 (Weakness interactions) and Q31 (retreat cost).

### Stadium cards — introduced B2 Fantastical Parade (Jan 29, 2026)
Grade: COMMUNITY (Bulbapedia, corroborated by PokeBeach headline "Introduces Stadium Cards to the Game")
Source: https://bulbapedia.bulbagarden.net/wiki/Stadium_card_(TCG_Pocket) ; https://www.pokebeach.com/2026/01/fantastical-parade-announced-for-pocket-introduces-stadium-cards-to-the-game

- "Only one Stadium card may be in play at any given time, and its effects apply to both players during a game." — confirms Q39: Stadiums are symmetric/global effects.
- "When a Stadium card is played, it is placed next to the Active Spot and stays in play, unless removed by the play of a new Stadium card or the effect of certain non-Stadium cards."
- "A player may play only one Stadium card during their turn" — one Stadium play per turn (like Supporters, but as its own category — need to verify if this is IN ADDITION to a Supporter play, i.e. are Stadiums their own Trainer subtype separate from the Supporter-per-turn limit? Bulbapedia lists Stadium as one of "four primary Trainer card subtypes" alongside Item/Supporter/Tool, implying its own once-per-turn allowance distinct from Supporters. OPEN — confirm explicitly.)
- Same-name rule: "if a Stadium card is already in play, any Stadium cards with the same name cannot be played" — answers Q39: you CANNOT replace a Stadium with another copy of the identical-name Stadium while one is in play (differs from some physical-TCG Stadium rulings historically — physical TCG's stadium same-name rule has varied by era; flag as a difference to verify in §4).
- A different-named Stadium CAN replace one in play (implied by "removed by the play of a new Stadium card").
- 13 Stadium cards exist across B2 through B4a as of this snapshot.

### Mega Evolution ex — introduced B1 Mega Rising (Oct 30, 2025)
Grade: COMMUNITY (Bulbapedia "Pokémon ex (TCG Pocket)" page, Bulbapedia "Mega Rising (TCG Pocket)" page, Game8 Mega Evolution list page — 3 independent corroborating sources)

- Confirmed by 3 sources: Mega Evolution ex Pokémon award **3 points when Knocked Out** (vs. 2 for normal ex). Quote: "they also feature the Mega Evolution ex rule, causing them to grant three points when they are Knocked Out, rather than the typical two for Pokémon ex" (Bulbapedia).
- Mega Evolution ex evolve from the expected prior stage (e.g. Mega Blaziken ex evolves from Combusken, is a Stage 2 Pokémon overall); some are Basic-stage Megas playable immediately (e.g. Mega Absol, Mega Pinsir per Game8 — these seem to be Megas with no pre-evolution modeled, functioning as Basics).
- Mega Rising "only features previous [movie-era] Mega Evolutions, not the new ones from Legends: Z-A" (PokeBeach).
- **NOT VERIFIED / OPEN despite dedicated search**: whether Mega Evolving a Pokémon ends the player's turn (as Mega Evolution did in the physical XY-era TCG) or whether the Pokémon can attack the same turn it Mega Evolves. No official or community source found explicitly states this either way. The official Pokémon TCG Pocket Battle Rules FAQ (support.pokemon.com, fetched directly) does NOT mention Mega Evolution at all as of this research. **This is a real gap — flag for the simulator team to test in-app directly rather than assume the physical-TCG rule applies.**
- pokemon.com official announcement pages for Mega Rising were NOT accessible — WebFetch blocked by Incapsula bot-protection on the entire pokemon.com domain (multiple pages tried: news article, strategy article, expansion overview). Per instructions, not working around this with curl/archives — noting as a persistent domain-level access failure.

### Past / Future sub-categories (Paradox Pokémon) — introduced B3a Paradox Drive (May 2026)
Grade: COMMUNITY (retrogems.fr FAQ article, PokeBeach reveal article)

- "Past and Future are 2 brand-new sub-categories introduced with Paradox Drive... Players can build decks built entirely around one of the 2 categories to trigger exclusive synergy bonuses" (retrogems.fr).
- PokeBeach: cards get "'Ancient' and 'Future' mechanic labels like the physical TCG, allowing those Pokemon to be supported by certain Trainer cards like Professor Sada and Turo" — i.e., this is explicitly modeled on the physical TCG's Ancient/Future mechanic (Paradox Rift era) — Past/Future are **card-targeting labels that specific Trainer cards can reference**, not a standalone rules-engine change (no new universal rule; functions like a type/subtype tag that a few Supporter cards key off of). Analogous to how "Pokémon ex" or "Stage" are tags certain cards reference.
- Ancient examples: Slither Wing, Scream Tail. Future examples: Iron Thorns, Iron Bundle.
- No exact rule text box quote obtained; mechanic is card-specific (a Supporter says something like "if you have X Past/Future Pokémon..."), not a global rule change. Confidence: MEDIUM (two corroborating community sources, no official rule text quote).

### "Owner's Pokémon" — introduced B4a Team Rocket's Ambition (Aug 26/27, 2026)
Grade: COMMUNITY (Bulbapedia set page confirms name/date; anketsu.com guide is the only source found with functional detail — SINGLE-SOURCED for the mechanical detail, flag accordingly)

- Bulbapedia: "It focuses on Team Rocket and introduces **Owner's Pokémon** to the game, with Team Rocket's Pokémon making their debut."
- Cards are named "Team Rocket's [Pokémon Name]" (e.g. Team Rocket's Meowth, Team Rocket's Persian, Team Rocket's Articuno ex, Team Rocket's Moltres ex, Team Rocket's Slowking ex, Team Rocket's Lapras).
- **Key rule (anketsu.com, single-sourced, NOT yet cross-checked against a second source):** "An evolution from this expansion can only evolve from another Team Rocket's Pokémon." Example given: "Team Rocket's Persian can only evolve from Team Rocket's Meowth. You cannot evolve it from a regular Meowth from one of the older expansions." — **This is a genuinely new evolution-restriction rule the simulator must encode if confirmed**: it narrows Q28's "evolution restrictions" list with an expansion-specific, name-line-specific same-owner requirement not previously documented. **HIGH PRIORITY to verify with a second/official source before trusting for simulator logic** — only one community guide found this; no PokeBeach/Serebii/official confirmation obtained (WebSearch budget was exhausted for this session before a second source could be found).
- At least two new Supporter cards ("Team Rocket's Master Plan", "Team Rocket's Researcher" per a PokeBeach forum commenter, unconfirmed exact names/text) appear to search the deck for Team Rocket's Pokémon specifically — consistent with treating "Owner's Pokémon" as a real deck-building card-pool category, not just flavor.
- OPEN: whether "Owner's Pokémon" extends beyond Team Rocket (i.e., is this a generalized "Owner" tag mechanic that could apply to other trainer-characters' Pokémon in future sets) or is Team-Rocket-specific naming. Not resolved.

### Sets confirmed to add NO new mechanic (cards-only expansions)
Grade: COMMUNITY, single-source-checked per set (Insider Gaming for A3; general absence of any "new mechanic" coverage for others found via search snippets — weaker confidence, marked accordingly)

- **A3 Celestial Guardians** (Apr 30, 2025): confirmed no new mechanic — "isn't the only new addition... new missions and solo battles" only; no new card subtype (Insider Gaming, fetched directly).
- **A4b Deluxe Pack: ex** (Sep 2025): name strongly implies a reprint/premium pack of existing ex cards rather than a new mechanic — NOT directly confirmed by a fetched source, flag as MEDIUM-confidence inference only.
- A1a, A2a, A2b, A3b, A4, A4a, B1a, B2a, B2b, B3, B3b, B4: **NOT YET individually verified** for "new mechanic vs. cards-only" in this research pass — WebSearch budget was exhausted (200/200 used this session) before these could be checked. Treat as OPEN/TODO, not as "confirmed no new mechanic." A few remaining known Bulbapedia set-page URLs are queued for follow-up via WebFetch only (no further WebSearch available this session).

---

## (3) Chronological rule changes / errata / behavior fixes

Grade for this whole section: COMMUNITY (Bulbapedia "Version history" table on the main TCG Pocket wiki page, cross-checked partially with other sources as noted). Bulbapedia's version-history table itself cites app-store/patch-note changelogs; treat as OFFICIAL-QUOTED where the changelog text is quoted verbatim from patch notes, COMMUNITY for Bulbapedia's own framing.
Source: https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_Trading_Card_Game_Pocket (section "Version history")

Full version history (dates iOS/Android as given; "N/A" changelog = not recorded):

| Version | Date | Changelog (as recorded) |
|---|---|---|
| 1.0.0 | Aug 18, 2024 | (initial) |
| 1.0.2 | iOS Aug 26 / Android Sep 26, 2024 | iOS bug fixes; Android soft launch |
| 1.0.3 | Oct 15/16, 2024 | Bug fixes |
| 1.0.5 | Oct 23/24, 2024 | Bug fixes — **"Global launch"** (note: this is the date Bulbapedia's table itself labels global launch; commonly-cited "Oct 30, 2024" launch date from other sources may refer to a slightly different regional/marketing rollout point — DISCREPANCY, not resolved, flag both dates) |
| 1.0.6 | Nov 3, 2024 | "fixed an issue where the app would not start for some using iOS devices and other minor problems" |
| 1.0.7 | Nov 11, 2024 | Fixed bug allowing more free booster packs than the daily limit |
| 1.0.8 | Nov 25, 2024 | "help address screen flashing issues for some people" |
| 1.0.9 | Dec 2, 2024 | Fixed bug relating to certain device models |
| **1.1.0** | **Jan 29, 2025** | New Space-Time Smackdown expansion; trade feature unlocked; **Pokémon Tools subtype added**; deck auto-build logic adjustments; Italian text correction; Wonder Pick sharing adjustments |
| 1.1.1 | Feb 7, 2025 | Bug fixes |
| 1.1.2 | Feb 16, 2025 | Fixed French Energy-discard icon display in Palkia ex's card text |
| **1.2.0** | **Mar 26, 2025** | New Shining Revelry packs; **Ranked Match feature added** (first appearance of Ranked mode); new tradable cards |
| 1.2.5 | May 27, 2025 | Bug fixes |
| 1.3.0 | Jul 29, 2025 | New Ho-Oh/Lugia (Wisdom of Sea and Sky, A4) packs; tradable cards added; trade feature revisions |
| 1.3.1 | Aug 25, 2025 | Bug fixes |
| 1.3.2 | Sep 29, 2025 | Bug fixes |
| 1.4.0 | Oct 29, 2025 | Mega Gyarados/Blaziken/Altaria (Mega Rising, B1) packs; new share feature; expanded trading |
| 1.4.1 | Nov 18, 2025 | Bug fixes |
| **1.5.0** | **Jan 29, 2026** | Fantastical Parade packs; **Stadium subtype added**; random solo battles [mode]; trade messaging |
| 1.5.1 | Mar 9, 2026 | Bug fixes |
| 1.6.0 | Apr 27, 2026 | Pulsing Aura packs; gold flair frames; "Claim All" feature; 2D-code friend requests |
| **1.7.0** | **Jul 29, 2026** | Ruler of the Skies packs; guaranteed-rarity packs; deck-sharing codes; **"rule changes for some cards"**; Step-Up Battles reworked (difficulty increases through stages); Ranked loss-penalty change: rank points lost on a loss changed to **0 for all ranks except Master Ball Rank** |
| 1.7.1 | Aug 6, 2026 | Same content as 1.7.0 (re-release/patch) |
| 1.7.2 | Sep 3, 2026 | Bug fixes |

**Notable rule-relevant entries, called out:**

0. **Special Conditions were added incrementally, not all present at launch.** Poison/Asleep/Paralyzed presumed present from A1 launch (Oct 30, 2024) — not directly quote-confirmed this session, flagged as inference. **Burned and Confused were added later, with A2 Space-Time Smackdown (Jan 29/30, 2025)** — direct Bulbapedia quote, see §2. Any simulator state reconstruction for the Oct 2024–Jan 2025 window should not include Burn/Confusion.
1. **Ranked Match mode did not exist at launch** — added in v1.2.0, **March 26, 2025**. Before this, all matches were presumably casual/unranked. (Answers part of Q49 — Ranked is a mid-life addition, not a launch feature.)
2. **v1.7.0 (Jul 29, 2026): Ranked loss penalty changed** — rank points deducted on a loss are now **0 for every rank except Master Ball Rank** (Master Ball rank presumably still loses points on a loss; other ranks below it no longer do). Source: Bulbagarden forum thread summarizing the patch (COMMUNITY, secondary summary of official patch notes) — https://bulbagarden.net/threads/latest-pokemon-tcg-pocket-update-brings-a-variety-of-feature-improvements-requires-3-5gb-download.311193/
3. **v1.7.0 (Jul 29, 2026): "The rule text for some cards will be updated"** — this appears to be the game's first acknowledged instance of card-text/rule changes to EXISTING cards (as opposed to new-set card design). Could NOT determine which specific cards or what the changes were despite multiple targeted searches (official pokemon.com patch-note pages blocked by Incapsula for WebFetch; a "Pokémon Forums" page found via search titled "Version 1.7.0 Patch Notes" turned out to be for **Pokémon TCG LIVE (the physical-game digital client), not TCG Pocket** — a false match, discarded). **OPEN — unresolved, needs a source with the specific card list.**
4. **Historical context (secondary source, cardsrealm.com, COMMUNITY):** prior to whatever changed in v1.7.0, the stated dev philosophy was explicitly NOT to nerf/buff existing cards: "the dev team behind the game decided to tackle the meta without nerfing or buffing any cards," instead adding new cards/reprints to shift the meta (cited re: early Mewtwo ex dominance). If accurate, v1.7.0's "rule changes for some cards" would be a philosophy reversal / first-ever balance-relevant card change — makes it especially important to pin down, but not resolved in this research pass.
5. **Step-Up Battles reworked, v1.7.0 (Jul 29, 2026)**: solo/PvE battle mode changed to a difficulty-increasing multi-stage format (COMMUNITY, Bulbagarden forum summary). Not a versus-mode rule change but a battle-mode change per the task's scope (Q49-adjacent).
6. **Random solo battles**, added v1.5.0 (Jan 29, 2026) alongside Stadium introduction — a new solo battle mode; not yet researched in detail. OPEN.
7. Trade system evolved over time: trade feature unlocked v1.1.0 (Jan 2025) using "trade tokens," later revised in v1.3.0 (Jul 2025); a separate community source (Wikipedia summary) says trade currency was later replaced by "shinedust" — exact version/date not yet pinned down. OPEN. (Meta-game, not a battle rule.)
8. **B3 Pulsing Aura (Apr 28, 2026): Emblem tickets and Dex Missions removed game-wide**, replaced by set emblems awarded for collecting a set number of cards from that set (Bulbapedia, direct paraphrase/quote: "Emblem tickets...were discontinued and removed for all previous sets; Dex Missions...were also removed from the game"). Meta-game/economy change, not a battle rule, but a genuine game-wide system change with a clear date.
9. **A2 Space-Time Smackdown (Jan 29/30, 2025): Burned and Confused Special Conditions added**, alongside Pokémon Tool cards — see §2 for full detail and the implication that these two conditions did not exist for the game's first ~3 months.

---

## (4) Physical-TCG vs Pocket differences

Grade: COMMUNITY (Bulbapedia "Differences from the Pokémon Trading Card Game" section, fetched verbatim below), corroborated in part by the official Pokémon Support Gameplay FAQ's blanket statement that Pocket's rules differ from the physical TCG (OFFICIAL-QUOTED: "The rules of Pokémon TCG Pocket are different from the Pokémon Trading Card Game" — support.pokemon.com Gameplay FAQ).

Full verbatim Bulbapedia paragraph (source: https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_Trading_Card_Game_Pocket, "Differences from the Pokémon Trading Card Game" section):

> "Decks are made of 20 cards. No more than two cards with the same name can be included in a deck. Energy cards are replaced by an Energy Zone, which generates one Energy each turn to attach to a Pokémon. At the start of a battle, each player draws five cards. The player that goes first cannot manually attach Energy, but can use Supporter cards, including those that attach Energy. The player who goes first may use an attack, but only if they are able to attach enough Energy to the attacking Pokémon. Each players' starting hand will always contain at least one Basic Pokémon, meaning mulligans will never be taken. Each player may only have up to 10 cards in their hand, whereas the physical game has no limit. Prize cards are replaced by points; players win battles by obtaining three points. Players unable to draw a card at the start of their turn do not lose the battle, as they would in the physical game. Unlike in the physical game—which has no turn limits—versus battles have a maximum of 30 turns, and solo battles have a maximum of 50 turns. In addition to their Active Pokémon, each player can have up to three Benched Pokémon, instead of five in the physical game. Pokémon cards have no Resistance and have a Weakness modifier of +20 instead of ×2. Effects of cards are generally simpler. No Pokémon, except Pokémon ex, has two attacks, though some Pokémon have an Ability and one attack. Effects of cards can affect a random Pokémon in play that is decided by the CPU. Confused Pokémon do not take damage when flipping tails for the Special Condition."

Breaking out individual claims with QUESTIONS.md cross-references:

1. **Deck size 20, max 2 copies per name** — matches Q1. No mention of an energy-type-declaration restriction here — still OPEN for Q1's second half.
2. **Energy Zone generates 1 Energy/turn** (not per-player-choice; the "next energy" mechanic isn't detailed here) — relevant to Q6, but doesn't resolve visibility/randomness-per-type detail. Still need dedicated Energy Zone source.
3. **Opening hand = 5 cards, always ≥1 Basic, no mulligans** — directly answers Q2 core question (mulligans never occur because the guarantee is structural, not a redraw rule) — but exact mechanism (Basic forced into the 5, vs. redraw-until-Basic) still not spelled out by this source. Partially resolves Q2.
4. **Player going first: cannot manually attach Energy on turn 1** — confirms half of Q5. **CAN still play Supporter cards on turn 1, including ones that attach Energy** — directly contradicts a naive assumption that Supporters might be restricted turn 1; Supporters are allowed turn 1 for the first player. **CAN attack on turn 1** if Energy is attached by some other means (i.e., via a Supporter) — so the turn-1 no-attack restriction on P1 is really just a case of "no Energy source available," not a hard rule against attacking. This meaningfully refines Q5.
5. **Hand limit = 10** — directly answers part of Q8. Mechanism for what happens on an over-limit draw is NOT stated here — still OPEN.
6. **No loss for failing to draw from an empty deck** — directly answers Q8's "empty deck: no draw, no loss" and matches Q15's deck-out framing (deck-out is not a loss condition in Pocket, unlike physical TCG where an empty-deck draw = loss).
7. **Turn cap: 30 turns (versus battles), 50 turns (solo battles)** — directly answers Q10's turn-cap question, not previously found in other sources checked. **What happens AT turn 30/50 (draw? sudden-death? whoever has more points wins?) is NOT stated here — still OPEN, high-value follow-up.**
8. **Bench size 3 (vs. 5 in physical)** — background confirmation, matches known Pocket rules (Q3 setup context).
9. **No Resistance; Weakness is flat +20 (not ×2)** — directly relevant to Q16 damage-calc-order question. Confirms the "+20" figure assumed in Q16's phrasing is correct and there is no Resistance layer to interact with.
10. **"No Pokémon, except Pokémon ex, has two attacks"** — general design-pattern note, not a hard rule enforced by the engine, but useful context.
11. **"Effects of cards can affect a random Pokémon in play that is decided by the CPU"** — relevant to Q1-adjacent randomness questions; some card effects use game-determined randomness rather than player choice, distinct from physical TCG norms.
12. **"Confused Pokémon do not take damage when flipping tails for the Special Condition"** — this is a DIRECT, explicit physical-vs-Pocket difference and directly answers Q22/Q23's Confusion mechanics: in the physical TCG, a Confused Pokémon that flips tails on attack deals no damage AND does 30 damage to itself; **in Pocket, the self-damage-on-tails-fail does NOT happen** — tails just means the attack fails, no self-inflicted damage. This is an important simulator-relevant difference and should be double-checked against another independent source given its importance (currently single-sourced to this Bulbapedia paragraph).

**Additional physical-vs-Pocket difference already noted in §2 above:** Stadium same-name rule — a Stadium card cannot be replaced by another copy of the identical name while one is in play (per Bulbapedia's Stadium card page). This differs from some physical-TCG Stadium ruling eras where a player could replace their own Stadium with an identical one to "refresh" an effect; Pocket explicitly blocks this. NOT yet cross-checked against a second source — flag as single-sourced.

---
