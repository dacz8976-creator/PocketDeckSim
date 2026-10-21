#!/usr/bin/env python3
"""Model providers for the judge. The PROMPT is provider-independent (judge.render_prompt, frozen: fingerprint 0cb24215...); a provider only carries the same system and
user text to a model and brings back (text, usage, seconds, model, extra) in the one shape judge.judge_one expects:

    usage = {'input_tokens', 'output_tokens' (everything billed as output, thinking included), ...}
    extra = {'stop_reason': 'end_turn' for an answer that finished, anything else for one that did not, 'content_types': [...]}

Anthropic (Messages API) lives in judge.call_claude and is unchanged. This module adds Google Gemini (frozen-5): `gemini-4-argon` through the Interactions API.

Sources (read on 2026-10-21; Google's own pages, not memory):
  model id, status, token limits: https://ai.google.dev/gemini-api/docs/models  (and .../models/gemini-4-argon): `gemini-4-argon`, Stable, thinking low / medium / high,
      65,536 output tokens synchronous, context window 1,048,576
  price: https://ai.google.dev/gemini-api/docs/pricing : Standard $2.00 / 1M input and $10.00 / 1M output "including thinking tokens" through 2026-11-30, then $4.00 / $20.00
      from 2026-12-01; no prompt-length tiers listed; not on the free tier (Batch / Flex / Priority / Contributor are other tiers: not used here)
  thinking: https://ai.google.dev/gemini-api/docs/thinking : generation_config.thinking_level low | medium | high (default medium); max_output_tokens is "the combined total of
      thinking tokens and output tokens"; thinking tokens are billed as output; a run that hits the limit during reasoning ends with status "incomplete"
  request / response: https://ai.google.dev/gemini-api/docs/interactions and https://ai.google.dev/api/interactions-api : POST https://generativelanguage.googleapis.com/v1beta/interactions,
      header x-goog-api-key, body {model, input, system_instruction (a string), generation_config {max_output_tokens, thinking_level, thinking_summaries: auto | none, ...}, store};
      the answer is in steps[].content[].text of the step type "model_output"; usage {total_input_tokens, total_output_tokens, total_thought_tokens, total_tokens, total_cached_tokens ...}
  Not documented there (so NOT sent): a temperature setting for this model. The frozen temperature is "not set", as for Anthropic.
"""
import datetime
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

GEMINI_ENDPOINT = 'https://generativelanguage.googleapis.com/v1beta/interactions'
GEMINI_KEY_VAR = 'GEMINI_API_KEY'

# The frozen judge settings of frozen-5. Recorded in FROZEN.json ("judge") and checked row by row by `compare`; the 8,000-token cap is the Anthropic freeze's, and for Gemini it
# covers thinking + answer together (documented), at the highest thinking level the model offers.
GEMINI_FROZEN = {'provider': 'gemini', 'model': 'gemini-4-argon', 'max_tokens': 8000, 'temperature': None, 'thinking_level': 'high', 'thinking_summaries': 'none'}
GEMINI_MODELS = {'gemini-4-argon'}

# USD per million tokens (input, output incl. thinking). ACTUAL = the price in force; RESERVE = the higher price (a conservative price for the budget's worst-case reservation).
GEMINI_PRICE_INTRO = (2.0, 10.0)
GEMINI_PRICE_STANDARD = (4.0, 20.0)
GEMINI_INTRO_LAST_DAY = datetime.date(2026, 11, 30)
GEMINI_PRICE_NOTE = ('Gemini 4 Argon Standard tier, ai.google.dev/gemini-api/docs/pricing (read 2026-10-21): $2 / $10 per 1M input / output tokens (thinking billed as output) through 2026-11-30, '
                     '$4 / $20 from 2026-12-01; input charged in full (the implicit-cache discount is ignored: a conservative upper bound)')


GEMINI_SOURCES = ['https://ai.google.dev/gemini-api/docs/models', 'https://ai.google.dev/gemini-api/docs/pricing', 'https://ai.google.dev/gemini-api/docs/thinking',
                  'https://ai.google.dev/gemini-api/docs/interactions', 'https://ai.google.dev/api/interactions-api']

