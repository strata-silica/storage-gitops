import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]


class ContextSiteTest(unittest.TestCase):
    def test_cross_org_context_and_pages_are_public_safe(self):
        context = json.loads((ROOT / "governance/cross-org-context.json").read_text())
        html = (ROOT / "site/index.html").read_text()
        self.assertEqual(context["repository"], "strata-silica/storage-gitops")
        self.assertGreaterEqual(len(context["relatedRepositories"]), 3)
        for value in ("canonical", "application/ld+json", "https://re8ch.com/", "Runtime Wiki"):
            self.assertIn(value, html)
        for value in ("kubectl get", "Secret/data", "10.251.", "223.159."):
            self.assertNotIn(value, html)
