### SOURCE.json
```json
{
  "filename": "20260908_010207000_iOS.MP4",
  "source_path": "C:\\Users\\dacz8\\OneDrive\\Desktop\\Battle Logs\\20260908_010207000_iOS.MP4",
  "sha256": "F4956D25FDC445C48FEC9D6705DE40A4721E37367BECE727AA0D7E50E09CCC1F",
  "bytes": 448053217,
  "duration_seconds": 240.595,
  "review_status": "partial",
  "index_update_performed": false,
  "media_move_performed": false,
  "reviewer_attribution": "Gemini 3.8 Flash API first-pass draft",
  "battle_identity": {
    "opponent_label": {
      "state": "observed",
      "value": "Opponent",
      "timestamp_seconds": 3.8,
      "observation": "VS screen shows opponent label 'Opponent' with 'AI' badge above it."
    },
    "opening_player": {
      "state": "observed",
      "value": "Team Rocket's Rattata",
      "timestamp_seconds": 10.4,
      "observation": "Player puts Team Rocket's Rattata (40 HP) into Active Spot."
    },
    "opening_opponent": {
      "state": "observed",
      "value": "Popplio",
      "timestamp_seconds": 13.4,
      "observation": "Opponent reveals Popplio (60 HP) in Active Spot."
    },
    "outcome": {
      "state": "observed",
      "value": "opponent_win",
      "timestamp_seconds": 240.4,
      "observation": "Opponent earns 3 points reaching 3-1; match ends with +2 points display after KOing Team Rocket's Raticate ex."
    },
    "result_text": {
      "state": "not_shown",
      "value": null,
      "timestamp_seconds": 240.4,
      "observation": "Video cuts off on '+2 points!' animation over Opponent score orb 3 before any Victory/Defeat banner appears."
    }
  },
  "evidence_audit": {
    "version": 1,
    "opponent_label": "Opponent",
    "match_mode": {
      "value": "solo",
      "evidence": [
        {
          "timestamp": "00:03.800",
          "observation": "VS splash shows 'AI' pill icon above 'Opponent'"
        }
      ],
      "uncertainty_id": null
    },
    "opponent_ai": {
      "value": "yes",
      "evidence": [
        {
          "timestamp": "00:03.800",
          "observation": "'AI' icon displayed directly over opponent label"
        }
      ],
      "uncertainty_id": null
    },
    "auto": {
      "value": "on",
      "evidence": [
        {
          "timestamp": "00:08.400",
          "observation": "Green 'Auto' checkmark toggle visible on upper right throughout match"
        }
      ],
      "uncertainty_id": null
    },
    "terminal": {
      "outcome": "opponent_win",
      "outcome_evidence": [
        {
          "timestamp": "04:00.400",
          "observation": "Opponent reaches 3 points after Knockout of Team Rocket's Raticate ex"
        }
      ],
      "result_text": null,
      "result_text_evidence": [
        {
          "timestamp": "04:00.400",
          "observation": "Recording ends during point award banner; no final Victory/Defeat screen shown"
        }
      ],
      "last_frame": {
        "timestamp": "04:00.400",
        "observation": "Opponent score orb 3 illuminated, '+2 points!' popup visible"
      },
      "uncertainty_id": null
    },
    "pokemon": [
      {
        "id": "player-1",
        "owner": "player",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:10.400",
          "observation": "Team Rocket's Rattata placed in Active Spot with 0 energy"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "01:45.600",
          "observation": "Knocked out and discarded"
        },
        "uncertainty_id": null
      },
      {
        "id": "opponent-1",
        "owner": "opponent",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:13.400",
          "observation": "Popplio revealed in Active Spot with 0 energy"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "01:25.800",
          "observation": "Knocked out and discarded"
        },
        "uncertainty_id": null
      },
      {
        "id": "opponent-2",
        "owner": "opponent",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:14.000",
          "observation": "Pyukumuku placed on opponent Bench (right)"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "03:58.400",
          "observation": "Pyukumuku remains on Bench with 60 HP, 0 energy"
        },
        "uncertainty_id": null
      },
      {
        "id": "opponent-3",
        "owner": "opponent",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:19.400",
          "observation": "Popplio placed on opponent Bench (left)"
        },
        "final": {
          "Water": 3
        },
        "final_evidence": {
          "timestamp": "03:58.400",
          "observation": "Evolved into Primarina ex in Active Spot with 3 Water energy attached, 60 HP remaining"
        },
        "uncertainty_id": null
      },
      {
        "id": "opponent-4",
        "owner": "opponent",
        "initial": {},
        "initial_evidence": {
          "timestamp": "01:10.600",
          "observation": "Second Pyukumuku placed on opponent Bench (left)"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "03:58.400",
          "observation": "Pyukumuku on Bench with 60 HP, 0 energy"
        },
        "uncertainty_id": null
      },
      {
        "id": "player-2",
        "owner": "player",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:44.800",
          "observation": "Team Rocket's Rattata placed on Bench (center)"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "02:48.400",
          "observation": "Returned to hand via Ilima"
        },
        "uncertainty_id": null
      },
      {
        "id": "player-3",
        "owner": "player",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:43.600",
          "observation": "Alolan Vulpix placed on Bench (right)"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "03:09.600",
          "observation": "Knocked out in Active Spot and discarded"
        },
        "uncertainty_id": null
      },
      {
        "id": "player-4",
        "owner": "player",
        "initial": {},
        "initial_evidence": {
          "timestamp": "02:44.400",
          "observation": "Second Alolan Vulpix placed on Bench (right)"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "03:58.400",
          "observation": "Evolved into Alolan Ninetales ex on Bench, 150 HP, 0 energy"
        },
        "uncertainty_id": null
      },
      {
        "id": "player-5",
        "owner": "player",
        "initial": {},
        "initial_evidence": {
          "timestamp": "02:51.800",
          "observation": "Team Rocket's Rattata replayed from hand onto Bench (left)"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "03:58.400",
          "observation": "Evolved into Team Rocket's Raticate ex in Active Spot, knocked out"
        },
        "uncertainty_id": null
      }
    ],
    "energy_events": [
      {
        "turn": 2,
        "pokemon_id": "player-1",
        "kind": "manual",
        "before": {},
        "after": {
          "Water": 1
        },
        "before_evidence": {
          "timestamp": "00:28.000",
          "observation": "Player Active Rattata has 0 energy"
        },
        "action_evidence": {
          "timestamp": "00:51.600",
          "observation": "Water energy dragged from Energy Zone to Active Rattata"
        },
        "after_evidence": {
          "timestamp": "00:52.200",
          "observation": "Active Rattata now shows 1 Water energy icon"
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 3,
        "pokemon_id": "opponent-3",
        "kind": "manual",
        "before": {},
        "after": {
          "Water": 1
        },
        "before_evidence": {
          "timestamp": "01:00.600",
          "observation": "Benched Popplio has 0 energy"
        },
        "action_evidence": {
          "timestamp": "01:01.800",
          "observation": "Water energy orb flies to Benched Popplio"
        },
        "after_evidence": {
          "timestamp": "01:04.400",
          "observation": "Benched Popplio (evolved to Brionne) has 1 Water energy"
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 4,
        "pokemon_id": "player-1",
        "kind": "manual",
        "before": {
          "Water": 1
        },
        "after": {
          "Water": 2
        },
        "before_evidence": {
          "timestamp": "01:13.000",
          "observation": "Player Active Rattata has 1 Water energy"
        },
        "action_evidence": {
          "timestamp": "01:16.800",
          "observation": "Water energy dragged from Energy Zone to Active Rattata"
        },
        "after_evidence": {
          "timestamp": "01:17.600",
          "observation": "Active Rattata shows 2 Water energy icons"
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 4,
        "pokemon_id": "player-1",
        "kind": "discard",
        "before": {
          "Water": 2
        },
        "after": {},
        "before_evidence": {
          "timestamp": "01:44.000",
          "observation": "Player Active Rattata has 2 Water energy"
        },
        "action_evidence": {
          "timestamp": "01:45.600",
          "observation": "Rattata knocked out by Hydro Pump"
        },
        "after_evidence": {
          "timestamp": "01:46.000",
          "observation": "Rattata removed from play"
        },
        "uncertainty_id": null
      },
      {
        "turn": 5,
        "pokemon_id": "opponent-3",
        "kind": "manual",
        "before": {
          "Water": 1
        },
        "after": {
          "Water": 2
        },
        "before_evidence": {
          "timestamp": "01:32.400",
          "observation": "Active Brionne has 1 Water energy"
        },
        "action_evidence": {
          "timestamp": "01:33.800",
          "observation": "Water energy orb flies to Active Brionne"
        },
        "after_evidence": {
          "timestamp": "01:34.600",
          "observation": "Active Brionne displays 2 Water energy icons"
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 6,
        "pokemon_id": "player-2",
        "kind": "manual",
        "before": {},
        "after": {
          "Water": 1
        },
        "before_evidence": {
          "timestamp": "01:53.400",
          "observation": "Player Benched Rattata has 0 energy"
        },
        "action_evidence": {
          "timestamp": "02:03.400",
          "observation": "Water energy attached to Benched Rattata"
        },
        "after_evidence": {
          "timestamp": "02:04.000",
          "observation": "Benched Rattata shows 1 Water energy icon"
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 6,
        "pokemon_id": "opponent-3",
        "kind": "effect",
        "before": {
          "Water": 2
        },
        "after": {
          "Water": 1
        },
        "before_evidence": {
          "timestamp": "02:00.600",
          "observation": "Opponent Primarina ex has 2 Water energy"
        },
        "action_evidence": {
          "timestamp": "02:04.800",
          "observation": "Thieving Incisors steals 1 energy from opponent Primarina ex to Raticate ex"
        },
        "after_evidence": {
          "timestamp": "02:06.800",
          "observation": "Opponent Primarina ex has 1 Water energy remaining"
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 6,
        "pokemon_id": "player-2",
        "kind": "effect",
        "before": {
          "Water": 1
        },
        "after": {
          "Water": 2
        },
        "before_evidence": {
          "timestamp": "02:04.000",
          "observation": "Benched Rattata/Raticate ex has 1 Water energy"
        },
        "action_evidence": {
          "timestamp": "02:04.800",
          "observation": "Thieving Incisors transfers stolen Water energy to Raticate ex"
        },
        "after_evidence": {
          "timestamp": "02:06.800",
          "observation": "Raticate ex has 2 Water energy"
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 7,
        "pokemon_id": "opponent-3",
        "kind": "manual",
        "before": {
          "Water": 1
        },
        "after": {
          "Water": 2
        },
        "before_evidence": {
          "timestamp": "02:26.800",
          "observation": "Opponent Primarina ex has 1 Water energy"
        },
        "action_evidence": {
          "timestamp": "02:28.000",
          "observation": "Water energy orb flies to Active Primarina ex"
        },
        "after_evidence": {
          "timestamp": "02:28.600",
          "observation": "Primarina ex now has 2 Water energy"
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 8,
        "pokemon_id": "player-3",
        "kind": "manual",
        "before": {},
        "after": {
          "Water": 1
        },
        "before_evidence": {
          "timestamp": "02:40.000",
          "observation": "Player Active Alolan Vulpix has 0 energy"
        },
        "action_evidence": {
          "timestamp": "02:52.800",
          "observation": "Water energy dragged to Active Alolan Vulpix"
        },
        "after_evidence": {
          "timestamp": "02:53.400",
          "observation": "Active Alolan Vulpix shows 1 Water energy"
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 8,
        "pokemon_id": "player-2",
        "kind": "discard",
        "before": {
          "Water": 2
        },
        "after": {},
        "before_evidence": {
          "timestamp": "02:44.000",
          "observation": "Active Raticate ex has 2 Water energy"
        },
        "action_evidence": {
          "timestamp": "02:48.400",
          "observation": "Ilima played to return damaged Raticate ex to hand; attached energy discarded"
        },
        "after_evidence": {
          "timestamp": "02:48.800",
          "observation": "Raticate ex card returned to hand, field spot cleared"
        },
        "uncertainty_id": null
      },
      {
        "turn": 9,
        "pokemon_id": "opponent-3",
        "kind": "manual",
        "before": {
          "Water": 2
        },
        "after": {
          "Water": 3
        },
        "before_evidence": {
          "timestamp": "02:59.600",
          "observation": "Opponent Primarina ex has 2 Water energy"
        },
        "action_evidence": {
          "timestamp": "03:00.600",
          "observation": "Water energy flies to Active Primarina ex"
        },
        "after_evidence": {
          "timestamp": "03:01.400",
          "observation": "Primarina ex displays 3 Water energy"
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 9,
        "pokemon_id": "player-3",
        "kind": "discard",
        "before": {
          "Water": 1
        },
        "after": {},
        "before_evidence": {
          "timestamp": "03:04.000",
          "observation": "Player Active Alolan Vulpix has 1 Water energy"
        },
        "action_evidence": {
          "timestamp": "03:08.400",
          "observation": "Alolan Vulpix knocked out by Sparkling Aria"
        },
        "after_evidence": {
          "timestamp": "03:09.600",
          "observation": "Alolan Vulpix removed to discard"
        },
        "uncertainty_id": null
      },
      {
        "turn": 10,
        "pokemon_id": "player-5",
        "kind": "manual",
        "before": {},
        "after": {
          "Water": 1
        },
        "before_evidence": {
          "timestamp": "03:16.400",
          "observation": "Active Rattata has 0 energy"
        },
        "action_evidence": {
          "timestamp": "03:19.400",
          "observation": "Water energy dragged to Active Rattata"
        },
        "after_evidence": {
          "timestamp": "03:20.000",
          "observation": "Active Rattata displays 1 Water energy"
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 10,
        "pokemon_id": "opponent-3",
        "kind": "effect",
        "before": {
          "Water": 3
        },
        "after": {
          "Water": 2
        },
        "before_evidence": {
          "timestamp": "03:21.000",
          "observation": "Primarina ex has 3 Water energy"
        },
        "action_evidence": {
          "timestamp": "03:25.000",
          "observation": "Second Raticate ex uses Thieving Incisors on Primarina ex"
        },
        "after_evidence": {
          "timestamp": "03:27.400",
          "observation": "Primarina ex has 2 Water energy"
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 10,
        "pokemon_id": "player-5",
        "kind": "effect",
        "before": {
          "Water": 1
        },
        "after": {
          "Water": 2
        },
        "before_evidence": {
          "timestamp": "03:20.000",
          "observation": "Active Raticate ex has 1 Water energy"
        },
        "action_evidence": {
          "timestamp": "03:26.800",
          "observation": "Thieving Incisors attaches stolen energy to Raticate ex"
        },
        "after_evidence": {
          "timestamp": "03:27.400",
          "observation": "Active Raticate ex has 2 Water energy"
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 11,
        "pokemon_id": "opponent-3",
        "kind": "manual",
        "before": {
          "Water": 2
        },
        "after": {
          "Water": 3
        },
        "before_evidence": {
          "timestamp": "03:44.400",
          "observation": "Primarina ex has 2 Water energy"
        },
        "action_evidence": {
          "timestamp": "03:45.000",
          "observation": "Water energy attaches to Primarina ex"
        },
        "after_evidence": {
          "timestamp": "03:45.600",
          "observation": "Primarina ex displays 3 Water energy"
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 11,
        "pokemon_id": "player-5",
        "kind": "discard",
        "before": {
          "Water": 2
        },
        "after": {},
        "before_evidence": {
          "timestamp": "03:52.400",
          "observation": "Active Raticate ex has 2 Water energy"
        },
        "action_evidence": {
          "timestamp": "03:56.800",
          "observation": "Raticate ex knocked out by Sparkling Aria"
        },
        "after_evidence": {
          "timestamp": "03:58.000",
          "observation": "Raticate ex discarded along with its attached energy"
        },
        "uncertainty_id": null
      }
    ]
  }
}
```

