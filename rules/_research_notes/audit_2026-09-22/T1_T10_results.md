# T1 — opening hands on the current app (Dustin's test, 2026-09-22)

**Question** (`05` #6, `07` H1): is the guaranteed Basic dealt "Basic first, then 4 random" (the engine) or "deal 5, swap in
a Basic only if there is none" (the 2025 Qiita studies, app v1.2.5)?

**Setup**: 50 Solo-battle starts, one screenshot of the opening hand each, in
`OneDrive\Desktop\Battle Logs\StartingBasicReview\` (20260922_183105 … 20260922_190348). The deck's QR screenshot
(20260922_182943) decodes with `lib/decode_qr.py` to exactly **2 Pokémon (2× Riolu B3 079) + 18 Trainers**, Fighting
Energy, no Fossils:
2 Riolu · 2 Poké Ball · Pokémon Flute · Lucky Ice Pop · Small Balloon · 2 Professor's Research · Cynthia · Copycat · Wally ·
2 Team Rocket's Researcher · 2 Team Rocket's Master Plan · Team Rocket's Boss · Mesagoza · Rainbow Cave · Arcade.

**Counting**: two independent Haiku passes (one on stacked sheets, one on single crops), then Claude viewed all 50 hands
directly. Final counts are Claude's. They match Haiku pass A exactly. Pass B had one false 2 (hand 10: the gold-frame
Rainbow Cave taken for a gold Riolu) and missed hand 14. Every hand had at least one Riolu, as the rule guarantees.
The Riolu here are the gold printing, so the reliable tells were the "Basic" label, the name and the cyan setup glow,
not the frame colour.

**Result: both Riolu in 3 of 50 hands (6%)** — hands 2, 4 and 14.

| Model | P(both Basics) | Expected in 50 | P(3 or fewer in 50) |
|---|---|---|---|
| Basic first, then 4 random (engine `unified1`) | 21.1% | 10.5 | **0.35%** — rejected |
| Redeal until a Basic appears | 11.8% | 5.9 | 14.5% |
| Deal 5, swap one for a Basic only if none (Qiita) | 5.3% | 2.6 | 73% — fits |

The swap-in model is ~83× likelier than Basic-first on this sample alone. Redeal isn't ruled out by 50 hands, but
machapin's 1,000-hand deck-1 result (62/1000, redeal p ≈ 5×10⁻⁸) is, and both samples agree with swap-in. Conclusion:
**the swap-in rule holds on the current app**, and the engine's Basic-first dealing (unified1) is wrong. Astra's
verified `0.1.0-pdl.rules1` build implements swap-in (`09`).

| Hand | Screenshot | Riolu |
|---|---|---|
| 1 | `20260922_183105000_iOS.png` | 1 |
| 2 | `20260922_183151000_iOS.png` | 2 |
| 3 | `20260922_183221000_iOS.png` | 1 |
| 4 | `20260922_183255000_iOS.png` | 2 |
| 5 | `20260922_183327000_iOS.png` | 1 |
| 6 | `20260922_183357000_iOS.png` | 1 |
| 7 | `20260922_183435000_iOS.png` | 1 |
| 8 | `20260922_183508000_iOS.png` | 1 |
| 9 | `20260922_183538000_iOS.png` | 1 |
| 10 | `20260922_183614000_iOS.png` | 1 |
| 11 | `20260922_183645000_iOS.png` | 1 |
| 12 | `20260922_183724000_iOS.png` | 1 |
| 13 | `20260922_183800000_iOS.png` | 1 |
| 14 | `20260922_183835000_iOS.png` | 2 |
| 15 | `20260922_183922000_iOS.png` | 1 |
| 16 | `20260922_183957000_iOS.png` | 1 |
| 17 | `20260922_184034000_iOS.png` | 1 |
| 18 | `20260922_184120000_iOS.png` | 1 |
| 19 | `20260922_184153000_iOS.png` | 1 |
| 20 | `20260922_184230000_iOS.png` | 1 |
| 21 | `20260922_184305000_iOS.png` | 1 |
| 22 | `20260922_184358000_iOS.png` | 1 |
| 23 | `20260922_184446000_iOS.png` | 1 |
| 24 | `20260922_184526000_iOS.png` | 1 |
| 25 | `20260922_184605000_iOS.png` | 1 |
| 26 | `20260922_184648000_iOS.png` | 1 |
| 27 | `20260922_184745000_iOS.png` | 1 |
| 28 | `20260922_184835000_iOS.png` | 1 |
| 29 | `20260922_184910000_iOS.png` | 1 |
| 30 | `20260922_184945000_iOS.png` | 1 |
| 31 | `20260922_185031000_iOS.png` | 1 |
| 32 | `20260922_185114000_iOS.png` | 1 |
| 33 | `20260922_185149000_iOS.png` | 1 |
| 34 | `20260922_185227000_iOS.png` | 1 |
| 35 | `20260922_185307000_iOS.png` | 1 |
| 36 | `20260922_185349000_iOS.png` | 1 |
| 37 | `20260922_185431000_iOS.png` | 1 |
| 38 | `20260922_185505000_iOS.png` | 1 |
| 39 | `20260922_185542000_iOS.png` | 1 |
| 40 | `20260922_185630000_iOS.png` | 1 |
| 41 | `20260922_185739000_iOS.png` | 1 |
| 42 | `20260922_185827000_iOS.png` | 1 |
| 43 | `20260922_185909000_iOS.png` | 1 |
| 44 | `20260922_185944000_iOS.png` | 1 |
| 45 | `20260922_190019000_iOS.png` | 1 |
| 46 | `20260922_190106000_iOS.png` | 1 |
| 47 | `20260922_190142000_iOS.png` | 1 |
| 48 | `20260922_190228000_iOS.png` | 1 |
| 49 | `20260922_190305000_iOS.png` | 1 |
| 50 | `20260922_190348000_iOS.png` | 1 |

# T10 — two Stadiums in one turn (Dustin's test, 2026-09-22)

Video `OneDrive\Desktop\Battle Logs\T10-stadiums.MP4` (22 s). With Mesagoza already played that turn, trying to play
Arcade shows the red banner **"You can't use any more Stadium cards this turn"** (≈18.5–20.5 s; read by OCR on frames
at 2 fps and checked by Claude on one frame). Every Stadium card's green rules box (visible on the enlarged Arcade)
reads: "You may play only 1 Stadium card during your turn. Put it next to the Active Spot, and discard it if another
Stadium comes into play. A Stadium with the same name can't be played." → one Stadium **play** per turn is
[OFFICIAL] (printed rules text) + [OBSERVED]. Engine `unified1` had no such limit (`07` M6); repaired in the
verified `0.1.0-pdl.rules1` build (`09`).
