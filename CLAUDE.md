# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NBA Points League is a Python fantasy basketball points league tracker. It fetches NBA player stats via the `nba_api` package, aggregates scores by fantasy team, outputs JSON and CSV files, and syncs data to Google Sheets.

## Commands

```bash
# Install dependencies
uv sync

# Run data aggregation for the active season (default: 2026)
uv run points_league.py

# Run for a specific season
SEASON=2024 uv run points_league.py

# Update Google Sheet from generated JSON data
uv run update_points_league.py
```

Dependencies are managed via `pyproject.toml` and `uv.lock`. There are no test or lint commands configured for this project.

## Architecture

**Data pipeline flow:**

```
nba_api (NBA stats) → points_league.py → seasons/<SEASON>/data/*.json + *.csv
                                                    ↓
                                         update_points_league.py → Google Sheets
```

The active season is controlled by the `SEASON` env var (defaults to `2026`).

**Core scripts:**
- `points_league.py` — Fetches playoff stats from `nba_api`, matches players to fantasy teams defined in `seasons/<SEASON>/drafted_players_<SEASON>.yml`, and exports JSON + CSV to `seasons/<SEASON>/data/`.
- `update_points_league.py` — Reads `seasons/<SEASON>/data/full_points_table_<SEASON>.json`, authenticates via OAuth (`credentials.json` / `token.pickle`), and batch-updates a Google Sheet (one sheet per team). Does not call the NBA API directly.

**Configuration:**
- `seasons/<SEASON>/drafted_players_<SEASON>.yml` — YAML file mapping team owner names to lists of drafted player names.
- `SHEET_NAME_MAP` in `update_points_league.py` maps team names to Google Sheet tab names.
- Google Sheet ID is hardcoded in `update_points_league.py`.

**Repo structure:**
- `seasons/` — Per-season directories containing rosters, notebooks, and generated data.
- `notebooks/` — Standalone exploratory notebooks (e.g., API testing).

**Automation (two separate workflows):**
- `.github/workflows/update-data.yml` — Runs `points_league.py` daily at 12:05 UTC, commits data files, and pushes. Season is set via env var in the workflow.
- `.github/workflows/update-sheets.yml` — Triggered after data workflow succeeds (or manually). Runs `update_points_league.py` to sync to Google Sheets.

## Key Details

- Python 3.8+ required
- Six fantasy teams: Andrew, Jono, Connor, Joe, Julian, Sam
- All generated data lives in `seasons/<SEASON>/data/` (JSON is the primary format, CSV for convenience)
- Sensitive files (`credentials.json`, `token.pickle`) are present in the repo for Google Sheets OAuth
