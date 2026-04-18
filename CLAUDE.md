# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NBA Points League is a Python fantasy basketball points league tracker. It fetches NBA player stats via the `nba_api` package, aggregates scores by fantasy team, and outputs JSON and CSV files.

## Commands

```bash
# Install dependencies
uv sync

# Run data aggregation for the active season (default: 2026)
uv run points_league.py

# Run for a specific season
SEASON=2024 uv run points_league.py
```

Dependencies are managed via `pyproject.toml` and `uv.lock`. There are no test or lint commands configured for this project.

## Architecture

**Data pipeline flow:**

```
nba_api (NBA stats) → points_league.py → seasons/<SEASON>/data/*.json + *.csv
```

The active season is controlled by the `SEASON` env var (defaults to `2026`).

**Core script:**
- `points_league.py` — Fetches playoff stats from `nba_api`, matches players to fantasy teams defined in `seasons/<SEASON>/drafted_players_<SEASON>.yml`, and exports JSON + CSV to `seasons/<SEASON>/data/`.

**Configuration:**
- `seasons/<SEASON>/drafted_players_<SEASON>.yml` — YAML file mapping team owner names to lists of drafted player names.

**Repo structure:**
- `seasons/` — Per-season directories containing rosters, notebooks, and generated data.
- `notebooks/` — Standalone exploratory notebooks (e.g., API testing).

**Automation:**
- `.github/workflows/update-data.yml` — Runs `points_league.py` daily at 12:05 UTC, commits data files, and pushes. Season is set via env var in the workflow.

## Key Details

- Minimize `nba_api` calls — the API throttles aggressively. Cache responses locally (e.g., to JSON) and reuse them rather than making repeated calls.
- Python 3.8+ required
- Six fantasy teams: Andrew, Jono, Connor, Joe, Julian, Sam
- All generated data lives in `seasons/<SEASON>/data/` (JSON is the primary format, CSV for convenience)
