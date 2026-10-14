"""page.py: the HTML of the ladder deck codes page, from build.py's results. One self-contained file: the QR codes are inline SVG, nothing is fetched except the fonts."""
import html

H = html.escape

STYLE = """
/* Layout: an index of the seven decks first, then one panel per deck: its QR code on a white tile, the 20 cards beside it, the checks underneath. */
:root {
  --bg: #edf0f3; --surface: #ffffff; --ink: #15202b; --muted: #546372; --line: #d6dce3; --soft: #f4f6f8;
  --accent: #0b7a62; --accent-ink: #ffffff; --bad: #b3261e;
  --e-grass: #2f8f46; --e-fire: #d2561d; --e-water: #1f78c1; --e-lightning: #d9a400; --e-psychic: #9a4fb8; --e-fighting: #a8553a; --e-darkness: #5a4a8e; --e-metal: #6f7c8a;
  --qr-bg: #ffffff; --qr-fg: #000000;
  --font-display: "Bricolage Grotesque", "Segoe UI", system-ui, sans-serif;
  --font-body: "Atkinson Hyperlegible", "Segoe UI", system-ui, sans-serif;
  --font-mono: "IBM Plex Mono", ui-monospace, "Cascadia Mono", Consolas, monospace;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #10161b; --surface: #182027; --ink: #e8eef3; --muted: #9aaab8; --line: #2a3640; --soft: #1e2831;
    --accent: #4fc9a6; --accent-ink: #08221b; --bad: #ff8a80;
    --e-grass: #5fc277; --e-fire: #f08a55; --e-water: #62aef0; --e-lightning: #f0c93a; --e-psychic: #c98be0; --e-fighting: #d68a6e; --e-darkness: #9c8bd6; --e-metal: #a3b0bd;
    color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --bg: #10161b; --surface: #182027; --ink: #e8eef3; --muted: #9aaab8; --line: #2a3640; --soft: #1e2831;
  --accent: #4fc9a6; --accent-ink: #08221b; --bad: #ff8a80;
  --e-grass: #5fc277; --e-fire: #f08a55; --e-water: #62aef0; --e-lightning: #f0c93a; --e-psychic: #c98be0; --e-fighting: #d68a6e; --e-darkness: #9c8bd6; --e-metal: #a3b0bd;
  color-scheme: dark;
}
* { box-sizing: border-box; }
body { background: var(--bg); color: var(--ink); font-family: var(--font-body); font-size: 1rem; line-height: 1.5; padding-inline: 1rem; padding-block: 1.5rem 3rem; }
main { max-width: 64rem; margin-inline: auto; display: flex; flex-direction: column; gap: 2rem; }
h1, h2, h3 { font-family: var(--font-display); text-wrap: balance; margin: 0; line-height: 1.15; }
h1 { font-size: clamp(1.9rem, 5vw, 2.7rem); font-weight: 750; letter-spacing: -0.01em; }
h2 { font-size: 1.25rem; font-weight: 700; }
h3 { font-size: 1.05rem; font-weight: 650; }
p { margin: 0; }
.lede { max-width: 42rem; color: var(--muted); }
.label { font-size: 0.78rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); }
header { display: flex; flex-direction: column; gap: 0.6rem; }
code, .mono { font-family: var(--font-mono); font-size: 0.82rem; }
a { color: var(--accent); }
:focus-visible { outline: 3px solid var(--accent); outline-offset: 2px; border-radius: 4px; }

.index { background: var(--surface); border: 1px solid var(--line); border-radius: 0.6rem; overflow-x: auto; }
.index table { border-collapse: collapse; width: 100%; min-width: 34rem; }
.index th, .index td { text-align: left; padding: 0.6rem 0.9rem; border-bottom: 1px solid var(--line); vertical-align: baseline; }
.index tr:last-child td { border-bottom: 0; }
.index th { font-size: 0.78rem; letter-spacing: 0.06em; text-transform: uppercase; color: var(--muted); font-weight: 700; background: var(--soft); }
.index td:first-child { white-space: nowrap; }
.index .grp td { background: var(--soft); font-size: 0.78rem; letter-spacing: 0.08em; text-transform: uppercase; font-weight: 700; color: var(--muted); padding-block: 0.4rem; }
.status { white-space: nowrap; font-weight: 700; color: var(--accent); }
.status.bad { color: var(--bad); }

section.group { display: flex; flex-direction: column; gap: 1.25rem; }
.deck { background: var(--surface); border: 1px solid var(--line); border-radius: 0.8rem; padding: 1.1rem; display: grid; grid-template-columns: minmax(0, 17.5rem) minmax(0, 1fr); gap: 1.4rem; scroll-margin-top: 1rem; }
.qrcol { display: flex; flex-direction: column; gap: 0.7rem; min-width: 0; }
.qrtile { background: var(--qr-bg); border: 1px solid var(--line); border-radius: 0.5rem; padding: 0.5rem; }
.qr { display: block; width: 100%; height: auto; }
.qr rect { fill: var(--qr-bg); }
.qr path { fill: var(--qr-fg); }
.buttons { display: flex; gap: 0.5rem; flex-wrap: wrap; align-items: center; }
button { font: inherit; font-weight: 700; background: var(--accent); color: var(--accent-ink); border: 0; border-radius: 0.45rem; padding: 0.5rem 0.9rem; cursor: pointer; }
button:hover { filter: brightness(1.08); }
.codetext { display: block; word-break: break-all; background: var(--soft); border: 1px solid var(--line); border-radius: 0.4rem; padding: 0.5rem 0.6rem; margin-top: 0.4rem; user-select: all; }
details > summary { cursor: pointer; color: var(--muted); font-size: 0.9rem; }
.info { display: flex; flex-direction: column; gap: 0.9rem; min-width: 0; }
.titlebar { display: flex; flex-direction: column; gap: 0.2rem; }
.blurb { color: var(--muted); max-width: 40rem; }
.chips { display: flex; flex-wrap: wrap; gap: 0.5rem; align-items: center; }
.chip { display: inline-flex; align-items: center; gap: 0.4rem; border: 1px solid var(--line); background: var(--soft); border-radius: 999px; padding: 0.15rem 0.7rem 0.15rem 0.55rem; font-size: 0.9rem; }
.dot { width: 0.7rem; height: 0.7rem; border-radius: 50%; background: var(--muted); }
.dot.Grass { background: var(--e-grass); } .dot.Fire { background: var(--e-fire); } .dot.Water { background: var(--e-water); } .dot.Lightning { background: var(--e-lightning); }
.dot.Psychic { background: var(--e-psychic); } .dot.Fighting { background: var(--e-fighting); } .dot.Darkness { background: var(--e-darkness); } .dot.Metal { background: var(--e-metal); }
.lists { display: grid; grid-template-columns: repeat(auto-fit, minmax(14.5rem, 1fr)); gap: 1rem 1.4rem; }
.list { display: flex; flex-direction: column; gap: 0.3rem; min-width: 0; }
.list ul { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; }
.list li { display: grid; grid-template-columns: 1.6rem minmax(0, 1fr) auto; gap: 0.5rem; align-items: baseline; padding-block: 0.22rem; border-bottom: 1px dotted var(--line); }
.list li:last-child { border-bottom: 0; }
.n { font-family: var(--font-mono); font-weight: 500; text-align: right; font-variant-numeric: tabular-nums; }
.pid { font-family: var(--font-mono); font-size: 0.78rem; color: var(--muted); white-space: nowrap; }
.verdict { border-top: 1px solid var(--line); padding-top: 0.8rem; display: flex; flex-direction: column; gap: 0.35rem; }
.verdict .head { font-weight: 700; color: var(--accent); }
.verdict .head.bad { color: var(--bad); }
.verdict ul { margin: 0.3rem 0 0; padding-left: 1.2rem; display: flex; flex-direction: column; gap: 0.2rem; }
.verdict li.bad { color: var(--bad); font-weight: 700; }
.src { font-size: 0.85rem; color: var(--muted); }
footer { color: var(--muted); font-size: 0.9rem; display: flex; flex-direction: column; gap: 0.4rem; max-width: 46rem; }
@media (max-width: 720px) {
  .deck { grid-template-columns: minmax(0, 1fr); }
  .qrcol { max-width: 20rem; }
}
@media (prefers-reduced-motion: reduce) { * { scroll-behavior: auto !important; transition: none !important; } }
"""

