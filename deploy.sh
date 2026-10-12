#!/usr/bin/env bash
# Build the Hugo site and assemble the Firebase Hosting deploy dir via the
# frontend repo's build-hosting.sh. Builds into a fresh temp directory every
# run: Hugo never deletes from its destination, so reusing ./public/ would
# let stale pages reach production.
#
# The language reference (/reference/) and pattern library (/design/patterns/)
# are generated from a fizzbee checkout first; they are not committed here.
#
# Usage: ./deploy.sh <path-to-frontend-checkout> <path-to-fizzbee-checkout>
# Then:  cd <frontend> && firebase deploy --only hosting
set -euo pipefail

USAGE="usage: deploy.sh <path-to-frontend-checkout> <path-to-fizzbee-checkout>"
FRONTEND="${1:?$USAGE}"
FIZZBEE="${2:?$USAGE}"
REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"

[[ -x "$FRONTEND/build-hosting.sh" ]] \
  || { echo "ERROR: $FRONTEND/build-hosting.sh not found or not executable — pull latest main in the frontend checkout" >&2; exit 1; }

[[ "$(git -C "$REPO_ROOT" rev-parse --is-shallow-repository)" == "false" ]] \
  || { echo "ERROR: shallow clone; sitemap lastmod needs full git history (run: git fetch --unshallow)" >&2; exit 1; }

[[ "$(git -C "$FIZZBEE" rev-parse --is-shallow-repository)" == "false" ]] \
  || { echo "ERROR: $FIZZBEE is a shallow clone; reference lastmod needs full git history (run: git -C $FIZZBEE fetch --unshallow)" >&2; exit 1; }

python3 "$REPO_ROOT/tools/gen_reference.py" "$FIZZBEE"

BUILD_ROOT="$(mktemp -d)"
trap 'rm -rf "$BUILD_ROOT"' EXIT

hugo --source "$REPO_ROOT" --destination "$BUILD_ROOT/public"

"$FRONTEND/build-hosting.sh" "$BUILD_ROOT/public"

echo
echo "To deploy: cd $FRONTEND && firebase deploy --only hosting"
