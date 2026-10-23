# Fizzbee Website

The hugo markdown for the main fizzbee website

## Generated reference pages

`/reference/` (the language reference) and `/design/patterns/` (the pattern
library) are generated from a checkout of
[fizzbee-io/fizzbee](https://github.com/fizzbee-io/fizzbee) and are not
committed. Generate them before running or building the site:

```
python3 tools/gen_reference.py <path-to-fizzbee-checkout>
```

Page descriptions, placements and other overrides live in
`tools/gen_reference.py`; edit them there, not in the generated files.
See [docs/reference-generator.md](docs/reference-generator.md) for what comes
from where and how to change it.
Tests: `python3 -m unittest discover -s tools`.

## To run locally
just the static site
```
hugo -D server
```
To make it run along with the playground (local dev only; the frontend's
node app serves `public/`):
```
hugo
cp -R public/ ../frontend/public
```

## To deploy

Build the site and assemble the Firebase Hosting deploy dir in the frontend
checkout (the frontend repo's README documents the checkout location):

```
./deploy.sh <path-to-frontend-checkout> <path-to-fizzbee-checkout>
```

The fizzbee checkout is published as the official reference: uncommitted
changes under `examples/references/` stop the deploy (pass `--allow-dirty`
first to override), and a checkout not on up-to-date `main` or a release tag
prints a warning.

Then deploy from that checkout:

```
firebase deploy --only hosting
```

Once the deploy is live, notify search engines (IndexNow: Bing, Yandex and
others; Google is covered by the sitemap's lastmod dates) of the changed URLs:

```
./notify-indexnow.sh
```

It diffs the live sitemap against the last-notified one (`.indexnow-state.xml`,
local only) and submits new, updated and removed URLs; `--dry-run` shows the
list without submitting. A fresh checkout has no state file and submits every
sitemap URL once, which is harmless.

`deploy.sh` first regenerates the reference pages from the fizzbee checkout
(use an up-to-date `main` with full history), then builds into a fresh temp directory on every run (never `./public/`,
which Hugo does not clean) and hands the output to the frontend repo's
`build-hosting.sh`, which assembles the hosting dir from scratch so stale
files from earlier deploys cannot accumulate. The script never deploys by
itself.
