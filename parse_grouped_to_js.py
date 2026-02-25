# -*- coding: utf-8 -*-
import re

INPUT_FILE  = 'c:\\Users\\izald\\Documents\\PROJECTS\\PS4 CHEATS\\games_list_for_covers_grouped.txt'
OUTPUT_FILE = 'c:\\Users\\izald\\Documents\\PROJECTS\\PS4 CHEATS\\cusa_id_map_output.js'

STRIP_CHARS  = re.compile('[' + chr(0x2122) + chr(0xae) + chr(0xa9) + ']')
LAST_BRACKET = re.compile(r'^(.*)\[([A-Z0-9]+)\]\s*$')
ARROW = chr(0x21b3)

def clean_display(raw):
    s = STRIP_CHARS.sub('', raw)
    s = re.sub(r'  +', ' ', s)
    return s.strip()

def escape_js(s):
    bs = chr(92)
    ap = chr(39)
    s = s.replace(bs, bs + bs)
    s = s.replace(ap, bs + ap)
    return s

def parse_line(line):
    stripped = line.strip()
    if stripped.startswith(ARROW):
        stripped = stripped[1:].strip()
    m = LAST_BRACKET.match(stripped)
    if not m:
        return None
    return m.group(2), clean_display(m.group(1))

def main():
    entries = {}
    cur_id = None
    cur_disp = None
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        for raw in f:
            line = raw.rstrip(chr(10))
            if not line.strip():
                cur_id = None
                cur_disp = None
                continue
            is_sub = line.startswith('  ' + ARROW) or line.startswith(chr(9) + ARROW)
            result = parse_line(line)
            if result is None:
                continue
            gid, disp = result
            if not is_sub:
                cur_id = gid
                cur_disp = disp
                entries[gid] = (gid, disp)
            else:
                if cur_id is not None:
                    entries[gid] = (cur_id, cur_disp)
                else:
                    entries[gid] = (gid, disp)

    sorted_e = sorted(entries.items(), key=lambda kv: kv[0])
    q = chr(39)
    out = ['const _CUSA_ID_MAP = {']
    for gid, (cid, disp) in sorted_e:
        safe = escape_js(disp)
        out.append('  ' + q + gid + q + ': { key: ' + q + cid + q + ', display: ' + q + safe + q + ' },')
    out.append('};')

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(chr(10).join(out) + chr(10))

    print('Written', len(entries), 'entries to', OUTPUT_FILE)

    bs2 = chr(92)
    ap2 = chr(39)
    problems = []
    for ol in out:
        marker = 'display: ' + ap2
        start = ol.find(marker)
        if start == -1:
            continue
        start += len(marker)
        end = ol.rfind(ap2 + ' }')
        if end == -1 or end <= start:
            continue
        val = ol[start:end]
        i = 0
        while i < len(val):
            if val[i] == ap2:
                problems.append(ol)
                break
            if val[i] == bs2:
                i += 2
                continue
            i += 1

    if problems:
        print('WARNING - unescaped apostrophes found:')
        for p in problems[:5]:
            print(' ', p)
    else:
        print('Apostrophe check passed - no unescaped apostrophes in display values.')

main()
