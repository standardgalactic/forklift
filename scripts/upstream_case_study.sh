#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m forklift . --revision "${1:-upstream/main}" --base "${2:-89d8b41}" --output "${3:-reports/upstream}" --plots
