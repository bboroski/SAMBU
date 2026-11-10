from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from sambu.apple_devices import AppleDeviceToolkit
from sambu.i18n import LanguageManager, normalize_language, translate


class FakeRunner:
    def __init__(self):
        self.calls = []

    def __call__(self, command, **kwargs):
        self.calls.append(command)
        joined = " ".join(command).lower()
        if "--version" in joined:
            tool = Path(command[0]).name.lower()
            return self.completed(command, 0, f"{tool} 1.4.0")
        if "idevice_id" in joined:
            return self.completed(command, 0, "00008020-TEST-UDID\n")
        if "idevicepair" in joined and "validate" in joined:
            return self.completed(command, 0, "")
        if "ideviceinfo" in joined:
            key = command[command.index("-k") + 1]
            values = {
                "DeviceName": "Test iPhone",
                "ProductType": "iPhone18,1",
                "ProductVersion": "26.1",
                "BuildVersion": "23B74",
            }
            return self.completed(command, 0, values[key])
        if "sc.exe" in joined:
            return self.completed(command, 0, "STATE : 4 RUNNING")
        if "pnputil.exe" in joined and "/enum-drivers" in joined:
            return self.completed(
                command, 0,
                "Original Name: usbaapl64.inf\nProvider Name: Apple, Inc.",
            )
        if "pnputil.exe" in joined:
            return self.completed(
                command, 0,
                "Instance ID: USB\\VID_05AC\nDevice Description: Apple iPhone",
            )
        return self.completed(command, 1, "", "not found")

    @staticmethod
    def completed(command, code, stdout="", stderr=""):
        return subprocess.CompletedProcess(command, code, stdout, stderr)


class LocalizationTests(unittest.TestCase):
    def test_locale_tags_normalize(self):
        self.assertEqual(normalize_language("ru-RU"), "ru")
        self.assertEqual(normalize_language("en_US"), "en")
        self.assertEqual(normalize_language("uk-UA"), "en")

    def test_language_manager_switches_between_ru_and_en(self):
        locale = LanguageManager("en")
        self.assertEqual(locale.language, "en")
        locale.set_language("ru-RU")
        self.assertEqual(locale.language, "ru")
        self.assertIn("Не найдена", translate("tool_missing", "ru", tool="idevice_id"))
        self.assertIn("будет пропущена", translate("recommend_pair_optional", "ru"))


