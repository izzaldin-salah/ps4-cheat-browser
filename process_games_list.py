import re
from collections import defaultdict
import json
import urllib.request
import urllib.parse

def parse_games_list(filepath):
    """Parse the games list and return list of (name, id) tuples."""
    entries = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Extract all IDs from the line (can have multiple [...] blocks)
            ids = re.findall(r'\[([A-Z]{2,6}\d{4,8}(?:[-_]\d+)?)\]', line)
            # Get the game name (text before the first bracket group)
            name_match = re.match(r'^(.+?)\s*\[', line)
            if name_match and ids:
                name = name_match.group(1).strip()
                # Use the last CUSA/SLUS/SLES/etc ID found
                game_id = ids[-1]
                entries.append((name, game_id, line))
    return entries

def get_base_name(name):
    """Normalize game name for comparison."""
    # Remove trademark/registered symbols
    n = name.replace('™', '').replace('®', '').replace('©', '')
    # Lowercase
    n = n.lower().strip()
    # Remove special punctuation
    n = re.sub(r'[:\-–—.,!?\'\"()]', ' ', n)
    # Collapse spaces
    n = re.sub(r'\s+', ' ', n).strip()
    return n

def lookup_ps4_title(cusa_id):
    """Try to get official title from PS Store API."""
    try:
        url = f"https://store.playstation.com/en-us/product/{cusa_id}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            # Just return None - we'll handle naming differently
            pass
    except:
        pass
    return None

def pick_best_name(names):
    """Pick the most 'official' name from a list of names for the same game."""
    if len(names) == 1:
        return names[0]
    
    # Scoring: prefer names with trademark symbols, proper capitalization, longer names
    def score(name):
        s = 0
        if '™' in name: s += 3
        if '®' in name: s += 3
        # Prefer names that aren't all caps (unless very short)
        if name != name.upper() or len(name) <= 5: s += 1
        # Prefer longer, more descriptive names
        s += len(name) * 0.01
        # Penalize names with extra info in parens
        if '(' in name: s -= 1
        # Prefer names that start with proper capitalization
        if name[0].isupper(): s += 1
        return s
    
    return max(names, key=score)

def main():
    filepath = r'c:\Users\izald\Documents\PROJECTS\PS4 CHEATS\games_list_for_covers.txt'
    entries = parse_games_list(filepath)
    
    print(f"Total entries: {len(entries)}")
    
    # Group by ID
    by_id = defaultdict(list)
    for name, gid, line in entries:
        by_id[gid].append((name, line))
    
    # Find IDs that appear more than once
    dup_ids = {gid: names for gid, names in by_id.items() if len(names) > 1}
    print(f"\nIDs with multiple entries (same ID, different names): {len(dup_ids)}")
    for gid, items in sorted(dup_ids.items()):
        names = [n for n,_ in items]
        unique_names = list(dict.fromkeys(names))
        if len(unique_names) > 1:
            print(f"  [{gid}]:")
            for n in unique_names:
                print(f"    - {n}")
    
    # Group by normalized base name
    by_base_name = defaultdict(list)
    for name, gid, line in entries:
        base = get_base_name(name)
        by_base_name[base].append((name, gid, line))
    
    # Find base names with multiple IDs (regional/version variants)
    dup_names = {base: items for base, items in by_base_name.items() if len(items) > 1}
    print(f"\nGames with multiple IDs (same game different regions/versions): {len(dup_names)}")
    
    return by_id, by_base_name, entries

if __name__ == '__main__':
    by_id, by_base_name, entries = main()
