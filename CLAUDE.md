# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NBA Points League is a Python fantasy basketball points league tracker. It fetches NBA player stats via the `nba_api` package, aggregates scores by fantasy team, outputs JSON and CSV files, and syncs data to Google Sheets.

## Commands

```bash
# Install dependencies
uv sync

# Run data aggregation (fetches NBA stats, outputs JSON + CSV to data/)
uv run points_league_2024.py

# Update Google Sheet from generated JSON data
uv run update_points_league.py
```

Dependencies are managed via `pyproject.toml` and `uv.lock`. There are no test or lint commands configured for this project.

## Architecture

**Data pipeline flow:**

```
nba_api (NBA stats) → points_league_2024.py → data/*.json + data/*.csv
                                                       ↓
                                              update_points_league.py → Google Sheets
```

**Core scripts:**
- `points_league_2024.py` — Fetches playoff stats from `nba_api`, matches players to fantasy teams defined in `drafted_players_2024.yml`, and exports JSON + CSV to the `data/` directory.
- `update_points_league.py` — Reads `data/full_points_table_2024.json`, authenticates via OAuth (`credentials.json` / `token.pickle`), and batch-updates a Google Sheet (one sheet per team). Does not call the NBA API directly.

**Configuration:**
- `drafted_players_2024.yml` — YAML file mapping team owner names to lists of drafted player names.
- `SHEET_NAME_MAP` in `update_points_league.py` maps team names to Google Sheet tab names.
- Google Sheet ID is hardcoded in `update_points_league.py`.

**Automation (two separate workflows):**
- `.github/workflows/update-data.yml` — Runs `points_league_2024.py` daily at 12:05 UTC, commits data files, and pushes.
- `.github/workflows/update-sheets.yml` — Triggered after data workflow succeeds (or manually). Runs `update_points_league.py` to sync to Google Sheets.

## Key Details

- Python 3.8+ required
- Six fantasy teams: Andrew, Jono, Connor, Joe, Julian, Sam
- All generated data lives in the `data/` directory (JSON is the primary format, CSV for convenience)
- Jupyter notebooks in the repo are for exploration/analysis, not part of the production pipeline
- Sensitive files (`credentials.json`, `token.pickle`) are present in the repo for Google Sheets OAuth
