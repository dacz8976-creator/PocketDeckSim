#!/usr/bin/env python3
"""Model providers for the judge. The PROMPT is provider-independent (judge.render_prompt, frozen: fingerprint 0cb24215...); a provider only carries the same system and
user text to a model and brings back (text, usage, seconds, model, extra) in the one shape judge.judge_one expects:

    usage = {'input_tokens', 'output_tokens' (everything billed as output, thinking included), ...}
    extra = {'stop_reason': 'end_turn' for an answer that finished, anything else for one that did not, 'content_types': [...]}

Anthropic (Messages API) lives in judge.call_claude and is unchanged. This module adds Google Gemini: `gemini-4-argon` through the Gemini Developer API's Interactions API
(provider "gemini", frozen-5) and through Vertex AI / Gemini Enterprise Agent Platform's GenerateContent API (provider "gemini-vertex", frozen-6 and -7: the free-trial credits pay
for this one, not for the Developer API; see FROZEN.md).

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

Vertex AI (read 2026-10-21, Google's own pages):
  model page: https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/4-argon : `gemini-4-argon` GA, location `global`, GenerateContent API supported (Interactions API
      only as a preview), thinking LOW / MEDIUM (default) / HIGH, custom temperature / top_p / top_k ignored, thinking_budget or MINIMAL is an HTTP 400
  guide: https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/guides/gemini-4-argon : generateContent REST with generationConfig.thinkingConfig.thinkingLevel;
      "65,536 output tokens, or 32,768 for non-streaming direct HTTP requests", output counted with thinking; finishReason STOP, MAX_TOKENS, CONTINUATION (long decode, v1beta1 only)
  key + URL: https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/start/api-keys?usertype=standard (a standard API key bound to a service account) and the API quickstart
      (models/start?usertype=apikey): POST https://aiplatform.googleapis.com/v1/publishers/google/models/MODEL:generateContent with no project or location in the path (frozen-6; it pins
      us-central1, where gemini-4-argon is not served: HTTP 404 NOT_FOUND on the live call). frozen-7 uses the project-scoped form of the model guide's REST example,
      /v1/projects/PROJECT/locations/global/publishers/google/models/MODEL:generateContent (the guide shows it with a Bearer token; a countTokens probe with the key and the header
      answered 200). The quickstart's curl passes the key as ?key=; the x-goog-api-key HEADER (used here, so the key is never in a URL) is documented by the express-mode REST reference
      (https://docs.cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/vertex-ai-express-mode-api-reference) and https://docs.cloud.google.com/docs/authentication/api-keys-use ;
      that a service-account-bound key accepts it is confirmed only by a live call
  price: the Google Cloud announcement https://cloud.google.com/blog/products/ai-machine-learning/gemini-4-argon-available-on-google-cloud : $2 / $10 per 1M input / output tokens through
      2026-11-30, then $4 / $20 (the Vertex pricing page's tables could not be read); that thinking tokens are billed as output is stated by the guide above ("every token the model
      processes is counted and billed, including thinking tokens") and by https://ai.google.dev/gemini-api/docs/pricing
  response fields: Vertex's own v1 reference, https://docs.cloud.google.com/vertex-ai/generative-ai/docs/reference/rest/v1/GenerateContentResponse (and .../Content, .../GenerationConfig):
      candidates[].content.parts[].text / thought, finishReason, usageMetadata.promptTokenCount / candidatesTokenCount / thoughtsTokenCount / totalTokenCount / cachedContentTokenCount,
      promptFeedback.blockReason. What it does NOT say: whether candidatesTokenCount includes the thoughts (the Developer API reference, https://ai.google.dev/api/generate-content, defines
      totalTokenCount as prompt + thoughts + candidates, so they are disjoint there) and whether promptTokenCount includes the cached tokens; _usage is right under either reading of the first
"""
import datetime
import http.client
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

