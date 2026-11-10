"""Read-only Apple USB and libimobiledevice diagnostics for Windows."""
from __future__ import annotations

import os
import shutil
import subprocess
from typing import Any


def _run(command: list[str], timeout: int = 8) -> dict[str, Any]:
    try:
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8",
                                errors="replace", timeout=timeout, check=False)
        return {"available": True, "returncode": result.returncode,
                "stdout": result.stdout.strip()[:12000], "stderr": result.stderr.strip()[:4000]}
    except FileNotFoundError:
        return {"available": False, "reason": "command_not_found"}
    except subprocess.TimeoutExpired:
        return {"available": True, "reason": "timeout"}
    except OSError as exc:
        return {"available": False, "reason": str(exc)[:500]}


def scan_apple_devices() -> dict[str, Any]:
    """Inspect installed tools, Apple services and paired USB devices without changing state."""
    report: dict[str, Any] = {
        "platform": os.name,
        "libimobiledevice": {},
        "apple_usb": {},
        "devices": [],
        "notes": [
            "Device model and iOS version require a trusted pairing record and a compatible ideviceinfo build.",
            "A failed USB enumeration cannot distinguish a charge-only cable from a faulty port.",
            "This diagnostic is read-only; it does not pair, trust, back up, restore or modify the device.",
        ],
    }
    idevice_id = shutil.which("idevice_id")
    ideviceinfo = shutil.which("ideviceinfo")
    report["libimobiledevice"] = {
        "idevice_id_path": idevice_id,
        "ideviceinfo_path": ideviceinfo,
        "installed": bool(idevice_id and ideviceinfo),
    }
    if idevice_id:
        listing = _run([idevice_id, "-l"])
        report["libimobiledevice"]["device_list"] = listing
        if listing.get("returncode") == 0:
            for udid in filter(None, listing.get("stdout", "").splitlines()):
                device: dict[str, Any] = {"udid": udid[:128]}
                if ideviceinfo:
                    for key, field in (("ProductType", "model_identifier"), ("ProductVersion", "ios_version"), ("DeviceName", "device_name")):
                        info = _run([ideviceinfo, "-u", udid, "-k", key])
                        value = info.get("stdout", "")
                        device[field] = value[:256] if info.get("returncode") == 0 and value else None
                    device["pairing_status"] = "paired" if device.get("ios_version") else "unavailable_or_untrusted"
                report["devices"].append(device)
    if os.name == "nt":
        service = _run(["sc", "query", "Apple Mobile Device Service"])
        report["apple_usb"]["mobile_device_service"] = service
        pnp = _run(["powershell", "-NoProfile", "-NonInteractive", "-Command",
                    "Get-PnpDevice -PresentOnly -ErrorAction SilentlyContinue | "
                    "Where-Object { $_.FriendlyName -match 'Apple|iPhone|iPad|USB' } | "
                    "Select-Object Status,Class,FriendlyName,InstanceId | ConvertTo-Json -Depth 3"], timeout=15)
        report["apple_usb"]["pnp_devices"] = pnp
        report["apple_usb"]["driver_hint"] = (
            "If no Apple device appears, install/update Apple Devices from Microsoft Store or "
            "repair Apple USB device drivers, then try a known data-capable cable and another direct USB port."
        )
    else:
        report["apple_usb"]["platform_note"] = "Windows Apple driver checks are available only on Windows."
    if not report["devices"]:
        report["summary"] = "No paired device was enumerated by the available libimobiledevice tools."
    else:
        report["summary"] = f"Detected {len(report['devices'])} device(s)."
    return report
