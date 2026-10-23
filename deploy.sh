#!/usr/bin/env bash
# Build the Hugo site and assemble the Firebase Hosting deploy dir via the
# frontend repo's build-hosting.sh. Builds into a fresh temp directory every
# run: Hugo never deletes from its destination, so reusing ./public/ would
# let stale pages reach production.
#
# The language reference (/reference/) and pattern library (/design/patterns/)
# are generated from a fizzbee checkout first; they are not committed here.
#
# The fizzbee checkout is what gets published as the official reference, so
# uncommitted changes under examples/references/ stop the deploy (override
# with --allow-dirty), and a checkout that is not on up-to-date main or a
# release tag gets a loud warning.
#
# Usage: ./deploy.sh [--allow-dirty] <path-to-frontend-checkout> <path-to-fizzbee-checkout>
# Then:  cd <frontend> && firebase deploy --only hosting
set -euo pipefail

USAGE="usage: deploy.sh [--allow-dirty] <path-to-frontend-checkout> <path-to-fizzbee-checkout>"
ALLOW_DIRTY=false
if [[ "${1:-}" == "--allow-dirty" ]]; then ALLOW_DIRTY=true; shift; fi
FRONTEND="${1:?$USAGE}"
FIZZBEE="${2:?$USAGE}"
REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"

[[ -x "$FRONTEND/build-hosting.sh" ]] \
  || { echo "ERROR: $FRONTEND/build-hosting.sh not found or not executable — pull latest main in the frontend checkout" >&2; exit 1; }

[[ "$(git -C "$REPO_ROOT" rev-parse --is-shallow-repository)" == "false" ]] \
  || { echo "ERROR: shallow clone; sitemap lastmod needs full git history (run: git fetch --unshallow)" >&2; exit 1; }

[[ "$(git -C "$FIZZBEE" rev-parse --is-shallow-repository)" == "false" ]] \
  || { echo "ERROR: $FIZZBEE is a shallow clone; reference lastmod needs full git history (run: git -C $FIZZBEE fetch --unshallow)" >&2; exit 1; }

# What is about to be published as the reference.
if [[ -n "$(git -C "$FIZZBEE" status --porcelain -- examples/references)" ]]; then
  if $ALLOW_DIRTY; then
    echo "WARNING: $FIZZBEE has uncommitted changes in examples/references/; publishing them (--allow-dirty)" >&2
  else
    echo "ERROR: $FIZZBEE has uncommitted changes in examples/references/:" >&2
    git -C "$FIZZBEE" status --short -- examples/references >&2
    echo "Commit or stash them, or pass --allow-dirty to publish them anyway." >&2
    exit 1
  fi
fi
FIZZBEE_SHA="$(git -C "$FIZZBEE" rev-parse --short HEAD)"
FIZZBEE_BRANCH="$(git -C "$FIZZBEE" rev-parse --abbrev-ref HEAD)"
FIZZBEE_TAG="$(git -C "$FIZZBEE" describe --tags --exact-match 2>/dev/null || true)"
if [[ -n "$FIZZBEE_TAG" ]]; then
  echo "Reference source: fizzbee tag $FIZZBEE_TAG ($FIZZBEE_SHA)"
elif [[ "$FIZZBEE_BRANCH" == "main" ]]; then
  if git -C "$FIZZBEE" fetch -q origin main 2>/dev/null; then
    if [[ "$(git -C "$FIZZBEE" rev-parse HEAD)" != "$(git -C "$FIZZBEE" rev-parse origin/main)" ]]; then
      echo "WARNING: fizzbee main ($FIZZBEE_SHA) differs from origin/main ($(git -C "$FIZZBEE" rev-parse --short origin/main)); run git pull to publish the latest reference" >&2
    else
      echo "Reference source: fizzbee main ($FIZZBEE_SHA), up to date with origin"
    fi
  else
    echo "WARNING: could not fetch fizzbee origin/main; publishing local main ($FIZZBEE_SHA) without checking it is current" >&2
  fi
else
  echo "WARNING: fizzbee checkout is on '$FIZZBEE_BRANCH' ($FIZZBEE_SHA), not main or a release tag" >&2
fi

python3 "$REPO_ROOT/tools/gen_reference.py" "$FIZZBEE"

BUILD_ROOT="$(mktemp -d)"
trap 'rm -rf "$BUILD_ROOT"' EXIT

hugo --source "$REPO_ROOT" --destination "$BUILD_ROOT/public"

python3 "$REPO_ROOT/tools/check_site.py" "$BUILD_ROOT/public"

"$FRONTEND/build-hosting.sh" "$BUILD_ROOT/public"

echo
echo "To deploy: cd $FRONTEND && firebase deploy --only hosting"
echo "Then notify search engines: $REPO_ROOT/notify-indexnow.sh"
