from __future__ import annotations
import hashlib
from dataclasses import replace
import unittest
from sambu.trust import PortfolioArtifact, PortfolioVerifier, trust_dig

def artifact(identifier="case-study", *, issuer="trusted-lab", content="verified content", expires="2027-01-01"):
    return PortfolioArtifact(
        identifier=identifier,title="Case study",content=content,
        expected_sha256=hashlib.sha256(content.encode("utf-8")).hexdigest(),
        issuer=issuer,evidence_ref="evidence://review/2026-01",
        issued_on="2026-01-01",expires_on=expires,
    )

class PortfolioTrustTests(unittest.TestCase):
    def test_verified_portfolio(self):
        report=PortfolioVerifier({"trusted-lab"},as_of="2026-11-09").verify("design-work",[artifact()])
        self.assertTrue(report.is_verified)
        self.assertEqual(report.status,"verified")
        self.assertEqual(report.trust_percent,100.0)
    def test_issuer_and_expiry_findings(self):
        report=trust_dig("design-work",[artifact(issuer="unknown-lab",expires="2026-01-02")],{"trusted-lab"},as_of="2026-11-09")
        self.assertFalse(report.is_verified)
        self.assertIn("untrusted_issuer",report.artifacts[0].reasons)
        self.assertIn("evidence_expired",report.artifacts[0].reasons)
    def test_weighted_partial_verification(self):
        good=artifact("good",content="one")
        bad=artifact("bad",issuer="unlisted",content="two")
        report=PortfolioVerifier({"trusted-lab"},as_of="2026-11-09").verify("mixed",[good,bad])
        self.assertEqual(report.status,"partial")
        self.assertEqual(report.trust_percent,50.0)

    def test_dates_require_the_documented_iso_calendar_format(self):
        with self.assertRaisesRegex(ValueError, "YYYY-MM-DD"):
            PortfolioVerifier({"trusted-lab"}, as_of="20261109")
        malformed = artifact()
        malformed = replace(malformed, issued_on="20260101")
        report = PortfolioVerifier({"trusted-lab"}, as_of="2026-11-09").verify("date-check", [malformed])
        self.assertIn("invalid_issued_on", report.artifacts[0].reasons)

    def test_unrepresentable_integer_weight_is_reported_not_crashed(self):
        item = artifact()
        item = replace(item, weight=10 ** 1000)
        report = PortfolioVerifier({"trusted-lab"}, as_of="2026-11-09").verify("weight-check", [item])
        self.assertIn("invalid_weight", report.artifacts[0].reasons)
        self.assertEqual(report.total_weight, 1.0)

    def test_combined_weight_overflow_is_rejected(self):
        first = artifact("first")
        second = artifact("second")
        first = replace(first, weight=1e308)
        second = replace(second, weight=1e308)
        verifier = PortfolioVerifier({"trusted-lab"}, as_of="2026-11-09")
        with self.assertRaisesRegex(ValueError, "combined artifact weight"):
            verifier.verify("overflow", [first, second])

if __name__ == "__main__": unittest.main()
