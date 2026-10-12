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

Then deploy from that checkout:

```
firebase deploy --only hosting
```

`deploy.sh` first regenerates the reference pages from the fizzbee checkout
(use an up-to-date `main` with full history), then builds into a fresh temp directory on every run (never `./public/`,
which Hugo does not clean) and hands the output to the frontend repo's
`build-hosting.sh`, which assembles the hosting dir from scratch so stale
files from earlier deploys cannot accumulate. The script never deploys by
itself.
