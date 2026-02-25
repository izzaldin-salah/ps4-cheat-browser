"""
Generate a grouped games_list_for_covers.txt where titles that represent the
same game (same name, different CUSA IDs / regions) are consolidated under
one canonical title with the variants listed beneath.

Output format:

  Official Title [CUSA00207]
    ↳ Bloodborne™ [CUSA03173]
    ↳ Bloodborne [CUSA00208]
    ...

  # Single entries are written as-is.
"""

import re
from collections import defaultdict, OrderedDict

# ── 1. Manual alias table (mirrors the HTML _GAME_GROUPS) ─────────────────────
_GAME_GROUPS = [
    # Call of Duty
    ['Call of Duty: Black Ops III',
     'call of duty black ops 3','call of duty black ops iii',
     'cod black ops 3','cod black ops iii'],
    ['Call of Duty: Black Ops 4',
     'call of duty black ops 4','cod black ops 4'],
    ['Call of Duty: Black Ops Cold War',
     'call of duty black ops cold war','cod black ops cold war'],
    ['Call of Duty: WWII',
     'call of duty wwii','call of duty ww2','cod wwii','cod ww2',
     'call of duty world war 2','call of duty world war ii',
     'call of duty wwii campaign','cod world war 2 mp zm','cod world war 2',
     'call of duty wwii mp zm'],
    ['Call of Duty: Infinite Warfare',
     'call of duty infinite warfare','cod infinite warfare'],
    ['Call of Duty: Advanced Warfare',
     'call of duty advanced warfare','cod advanced warfare'],
    ['Call of Duty: Modern Warfare Remastered',
     'call of duty modern warfare remastered','cod modern warfare remastered'],
    ['Call of Duty: Modern Warfare',
     'call of duty modern warfare'],
    ['Call of Duty: Modern Warfare 2 Campaign Remastered',
     'call of duty modern warfare 2 campaign remastered',
     'cod modern warfare 2 remastered','cod mw2 remastered'],
    ['Call of Duty: Modern Warfare II',
     'call of duty modern warfare 2','call of duty modern warfare ii'],
    ['Call of Duty: Vanguard',
     'call of duty vanguard','cod vanguard'],
    ['Call of Duty: Ghosts',
     'call of duty ghosts','cod ghosts','cod ghosts ex'],
    # Grand Theft Auto
    ['Grand Theft Auto V',
     'grand theft auto 5','grand theft auto v','gta 5','gta v'],
    # Tom Clancy
    ["Tom Clancy's Rainbow Six Siege",
     "tom clancy s rainbow six siege","tom clancys rainbow six seige",
     'rainbow six siege','tom clancys rainbow six siege'],
    ["Tom Clancy's Ghost Recon Wildlands",
     "tom clancy s ghost recon wildlands",'ghost recon wildlands',
     'tom clancys ghost recon wildlands'],
    # The Witcher
    ['The Witcher 3: Wild Hunt',
     'the witcher 3 wild hunt','the witcher 3','witcher 3',
     'the witcher 3 wild hunt complete edition',
     'the witcher 3 wild hunt game of the year edition'],
    # Dark Souls
    ['Dark Souls III',
     'dark souls 3','dark souls iii','dark souls iii the fire fades edition'],
    ['Dark Souls II',
     'dark souls 2','dark souls ii','dark souls ii scholar of the first sin'],
    ['Dark Souls: Remastered', 'dark souls remastered'],
    # inFAMOUS
    ['inFAMOUS: Second Son', 'infamous second son'],
    ['inFAMOUS: First Light','infamous first light'],
    # Spider-Man
    ["Marvel's Spider-Man",
     "marvel s spider man","marvels spider man","spider man",
     "spider-man","marvels spider-man"],
    ["Marvel's Spider-Man: Miles Morales",
     "marvel s spider man miles morales","marvels spider man miles morales"],
    # Batman
    ['Batman: Arkham Knight',  'batman arkham knight'],
    ['Batman: Arkham City',    'batman arkham city','batman return to arkham arkham city'],
    # Devil May Cry
    ['Devil May Cry 5',  'devil may cry 5','devil may cry v'],
    ['Devil May Cry 4 Special Edition',
     'devil may cry 4','devil may cry 4 special edition'],
    ['Devil May Cry HD Collection',
     'devil may cry hd collection','devil may cry hd collection 1'],
    # Final Fantasy
    ['FINAL FANTASY XV',
     'final fantasy 15','final fantasy xv',
     'final fantasy xv pocket edition hd','final fantasy 15 pocket edition hd'],
    ['FINAL FANTASY VII REMAKE',
     'final fantasy 7 remake','final fantasy vii remake'],
    ['FINAL FANTASY XII: THE ZODIAC AGE',
     'final fantasy 12 the zodiac age','final fantasy xii the zodiac age'],
    ['FINAL FANTASY X/X-2 HD Remaster',
     'final fantasy x x 2 hd remaster'],
    # NieR
    ['NieR:Automata', 'nier automata'],
    ['NieR Replicant', 'nier replicant','nier replicant ver 1 22474487139'],
    # Yakuza / Like a Dragon
    ['Yakuza 0',         'yakuza 0'],
    ['Yakuza Kiwami',    'yakuza kiwami'],
    ['Yakuza Kiwami 2',  'yakuza kiwami 2'],
    ['Yakuza 3 Remastered', 'yakuza 3 remastered'],
    ['Yakuza 4',            'yakuza 4'],
    ['Yakuza 5',            'yakuza 5 remastered','yakuza 5'],
    ['Yakuza 6: The Song of Life', 'yakuza 6 the song of life','yakuza 6'],
    ['Yakuza: Like a Dragon', 'yakuza like a dragon','like a dragon'],
    ['Like a Dragon: Infinite Wealth', 'like a dragon infinite wealth'],
    ['Like a Dragon: Ishin',  'like a dragon ishin'],
    # Gravity Rush
    ['Gravity Rush 2',   'gravity rush 2'],
    ['Gravity Rush Remastered', 'gravity rush remastered','gravity rush 1'],
    # Battlefield
    ['Battlefield 4',    'battlefield 4'],
    ['Battlefield 1',    'battlefield 1'],
    ['Battlefield V',    'battlefield 5','battlefield v'],
    # Assassin's Creed
    ["Assassin's Creed: The Ezio Collection",
     "assassin s creed the ezio collection","assassins creed the ezio collection",
     "assassins creed the ezio collection assasins creed 2",
     "assassin s creed the ezio collection assasins creed 2"],
    ["Assassin's Creed III Remastered",
     "assassin s creed iii remastered","assassins creed iii remastered"],
    ["Assassin's Creed IV Black Flag",
     "assassin s creed iv black flag","assassins creed iv black flag"],
    ["Assassin's Creed Unity",
     "assassin s creed unity","assassins creed unity","assassins creed unity"],
    ["Assassin's Creed Syndicate",
     "assassin s creed syndicate","assassins creed syndicate"],
    ["Assassin's Creed Origins",
     "assassin s creed origins","assassins creed origins","ac origins"],
    ["Assassin's Creed Odyssey",
     "assassin s creed odyssey","assassins creed odyssey"],
    ["Assassin's Creed Valhalla",
     "assassin s creed valhalla","assassins creed valhalla"],
    ["Assassin's Creed Mirage",
     "assassin s creed mirage","assassins creed mirage"],
    ["Assassin's Creed Rogue Remastered",
     "assassin s creed rogue remastered","assassins creed rogue remastered"],
    ["Assassin's Creed Chronicles: Trilogy Pack",
     "assassin s creed chronicles trilogy pack","assassins creed chronicles trilogy pack"],
    # Resident Evil
    ['Resident Evil 7 biohazard',
     'resident evil 7','resident evil 7 gold edition',
     'resident evil 7 biohazard gold edition'],
    ['Resident Evil 2', 'resident evil 2'],
    ['Resident Evil 3', 'resident evil 3','resident evil 3 nemesis'],
    ['Resident Evil Village', 'resident evil village'],
    ['Resident Evil 5', 'resident evil 5'],
    ['Resident Evil 6', 'resident evil 6'],
    ['Resident Evil 4', 'resident evil 4'],
    ['Resident Evil: Origins Collection', 'resident evil origins collection'],
    ['Resident Evil: Revelations',
     'resident evil revelations','resident evil revelations 1',
     'resident evil revelation'],
    ['Resident Evil: Revelations 2', 'resident evil revelations 2'],
    # Horizon
    ['Horizon Zero Dawn',      'horizon zero dawn'],
    ['Horizon Forbidden West', 'horizon forbidden west'],
    # The Last of Us
    ['The Last of Us Remastered', 'the last of us remastered','the last of us'],
    ['The Last of Us Part II',    'the last of us part 2','the last of us part ii'],
    # God of War
    ['God of War',       'god of war','god of war 2018'],
    ['God of War Ragnarök', 'god of war ragnarok',
     'god of war ragnarok valhalla dlc compatibility'],
    ['God of War III Remastered', 'god of war iii remastered','god of war 3 remastered'],
    # Uncharted
    ["Uncharted 4: A Thief's End",
     "uncharted 4 a thief s end","uncharted 4"],
    ['Uncharted: The Lost Legacy', 'uncharted the lost legacy'],
    ['Uncharted: The Nathan Drake Collection',
     'uncharted the nathan drake collection',
     'uncharted collection uncharted 1'],
    # Borderlands
    ['Borderlands 3',    'borderlands 3'],
    # Monster Hunter
    ['Monster Hunter: World',          'monster hunter world'],
    ['Monster Hunter World: Iceborne', 'monster hunter world iceborne'],
    ['Monster Hunter Rise: Sunbreak',  'monster hunter rise sunbreak'],
    # Persona
    ['Persona 5 Royal',    'persona 5 royal'],
    ['Persona 5 Strikers', 'persona 5 strikers','persona 5 striker'],
    # Dragon Age
    ['Dragon Age: Inquisition', 'dragon age inquisition','dragon age'],
    # Mass Effect
    ['Mass Effect: Andromeda',       'mass effect andromeda'],
    ['Mass Effect Legendary Edition','mass effect legendary edition',
     'mass effect 1 legendary edition'],
    # Far Cry
    ['Far Cry 3',       'far cry 3','far cry 3 blood dragon classic edition',
     'far cry 3 classic edition'],
    ['Far Cry 4',       'far cry 4'],
    ['Far Cry 5',       'far cry 5'],
    ['Far Cry 6',       'far cry 6'],
    ['Far Cry: New Dawn', 'far cry new dawn'],
    # Watch Dogs
    ['Watch_Dogs',   'watch dogs','watch_dogs'],
    ['Watch_Dogs 2', 'watch dogs 2','watch_dogs 2'],
    ['Watch Dogs: Legion', 'watch dogs legion'],
    # Need for Speed
    ['Need for Speed: Rivals',              'need for speed rivals'],
    ['Need for Speed: Payback',             'need for speed payback'],
    ['Need for Speed: Heat',                'need for speed heat'],
    ['Need for Speed: Hot Pursuit Remastered','need for speed hot pursuit remastered'],
    # Red Dead
    ['Red Dead Redemption 2', 'red dead redemption 2'],
    # Sekiro
    ['Sekiro: Shadows Die Twice', 'sekiro shadows die twice','sekiro'],
    # Cyberpunk
    ['Cyberpunk 2077', 'cyberpunk 2077'],
    # Detroit
    ['Detroit: Become Human', 'detroit become human'],
    # Death Stranding
    ['Death Stranding', 'death stranding'],
    # Crash Bandicoot
    ['Crash Bandicoot N. Sane Trilogy',
     'crash bandicoot n sane trilogy','crash bandicoot n. sane trilogy'],
    ["Crash Bandicoot 4: It's About Time",
     'crash bandicoot 4 its about time'],
    # Spyro
    ['Spyro Reignited Trilogy',
     'spyro reignited trilogy','spyro the dragon','spyro 2','spyro 3 5 return'],
    # Ratchet & Clank
    ['Ratchet & Clank', 'ratchet clank','ratchet & clank'],
    # Bloodborne
    ['Bloodborne', 'bloodborne'],
    # Elden Ring
    ['Elden Ring',
     'elden ring','elden ring shadow of the erdtree',
     'elden ring network test ver'],
    ['Elden Ring: Nightreign', 'elden ring nightreign'],
    # Days Gone
    ['Days Gone', 'days gone'],
    # Ghost of Tsushima
    ['Ghost of Tsushima', 'ghost of tsushima'],
    # Metal Gear Solid V
    ['Metal Gear Solid V: The Phantom Pain',
     'metal gear solid v phantom pain',
     'metal gear solid v the definitive experience'],
    # Fallout 4
    ['Fallout 4', 'fallout 4','fallout 4 game of the year edition'],
    # Dying Light
    ['Dying Light',
     'dying light','dying light the following enhanced edition'],
    ['Dying Light 2: Stay Human', 'dying light 2 stay human'],
    # Captain Tsubasa
    ['Captain Tsubasa: Rise of New Champions',
     'captain tsubasa rise of new champion',
     'captain tsubasa rise of new champions'],
    # Dragon Quest XI
    ['Dragon Quest XI: Echoes of an Elusive Age',
     'dragon quest xi echoes of an elusive age',
     'dragon quest xi s echoes of an elusive age definitive edition'],
    # Dragon Ball
    ['Dragon Ball Xenoverse 2', 'dragon ball xenoverse 2','dragonball xenoverse 2'],
    # Darksiders
    ['Darksiders II Deathinitive Edition',
     'darksiders ii deathinitive edition'],
    # Diablo
    ['Diablo III: Reaper of Souls',
     'diablo iii reaper of souls ultimate evil edition',
     'diablo 3 ultimate evil edition'],
    # Dishonored 2
    ['Dishonored 2', 'dishonored 2'],
    # Just Cause
    ['Just Cause 3', 'just cause 3'],
    ['Just Cause 4', 'just cause 4'],
    # Sniper Elite
    ['Sniper Elite 4', 'sniper elite 4'],
    ['Sniper Elite 5', 'sniper elite 5'],
    # ACE COMBAT 7
    ['ACE COMBAT™ 7: SKIES UNKNOWN', 'ace combat 7 skies unknown'],
    # FIFA
    ['FIFA 22', 'fifa 22','fifa22'],
    ['FIFA 23', 'fifa 23','fifa23'],
    # Nioh
    ['Nioh', 'nioh','nioh complete edition'],
    ['Nioh 2', 'nioh 2'],
    # Remant
    ['Remnant: From the Ashes', 'remnant from the ashes'],
    # Metro
    ['Metro Redux', 'metro redux'],
    # Destroy All Humans
    ['Destroy All Humans! 2 - Reprobed', 'destroy all humans 2 reprobed'],
    # One Piece
    ['ONE PIECE PIRATE WARRIORS 4', 'one piece pirate warriors 4'],
    # Naruto
    ['Naruto Shippuden: Ultimate Ninja Storm 4',
     'naruto shippuden ultimate ninja storm 4 road to boruto'],
    # Mafia
    ['Mafia II: Definitive Edition', 'mafia ii definitive edition'],
    # World War Z
    ['World War Z: Aftermath', 'world war z aftermath'],
    # Maneater
    ['Maneater', 'maneater'],
    # Prototype
    ['[PROTOTYPE® BIOHAZARD BUNDLE]', 'prototype biohazard bundle'],
    # Sword Art Online
    ['SWORD ART ONLINE Alicization Lycoris', 'sword art online alicization lycoris'],
    # Sackboy
    ["Sackboy™: A Big Adventure", 'sackboy a big adventure'],
    # GTA Trilogy
    ['Grand Theft Auto: The Trilogy – The Definitive Edition',
     'grand theft auto iii the definitive edition',
     'grand theft auto vice city the definitive edition',
     'grand theft auto san andreas the definitive edition',
     'grand theft auto vice city the definitive edition',
     'grand theft auto san andreas ? the definitive edition'],
    # LEGO Star Wars
    ['LEGO® Star Wars: The Skywalker Saga', 'lego star wars the skywalker saga'],
    # Metaphor
    ['Metaphor: ReFantazio', 'metaphor refantazio'],
    # Star Ocean
    ['Star Ocean: The Second Story R', 'star ocean the second story r'],
    # Wo Long
    ['Wo Long: Fallen Dynasty', 'wo long fallen dynasty'],
    # Bulletstorm
    ['Bulletstorm: Full Clip Edition', 'bulletstorm full clip edition'],
    # Aragami
    ['Aragami 2', 'aragami 2'],
    # ARK
    ['ARK: Survival Evolved', 'ark survival evolved'],
    # 7 Days to Die
    ['7 Days to Die', '7 days to die'],
    # Cities: Skylines
    ['Cities: Skylines', 'cities skylines'],
    # COD: Black Ops III (alt)
    ['Call of Duty: Black Ops III', 'cod black ops iii'],
    # Crysis Remastered
    ['Crysis® Remastered', 'crysis remastered'],
    # Guns Gore and Cannoli
    ['Guns, Gore and Cannoli', 'guns gore and cannoli'],
    # Hotshots / WWE
    ['WWE 2K22','wwe 2k22'],['WWE 2K24','wwe 2k24'],
    # Horizon Chase
    ['Horizon Chase Turbo', 'horizon chase turbo'],
    # Hitman
    ['HITMAN™', 'hitman'],
    ['HITMAN™ 2', 'hitman 2'],
    ['HITMAN 3', 'hitman 3'],
    # Injustice
    ['Injustice: Gods Among Us', 'injustice gods among us ultimate edition'],
    # Sims
    ['The Sims™ 4', 'the sims 4'],
    # BioShock
    ['BioShock: The Collection', 'bioshock the collection'],
    # Minecraft
    ['Minecraft', 'minecraft','minecraft playstation 4 edition'],
    # DOOM
    ['DOOM Eternal', 'doom eternal'],
    # KNACK 2
    ['Knack 2', 'knack 2'],
    # Kingdom Hearts
    ['KINGDOM HEARTS HD 1.5+2.5 ReMIX',
     'kingdom hearts hd 1 5 2 5 remix'],
    # NBA
    ['NBA 2K17', 'nba 2k17'],
    ['NBA 2K18', 'nba 2k18'],
    ['NBA 2K19', 'nba 2k19'],
    # Mortal Kombat 11
    ['Mortal Kombat 11', 'mortal kombat 11'],
    # Ys
    ['Ys IX: Monstrum Nox', 'ys 9 monstrum nox','ys ix monstrum nox'],
    # Trials of Mana
    ['Trials of Mana', 'trials of mana'],
    # Sniper Ghost Warrior Contracts
    ['Sniper Ghost Warrior Contracts', 'sniper ghost warrior contracts'],
    # Saints Row
    ['Saints Row', 'saints row'],
    # Scarlet Nexus
    ['Scarlet Nexus', 'scarlet nexus'],
    # Tales of Arise
    ['Tales of Arise', 'tales of arise'],
    # Desperados III
    ['Desperados III', 'desperados iii','desperados 3'],
    # Sky Force
    ['Sky Force Anniversary', 'sky force anniversary'],
    # Killzone
    ['Killzone Shadow Fall', 'killzone shadow fall'],
    # DEAD OR ALIVE 6
    ['DEAD OR ALIVE 6', 'dead or alive 6'],
    # Sword and Fairy
    ['Sword and Fairy: Together Forever', 'sword and fairy together forever'],
    # Jurassic World Evolution 2
    ['Jurassic World Evolution 2', 'jurassic world evolution 2'],
    # Evil Within
    ['The Evil Within 2', 'the evil within 2'],
    ['The Evil Within',   'the evil within'],
    # Sand Land
    ['Sand Land', 'sand land'],
    # Star Wars Jedi
    ['STAR WARS Jedi: Survivor', 'star wars jedi survivor'],
    # Hogwarts
    ['Hogwarts Legacy', 'hogwarts legacy'],
    # Stranded Deep
    ['Stranded Deep', 'stranded deep'],
    # COD: Ghosts
    ['Call of Duty: Ghosts', 'call of duty ghosts','cod ghosts'],
    # Harry Potter
    ['LEGO Harry Potter: Years 1-4', 'harry potter years 1 4'],
    # Sims 4
    ['The Sims™ 4', 'the sims 4'],
    # SnowRunner
    ['SnowRunner', 'snowrunner'],
    # Tails of Iron
    ['Tails of Iron', 'tails of iron'],
    # Thief
    ['Thief', 'thief'],
    # Watch Dogs: Legion
    ['Watch Dogs: Legion', 'watch dogs legion'],
    # Hellpoint
    ['Hellpoint', 'hellpoint'],
    # Blasphemous
    ['Blasphemous', 'blasphemous'],
    # Kena
    ['Kena: Bridge of Spirits', 'kena bridge of spirits'],
    # Surviving the Aftermath
    ['Surviving the Aftermath', 'surviving the aftermath'],
    # The Survivalists
    ['The Survivalists', 'the survivalists'],
    # Borderlands GOTY
    ['Borderlands: Game of the Year',    'borderlands goty'],
]

