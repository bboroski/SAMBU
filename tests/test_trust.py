from __future__ import annotations
import hashlib
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

if __name__ == "__main__": unittest.main()
