"""Tests for check_site.py. Run: python3 -m unittest discover -s tools"""

import unittest

import check_site as c


class ResolveTest(unittest.TestCase):
    PAGE = "/testing/tutorials/getting-started/"

    def test_root_relative(self):
        self.assertEqual(c.resolve(self.PAGE, "/design/"), "/design/")

    def test_relative_updir(self):
        self.assertEqual(c.resolve(self.PAGE, "../quick-start/"),
                         "/testing/tutorials/quick-start/")

    def test_relative_with_fragment(self):
        self.assertEqual(c.resolve(self.PAGE, "../quick-start/#step-1"),
                         "/testing/tutorials/quick-start/#step-1")

    def test_same_page_fragment(self):
        self.assertEqual(c.resolve(self.PAGE, "#intro"), self.PAGE + "#intro")

    def test_absolute_same_host_is_internal(self):
        self.assertEqual(c.resolve(self.PAGE, "https://fizzbee.io/design/"), "/design/")

    def test_external_hosts_skipped(self):
        self.assertIsNone(c.resolve(self.PAGE, "https://github.com/fizzbee-io/fizzbee"))
        self.assertIsNone(c.resolve(self.PAGE, "//cdn.example.com/x.js"))
        self.assertIsNone(c.resolve(self.PAGE, "mailto:x@fizzbee.io"))


class AllowlistTest(unittest.TestCase):
    def test_allowed_pairs_are_exact_urls(self):
        for title, urls in c.DUP_TITLE_ALLOW.items():
            self.assertEqual(len(urls), 2, title)
            self.assertNotIn("/posts/", urls)




class AllowedDuplicateTest(unittest.TestCase):
    ALLOW = {"T": {"/a/", "/b/"}}

    def test_allowed_pair_passes(self):
        self.assertTrue(c.allowed_duplicate(self.ALLOW, "T", "/a/", "/b/"))

    def test_stray_scanned_first_fails(self):
        # /about/ sorts before the allowed pair and gets recorded first;
        # the allowed pages must still fail against it.
        self.assertFalse(c.allowed_duplicate(self.ALLOW, "T", "/about/", "/a/"))

    def test_stray_scanned_last_fails(self):
        self.assertFalse(c.allowed_duplicate(self.ALLOW, "T", "/a/", "/about/"))

    def test_unlisted_title_fails(self):
        self.assertFalse(c.allowed_duplicate(self.ALLOW, "X", "/a/", "/b/"))


if __name__ == "__main__":
    unittest.main()