# ── 2. Parse / normalize helpers ──────────────────────────────────────────────

def normalize(name: str) -> str:
    n = name.replace('™','').replace('®','').replace('©','').replace('–','-').replace('—','-')
    n = n.lower().strip()
    n = re.sub(r'[:\-–—.,!?\'\"()+&]', ' ', n)
    # roman-numeral suffixes  I II III IV V VI VII – keep them
    n = re.sub(r'\s+', ' ', n).strip()
    return n

def parse_file(path: str):
    """Return list of (original_line, name, game_id)."""
    entries = []
    with open(path, encoding='utf-8') as f:
        for raw in f:
            raw = raw.rstrip()
            if not raw:
                continue
            ids = re.findall(r'\[([A-Z]{2,6}\d{4,9})\]', raw)
            m   = re.match(r'^(.+?)\s*\[', raw)
            if m and ids:
                entries.append((raw, m.group(1).strip(), ids[-1]))
    return entries

# ── 3. Build alias → canonical-key map ───────────────────────────────────────

_ALIAS_MAP: dict[str, str] = {}   # normalised alias → canonical display name
_CANONICAL_SET: set[str] = set()  # all canonical display names

for group in _GAME_GROUPS:
    canonical = group[0]
    _CANONICAL_SET.add(canonical)
    for alias in group[1:]:
        _ALIAS_MAP[alias] = canonical
    # also map the normalised canonical itself
    _ALIAS_MAP[normalize(canonical)] = canonical

