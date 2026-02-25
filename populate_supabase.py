#!/usr/bin/env python3
"""
Populates the Supabase `games` table from the local json/ folder.
Run once (or whenever you add new cheat files):

    python populate_supabase.py

Requires:  pip install requests
Needs:     SUPABASE_URL and SUPABASE_SERVICE_KEY set below (or as env vars).

Use your SERVICE ROLE key here (only runs locally, never committed to git).
The anon key goes in the website — the service key stays on your machine.
"""

import json, os, glob, sys, time
import requests

# ─── CONFIG ──────────────────────────────────────────────────────────────────
SUPABASE_URL         = os.environ.get('SUPABASE_URL', '')          # https://xxxx.supabase.co
SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '')  # service_role key (secret!)
BATCH_SIZE           = 200   # rows per upsert request
# ─────────────────────────────────────────────────────────────────────────────

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