SCRIPT = """
document.addEventListener('click', function (e) {
  var b = e.target.closest('[data-copy]');
  if (!b) return;
  var old = b.textContent;
  function done() { b.textContent = 'Copied'; setTimeout(function () { b.textContent = old; }, 1600); }
  function fallback() {
    var deck = b.closest('.deck');
    var det = deck.querySelector('details.codebox');
    if (det) det.open = true;
    var t = deck.querySelector('.codetext');
    var r = document.createRange(); r.selectNodeContents(t);
    var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
    b.textContent = 'Code selected';
    setTimeout(function () { b.textContent = old; }, 2200);
  }
  try { navigator.clipboard.writeText(b.getAttribute('data-copy')).then(done, fallback); } catch (err) { fallback(); }
});
"""


def verdict_words(c):
    extra = '; '.join(f'{H(k)}: {a} here, {b} there' for k, (a, b) in c['diff'].items())
    if c['verdict'] == 'same code':
        return 'same code'
    if c['verdict'] == 'same cards, other order':
        return 'same 20 cards, written in another order (a different string for the same deck)'
    if c['verdict'] == 'unreadable':
        return 'the image could not be read'
    return 'a different list' + (f' ({extra})' if extra else '') + ('; different Energy' if c['energy_differs'] else '')


def card_list(title, cards):
    n = sum(c['n'] for c in cards)
    rows = ''.join(f'<li><span class="n">{c["n"]}</span><span>{H(c["name"])}</span><span class="pid">{H(c["id"])}</span></li>' for c in cards)
    return f'<div class="list"><span class="label">{title} · {n}</span><ul>{rows}</ul></div>'


