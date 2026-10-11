#!/usr/bin/env bash
# Build the Hugo site and assemble the Firebase Hosting deploy dir via the
# frontend repo's build-hosting.sh. Builds into a fresh temp directory every
# run: Hugo never deletes from its destination, so reusing ./public/ would
# let stale pages reach production.
#
# Usage: ./deploy.sh <path-to-frontend-checkout>
# Then:  cd <frontend> && firebase deploy --only hosting
set -euo pipefail

FRONTEND="${1:?usage: deploy.sh <path-to-frontend-checkout>}"
REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"

[[ -x "$FRONTEND/build-hosting.sh" ]] \
  || { echo "ERROR: $FRONTEND/build-hosting.sh not found or not executable — pull latest main in the frontend checkout" >&2; exit 1; }

BUILD_ROOT="$(mktemp -d)"
trap 'rm -rf "$BUILD_ROOT"' EXIT

hugo --source "$REPO_ROOT" --destination "$BUILD_ROOT/public"

"$FRONTEND/build-hosting.sh" "$BUILD_ROOT/public"

echo
echo "To deploy: cd $FRONTEND && firebase deploy --only hosting"
