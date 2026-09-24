# Rules3 pool benchmark

| k2 deck | k3 deck | k2 wins | k3 wins | k2−k3 (pts) | discordant k2/k3 | exact p |
|---|---|---:|---:|---:|---:|---:|
| blaziken | lucario | 443 | 474 | -3.1 | 86/117 | 0.034981 |
| lucario | blaziken | 448 | 525 | -7.7 | 77/154 | 4.5227e-07 |
| blaziken | weezing | 441 | 504 | -6.3 | 54/117 | 1.6396e-06 |
| weezing | blaziken | 393 | 488 | -9.5 | 39/134 | 2.1229e-13 |
| blaziken | altaria | 377 | 431 | -5.4 | 75/129 | 0.00019104 |
| altaria | blaziken | 534 | 568 | -3.4 | 103/137 | 0.032943 |
| blaziken | suicune | 460 | 543 | -8.3 | 51/134 | 8.66e-10 |
| suicune | blaziken | 382 | 456 | -7.4 | 31/105 | 1.3263e-10 |
| lucario | weezing | 453 | 531 | -7.8 | 64/142 | 5.6856e-08 |
| weezing | lucario | 368 | 469 | -10.1 | 55/156 | 2.1871e-12 |
| lucario | altaria | 410 | 449 | -3.9 | 72/111 | 0.0048325 |
| altaria | lucario | 528 | 551 | -2.3 | 93/116 | 0.12787 |
| lucario | suicune | 440 | 527 | -8.7 | 62/149 | 1.9094e-09 |
| suicune | lucario | 420 | 473 | -5.3 | 52/105 | 2.8231e-05 |
| weezing | altaria | 520 | 606 | -8.6 | 71/157 | 1.2278e-08 |
| altaria | weezing | 307 | 387 | -8.0 | 60/140 | 1.5071e-08 |
| weezing | suicune | 189 | 380 | -19.1 | 25/216 | 4.0317e-39 |
| suicune | weezing | 427 | 618 | -19.1 | 45/236 | 1.9883e-32 |
| altaria | suicune | 319 | 371 | -5.2 | 59/111 | 8.1525e-05 |
| suicune | altaria | 549 | 629 | -8.0 | 53/133 | 4.0261e-09 |

Per-deck mean k2-minus-k3 (points):
- blaziken: -5.8
- lucario: -7.0
- weezing: -11.8
- altaria: -4.7
- suicune: -10.0

Actual game rows: 30000. Raw rows are in `games.jsonl`; identity and task plan are frozen beside this report.