def deck_panel(d):
    ok = all(c['ok'] for c in d['checks'])
    pk = [c for c in d['cards'] if c['kind'] == 'Pokémon']
    tr = [c for c in d['cards'] if c['kind'] == 'Trainer']
    chips = ''.join(f'<span class="chip"><span class="dot {H(e)}"></span>{H(e)} Energy</span>' for e in d['energy'])
    checks = ''.join(f'<li class="{"" if c["ok"] else "bad"}">{"" if c["ok"] else "FAILED: "}{H(c["name"])}</li>' for c in d['checks'])
    cmp_ = ''.join(f'<li>Compared with {H(c["what"])}: {verdict_words(c)}.</li>' for c in d['compared'])
    notes = ''.join(f'<li>{H(n)}</li>' for n in d['notes'])
    pnotes = ''
    if d['printing_notes']:
        pnotes = ('<li>The code names the card, not its printing, so any printing you own works. '
                  f'Where the deck file lists another printing than the one a decoder shows first: {H("; ".join(d["printing_notes"]))}.</li>')
    head = 'Checked: the code decodes to the same 20 cards as the deck file, and the QR reads back.' if ok else 'A check failed. Do not use this code.'
    return f'''<article class="deck" id="{H(d["key"])}">
  <div class="qrcol">
    <div class="qrtile">{d["svg"]}</div>
    <div class="buttons"><button type="button" data-copy="{H(d["code"])}">Copy code</button></div>
    <details class="codebox"><summary>Code text</summary><code class="codetext">{H(d["code"])}</code></details>
  </div>
  <div class="info">
    <div class="titlebar"><span class="label">{H(d["label"])}</span><h3>{H(d["title"])}</h3></div>
    <p class="blurb">{H(d["blurb"])}</p>
    <div class="chips">{chips}</div>
    <div class="lists">{card_list("Pokémon", pk)}{card_list("Trainers", tr)}</div>
    <div class="verdict">
      <span class="head{"" if ok else " bad"}">{head}</span>
      <details><summary>What was checked</summary><ul>{checks}{cmp_}{pnotes}{notes}</ul></details>
      <span class="src">Deck file <code>{H(d["file"])}</code>, SHA-256 <code>{H(d["sha256"][:16])}…</code>, the one in the slow report <code>{H(d["report"])}</code>.</span>
    </div>
  </div>
</article>'''


def index_rows(decks):
    rows, group = [], None
    for d in decks:
        if d['group'] != group:
            group = d['group']
            rows.append(f'<tr class="grp"><td colspan="4">{H(group)}</td></tr>')
        ok = all(c['ok'] for c in d['checks'])

        def short(c):
            return 'Pause Games' if c['what'].startswith('Pause Games') else 'the image'
        parts = []
        for verdict, words in (('same code', 'Same code as'), ('same cards, other order', 'Same cards, other order, as'), ('different', 'Different from'), ('unreadable', 'Unreadable:')):
            names = [short(c) for c in d['compared'] if c['verdict'] == verdict]
            if names:
                parts.append(f'{words} {" and ".join(dict.fromkeys(names))}')
        other = '; '.join(parts) or 'No existing code to compare'
        rows.append(f'<tr><td><a href="#{H(d["key"])}">{H(d["label"])}</a></td><td>{H(d["title"])}</td>'
                    f'<td class="status{"" if ok else " bad"}">{"✓ Checked" if ok else "FAILED"}</td><td>{H(other)}</td></tr>')
    return ''.join(rows)


def render(decks, commit):
    groups = []
    for g in dict.fromkeys(d['group'] for d in decks):
        title = 'Shortlist' if g == 'Shortlist' else 'Also tested'
        groups.append(f'<section class="group" aria-label="{H(title)}"><h2>{H(title)}</h2>' + ''.join(deck_panel(d) for d in decks if d['group'] == g) + '</section>')
    return f'''<title>Ladder Deck Codes</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Bricolage+Grotesque:opsz,wght@12..96,500..800&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>{STYLE}</style>
<main>
  <header>
    <span class="label">Ranked ladder sheet</span>
    <h1>Ladder deck codes</h1>
    <p class="lede">The in-game deck import code for each of the seven decks on the sheet, in the sheet's order. Every code was decoded again and compared card for card with the tested deck file.</p>
  </header>
  <div class="index"><table>
    <thead><tr><th>Deck</th><th>Name</th><th>Check</th><th>Existing codes</th></tr></thead>
    <tbody>{index_rows(decks)}</tbody>
  </table></div>
  {"".join(groups)}
  <footer>
    <p>The codes name each card and not a printing, so any printing you own satisfies them. They are in the game's format (the same builder as Season Brews and Pause Games, <code>lib/encode_qr.py</code>).</p>
    <p>Built from main {H(commit)} by <code>rl/results/ladder_qr_page_2026-10-14/build.py</code>. This page is separate from Pause Games and writes nothing to it.</p>
  </footer>
</main>
<script>{SCRIPT}</script>
'''
