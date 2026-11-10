"""Small dependency-free RU/EN localization primitives for SAMBU."""
from __future__ import annotations

SUPPORTED_LANGUAGES = ("en", "ru")

_MESSAGES = {
    "en": {
        "tool_missing": "Required libimobiledevice utility is not available: {tool}.",
        "tool_ready": "{tool} is available{version}.",
        "device_found": "Found {count} Apple device(s).",
        "no_device": "No Apple device was enumerated by idevice_id.",
        "windows_driver_present": "Apple Mobile Device USB driver is present in the Windows driver store.",
        "windows_driver_missing": "Apple Mobile Device USB driver was not found in the Windows driver store.",
        "windows_service_running": "Apple Mobile Device Service is running.",
        "windows_service_stopped": "Apple Mobile Device Service is installed but not running.",
        "windows_service_missing": "Apple Mobile Device Service was not found.",
        "usb_present": "Windows currently lists an Apple USB device.",
        "usb_missing": "Windows did not list an Apple USB device among connected devices.",
        "device_detected": "Detected {family}.",
        "model_unavailable": "model unavailable",
        "version_unavailable": "version unavailable",
        "windows_diag_unavailable": "Windows USB diagnostics could not be completed: {reason}",
        "pairing_valid": "The existing pairing record was validated.",
        "pairing_invalid": "The pairing record could not be validated; unlock the device and accept the Trust prompt.",
        "pairing_unavailable": "Pairing validation is unavailable because idevicepair is missing.",
        "metadata_available": "Device identity and iOS version were read successfully.",
        "model_ios_unavailable": "Model or iOS version could not be read; pairing, Trust approval or device connectivity may be required.",
        "cable_advice": "No device is visible to libimobiledevice. Try a known-good data cable, a direct USB port (not a hub), another port, an unlocked device and the Trust This Computer prompt. This check cannot identify a broken cable or port with certainty.",
        "usb_detected_not_listed": "Windows sees an Apple USB device, but idevice_id does not enumerate it. Check Apple Mobile Device Service, matching x64 binaries and the pairing/trust state.",
        "toolchain_missing": "The required libimobiledevice command-line tools are incomplete.",
        "not_windows": "Apple USB driver checks are only available on Windows.",
        "device_not_apple": "The connected device does not identify itself as an iPhone or iPad.",
        "metadata_incomplete": "The device was discovered, but ProductType or ProductVersion is missing.",
        "device_ok": "The iPhone/iPad passed the non-destructive identity smoke test.",
        "smoke_no_device": "No connected iPhone or iPad was available for hardware tests.",
        "smoke_tool_missing": "Hardware tests require idevice_id and ideviceinfo.",
        "recommend_pair_readonly": "This diagnostic only validates an existing pairing record; it never creates, replaces or deletes one.",
        "device_detected": "Detected {family}.",
        "model_unavailable": "model unavailable",
        "version_unavailable": "version unavailable",
        "recommend_pair_optional": "Pairing validation will be skipped; model and iOS metadata can still be read.",
        "recommend_install_tools": "Install a compatible libimobiledevice Windows build and add its bin directory to PATH or pass --bin-dir.",
        "recommend_install_driver": "Check Device Manager and install Apple Mobile Device Support from an official Apple/iTunes distribution.",
        "recommend_start_service": "Start Apple Mobile Device Service from Windows Services and reconnect the device.",
        "recommend_reconnect": "Unlock the device, accept Trust This Computer, validate pairing, then reconnect.",
        "recommend_cable": "Try a known-good data cable, a direct USB port and another port; inspect Device Manager for unknown USB devices.",
        "recommend_transport": "Restart Apple Mobile Device Service, confirm 64-bit binary compatibility and check the Trust/pairing state.",
        "report_title": "SAMBU Apple Device Diagnostics",
        "platform_label": "Platform",
        "tools_label": "Tools",
        "devices_label": "Devices",
        "device_ios_label": "iOS",
        "pairing_label": "pairing",
        "smoke_title": "SAMBU Apple hardware smoke tests",
        "test_status_ok": "OK",
        "test_status_warning": "WARNING",
        "test_status_error": "ERROR",
        "test_status_unsupported": "UNSUPPORTED",
        "test_status_pass": "PASS",
        "test_status_fail": "FAIL",
        "test_status_skip": "SKIP",
        "test_status_warn": "WARN",
        "tool_state_available": "available",
        "tool_state_missing": "missing",
    },
    "ru": {
        "tool_missing": "Не найдена необходимая утилита libimobiledevice: {tool}.",
        "tool_ready": "{tool} доступна{version}.",
        "device_found": "Обнаружено устройств Apple: {count}.",
        "no_device": "idevice_id не обнаружила подключённое устройство Apple.",
        "windows_driver_present": "Драйвер Apple Mobile Device USB найден в хранилище драйверов Windows.",
        "windows_driver_missing": "Драйвер Apple Mobile Device USB не найден в хранилище драйверов Windows.",
        "windows_service_running": "Служба Apple Mobile Device Service запущена.",
        "windows_service_stopped": "Служба Apple Mobile Device Service установлена, но не запущена.",
        "windows_service_missing": "Служба Apple Mobile Device Service не найдена.",
        "usb_present": "Windows отображает подключённое USB-устройство Apple.",
        "usb_missing": "Windows не отображает USB-устройство Apple среди подключённых устройств.",
        "device_detected": "Обнаружено устройство: {family}.",
        "model_unavailable": "модель не определена",
        "version_unavailable": "версия не определена",
        "windows_diag_unavailable": "Не удалось выполнить диагностику USB в Windows: {reason}",
        "pairing_valid": "Существующая запись pairing успешно проверена.",
        "pairing_invalid": "Не удалось проверить pairing; разблокируйте устройство и подтвердите запрос «Доверять этому компьютеру».",
        "pairing_unavailable": "Проверка pairing недоступна: отсутствует idevicepair.",
        "metadata_available": "Модель устройства и версия iOS успешно прочитаны.",
        "model_ios_unavailable": "Не удалось прочитать модель или версию iOS; может потребоваться pairing, подтверждение доверия или восстановление соединения.",
        "cable_advice": "libimobiledevice не видит устройство. Проверьте заведомо исправный кабель с передачей данных, прямой USB-порт без хаба, другой порт, разблокировку устройства и запрос «Доверять этому компьютеру». Эта проверка не может достоверно определить поломку кабеля или порта.",
        "usb_detected_not_listed": "Windows видит USB-устройство Apple, но idevice_id его не перечисляет. Проверьте Apple Mobile Device Service, совместимость x64-бинарников и состояние pairing/доверия.",
        "toolchain_missing": "Набор консольных утилит libimobiledevice установлен не полностью.",
        "not_windows": "Проверка USB-драйверов Apple доступна только в Windows.",
        "device_not_apple": "Подключённое устройство не определяется как iPhone или iPad.",
        "metadata_incomplete": "Устройство обнаружено, но ProductType или ProductVersion отсутствует.",
        "device_ok": "iPhone/iPad прошёл неразрушающий тест идентификации.",
        "smoke_no_device": "Для аппаратных тестов не найден подключённый iPhone или iPad.",
        "smoke_tool_missing": "Для аппаратных тестов нужны idevice_id и ideviceinfo.",
        "recommend_pair_readonly": "Диагностика проверяет только существующую запись pairing и не создаёт, не заменяет и не удаляет её.",
        "device_detected": "Обнаружено устройство: {family}.",
        "model_unavailable": "модель не определена",
        "version_unavailable": "версия не определена",
        "recommend_pair_optional": "Проверка pairing будет пропущена; модель и версию iOS всё равно можно прочитать.",
        "recommend_install_tools": "Установите совместимую сборку libimobiledevice для Windows и добавьте папку bin в PATH либо укажите --bin-dir.",
        "recommend_install_driver": "Проверьте Диспетчер устройств и установите Apple Mobile Device Support из официального пакета Apple/iTunes.",
        "recommend_start_service": "Запустите Apple Mobile Device Service в службах Windows и переподключите устройство.",
        "recommend_reconnect": "Разблокируйте устройство, подтвердите «Доверять этому компьютеру», проверьте pairing и подключите устройство повторно.",
        "recommend_cable": "Проверьте кабель с передачей данных, прямой USB-порт без хаба и другой порт; посмотрите Диспетчер устройств на наличие неизвестных USB-устройств.",
        "recommend_transport": "Перезапустите Apple Mobile Device Service, проверьте совместимость 64-разрядных утилит и состояние доверия/pairing.",
        "report_title": "Диагностика устройств Apple в SAMBU",
        "platform_label": "Платформа",
        "tools_label": "Утилиты",
        "devices_label": "Устройства",
        "device_ios_label": "iOS",
        "pairing_label": "pairing",
        "smoke_title": "Аппаратные smoke-тесты Apple в SAMBU",
        "test_status_ok": "НОРМА",
        "test_status_warning": "ПРЕДУПРЕЖДЕНИЕ",
        "test_status_error": "ОШИБКА",
        "test_status_unsupported": "НЕ ПОДДЕРЖИВАЕТСЯ",
        "test_status_pass": "УСПЕХ",
        "test_status_fail": "ОШИБКА",
        "test_status_skip": "ПРОПУСК",
        "test_status_warn": "ПРЕДУПРЕЖДЕНИЕ",
        "tool_state_available": "доступна",
        "tool_state_missing": "не найдена",
    },
}


def normalize_language(language: str | None, default: str = "en") -> str:
    """Normalize locale tags such as ru-RU and en-US to supported language codes."""
    candidate = (language or default or "en").strip().lower().replace("_", "-").split("-", 1)[0]
    return candidate if candidate in SUPPORTED_LANGUAGES else normalize_language(default, "en")


def translate(key: str, language: str = "en", **values: object) -> str:
    """Translate a stable message key, falling back to English and then the key."""
    locale = normalize_language(language)
    template = _MESSAGES.get(locale, {}).get(key, _MESSAGES["en"].get(key, key))
    try:
        return template.format(**values)
    except (KeyError, ValueError):
        return template


class LanguageManager:
    """Mutable RU/EN locale provider for CLI and host application surfaces."""

    def __init__(self, language: str = "en") -> None:
        self._language = normalize_language(language)

    @property
    def language(self) -> str:
        return self._language

    @property
    def supported_languages(self) -> tuple[str, ...]:
        return SUPPORTED_LANGUAGES

    def set_language(self, language: str) -> str:
        self._language = normalize_language(language)
        return self._language

    def gettext(self, key: str, **values: object) -> str:
        return translate(key, self._language, **values)
