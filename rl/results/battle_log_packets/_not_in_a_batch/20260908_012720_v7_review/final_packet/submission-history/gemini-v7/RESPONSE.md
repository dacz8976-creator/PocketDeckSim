### SOURCE.json
```json
{
  "filename": "20260908_012720000_iOS.MP4",
  "source_path": "C:\\Users\\dacz8\\OneDrive\\Desktop\\Battle Logs\\20260908_012720000_iOS.MP4",
  "sha256": "B9E76626643D8950CB7A4277487DA2262B5FA96FAF9E87454495EBE896D47085",
  "bytes": 530226009,
  "duration_seconds": 282.628,
  "review_status": "partial",
  "reviewer_attribution": "Gemini 3.8 Flash API first-pass draft",
  "recording_type": "screen_recording",
  "relationships": [],
  "index_update_performed": false,
  "media_move_performed": false,
  "battle_identity": {
    "opponent_label": {
      "state": "observed",
      "value": "Opponent",
      "timestamp_seconds": 4.5,
      "observation": "VS splash screen displays Opponent with an AI badge above it."
    },
    "opening_player": {
      "state": "observed",
      "value": "Teal Mask Ogerpon ex",
      "timestamp_seconds": 13.0,
      "observation": "Player places Teal Mask Ogerpon ex into the Active Spot."
    },
    "opening_opponent": {
      "state": "observed",
      "value": "Happiny",
      "timestamp_seconds": 16.2,
      "observation": "Opponent reveals Happiny in the Active Spot."
    },
    "outcome": {
      "state": "observed",
      "value": "player_win",
      "timestamp_seconds": 276.5,
      "observation": "Player achieves 3 points and the Victory screen displays Whimsicott ex."
    },
    "result_text": {
      "state": "observed",
      "value": "Victory!",
      "timestamp_seconds": 276.6,
      "observation": "Victory! text is prominently displayed over Whimsicott ex."
    }
  },
  "evidence_audit": {
    "version": 1,
    "opponent_label": "Opponent",
    "match_mode": {
      "value": "solo",
      "evidence": [
        {
          "timestamp": "00:04.400",
          "observation": "AI badge shown directly above Opponent label."
        }
      ],
      "uncertainty_id": null
    },
    "opponent_ai": {
      "value": "yes",
      "evidence": [
        {
          "timestamp": "00:04.400",
          "observation": "AI badge displayed on VS splash screen."
        }
      ],
      "uncertainty_id": null
    },
    "auto": {
      "value": "off",
      "evidence": [
        {
          "timestamp": "00:08.800",
          "observation": "Auto toggle button is visible with checkmark/Auto state in play field."
        }
      ],
      "uncertainty_id": null
    },
    "terminal": {
      "outcome": "player_win",
      "outcome_evidence": [
        {
          "timestamp": "04:32.200",
          "observation": "Player reaches 3 points (+2 points animation triggers)."
        }
      ],
      "result_text": "Victory!",
      "result_text_evidence": [
        {
          "timestamp": "04:36.400",
          "observation": "Victory! banner appears over Whimsicott ex card."
        }
      ],
      "last_frame": {
        "timestamp": "04:42.400",
        "observation": "Final frame showing Victory! screen and Tap to Proceed prompt."
      },
      "uncertainty_id": null
    },
    "pokemon": [
      {
        "id": "player-ogerpon",
        "owner": "player",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:13.000",
          "observation": "Teal Mask Ogerpon ex placed into Active Spot."
        },
        "final": {},
        "final_evidence": {
          "timestamp": "03:19.400",
          "observation": "Teal Mask Ogerpon ex knocked out and sent to discard."
        },
        "uncertainty_id": null
      },
      {
        "id": "player-cottonee",
        "owner": "player",
        "initial": {},
        "initial_evidence": {
          "timestamp": "01:31.400",
          "observation": "Cottonee placed onto player's Bench."
        },
        "final": {
          "Grass": 3
        },
        "final_evidence": {
          "timestamp": "04:34.000",
          "observation": "Whimsicott ex (evolved from Cottonee) on Bench with 3 Grass Energy."
        },
        "uncertainty_id": null
      },
      {
        "id": "player-spinarak",
        "owner": "player",
        "initial": {},
        "initial_evidence": {
          "timestamp": "04:16.200",
          "observation": "Spinarak played to Bench via Quick-Grow Extract."
        },
        "final": {
          "Grass": 1
        },
        "final_evidence": {
          "timestamp": "04:34.000",
          "observation": "Spinarak active with 1 Grass Energy attached."
        },
        "uncertainty_id": null
      },
      {
        "id": "opp-happiny",
        "owner": "opponent",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:16.200",
          "observation": "Happiny revealed in Active Spot."
        },
        "final": {},
        "final_evidence": {
          "timestamp": "01:40.400",
          "observation": "Happiny knocked out and discarded."
        },
        "uncertainty_id": null
      },
      {
        "id": "opp-koffing",
        "owner": "opponent",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:16.800",
          "observation": "Team Rocket's Koffing placed on opponent's Bench."
        },
        "final": {},
        "final_evidence": {
          "timestamp": "04:29.400",
          "observation": "Team Rocket's Weezing ex (evolved from Koffing) knocked out and discarded."
        },
        "uncertainty_id": null
      },
      {
        "id": "opp-magmar",
        "owner": "opponent",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:31.800",
          "observation": "Team Rocket's Magmar played to opponent's Bench."
        },
        "final": {},
        "final_evidence": {
          "timestamp": "02:55.600",
          "observation": "Team Rocket's Magmar knocked out and discarded."
        },
        "uncertainty_id": null
      }
    ],
    "energy_events": [
      {
        "turn": 2,
        "pokemon_id": "player-ogerpon",
        "kind": "manual",
        "before": {},
        "after": {
          "Grass": 1
        },
        "before_evidence": {
          "timestamp": "00:41.200",
          "observation": "Teal Mask Ogerpon ex has 0 attached Energy."
        },
        "action_evidence": {
          "timestamp": "00:42.800",
          "observation": "Grass Energy dragged to Teal Mask Ogerpon ex."
        },
        "after_evidence": {
          "timestamp": "00:43.600",
          "observation": "Teal Mask Ogerpon ex displays 1 Grass Energy attached."
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 4,
        "pokemon_id": "player-ogerpon",
        "kind": "manual",
        "before": {
          "Grass": 1
        },
        "after": {
          "Grass": 2
        },
        "before_evidence": {
          "timestamp": "01:21.800",
          "observation": "Teal Mask Ogerpon ex has 1 Grass Energy attached."
        },
        "action_evidence": {
          "timestamp": "01:32.800",
          "observation": "Grass Energy dragged to Teal Mask Ogerpon ex."
        },
        "after_evidence": {
          "timestamp": "01:33.800",
          "observation": "Teal Mask Ogerpon ex displays 2 Grass Energy attached."
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 5,
        "pokemon_id": "opp-magmar",
        "kind": "manual",
        "before": {},
        "after": {
          "Fire": 1
        },
        "before_evidence": {
          "timestamp": "01:46.800",
          "observation": "Team Rocket's Magmar has 0 Energy attached."
        },
        "action_evidence": {
          "timestamp": "01:48.400",
          "observation": "Opponent attaches Darkness/Fire Energy to Magmar."
        },
        "after_evidence": {
          "timestamp": "01:49.000",
          "observation": "Team Rocket's Magmar displays 1 Energy attached."
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 6,
        "pokemon_id": "player-cottonee",
        "kind": "manual",
        "before": {},
        "after": {
          "Grass": 1
        },
        "before_evidence": {
          "timestamp": "02:04.800",
          "observation": "Cottonee on Bench has 0 attached Energy."
        },
        "action_evidence": {
          "timestamp": "02:12.800",
          "observation": "Grass Energy dragged to Whimsicott ex."
        },
        "after_evidence": {
          "timestamp": "02:13.800",
          "observation": "Whimsicott ex has 1 Grass Energy attached."
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 7,
        "pokemon_id": "opp-magmar",
        "kind": "manual",
        "before": {
          "Fire": 1
        },
        "after": {
          "Fire": 2
        },
        "before_evidence": {
          "timestamp": "02:22.000",
          "observation": "Team Rocket's Magmar has 1 Energy."
        },
        "action_evidence": {
          "timestamp": "02:22.800",
          "observation": "Opponent attaches a second Energy to Magmar."
        },
        "after_evidence": {
          "timestamp": "02:23.400",
          "observation": "Team Rocket's Magmar displays 2 Energy attached."
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 8,
        "pokemon_id": "player-cottonee",
        "kind": "manual",
        "before": {
          "Grass": 1
        },
        "after": {
          "Grass": 2
        },
        "before_evidence": {
          "timestamp": "02:38.600",
          "observation": "Whimsicott ex has 1 Grass Energy attached."
        },
        "action_evidence": {
          "timestamp": "02:42.800",
          "observation": "Grass Energy dragged to Whimsicott ex."
        },
        "after_evidence": {
          "timestamp": "02:43.400",
          "observation": "Whimsicott ex displays 2 Grass Energy attached."
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 8,
        "pokemon_id": "opp-magmar",
        "kind": "discard",
        "before": {
          "Fire": 2
        },
        "after": {},
        "before_evidence": {
          "timestamp": "02:51.600",
          "observation": "Team Rocket's Magmar has 2 Energy."
        },
        "action_evidence": {
          "timestamp": "02:52.000",
          "observation": "Magmar takes 100 damage and is knocked out."
        },
        "after_evidence": {
          "timestamp": "02:55.400",
          "observation": "Magmar is sent to discard pile."
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 9,
        "pokemon_id": "opp-koffing",
        "kind": "manual",
        "before": {},
        "after": {
          "Darkness": 1
        },
        "before_evidence": {
          "timestamp": "03:05.400",
          "observation": "Team Rocket's Weezing ex has 0 attached Energy."
        },
        "action_evidence": {
          "timestamp": "03:13.000",
          "observation": "Opponent attaches Darkness Energy to Weezing ex."
        },
        "after_evidence": {
          "timestamp": "03:13.600",
          "observation": "Team Rocket's Weezing ex displays 1 Darkness Energy attached."
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 9,
        "pokemon_id": "player-ogerpon",
        "kind": "discard",
        "before": {
          "Grass": 2
        },
        "after": {},
        "before_evidence": {
          "timestamp": "03:16.800",
          "observation": "Ogerpon ex has 2 Grass Energy attached."
        },
        "action_evidence": {
          "timestamp": "03:17.600",
          "observation": "Ogerpon ex HP drops to 0."
        },
        "after_evidence": {
          "timestamp": "03:19.400",
          "observation": "Ogerpon ex is sent to discard pile."
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 10,
        "pokemon_id": "player-cottonee",
        "kind": "manual",
        "before": {
          "Grass": 2
        },
        "after": {
          "Grass": 3
        },
        "before_evidence": {
          "timestamp": "03:30.000",
          "observation": "Whimsicott ex has 2 Grass Energy attached."
        },
        "action_evidence": {
          "timestamp": "03:47.800",
          "observation": "Grass Energy dragged to Whimsicott ex."
        },
        "after_evidence": {
          "timestamp": "03:48.400",
          "observation": "Whimsicott ex displays 3 Grass Energy attached."
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 12,
        "pokemon_id": "player-spinarak",
        "kind": "manual",
        "before": {},
        "after": {
          "Grass": 1
        },
        "before_evidence": {
          "timestamp": "04:16.200",
          "observation": "Spinarak played to Bench with 0 Energy."
        },
        "action_evidence": {
          "timestamp": "04:24.400",
          "observation": "Grass Energy attached to Spinarak."
        },
        "after_evidence": {
          "timestamp": "04:25.000",
          "observation": "Spinarak displays 1 Grass Energy attached."
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 12,
        "pokemon_id": "opp-koffing",
        "kind": "discard",
        "before": {
          "Darkness": 1
        },
        "after": {},
        "before_evidence": {
          "timestamp": "04:27.200",
          "observation": "Team Rocket's Weezing ex has 1 Darkness Energy."
        },
        "action_evidence": {
          "timestamp": "04:27.600",
          "observation": "Weezing ex HP reduced to 0 by Sting."
        },
        "after_evidence": {
          "timestamp": "04:29.400",
          "observation": "Weezing ex discarded upon knockout."
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      }
    ]
  }
}
```

