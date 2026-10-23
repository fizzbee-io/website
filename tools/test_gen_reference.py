"""Tests for gen_reference.py. Run: python3 -m unittest discover -s tools"""

import unittest

import gen_reference as g

DOC = """# Title

## Actions

### Syntax

See [Fairness](#fairness) and [its syntax](#syntax-1).

```python
# [not a link](#fairness)
```

## Fairness

### Syntax

Inline `[code](#actions)` stays.

### Syntax

## Version History

### Syntax
"""


class AnchorMapTest(unittest.TestCase):
    def setUp(self):
        self.amap = g.build_anchor_map(DOC, {"actions", "fairness"})

    def test_chapter_headings_map_to_pages(self):
        self.assertEqual(self.amap["actions"], ("actions", None))
        self.assertEqual(self.amap["fairness"], ("fairness", None))

    def test_duplicate_headings_resolve_to_the_right_chapter(self):
        # GitHub numbers duplicates across the whole document; Hugo per page.
        self.assertEqual(self.amap["syntax"], ("actions", "syntax"))
        self.assertEqual(self.amap["syntax-1"], ("fairness", "syntax"))
        self.assertEqual(self.amap["syntax-2"], ("fairness", "syntax-1"))

    def test_skipped_chapters_are_left_out(self):
        self.assertNotIn("version-history", self.amap)
        self.assertNotIn("syntax-3", self.amap)


class RewriteLinksTest(unittest.TestCase):
    def setUp(self):
        self.amap = g.build_anchor_map(DOC, {"actions", "fairness"})
        self.out = g.rewrite_links(DOC, self.amap, {}, "/reference/language/actions/")

    def test_links_are_rewritten(self):
        self.assertIn("[Fairness](/reference/language/fairness/)", self.out)
        self.assertIn("[its syntax](/reference/language/fairness/#syntax)", self.out)

    def test_code_is_untouched(self):
        self.assertIn("# [not a link](#fairness)", self.out)
        self.assertIn("`[code](#actions)`", self.out)


class MetaDescriptionTest(unittest.TestCase):
    def test_never_cut_mid_sentence(self):
        long = "First sentence is here. " * 20
        d = g.meta_description(long, "suffix")
        self.assertTrue(d.endswith("."))
        self.assertFalse(d.endswith("..."))
        self.assertLessEqual(len(d), g.MAX_DESCRIPTION)

    def test_no_dashes(self):
        d = g.meta_description("Crash on yield — FizzBee's key differentiator – automatic.", "x")
        self.assertNotIn("—", d)
        self.assertNotIn("–", d)


class PlaygroundTest(unittest.TestCase):
    def example(self, **overrides):
        ex = g.Example.__new__(g.Example)
        ex.name, ex.overrides, ex.flags, ex.fizz_yaml, ex.baseline = "x", overrides, [], None, None
        return ex

    def test_forced_off_has_a_note(self):
        allowed, note = self.example(playground=False).playground()
        self.assertFalse(allowed)
        self.assertTrue(note)

    def test_string_override_is_an_error(self):
        g.ERRORS.clear()
        self.example(playground="false")._validate_overrides()
        self.assertTrue(any("playground" in e for e in g.ERRORS))
        g.ERRORS.clear()


class CleanBaselineTest(unittest.TestCase):
    def test_keeps_results_and_drops_noise(self):
        text = "\n".join([
            "Model checking examples/references/x/X.json",
            "Nodes: 5, queued: 3, elapsed: 1ms",
            "Nodes: 9, queued: 0, elapsed: 2ms",
            "Time taken for model checking: 2ms",
            "Valid Nodes: 9 Unique states: 7",
            "PASSED: Model checker completed successfully",
        ])
        self.assertEqual(g.clean_baseline(text), [
            "Nodes: 9, queued: 0", "Valid Nodes: 9 Unique states: 7",
            "PASSED: Model checker completed successfully"])


class ReadmeIntroTest(unittest.TestCase):
    def test_finds_first_prose_paragraph(self):
        readme = "# T\n\nComprehensive FizzBee examples.\n\n\U0001F4D6 **[Guide](x.md)**\n\n## Org\n"
        self.assertEqual(g.readme_intro(readme), "Comprehensive FizzBee examples.")

    def test_warns_when_shape_changes(self):
        g.WARNINGS.clear()
        g.readme_intro("# T\n\n## Only sections\n\nFizzBee text under a section.\n")
        self.assertTrue(g.WARNINGS)
        g.WARNINGS.clear()


class PageLastmodTest(unittest.TestCase):
    def test_older_sources_floor_at_launch_date(self):
        self.assertEqual(g.page_lastmod("2026-03-08T01:12:12-08:00"),
                         g.REFERENCE_LAUNCH_DATE)

    def test_newer_source_wins(self):
        newer = "2027-01-05T10:00:00-08:00"
        self.assertEqual(g.page_lastmod("2026-05-01T00:00:00-07:00", newer), newer)

    def test_compares_as_datetimes_not_strings(self):
        # a is the later instant (12:00Z vs 11:00Z) but the smaller string;
        # a string max() would wrongly pick b.
        a = "2027-06-01T05:00:00-07:00"
        b = "2027-06-01T11:00:00+00:00"
        self.assertEqual(g.page_lastmod(a, b), a)

    def test_none_and_empty_filtered(self):
        self.assertEqual(g.page_lastmod(None), g.REFERENCE_LAUNCH_DATE)
        self.assertEqual(g.page_lastmod(), g.REFERENCE_LAUNCH_DATE)


class StripRepoPointer(unittest.TestCase):
    def test_pointer_blockquote_is_dropped(self):
        text = "> Rendered at [fizzbee.io/x](https://fizzbee.io/x/).\n\nBody stays.\n"
        self.assertEqual(g.strip_repo_pointer(text), "Body stays.\n")

    def test_text_without_pointer_is_unchanged(self):
        self.assertEqual(g.strip_repo_pointer("Body only.\n"), "Body only.\n")

    def test_only_leading_pointer_is_dropped(self):
        text = "Intro.\n\n> Rendered at [fizzbee.io/x](https://fizzbee.io/x/).\n"
        self.assertEqual(g.strip_repo_pointer(text), text)

    def test_ordinary_rendered_blockquote_is_kept(self):
        text = "> Rendered output can differ between runs.\n\nBody.\n"
        self.assertEqual(g.strip_repo_pointer(text), text)


if __name__ == "__main__":
    unittest.main()
