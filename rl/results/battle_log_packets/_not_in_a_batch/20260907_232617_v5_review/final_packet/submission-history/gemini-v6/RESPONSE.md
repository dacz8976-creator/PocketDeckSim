### SOURCE.json
```json
{
  "filename": "20260907_232617000_iOS.MP4",
  "source_path": "C:\\Users\\dacz8\\OneDrive\\Desktop\\Battle Logs\\20260907_232617000_iOS.MP4",
  "sha256": "0114215B1DF4E6D6DD2B21C47616B9F9486788F815BC48B978DBA06D68490166",
  "bytes": 824157596,
  "duration_seconds": 441.538,
  "recording_type": "battle_recording",
  "relationships": [],
  "model": "gemini-3.8-flash",
  "sampling_method": "static video processing at 5 source frames per second with high media resolution",
  "reviewer_attribution": "Gemini 3.8 Flash API first-pass draft",
  "review_status": "partial",
  "outcome": "player_win",
  "index_update_performed": false,
  "media_move_performed": false,
  "evidence_audit": {
    "version": 1,
    "opponent_label": "Kuro",
    "match_mode": {
      "value": "unknown",
      "evidence": [
        {
          "timestamp": "00:04.500",
          "observation": "Versus display shows Kuro with custom emblem; no matchmaking mode label visible"
        }
      ],
      "uncertainty_id": "U1"
    },
    "opponent_ai": {
      "value": "unknown",
      "evidence": [
        {
          "timestamp": "00:04.500",
          "observation": "Opponent name Kuro displayed without CPU/AI tag"
        }
      ],
      "uncertainty_id": "U1"
    },
    "auto": {
      "value": "unknown",
      "evidence": [
        {
          "timestamp": "00:25.000",
          "observation": "No Auto button displayed on interface"
        }
      ],
      "uncertainty_id": "U2"
    },
    "terminal": {
      "outcome": "player_win",
      "outcome_evidence": [
        {
          "timestamp": "07:18.500",
          "observation": "Player awarded final 2 points for knocking out Articuno ex, reaching winning score"
        }
      ],
      "result_text": "VICTORY",
      "result_text_evidence": [
        {
          "timestamp": "07:20.500",
          "observation": "VICTORY banner displayed across center screen"
        }
      ],
      "last_frame": {
        "timestamp": "07:21.538",
        "observation": "Victory banner and particle effects visible on final frame"
      },
      "uncertainty_id": null
    },
    "pokemon": [
      {
        "id": "player-koffing-1",
        "owner": "player",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:18.000",
          "observation": "Koffing placed in Active Spot with 0 Energy"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "03:35.000",
          "observation": "Evolved Weezing returned to hand via Koga; attached Darkness Energy discarded"
        },
        "uncertainty_id": null
      },
      {
        "id": "player-ekans-1",
        "owner": "player",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:40.000",
          "observation": "Ekans benched with 0 Energy"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "06:00.000",
          "observation": "Evolved Arbok knocked out by Blizzard and discarded"
        },
        "uncertainty_id": null
      },
      {
        "id": "player-ekans-2",
        "owner": "player",
        "initial": {},
        "initial_evidence": {
          "timestamp": "03:20.000",
          "observation": "Second Ekans benched with 0 Energy"
        },
        "final": {
          "Darkness": 1
        },
        "final_evidence": {
          "timestamp": "07:21.000",
          "observation": "Ekans remains on Bench with 1 Darkness Energy attached"
        },
        "uncertainty_id": null
      },
      {
        "id": "player-koffing-2",
        "owner": "player",
        "initial": {},
        "initial_evidence": {
          "timestamp": "04:38.000",
          "observation": "Koffing played to Bench with 0 Energy"
        },
        "final": {
          "Darkness": 1
        },
        "final_evidence": {
          "timestamp": "07:21.000",
          "observation": "Weezing remains in Active Spot with 1 Darkness Energy attached"
        },
        "uncertainty_id": null
      },
      {
        "id": "opp-staryu-1",
        "owner": "opponent",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:18.000",
          "observation": "Staryu placed in Active Spot with 0 Energy"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "02:18.000",
          "observation": "Staryu knocked out by Poison and discarded"
        },
        "uncertainty_id": null
      },
      {
        "id": "opp-froakie-1",
        "owner": "opponent",
        "initial": {},
        "initial_evidence": {
          "timestamp": "01:19.000",
          "observation": "Froakie played to Bench with 0 Energy"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "04:28.000",
          "observation": "Evolved Frogadier knocked out by Poison and discarded"
        },
        "uncertainty_id": null
      },
      {
        "id": "opp-articuno-ex-1",
        "owner": "opponent",
        "initial": {},
        "initial_evidence": {
          "timestamp": "02:34.000",
          "observation": "Articuno ex played to Bench with 0 Energy"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "07:18.500",
          "observation": "Articuno ex knocked out by Tackle and discarded"
        },
        "uncertainty_id": null
      }
    ],
    "energy_events": [
      {
        "turn": 2,
        "pokemon_id": "player-koffing-1",
        "kind": "manual",
        "before": {},
        "after": {
          "Darkness": 1
        },
        "before_evidence": {
          "timestamp": "00:35.000",
          "observation": "Koffing has 0 Energy attached"
        },
        "action_evidence": {
          "timestamp": "00:44.000",
          "observation": "Darkness Energy dragged from Energy Zone to Active Koffing"
        },
        "after_evidence": {
          "timestamp": "00:46.500",
          "observation": "Active Koffing displays 1 Darkness Energy icon"
        },
        "attachment_evidence": "movement_and_attached_icons",
        "cause": null,
        "uncertainty_id": null
      },
      {
        "turn": 3,
        "pokemon_id": "opp-staryu-1",
        "kind": "manual",
        "before": {},
        "after": {
          "Water": 1
        },
        "before_evidence": {
          "timestamp": "01:00.000",
          "observation": "Staryu has 0 Energy attached"
        },
        "action_evidence": {
          "timestamp": "01:14.000",
          "observation": "Water Energy moves from Energy Zone to Active Staryu"
        },
        "after_evidence": {
          "timestamp": "01:16.500",
          "observation": "Active Staryu displays 1 Water Energy icon"
        },
        "attachment_evidence": "movement_and_attached_icons",
        "cause": null,
        "uncertainty_id": null
      },
      {
        "turn": 4,
        "pokemon_id": "player-ekans-1",
        "kind": "manual",
        "before": {},
        "after": {
          "Darkness": 1
        },
        "before_evidence": {
          "timestamp": "01:55.000",
          "observation": "Benched Ekans has 0 Energy attached"
        },
        "action_evidence": {
          "timestamp": "02:01.000",
          "observation": "Darkness Energy dragged from Energy Zone to Benched Ekans"
        },
        "after_evidence": {
          "timestamp": "02:04.000",
          "observation": "Benched Ekans displays 1 Darkness Energy icon"
        },
        "attachment_evidence": "movement_and_attached_icons",
        "cause": null,
        "uncertainty_id": null
      },
      {
        "turn": 4,
        "pokemon_id": "opp-staryu-1",
        "kind": "discard",
        "before": {
          "Water": 1
        },
        "after": {},
        "before_evidence": {
          "timestamp": "02:12.000",
          "observation": "Staryu has 1 Water Energy before knockout"
        },
        "action_evidence": {
          "timestamp": "02:16.000",
          "observation": "Staryu knocked out by Poison"
        },
        "after_evidence": {
          "timestamp": "02:18.000",
          "observation": "Staryu and its attached Water Energy sent to discard pile"
        },
        "attachment_evidence": null,
        "cause": null,
        "uncertainty_id": null
      },
      {
        "turn": 5,
        "pokemon_id": "opp-froakie-1",
        "kind": "manual",
        "before": {},
        "after": {
          "Water": 1
        },
        "before_evidence": {
          "timestamp": "02:28.000",
          "observation": "Active Frogadier has 0 Energy attached"
        },
        "action_evidence": {
          "timestamp": "02:39.000",
          "observation": "Water Energy moves from Energy Zone to Active Frogadier"
        },
        "after_evidence": {
          "timestamp": "02:41.500",
          "observation": "Active Frogadier displays 1 Water Energy icon"
        },
        "attachment_evidence": "movement_and_attached_icons",
        "cause": null,
        "uncertainty_id": null
      },
      {
        "turn": 6,
        "pokemon_id": "player-ekans-1",
        "kind": "manual",
        "before": {
          "Darkness": 1
        },
        "after": {
          "Darkness": 2
        },
        "before_evidence": {
          "timestamp": "03:18.000",
          "observation": "Benched Arbok has 1 Darkness Energy attached"
        },
        "action_evidence": {
          "timestamp": "03:25.000",
          "observation": "Darkness Energy dragged from Energy Zone to Benched Arbok"
        },
        "after_evidence": {
          "timestamp": "03:27.500",
          "observation": "Benched Arbok displays 2 Darkness Energy icons"
        },
        "attachment_evidence": "movement_and_attached_icons",
        "cause": null,
        "uncertainty_id": null
      },
      {
        "turn": 6,
        "pokemon_id": "player-koffing-1",
        "kind": "discard",
        "before": {
          "Darkness": 1
        },
        "after": {},
        "before_evidence": {
          "timestamp": "03:28.000",
          "observation": "Active Weezing has 1 Darkness Energy attached"
        },
        "action_evidence": {
          "timestamp": "03:32.000",
          "observation": "Koga played, returning Weezing to hand"
        },
        "after_evidence": {
          "timestamp": "03:35.000",
          "observation": "Weezing returns to hand and attached Darkness Energy is discarded"
        },
        "attachment_evidence": null,
        "cause": null,
        "uncertainty_id": null
      },
      {
        "turn": 7,
        "pokemon_id": "opp-articuno-ex-1",
        "kind": "effect",
        "before": {},
        "after": {
          "Water": 2
        },
        "before_evidence": {
          "timestamp": "03:52.000",
          "observation": "Benched Articuno ex has 0 Energy attached"
        },
        "action_evidence": {
          "timestamp": "04:00.000",
          "observation": "Misty resolves with 2 heads, attaching 2 Water Energy to Articuno ex"
        },
        "after_evidence": {
          "timestamp": "04:06.000",
          "observation": "Benched Articuno ex displays 2 Water Energy icons"
        },
        "attachment_evidence": null,
        "cause": "Misty",
        "uncertainty_id": null
      },
      {
        "turn": 7,
        "pokemon_id": "opp-articuno-ex-1",
        "kind": "manual",
        "before": {
          "Water": 2
        },
        "after": {
          "Water": 3
        },
        "before_evidence": {
          "timestamp": "04:08.000",
          "observation": "Benched Articuno ex has 2 Water Energy attached"
        },
        "action_evidence": {
          "timestamp": "04:12.000",
          "observation": "Water Energy moves from Energy Zone to Benched Articuno ex"
        },
        "after_evidence": {
          "timestamp": "04:14.500",
          "observation": "Benched Articuno ex displays 3 Water Energy icons"
        },
        "attachment_evidence": "movement_and_attached_icons",
        "cause": null,
        "uncertainty_id": null
      },
      {
        "turn": 7,
        "pokemon_id": "opp-froakie-1",
        "kind": "discard",
        "before": {
          "Water": 1
        },
        "after": {},
        "before_evidence": {
          "timestamp": "04:22.000",
          "observation": "Frogadier has 1 Water Energy before knockout"
        },
        "action_evidence": {
          "timestamp": "04:26.000",
          "observation": "Frogadier knocked out by Poison"
        },
        "after_evidence": {
          "timestamp": "04:28.000",
          "observation": "Frogadier and attached Water Energy discarded"
        },
        "attachment_evidence": null,
        "cause": null,
        "uncertainty_id": null
      },
      {
        "turn": 8,
        "pokemon_id": "player-ekans-2",
        "kind": "manual",
        "before": {},
        "after": {
          "Darkness": 1
        },
        "before_evidence": {
          "timestamp": "04:36.000",
          "observation": "Benched Ekans has 0 Energy attached"
        },
        "action_evidence": {
          "timestamp": "04:42.000",
          "observation": "Darkness Energy dragged from Energy Zone to Benched Ekans"
        },
        "after_evidence": {
          "timestamp": "04:45.000",
          "observation": "Benched Ekans displays 1 Darkness Energy icon"
        },
        "attachment_evidence": "movement_and_attached_icons",
        "cause": null,
        "uncertainty_id": null
      },
      {
        "turn": 9,
        "pokemon_id": "opp-articuno-ex-1",
        "kind": "manual",
        "before": {
          "Water": 3
        },
        "after": {
          "Water": 4
        },
        "before_evidence": {
          "timestamp": "05:28.000",
          "observation": "Active Articuno ex has 3 Water Energy attached"
        },
        "action_evidence": {
          "timestamp": "05:33.000",
          "observation": "Water Energy moves from Energy Zone to Active Articuno ex"
        },
        "after_evidence": {
          "timestamp": "05:35.500",
          "observation": "Active Articuno ex displays 4 Water Energy icons"
        },
        "attachment_evidence": "movement_and_attached_icons",
        "cause": null,
        "uncertainty_id": null
      },
      {
        "turn": 9,
        "pokemon_id": "player-ekans-1",
        "kind": "discard",
        "before": {
          "Darkness": 2
        },
        "after": {},
        "before_evidence": {
          "timestamp": "05:44.000",
          "observation": "Active Arbok has 2 Darkness Energy attached"
        },
        "action_evidence": {
          "timestamp": "05:54.000",
          "observation": "Arbok knocked out by Blizzard"
        },
        "after_evidence": {
          "timestamp": "05:58.000",
          "observation": "Arbok and attached 2 Darkness Energy sent to discard pile"
        },
        "attachment_evidence": null,
        "cause": null,
        "uncertainty_id": null
      },
      {
        "turn": 10,
        "pokemon_id": "player-koffing-2",
        "kind": "manual",
        "before": {},
        "after": {
          "Darkness": 1
        },
        "before_evidence": {
          "timestamp": "06:14.000",
          "observation": "Active Weezing has 0 Energy attached"
        },
        "action_evidence": {
          "timestamp": "06:27.000",
          "observation": "Darkness Energy dragged from Energy Zone to Active Weezing"
        },
        "after_evidence": {
          "timestamp": "06:30.000",
          "observation": "Active Weezing displays 1 Darkness Energy icon"
        },
        "attachment_evidence": "movement_and_attached_icons",
        "cause": null,
        "uncertainty_id": null
      },
      {
        "turn": 11,
        "pokemon_id": "opp-articuno-ex-1",
        "kind": "manual",
        "before": {
          "Water": 4
        },
        "after": {
          "Water": 5
        },
        "before_evidence": {
          "timestamp": "06:46.000",
          "observation": "Active Articuno ex has 4 Water Energy attached"
        },
        "action_evidence": {
          "timestamp": "06:51.000",
          "observation": "Water Energy moves from Energy Zone to Active Articuno ex"
        },
        "after_evidence": {
          "timestamp": "06:53.500",
          "observation": "Active Articuno ex displays 5 Water Energy icons"
        },
        "attachment_evidence": "movement_and_attached_icons",
        "cause": null,
        "uncertainty_id": null
      },
      {
        "turn": 12,
        "pokemon_id": "opp-articuno-ex-1",
        "kind": "discard",
        "before": {
          "Water": 5
        },
        "after": {},
        "before_evidence": {
          "timestamp": "07:12.000",
          "observation": "Active Articuno ex has 5 Water Energy attached"
        },
        "action_evidence": {
          "timestamp": "07:16.000",
          "observation": "Articuno ex knocked out by Tackle"
        },
        "after_evidence": {
          "timestamp": "07:18.500",
          "observation": "Articuno ex and attached 5 Water Energy sent to discard pile"
        },
        "attachment_evidence": null,
        "cause": null,
        "uncertainty_id": null
      }
    ]
  }
}
```