# Vertex AI (frozen-6, frozen-7): the same model, GenerateContent API, a key in the x-goog-api-key header. maxOutputTokens 32,768 is the most a non-streaming direct HTTP call allows
# (documented), chosen so that high thinking does not use the cap up (a cut reply has no choice). The level is sent as written ("HIGH").
# frozen-7: the URL names the PROJECT and the LOCATION. The project-less URL of frozen-6 (the express-mode form) pins location us-central1, where gemini-4-argon is not served (the one
# smoke call of frozen-6 got HTTP 404 NOT_FOUND there); a countTokens probe on the project-scoped global URL with the same key and header answered 200 (Oct 21). The project id is not a
# secret: it comes from the VERTEX_PROJECT setting (environment, or the run kit's --vertex-project flag), is not stored in the freeze, and is recorded in every row.
VERTEX_URL = 'https://aiplatform.googleapis.com/v1/projects/{project}/locations/{location}/publishers/google/models/{model}:generateContent'
VERTEX_KEY_VAR = 'VERTEX_API_KEY'
VERTEX_PROJECT_VAR = 'VERTEX_PROJECT'
VERTEX_FROZEN = {'provider': 'gemini-vertex', 'model': 'gemini-4-argon', 'location': 'global', 'max_tokens': 32768, 'temperature': None, 'thinking_level': 'HIGH'}
_VERTEX_PROJECT = [None]  # a run kit's --vertex-project flag (set_vertex_project); the environment variable is the fallback
GEMINI_PROVIDERS = ('gemini', 'gemini-vertex')  # the two Gemini providers: same price table, same unfinished-reply rule (stop_reason 'end_turn' or 'gemini:<status>' / 'vertex:<reason>')

# USD per million tokens (input, output incl. thinking). ACTUAL = the price in force; RESERVE = the higher price (a conservative price for the budget's worst-case reservation).
GEMINI_PRICE_INTRO = (2.0, 10.0)
GEMINI_PRICE_STANDARD = (4.0, 20.0)
GEMINI_INTRO_LAST_DAY = datetime.date(2026, 11, 30)
GEMINI_PRICE_NOTE = ('Gemini 4 Argon Standard tier, ai.google.dev/gemini-api/docs/pricing (read 2026-10-21): $2 / $10 per 1M input / output tokens (thinking billed as output) through 2026-11-30, '
                     '$4 / $20 from 2026-12-01; input charged in full (the implicit-cache discount is ignored: a conservative upper bound)')
VERTEX_PRICE_NOTE = ('Gemini 4 Argon on Vertex AI (Gemini Enterprise Agent Platform): $2 / $10 per 1M input / output tokens through 2026-11-30, $4 / $20 from 2026-12-01, per the Google Cloud '
                     'announcement cloud.google.com/blog/products/ai-machine-learning/gemini-4-argon-available-on-google-cloud (read 2026-10-21; the Vertex pricing page tables could not be read, so '
                     'verify in the billing console); thinking tokens are billed as output (the model guide: every token processed is billed, thinking included; ai.google.dev/gemini-api/docs/pricing); '
                     'input charged in full (the cached-input discount is ignored: a conservative upper bound)')


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


VERTEX_SOURCES = ['https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/4-argon', 'https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/guides/gemini-4-argon',
                  'https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/start/api-keys?usertype=standard', 'https://cloud.google.com/blog/products/ai-machine-learning/gemini-4-argon-available-on-google-cloud',
                  'https://docs.cloud.google.com/vertex-ai/generative-ai/docs/reference/rest/v1/GenerateContentResponse', 'https://docs.cloud.google.com/vertex-ai/generative-ai/docs/reference/rest/v1/GenerationConfig',
                  'https://docs.cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/vertex-ai-express-mode-api-reference', 'https://docs.cloud.google.com/docs/authentication/api-keys-use',
                  'https://ai.google.dev/api/generate-content', 'https://ai.google.dev/gemini-api/docs/pricing', 'https://ai.google.dev/gemini-api/docs/billing', 'https://docs.cloud.google.com/free/docs/free-cloud-features']