def get_group_key(name: str) -> str:
    """Return canonical group key for a game name, or the normalised name if no alias match."""
    n = normalize(name)
    return _ALIAS_MAP.get(n, n)

# ── 4. Group the entries ──────────────────────────────────────────────────────

def group_entries(entries):
    """Return OrderedDict: group_key → list of (original_line, name, id)."""
    groups = OrderedDict()
    order  = []   # keeps first-seen ordering

    for entry in entries:
        raw, name, gid = entry
        key = get_group_key(name)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(entry)

    return groups, order

# ── 5. Pick the best display name for a group ─────────────────────────────────

def pick_best_display(entries, alias_canonical: str | None) -> str:
    """
    If this group maps to a known canonical name, use that.
    Otherwise score the names.
    """
    if alias_canonical:
        return alias_canonical

    names = [n for _, n, _ in entries]

    def score(name):
        s = 0
        nl = name.lower()
        if '™' in name: s += 4
        if '®' in name: s += 3
        # mixed-case preferred over all-caps or all-lower
        if name != name.upper() and name != name.lower(): s += 2
        s += len(name) * 0.01
        if '(' in name or '[' in name: s -= 2
        if name[0].isupper(): s += 1
        # Penalise demo / test / trial versions being the representative
        if any(w in nl for w in ('network test','demo','trial','beta','preview')): s -= 10
        return s

    return max(names, key=score)