class AppleDeviceToolkitTests(unittest.TestCase):
    def test_discovers_model_ios_and_existing_pairing_without_mutation(self):
        runner = FakeRunner()
        with patch("sambu.apple_devices.shutil.which", side_effect=lambda name: "C:/fake/" + name):
            toolkit = AppleDeviceToolkit(runner=runner, platform_name="Linux")
            report = toolkit.diagnose()
        self.assertEqual(len(report.devices), 1)
        device = report.devices[0]
        self.assertEqual(device.family, "iPhone")
        self.assertEqual(device.product_type, "iPhone18,1")
        self.assertEqual(device.ios_version, "26.1")
        self.assertTrue(device.pairing_valid)
        commands = [" ".join(call).lower() for call in runner.calls]
        self.assertTrue(any("ideviceinfo" in item and "-k producttype" in item for item in commands))
        self.assertFalse(any(
            "ideviceinfo" in item and "-k" not in item and "--version" not in item
            for item in commands
        ))
        self.assertFalse(any(
            "idevicepair" in item and "validate" not in item and "--version" not in item
            for item in commands
        ))

    def test_windows_diagnostics_check_driver_service_and_usb_visibility(self):
        runner = FakeRunner()
        with patch("sambu.apple_devices.shutil.which", side_effect=lambda name: "C:/fake/" + name):
            toolkit = AppleDeviceToolkit(runner=runner, platform_name="Windows")
            report = toolkit.diagnose()
        codes = {item.code for item in report.diagnostics}
        self.assertIn("apple_service", codes)
        self.assertIn("apple_usb_driver", codes)
        self.assertIn("apple_usb_enumeration", codes)
        self.assertTrue(any(
            item.code == "apple_usb_enumeration" and item.status == "ok"
            for item in report.diagnostics
        ))

    def test_bin_dir_accepts_exe_names_on_windows(self):
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as directory:
            for name in ("idevice_id.exe", "ideviceinfo.exe", "idevicepair.exe"):
                Path(directory, name).touch()
            toolkit = AppleDeviceToolkit(
                bin_dir=directory, runner=runner, platform_name="Windows"
            )
            report = toolkit.diagnose()
        self.assertTrue(all(item.available for item in report.tools))

    def test_missing_tools_are_reported_without_crashing(self):
        with patch("sambu.apple_devices.shutil.which", return_value=None):
            toolkit = AppleDeviceToolkit(platform_name="Linux")
            report = toolkit.diagnose()
        self.assertTrue(all(not item.available for item in report.tools))
        self.assertTrue(any(item.status == "error" for item in report.diagnostics))

    def test_requested_udid_must_match_discovery(self):
        with patch("sambu.apple_devices.shutil.which", side_effect=lambda name: "C:/fake/" + name):
            toolkit = AppleDeviceToolkit(runner=FakeRunner(), platform_name="Linux")
            report = toolkit.diagnose(udid="NOT-CONNECTED")
        self.assertEqual(report.devices, ())
        self.assertTrue(any(item.code == "requested_device" for item in report.diagnostics))

    def test_hardware_smoke_runs_for_each_device(self):
        with patch("sambu.apple_devices.shutil.which", side_effect=lambda name: "C:/fake/" + name):
            toolkit = AppleDeviceToolkit(runner=FakeRunner(), platform_name="Linux")
            report = toolkit.run_hardware_smoke()
        self.assertEqual(report.devices_tested, 1)
        self.assertTrue(report.passed)
        self.assertTrue(any(
            item.name == "device_metadata" and item.status == "pass"
            for item in report.tests
        ))

    def test_windows_hardware_smoke_includes_driver_and_service_checks(self):
        with patch("sambu.apple_devices.shutil.which", side_effect=lambda name: "C:/fake/" + name):
            toolkit = AppleDeviceToolkit(runner=FakeRunner(), platform_name="Windows")
            report = toolkit.run_hardware_smoke()
        names = {item.name for item in report.tests}
        self.assertIn("apple_service", names)
        self.assertIn("apple_usb_driver", names)
        self.assertIn("apple_usb_enumeration", names)
        self.assertTrue(report.passed)

    def test_missing_pairing_utility_is_a_skipped_optional_check(self):
        def available(name):
            return None if name == "idevicepair" else "/fake/" + name
        with patch("sambu.apple_devices.shutil.which", side_effect=available):
            toolkit = AppleDeviceToolkit(runner=FakeRunner(), platform_name="Linux")
            report = toolkit.run_hardware_smoke()
        self.assertTrue(report.passed)
        self.assertTrue(any(
            item.name == "pairing_validation" and item.status == "skip"
            for item in report.tests
        ))

    def test_timeout_must_be_finite_and_positive(self):
        for value in (0, -1, float("nan"), float("inf")):
            with self.subTest(timeout=value):
                with self.assertRaises(ValueError):
                    AppleDeviceToolkit(timeout=value)

    def test_pairing_tool_is_optional_when_metadata_api_is_available(self):
        runner = FakeRunner()
        def available(name):
            return None if name == "idevicepair" else "/fake/" + name
        with patch("sambu.apple_devices.shutil.which", side_effect=available):
            toolkit = AppleDeviceToolkit(runner=runner, platform_name="Linux")
            report = toolkit.diagnose()
        self.assertEqual(len(report.devices), 1)
        self.assertIsNone(report.devices[0].pairing_valid)
        self.assertTrue(any(
            item.code == "tool_idevicepair" and item.status == "warning"
            for item in report.diagnostics
        ))

    def test_diagnostic_does_not_run_pair_or_device_write_commands(self):
        runner = FakeRunner()
        with patch("sambu.apple_devices.shutil.which", side_effect=lambda name: "C:/fake/" + name):
            toolkit = AppleDeviceToolkit(runner=runner, platform_name="Linux")
            toolkit.diagnose()
        commands = [" ".join(call).lower() for call in runner.calls]
        self.assertFalse(any(
            "idevicepair" in item and "validate" not in item and "--version" not in item
            for item in commands
        ))
        self.assertFalse(any(
            any(token in item for token in ("unpair", "backup", "restore", "enterrecovery"))
            for item in commands
        ))


if __name__ == "__main__":
    unittest.main()
