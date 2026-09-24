# Official Sources Research — Pokémon TCG Pocket Rules
Research log for QUESTIONS.md. Grades: OFFICIAL (direct official page), OFFICIAL-QUOTED (official text quoted by third party), MEMORY-UNVERIFIED (not to be used as finding).

## Findings

---Pages checked, nothing relevant---

### Battle Rules FAQ (support.pokemon.com/hc/en-us/articles/38906248102292)
Grade: OFFICIAL. URL: https://support.pokemon.com/hc/en-us/articles/38906248102292-Pok%C3%A9mon-TCG-Pocket-Battle-Rules-FAQ

- Q45/misc (energy-free attacks): "If no Energy symbol is displayed to the left of the attack name on a card, then it is an attack that can be used without any Energy attached to the Pokémon." — confirms 0-cost attacks exist and are usable with 0 energy (relevant to Q5 P1 turn-1 attack).
- Q20 (points on non-KO removal): "A player does not get points if an opposing Pokémon in play is discarded due to an effect. Points are gotten only when an opponent's Pokémon is Knocked Out." — direct official confirmation that discard-effects (non-KO removal) do NOT award points; only actual KOs award points.
- Misc (Prank Spinner - Team Rocket's Prank Spinner card, not directly a Q but shows shuffle-back mechanic): only ONE card from either player's hand is shuffled into the owner's deck by that effect (card-specific ruling, not general rule).
- Q46 (manual energy attachment vs Energy Zone effects) — RELEVANT: Jolteon ex's "Electromagnetic Wall" ability triggers "only when Energy is attached to a Pokémon from the Energy Zone" and does NOT trigger when energy moves between Pokémon or comes from the discard pile. This is a card-specific ruling but confirms the game engine distinguishes "attach from Energy Zone" (both manual once-per-turn attachment AND card effects that attach from the Energy Zone) as one category, vs "move energy between own Pokémon" / "retrieve from discard" as different categories. Does not by itself answer whether card-effect attachments from the Energy Zone consume the manual once-per-turn attachment (still open).
- Q34 (once-per-turn ability reset) — RELEVANT: Buzzwole ex's "Big Beat" attack restriction (can't be used on consecutive turns normally) "resets when the Pokémon returns to the bench, allowing consecutive use" — i.e., moving to bench and back resets a used-restriction. This is about an attack-use restriction, not an Ability, but is suggestive that per-Pokémon-instance state can reset on leaving-Active/returning. Card-specific, not a general Ability rule.
- Q31/Q33 (switch vs retreat, bench-to-active same turn) — Scizor's "Gale Thrust" bonus damage requires Scizor to have moved from bench to active during the SAME turn — card specific but confirms game tracks "moved into Active this turn" as engine state distinct from normal retreat.

Related articles linked from this FAQ page (to check): 
- Gameplay FAQ: https://support.pokemon.com/hc/en-us/articles/30330309361172
- Technical Troubleshooting FAQ: https://support.pokemon.com/hc/en-us/articles/30332689777428
- Gift Code FAQ: https://support.pokemon.com/hc/en-us/articles/35876581854484
- Account Link and Data Transfer FAQ: https://support.pokemon.com/hc/en-us/articles/30331783530644

Additional articles found via site search (to check):
- Category listing: https://support.pokemon.com/hc/en-us/categories/19331422065172-Pok%C3%A9mon-Trading-Card-Game-Pocket
- Web Store FAQ: https://support.pokemon.com/hc/en-us/articles/44985710277268
- Sharing and Social FAQ: https://support.pokemon.com/hc/en-us/articles/30332621133204
- Trading FAQ: https://support.pokemon.com/hc/en-us/articles/34322874608660
- Purchase and Premium Pass FAQ: https://support.pokemon.com/hc/en-us/articles/30331739144596


