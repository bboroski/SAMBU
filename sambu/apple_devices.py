"""Non-destructive Apple device discovery and diagnostics.

This module shells out only to explicitly supported libimobiledevice utilities.
It never initiates pairing, changes device settings, installs drivers or writes to
an iPhone/iPad. Windows USB diagnostics are read-only.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import platform as host_platform
import math
import shutil
import subprocess
from typing import Callable, Sequence

from .i18n import LanguageManager


Runner = Callable[..., subprocess.CompletedProcess[str]]


@dataclass(frozen=True)
class ToolStatus:
    name: str
    available: bool
    path: str | None = None
    version: str | None = None
    error: str | None = None


@dataclass(frozen=True)
class Diagnostic:
    code: str
    status: str
    message: str
    recommendation: str | None = None


@dataclass(frozen=True)
class AppleDevice:
    udid: str
    name: str | None = None
    product_type: str | None = None
    ios_version: str | None = None
    build_version: str | None = None
    pairing_valid: bool | None = None
    pairing_detail: str | None = None

    @property
    def family(self) -> str:
        product_type = (self.product_type or "").lower()
        if product_type.startswith("iphone"):
            return "iPhone"
        if product_type.startswith("ipad"):
            return "iPad"
        return "unknown"


@dataclass(frozen=True)
class AppleDiagnosticReport:
    platform: str
    tools: tuple[ToolStatus, ...]
    devices: tuple[AppleDevice, ...]
    diagnostics: tuple[Diagnostic, ...]

    @property
    def ok(self) -> bool:
        return all(item.status not in {"error"} for item in self.diagnostics)

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": "1.0",
            "platform": self.platform,
            "device_count": len(self.devices),
            "tools": [asdict(item) for item in self.tools],
            "devices": [
                {**asdict(item), "family": item.family}
                for item in self.devices
            ],
            "diagnostics": [asdict(item) for item in self.diagnostics],
        }


@dataclass(frozen=True)
class HardwareTest:
    name: str
    status: str
    message: str
    device_udid: str | None = None


@dataclass(frozen=True)
class HardwareTestReport:
    platform: str
    tests: tuple[HardwareTest, ...]
    devices_tested: int

    @property
    def passed(self) -> bool:
        return bool(self.tests) and all(
            item.status in {"pass", "skip"} for item in self.tests
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": "1.0",
            "platform": self.platform,
            "devices_tested": self.devices_tested,
            "passed": self.passed,
            "tests": [asdict(item) for item in self.tests],
        }


class AppleDeviceToolkit:
    """Read-only iPhone/iPad diagnostics backed by libimobiledevice CLI tools."""

    REQUIRED_TOOLS = ("idevice_id", "ideviceinfo")
    OPTIONAL_TOOLS = ("idevicepair",)
    ALL_TOOLS = REQUIRED_TOOLS + OPTIONAL_TOOLS

    def __init__(
        self,
        bin_dir: str | Path | None = None,
        language: str = "en",
        timeout: float = 8.0,
        runner: Runner = subprocess.run,
        platform_name: str | None = None,
    ) -> None:
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("timeout must be a finite number greater than zero")
        self.bin_dir = Path(bin_dir).expanduser() if bin_dir is not None else None
        self.locale = LanguageManager(language)
        self.timeout = float(timeout)
        self._runner = runner
        self.platform = platform_name or host_platform.system()

    def set_language(self, language: str) -> str:
        return self.locale.set_language(language)

    def _message(self, key: str, **values: object) -> str:
        return self.locale.gettext(key, **values)

    def _resolve_tool(self, name: str) -> str | None:
        candidates = [name + ".exe", name] if self.platform.lower().startswith("win") else [name]
        if self.bin_dir is not None:
            for candidate in candidates:
                path = self.bin_dir / candidate
                if path.is_file():
                    return str(path)
            return None
        for candidate in candidates:
            found = shutil.which(candidate)
            if found:
                return found
        return None

    def _run(self, command: Sequence[str]) -> subprocess.CompletedProcess[str] | None:
        try:
            completed = self._runner(
                list(command),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.timeout,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return subprocess.CompletedProcess(list(command), 127, "", str(exc))
        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        return subprocess.CompletedProcess(
            list(command), completed.returncode, str(stdout), str(stderr)
        )

    def _run_tool(self, name: str, args: Sequence[str]) -> subprocess.CompletedProcess[str] | None:
        path = self._resolve_tool(name)
        return None if path is None else self._run([path, *args])

    @staticmethod
    def _short_error(result: subprocess.CompletedProcess[str] | None) -> str | None:
        if result is None:
            return None
        message = (result.stderr or result.stdout or "").strip().replace("\r", " ")
        return message[:240] or None

    def _probe_tools(self) -> tuple[ToolStatus, ...]:
        tools: list[ToolStatus] = []
        for name in self.ALL_TOOLS:
            path = self._resolve_tool(name)
            if path is None:
                tools.append(ToolStatus(name=name, available=False))
                continue
            version_result = self._run([path, "--version"])
            version = None
            error = None
            runnable = version_result is not None and version_result.returncode == 0
            if version_result is not None:
                candidate = (version_result.stdout or version_result.stderr).strip()
                if runnable and candidate:
                    version = candidate.splitlines()[0][:120]
                elif not runnable:
                    error = self._short_error(version_result) or "The utility did not pass its version probe."
            tools.append(ToolStatus(
                name=name, available=runnable, path=path, version=version, error=error
            ))
        return tuple(tools)

    def _windows_diagnostics(self) -> tuple[list[Diagnostic], bool | None]:
        diagnostics: list[Diagnostic] = []
        service = self._run(["sc.exe", "query", "Apple Mobile Device Service"])
        service_text = (
            (service.stdout if service else "") + " " +
            (service.stderr if service else "")
        ).lower()
        if service is None or service.returncode == 127:
            diagnostics.append(Diagnostic(
                "apple_service_check", "unsupported",
                self._message("windows_diag_unavailable", reason="sc.exe is unavailable"),
            ))
        elif "1060" in service_text or "does not exist" in service_text:
            diagnostics.append(Diagnostic(
                "apple_service", "warning", self._message("windows_service_missing"),
                self._message("recommend_install_driver"),
            ))
        elif "running" in service_text:
            diagnostics.append(Diagnostic(
                "apple_service", "ok", self._message("windows_service_running")
            ))
        elif "stopped" in service_text:
            diagnostics.append(Diagnostic(
                "apple_service", "warning", self._message("windows_service_stopped"),
                self._message("recommend_start_service"),
            ))
        else:
            diagnostics.append(Diagnostic(
                "apple_service", "warning",
                self._message(
                    "windows_diag_unavailable",
                    reason=self._short_error(service) or "unknown service state",
                ),
            ))

        drivers = self._run(["pnputil.exe", "/enum-drivers"])
        driver_text = (
            (drivers.stdout if drivers else "") + " " +
            (drivers.stderr if drivers else "")
        ).lower()
        driver_present = bool(
            drivers is not None
            and drivers.returncode == 0
            and ("usbaapl" in driver_text or "apple mobile device usb" in driver_text)
        )
        if drivers is None or drivers.returncode != 0:
            diagnostics.append(Diagnostic(
                "apple_usb_driver", "unsupported",
                self._message(
                    "windows_diag_unavailable",
                    reason=self._short_error(drivers) or "pnputil.exe is unavailable",
                ),
            ))
        else:
            diagnostics.append(Diagnostic(
                "apple_usb_driver",
                "ok" if driver_present else "warning",
                self._message(
                    "windows_driver_present" if driver_present else "windows_driver_missing"
                ),
                None if driver_present else
                self._message("recommend_install_driver"),
            ))

        devices = self._run(["pnputil.exe", "/enum-devices", "/connected"])
        pnp_text = (
            (devices.stdout if devices else "") + " " +
            (devices.stderr if devices else "")
        ).lower()
        apple_usb_present = None
        if devices is not None and devices.returncode == 0:
            apple_usb_present = (
                "apple iphone" in pnp_text
                or "apple mobile device usb" in pnp_text
                or "apple mobile device" in pnp_text
            )
            diagnostics.append(Diagnostic(
                "apple_usb_enumeration",
                "ok" if apple_usb_present else "warning",
                self._message("usb_present" if apple_usb_present else "usb_missing"),
                None if apple_usb_present else
                self._message("recommend_cable"),
            ))
        else:
            diagnostics.append(Diagnostic(
                "apple_usb_enumeration", "unsupported",
                self._message(
                    "windows_diag_unavailable",
                    reason=self._short_error(devices) or "pnputil device enumeration failed",
                ),
            ))
        return diagnostics, apple_usb_present

    @staticmethod
    def _parse_device_id_output(output: str) -> list[str]:
        return [line.strip() for line in output.splitlines() if line.strip()]

    def _read_device(self, udid: str) -> AppleDevice:
        pairing_valid: bool | None = None
        pairing_detail = None
        pairing = self._run_tool("idevicepair", ["-u", udid, "validate"])
        if pairing is not None:
            pairing_valid = pairing.returncode == 0
            pairing_detail = self._short_error(pairing) if not pairing_valid else None

        # Request each allow-listed property explicitly. Do not dump the full
        # ideviceinfo output, which can contain serial and other personal data.
        properties: dict[str, str] = {}
        for key in ("DeviceName", "ProductType", "ProductVersion", "BuildVersion"):
            result = self._run_tool("ideviceinfo", ["-u", udid, "-k", key])
            if result is not None and result.returncode == 0:
                properties[key] = result.stdout.strip()

        return AppleDevice(
            udid=udid,
            name=properties.get("DeviceName") or None,
            product_type=properties.get("ProductType") or None,
            ios_version=properties.get("ProductVersion") or None,
            build_version=properties.get("BuildVersion") or None,
            pairing_valid=pairing_valid,
            pairing_detail=pairing_detail,
        )

    def diagnose(self, udid: str | None = None) -> AppleDiagnosticReport:
        """Collect tool, driver, USB-enumeration and device-identity diagnostics."""
        tools = self._probe_tools()
        tool_map = {item.name: item for item in tools}
        diagnostics: list[Diagnostic] = []
        for name in self.REQUIRED_TOOLS + self.OPTIONAL_TOOLS:
            item = tool_map[name]
            if item.available:
                version = f" ({item.version})" if item.version else ""
                diagnostics.append(Diagnostic(
                    f"tool_{name}", "ok",
                    self._message("tool_ready", tool=name, version=version),
                ))
            else:
                optional = name in self.OPTIONAL_TOOLS
                diagnostics.append(Diagnostic(
                    f"tool_{name}", "warning" if optional else "error",
                    self._message("tool_missing", tool=name),
                    (
                        self._message("recommend_pair_optional")
                        if optional else
                        self._message("recommend_install_tools")
                    ),
                ))

        devices: list[AppleDevice] = []
        apple_usb_present: bool | None = None
        if tool_map["idevice_id"].available:
            discovery = self._run_tool("idevice_id", ["-l"])
            if discovery is not None and discovery.returncode == 0:
                udids = self._parse_device_id_output(discovery.stdout)
                if udid:
                    udids = [value for value in udids if value == udid]
                devices = [self._read_device(value) for value in udids]
                diagnostics.append(Diagnostic(
                    "device_discovery", "ok" if devices else "warning",
                    self._message("device_found", count=len(devices))
                    if devices else self._message("no_device"),
                ))
                if udid and not devices:
                    diagnostics.append(Diagnostic(
                        "requested_device", "error",
                        f"Requested UDID was not discovered: {udid}",
                    ))
            else:
                diagnostics.append(Diagnostic(
                    "device_discovery", "warning",
                    self._short_error(discovery) or self._message("no_device"),
                ))
        else:
            diagnostics.append(Diagnostic(
                "device_discovery", "error", self._message("toolchain_missing")
            ))

        if self.platform.lower().startswith("win"):
            windows_items, apple_usb_present = self._windows_diagnostics()
            diagnostics.extend(windows_items)
        else:
            diagnostics.append(Diagnostic(
                "windows_usb_diagnostics", "unsupported", self._message("not_windows")
            ))

        if devices:
            for device in devices:
                if device.product_type and device.ios_version:
                    diagnostics.append(Diagnostic(
                        f"metadata_{device.udid}", "ok",
                        self._message("metadata_available"),
                    ))
                else:
                    diagnostics.append(Diagnostic(
                        f"metadata_{device.udid}", "warning",
                        self._message("model_ios_unavailable"),
                        self._message("recommend_reconnect"),
                    ))
                if device.pairing_valid is True:
                    diagnostics.append(Diagnostic(
                        f"pairing_{device.udid}", "ok",
                        self._message("pairing_valid"),
                    ))
                elif device.pairing_valid is False:
                    diagnostics.append(Diagnostic(
                        f"pairing_{device.udid}", "warning",
                        self._message("pairing_invalid"),
                        self._message("recommend_pair_readonly"),
                    ))
                else:
                    diagnostics.append(Diagnostic(
                        f"pairing_{device.udid}", "unsupported",
                        self._message("pairing_unavailable"),
                    ))
        elif tool_map["idevice_id"].available:
            if self.platform.lower().startswith("win") and apple_usb_present is True:
                diagnostics.append(Diagnostic(
                    "usb_transport", "warning",
                    self._message("usb_detected_not_listed"),
                    self._message("recommend_transport"),
                ))
            else:
                diagnostics.append(Diagnostic(
                    "cable_port", "warning", self._message("cable_advice")
                ))

        return AppleDiagnosticReport(
            platform=self.platform,
            tools=tools,
            devices=tuple(devices),
            diagnostics=tuple(diagnostics),
        )

    def run_hardware_smoke(self, udid: str | None = None) -> HardwareTestReport:
        """Run read-only smoke tests against every discovered iPhone/iPad."""
        report = self.diagnose(udid=udid)
        tests: list[HardwareTest] = []
        tool_map = {item.name: item for item in report.tools}
        tools_ready = all(tool_map[name].available for name in self.REQUIRED_TOOLS)
        tests.append(HardwareTest(
            "libimobiledevice_toolchain",
            "pass" if tools_ready else "fail",
            "Required command-line tools are available."
            if tools_ready else self._message("smoke_tool_missing"),
        ))
        if not report.devices:
            tests.append(HardwareTest(
                "connected_device", "fail", self._message("smoke_no_device")
            ))
            return HardwareTestReport(self.platform, tuple(tests), 0)

        for device in report.devices:
            prefix = device.udid
            if device.family == "unknown":
                tests.append(HardwareTest(
                    "device_family", "fail", self._message("device_not_apple"), prefix
                ))
            else:
                tests.append(HardwareTest(
                    "device_family", "pass",
                    self._message("device_detected", family=device.family), prefix
                ))
            metadata_ok = bool(device.product_type and device.ios_version)
            tests.append(HardwareTest(
                "device_metadata",
                "pass" if metadata_ok else "warn",
                self._message("device_ok")
                if metadata_ok else self._message("metadata_incomplete"),
                prefix,
            ))
            pairing_status = (
                "pass" if device.pairing_valid is True else
                "warn" if device.pairing_valid is False else "skip"
            )
            pairing_key = (
                "pairing_valid" if pairing_status == "pass" else
                "pairing_invalid" if pairing_status == "warn" else
                "pairing_unavailable"
            )
            tests.append(HardwareTest(
                "pairing_validation", pairing_status,
                self._message(pairing_key), prefix,
            ))

        # Promote Windows transport checks into the physical hardware suite.
        # An unsupported check is explicitly skipped; a detected warning fails
        # the suite so driver/service regressions are visible in the lab.
        windows_codes = {
            "apple_service", "apple_service_check", "apple_usb_driver",
            "apple_usb_enumeration", "usb_transport", "cable_port",
        }
        status_map = {"ok": "pass", "warning": "warn", "error": "fail", "unsupported": "skip"}
        for diagnostic in report.diagnostics:
            if diagnostic.code in windows_codes:
                tests.append(HardwareTest(
                    diagnostic.code,
                    status_map.get(diagnostic.status, "skip"),
                    diagnostic.message,
                ))

        return HardwareTestReport(self.platform, tuple(tests), len(report.devices))
