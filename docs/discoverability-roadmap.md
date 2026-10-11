# FizzBee Discoverability Roadmap

**Goal:** Get FizzBee's tutorials, language reference and examples found by Google, Bing and AI assistants (ChatGPT, Claude, Perplexity, Copilot, coding agents), and get models to know FizzBee syntax well enough to write correct specs.

**Scope:** fizzbee.io (docs + playground), the `fizzbee-io/fizzbee` repo (examples, reference), fizzbee.ai (SaaS), blog.fizzbee.ai.

**Status:** In progress. Phase 0 and Phase 1.1 complete (Oct 11, 2026); next: Phase 1.2–1.6. Originally drafted Oct 10, 2026. Based on an audit of the `fizzbee-io/website` and `fizzbee-io/fizzbee` repos and the live sites, plus two rounds of review by ChatGPT (accepted changes: stricter live-site acceptance tests, prototype-first generator, expanded validation, per-example overrides, D4 migration criterion, per-page Markdown). The `fizzbee-io/frontend` repo (private) was **not** reviewed, so anything about deployment is inferred from the website README.

### How to use this document

- **Reviewers (human or AI):** Sections 2–4 are the findings and target design; Section 6 lists open decisions with recommendations. Challenge anything there, especially the recommendations that differ from conventional SEO advice (D1, D3).
- **Claude Code:** work one phase (or sub-step) per session, in the order in Section 7. Each sub-step has an "Accept when" criterion; verify it before finishing. Before changing anything, re-check the current state of the repo, since findings here are a snapshot from Oct 10, 2026. Don't start a phase whose decisions (Section 6) are still open; ask instead.
- **Suggested location:** commit this file to the website repo (e.g. `docs/discoverability-roadmap.md`) and tick the checkboxes / update the status as phases complete.

---

## 1. Summary

The content already exists. The problem is that most of it lives only in GitHub, where search engines don't treat it as documentation and many crawlers can't browse it at all. Meanwhile, fizzbee.io has a few technical problems that make the content it *does* have less effective.

The plan, in one line: **make fizzbee.io the canonical home for all FizzBee documentation, generate pages automatically from the fizzbee repo, fix the technical issues, then tell search engines and AI tools about it.**

Biggest findings:

1. **~110 reference examples, a 2,390-line language reference, and three guides are not on fizzbee.io at all.** They exist only in `examples/references/` in the fizzbee repo. (Other repo content — `docs/`, `examples/tutorials/`, `examples/comparisons/` — is outdated and out of scope.)
2. **98 of the 110 examples already have structured header comments** (title, one-line description, topics). Pages can be generated from them with almost no hand-writing.
3. **The deploy process never deletes old pages.** A full duplicate of the homepage is live at `/_index_bak/`.
4. **fizzbee.io has no canonical tags**, and 15 pages (including the homepage) have no meta description.
5. **fizzbee.ai returns its homepage with HTTP 200 for every URL**, including `/sitemap.xml`. It effectively has no sitemap and every typo URL looks like a duplicate homepage.

---

## 2. Current state (audit findings)

### 2.1 fizzbee.io

| Area | Finding | Impact |
|---|---|---|
| Stack | Hugo, `hugo-geekdoc` theme, repo `fizzbee-io/website`. 37 content pages. | — |
| Deploy | README says: `hugo` then `cp -R public/ ../frontend/public`, then build the Node Docker image (Cloud Run; Firebase likely in front). | `cp -R` adds files but never removes them. |
| Stale pages | `/_index_bak/`, `/_index_bak1/`, `/posts/where-is-the-beef/` are live and in the sitemap but no longer exist in the repo. `/_index_bak/` is a full copy of the homepage (same title and H1). | Duplicate content; junk in the sitemap. |
| Canonical tags | The theme does not output `<link rel="canonical">`. | Google has to guess the canonical copy (worse with the duplicates above). |
| Meta descriptions | Missing on 15 pages: homepage, `/design/`, `/design/examples/` and 8 of its 10 examples, `/design/tutorials/`, `frontmatter`, `limitations`, `/posts/` and both posts. Full list in Appendix A. | Google writes its own snippets; lower click-through. |
| Sitemap | Most pages have no `<lastmod>`. Tag pages (`/tags/...`) are listed even though robots.txt disallows `/tags/*`. | Contradictory signals; crawlers can't tell what changed. |
| robots.txt | Generated from the theme template: allows all except `/tags/*`. No explicit AI-bot rules (fine, `*` allows them). | OK. |
| Code rendering | The `{{< fizzbee >}}` shortcode renders specs as real highlighted HTML, with "Run in playground" layered on via JS. | Good — crawlers can read the code. No change needed. |
| 404s | Unknown URLs appear to return a real error (good). | — |
| llms.txt | Returns 404. | Minor; cheap to add. |
| Analytics | Google tag + GTM present with consent mode. | Can be used to verify Search Console. |

