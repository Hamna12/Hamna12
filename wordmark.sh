#!/usr/bin/env bash
# Regenerate the 3D wordmark image (wordmark.svg) shown on the profile.
# Usage:
#   ./wordmark.sh                # renders "HAMNA"
#   ./wordmark.sh Hamna          # render a different name/casing
set -e
NAME="${1:-HAMNA}"
echo ">> rendering wordmark: $NAME"
WORDMARK_TEXT="$NAME" python3 scripts/make_wordmark_svg.py wordmark.svg
echo ">> done -> wordmark.svg"