# How each frozen-4 (Anthropic) judge setting maps to Gemini, and what cannot match. Recorded in FROZEN.json.
GEMINI_MAPPING = {
    'prompt': 'identical: the frozen system text goes in `system_instruction`, the user text in `input`; the prompt fingerprint and every row\'s prompt_sha256 are the same as for the Anthropic judge',
    'output cap': 'max_tokens 8000 -> generation_config.max_output_tokens 8000; for Gemini it is documented as thinking + answer together, as the Anthropic cap was (reasoning counted as output). '
                  'CANNOT MATCH: tokenizers differ, so 8,000 Gemini tokens is not 8,000 Claude tokens, and at high thinking the model may spend the cap on thinking; such a reply is status '
                  '"incomplete" and fails exactly like a reply cut at max_tokens (no retry, no choice kept)',
    'reasoning': 'Anthropic: the model\'s default reasoning, no setting. Gemini: generation_config.thinking_level "high" (the highest of low / medium / high; the coordinator\'s pre-registered choice). '
                 'CANNOT MATCH: the two are different mechanisms; "high" is the closest to "as much reasoning as the model will do"',
    'thought text': 'generation_config.thinking_summaries "none": no thought summary is requested, so none is billed beyond the thinking tokens, and none could enter the stored reply (`raw` is model_output text only)',
    'temperature': 'not set for either (the provider default); Gemini 4 Argon documents no temperature setting, so none is sent and --temperature is refused',
    'other sampling': 'top_p, top_k, seed, stop sequences: not set',
    'retries': 'none: one request per call; a failed request is a failed call (the budget wrapper charges its full worst case and the batch is incomplete)',
    'streaming': 'none: one synchronous request; the 65,536 synchronous output limit is above the 8,000 cap',
    'storage': 'store false: Google keeps no interaction',
    'price': 'USD per 1M tokens, input / output including thinking: 2 / 10 through 2026-11-30, 4 / 20 from 2026-12-01 (Standard tier); the budget reserves every call at 4 / 20; the cached-input discount is ignored',
    'finish': 'stop_reason is "end_turn" only for status "completed"; anything else ("incomplete", "failed", "cancelled", ...) is stored as "gemini:<status>" and is never an intact answer',
}


def gemini_price(today=None):
    """The (input, output) price per million tokens in force on `today`."""
    today = today or datetime.date.today()
    return GEMINI_PRICE_INTRO if today <= GEMINI_INTRO_LAST_DAY else GEMINI_PRICE_STANDARD


def gemini_reserve_price():
    """The price a call's worst case is reserved at: the higher of the two published prices, whatever the date."""
    return GEMINI_PRICE_STANDARD


# ---------------------------------------------------------------------------------------------------------------------------------- the key
def parse_export_value(raw):
    """The value of a shell `export NAME=value` line: a quoted value up to its closing quote, an unquoted one up to the first blank or # (a trailing comment is not part of it)."""
    raw = raw.strip()
    if raw[:1] in ('"', "'"):
        end = raw.find(raw[0], 1)
        return raw[1:end] if end > 0 else raw[1:]
    return re.split(r'\s|#', raw, maxsplit=1)[0]


def load_key(var=GEMINI_KEY_VAR):
    """The key: the environment first, else the LAST `export VAR=...` line of ~/.bashrc (read as text and parsed; never executed, never printed, never stored). Exits with a message
    that names the variable and never the value."""
    k = os.environ.get(var)
    if k:
        return k
    bashrc = os.path.expanduser('~/.bashrc')
    if os.path.exists(bashrc):
        last = None
        with open(bashrc, encoding='utf-8', errors='replace') as f:
            for line in f:
                m = re.match(r'\s*export\s+' + re.escape(var) + r'=(.+)$', line.strip())
                if m:
                    last = parse_export_value(m.group(1))
        if last:
            return last
    sys.exit(f'no {var} (environment or ~/.bashrc)')


def scrub(text, key):
    """A message that may be shown or stored, without the key (and without anything that looks like one)."""
    text = str(text)
    if key:
        text = text.replace(key, '***')
    return re.sub(r'AIza[0-9A-Za-z_\-]{20,}', '***', text)