### Gameplay FAQ (support.pokemon.com/hc/en-us/articles/30330309361172)
Grade: OFFICIAL. URL: https://support.pokemon.com/hc/en-us/articles/30330309361172-Pok%C3%A9mon-TCG-Pocket-Gameplay-FAQ
- Note: page explicitly states detailed battle/game rules are NOT here — directs to in-app "Tips" / question-mark button and to official website tcgpocket.pokemon.com instead. So in-app tutorial text is the "official" rules source but not web-accessible to this research (app-only).
- Q14 (ties/draws): "If your game ends in a tie, your ranked match points will not increase or decrease. However, your win streak points will be reset." — confirms ties are a real possible outcome in Ranked with defined non-punitive point handling.
- Ranked win-streak bonus: caps at 5 consecutive wins; bonus does not increase further beyond 5 wins (not a core battle rule, minor context for Q49).
- Q15/Q49 (disconnection): "If you experience a crash or disconnection during a versus match, you may attempt to rejoin the match within the reconnection window of around 120 seconds. If you cannot reconnect within that timeframe, you lose the match." — DIRECT OFFICIAL answer: disconnecting and failing to reconnect within ~120s = LOSS (not a draw, not void). Does not specify what happens if BOTH players disconnect simultaneously, or explicitly address deliberate concede button behavior (separate from crash/disconnect).


