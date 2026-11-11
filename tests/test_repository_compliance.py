import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "repository_compliance.py"
SPEC = importlib.util.spec_from_file_location("repository_compliance", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

class RepositoryComplianceTests(unittest.TestCase):
    def test_private_key_marker_is_reported_without_value(self):
        findings = MODULE.scan_text("-----BEGIN RSA PRIVATE KEY-----\nREDACTED\n")
        self.assertEqual([item["code"] for item in findings], ["PRIVATE_KEY"])
        self.assertNotIn("REDACTED", str(findings))

    def test_github_token_pattern_is_detected_without_disclosure(self):
        marker = "A" * 32
        findings = MODULE.scan_text("token = 'ghp_" + marker + "'")
        self.assertTrue(any(item["code"] == "GITHUB_TOKEN" for item in findings))
        self.assertNotIn(marker, str(findings))

    def test_normal_text_does_not_trigger_secret_rules(self):
        self.assertEqual(MODULE.scan_text("This is a normal README paragraph."), [])

    def test_trademark_watchlist_is_contextual_review(self):
        findings = MODULE.scan_text("Compatible with ExamplePlatform.", ["ExamplePlatform"])
        self.assertEqual(findings[0]["code"], "TRADEMARK_REVIEW")
        self.assertEqual(findings[0]["line"], 1)

    def test_policy_requires_schema_version_one(self):
        with tempfile.TemporaryDirectory() as directory:
            policy = Path(directory) / "policy.json"
            policy.write_text(json.dumps({"schema_version": 2}), encoding="utf-8")
            with self.assertRaises(ValueError):
                MODULE.load_policy(policy)

if __name__ == "__main__":
    unittest.main()