### 2.2 fizzbee repo (`fizzbee-io/fizzbee`)

| Content | Location | On fizzbee.io? |
|---|---|---|
| 110 reference examples, numbered by section (`01-01-noop` … `99-01-checkpoints`) | `examples/references/<NN-NN-name>/` | No |
| Each example: one `.fizz` file + `baseline.txt` (expected model-checker output); a few have `flags.txt` or `README.md` | same | No |
| Header comments in 98/110 examples: `# Example 0073: Saga Pattern` / `# Long-running transaction with compensation` / `# Demonstrates: saga pattern, compensating transactions, rollback` | first lines of each `.fizz` | No |
| `LANGUAGE_REFERENCE.md` (2,390 lines, 21 H2 chapters: Actions, Functions, Roles, Flow Modifiers, Fairness, Assertions, Data Structures, Fault Injection, Symmetry Reduction, …) | `examples/references/` | No |
| `GOTCHAS.md`, `VERIFICATION_GUIDE.md`, `PERFORMANCE_GUIDE.md` | `examples/references/` | No |
| `README.md` (732 lines; section index with descriptions) | `examples/references/` | No |
| `docs/` (TLA+ quick start, language design draft) | `docs/` | **Out of scope:** predates the public release; outdated. |
| 48 older tutorial examples | `examples/tutorials/` | **Out of scope:** superseded by `examples/references/` and the website tutorials. |
| 4 comparison specs | `examples/comparisons/` | **Out of scope:** old; Die Hard, token ring and gossip are already on the website. |
| Requirements-engineering examples | `examples/requirements/` | **Optional, later:** correct but focused on requirements engineering; may fit better alongside fizzbee.ai. |
| Claude skills (`fizz-spec`, `fizz-check`, `fizz-debug`, `fizz-mbt`) | `.claude/skills/` | N/A — good for coding agents already |

Section 13 ("Patterns") is the most search-relevant: mutex, read-write lock, distributed lock, optimistic locking, two-phase commit, saga, snapshot isolation, consensus, leader election, compare-and-swap, producer-consumer, message queue, cache coherence, eventual consistency, idempotent operations, circuit breaker, rate limiting, write-ahead log, event sourcing.

The repo README links to only one doc, the TLA+ quick start, which is outdated. GitHub's robots.txt blocks many crawlers from browsing repo directories, which is why this content isn't discovered.

### 2.3 fizzbee.ai

| Area | Finding |
|---|---|
| robots.txt | Excellent: explicitly allows GPTBot, OAI-SearchBot, ClaudeBot, PerplexityBot, Google-Extended, Applebot-Extended, etc. No `Sitemap:` line. |
| Homepage | Server-rendered, good title, meta description and canonical tag. |
| Catch-all | **Every unknown URL returns the homepage with HTTP 200**, including `/sitemap.xml`. Search engines treat these as soft 404s. |
| Sitemap | None (the URL returns homepage HTML). |
| Sample project (`/projects/<id>/view`) | Fully server-rendered: actors, use cases, Q&A, scenarios. Excellent indexable content, currently linked only from the homepage. |

### 2.4 blog.fizzbee.ai

Ghost. Correct sitemap index and robots.txt. One post so far. No issues beyond low cross-linking with the other two domains.

Note: fizzbee.io also has `/posts/` (two posts from 2024). Two blogs split attention; see Decision D5.

### 2.5 Search Console baseline for fizzbee.io (exported Oct 11, 2026)

**Indexing:** 39 indexed, 42 not indexed (as of Oct 3). Not-indexed reasons:

| Reason | Pages | Likely cause / action |
|---|---|---|
| Page with redirect | 22 | Unknown: probably URL variants (no trailing slash, `http://`, `index.html`). Export the list; harmless if they're variants of real pages. |
| Discovered – currently not indexed | 14 | Google knows but hasn't crawled. Export the list; if real pages are here, request indexing after Phase 1. |
| Crawled – currently not indexed | 2 | Export; often thin pages (e.g. section index pages). |
| Blocked by robots.txt | 2 | Tag pages; expected. Removing tags from the sitemap (1.4) stops Google trying. |
| Not found (404) | 1 | Export to see which. |
| Duplicate without user-selected canonical | 1 | Likely a stale backup page; canonical tags (1.2) address this class. |

**Traffic (last 3 months):** 665 clicks, ~87k impressions. Impressions are growing fast: ~13k (Jul) → ~31k (Aug) → ~40k (Sep).

