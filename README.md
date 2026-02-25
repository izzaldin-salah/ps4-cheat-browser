# PS4 Cheat Browser — GoldHEN

![Version](https://img.shields.io/badge/version-2.1-blue)
![Games](https://img.shields.io/badge/games-1700%2B-green)
![License](https://img.shields.io/badge/license-MIT-orange)

A modern, fully client-side web application for browsing, searching, and exploring the complete **GoldHEN Cheat Repository** for PlayStation 4 (PS4) games. No installation required — just open the HTML file in any browser and sync once from GitHub.

---

## Overview

This project provides a polished, responsive interface to the [GoldHEN Cheat Repository](https://github.com/GoldHEN/GoldHEN_Cheat_Repository), giving PS4 hobbyists and homebrewers an organized, searchable reference for all available game cheats organized by game title, CUSA ID, and firmware version.

The PS4 Cheat Browser solves a common pain point: the raw JSON cheat files from the repository are hard to navigate manually. This browser makes the entire collection instantly searchable and visually accessible, with game cover art fetched automatically from the PlayStation Store.

---

## Features

### Core Browser (`index.html`)
- **1,700+ Games** — Full coverage of the GoldHEN cheat repository across 1,702 JSON cheat files
- **Instant Search** — Real-time filtering by game title or CUSA ID as you type
- **Game Cover Art** — Automatically fetches official cover images from the PlayStation Store
- **Game Grouping** — Intelligently groups regional variants and re-releases of the same game (e.g., multiple CUSA IDs for *Bloodborne*, *The Witcher 3*, *GTA V*)
- **CUSA ID Tabs** — When a game has multiple regional releases, each CUSA ID is presented as a selectable tab with its associated firmware versions
- **Version Accordion** — Cheat entries are organized into collapsible sections by game version for easy navigation
- **Favorites System** — Star games to save them for quick access, persisted in browser `localStorage`
- **Offline-First** — After the initial sync from GitHub, all data is cached in `localStorage`; no internet required to browse
- **Sync from GitHub** — One-click sync pulls the latest cheat data directly from the GoldHEN repository
- **Local JSON Upload** — Load individual or bulk JSON cheat files directly from your file system via file picker
- **Dark/Light UI** — Clean, modern interface built with CSS custom properties; glassmorphism nav bar; smooth animations

### Python Utilities
| Script | Purpose |
|--------|---------|
| `ps4_cover_scraper.py` | Scrapes official game cover art from the PlayStation Store API and saves them locally |
| `generate_grouped_list.py` | Generates a grouped, deduplicated game list consolidating regional variants under canonical titles |
| `process_games_list.py` | Processes and normalizes the raw game list from cheat files |
| `parse_grouped_to_js.py` | Converts grouped game data into a JavaScript-ready output format |
| `analyze_groups.py` | Analyzes grouping quality and coverage statistics |

---

## Project Structure

```
ps4-cheat-browser/
├── index.html                      # Main browser application (standalone)
├── cusa_id_map_output.js           # Auto-generated CUSA ID → game name mapping
├── all_cheats_list.txt             # Flat list of all cheat entries
├── games_list_for_covers.txt       # Game list for cover art scraping
├── games_list_for_covers_grouped.txt # Grouped game list after deduplication
├── ps4_cover_scraper.py            # Python: cover art scraper
├── generate_grouped_list.py        # Python: game grouping logic
├── process_games_list.py           # Python: game list processor
├── parse_grouped_to_js.py          # Python: convert data to JS format
├── analyze_groups.py               # Python: grouping analysis
└── json/
    ├── CUSA00002_01.00.json        # Cheat file: CUSA ID + version
    ├── CUSA00004_01.07.json
    └── ... (1,702 total JSON files)
```

---

## Getting Started

### Prerequisites
- A modern web browser (Chrome, Firefox, Edge)
- Internet connection for the initial sync and cover art loading (offline use supported after first sync)

### Usage

1. **Clone or download** this repository
2. **Open** `index.html` in your browser
3. Click **"Sync from GitHub"** — this fetches the latest cheat list from the GoldHEN repository
4. Browse, search, and explore over 1,700 PS4 games with their cheat codes

### Running Python Scripts

```bash
# Install dependencies
pip install requests

# Scrape cover art
python ps4_cover_scraper.py

# Generate grouped game list
python generate_grouped_list.py
```

### Supabase Setup (Optional)

The browser supports loading cheat data from a Supabase backend. To enable it, set your credentials in the browser console once:

```js
localStorage.setItem('supabaseUrl', 'https://your-project.supabase.co');
localStorage.setItem('supabaseKey', 'your-anon-key');
```

---

## Cheat JSON Format

Each cheat file in the `json/` directory follows the GoldHEN standard format:

```json
{
  "name": "Game Title",
  "region": "CUSA00000",
  "version": "01.00",
  "cheats": [
    {
      "name": "Infinite Health",
      "type": "constant",
      "address": "0x...",
      "value": "..."
    }
  ]
}
```

---

## Data Source

All cheat data is sourced from the **[GoldHEN Cheat Repository](https://github.com/GoldHEN/GoldHEN_Cheat_Repository)**, a community-maintained collection of cheat codes for PS4 games compatible with the GoldHEN homebrew enabler.

> **Disclaimer:** This tool is intended for educational and personal use. Game cheats are only functional on jailbroken PS4 consoles running GoldHEN firmware. The authors of this project do not endorse piracy or any violation of PlayStation's terms of service.

---

## Contributing

Contributions are welcome! If you'd like to improve the UI, add new features, or fix bugs:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'Add my feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

The cheat data (`json/` folder) is sourced from the GoldHEN Cheat Repository and is subject to its own license terms.

---

## Acknowledgements

- **[GoldHEN Team](https://github.com/GoldHEN)** — For the cheat repository and the PS4 homebrew enabler
- **[Supabase](https://supabase.com)** — Open-source Firebase alternative used for cloud storage
- **Google Fonts** — Barlow Condensed & Inter typefaces used in the UI