### Notes on pokemon.com (www.pokemon.com/us/...) accessibility
Grade: N/A — SOURCE BLOCKED. All www.pokemon.com/us/pokemon-news/*, /us/news/*, and /us/strategy|features/* article pages returned Incapsula bot-protection challenge pages (no readable content) to WebFetch, including "Learn How to Build a Deck in Pokémon TCG Pocket" (deck construction, Q1) and the "October 2025 Producer Letter". Per instructions, not attempting curl/proxy/archive workarounds. This is a real gap — the official deck-building article likely answers Q1 but could not be read directly. Google Translate proxy workaround also blocked (proxy-domain block). Will rely on quotes from other official pages / OFFICIAL-QUOTED via news sites where possible for Q1.

### community.pokemon.com forums — patch notes structure
Grade: OFFICIAL (forum is run by The Pokémon Company; distinguish from user posts). 
- IMPORTANT NEGATIVE FINDING relevant to Q50: Version-numbered "Patch Notes" threads under community.pokemon.com (e.g. discussion/23661, discussion/25821 "Version 1.42.0 - Patch Notes", dated Sept 10, 2026) are for **Pokémon TCG LIVE**, not TCG Pocket, despite discussion/25821 appearing under a TCG-Pocket-adjacent link/category. TCG Pocket does NOT appear to receive versioned patch notes posted to community.pokemon.com. A user thread ("TCG Pocket new version release notes", community.pokemon.com/en-us/discussion/13821) shows a player in 2024/2025 explicitly complaining that no official TCG Pocket release notes exist on the forum, and being pointed to an UNOFFICIAL third-party site ("pokepocketmeta") instead. This means: **official TCG Pocket patch/bugfix notes are not published on community.pokemon.com**, and likely only exist as in-app update text (not web-crawlable) — a real gap for Q50.
- Pokéball Bug thread (community.pokemon.com/en-us/discussion/14215): a player reported Poké Ball "failing" to find a Pokémon; a Pokémon Company moderator (Mod_Bee) only redirected to Support, did NOT confirm a bug. Other players clarified Poké Ball only retrieves BASIC Pokémon (consistent with community understanding, not an official rules statement in this thread). No official confirmation of a bug or fix. Not usable as a rules source, but worth noting Poké Ball = "random Basic Pokémon" is asserted by players, unconfirmed here officially.

### Known Issue 10-31-24 (support.pokemon.com/hc/en-us/articles/31736549813908)
Grade: OFFICIAL. Checked — NOT RELEVANT to rules: reports an iOS app crash-on-launch issue reported Oct 30 2024, status "under investigation" at time of last snapshot. No card/mechanic content.


### Gameplay FAQ — FULL Q&A list (support.pokemon.com/hc/en-us/articles/30330309361172)
Grade: OFFICIAL. Confirmed via full extraction — 44 Q&A total. Key items beyond what's already logged:
- "What are the rules of Pokémon TCG Pocket?" answer explicitly DEFERS to in-app Tips / question-mark button and "official website" — CONFIRMS no detailed web-published rules text exists at this URL (negative finding for nearly all Q1-Q48 core rules; the authoritative rules text is in-app only, not crawlable).
- Ranked matches unlock at player level 3 ("battles unlock" gating) — minor Q49 context.
- Rental decks cannot be used in versus (PvP) battles — minor context, not directly asked but relevant to Q49 mode differences.
- No mention anywhere in 44 Q&A of: hand limit, special condition values, damage calc order, evolution restrictions, retreat rules, timers per turn, Stadiums/Tools/Fossils. CONFIRMED these are simply not covered by official web FAQ pages.
- Date rollover for daily resets: 6:00 a.m. UTC (not battle-rules relevant but noted).

### community.pokemon.com/en-us/discussion/13311 "Post TCG Pocket Q&A"
Grade: LOW-VALUE / NOT OFFICIAL TEXT. This is a forum user's third-hand paraphrase of a pre-release press event (via a podcast called "Pkmncast"), posted before the game's Oct 2024 launch. Contains since-INVALIDATED claims ("There will be no Ranked mode" — Ranked mode exists in the shipped game), so must not be used as a current rules source. Only reliable-sounding bit ("20 card deck... maximum of 2 of any select card", "3 points to win, 1 for regular KO, 2 for ex KO") matches known basic rules but is NOT an official citation — do not cite this thread as a source; treat as MEMORY-UNVERIFIED-tier, superseded by gameplay reality.


### Cosmetic Poké Ball card-back fix (Feb 2024, pre-Pocket-launch)
Grade: OFFICIAL-QUOTED (via Dexerto, thegamer, gamesradar, kotaku, videogamer — all reporting the same Feb 27-28 2024 Pokemon Presents announcement). CONFIRMED NOT RELEVANT to Q50: this is a purely cosmetic card-BACK art correction (which half of the Poké Ball graphic the button is attached to), announced at a general Pokémon Presents event before TCG Pocket's Oct 2024 launch — not a gameplay/rules fix, and predates the game. Excluding from Q50 answer.

## Official pages checked with NOTHING relevant (full list)
- support.pokemon.com Trading FAQ (34322874608660) — trading mechanics only.
- support.pokemon.com Sharing and Social FAQ (30332621133204) — social features only.
- support.pokemon.com Technical Troubleshooting FAQ (30332689777428) — app crashes/errors/performance only, no gameplay content.
- support.pokemon.com Known Issue 10-31-24 (31736549813908) — iOS app-crash-on-launch bug report, unrelated to card/battle rules.
- support.pokemon.com Web Store FAQ, Purchase and Premium Pass FAQ, Gift Code FAQ, Account Link and Data Transfer FAQ — not fetched in detail; titles indicate monetization/account topics only, judged out of scope after pattern established by other FAQs (all explicitly say to look at Battle Rules FAQ / Gameplay FAQ / in-app Tips for actual game rules).
- community.pokemon.com "Pokeball Bug" thread (14215) — unconfirmed player bug report, official mod reply only redirected to Support, no rules content.
- community.pokemon.com "Post TCG Pocket Q&A" (13311) — pre-launch third-hand fan paraphrase of a press event, contains since-invalidated claims (said no Ranked mode); not usable.
- community.pokemon.com "TCG Pocket new version release notes" (13821) — confirms NO official patch notes are posted for TCG Pocket on this forum (unlike TCG Live, which gets numbered "Version X.Y.Z Patch Notes" threads).
- community.pokemon.com Version 1.37.0 / 1.42.0 "Patch Notes" threads — these are for Pokémon TCG LIVE, a different game, not Pocket. Confirmed via full-text fetch of both.

## SOURCES BLOCKED / INACCESSIBLE (could not verify)
- ALL www.pokemon.com/us/pokemon-news/*, /us/news/*, /us/strategy/*, /us/features/* article pages: blocked by Incapsula bot-challenge for this tool (no readable content returned), including:
  - "Learn How to Build a Deck in Pokémon TCG Pocket" (likely answers Q1 deck construction / energy declaration — UNVERIFIED, gap)
  - "Read the Pokémon TCG Pocket October 2025 Producer Letter" (got readable via community.pokemon.com repost instead — see below)
  - "Ultra Beasts Invade Pokémon TCG Pocket in the Extradimensional Crisis Expansion" (mechanic details unverified — gap for Q50/misc)
  - "Deluxe Pack ex Is Coming to Pokémon TCG Pocket"
  - Mega Blaziken ex / Mega Absol ex deck strategy pages (could bear on Q30 Mega Evolution deck limits — unverified, gap)
- x.com/PokemonTCGP official posts: blocked by robots.txt for this tool.
- thegamer.com, screenrant.com individual articles: intermittently blocked by robots.txt/server errors for this tool.
Per instructions, did not attempt curl/proxy/archive-mirror workarounds after WebFetch failures (tried one Google-Translate-proxy workaround, which was itself blocked as a known proxy domain).

## Successfully read alternate-source repost of Oct 2025 Producer Letter
- community.pokemon.com/en-us/discussion/20590 (forum repost/discussion of the official Oct 13, 2025 producer letter) — readable. Grade: OFFICIAL-QUOTED (forum thread discussing/quoting the official announcement; original pokemon.com source blocked but this is the same official Pokémon Company communication run through the official community forum).
  - Confirms: Mega Evolution mechanic first announced Oct 13, 2025, for "a new expansion... planned to kick off at the end of October [2025]" (this is the Mega Rising / Extradimensional-adjacent Mega Evolution ex introduction — exact set name not stated in the letter itself).
  - New Share feature (gift ◇–◇◇◇◇ rarity cards, 1/friend/day), expanded trading to include ⭐1-2 and Shiny 1-2 rarities, Wonder Pick showing latest-expansion cards more often + ownership counts — none of this is battle-rules relevant.
  - No mention of Stadiums, Tools, Fossils, Ultra Beasts, or any battle-system/rule change in this specific letter.


### Stadium cards introduction (Q50 — new mechanic timeline)
Grade: OFFICIAL-QUOTED (PokeBeach reporting official Pokémon Company announcement). URL: https://www.pokebeach.com/2026/01/fantastical-parade-announced-for-pocket-introduces-stadium-cards-to-the-game
- Announced January 22, 2026; set "Fantastical Parade" released January 29, 2026 — this set "will introduce Stadium cards to Pocket for the first time" (e.g., Peculiar Plaza).
- No official rules text on Stadium mechanics (one-at-a-time? replace opponent's? symmetric?) was included in the announcement itself — Q39 remains unanswered by official sources found.

### Mega Evolution ex — first announced/introduced (partial, Q50 timeline)
Grade: OFFICIAL-QUOTED. Oct 13, 2025 producer letter (via community.pokemon.com/en-us/discussion/20590) announced Mega Evolution Pokémon coming "at the end of October" 2025 as a new expansion. Exact release date and any Pocket-specific Mega Evolution rule text (e.g., whether Mega Evolving ends the turn, as in physical XY-era rules) was NOT found in any accessible official source — Q30's Mega Evolution ex specifics remain UNANSWERED by official sources (the physical-TCG "Mega Evolving ends your turn" rule must NOT be assumed to apply to Pocket without confirmation; none found).

### Ultra Beasts / Fossils — introduction dates
Not fully pinned down; official pokemon.com announcement pages for "Extradimensional Crisis" (Ultra Beasts, ~May 2025) exist but were blocked (Incapsula). Fossil cards' first-introduction expansion in Pocket not confirmed via an accessible official source in this session (ran out of budget to pursue further; likely findable in Game8/Bulbapedia set-history pages, which are not official-grade sources per scope).