### COVERAGE.md
```markdown
# Battle Coverage: 20260908_012720000_iOS.MP4

## Match Setup & Initial State
- **00:00.000 - 00:08.000**: Loading screen, coin toss, player assigned going second.
- **00:08.000 - 00:20.600**: Opening setup. Player places Teal Mask Ogerpon ex Active. Opponent reveals Happiny Active and benches Team Rocket's Koffing.

## Turns Breakdown

### Turn 1 (Opponent)
- **Timestamp range**: 00:20.600 - 00:37.200
- **Evidence anchors**:
  - 00:24.600: Opponent plays Pokémon Tool Poison Barb onto Happiny.
  - 00:28.400: Opponent plays Supporter Professor's Research (draws 2 cards).
  - 00:31.400: Opponent benches Team Rocket's Magmar.
  - 00:33.000: Happiny attacks with Chubby Cheer (10 damage to Ogerpon ex; next turn attacks do +20).
- **State delta**: Ogerpon ex HP 130 -> 120.

### Turn 2 (Player)
- **Timestamp range**: 00:37.200 - 00:49.600
- **Evidence anchors**:
  - 00:43.000: Player attaches Grass Energy to Teal Mask Ogerpon ex (1 Grass total).
  - 00:45.000: Player attaches Pokémon Tool Leaf Cape to Teal Mask Ogerpon ex (+30 max HP).
- **State delta**: Ogerpon ex max HP becomes 160 (current HP 150), 1 Grass Energy attached. Turn ends without attacking.

### Turn 3 (Opponent)
- **Timestamp range**: 00:49.600 - 01:21.000
- **Evidence anchors**:
  - 00:53.400: Opponent plays Poké Ball (adds card to hand).
  - 00:57.800: Opponent plays Supporter Copycat (shuffles and draws equal to player's hand).
  - 01:04.600: Opponent evolves benched Team Rocket's Koffing into Team Rocket's Weezing ex. Ability Boiler Smog triggers, but Ogerpon ex's Soothing Wind prevents Special Conditions (01:10.200).
  - 01:11.000: Opponent attaches Poison Barb to Team Rocket's Magmar.
  - 01:16.000: Happiny uses Chubby Cheer (10 + 20 = 30 damage to Ogerpon ex).
- **State delta**: Ogerpon ex HP 150 -> 120.

### Turn 4 (Player)
- **Timestamp range**: 01:21.000 - 01:47.000
- **Evidence anchors**:
  - 01:26.400: Player plays Poké Ball, retrieving Cottonee (01:28.600).
  - 01:31.400: Player benches Cottonee.
  - 01:33.000: Player attaches Grass Energy to Active Teal Mask Ogerpon ex (2 Grass total).
  - 01:34.400: Ogerpon ex uses Energized Leaves for 60 damage on Happiny.
  - 01:37.000: Happiny's HP drops to 0 (Knocked Out).
  - 01:37.800: Poison Barb triggers, but Ogerpon ex is protected by Soothing Wind (01:39.400).
  - 01:42.200: Player earns 1 point (Score: Player 1 - Opponent 0).
  - 01:45.400: Opponent promotes Team Rocket's Magmar to Active Spot.
- **State delta**: Happiny discarded. Score 1 - 0.

### Turn 5 (Opponent)
- **Timestamp range**: 01:47.000 - 02:03.600
- **Evidence anchors**:
  - 01:48.400: Opponent attaches Darkness/Fire Energy to Team Rocket's Magmar (1 Energy).
  - 01:50.800: Opponent plays Team Rocket's Master Plan (tries to Confuse Ogerpon ex, prevented by Soothing Wind at 01:52.400; opponent flips heads on self-confusion check at 01:56.600).
  - 01:59.800: Team Rocket's Magmar uses Derisive Roasting (10 base damage + weakness x2 against Grass = 30 damage, or boosted; takes 50 total damage due to Fire weakness +20).
- **State delta**: Ogerpon ex HP 120 -> 70.

### Turn 6 (Player)
- **Timestamp range**: 02:03.600 - 02:21.000
- **Evidence anchors**:
  - 02:06.000: Player plays Stadium Hiking Trail.
  - 02:10.000: Player evolves benched Cottonee into Whimsicott ex.
  - 02:13.000: Player attaches Grass Energy to benched Whimsicott ex (1 Grass).
  - 02:15.600: Teal Mask Ogerpon ex attacks with Energized Leaves (60 damage).
  - 02:18.000: Magmar takes 60 damage (HP 70 -> 10).
  - 02:19.200: Magmar's Poison Barb triggers; Ogerpon ex's Soothing Wind prevents Poison (02:20.800).
- **State delta**: Opponent Magmar HP 10/70.

### Turn 7 (Opponent)
- **Timestamp range**: 02:21.000 - 02:37.600
- **Evidence anchors**:
  - 02:23.000: Opponent attaches Fire Energy to Active Magmar (2 Energy total).
  - 02:25.600: Opponent plays Team Rocket's Master Plan; Soothing Wind blocks Confusion on Ogerpon ex (02:27.400); opponent coin flip lands heads (02:31.400).
  - 02:34.400: Magmar uses Derisive Roasting (10 + 20 weakness = 30 damage).
- **State delta**: Ogerpon ex HP 70 -> 40.

### Turn 8 (Player)
- **Timestamp range**: 02:37.600 - 03:03.800
- **Evidence anchors**:
  - 02:43.000: Player attaches Grass Energy to benched Whimsicott ex (2 Grass total).
  - 02:44.800: Player retreats Ogerpon ex and promotes Whimsicott ex to Active Spot.
  - 02:49.600: Whimsicott ex attacks with Grass Knot (40 + 30 per retreat cost energy = 100 damage).
  - 02:52.000: Magmar takes 100 damage and is Knocked Out.
  - 02:53.400: Poison Barb triggers on Whimsicott ex, but Whimsicott ex doesn't become Poisoned due to Soothing Wind (Ogerpon has Energy on Bench, or ability active, 02:54.800).
  - 02:57.600: Player awarded 1 point (Score: Player 2 - Opponent 0).
  - 03:02.400: Opponent promotes Team Rocket's Weezing ex to Active Spot.
- **State delta**: Magmar discarded. Score 2 - 0.

### Turn 9 (Opponent)
- **Timestamp range**: 03:03.800 - 03:28.800
- **Evidence anchors**:
  - 03:07.600: Opponent plays Supporter Cyrus (targets benched Ogerpon ex with 40 HP).
  - 03:11.200: Ogerpon ex is switched into the Active Spot.
  - 03:13.200: Opponent attaches Darkness Energy to Weezing ex (1 Energy total).
  - 03:15.000: Weezing ex uses Confusion Gas (60 damage).
  - 03:17.600: Ogerpon ex takes 60 damage; HP drops from 40 to 0 (Knocked Out).
  - 03:21.400: Opponent awarded 2 points (Score: Player 2 - Opponent 2).
  - 03:26.200: Player promotes Whimsicott ex to the Active Spot.
- **State delta**: Ogerpon ex discarded. Score 2 - 2.

### Turn 10 (Player)
- **Timestamp range**: 03:28.800 - 03:57.600
- **Evidence anchors**:
  - 03:34.600: Player plays Team Rocket's Goo-zooka (opponent's retreat cost +1).
  - 03:41.000: Player plays Supporter Copycat (draws hand).
  - 03:47.800: Player attaches Grass Energy to Active Whimsicott ex (3 Grass total).
  - 03:49.600: Whimsicott ex attacks with Grass Knot (dealing 130 damage: base 40 + 30 * 3 retreat cost).
  - 03:52.000: Weezing ex HP drops from 140 to 10.
  - 03:54.000: Hiking Trail triggers at end of turn.
- **State delta**: Weezing ex HP 10/140.

### Turn 11 (Opponent)
- **Timestamp range**: 03:57.600 - 04:10.200
- **Evidence anchors**:
  - 04:02.600: Opponent attacks with Weezing ex using Confusion Gas (60 damage).
  - 04:05.000: Whimsicott ex takes 60 damage (HP 140 -> 80) and becomes Confused (04:06.000).
- **State delta**: Whimsicott ex HP 80/140, Confused.

### Turn 12 (Player)
- **Timestamp range**: 04:10.200 - 04:32.400
- **Evidence anchors**:
  - 04:12.400: Player plays Quick-Grow Extract (draws/plays Spinarak to Bench at 04:16.200).
  - 04:17.000: Player plays X Speed (retreat cost 1 less).
  - 04:21.000: Whimsicott ex retreats to Bench, clearing Confusion; Spinarak is promoted to Active.
  - 04:24.400: Player attaches Grass Energy to Active Spinarak (1 Grass).
  - 04:25.600: Spinarak uses Sting (20 damage).
  - 04:27.600: Weezing ex takes 20 damage; HP drops from 10 to 0 (Knocked Out).
  - 04:31.400: Knockout of an ex yields +2 points (Score: Player 3 - Opponent 2).
- **State delta**: Weezing ex Knocked Out. Match ends.

## Terminal Sequence
- **04:31.400 - 04:36.400**: Point counter reaches 3 points for player.
- **04:36.400 - 04:42.400**: "Victory!" banner and post-game presentation displayed.

---

## Required Event Audit
- `Deck searches and failed searches:` 00:53.400 Opponent Poké Ball; 01:26.400 Player Poké Ball; 04:12.400 Player Quick-Grow Extract.
- `Energy attachments and acceleration:` 00:43.000 (Player, Ogerpon ex); 01:33.000 (Player, Ogerpon ex); 01:48.400 (Opponent, Magmar); 02:13.000 (Player, Whimsicott ex); 02:23.000 (Opponent, Magmar); 02:43.000 (Player, Whimsicott ex); 03:13.200 (Opponent, Weezing ex); 03:47.800 (Player, Whimsicott ex); 04:24.400 (Player, Spinarak).
- `Return-to-hand, replay, and exchange events:` 00:57.800 Opponent Copycat; 03:41.000 Player Copycat.
- `Knockouts and score changes:` 01:37.000 Happiny KO (+1 pt player, 1-0); 02:52.000 Magmar KO (+1 pt player, 2-0); 03:17.600 Ogerpon ex KO (+2 pts opponent, 2-2); 04:27.600 Weezing ex KO (+2 pts player, 3-2 / Player Win).
- `Switches, retreats, and Bench changes:` 01:45.400 Opponent promotes Magmar; 02:44.800 Player retreats Ogerpon ex to Whimsicott ex; 03:02.400 Opponent promotes Weezing ex; 03:07.600 Opponent uses Cyrus forcing Ogerpon ex Active; 03:26.200 Player promotes Whimsicott ex; 04:21.000 Player retreats Whimsicott ex to Spinarak.
- `Terminal sequence:` 04:31.400 Player earns 3rd point; 04:36.400 Victory! banner displayed.
```

