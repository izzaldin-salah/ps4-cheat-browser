#!/usr/bin/env python3
"""
Matches games-cache.json cover URLs to cheat JSON files by game name.
Outputs cusa_covers.json: { "CUSA00002": "https://...", ... }

Run:  python match_covers.py
"""

import json, os, re, glob
from collections import defaultdict

ROOT = os.path.dirname(__file__)

# ── Load cache ────────────────────────────────────────────────────────────────
with open(os.path.join(ROOT, 'games-cache.json'), encoding='utf-8') as f:
    cache_games = json.load(f)['games']

# ── Normalise helper ──────────────────────────────────────────────────────────
_NOISE = re.compile(
    r'\b(ps4|ps3|ps5|pkg|fpkg|iso|remaster(ed)?|definitive edition|'
    r'complete edition|gold edition|goty|game of the year|'
    r'deluxe edition|standard edition|digital edition|bundle|collection|'
    r'hd|4k|vr)\b',
    re.IGNORECASE
)

def norm(s):
    s = s.lower()
    s = re.sub(r'[®™©]', '', s)
    s = _NOISE.sub('', s)
    s = re.sub(r'[^a-z0-9 ]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def tokens(s):
    return set(norm(s).split())

# ── Build cache lookup ────────────────────────────────────────────────────────
# Map normalised title → cover URL
cache_norm  = {}   # exact normalised → url
cache_entries = []
for g in cache_games:
    n = norm(g['title'])
    if n:
        cache_norm[n] = g['cover']
        cache_entries.append((n, tokens(g['title']), g['cover']))

# ── Match each cheat file ─────────────────────────────────────────────────────
json_dir = os.path.join(ROOT, 'json')
files    = sorted(glob.glob(os.path.join(json_dir, '*.json')))

cusa_covers = {}   # CUSA ID → cover URL
matched = unmatched = 0

for path in files:
    try:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        continue

    cusa_id   = data.get('id') or ''
    game_name = data.get('name') or ''
    if not cusa_id or not game_name or cusa_id in cusa_covers:
        continue

    n = norm(game_name)
    t = tokens(game_name)

    # 1 — exact normalised match
    if n in cache_norm:
        cusa_covers[cusa_id] = cache_norm[n]
        matched += 1
        continue

    # 2 — token-based: cache entry tokens ⊇ game tokens (80 %+ overlap)
    best_url   = None
    best_score = 0.0
    for cn, ct, curl in cache_entries:
        if not t:
            continue
        overlap = len(t & ct) / len(t)
        if overlap > best_score and overlap >= 0.75:
            best_score = overlap
            best_url   = curl

    if best_url:
        cusa_covers[cusa_id] = best_url
        matched += 1
    else:
        unmatched += 1

# ── Write output ──────────────────────────────────────────────────────────────
out_path = os.path.join(ROOT, 'cusa_covers.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(cusa_covers, f, separators=(',', ':'), ensure_ascii=False)

total = matched + unmatched
print(f'✅  {matched}/{total} CUSA IDs matched  ({round(matched/total*100)}%)')
print(f'❌  {unmatched} unmatched')
print(f'📄  Written → cusa_covers.json  ({os.path.getsize(out_path)//1024} KB)')