### COVERAGE.md
```markdown
# Battle Coverage: 20260908_010207000_iOS.MP4

## Overview
- **Setup Interval:** 00:00.000 – 00:16.400
- **Match Outcome:** Opponent Win (3 - 1)
- **Terminal Sequence:** 03:52.000 – 04:00.400

---

## Turn Breakdown

### Setup (00:00.000 – 00:16.400)
- **Evidence anchors:** Coin flip at 00:05.400 reveals player is "Going second" (Turn 2). Player places Team Rocket's Rattata in Active Spot (00:10.400). Opponent reveals Popplio in Active Spot (00:13.400) and benches Pyukumuku (00:14.000).
- **State delta:** Board initialized.

### Turn 1: Opponent (00:16.600 – 00:27.800)
- **Evidence anchors:** Opponent turn banner at 00:16.800. Opponent benches second Popplio at 00:19.400. Opponent plays Professor's Research at 00:20.800 (draws 2 cards). Opponent plays Poké Ball at 00:24.400 (no Pokémon placed). Opponent passes turn.
- **State delta:** Opponent Bench adds Popplio.

### Turn 2: Player (00:27.800 – 00:59.200)
- **Evidence anchors:** Player draws Professor's Research (00:29.800). Plays Poké Ball (00:33.600) retrieving Alolan Vulpix; benches Alolan Vulpix (00:43.600). Plays second Poké Ball (00:38.800) retrieving Team Rocket's Rattata; benches Rattata (00:44.800). Plays Professor's Research (00:46.000), drawing Ilima and Team Rocket's Raticate ex. Attaches Water Energy to Active Team Rocket's Rattata (00:51.600). Uses Ambush (00:52.600); coin flip Heads (00:54.800), deals 40 damage to Popplio (00:57.400, HP 60 -> 20).
- **State delta:** Player bench populated (Vulpix, Rattata). Active Rattata 1 Energy. Opponent Active Popplio at 20 HP.

### Turn 3: Opponent (00:59.400 – 01:11.400)
- **Evidence anchors:** Generates Water Energy, manually attaches to Benched Popplio (01:01.800). Evolves Benched Popplio into Brionne (01:02.600). Plays Giant Cape onto Brionne (01:06.000, HP 80 -> 100). Benches Pyukumuku (01:10.600). Active Popplio passes/takes no attack action.
- **State delta:** Opponent benched Brionne has 1 Water Energy + Giant Cape (100 HP max). Second Pyukumuku on Bench.

### Turn 4: Player (01:11.600 – 01:31.000)
- **Evidence anchors:** Player turn start. Draws card. Attaches Water Energy to Active Rattata (01:16.800, now 2 Energy). Attacks with Ambush (01:18.400); coin flip Heads (01:20.600), dealing 40 damage to Popplio (01:23.000), knocking it out (01:25.400). Player scores 1st point (01:28.200, Score 1 - 0). Opponent promotes Brionne (01:30.600).
- **State delta:** Opponent Popplio KO'd. Player score 1. Opponent Active is Brionne (100 HP, 1 Energy, Giant Cape).

### Turn 5: Opponent (01:31.200 – 01:52.000)
- **Evidence anchors:** Manually attaches Water Energy to Active Brionne (01:33.800, now 2 Energy). Evolves Brionne into Primarina ex (01:35.400, max HP increases to 200 with Giant Cape). Primarina ex attacks with Hydro Pump (01:41.400) dealing 80 damage (40 base + 40 extra energy) to Rattata (01:43.600), knocking it out. Opponent scores 1 point (01:48.200, Score 1 - 1). Player promotes Alolan Vulpix (01:51.000).
- **State delta:** Player Active Rattata KO'd. Score 1 - 1. Opponent Primarina ex Active (200 HP, 2 Water Energy). Player promotes Alolan Vulpix.

### Turn 6: Player (01:52.000 – 02:25.400)
- **Evidence anchors:** Player draws Field Blower (01:54.000). Attaches Water Energy to Benched Rattata (02:03.400). Evolves Benched Rattata into Team Rocket's Raticate ex (01:58.200). Activates Ability Thieving Incisors (02:01.600), moving 1 Water Energy from opponent Primarina ex to Raticate ex (02:04.800, Raticate now has 2 Energy, Primarina down to 1). Plays Elegant Cape on Raticate ex (02:08.800, HP 120 -> 150). Plays Field Blower (02:13.800) discarding Giant Cape from Primarina ex (02:16.400, Primarina max HP 200 -> 180). Retreats Alolan Vulpix (0 energy cost) to promote Raticate ex (02:20.400). Raticate ex attacks with Boost Dash (02:21.800) dealing 70 damage to Primarina ex (02:23.600, HP 180 -> 110).
- **State delta:** Primarina ex has 110 HP, 1 Energy, no tool. Player Active is Raticate ex (150 HP, 2 Energy, Elegant Cape).

### Turn 7: Opponent (02:25.400 – 02:38.400)
- **Evidence anchors:** Attaches Water Energy to Active Primarina ex (02:28.000, now 2 Energy). Plays Hau (02:29.400), adding +30 damage to Primarina ex's attack. Primarina ex attacks with Hydro Pump (02:34.200) for 110 damage (80 + 30 from Hau) to Raticate ex (02:36.000, HP 150 -> 40).
- **State delta:** Player Raticate ex at 40 HP. Opponent Primarina ex at 110 HP, 2 Energy.

### Turn 8: Player (02:38.600 – 02:57.400)
- **Evidence anchors:** Player draws Alolan Vulpix (02:40.600) and benches it (02:44.400). Plays Supporter Ilima (02:45.400), choosing damaged Active Raticate ex to return to hand (02:48.400); attached Elegant Cape and 2 Water Energy are discarded. Player promotes Benched Alolan Vulpix to Active (02:50.400). Replays Team Rocket's Rattata onto Bench (02:51.600). Attaches Water Energy to Active Alolan Vulpix (02:52.800). Active Alolan Vulpix uses Gnaw (02:54.400), dealing 20 damage to Primarina ex (02:55.600, HP 110 -> 90).
- **State delta:** Primarina ex at 90 HP. Player Active Alolan Vulpix (60 HP, 1 Energy). Player Bench: Alolan Vulpix, Team Rocket's Rattata.

### Turn 9: Opponent (02:57.600 – 03:15.000)
- **Evidence anchors:** Attaches 3rd Water Energy to Primarina ex (03:00.600). Attacks with Sparkling Aria (03:02.800) dealing 100 damage to Alolan Vulpix (03:04.200), knocking it out, while healing 20 damage on Primarina ex (03:06.600, HP 90 -> 110). Opponent scores 1 point (03:11.400, Score 1 - 2). Player promotes Team Rocket's Rattata to Active (03:14.000).
- **State delta:** Score 1 - 2. Primarina ex has 110 HP, 3 Water Energy. Player Active: Team Rocket's Rattata (40 HP, 0 Energy). Player Bench: Alolan Vulpix.

### Turn 10: Player (03:15.200 – 03:42.600)
- **Evidence anchors:** Player draws Professor's Research (03:17.000). Attaches Water Energy to Active Rattata (03:19.400). Evolves Active Rattata into Team Rocket's Raticate ex (03:21.200). Activates Thieving Incisors (03:24.000), moving 1 Water Energy from Primarina ex to Raticate ex (03:26.800, Raticate ex now 2 Energy, Primarina ex down to 2 Energy). Plays Professor's Research (03:28.600), drawing Copycat and Alolan Ninetales ex (03:31.800). Evolves Benched Alolan Vulpix into Alolan Ninetales ex (03:34.200). Attacks with Boost Dash (03:39.000) dealing 70 damage to Primarina ex (03:40.600, HP 110 -> 40).
- **State delta:** Primarina ex at 40 HP, 2 Water Energy. Player Active Raticate ex (120 HP, 2 Water Energy). Player Bench: Alolan Ninetales ex (150 HP, 0 Energy).

### Turn 11: Opponent (03:42.600 – 04:00.400)
- **Evidence anchors:** Attaches Water Energy to Primarina ex (03:45.000, now 3 Water Energy). Plays Hau (03:46.400, +30 damage). Primarina ex attacks with Sparkling Aria (03:51.200) dealing 130 damage (100 + 30) to Raticate ex (03:53.000), knocking it out (03:57.200). Primarina heals 20 damage (HP 40 -> 60). Opponent awarded 2 points for Knockout of an ex Pokémon (04:00.400), bringing Opponent score to 3.
- **State delta:** Opponent reaches 3 points. Match concluded.

---

## Required Event Audit
- `Deck searches and failed searches:` Turn 2 Poké Ball (00:33.600) retrieved Alolan Vulpix; Poké Ball (00:38.800) retrieved Team Rocket's Rattata.
- `Energy attachments and acceleration:` Turn 2 player manual to player-1 (00:51.600); Turn 3 opponent manual to opponent-3 (01:01.800); Turn 4 player manual to player-1 (01:16.800); Turn 5 opponent manual to opponent-3 (01:33.800); Turn 6 player manual to player-2 (02:03.400); Turn 6 player Ability Thieving Incisors moves 1 energy from opponent-3 to player-2 (02:04.800); Turn 7 opponent manual to opponent-3 (02:28.000); Turn 8 player manual to player-3 (02:52.800); Turn 9 opponent manual to opponent-3 (03:00.600); Turn 10 player manual to player-5 (03:19.400); Turn 10 player Ability Thieving Incisors moves 1 energy from opponent-3 to player-5 (03:26.800); Turn 11 opponent manual to opponent-3 (03:45.000).
- `Return-to-hand, replay, and exchange events:` Turn 8 player plays Ilima (02:45.400), returning damaged player-2 (Raticate ex) to hand (02:48.400); Team Rocket's Rattata replayed from hand at 02:51.600.
- `Knockouts and score changes:` Turn 4 opponent-1 KO'd (01:25.400), Player score 0 -> 1 (01:28.200); Turn 5 player-1 KO'd (01:45.600), Opponent score 0 -> 1 (01:48.200); Turn 9 player-3 KO'd (03:08.400), Opponent score 1 -> 2 (03:11.400); Turn 11 player-5 KO'd (03:57.200), Opponent score 2 -> 3 (04:00.400).
- `Switches, retreats, and Bench changes:` Turn 4 opponent promotes Brionne (01:30.600); Turn 5 player promotes Alolan Vulpix (01:51.000); Turn 6 player retreats Alolan Vulpix, promotes Raticate ex (02:20.400); Turn 8 Raticate ex lifted via Ilima, promotes Alolan Vulpix (02:50.400); Turn 9 player promotes Rattata (03:14.000).
- `Terminal sequence:` Turn 11 Primarina ex knocks out Team Rocket's Raticate ex with Sparkling Aria boosted by Hau (130 damage); opponent receives 2 points to reach 3 points at 04:00.400; video ends during '+2 points!' animation.
```

