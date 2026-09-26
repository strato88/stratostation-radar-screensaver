#!/usr/bin/env bash
#
# desplegar.sh — update the production clone to the latest `main`.
#
# This is THE deploy script: the self-hosted GitHub Actions workflow runs it,
# and you can run it by hand on the station server (for example when Actions
# is unavailable), so both paths always do exactly the same thing:
#
#   bash /path/to/production/clone/scripts/desplegar.sh          # deploy
#   bash /path/to/production/clone/scripts/desplegar.sh --check  # show what would change, touch nothing
#
# The production clone is DEPLOY_PATH if set, otherwise the clone this script
# lives in. It may carry permanent local customizations (a hand-edited CONFIG
# block, extra pages…) that will never match main — that's expected. So this
# fast-forwards when it can, does a real merge when main and the local
# customizations don't overlap, and only when the same lines are touched on
# both sides does it back out cleanly (never leaving conflict markers live in
# files the server is serving) and exit with an error, for you to resolve by
# hand over SSH.
#
set -euo pipefail

DEPLOY_PATH="${DEPLOY_PATH:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
BRANCH="${DEPLOY_BRANCH:-main}"
SERVICE="${DEPLOY_SERVICE:-adsb-radar.service}"

check=0
case "${1:-}" in
  "") ;;
  --check) check=1 ;;
  -h|--help) sed -n '2,19p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
  *) echo "Unknown option: $1 (see --help)" >&2; exit 2 ;;
esac

cd "$DEPLOY_PATH"

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "✗ $DEPLOY_PATH has uncommitted local changes. Commit or stash them, then run this again." >&2
  git status --short >&2
  exit 1
fi

git fetch --quiet origin "$BRANCH"
before="$(git rev-parse HEAD)"

if [ "$check" = 1 ]; then
  pending="$(git log --oneline "HEAD..origin/$BRANCH")"
  if [ -z "$pending" ]; then
    echo "Up to date with origin/$BRANCH (${before:0:7})."
  else
    echo "Would bring in from origin/$BRANCH:"
    echo "$pending"
  fi
  exit 0
fi

if git merge --quiet --ff-only "origin/$BRANCH" 2>/dev/null; then
  echo "Fast-forwarded to $(git rev-parse --short HEAD)."
elif git merge --quiet --no-edit "origin/$BRANCH"; then
  echo "Merged origin/$BRANCH into local customizations (new commit $(git rev-parse --short HEAD))."
else
  git merge --abort
  echo "✗ origin/$BRANCH conflicts with local customizations in $DEPLOY_PATH." >&2
  echo "  Production files were left untouched. Resolve the conflict by hand" >&2
  echo "  (git merge origin/$BRANCH, fix the files, git add, git commit), then run this again." >&2
  exit 1
fi

# Optional: only relevant if you installed examples/adsb-radar.service.
# Harmless (and non-fatal) if that unit isn't installed.
if systemctl list-unit-files "$SERVICE" 2>/dev/null | grep -q "$SERVICE"; then
  sudo -n systemctl restart "$SERVICE" && echo "Restarted $SERVICE." \
    || echo "Note: could not restart $SERVICE (needs passwordless sudo for that command)."
fi
