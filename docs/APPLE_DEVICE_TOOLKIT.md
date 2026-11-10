# Apple Device Toolkit

SAMBU provides an optional, read-only Apple device diagnostic adapter. It is a Python SDK/CLI subsystem, not an iPhone repair utility and not a substitute for Apple Devices or iTunes.

## Scope

- Detects the supported idevice_id, ideviceinfo and idevicepair command-line tools from PATH or an explicitly supplied binary directory.
- On Windows, checks Apple Mobile Device Service, the Apple USB driver package and currently enumerated Plug and Play devices using sc.exe and pnputil.exe.
- Enumerates attached iPhone/iPad UDIDs and reads only a small allow-list of identity fields: DeviceName, ProductType, ProductVersion and BuildVersion.
- Validates an existing pairing record with idevicepair validate. It never creates, replaces or deletes a pairing record.
- Produces JSON diagnostics and repeatable, non-destructive hardware smoke-test results.
- Exposes RU/EN language switching through LanguageManager and the CLI --lang option.

The adapter does not install Apple drivers, restart services, pair devices, back up data, restore firmware, change settings or run device benchmarks. A USB visibility check cannot prove that a cable or connector is physically defective; it only narrows down likely causes.

## Windows requirements

The official libimobiledevice project documents building its Windows stack with MSYS2/MinGW and notes that Windows USB communication depends on Apple Mobile Device Support because usbmuxd is not fully supported on Windows. Install Apple Mobile Device Support through a supported Apple/iTunes distribution, then use a compatible 64-bit Windows build of the libimobiledevice command-line tools.

SAMBU does not download or bundle third-party binaries. Place idevice_id.exe, ideviceinfo.exe and idevicepair.exe on PATH, or pass their directory with --bin-dir.

Useful upstream resources:

- [libimobiledevice — official project and Windows/MSYS2 build notes](https://libimobiledevice.org/)
- [libimobiledevice Windows binaries (community project)](https://github.com/jrjr/libimobiledevice-windows)
- [Apple Devices for Windows](https://support.apple.com/guide/devices-windows/welcome/windows)

A community-provided Windows binary package is not an Apple product and is not endorsed by SAMBU. Review its provenance and license before installing it.

## CLI

    # English report
    sambu device diagnose --lang en

    # Russian text report
    sambu device diagnose --lang ru

    # Machine-readable report for support bundles and CI
    sambu device diagnose --json --lang en

    # Use a portable libimobiledevice folder without changing PATH
    sambu device diagnose --bin-dir C:\tools\libimobiledevice --json

    # Validate one already-known device (does not initiate pairing)
    sambu device diagnose --udid 00008020-... --lang en

    # Run non-destructive smoke tests on all connected iPhone/iPad devices
    sambu device test --json --lang en

Exit codes: 0 means the diagnostic command completed; 1 means the requested hardware smoke test failed; 2 means CLI input or execution failed. A diagnostic report can contain warnings even when collection succeeds.

## Python API

    from sambu.apple_devices import AppleDeviceToolkit
    from sambu.i18n import LanguageManager

    locale = LanguageManager("ru")
    toolkit = AppleDeviceToolkit(
        bin_dir=r"C:\tools\libimobiledevice",
        language=locale.language,
    )
    report = toolkit.diagnose()
    print(report.to_dict())

    smoke = toolkit.run_hardware_smoke()
    print(smoke.to_dict())

AppleDiagnosticReport contains the platform, tool availability and versions, discovered devices and diagnostic checks. HardwareTestReport records each smoke test independently. Device identifiers and model/version fields are reported because they are needed to distinguish test targets; serial numbers, phone numbers, user content and backup data are never queried.

## Hardware lab CI

Ordinary hosted CI cannot validate physical USB hardware. The manual workflow .github/workflows/apple-device-lab.yml targets a Windows self-hosted runner labelled apple-device-lab. Register that runner on a machine with Apple Mobile Device Support, compatible libimobiledevice tools on PATH, and one or more trusted test devices connected by USB. The workflow runs the read-only smoke suite and uploads a JSON report. Do not put personal devices or personal device data on unattended runners.

The workflow tests every connected device exposed by idevice_id; the reported ProductType and iOS version form the hardware compatibility record. Expanding the lab to named model/OS combinations requires physically available devices and should not be inferred from simulator or mocked test results.

## RU/EN interface localization

SAMBU currently exposes the Apple toolkit through a CLI and Python API; it does not ship a graphical application window. The --lang ru|en switch localizes this subsystem's CLI diagnostics. LanguageManager is the shared locale provider intended for future GUI and host integrations. Unsupported locale tags fall back to English.

## Signed Windows installer

The release workflow builds a self-contained sambu.exe, packages it with Inno Setup, signs both the executable and installer using an organization-owned Authenticode certificate, verifies the signature, and publishes the installer artifact. Configure the repository Actions secrets:

- WINDOWS_CERTIFICATE_BASE64: base64-encoded PFX certificate.
- WINDOWS_CERTIFICATE_PASSWORD: PFX password.

No signing certificate is included in the repository. The release job fails closed when the signing secrets are missing or signature verification fails; it does not publish an unsigned installer under a signed-release name.
