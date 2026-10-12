# Reference generator

`tools/gen_reference.py` builds the language reference (`/reference/`) and the
pattern library (`/design/patterns/`) from a checkout of
[fizzbee-io/fizzbee](https://github.com/fizzbee-io/fizzbee). The output is not
committed. `content/reference/` and `content/design/patterns/` are gitignored
and regenerated on every deploy.

## Running it

```
python3 tools/gen_reference.py <path-to-fizzbee-checkout>          # full site
python3 tools/gen_reference.py <path-to-fizzbee-checkout> --sample # prototype sample only
hugo server
```

`./deploy.sh <frontend> <fizzbee>` runs the generator before building. The
fizzbee checkout becomes the published reference, so `deploy.sh`:

- stops if `examples/references/` has uncommitted changes. Pass
  `--allow-dirty` as the first argument to publish them anyway.
- prints which tag or `main` commit it is publishing, and warns if the checkout
  is on another branch or differs from `origin/main`.
- refuses a shallow clone, because page dates come from the fizzbee git
  history.

Tests: `python3 -m unittest discover -s tools`.

## What comes from where

| Output | Source in `examples/references/` |
|---|---|
| `/reference/` landing page | the intro paragraph of `README.md` |
| `/reference/language/<chapter>/` | one H2 section of `LANGUAGE_REFERENCE.md`, followed by the examples mapped to that chapter |
| `/reference/language/gotchas/` | `GOTCHAS.md` |
| `/reference/verification/`, `/reference/performance/` | `VERIFICATION_GUIDE.md`, `PERFORMANCE_GUIDE.md` |
| `/design/patterns/<slug>/` and its index | the `13-*` example directories |

Each example shows its title, description and "Demonstrates" topics from the
header comments, the spec, and the expected result cleaned from `baseline.txt`.
Examples without header comments fall back to their `README.md` entry and are
reported as warnings. Page `lastmod` comes from the fizzbee git log.

## Where to change things

Everything editable lives in `tools/gen_reference.py`. Never edit the
generated files: the next run overwrites them.

| To change | Edit |
|---|---|
| Which chapter an example goes in | `SECTION_CHAPTER` (by section), `EXAMPLE_CHAPTER` (single examples) |
| Page or pattern meta descriptions | `PAGE_DESCRIPTIONS`, `PATTERN_DESCRIPTIONS` |
| Patterns that link to an existing page instead of getting one | `OVERRIDES` (`placement: link`) |
| Pattern index categories | `PATTERN_CATEGORIES` |
| Menu label of the pattern library | `linkTitle` in the index front matter (the menu uses `linkTitle`, falling back to `title`; see `layouts/partials/menu-filetree.html`) |
| When the playground button is hidden | `PLAYGROUND_MAX_SECONDS`, `PLAYGROUND_MAX_NODES` |
| Chapters that are not published | `SKIP_CHAPTERS` |

A single example can also be overridden from the fizzbee repo with a
`page.yaml` next to its `.fizz` file (requires PyYAML):

```yaml
title: Custom title
description: Custom description
demonstrates: topics shown under the description
placement: embed        # embed | standalone | link | exclude
chapter: fairness       # for embed
url: /design/examples/two_phase_commit/   # for link
reason: why             # required for exclude
playground: false       # true | false
```

Descriptions follow the site style: lead with the topic and what the page
shows, name FizzBee only on pages about FizzBee itself, no em or en dashes, and
aim for 120 to 160 characters. A chapter with no hand-written description gets
one derived from its first paragraph, and the run warns about it.

## Checks the run makes

- **Errors** stop the run before any output changes: an example with no
  `.fizz` file, an unknown chapter, an invalid override, or a `page.yaml`
  without PyYAML installed. Pages are written to a temporary directory and
  replace the old output only after every page has been written.
- **Warnings** are printed but don't stop the run: examples without header
  comments, unresolved `#anchor` links, chapters without a hand-written
  description, a README whose intro can't be found, and titles or
  descriptions shared by two pages anywhere on the site.