# ── 6. Generate the output text ───────────────────────────────────────────────

def generate_output(groups, order, path_out: str):
    lines = []
    single = 0
    grouped = 0

    for key in order:
        members = groups[key]

        if len(members) == 1:
            # unchanged
            lines.append(members[0][0])
            single += 1
        else:
            # key is either already a canonical name or a normalized auto-detected name
            # if it's a canonical from _GAME_GROUPS, use it directly
            canonical = key if key in _CANONICAL_SET else None
            display   = pick_best_display(members, canonical)

            # sort members: put the one with best name first
            def entry_score(e):
                n  = e[1]
                nl = n.lower()
                s  = 0
                if '™' in n: s += 4
                if '®' in n: s += 3
                if n != n.upper() and n != n.lower(): s += 2
                if any(w in nl for w in ('network test','demo','trial','beta','preview')): s -= 10
                return s

            members_sorted = sorted(members, key=entry_score, reverse=True)

            # first member gets the canonical display name
            primary = members_sorted[0]
            lines.append(f"{display} [{primary[2]}]")

            for extra in members_sorted[1:]:
                raw_extra, extra_name, extra_id = extra
                lines.append(f"  ↳ {extra_name} [{extra_id}]")

            lines.append("")   # blank line between groups
            grouped += 1

    with open(path_out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
        if not lines[-1]:
            pass  # trailing newline already there
        else:
            f.write('\n')

    print(f"Done. {single} single entries, {grouped} grouped games.")
    print(f"Output: {path_out}")

# ── 7. Main ───────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    import sys, os
    base = os.path.dirname(os.path.abspath(__file__))
    src  = os.path.join(base, 'games_list_for_covers.txt')
    dst  = os.path.join(base, 'games_list_for_covers_grouped.txt')

    entries        = parse_file(src)
    groups, order  = group_entries(entries)
    generate_output(groups, order, dst)