### REVIEW.md
```markdown
# Battle Review: 20260908_012720000_iOS.MP4

## Overview
- **Date**: Unknown (filename implies 2026-09-08 or export convention)
- **Game Mode**: Solo vs AI (indicated by explicit AI badge above Opponent label)
- **Auto Status**: Toggle displayed on board (manual player control maintained)
- **Player**: Dacz8976
- **Opponent**: Opponent (AI)
- **Outcome**: Player Win (Score 3 - 2; Victory! banner shown)

---

## Starting Board & Opening Setup
- **Player Hand**: Whimsicott ex, Leaf Cape, Ariados, Team Rocket's Goo-zooka.
- **Opening Selection**:
  - Player places Teal Mask Ogerpon ex into the Active Spot.
  - Opponent places Happiny in the Active Spot and benched Team Rocket's Koffing.
- **Turn Priority**: Opponent goes first; Player goes second.

---

## Evidence Ledger

### Turn 1 (Opponent)
- **Observed actions**: Opponent attaches Poison Barb to Happiny, plays Professor's Research drawing 2 cards, benches Team Rocket's Magmar, and attacks with Chubby Cheer.
- **State delta**: Ogerpon ex takes 10 damage (HP 130 -> 120).
- **Evidence anchors**:
  - Card plays: 00:24.600 (Poison Barb), 00:28.400 (Professor's Research), 00:31.400 (Magmar bench).
  - Attack: 00:33.000 (Chubby Cheer). Damage: 00:34.000 (10 damage).

### Turn 2 (Player)
- **Observed actions**: Grass Energy attached to Teal Mask Ogerpon ex; Leaf Cape attached to Ogerpon ex.
- **State delta**: Ogerpon ex HP increases to 150/160; 1 Grass Energy attached.
- **Evidence anchors**:
  - Energy: 00:42.800 (Energy attached).
  - Leaf Cape: 00:46.800 (Leaf Cape attached, HP up at 00:48.000).

### Turn 3 (Opponent)
- **Observed actions**: Plays Poké Ball; plays Copycat; evolves Koffing to Team Rocket's Weezing ex. Boiler Smog triggers, but Ogerpon ex's Soothing Wind prevents Poison/Burn. Poison Barb attached to Magmar. Happiny attacks with Chubby Cheer (+20 boosted = 30 damage).
- **State delta**: Ogerpon ex HP 150 -> 120.
- **Evidence anchors**:
  - Plays: 00:53.400 (Poké Ball), 00:57.800 (Copycat), 01:04.600 (Weezing ex evolution).
  - Soothing Wind protection: 01:10.200 ("Teal Mask Ogerpon ex didn't become Poisoned or Burned").
  - Attack & Damage: 01:16.000, 01:17.200 (30 damage).

### Turn 4 (Player)
- **Observed actions**: Plays Poké Ball grabbing Cottonee; benches Cottonee; attaches Grass Energy to Ogerpon ex; attacks with Energized Leaves (60 damage).
- **State delta**: Happiny KO'd (HP 30 -> 0). Score: 1 - 0. Poison Barb blocked by Soothing Wind. Magmar promoted.
- **Evidence anchors**:
  - Poké Ball: 01:26.400.
  - Energy: 01:32.800.
  - Attack & KO: 01:34.400 - 01:37.000.
  - Point award: 01:42.200 (+1 point).
  - Promotion: 01:45.400 (Magmar Active).

### Turn 5 (Opponent)
- **Observed actions**: Attaches Fire Energy to Magmar; plays Team Rocket's Master Plan (Confusion blocked by Soothing Wind); attacks with Derisive Roasting (50 damage with weakness).
- **State delta**: Ogerpon ex HP 120 -> 70.
- **Evidence anchors**:
  - Attachment: 01:48.400.
  - Master Plan: 01:50.800 (Confusion blocked at 01:52.400).
  - Attack & Weakness Damage: 01:59.800 - 02:01.400 (50 damage shown).

### Turn 6 (Player)
- **Observed actions**: Plays Hiking Trail; evolves Cottonee to Whimsicott ex; attaches Grass Energy to Whimsicott ex; Ogerpon ex attacks with Energized Leaves (60 damage).
- **State delta**: Magmar HP 70 -> 10. Poison Barb blocked by Soothing Wind.
- **Evidence anchors**:
  - Stadium: 02:06.000.
  - Evolution: 02:10.000.
  - Energy: 02:13.000.
  - Attack: 02:15.600; Damage: 02:17.200 (60 damage).

### Turn 7 (Opponent)
- **Observed actions**: Attaches Fire Energy to Magmar; plays Team Rocket's Master Plan (blocked by Soothing Wind); attacks with Derisive Roasting (30 damage).
- **State delta**: Ogerpon ex HP 70 -> 40.
- **Evidence anchors**:
  - Master Plan: 02:25.600.
  - Attack & Damage: 02:34.400 - 02:35.800 (30 damage).

### Turn 8 (Player)
- **Observed actions**: Attaches Grass Energy to Whimsicott ex; retreats Ogerpon ex to Whimsicott ex; Whimsicott ex attacks with Grass Knot for 100 damage (40 base + 60 for 2 retreat cost).
- **State delta**: Magmar KO'd. Score: 2 - 0. Opponent promotes Weezing ex.
- **Evidence anchors**:
  - Energy: 02:42.800.
  - Retreat: 02:44.800.
  - Attack: 02:49.600; KO: 02:52.000.
  - Point award: 02:57.600 (+1 point).
  - Promotion: 03:02.400 (Weezing ex Active).

### Turn 9 (Opponent)
- **Observed actions**: Plays Cyrus, pulling benched damaged Ogerpon ex to Active Spot; attaches Darkness Energy to Weezing ex; attacks with Confusion Gas (60 damage).
- **State delta**: Ogerpon ex KO'd. Opponent awarded 2 points. Score: 2 - 2. Whimsicott ex promoted.
- **Evidence anchors**:
  - Cyrus: 03:07.600 (Ogerpon switched in at 03:11.200).
  - Energy: 03:13.200.
  - Attack & KO: 03:15.000 - 03:17.600.
  - Points: 03:21.400 (+2 points opponent).
  - Promotion: 03:26.200.

### Turn 10 (Player)
- **Observed actions**: Plays Team Rocket's Goo-zooka (+1 retreat cost to Weezing ex); plays Copycat; attaches Grass Energy to Whimsicott ex (3 Grass total); attacks with Grass Knot for 130 damage (base 40 + 30 * 3 retreat cost).
- **State delta**: Weezing ex HP 140 -> 10.
- **Evidence anchors**:
  - Goo-zooka: 03:34.600.
  - Copycat: 03:41.000.
  - Energy: 03:47.800.
  - Attack & Damage: 03:49.600 - 03:51.200 (130 damage).

### Turn 11 (Opponent)
- **Observed actions**: Weezing ex uses Confusion Gas (60 damage).
- **State delta**: Whimsicott ex HP 140 -> 80, Confused.
- **Evidence anchors**:
  - Attack: 04:02.600; Damage: 04:04.200; Confusion applied: 04:06.000.

### Turn 12 (Player)
- **Observed actions**: Plays Quick-Grow Extract benching Spinarak; plays X Speed; retreats Confused Whimsicott ex, promoting Spinarak; attaches Grass Energy to Spinarak; Spinarak attacks with Sting (20 damage).
- **State delta**: Weezing ex KO'd (HP 10 -> 0). Player gains 2 points. Score: 4 (3 required) - 2. Match concludes.
- **Evidence anchors**:
  - Quick-Grow Extract: 04:12.400 (Spinarak placed at 04:16.200).
  - X Speed: 04:17.000.
  - Retreat: 04:21.000.
  - Energy: 04:24.400.
  - Attack & KO: 04:25.600 - 04:27.600.
  - Final points & Victory: 04:31.400 (+2 points), 04:36.400 (Victory!).

---

## Important Mechanics & Tactical Observations
1. **Teal Mask Ogerpon ex Ability (Soothing Wind)**: Completely shut down all poison and status condition strategies from Team Rocket's Weezing ex (Boiler Smog), Poison Barb, and Team Rocket's Master Plan as long as Energy was attached.
2. **Grass Knot + Retreat Cost Synergies**: Whimsicott ex's damage scaled based on the opponent Active's retreat cost, which was actively increased using Team Rocket's Goo-zooka to maximize damage against Weezing ex.
3. **End-game Sequence**: The player cleanly avoided confusion flip risks on Whimsicott ex by using X Speed to retreat into a freshly benched Spinarak via Quick-Grow Extract, attaching an Energy, and taking the final knockout with Sting for 20 damage.

---

## Explicit Uncertainties
None reported by Gemini

---
*Status: Partial pending independent Sol verification*
```

### UNCERTAINTIES.json
```json
[]
```
<!-- END_BATTLE_PACKET -->