### REVIEW.md
```markdown
# Match Review: 20260908_010207000_iOS.MP4

## Match Metadata
- **Date:** Unknown (derived filename date pattern 2026-09-08 is future/unverified)
- **Mode:** Solo (AI match, indicated by "AI" emblem on opponent banner at 00:03.800)
- **Auto:** Enabled (green checkmark visible throughout)
- **Player:** Dacz8976
- **Opponent:** Opponent (AI)
- **Starting Board:**
  - Player: Team Rocket's Rattata Active (40 HP)
  - Opponent: Popplio Active (60 HP), Pyukumuku Bench (60 HP)
- **Opening Hand (Player):** Poké Ball, Sabrina, Poké Ball, Elegant Cape

---

## Turn-by-Turn Evidence Ledger

### Turn 1 (Opponent)
- **Observed actions:** Plays Popplio to Bench. Plays Professor's Research, drawing 2 cards. Plays Poké Ball. Passes turn.
- **State delta:** Opponent Bench: Popplio (60 HP), Pyukumuku (60 HP). Hand: 3 cards.
- **Evidence anchors:** 00:19.400 (Popplio bench), 00:20.800 (Professor's Research), 00:24.400 (Poké Ball).

### Turn 2 (Player)
- **Observed actions:** Draws Professor's Research. Plays Poké Ball -> retrieves Alolan Vulpix, benches it. Plays Poké Ball -> retrieves Team Rocket's Rattata, benches it. Plays Professor's Research -> draws Ilima and Team Rocket's Raticate ex. Attaches Water Energy to Active Rattata. Uses Ambush (Heads) for 40 damage.
- **State delta:** Player Active Rattata: 1 Water Energy. Benched: Alolan Vulpix (60 HP), Rattata (40 HP). Opponent Active Popplio: 20 HP remaining.
- **Evidence anchors:** 00:29.800 (draw), 00:33.600 (Poké Ball 1), 00:38.800 (Poké Ball 2), 00:46.000 (Research), 00:51.600 (Energy), 00:54.800 (coin flip Heads), 00:57.400 (40 damage).

### Turn 3 (Opponent)
- **Observed actions:** Attaches Water Energy to Benched Popplio. Evolves Benched Popplio into Brionne. Attaches Giant Cape to Brionne (+20 HP max). Benches second Pyukumuku. Passes turn.
- **State delta:** Opponent Benched Brionne: 1 Water Energy, Giant Cape (100 HP max). Second Pyukumuku benched (60 HP).
- **Evidence anchors:** 01:01.800 (Energy), 01:02.600 (Brionne), 01:06.000 (Giant Cape), 01:10.600 (Pyukumuku).

### Turn 4 (Player)
- **Observed actions:** Draws card. Attaches second Water Energy to Active Rattata. Attacks with Ambush (Heads) for 40 damage, knocking out Active Popplio. Player awarded 1 point. Opponent promotes Brionne.
- **State delta:** Player score: 1. Opponent Popplio KO'd. Opponent Active: Brionne (100 HP, 1 Water Energy, Giant Cape).
- **Evidence anchors:** 01:16.800 (Energy), 01:20.600 (Heads), 01:23.000 (40 damage), 01:25.400 (KO), 01:28.200 (Score 1-0), 01:30.600 (promotion).

### Turn 5 (Opponent)
- **Observed actions:** Attaches Water Energy to Active Brionne (now 2 Energy). Evolves Brionne into Primarina ex (max HP 200 with Giant Cape). Primarina ex attacks with Hydro Pump (80 damage) knocking out player's Active Rattata. Opponent awarded 1 point. Player promotes Alolan Vulpix.
- **State delta:** Score: 1 - 1. Player Active: Alolan Vulpix (60 HP, 0 Energy). Opponent Active: Primarina ex (200 HP, 2 Water Energy, Giant Cape).
- **Evidence anchors:** 01:33.800 (Energy), 01:35.400 (Primarina ex), 01:41.400 (Hydro Pump), 01:45.600 (KO), 01:48.200 (Score 1-1), 01:51.000 (promotion).

### Turn 6 (Player)
- **Observed actions:** Draws Field Blower. Attaches Water Energy to Benched Rattata. Evolves Benched Rattata into Team Rocket's Raticate ex. Triggers Ability Thieving Incisors to steal 1 Energy from Primarina ex to Raticate ex. Attaches Elegant Cape to Raticate ex (+30 HP, max 150). Plays Field Blower, discarding Giant Cape from Primarina ex (HP drops to 180 max). Retreats Alolan Vulpix for 0 Energy, promoting Raticate ex. Raticate ex attacks with Boost Dash (70 damage).
- **State delta:** Primarina ex at 110 HP, 1 Water Energy. Player Active Raticate ex at 150 HP, 2 Water Energy, Elegant Cape.
- **Evidence anchors:** 01:54.000 (draw), 01:58.200 (Raticate ex), 02:01.600 (Ability), 02:04.800 (energy stolen), 02:08.800 (Elegant Cape), 02:13.800 (Field Blower), 02:20.400 (switch/promotion), 02:21.800 (Boost Dash), 02:23.600 (70 damage).

### Turn 7 (Opponent)
- **Observed actions:** Attaches Water Energy to Primarina ex (now 2 Energy). Plays Hau (+30 attack damage). Attacks with Hydro Pump for 110 damage (80 + 30).
- **State delta:** Player Active Raticate ex at 40 HP (150 - 110). Opponent Primarina ex at 110 HP, 2 Water Energy.
- **Evidence anchors:** 02:28.000 (Energy), 02:29.400 (Hau), 02:34.200 (Hydro Pump), 02:36.000 (110 damage).

### Turn 8 (Player)
- **Observed actions:** Draws Alolan Vulpix, benches it. Plays Ilima to scoop damaged Active Raticate ex back to hand (Elegant Cape and 2 attached Water Energy are discarded). Promotes Benched Alolan Vulpix to Active. Replays Team Rocket's Rattata onto Bench. Attaches Water Energy to Active Alolan Vulpix. Uses Gnaw for 20 damage.
- **State delta:** Opponent Primarina ex at 90 HP (110 - 20). Player Active: Alolan Vulpix (60 HP, 1 Water Energy). Player Bench: Alolan Vulpix (60 HP), Team Rocket's Rattata (40 HP).
- **Evidence anchors:** 02:40.600 (draw), 02:44.400 (bench Vulpix), 02:45.400 (Ilima), 02:48.400 (scoop), 02:50.400 (promotion), 02:51.600 (bench Rattata), 02:52.800 (Energy), 02:54.400 (Gnaw), 02:55.600 (20 damage).

### Turn 9 (Opponent)
- **Observed actions:** Attaches 3rd Water Energy to Primarina ex. Attacks with Sparkling Aria for 100 damage, knocking out Active Alolan Vulpix and healing Primarina ex for 20 HP (90 -> 110 HP). Opponent awarded 1 point. Player promotes Team Rocket's Rattata.
- **State delta:** Score: 1 - 2. Primarina ex at 110 HP, 3 Water Energy. Player Active: Team Rocket's Rattata (40 HP).
- **Evidence anchors:** 03:00.600 (Energy), 03:02.800 (Sparkling Aria), 03:04.200 (100 damage & KO), 03:06.600 (heal 20), 03:11.400 (Score 1-2), 03:14.000 (promotion).

### Turn 10 (Player)
- **Observed actions:** Draws Professor's Research. Attaches Water Energy to Active Rattata. Evolves Active Rattata into Team Rocket's Raticate ex. Triggers Thieving Incisors, stealing 1 Water Energy from Primarina ex. Plays Professor's Research, drawing Copycat and Alolan Ninetales ex. Evolves Benched Alolan Vulpix into Alolan Ninetales ex. Raticate ex attacks with Boost Dash for 70 damage.
- **State delta:** Primarina ex at 40 HP (110 - 70), 2 Water Energy. Player Active Raticate ex at 120 HP, 2 Water Energy. Player Benched Alolan Ninetales ex (150 HP, 0 Energy).
- **Evidence anchors:** 03:17.000 (draw), 03:19.400 (Energy), 03:21.200 (evolution), 03:24.000 (Ability), 03:26.800 (energy stolen), 03:28.600 (Research), 03:34.200 (evolution), 03:39.000 (Boost Dash), 03:40.600 (70 damage).

### Turn 11 (Opponent)
- **Observed actions:** Attaches Water Energy to Primarina ex (now 3 Water Energy). Plays Hau (+30 damage). Attacks with Sparkling Aria dealing 130 damage (100 + 30) to Active Raticate ex, knocking it out. Opponent awarded 2 points for Knockout of an ex Pokémon, reaching 3 points total.
- **State delta:** Score: 1 - 3. Player Active Raticate ex KO'd. Opponent wins.
- **Evidence anchors:** 03:45.000 (Energy), 03:46.400 (Hau), 03:51.200 (Sparkling Aria), 03:53.000 (130 damage), 03:57.200 (KO), 04:00.400 (+2 points to 3).

---

## Tactical Summary & Outcome
- **Outcome:** Opponent Win (3 - 1)
- **Deciding Factors:** Primarina ex's high HP combined with Hau gave the AI enough burst damage (130) to achieve a one-hit knockout on Team Rocket's Raticate ex on Turn 11, securing the match before the player could clean up the remaining 40 HP on Primarina ex.
- **Status:** Partial pending independent Sol verification

## Explicit Uncertainties
None reported by Gemini
```

### UNCERTAINTIES.json
```json
[]
```
<!-- END_BATTLE_PACKET -->