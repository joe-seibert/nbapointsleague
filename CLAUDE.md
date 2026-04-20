# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NBA Points League is a Python fantasy basketball points league tracker. It fetches NBA player stats via the `nba_api` package, aggregates scores by fantasy team, outputs JSON and CSV files, and syncs results to a Google Sheet.

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
- `points_league.py` — Fetches playoff stats from `nba_api`, matches players to fantasy teams defined in `seasons/<SEASON>/drafted_players_<SEASON>.yml`, and exports JSON + CSV to `seasons/<SEASON>/data/`. Uses `WEBSHARE_PROXY` env var when set (required in CI, optional locally).
- `update_points_league.py` — Reads `seasons/<SEASON>/data/full_points_table_<SEASON>.json` and batch-updates a Google Sheet (one tab per team). Uses Google Service Account auth via `GOOGLE_SERVICE_ACCOUNT` env var in CI.

**Configuration:**
- `seasons/<SEASON>/drafted_players_<SEASON>.yml` — YAML file mapping team owner names to lists of drafted player names.
- Google Sheet ID is hardcoded in `update_points_league.py`.

**Repo structure:**
- `seasons/` — Per-season directories containing rosters and notebooks. Generated data (`seasons/*/data/`) is gitignored on `main`; live data lives on the `data` branch.
- `notebooks/` — Standalone exploratory notebooks (e.g., API testing).
- `docs/` — Static GitHub Pages site (`index.html`) that fetches JSON from the `data` branch via raw.githubusercontent.com.

**Branches:**
- `main` — Code, config, and the static site. **Direct pushes are blocked; all changes require a pull request.**
- `data` — Holds only `pointsleague_<SEASON>.json` and `full_points_table_<SEASON>.json`. Force-pushed daily by the workflow; no meaningful history.

**Automation (two chained workflows):**
- `.github/workflows/update-data.yml` — Runs `points_league.py` daily at 12:05 UTC via proxy, then force-pushes the generated JSON to the `data` branch. Retries up to 3 times on failure.
- `.github/workflows/update-sheets.yml` — Triggers automatically after the data workflow succeeds (or manually). Runs `update_points_league.py` to sync to Google Sheets.

**GitHub Secrets:**
- `WEBSHARE_PROXY` — Proxy URL for NBA API access from CI (stats.nba.com blocks cloud IPs).
- `GOOGLE_SERVICE_ACCOUNT` — Service account JSON for Google Sheets API auth.

## Key Details

- Minimize `nba_api` calls — the API throttles aggressively. Cache responses locally (e.g., to JSON) and reuse them rather than making repeated calls.
- Python 3.8+ required
- Six fantasy teams: Andrew, Jono, Connor, Joe, Julian, Sam
- All generated data lives in `seasons/<SEASON>/data/` (JSON is the primary format, CSV for convenience)
