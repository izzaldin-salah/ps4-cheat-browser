#!/usr/bin/env python3
"""
Populates the Supabase `games` table from the local json/ folder.
Also fetches Wikipedia cover art for each game and stores it in the data JSON.

Run once (or whenever you add new cheat files):

    python populate_supabase.py

Requires:  pip install requests
Needs:     SUPABASE_URL and SUPABASE_SERVICE_KEY set as env vars.

Use your SERVICE ROLE key here (only runs locally, never committed to git).
The anon key goes in the website — the service key stays on your machine.
"""

import json, os, glob, sys, time, re
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote

# ─── CONFIG ──────────────────────────────────────────────────────────────────
SUPABASE_URL         = os.environ.get('SUPABASE_URL', '')
SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '')
BATCH_SIZE           = 200
COVER_WORKERS        = 10   # parallel Wikipedia requests
# ─────────────────────────────────────────────────────────────────────────────

def fetch_wiki_cover(game_name):
    """Fetch cover art URL from Wikipedia. Returns URL string or None."""
    try:
        clean = re.sub(r'[®™©]', '', game_name).strip()
        url = (
            'https://en.wikipedia.org/w/api.php'
            '?action=query&generator=search'
            f'&gsrsearch={quote(clean + " video game")}'
            '&gsrlimit=3&prop=pageimages&pithumbsize=600&format=json'
        )
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        pages = sorted(r.json().get('query', {}).get('pages', {}).values(),
                       key=lambda p: p.get('index', 999))
        for page in pages:
            if page.get('thumbnail', {}).get('source'):
                return page['thumbnail']['source']
    except Exception:
        pass
    return None

def main():
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print('❌  Set SUPABASE_URL and SUPABASE_SERVICE_KEY as environment variables.')
        print()
        print('  Windows PowerShell:')
        print('    $env:SUPABASE_URL="https://xxxx.supabase.co"')
        print('    $env:SUPABASE_SERVICE_KEY="eyJ..."')
        print('    python populate_supabase.py')
        sys.exit(1)

    headers = {
        'apikey':        SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type':  'application/json',
        'Prefer':        'resolution=merge-duplicates',
    }
    endpoint = f'{SUPABASE_URL.rstrip("/")}/rest/v1/games'

    # ── Load all JSON files ───────────────────────────────────────────────────
    json_dir = os.path.join(os.path.dirname(__file__), 'json')
    files    = sorted(glob.glob(os.path.join(json_dir, '*.json')))
    print(f'📂  Found {len(files)} JSON files in ./json/')

    rows = []
    skipped = 0
    for path in files:
        try:
            with open(path, encoding='utf-8') as f:
                data = json.load(f)
            name    = data.get('name')
            cusa_id = data.get('id') or data.get('region') or data.get('titleid') or ''
            if not isinstance(name, str) or not isinstance(data.get('mods'), list):
                skipped += 1
                continue
            file_id = os.path.splitext(os.path.basename(path))[0]
            rows.append({'file_id': file_id, 'name': name, 'cusa_id': cusa_id, 'data': data})
        except Exception as e:
            print(f'  ⚠  skip {os.path.basename(path)}: {e}')
            skipped += 1

    print(f'✅  {len(rows)} valid games, {skipped} skipped')

    # ── Fetch covers in parallel ──────────────────────────────────────────────
    # Deduplicate by name so we only fetch each game once
    name_to_cover = {}
    unique_names  = list({r['name'] for r in rows})
    print(f'🎨  Fetching covers for {len(unique_names)} unique titles ({COVER_WORKERS} parallel)…')

    done = 0
    with ThreadPoolExecutor(max_workers=COVER_WORKERS) as ex:
        futures = {ex.submit(fetch_wiki_cover, name): name for name in unique_names}
        for future in as_completed(futures):
            name = futures[future]
            name_to_cover[name] = future.result()
            done += 1
            if done % 50 == 0 or done == len(unique_names):
                hits = sum(1 for v in name_to_cover.values() if v)
                print(f'  {done}/{len(unique_names)} — {hits} covers found', end='\r')

    hits = sum(1 for v in name_to_cover.values() if v)
    print(f'\n  ✔  {hits}/{len(unique_names)} covers found')

    # Bake coverUrl into each game's data JSON
    for row in rows:
        cv = name_to_cover.get(row['name'])
        if cv:
            row['data']['coverUrl'] = cv

    # ── Upload in batches ─────────────────────────────────────────────────────
    print(f'⬆️   Uploading {len(rows)} rows in batches of {BATCH_SIZE}…')
    total_done = 0
    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i : i + BATCH_SIZE]
        resp  = requests.post(endpoint, headers=headers, json=batch, timeout=30)
        if resp.status_code not in (200, 201):
            print(f'  ❌  Batch {i}–{i+len(batch)} failed: {resp.status_code} {resp.text[:200]}')
        else:
            total_done += len(batch)
            pct = round(total_done / len(rows) * 100)
            print(f'  ✔  {total_done}/{len(rows)} ({pct}%)', end='\r')
        time.sleep(0.1)

    print(f'\n🎉  Done — {total_done} games upserted to Supabase (with cover URLs).')

if __name__ == '__main__':
    main()


def main():
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print('❌  Set SUPABASE_URL and SUPABASE_SERVICE_KEY as environment variables.')
        print()
        print('  Windows PowerShell:')
        print('    $env:SUPABASE_URL="https://xxxx.supabase.co"')
        print('    $env:SUPABASE_SERVICE_KEY="eyJ..."')
        print('    python populate_supabase.py')
        sys.exit(1)

    headers = {
        'apikey':        SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type':  'application/json',
        'Prefer':        'resolution=merge-duplicates',  # upsert
    }
    endpoint = f'{SUPABASE_URL.rstrip("/")}/rest/v1/games'

    # ── Load all JSON files ───────────────────────────────────────────────────
    json_dir = os.path.join(os.path.dirname(__file__), 'json')
    files    = sorted(glob.glob(os.path.join(json_dir, '*.json')))
    print(f'📂  Found {len(files)} JSON files in ./json/')

    rows = []
    skipped = 0
    for path in files:
        try:
            with open(path, encoding='utf-8') as f:
                data = json.load(f)
            name    = data.get('name')
            cusa_id = data.get('id') or data.get('region') or data.get('titleid') or ''

            if not isinstance(name, str) or not isinstance(data.get('mods'), list):
                skipped += 1
                continue

            # file_id = filename without .json
            file_id = os.path.splitext(os.path.basename(path))[0]

            rows.append({
                'file_id': file_id,
                'name':    name,
                'cusa_id': cusa_id,
                'data':    data,      # store the full original JSON
            })
        except Exception as e:
            print(f'  ⚠  skip {os.path.basename(path)}: {e}')
            skipped += 1

    print(f'✅  {len(rows)} valid games, {skipped} skipped')
    print(f'⬆️   Uploading in batches of {BATCH_SIZE}…')

    # ── Upload in batches ─────────────────────────────────────────────────────
    total_done = 0
    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i : i + BATCH_SIZE]
        resp  = requests.post(endpoint, headers=headers, json=batch, timeout=30)
        if resp.status_code not in (200, 201):
            print(f'  ❌  Batch {i}–{i+len(batch)} failed: {resp.status_code} {resp.text[:200]}')
        else:
            total_done += len(batch)
            pct = round(total_done / len(rows) * 100)
            print(f'  ✔  {total_done}/{len(rows)} ({pct}%)', end='\r')
        time.sleep(0.1)   # be gentle with the API

    print(f'\n🎉  Done — {total_done} games upserted to Supabase.')

if __name__ == '__main__':
    main()