### COVERAGE.md
```markdown
# Coverage Summary: 20260907_232617000_iOS.MP4

## Match Intervals
- **Setup:** 00:00.000 - 00:18.000
  - *Evidence anchors:* Versus screen Dacz vs Kuro at 00:04.500; coin flip gives Kuro first turn at 00:13.000; Staryu and Koffing revealed active at 00:18.000.
  - *State delta:* Kuro Active: Staryu (60 HP, 0 Energy); Dacz Active: Koffing (60 HP, 0 Energy).
- **Turn 1 (Opponent - Kuro):** 00:18.000 - 00:32.000
  - *Evidence anchors:* Turn announcement 00:18.500; pass action 00:30.000.
  - *State delta:* None. Turn 1 going first player cannot attach energy or attack.
- **Turn 2 (Player - Dacz):** 00:32.000 - 00:58.000
  - *Evidence anchors:* Darkness Energy generated 00:34.000; Ekans benched 00:40.000; Darkness Energy attached to Koffing 00:44.000; Tackle deals 20 damage 00:51.000.
  - *State delta:* Dacz Bench: Ekans (60 HP, 0 Energy); Koffing Energy: 0 -> 1 Darkness; Kuro Active Staryu HP: 60 -> 40.
- **Turn 3 (Opponent - Kuro):** 00:58.000 - 01:34.000
  - *Evidence anchors:* Misty played 01:04.000 (tails, 0 Energy); Water Energy attached to Staryu 01:14.000; Froakie benched 01:19.000; Smack deals 20 damage 01:26.000.
  - *State delta:* Kuro Bench: Froakie (60 HP, 0 Energy); Staryu Energy: 0 -> 1 Water; Dacz Active Koffing HP: 60 -> 40.
- **Turn 4 (Player - Dacz):** 01: