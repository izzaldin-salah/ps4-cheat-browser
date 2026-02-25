import re
from collections import defaultdict

def parse_games_list(filepath):
    entries = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            ids = re.findall(r'\[([A-Z]{2,6}\d{4,8}(?:[-_]\d+)?)\]', line)
            name_match = re.match(r'^(.+?)\s*\[', line)
            if name_match and ids:
                name = name_match.group(1).strip()
                game_id = ids[-1]
                entries.append((name, game_id, line))
    return entries

def get_base_name(name):
    n = name.replace('™', '').replace('®', '').replace('©', '')
    n = n.lower().strip()
    n = re.sub(r'[:\-–—.,!?\'\"()]', ' ', n)
    n = re.sub(r'\s+', ' ', n).strip()
    return n

def pick_best_name(names):
    if len(names) == 1:
        return names[0]
    def score(name):
        s = 0
        if '™' in name: s += 3
        if '®' in name: s += 2
        if name != name.upper() or len(name) <= 5: s += 1
        s += len(name) * 0.01
        if '(' in name: s -= 1
        if name[0].isupper(): s += 1
        return s
    return max(names, key=score)

filepath = r'games_list_for_covers.txt'
entries = parse_games_list(filepath)
print(f"Total entries: {len(entries)}")

by_base_name = defaultdict(list)
for name, gid, line in entries:
    base = get_base_name(name)
    by_base_name[base].append((name, gid, line))

dup_names = {base: items for base, items in by_base_name.items() if len(items) > 1}
print(f"\nGroups (same normalized name): {len(dup_names)}")
for base, items in sorted(dup_names.items()):
    names = [n for n,g,l in items]
    ids = [g for n,g,l in items]
    best = pick_best_name(names)
    print(f"\n  Base: [{base}] => Official: [{best}]")
    for n, g, _ in items:
        marker = " <-- BEST" if n == best else ""
        print(f"    [{g}] {n}{marker}")
