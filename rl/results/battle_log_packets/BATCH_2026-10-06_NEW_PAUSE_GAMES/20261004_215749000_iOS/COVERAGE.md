# Coverage and acceptance checklist

Source:20261004_215749000_iOS.MP4,257.066667s, SHA-2562015607dfe613e8bf71f4637d5d26ed625d8a451b0541b93b3a82bf0457126af. Reviewer:/root/pause_20261004_215749000_iOS, gpt-6.1-sol, high. The frozen source, index, shared events and external logs were not changed by this worker.

## Available source coverage

| Interval | Phase | Review and evidence |
|---|---|---|
|0-7s|Deck QR and list|Native QR retained at1s, decoded20 functional slots, Fire. Film/live evolution-line conflict preserved.|
|7-28s|Online matchmaking and coin animation|Single opponent match found; no Auto seen.|
|28-52s|Opening and both-player setup|Five owner cards before Active placement at30s; Torchic selected31s; opponent Tinkatink/Rookidee revealed.|
|52-75s|Owner turn1|Normal Poké Ball, search Castform, Bench placement, Helmet, visible supporter warning and accepted End Turn.|
|75-103s|Opponent turn2|Normal hidden draw, Tinkatink Metal, Red Card replacement three draws, attack20 and Helmet20.|
|103-133s|Owner turn3|Normal Combusken, evolution, Research draws Torchic/Field Blower, Bench Torchic, Fire Active Combusken, pass.|
|133-165s|Opponent turn4|Normal hidden draw, Research, Bench Meltan, Potion, Metal Meltan, attack20 and Helmet20.|
|165-226s|Owner turn5 and resolution|Copycat draw, Research Combusken/Hiking Trail, evolution, Stadium, retreat, current Fire to Bench Combusken, Flame Patch to Castform, Sunny Scorching KO,1point, Meltan replacement, Trail draws Mega Blaziken ex.|
|226-245s|Opponent turn6|Hidden normal draw, Research, concession.|
|245-257.066667s|Result animation and victory|Castform animation, loading, Victory vs. Sherwin. No second match.|

The entire source was inspected using86 overview frames at3-second midpoint intervals, then111 native seeks concentrated on setup, every draw, boundary, rapid action and decisive resolution. Coarse sheets locate intervals; only native evidence supplies the mandatory hands. Retained action frames also reconcile before/after HP, Energy and point changes. No uncovered match phase or suspected recording cut remains. This describes meaningful gameplay coverage, not a claim of examining every video frame.

## Mandatory supplement

- Five opening slots and selected Active: complete, native30/31s.
- Three owner turns, draw-timed +1/+3/+6 candidates: retained. Dense55/106s selected where immediate first plays make scheduled offsets unsuitable;170s selected for turn5.
- Before-end hand/count:72s3,130s3,206s2 before attack;226s3 after the separate Stadium draw.
- Named owner normal draws: Poké Ball, Combusken, Copycat. Named search: Castform. Named Research draws: Torchic, Field Blower, Combusken, Hiking Trail. Red Card replacement: Flame Patch, Research, Research. Stadium draw: Mega Blaziken ex, with reveal-popup limitation.
- Numbered voluntary plays: all visible gameplay plays, retreat cost, both distinct Fire destinations and affirmative turn1 warning acceptance retained. No Copycat, Misty, other no-effect action or invented decline.
- Both boards at each boundary: explicit Active, ordered Bench slots including empty slots, HP/max/damage, Energy, Tools, conditions, Stadium, points, Energy Zone current and next.
- Opponent fan at each owner start: three directly counted backs at55/106/170s. Opponent identities remain hidden.
- Periodic discard snapshots: unavailable in source; neither pile opened. Every row carries an explicit no-view limit.
- Exact current20-card log snapshot: saved. Exact filmed20-slot functional QR: saved separately. Combusken2 versus RareCandy2 conflict prevents exact-current-list game binding.
- JSON ledger: six rows, one per recorded owner/opponent turn. Opening remains in PAUSE_GAME.json, not an invented turn0.
- Evidence: native1170x2532 full frames, full-width bottom fifth and top crops with saved bounds, source filenames and SHA binding.
- Source timing: all timestamps local to this single recording. Embedded recording time establishes local match date2026-10-04.

## Worker disposition

Full available battle review submitted for independent acceptance. Capture supplement:complete_with_recording_limits. Lead_checked:false. The lead must perform independent bounded source checks, then register and archive if accepted. No external game entry, shared index mutation or source move has been performed by this worker.
