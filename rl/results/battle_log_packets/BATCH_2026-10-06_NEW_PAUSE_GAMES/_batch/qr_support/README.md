# Retained QR decoding support, October 6, 2026

Scope: new October 4 through 6 Pause Games uploads only. This support packet has not opened any source video, claimed review work, registered an event, moved media, or changed simulator files.

Supply a retained native-resolution PNG frame, preferably with the whole deck-sharing screen. A lossless native crop around the QR plus its white margin also works. Keep the full source frame, its source-local seconds, original video basename and lead-verified source SHA-256. Do not resize a contact sheet or thumbnail to create evidence. JPEG is accepted by the reader but PNG avoids additional compression. If possible retain the deck label alongside the full frame.

The helper first scans the native image or explicitly supplied native crop with ZXing-C++. On failure it reuses the existing `Pocket Deck Lab/lib/decode_qr.py` image reader, including its phone-screen crop and bounded dotted-module variants. That fallback assumes the game's portrait screenshot layout: x=17% to 83%, y=45% to 77%. It is not suitable for arbitrary montage layouts. Supply a clearer retained crop if the read fails. Multiple detected codes are rejected instead of choosing a deck arbitrarily.

The helper calls the pinned `third_party/s216/tcgp-deck-qr-102d75e/src/payload.js` directly. It retains the original Base64 payload, the trainer and Pokemon entity ID arrays including duplicate slots, the Energy array in payload order, image/source binding and decoder/catalog hashes. It requires exactly 20 card slots, reports unknown entities and lists possible printing aliases without selecting a filmed printing. Unknown Energy bytes remain raw and receive an explicit round-trip limitation.

The repository's `s216_card_catalog_v1.json` provides the accepted local entity crosswalk. Its upstream card list is the pinned community database `pokemon-tcg-pocket-database-2.10.0`, as explicitly recorded in `third_party/s216/SOURCES.json`. No complete official local card-text export was found in the inspected catalog inputs. Do not describe this crosswalk as official game certification. Unknown or conflicting entities stay unresolved.

QR codes carry semantic playable card identity, not exact artwork, rarity or owned printing. A valid QR establishes the displayed deck code. It does not establish an opening hand, a hidden draw or that the deck was used in every match. The Pause Games protocol still requires its separately dated external log snapshot and per-game DECK_USED.json. Keep any conflict between that snapshot and the filmed QR explicit.

The older Python decoder's displayed Energy labels are stale. The pinned codec maps 1 Grass, 2 Fire, 3 Water, 4 Lightning, 5 Psychic, 6 Fighting, 7 Darkness, 8 Metal, 10 Dragon and 11 Colorless. It has no known label for 9. The helper uses the pinned codec's labels and records whether each value is selectable in the ordinary editor.

Run from PowerShell:

```powershell
$qrSupport = 'C:\Users\dacz8\OneDrive\Desktop\Battle Logs\Recording_QA\BATCH_2026-10-06_NEW_PAUSE_GAMES\qr_support'
$qrPython = 'C:\Users\dacz8\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $qrPython "$qrSupport\decode_retained_qr.py" 'C:\absolute\retained_native_frame.png' --source-video 'EXACT_BASENAME.MP4' --seconds 123.4 --source-sha256 'LEAD_VERIFIED_SHA256' --out "$qrSupport\EXACT_BASENAME_QR_123.4.json"
```

For a whole frame with a known QR rectangle, add `--crop X1 Y1 X2 Y2` in native pixels. The receipt preserves the supplied rectangle and original image dimensions/hash. The output path must be new; the helper refuses to overwrite a prior receipt. Omit `--source-sha256` only when the lead has not supplied it; the missing value stays null and needs later source binding. Do not use a fabricated hash or time.

The scoped `deps` directory contains ZXing-C++ 3.1.1 and OpenCV headless 5.0.0.93, installed without modifying the shared Python runtime. Its bundled NumPy and Pillow remain in the approved runtime. To recreate these scoped dependencies:

```powershell
& $qrPython -m pip install --target "$qrSupport\deps" --no-deps zxing-cpp==3.1.1 opencv-python-headless==5.0.0.93
```

Verification: all eight pinned codec tests passed. `verification/synthetic_known_payload.png` was generated from the codec's known 20-card Lightning fixture, read by the helper, mapped to 20 resolved semantic card slots and re-encoded byte-exactly. `verification/synthetic_decode.json` records that synthetic fixture and explicitly names it as non-media. This checks the integration, not the readability of new video QR frames or the dotted-code fallback on this batch. Those checks await retained images from the lead.