- **Brand dominates clicks:** "fizzbee" and misspellings drive ~338 of the ~372 clicks attributed to queries. The homepage gets 429 clicks.
- **Many impressions look machine-generated.** About 150 queries have 6+ words (e.g. "knuth yao algorithm dice expected rolls optimal prefix", 5,444 impressions, position 2.7) and together account for ~16k impressions with **zero** clicks. US desktop has 0.33% CTR vs 2–4% elsewhere. This pattern is consistent with AI assistants and AI search features issuing long queries and reading results without clicking, which would mean fizzbee.io pages are already being retrieved by AI systems. Treat as a strong hint, not proven.
- **High-impression pages with no meta description:** Knuth-Yao (32.8k impressions, 0.14% CTR), EWD426 token ring (15.6k, 0.03%), linked list cycle (6.3k, 0.1%). All three are in Appendix A. Prioritize these in Phase 1.3.
- **Non-brand rankings:** "symmetry reduction" (position 1.8, 17% CTR — the tutorial owns this; supports D3), "knuth yao" (2.4), "tla+ alternatives" (position 1, small volume), conversational queries like "what are modern alternatives to tla+…" (position 1).
- **Opportunities ranking poorly:** "model based testing" (928 impressions, position 19) plus variants ("model-based testing", "…tools", "what is…", positions 19–41). Also raft protocol/consensus (position ~9), linked list cycle detection (~10–13), "python formal verification" (~8).
- **`/_index_bak1/` appears in search results** (84 impressions, position 2.4), so unlike `/_index_bak/` it is known to Google. Request removal in Phase 4.

---

## 3. Claude vs ChatGPT: where the recommendations agree and differ

**Both agree on:** fizzbee.io as canonical home; GitHub stays the source of truth for code; one page per example with prose, not bare code; automated publishing from the repo; sitemaps + Search Console + Bing Webmaster Tools + IndexNow; server-rendered HTML; separate tutorials / reference / examples; `llms.txt` as a supplement, not a substitute.

