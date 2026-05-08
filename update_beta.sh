#!/bin/bash
# Sync the WIP advanced_stats experience into docs/beta/.
#
# Workflow: build the new feature in docs/ as if it were going to ship, get it
# right locally, then run this script to copy the WIP files into docs/beta/
# (the unlisted-but-deployed preview directory). Production stays untouched
# until the feature is actually ready to merge into the main site.
#
# This script:
#   - copies the WIP advanced_stats.html / draft_order_2026.json into beta
#   - copies the latest index.html / stats.html into beta but adds the
#     "Advanced" nav link so the inter-page links work inside beta
#   - re-injects the BETA banner into every beta page

set -e

mkdir -p docs/beta
cp docs/advanced_stats.html docs/beta/advanced_stats.html 2>/dev/null || true
cp seasons/2026/draft_order_2026.json docs/beta/draft_order_2026.json
cp docs/index.html docs/beta/index.html
cp docs/stats.html docs/beta/stats.html

python3 - <<'PY'
import re

CSS_BLOCK = """
    .beta-banner {
      background: rgba(248, 184, 71, 0.10);
      border: 1px solid rgba(248, 184, 71, 0.32);
      border-radius: 6px;
      padding: 0.5rem 0.85rem;
      text-align: center;
      font-size: 0.74rem;
      color: #f8b847;
      margin-bottom: 1.25rem;
      letter-spacing: 0.05em;
    }
    .beta-banner a {
      color: #f8b847;
      text-decoration: underline;
      text-underline-offset: 2px;
    }
"""
BANNER = '    <div class="beta-banner">🧪 BETA — preview of WIP features · <a href="../">main site →</a></div>\n\n'

ADVANCED_NAV = '      <a href="advanced_stats.html">Advanced</a>\n'

for path in ("docs/beta/index.html", "docs/beta/stats.html", "docs/beta/advanced_stats.html"):
    with open(path) as fp:
        src = fp.read()
    if ".beta-banner" not in src:
        src = src.replace("  </style>", CSS_BLOCK + "  </style>", 1)
    if 'class="beta-banner"' not in src:
        src = src.replace('<div class="container">\n', '<div class="container">\n' + BANNER, 1)
    # Make sure the "Advanced" nav link is present in index/stats (advanced page already has its own)
    if path.endswith(("index.html", "stats.html")) and 'href="advanced_stats.html"' not in src:
        # Insert after the Stats nav link
        src = re.sub(r'(<a href="stats\.html"[^>]*>Stats</a>\n)', r"\1" + ADVANCED_NAV, src, count=1)
    with open(path, "w") as fp:
        fp.write(src)
    print(f"  refreshed {path}")
PY

echo
echo "Beta synced. Files now in docs/beta/:"
ls docs/beta/
