#!/usr/bin/env bash
set -euo pipefail
manifest_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
python3 "$manifest_root/ci/validate-manifests.py"
python3 -m unittest discover -s "$manifest_root/tests" -v