| Topic | ChatGPT | Claude | Proposed resolution |
|---|---|---|---|
| Example metadata | Add a YAML metadata file next to each example. | The `.fizz` header comments already contain title, description and topics for 98/110. | Use the headers. Add an optional sidecar file only for overrides (related links, longer prose). |
| Training crawlers | Example robots.txt allows OAI-SearchBot but **disallows GPTBot**. | For a new language, you *want* models trained on FizzBee syntax. Allow training crawlers. | Allow all (matches current fizzbee.io behavior and fizzbee.ai's explicit policy). Decision D1. |
| URL structure | Proposes `/docs/`, `/examples/`, `/concepts/` (with caveat to preserve existing URLs). | Keep existing `/design/...` paths; add new sections under them. | Keep existing URLs. New content under `/design/reference/`. Decision D2. |
| Validation | Build-time manifest check that every example has a page. | Agree. | Adopt. |
| Diagnostics | "Not discovered / discovered not indexed / indexed not ranking" framework. | Agree. | Adopt for Phase 6. |
| Specific defects | Not found (didn't inspect repos). | Stale-file deploy bug, missing canonicals, missing descriptions, tag/sitemap conflict, fizzbee.ai soft 404s. | Fix first (Phase 1). |
| Backlinks | Mentions "external references" briefly. | Awesome-lists, TLA+ community, HN/lobste.rs, Context7. | Phase 6. |

---

## 4. Target structure for fizzbee.io

Existing URLs stay unchanged. The principle is **one primary page per search intent, not one page per source file**. By default, construct examples live inside the reference chapter that explains the construct, and pattern examples get their own pages in the existing examples catalog. A per-example override (Phase 2.1) handles exceptions. Section numbers only drive the default mapping; they never appear in URLs.

| URL | Content | Source | Est. pages |
|---|---|---|---|
| `/design/reference/` | Reference landing page (from `references/README.md` intro + chapter list) | README.md | 1 |
| `/design/reference/<chapter>/` | One page per language-reference chapter (actions, roles, fairness, …): the chapter's prose, then an **Examples** section embedding the matching reference examples | LANGUAGE_REFERENCE.md + `examples/references/01–12, 14–16, 99` | ~20 |
| `/design/reference/gotchas/`, `/verification/`, `/performance/` | Guides | the three guide files | 3 |
| `/design/examples/` (existing) | Catalog regrouped into "In-depth walkthroughs" (existing 10 pages) and "Pattern library" | existing + generated | 1 (updated) |
| `/design/examples/<pattern-slug>/` | One page per Section 13 pattern (saga, mutex, distributed lock, …) | `examples/references/13-*` | ~18 |

### Why embed construct examples in the reference chapters

Example sections 01–16 map almost one-to-one onto `LANGUAGE_REFERENCE.md` chapters (Appendix C has the mapping). The larger construct topics, like symmetry and fault injection, already have their own website tutorials (`symmetry_reduction`, `fault-injection`). A standalone page for their examples would make a third page competing for the same searches, next to the tutorial and the reference chapter. Separate "Fairness" reference and "Fairness examples" pages would compete for the same searches (keyword cannibalization), and Google often ranks neither well. Embedding gives one strong page per construct, keeps explanation and runnable example together for readers, and avoids thin pages for tiny examples like `01-01-noop`. Each embedded example gets a heading anchor (e.g. `/design/reference/fairness/#strong-fair-action`) so it can be linked directly.

### Why patterns get their own pages

Patterns are searched by problem name ("saga pattern formal specification"), not by language construct, so each needs its own page with the name in the title. They go in the **existing** `/design/examples/` catalog rather than a second examples area.

**Avoid duplicates with existing pages:** `13-02-01-two-phase-commit` overlaps the three existing two-phase-commit pages, and `13-03-01-consensus` overlaps the Raft pages. For these, the pattern-library entry links to the existing page instead of generating a new one (or the spec is added to the existing page as a variant).

### What each embedded or pattern example shows

- Title and description (from header comments)
- "Demonstrates" topics (from header)
- The spec, highlighted, with "Run in playground" (reuse existing `fizzbee` shortcode)
- Expected result, cleaned from `baseline.txt`: PASSED/FAILED, state counts, which assertions were checked (strip file paths, timestamps, dot-file noise)
- Links: source on GitHub; for patterns, the reference chapters for the constructs they use; for reference chapters, the patterns that use the construct
- `lastmod` from the fizzbee repo's git history for that file

---

## 5. Roadmap

Each phase is sized to be one or a few Claude Code sessions. Each has acceptance criteria so the result can be checked.

### Phase 0: Prerequisites and baseline (you, ~30 min)

- [x] Confirm whether fizzbee.io is verified in Google Search Console and Bing Webmaster Tools. If not, verify (DNS TXT is simplest; works for all subdomains). Do the same for fizzbee.ai.
- [x] In Search Console, export the current Pages report (indexed / not indexed counts) as the baseline.
- [x] Note the actual deploy steps from the frontend repo (how `public/` gets into the Docker image, what Firebase does). Phase 1.1 depends on this.
- [x] Answer the decisions in Section 6. (D1 deferred to 1.5; D5 open; others per recommendation, confirmed as each phase reaches them.)

### Phase 1: Fix technical issues on fizzbee.io (1 Claude Code session in `website`, 1 in `frontend`)

**1.1 Stop stale pages from accumulating** (`frontend` + `website` repos)
- [x] **Done (Oct 11, 2026).** Production turned out to serve all docs from Firebase Hosting (Cloud Run only serves `/play`, `/play/run`, `/chat`, `/chat/api`), so the fix was: frontend `build-hosting.sh` assembles the hosting dir from scratch (Hugo output + the six git-tracked playground assets; frontend PRs #39/#40), website `deploy.sh` builds into a fresh temp dir and hands off (PR #81). Verified on a preview channel, then in production: all 73 stale files gone (66 × 404, 7 old-path 301s), all 50 sitemap URLs 200, playground smoke test passed. Bonus: fixed a live broken redirect via aliases (PR #80).
- Make the Hugo output a separate directory that is replaced wholesale on each deploy, rather than merged into `frontend/public` alongside playground assets. Exact approach depends on the frontend layout.
- One-time cleanup: delete `_index_bak/`, `_index_bak1/`, `posts/where-is-the-beef/` and any other HTML in the deployed folder that a fresh `hugo` build does not produce. Have Claude Code diff a clean build against the current deployed folder to find them all.
- Add a script (`deploy.sh` or Makefile target) in the website repo that builds and hands off the Hugo output. Note: `hugo --cleanDestinationDir` only cleans Hugo's own `public/`; the stale files come from *merging* into the frontend folder, so the hand-off itself must replace the docs files wholesale without touching playground assets.
- **Accept when** (check against the live site after deploy, not just the build output):
  - `/_index_bak/`, `/_index_bak1/`, `/posts/where-is-the-beef/` return a real HTTP 404.
  - Every URL in the sitemap returns HTTP 200, and the sitemap lists only canonical, intended-to-be-indexed URLs.
  - Smoke test (by hand, ~1 minute): `/play` loads, and one "Run in playground" link from a docs page opens the playground with the code filled in. This only checks that the deploy didn't delete or overwrite playground files; it doesn't run any specs.

**1.2 Canonical tags** (`website`)
- Add `<link rel="canonical" href="{{ .Permalink }}">` in `layouts/partials/head/custom.html`.
- **Accept when:** every page's HTML has exactly one canonical tag pointing to itself.

**1.3 Meta descriptions** (`website`)
- Add `description:` front matter to the 15 pages in Appendix A. Start with the homepage and the three high-impression pages from Section 2.5 (Knuth-Yao, EWD426 token ring, linked list cycle). 120–160 characters, written to match what people search for.
- Optionally add a fallback in the head partial that uses `.Summary` when `description` is empty, so future pages are never blank.
- **Accept when:** a build-time check (simple script or `hugo` + grep over `public/`) shows every page has a non-empty meta description.

**1.4 Sitemap cleanup** (`website`)
- `enableGitInfo = true` in `hugo.toml` so `lastmod` comes from git. (Requires full git history at build time; note that shallow clones break this.)
- Custom `layouts/sitemap.xml` (or `_default/sitemap.xml`) that excludes taxonomy/term pages (`/tags/...`) and any page with `sitemap_exclude: true`.
- **Accept when:** sitemap has no `/tags/`, no `_index_bak`, and every URL has a `lastmod`.

**1.5 robots.txt** (`website`)
- Override the theme's `robots.txt` in `layouts/robots.txt`. Keep `Disallow: /tags/`, add explicit allows for AI crawlers (copy the fizzbee.ai list), keep the `Sitemap:` line.
- **Accept when:** live robots.txt matches; Search Console robots tester shows no errors.

**1.6 Open Graph / social metadata check** (`website`)
- Verify the theme emits `og:title`, `og:description`, `og:image`, `twitter:card`. Add a default `og:image` if missing.

### Phase 2: Publish the reference corpus (2–3 Claude Code sessions in `website`)

**2.1 Generator script**
- **Prototype first.** Before generating everything, run the generator on a representative sample and review the output: one reference chapter with its embedded examples, one tiny example, one pattern page, one example with missing headers, and one duplicate pattern (two-phase commit). Only then generate the full corpus.
- Script in the website repo (e.g. `tools/gen_reference.py`) that takes a path to a fizzbee checkout (pinned commit or `main`) and writes Hugo content under `content/design/reference/`.
- Parses each example's header comments (title, description, "Demonstrates"), reads the `.fizz` source, and cleans `baseline.txt` into a short "expected result" block. Reuse the normalization rules in the fizzbee repo's `test_references.py` (it already keeps `Valid Nodes`, `IsLive`, `Checking …`, `PASSED`/`FAILED` and drops paths and timestamps).
- **Playground time limit.** The online playground has a ~20-second limit and fewer resources than a laptop. Use the timing and node counts already recorded in each `baseline.txt` to flag examples likely to exceed it. For those, hide the "Run in playground" button or replace it with a note like "Large state space; run locally with `fizz`." Start with a conservative threshold and tune it after trying a few flagged examples in the playground. The override file can force `playground: false` or `true`.
- **Per-example overrides.** Default placement comes from the section→chapter mapping, but an optional sidecar file (e.g. `page.yaml` next to the `.fizz`) can override title, description, placement (`embed` / `standalone` / `exclude` with a reason) and related links. Expected to be needed rarely; header comments remain the default.
- Splits `LANGUAGE_REFERENCE.md` by H2 into chapter pages; rewrites internal `#anchor` links to the new URLs. Copies the three guides.
- Appends an **Examples** section to each chapter page, embedding the reference examples for that chapter using the section→chapter mapping in Appendix C (kept as a small editable table in the script).
- Writes one page per Section 13 pattern under `content/design/examples/`, skipping the ones that duplicate existing pages (two-phase commit, consensus) and recording a link to the existing page instead.
- Generates front matter: `title`, `description`, `lastmod` (from fizzbee repo git log), `weight` (ordering), source GitHub URL.
- Generated output is committed, with a drift check (Decision D4).
- **Accept when:** running the script produces a clean `hugo` build with all pages, no broken internal links or chapter anchors (check with `htmltest` or `lychee`), and the 12 examples lacking headers are reported as warnings.

**2.2 Validation checks** (expanded after ChatGPT review)
- **Manifest:** every example directory is accounted for as *embedded* (with its chapter URL + anchor), *standalone* (with its URL), *linked to an existing page* (duplicates like two-phase commit), or *excluded with a reason*. Anything unaccounted for fails the build.
- **Uniqueness:** every generated page has a unique title, description and canonical URL.
- **Severity:** missing metadata is a warning; an unaccounted example, broken link or duplicate canonical is a failure.
- **Drift:** a CI check regenerates the content and fails if it differs from what's committed (keeps the committed output honest; see D4).
- **Not here:** checking that `baseline.txt` matches current model-checker output belongs in the fizzbee repo, not the website build (see 2.7).

**2.3 Navigation and cross-links**
- Add Reference to the geekdoc menu.
- Link each existing tutorial to the relevant reference chapter and examples (e.g. `fault-injection` tutorial → Fault Injection chapter + Section 14 examples). Link reference chapters back to tutorials.
- **Accept when:** every new page is reachable by normal links from the homepage within ~3 clicks.

**2.4 Fix the 12 unheadered examples** (`fizzbee` repo)
- Add header comments to the 12 examples in Appendix B, in the same format as the others. Small PR to the fizzbee repo.

**2.5 Repo README docs links** (`fizzbee` repo)
- Replace the README's only docs link (the outdated `docs/fizzbee-quick-start-for-tlaplus-users.md`) with a Documentation section linking to fizzbee.io Tutorials, Language Reference and Examples.
- Add a note at the top of the old `docs/` files that they are outdated, pointing to fizzbee.io (or delete them).

**2.6 Fill in thin existing example pages**
- Add descriptions and a short "what this demonstrates" intro to the 8 existing `/design/examples/` pages that lack them.

**2.7 Run the baseline tests in CI** (`fizzbee` repo)
- `test_references.py` compares every reference example against its `baseline.txt`, but the fizzbee repo's CI (`build.yaml`) doesn't run it; it only smoke-tests one old tutorial spec. Add `python3 test_references.py` to CI. Once the website publishes these examples with their expected results, a failing baseline means a wrong page.
- **Accept when:** a PR that changes model-checker output for any reference example fails CI until its baseline is updated.

### Phase 3: AI-assistant discoverability (1 Claude Code session in `website`)

- **`/llms.txt`**: Hugo custom output format on the home page listing every doc page with title, URL and one-line description, grouped by section (Tutorials, Reference, Examples).
- **`/llms-full.txt`**: concatenated raw markdown of tutorials + language reference + guides (not every example, to keep size reasonable).
- **Per-page Markdown output** (`/path/index.md`, Hugo output format) for reference and example pages, so agents can fetch one clean chapter instead of a giant file. Likely more useful to coding agents than `llms-full.txt`.
- **Context7**: check its current submission and maintenance requirements, then submit the fizzbee.io docs or the fizzbee repo.
- These are supplements. They come after the HTML pages, sitemap and cross-links work, and they don't guarantee any particular assistant uses them.
- **Repo pointers** (fizzbee): add a "Rendered at fizzbee.io/…" line at the top of `LANGUAGE_REFERENCE.md` and the guides (README links are handled in 2.5).
- **Accept when:** `/llms.txt` and `/llms-full.txt` are live and listed.

### Phase 4: Search engine submission and change notification (you + 1 short session)

- Submit `https://fizzbee.io/sitemap.xml` in Search Console and Bing Webmaster Tools.
- **Removals → New request** for `https://fizzbee.io/_index_bak1/` (it appears in search results; see 2.5). Not needed for `/_index_bak/`, which Google has never seen.
- URL Inspection → Request indexing for the homepage, reference landing, language reference index, examples index, and the top ~10 pattern pages.
- **IndexNow**: add the key file to `static/`, and a post-deploy script that POSTs changed URLs (diff of sitemap before/after deploy) to `api.indexnow.org`.
- **Accept when:** Search Console shows the sitemap processed with the new URL count; IndexNow returns 200/202 on deploy.

### Phase 5: Automate (1–2 sessions, `website` + possibly `fizzbee`)

- GitHub Action in the website repo: on push to `main`, and on a `repository_dispatch` from the fizzbee repo when `examples/references/**` or `docs/**` change:
  1. Check out website and fizzbee (full history for `lastmod`).
  2. Run the generator + manifest check.
  3. Build Hugo; run link checker; run description/canonical checks.
  4. Deploy (depends on how the frontend image is built; may mean building and pushing the Cloud Run image, or splitting static hosting off — Decision D6).
  5. Ping IndexNow.
- **Accept when:** adding a new example to the fizzbee repo results in a live page without manual steps.

### Phase 6: fizzbee.ai and blog (separate track, `fizzbee.ai` app repo)

- **Real 404s**: unknown paths return HTTP 404 (still render a friendly page).
- **Sitemap**: serve a real `/sitemap.xml` with the homepage, privacy page and public sample projects. Add `Sitemap:` to robots.txt.
- **Public sample gallery**: a `/examples` (or `/samples`) index of curated, server-rendered sample projects, each with a stable descriptive URL (consider slugs instead of UUIDs) and its own title/description. These are strong indexable pages.
- **Cross-linking**: fizzbee.io ↔ fizzbee.ai ↔ blog.fizzbee.ai in navs and footers; each blog post links to relevant fizzbee.io docs.
- Submit fizzbee.ai and blog.fizzbee.ai sitemaps in Search Console / Bing.

### Phase 7: Measure and grow (ongoing)

- **Weekly for the first month:** Search Console Pages report. Classify issues as ChatGPT suggested:
  - *Not discovered* → sitemap coverage, internal links.
  - *Discovered/crawled but not indexed* → thin content, duplication, canonicals.
  - *Indexed but not ranking* → better titles/descriptions/prose, more links.
- **Queries to watch:** "fizzbee", "TLA+ alternative", "formal methods for developers", "<pattern> formal specification" (saga, 2PC, raft, leader election, distributed lock), FizzBee construct names.
- **AI crawler visits:** query Cloud Run request logs for user agents (`GPTBot`, `OAI-SearchBot`, `ClaudeBot`, `PerplexityBot`, `Google-Extended`, `bingbot`). Claude Code can write the `gcloud logging read` query.
- **Backlinks:** submit to awesome-tla+ and awesome-formal-methods lists; post the Raft and pattern examples to the TLA+ Google group, Hacker News, lobste.rs; write blog posts on blog.fizzbee.ai that link into the reference.
- **Content priorities:** feed Search Console impressions into Phase 8 to choose which patterns get deeper treatment.

### Phase 8: Content depth — walkthroughs vs automated patterns (ongoing, after Phase 2)

The existing in-depth examples (two-phase commit with actors ~900 lines, Raft ~1,000 lines) are the strongest content on the site. They build a model step by step (roles → states → RPCs → actions → invariants), show diagrams, and — most valuable — show the model checker breaking plausible designs (the two-phase commit timeout section tries five fixes; four fail). That is what earns rankings for competitive searches, gets shared, and gets cited by AI assistants. But they are expensive to write and maintain, so they can't be produced for every pattern.

Approach: **three tiers.**

| Tier | What | How many | Maintenance |
|---|---|---|---|
| 1. Automated pattern pages | Generated from the Section 13 specs (Phase 2): spec, description, expected result, links | All ~18 | None beyond the generator |
| 2. "Bug and fix" pairs | A deliberately broken spec next to the correct one; the page shows the model checker's counterexample, then the fix. Still generated from files with baselines. | A handful | Low (baselines catch drift) |
| 3. Hand-written walkthroughs | Full tutorial-style pages like two-phase commit and Raft | 3–5, chosen by search demand | Medium; reduced by testing (below) |

**Walkthrough candidates** (confirm with Search Console data once available):

- **Distributed lock with leases and fencing tokens.** Heavily searched (the Redlock debate); a model checker finding the lease-expiry bug is an ideal demonstration.
- **Saga pattern.** What microservice developers actually build — fizzbee.io's core audience.
- **Idempotency / exactly-once delivery.** Connects to the existing message-delivery-guarantees tutorial.
- **Model-based testing.** "model based testing" gets ~930 impressions per quarter, with more from variants, but fizzbee.io ranks around position 19–41. FizzBee has a model-based testing product (`/testing/`), so a strong explainer ("What is model-based testing?" with a concrete FizzBee + Go walkthrough) targets a real, non-brand audience. This came from the Search Console baseline, not the original audit.
- **"FizzBee for TLA+ users."** Write fresh (the old `docs/` version is outdated). "TLA+ alternative" is among the highest-value searches for FizzBee; showing the same spec in both languages side by side would also attract links from the TLA+ community.

**Test the walkthrough code.** Code blocks in markdown silently go stale when the language changes. For each walkthrough (existing and new), put the complete spec and the key intermediate steps (e.g. two-phase-commit timeout attempts 1–5) into the repo as `.fizz` files with `baseline.txt`, the same mechanism `examples/references/` already uses. A language change then shows up as a failing test rather than a broken page. Ideally the page pulls the code from those files (Hugo `readFile` or a shortcode) so there is one copy.

**Drafting with Claude Code.** Claude Code can draft a walkthrough from a pattern spec in the style of the two-phase commit page, running every intermediate spec through `fizz` to confirm it behaves as the prose claims (including the failing attempts). You then review for what's genuinely interesting — the part that can't be automated.

- **Accept when (per walkthrough):** every code step on the page exists as a tested `.fizz` file with a baseline; the page has a title, description and links to the pattern page and relevant reference chapters.

---

## 6. Decisions needed

| # | Decision | Recommendation |
|---|---|---|
| D1 | Allow AI training crawlers (GPTBot, ClaudeBot, Google-Extended) or only search crawlers? | **Decided: allow all** (wider distribution is the goal). fizzbee.io already allows them by default and fizzbee.ai explicitly allows them, so this keeps the two sites consistent. The docs are Apache-licensed and the goal is adoption, so there's little downside. Training is a complement to retrieval, not a substitute: an agent that fetches the current reference and runs `fizz` (Phase 3 + the existing skills) is more reliable than recall. |
| D2 | URL scheme for new content. | `/design/reference/...` as in Section 4; keep all existing URLs. |
| D3 | Where examples live: separate examples section vs embedded in the reference. | One primary page per search intent. By default, embed construct examples (Sections 01–12, 14–16, 99) in their reference chapters, and give Section 13 patterns their own pages in the existing `/design/examples/` catalog. Use the per-example override (2.1) for any exception. See Section 4. |
| D4 | Generated content committed to the website repo or generated at build time (gitignored)? | Commit it, with a CI drift check that regenerates and fails on differences. It's the same generator either way; only whether the output is committed differs. Committed output gives reviewable diffs and works with today's manual deploy. **Migration criterion:** once Phase 5 has an automated CI deploy, gitignore the generated folder and generate at build time. |
| D5 | Which blog is canonical: fizzbee.io/posts or blog.fizzbee.ai? | Pick one for new posts. If blog.fizzbee.ai, leave the two old fizzbee.io posts in place (they have links) but link to the new blog from fizzbee.io's nav. |
| D6 | Keep static docs inside the frontend Cloud Run image, or host them separately (Firebase Hosting static, Cloudflare Pages) with `/play` routed to Cloud Run? | Decide after reviewing the frontend repo. Separate static hosting makes Phase 5 automation much simpler and is what the website README already hints at ("soon … cloudflare pages"). |
| D7 | Scope of repo content to publish. | **Decided:** `examples/references/` only. `docs/`, `examples/tutorials/` and `examples/comparisons/` are outdated and out of scope; `examples/requirements/` is optional, later. |
| D8 | Walkthroughs vs automated patterns. | All patterns automated (tier 1); a few "bug and fix" pairs (tier 2); 3–5 hand-written walkthroughs (tier 3), starting with distributed lock or saga. See Phase 8. |

---

## 7. Suggested session order

**[CC]** = Claude Code session in the named repo. **[You]** = manual step (accounts, dashboards, judgment calls).

1. **[You]** Phase 0: verify Search Console / Bing, record baseline, answer decisions D1–D8.
2. **[CC] `website`**: Phase 1.2–1.6 (canonical, descriptions, sitemap, robots, OG). Small, safe, immediately useful. You review the 15 descriptions.
3. **[CC] `frontend` + `website`**: Phase 1.1 (deploy fix + stale cleanup). Start by having Claude Code explain the actual Cloud Run / Firebase setup; that also settles D6. **[You]** deploy.
4. **[CC] `fizzbee`**: Phase 2.4 (headers on 12 examples) + 2.5 (README docs links, mark old `docs/` outdated) + 2.7 (baseline tests in CI). Small PR.
5. **[CC] `website`**: Phase 2.1–2.2 (generator + validation). Prototype on the sample set first, then the full corpus. **[You]** confirm the Appendix C mapping and review the prototype output.
6. **[CC] `website`**: Phase 2.3, 2.6 (navigation, cross-links, thin pages).
7. **[CC] `website`**: Phase 3 (llms.txt, llms-full.txt). **[You]** submit to Context7.
8. **[You]** Phase 4: submit sitemaps, request indexing. **[CC]** IndexNow script.
9. **[CC] `website` (+ `fizzbee`)**: Phase 5 automation.
10. **[CC] fizzbee.ai repo**: Phase 6. **[You]** pick sample projects for the gallery.
11. **[CC] + [You]** Phase 8: first walkthrough (draft + test by Claude Code, review by you); tests for the existing walkthrough code.
12. **[You]** Phase 7 ongoing: weekly Search Console review, backlinks and community posts.

---

## Appendix A: fizzbee.io pages missing `description`

- `content/_index.md` (homepage)
- `content/design/_index.md`
- `content/design/examples/_index.md`
- `content/design/examples/die-hard.md`
- `content/design/examples/ewd426-token-ring.md`
- `content/design/examples/knuth-yao-sampling-algorithm.md`
- `content/design/examples/linked_list_cycle.md`
- `content/design/examples/time-oblivious-sampling-algorithm.md`
- `content/design/examples/two_phase_commit.md`
- `content/design/examples/two_phase_commit_actors.md`
- `content/design/examples/two_phase_commit_procedural.md`
- `content/design/tutorials/_index.md`
- `content/design/tutorials/frontmatter.md`
- `content/design/tutorials/limitations.md`
- `content/posts/_index.md`, `formal-methods-wire-transfer.md`, `pseudocode-modelchecking.md`

## Appendix B: reference examples without header comments

`09-06-next-states-restorable`, `09-07-next-states-violation`, `09-08-next-states-concurrency-cap`, `09-09-next-states-role-id`, `09-10-exists-no-graph-unreachable`, `09-11-exists-no-graph-reachable`, `09-12-exists-simulation-warning`, `12-02-yaml-frontmatter`, `14-01-crash-on-yield`, `14-02-disable-crash-on-yield`, `14-04-message-loss-rpc`, `15-01-action-level-config`

## Appendix C: example section → reference chapter mapping

Draft mapping; confirm when building the generator.

| Example section | Embedded in reference chapter |
|---|---|
| 01 Basics | Actions (and File Structure) |
| 02 Flow Modifiers | Flow Modifiers |
| 03 Conditionals, 04 Loops | Control Flow |
| 05 Nondeterminism | Nondeterminism |
| 06 Functions | Functions |
| 07 Guards | Actions (guards / `require`) |
| 08 Data Types | Data Structures |
| 09 Assertions | Assertions |
| 10 Fairness | Fairness |
| 11 Roles | Roles |
| 12 Advanced | Best Practices / Configuration (split by example) |
| 13 Patterns | **Own pages** in `/design/examples/` |
| 14 Fault Injection | Fault Injection |
| 15 Action Configuration | Configuration |
| 16 Symmetry | Symmetry Reduction |
| 99 Miscellaneous (checkpoints) | State Management (or wherever checkpoints are documented) |

## Appendix D: example header format (already in use)

```
# Example 0073: Saga Pattern
# Long-running transaction with compensation
# Demonstrates: saga pattern, compensating transactions, rollback
```

Line 1 → page title, line 2 → meta description seed, line 3 → topics/tags.
