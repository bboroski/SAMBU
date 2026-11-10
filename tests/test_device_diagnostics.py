from __future__ import annotations

import unittest
from unittest.mock import patch

from sambu_ide.device_diagnostics import scan_apple_devices


class DeviceDiagnosticsTests(unittest.TestCase):
    @patch("sambu_ide.device_diagnostics.os.name", "posix")
    @patch("sambu_ide.device_diagnostics.shutil.which", return_value=None)
    def test_missing_tools_are_reported_without_crashing(self, _which):
        report = scan_apple_devices()
        self.assertFalse(report["libimobiledevice"]["installed"])
        self.assertEqual(report["devices"], [])
        self.assertIn("summary", report)

    @patch("sambu_ide.device_diagnostics.os.name", "posix")
    @patch("sambu_ide.device_diagnostics.shutil.which")
    @patch("sambu_ide.device_diagnostics._run")
    def test_paired_device_model_and_ios_are_reported(self, run, which):
        which.side_effect = lambda name: f"/usr/bin/{name}"
        def fake(command, timeout=8):
            if command[0].endswith("idevice_id"):
                return {"returncode": 0, "stdout": "00008020-DEVICE"}
            return {"returncode": 0, "stdout": {"ProductType": "iPhone17,1",
                    "ProductVersion": "18.2", "DeviceName": "Test iPhone"}.get(command[-1], "")}
        run.side_effect = fake
        report = scan_apple_devices()
        self.assertEqual(report["devices"][0]["model_identifier"], "iPhone17,1")
        self.assertEqual(report["devices"][0]["ios_version"], "18.2")
        self.assertEqual(report["devices"][0]["pairing_status"], "paired")


if __name__ == "__main__":
    unittest.main()