# How each frozen-4 (Anthropic) judge setting maps to Vertex AI, and what cannot match. Recorded in FROZEN.json (frozen-6, frozen-7).
VERTEX_MAPPING = {
    'prompt': 'identical: the frozen system text goes in `systemInstruction` (one text part), the user text in `contents` (one user turn, one text part); the prompt fingerprint and every row\'s '
              'prompt_sha256 are the same as for the Anthropic judge and for frozen-5',
    'output cap': 'max_tokens 32768 -> generationConfig.maxOutputTokens 32768: the most a non-streaming direct HTTP call allows (documented: 65,536 per synchronous request, 32,768 for '
                  'non-streaming direct HTTP), counting thinking + answer together as the Anthropic cap did. It is NOT the 8,000 of frozen-4 / frozen-5: raised so that high thinking '
                  'does not use the cap up (a cut reply keeps no choice and aborts the formal comparison). CANNOT MATCH: the tokenizers differ and the cap is four times larger',
    'reasoning': 'Anthropic: the model\'s default reasoning, no setting. Vertex: generationConfig.thinkingConfig.thinkingLevel "HIGH" (LOW / MEDIUM default / HIGH; thinking_budget and MINIMAL are '
                 'HTTP 400). CANNOT MATCH: different mechanisms',
    'thought text': 'not requested (includeThoughts is not sent); any part the response flags `thought: true` is skipped, so `raw` is the answer text only',
    'temperature': 'not set for either; Vertex ignores a custom temperature / top_p / top_k for this model, so none is sent and --temperature is refused',
    'other sampling': 'seed, stop sequences, safety settings, candidateCount: not set (defaults); a prompt the service blocks (promptFeedback.blockReason) has no candidate and so no choice',
    'retries': 'none: one request per call; a failed request is a failed call (the budget wrapper charges its full worst case and the batch is incomplete)',
    'streaming': 'none: one synchronous generateContent request on v1 (no long decode: it needs v1beta1; a finishReason CONTINUATION would keep no choice)',
    'serving': 'the same model id as frozen-5 but the Vertex AI serving stack, not the Gemini Developer API; identical outputs are not guaranteed',
    'location': 'global, in the URL path (projects/PROJECT/locations/global/publishers/google/models/gemini-4-argon:generateContent): the project-less key URL of frozen-6 pins us-central1, where '
                'the model is not served; every row records its location, and `compare` refuses another',
    'project': 'the Google Cloud project the key bills to (not a secret): the VERTEX_PROJECT setting (environment, or the run kit\'s --vertex-project flag); it is in the URL, recorded in every '
               'row as vertex_project and listed in the compare report, and NOT part of the freeze (the freeze names the setting, not the value)',
    'price': 'USD per 1M tokens, input / output including thinking: 2 / 10 through 2026-11-30, 4 / 20 from 2026-12-01 (Google Cloud announcement; the Vertex pricing tables could not be read); the budget '
             'reserves every call at 4 / 20; the cached-input discount is ignored',
    'finish': 'stop_reason is "end_turn" only for finishReason STOP; any other finishReason (MAX_TOKENS, SAFETY, CONTINUATION, ...), a candidate without a finishReason, no candidate, or a blocked '
              'prompt is stored as "vertex:<reason>" (NO_FINISH_REASON, NO_CANDIDATE, BLOCKED_<blockReason>) and is never an intact answer',
    'usage': 'input = promptTokenCount (cached input charged in full); output = totalTokenCount - promptTokenCount when the total is consistent, else candidatesTokenCount + thoughtsTokenCount',
    'key': 'a Google Cloud API key bound to a service account, read from VERTEX_API_KEY (environment, else the last export line of ~/.bashrc, parsed as text; an empty last export retires an '
           'earlier key; the key must be letters, digits, ".", "-" and "_" only, so a shell expression is refused, not expanded) and sent only in the x-goog-api-key header; a redirect '
           'answer is an error, never followed',
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
    """The key: the environment first, else the LAST `export VAR=...` line of ~/.bashrc (read as text and parsed; never executed, never printed, never stored: a shell expression such as
    `$(cat file)` is NOT expanded, so it is refused). A later EMPTY export retires an earlier key, as it would in the shell. The key must consist of letters, digits, '.', '-' and '_' (every
    Google API key does: 'AIza...' and 'AQ....'); a trailing CR from a Windows-edited file is stripped first. Anything else (a blank, a control character, shell syntax, a quote or backslash that
    JSON and repr would escape) is refused, because a key the HTTP library rejects would be quoted in its error and a literal `$(cat` would burn a charged call. Exits with a message that names
    the variable and never the value."""
    k = (os.environ.get(var) or '').strip()
    if not k:
        bashrc = os.path.expanduser('~/.bashrc')
        if os.path.exists(bashrc):
            last = None
            with open(bashrc, encoding='utf-8', errors='replace') as f:
                for line in f:
                    m = re.match(r'\s*export\s+' + re.escape(var) + r'=(.*)$', line.strip())
                    if m:
                        last = parse_export_value(m.group(1))
            k = (last or '').strip()
    if not k:
        sys.exit(f'no {var} (environment or ~/.bashrc)')
    if not re.fullmatch(r'[A-Za-z0-9._\-]+', k):
        sys.exit(f"{var} is not a usable key (letters, digits, '.', '-' and '_' only: a shell expression such as $(...) is not expanded here, export the literal key); its value is not shown")
    return k


def scrub(text, key):
    """A message that may be shown or stored, without the key (and without anything that looks like one: the 'AIza...' keys of the Developer API and the 'AQ....' keys bound to a service account)."""
    text = str(text)
    if key:
        text = text.replace(key, '***')
    text = re.sub(r'AIza[0-9A-Za-z_\-]{20,}', '***', text)
    return re.sub(r'\bAQ\.[0-9A-Za-z_\-]{20,}', '***', text)


def _num(x):
    """A token count: a whole number that is not a bool, else None."""
    return x if isinstance(x, int) and not isinstance(x, bool) and x >= 0 else None


def _usage(tin, tout, tth, total, cached):
    """(usage, missing): input_tokens = the prompt count (cached input is NOT discounted); output_tokens = everything billed as output (answer + thinking) = total - input when the
    provider's own total is consistent (it does not matter whether the answer count already holds the thinking), else answer + thinking; `missing` when the input count or both output
    counts are absent (the cost is then unknown and charged at its worst case)."""
    tin, tout, tth, total, cached = _num(tin), _num(tout), _num(tth), _num(total), _num(cached)
    missing = tin is None or (tout is None and tth is None)
    billed_out = (tout or 0) + (tth or 0)
    if total is not None and tin is not None and (tout or 0) <= total - tin:
        billed_out = total - tin
    return {'input_tokens': tin, 'output_tokens': billed_out, 'thought_tokens': tth or 0, 'answer_tokens': tout or 0, 'cached_tokens': cached or 0, 'total_tokens': total}, missing


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
    usage, missing = _usage(u.get('total_input_tokens'), u.get('total_output_tokens'), u.get('total_thought_tokens'), u.get('total_tokens'), u.get('total_cached_tokens'))
    status = j.get('status')
    extra = {'stop_reason': 'end_turn' if status == 'completed' else f'gemini:{status}', 'content_types': types, 'status': status, 'usage_missing': missing}
    if j.get('errors'):
        extra['errors'] = j['errors']
    return ''.join(texts), usage, j.get('model', model), extra


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """A redirect answer is an error, never followed: urllib would send the x-goog-api-key header on to whatever host the answer names."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)


def _post_json(url, headers, body, timeout):
    req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), method='POST', headers=headers)
    with _OPENER.open(req, timeout=timeout) as r:
        return json.load(r)


def _send(url, key, body, timeout):
    """One request, no retry: the answer as a dict, or SystemExit with a message that never holds the key (an HTTP error, no answer, a timeout, a body that is not a JSON object).
    The key travels only in the x-goog-api-key header, never in the URL."""
    headers = {'x-goog-api-key': key, 'content-type': 'application/json'}
    try:
        j = _post_json(url, headers, body, timeout)
    except urllib.error.HTTPError as e:
        try:
            text = e.read().decode('utf-8', 'replace')
        except Exception:  # the error body itself did not arrive
            text = ''
        sys.exit(f'API error {e.code}: {scrub(text, key)[:500]}')  # scrub first, THEN cut: a key that straddles the cut must not survive as a prefix
    except urllib.error.URLError as e:
        sys.exit(f'API error (no answer): {scrub(e.reason, key)}')
    except (OSError, http.client.HTTPException) as e:  # a timeout while reading the answer, a connection that broke, a body cut short
        sys.exit(f'API error (no usable answer): {type(e).__name__}: {scrub(e, key)}')
    except (ValueError, RecursionError, MemoryError) as e:  # a body that is not JSON (or absurdly nested / large), or a header the HTTP library refuses: its message can QUOTE the header, so only the type is shown
        sys.exit(f'API error (no usable answer): {type(e).__name__}')
    if not isinstance(j, dict):
        sys.exit('API error: the answer is not a JSON object')
    return j


def call_gemini(system, user, model=GEMINI_FROZEN['model'], max_tokens=GEMINI_FROZEN['max_tokens'], temperature=None, thinking=None, timeout=300):
    """One Interactions API call: one request, no retry (a failed call is a failed call). Returns (text, usage, seconds, model, extra) like judge.call_claude."""
    if temperature is not None:
        raise ValueError('temperature is not a documented setting of gemini-4-argon: the frozen judge sets none')
    thinking = thinking or {k: GEMINI_FROZEN[k] for k in ('thinking_level', 'thinking_summaries')}
    key = load_key()
    t0 = time.time()
    j = _send(GEMINI_ENDPOINT, key, build_gemini_request(system, user, model, max_tokens, thinking), timeout)
    text, usage, model_used, extra = parse_interaction(j, model)
    return text, usage, round(time.time() - t0, 2), model_used, extra


# ---------------------------------------------------------------------------------------------------------------------------------- Vertex AI
_PROJECT_ID = re.compile(r'[a-z][a-z0-9\-]{4,28}[a-z0-9]')  # a Google Cloud project id: 6-30 lowercase letters, digits and hyphens
_PROJECT_NUMBER = re.compile(r'[0-9]{6,20}')


def valid_project(project):
    return isinstance(project, str) and bool(_PROJECT_ID.fullmatch(project) or _PROJECT_NUMBER.fullmatch(project))


def set_vertex_project(project):
    """The run kit's --vertex-project flag: wins over the environment. A malformed value stops the run (the message names the setting; the project id is not a secret)."""
    if project is not None and not valid_project(project):
        sys.exit(f'--vertex-project is not a Google Cloud project id (6-30 lowercase letters, digits and hyphens) or number (6-20 digits); its value is not shown')
    _VERTEX_PROJECT[0] = project


def vertex_project(required=True, strict=True):
    """The Google Cloud project the key bills to: set_vertex_project, else the VERTEX_PROJECT environment variable. None when it is not set and not `required`. A value that is not a
    project id or number stops the run (strict), naming the setting and never the value (the validator cannot know it is not an API key pasted in the wrong place); with strict=False
    (a dry run, a mock run, a row's provenance) it is treated as not set."""
    p = (_VERTEX_PROJECT[0] or os.environ.get(VERTEX_PROJECT_VAR) or '').strip()
    if not p:
        if required:
            sys.exit(f'no {VERTEX_PROJECT_VAR} (environment) and no --vertex-project: the Vertex AI URL names the project')
        return None
    if not valid_project(p):
        if strict:
            sys.exit(f'{VERTEX_PROJECT_VAR} is not a Google Cloud project id (6-30 lowercase letters, digits and hyphens) or number (6-20 digits); its value is not shown')
        return None
    return p


def vertex_url(model, project, location=None):
    """The generateContent URL of a publisher model in a project and location: the model id, the project and the location must be plain names (nothing that could change the path)."""
    location = location or VERTEX_FROZEN['location']
    if not isinstance(model, str) or not re.fullmatch(r'[a-z0-9][a-z0-9.\-]*', model):
        raise ValueError(f'not a model id: {model!r}')
    if not valid_project(project):
        raise ValueError('not a project id or number')  # the value is not echoed: it may be an API key pasted in the wrong place
    if not isinstance(location, str) or not re.fullmatch(r'[a-z0-9][a-z0-9\-]*', location):
        raise ValueError(f'not a location: {location!r}')
    return VERTEX_URL.format(project=project, location=location, model=model)


def build_vertex_request(system, user, max_tokens, thinking_level):
    """The JSON body of one GenerateContent request. Exactly the frozen prompt: `system` is the system instruction, `user` the one user turn. generationConfig holds only the output cap
    and the thinking level: no temperature / top_p / top_k (ignored by this model on Vertex), no includeThoughts, no safety settings, no candidateCount."""
    return {'systemInstruction': {'parts': [{'text': system}]}, 'contents': [{'role': 'user', 'parts': [{'text': user}]}],
            'generationConfig': {'maxOutputTokens': max_tokens, 'thinkingConfig': {'thinkingLevel': thinking_level}}}


def parse_generate_content(j, model):
    """(text, usage, model_used, extra) from a GenerateContentResponse. The answer is the text of the FIRST candidate's parts that are not flagged `thought: true`. stop_reason is
    'end_turn' only for finishReason STOP; any other finishReason, a missing candidate, or a blocked prompt is 'vertex:<reason>' (never an intact answer). Usage: see _usage
    (promptTokenCount / candidatesTokenCount / thoughtsTokenCount / totalTokenCount); a missing usageMetadata sets usage_missing."""
    cands = j.get('candidates') if isinstance(j.get('candidates'), list) else []
    cand = cands[0] if cands and isinstance(cands[0], dict) else {}
    content = cand.get('content') if isinstance(cand.get('content'), dict) else {}
    texts, kinds = [], []
    for p in content.get('parts') if isinstance(content.get('parts'), list) else []:
        if not isinstance(p, dict):
            continue
        thought = p.get('thought') is True
        kinds.append('thought' if thought else ('text' if isinstance(p.get('text'), str) else 'other'))
        if not thought and isinstance(p.get('text'), str):
            texts.append(p['text'])
    feedback = j.get('promptFeedback') if isinstance(j.get('promptFeedback'), dict) else {}
    block = feedback.get('blockReason')
    finish = cand.get('finishReason')
    if finish is None:  # an empty finishReason on a candidate means "has not stopped" (Vertex v1 reference); no candidate at all is a blocked prompt or an empty answer
        finish = 'NO_FINISH_REASON' if cand else (f'BLOCKED_{block}' if block else 'NO_CANDIDATE')
    u = j.get('usageMetadata') if isinstance(j.get('usageMetadata'), dict) else {}
    usage, missing = _usage(u.get('promptTokenCount'), u.get('candidatesTokenCount'), u.get('thoughtsTokenCount'), u.get('totalTokenCount'), u.get('cachedContentTokenCount'))
    extra = {'stop_reason': 'end_turn' if finish == 'STOP' else f'vertex:{finish}', 'content_types': kinds, 'finish_reason': cand.get('finishReason'), 'usage_missing': missing, 'n_candidates': len(cands)}
    if block:
        extra['block_reason'] = block
    return ''.join(texts), usage, j.get('modelVersion') if isinstance(j.get('modelVersion'), str) else model, extra


def call_vertex(system, user, model=VERTEX_FROZEN['model'], max_tokens=VERTEX_FROZEN['max_tokens'], temperature=None, thinking=None, timeout=1260):
    """One GenerateContent call on Vertex AI: one request, no retry. Returns (text, usage, seconds, model, extra) like judge.call_claude. The timeout is long on purpose: a non-streaming
    call that thinks up to the 32,768-token cap can take minutes, and the model guide gives 20 minutes (1,200 s) as the per-request limit of that loop; 1,260 s waits at least that long."""
    if temperature is not None:
        raise ValueError('a custom temperature is ignored by gemini-4-argon on Vertex AI: the frozen judge sets none')
    thinking = thinking or {'thinking_level': VERTEX_FROZEN['thinking_level']}
    url = vertex_url(model, vertex_project(), VERTEX_FROZEN['location'])
    key = load_key(VERTEX_KEY_VAR)
    t0 = time.time()
    j = _send(url, key, build_vertex_request(system, user, max_tokens, thinking['thinking_level']), timeout)
    text, usage, model_used, extra = parse_generate_content(j, model)
    return text, usage, round(time.time() - t0, 2), model_used, extra
