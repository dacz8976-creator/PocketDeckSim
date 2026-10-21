#!/usr/bin/env python3
"""DESCRIPTIVE only (PREREG_RUN2 section 5): run 2's judge (Gemini 4 Argon, frozen-7) against run 1's judge (claude-sonnet-5-5, frozen-4) on the 49
primary points, from each run's formal report (the judge's primary call, prefix agreement). No interval, no p-value, no verdict.
usage: desc_vs_run1.py RUN2_REPORT RUN1_REPORT ELIGIBILITY OUT"""
import json, sys

r2_path, r1_path, elig_path, out_path = sys.argv[1:5]
primary = json.load(open(elig_path))['primary_ids']


def judge_rows(path):
    rep = json.load(open(path))
    out = {}
    for row in rep['rows']:
        if row.get('bot') == 'judge' and str(row.get('run')) in ('0', 'None'):
            out[row['position']] = row
    return out


def km3_mean(path):
    rep = json.load(open(path))
    per = {}
    for row in rep['rows']:
        if row.get('bot') == 'km3':
            per.setdefault(row['position'], []).append(1.0 if row.get('agrees') else 0.0)
    return {p: sum(v) / len(v) for p, v in per.items()}


g, s = judge_rows(r2_path), judge_rows(r1_path)
missing = [p for p in primary if p not in g or p not in s]
if missing:
    sys.exit(f'primary points without a judge row in one report: {missing}')
ga = {p: bool(g[p].get('agrees')) for p in primary}
sa = {p: bool(s[p].get('agrees')) for p in primary}
no_choice = [p for p in primary if g[p].get('state') != 'ok' or g[p].get('plan_number') is None]
both = [p for p in primary if ga[p] and sa[p]]
g_only = [p for p in primary if ga[p] and not sa[p]]
s_only = [p for p in primary if sa[p] and not ga[p]]
neither = [p for p in primary if not ga[p] and not sa[p]]
km3 = km3_mean(r2_path)
res = {
    'what': 'DESCRIPTIVE only: Gemini 4 Argon (run 2, frozen-7) v claude-sonnet-5-5 (run 1, frozen-4), prefix agreement of the primary judge call on the 49 '
            'primary points; no interval, no p-value, no verdict (PREREG_RUN2 section 5)',
    'n_points': len(primary),
    'gemini_agrees': sum(ga.values()), 'sonnet_run1_agrees': sum(sa.values()),
    'km3_mean_agrees': round(sum(km3.get(p, 0.0) for p in primary), 4),
    'paired_difference_gemini_minus_sonnet': round((sum(ga.values()) - sum(sa.values())) / len(primary), 4),
    'both_agree': len(both), 'gemini_only': len(g_only), 'sonnet_only': len(s_only), 'neither': len(neither),
    'gemini_no_choice_rows': len(no_choice),
    'points_gemini_only': g_only, 'points_sonnet_only': s_only, 'points_gemini_no_choice': no_choice,
}
json.dump(res, open(out_path, 'w'), indent=1)
print(f"Gemini v run 1's Sonnet (descriptive): Gemini {res['gemini_agrees']}/{len(primary)}, Sonnet {res['sonnet_run1_agrees']}/{len(primary)}, "
      f"km3 mean {res['km3_mean_agrees']}/{len(primary)}; both {len(both)}, Gemini only {len(g_only)}, Sonnet only {len(s_only)}, neither {len(neither)}; "
      f"Gemini rows without a choice {len(no_choice)}")
