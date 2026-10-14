# Sparse triage: 20260907_232035 and 20260907_232617

## Disposition

The two recordings are independent, apparently complete matches rather than parts of one split recording. Each begins at its own setup/opening and reaches its own opponent-win screen. The opponents and opposing decks differ: `232035` opens against a Psychic/Team Rocket board, while `232617` opens against a Fighting board that includes Falinks and Hitmonchan ex. The recorder uses the same Eevee/Jolteon ex/Oricorio/Team Rocket Rattata family in both.

This is a sparse visual intake, not a full action transcript. It establishes file identity, broad match boundaries, sampled Auto state, and one follow-up candidate.

## Sources

| Video | Bytes | Duration | SHA-256 | Boundary evidence |
|---|---:|---:|---|---|
| `20260907_232035000_iOS.MP4` | 324,067,959 | 174.94 s | `6d46c09829214b203de0f3fb7a52b9f394a06e6f586395b984f4662344ff6be3` | Own opening/setup at 1–10 s; opponent reaches three points by 172 s |
| `20260907_232617000_iOS.MP4` | 824,157,596 | 441.54 s | `0114215b1df4e6d6dd2b21c47616b9f9486788f815bc48b978dba06d68490166` | Separate opponent setup visible at 20 s; opponent reaches three points by 438 s |

The source byte sizes still match `INTAKE.json` after extraction. Whole-file hashes come from that completed intake; the sparse decoder did not rehash or modify the originals.

## Auto evidence

In `232035`, the checked turquoise **Auto** control is visible in sampled gameplay frames at 25, 40, 55, 70, 85, 100, 115, 130, 145, and 160 seconds. It is also visible throughout the focused 145–150 second sequence. These observations establish Auto at those timestamps; they do not prove uninterrupted Auto state between samples.

No checked Auto control is visible in the sampled gameplay frames from `232617` (50–410 seconds). That recording uses a different battle UI with clocks and frequent “Waiting for opponent” states. Sparse sampling does not establish the control's state at every moment.

## Candidate: Thieving Incisors Energy movement

The clearest bounded mechanic candidate occurs in `232035` while Auto is visibly checked:

- [145.000 s](focus/232035-raticate/145.000.jpg): Team Rocket's Raticate ex is being played to evolve the recorder's Benched Pokémon. The opposing Active Team Rocket's Slowking ex has two visible Psychic Energy; the recorder has one point and the opponent has two.
- [147.000 s](focus/232035-raticate/147.000.jpg): Raticate ex has settled on the Bench with no attached Energy; both Psychic Energy remain on Slowking ex.
- [148.000 s](focus/232035-raticate/148.000.jpg): the **Thieving Incisors** ability banner is visible.
- [149.000 s](focus/232035-raticate/149.000.jpg): the Energy-transfer animation travels from the opposing Active toward Raticate ex.
- [150.000 s](focus/232035-raticate/150.000.jpg): Raticate ex has one Psychic Energy and Slowking ex has one, confirming one attached Energy moved. Because both source Energy were visibly Psychic, the random selection does not distinguish Energy types in this observed instance.

The readable card inspection at [158.000 s](focus/232035-raticate/158.000.jpg) says the ability may move a random Energy from the opponent's Active Pokémon to this Pokémon when it is played from hand to evolve one of the player's Pokémon. The exact database/CardId printing is intentionally unassigned in this intake.

A later focused review could bind the card printing and create a composite engine check for evolution-trigger timing, the optional ability choice, removal from the opposing Active, and attachment to the newly evolved Benched Pokémon. Useful controls would cover no opposing Energy and a non-evolution placement. This intake does not establish a bug, strategy error, or optimal line.

## Limits and preserved evidence

The opponent's hand and deck order are private. The recorder's hand is only partially visible, and neither match was reconstructed into a full public state. Card identities outside the readable candidate and broad matchup anchors remain provisional. The contact sheets are row-major and timestamp-bound through `CONTACT_INDEX.json`; exact extraction commands and frame hashes are in `FRAME_MANIFEST.json`, `FOCUS_MANIFEST.json`, and `CONTACT_COMMANDS.json`.