# ---------------------------------------------------------------------------------------------------------------------------------- Gemini
def build_gemini_request(system, user, model, max_tokens, thinking):
    """The JSON body of one Interactions request. Exactly the frozen prompt: `system` is the system instruction, `user` the input text. No temperature (not documented for this
    model; the frozen value is 'not set'); store false (no interaction is kept on Google's side)."""
    return {'model': model, 'input': user, 'system_instruction': system, 'store': False,
            'generation_config': {'max_output_tokens': max_tokens, 'thinking_level': thinking['thinking_level'], 'thinking_summaries': thinking['thinking_summaries']}}


def parse_interaction(j, model):
    """(text, usage, model_used, extra) from an Interaction resource. Only `model_output` text counts as the answer (thought summaries are never part of it). A reply that is
    not status "completed" is not an answer that finished: stop_reason says so ('gemini:<status>'). Usage: input_tokens = total_input_tokens (cached input is NOT discounted),
    output_tokens = everything billed as output = total_tokens - total_input_tokens when the response gives a total (it does not matter whether total_output_tokens already
    holds the thinking), else total_output_tokens + total_thought_tokens; a usage block that is missing sets usage_missing."""
    texts, types = [], []
    steps = j.get('steps')
    if isinstance(steps, list):
        for s in steps:
            if not isinstance(s, dict):
                continue
            types.append(s.get('type'))
            if s.get('type') == 'model_output':
                content = s.get('content')
                if isinstance(content, str):
                    texts.append(content)
                for c in content if isinstance(content, list) else []:
                    if isinstance(c, dict) and c.get('type') == 'text' and isinstance(c.get('text'), str):
                        texts.append(c['text'])
    else:  # the earlier beta shape: a flat list of outputs
        for o in j.get('outputs') or []:
            if isinstance(o, dict):
                types.append(o.get('type'))
                if o.get('type') == 'text' and isinstance(o.get('text'), str):
                    texts.append(o['text'])
    u = j.get('usage') if isinstance(j.get('usage'), dict) else {}
    tin, tout, tth, total = u.get('total_input_tokens'), u.get('total_output_tokens'), u.get('total_thought_tokens'), u.get('total_tokens')
    missing = tin is None or (tout is None and tth is None)
    billed_out = (tout or 0) + (tth or 0)
    if isinstance(total, int) and isinstance(tin, int) and (tout or 0) <= total - tin:  # the provider's own total says what was billed as output (answer + thinking), whichever way the parts are split
        billed_out = total - tin
    usage = {'input_tokens': tin, 'output_tokens': billed_out, 'thought_tokens': tth or 0, 'answer_tokens': tout or 0, 'cached_tokens': u.get('total_cached_tokens') or 0, 'total_tokens': total}
    status = j.get('status')
    extra = {'stop_reason': 'end_turn' if status == 'completed' else f'gemini:{status}', 'content_types': types, 'status': status, 'usage_missing': missing}
    if j.get('errors'):
        extra['errors'] = j['errors']
    return ''.join(texts), usage, j.get('model', model), extra


def _post_json(url, headers, body, timeout):
    req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), method='POST', headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def call_gemini(system, user, model=GEMINI_FROZEN['model'], max_tokens=GEMINI_FROZEN['max_tokens'], temperature=None, thinking=None, timeout=300):
    """One Interactions API call: one request, no retry (a failed call is a failed call). Returns (text, usage, seconds, model, extra) like judge.call_claude."""
    if temperature is not None:
        raise ValueError('temperature is not a documented setting of gemini-4-argon: the frozen judge sets none')
    thinking = thinking or {k: GEMINI_FROZEN[k] for k in ('thinking_level', 'thinking_summaries')}
    key = load_key()
    headers = {'x-goog-api-key': key, 'content-type': 'application/json'}
    t0 = time.time()
    try:
        j = _post_json(GEMINI_ENDPOINT, headers, build_gemini_request(system, user, model, max_tokens, thinking), timeout)
    except urllib.error.HTTPError as e:
        sys.exit(f'API error {e.code}: {scrub(e.read().decode("utf-8", "replace")[:500], key)}')
    except urllib.error.URLError as e:
        sys.exit(f'API error (no answer): {scrub(e.reason, key)}')
    text, usage, model_used, extra = parse_interaction(j, model)
    return text, usage, round(time.time() - t0, 2), model_used, extra
