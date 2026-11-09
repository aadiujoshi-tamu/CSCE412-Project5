#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" != "--approve-controlled-failure" ]]; then
  echo "Refusing to change infrastructure without --approve-controlled-failure."
  exit 2
fi

echo "This script intentionally does not implement a destructive DNS or bucket-policy mutation."
echo "Use it as a documented approval gate before running a reviewed, environment-specific failure experiment."
echo "Recommended experiment: temporarily remove the CloudFront A/AAAA aliases, run scripts/verify.sh to capture failure, restore the same aliases, then re-run verification."
