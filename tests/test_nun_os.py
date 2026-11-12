from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from sambu.nun_os import (
    NUNOSFeatureUnavailable, NUNOSProfileError,
    load_nun_os_profile, validate_nun_os_profile,
)

FIXTURE = Path(__file__).parent / "fixtures" / "nun-os-profile.json"


class NUNOSProfileTests(unittest.TestCase):
    def test_loads_profile_and_summarizes_feature_maturity(self):
        profile = load_nun_os_profile(FIXTURE)
        self.assertEqual(profile.profile_id, "nun-test-profile")
        self.assertEqual(profile.feature("services.dependency-graph").status, "implemented")
        self.assertEqual(profile.feature("scheduler.preemptive").status, "planned")
        self.assertEqual(profile.summary()["status_counts"]["implemented"], 1)
        self.assertEqual(len(profile.digest), 64)

    def test_requires_implemented_features_by_default(self):
        profile = load_nun_os_profile(FIXTURE)
        self.assertEqual(profile.require_feature("services.dependency-graph").status, "implemented")
        with self.assertRaises(NUNOSFeatureUnavailable):
            profile.require_feature("scheduler.preemptive")
        with self.assertRaises(NUNOSFeatureUnavailable):
            profile.require_feature("missing.feature")

    def test_partial_feature_requires_explicit_opt_in(self):
        payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
        payload["features"][0]["status"] = "partial"
        profile = validate_nun_os_profile(payload)
        with self.assertRaises(NUNOSFeatureUnavailable):
            profile.require_feature("services.dependency-graph")
        self.assertEqual(profile.require_feature("services.dependency-graph", allow_partial=True).status, "partial")

    def test_rejects_implemented_feature_without_evidence(self):
        payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
        payload["features"][0]["evidence"] = []
        with self.assertRaises(NUNOSProfileError):
            validate_nun_os_profile(payload)

    def test_rejects_duplicate_ids_and_unknown_fields(self):
        payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
        payload["features"].append(dict(payload["features"][0]))
        with self.assertRaises(NUNOSProfileError):
            validate_nun_os_profile(payload)
        payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
        payload["unexpected"] = True
        with self.assertRaises(NUNOSProfileError):
            validate_nun_os_profile(payload)

    def test_rejects_duplicate_json_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profile.json"
            path.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
            with self.assertRaises(NUNOSProfileError):
                load_nun_os_profile(path)

    def test_rejects_oversized_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profile.json"
            path.write_bytes(b" " * (1_048_577))
            with self.assertRaises(NUNOSProfileError):
                load_nun_os_profile(path)


if __name__ == "__main__":
    unittest.main()
