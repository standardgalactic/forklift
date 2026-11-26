#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p reports/verification
python3 -m unittest discover -s tests -v 2>&1 | tee reports/verification/tests.txt
