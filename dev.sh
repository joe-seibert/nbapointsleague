#!/bin/bash
set -e
SEASON=${SEASON:-2026}

uv run points_league.py
cp seasons/$SEASON/data/pointsleague_$SEASON.json docs/
cp seasons/$SEASON/data/full_points_table_$SEASON.json docs/
cp seasons/$SEASON/data/undrafted_$SEASON.json docs/
cp seasons/$SEASON/data/all_players_$SEASON.json docs/

echo "Data ready. Starting server at http://localhost:8765"
python3 -m http.server 8765 --directory docs
