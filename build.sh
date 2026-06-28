#!/usr/bin/env bash
# Rebuild the algorithm-cheat-sheet PDF from flowchart.yaml. Run from anywhere.
set -e
cd "$(dirname "$0")"
python3 build.py
echo "Done. Open algorithm-cheat-sheet.pdf"
