"""Static Magento project inspection for SAMBU Studio.

No Magento runtime, XSD resolver, network client or external dependency is loaded.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
import re
import xml.etree.ElementTree as ET


CONFIG_NAMES = {
    "di.xml",
    "communication.xml",
    "queue_consumer.xml",
    "queue_topology.xml",
    "queue_publisher.xml",
}
SKIP_DIRS = {
    ".git", ".idea", ".vscode", "generated", "node_modules",
    "pub", "var", "vendor",
}
MAX_XML_BYTES = 2 * 1024 * 1024
VALID_CONNECTIONS = {"amqp", "stomp", "db"}
XSI_TYPE = "{http://www.w3.org/2001/XMLSchema-instance}type"


@dataclass(frozen=True)
class Diagnostic:
    path: str
    code: str
    severity: str
    message: str


@dataclass
class InspectionReport:
    root: str
    files_scanned: list[str] = field(default_factory=list)
    preferences: list[dict[str, str]] = field(default_factory=list)
    plugins: list[dict[str, str | int | bool | None]] = field(default_factory=list)
    topics: list[dict[str, object]] = field(default_factory=list)
    consumers: list[dict[str, str]] = field(default_factory=list)
    exchanges: list[dict[str, str]] = field(default_factory=list)
    bindings: list[dict[str, str]] = field(default_factory=list)
    publishers: list[dict[str, str]] = field(default_factory=list)
    diagnostics: list[Diagnostic] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return sum(item.severity == "error" for item in self.diagnostics)

    @property
    def warning_count(self) -> int:
        return sum(item.severity == "warning" for item in self.diagnostics)

    @property
    def is_valid(self) -> bool:
        return self.error_count == 0

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "root": self.root,
            "is_valid": self.is_valid,
            "summary": {
                "files_scanned": len(self.files_scanned),
                "preferences": len(self.preferences),
                "plugins": len(self.plugins),
                "topics": len(self.topics),
                "consumers": len(self.consumers),
                "exchanges": len(self.exchanges),
                "bindings": len(self.bindings),
                "publishers": len(self.publishers),
                "errors": self.error_count,
                "warnings": self.warning_count,
            },
            "files_scanned": self.files_scanned,
            "preferences": self.preferences,
            "plugins": self.plugins,
            "topics": self.topics,
            "consumers": self.consumers,
            "exchanges": self.exchanges,
            "bindings": self.bindings,
            "publishers": self.publishers,
            "diagnostics": [asdict(item) for item in self.diagnostics],
        }


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _diag(
    report: InspectionReport,
    path: str,
    code: str,
    severity: str,
    message: str,
) -> None:
    report.diagnostics.append(Diagnostic(path, code, severity, message))


def _required(
    element: ET.Element,
    attributes: tuple[str, ...],
    report: InspectionReport,
    path: str,
    code: str,
    element_name: str,
) -> bool:
    missing = [name for name in attributes if not (element.get(name) or "").strip()]
    if not missing:
        return True
    _diag(
        report,
        path,
        code,
        "error",
        f"{element_name} is missing required attribute(s): {', '.join(missing)}",
    )
    return False


def _validate_bool(
    element: ET.Element,
    attribute: str,
    report: InspectionReport,
    path: str,
    code: str,
    element_name: str,
) -> None:
    value = element.get(attribute)
    if value is not None and value.strip().lower() not in {"true", "false"}:
        _diag(
            report,
            path,
            code,
            "error",
            f"{element_name}.{attribute} must be 'true' or 'false'",
        )


def _parse_xml(path: Path, root: Path, report: InspectionReport) -> ET.Element | None:
    relative = _relative(path, root)
    try:
        data = path.read_bytes()
    except OSError as exc:
        _diag(report, relative, "STUDIO-XML-001", "error", f"Cannot read XML file: {exc}")
        return None

    if len(data) > MAX_XML_BYTES:
        _diag(
            report,
            relative,
            "STUDIO-XML-002",
            "error",
            f"XML file exceeds the {MAX_XML_BYTES}-byte inspection limit",
        )
        return None

    # Magento configuration files are UTF-8. Decoding before the DTD check
    # also prevents UTF-16 byte streams from bypassing the declaration guard.
    try:
        source = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        _diag(report, relative, "STUDIO-XML-003", "error", "XML configuration must be UTF-8")
        return None

    if re.search(r"<!\s*(DOCTYPE|ENTITY)\b", source, re.IGNORECASE):
        _diag(
            report,
            relative,
            "STUDIO-XML-004",
            "error",
            "DOCTYPE and ENTITY declarations are not accepted by the static inspector",
        )
        return None

    try:
        document = ET.fromstring(source)
    except ET.ParseError as exc:
        location = ""
        if getattr(exc, "position", None):
            location = f" at line {exc.position[0]}, column {exc.position[1]}"
        _diag(report, relative, "STUDIO-XML-005", "error", f"Malformed XML{location}: {exc}")
        return None

    if _local(document.tag) != "config":
        _diag(
            report,
            relative,
            "STUDIO-XML-006",
            "error",
            "Magento configuration document must have a <config> root element",
        )
        return None
    return document


def _inspect_di(document: ET.Element, path: str, report: InspectionReport) -> None:
    preference_targets: dict[str, str] = {}
    plugin_names: set[tuple[str, str]] = set()

    for element in document.iter():
        tag = _local(element.tag)
        if tag == "preference":
            if not _required(element, ("for", "type"), report, path, "STUDIO-DI-001", "preference"):
                continue
            target = element.get("for", "")
            implementation = element.get("type", "")
            if target in preference_targets and preference_targets[target] != implementation:
                _diag(
                    report,
                    path,
                    "STUDIO-DI-002",
                    "warning",
                    f"Multiple preference mappings for {target!r} occur in the same file",
                )
            preference_targets[target] = implementation
            report.preferences.append({"path": path, "for": target, "type": implementation})

        if tag != "type":
            continue
        observed = element.get("name", "")
        if not observed:
            continue
        for plugin in element:
            if _local(plugin.tag) != "plugin":
                continue
            valid = _required(plugin, ("name", "type"), report, path, "STUDIO-DI-003", "plugin")
            plugin_name = plugin.get("name", "")
            plugin_type = plugin.get("type", "")
            if not valid:
                continue
            identity = (observed, plugin_name)
            if identity in plugin_names:
                _diag(
                    report,
                    path,
                    "STUDIO-DI-004",
                    "warning",
                    f"Plugin name {plugin_name!r} is repeated for observed type {observed!r}",
                )
            plugin_names.add(identity)
            sort_order: int | None = None
            raw_sort = plugin.get("sortOrder")
            if raw_sort is not None:
                try:
                    sort_order = int(raw_sort)
                    if sort_order < 0:
                        raise ValueError
                except ValueError:
                    _diag(
                        report,
                        path,
                        "STUDIO-DI-005",
                        "error",
                        f"Plugin {plugin_name!r} has an invalid non-negative integer sortOrder",
                    )
                    sort_order = None
            _validate_bool(plugin, "disabled", report, path, "STUDIO-DI-006", "plugin")
            report.plugins.append({
                "path": path,
                "observed_type": observed,
                "name": plugin_name,
                "type": plugin_type,
                "sortOrder": sort_order,
                "disabled": plugin.get("disabled", "false").strip().lower() == "true",
            })


def _inspect_communication(document: ET.Element, path: str, report: InspectionReport) -> None:
    seen: set[str] = set()
    for topic in document:
        if _local(topic.tag) != "topic":
            continue
        if not _required(topic, ("name",), report, path, "STUDIO-MQ-001", "topic"):
            continue
        name = topic.get("name", "")
        if name in seen:
            _diag(report, path, "STUDIO-MQ-002", "error", f"Duplicate topic name {name!r}")
        seen.add(name)
        if XSI_TYPE in topic.attrib:
            _diag(
                report,
                path,
                "STUDIO-MQ-003",
                "error",
                "The <topic> element uses xsi:type; define its message contract with request or schema",
            )
        has_request = bool((topic.get("request") or "").strip())
        has_schema = bool((topic.get("schema") or "").strip())
        if has_request == has_schema:
            _diag(
                report,
                path,
                "STUDIO-MQ-004",
                "error",
                f"Topic {name!r} must define exactly one of request or schema",
            )
        handlers: list[dict[str, str | bool]] = []
        handler_names: set[str] = set()
        for handler in topic:
            if _local(handler.tag) != "handler":
                continue
            valid = _required(handler, ("name", "type", "method"), report, path, "STUDIO-MQ-005", "handler")
            if not valid:
                continue
            hname = handler.get("name", "")
            if hname in handler_names:
                _diag(report, path, "STUDIO-MQ-006", "error", f"Duplicate handler name {hname!r} for topic {name!r}")
            handler_names.add(hname)
            _validate_bool(handler, "disabled", report, path, "STUDIO-MQ-007", "handler")
            handlers.append({
                "name": hname,
                "type": handler.get("type", ""),
                "method": handler.get("method", ""),
                "disabled": handler.get("disabled", "false").strip().lower() == "true",
            })
        report.topics.append({
            "path": path,
            "name": name,
            "request": topic.get("request", ""),
            "schema": topic.get("schema", ""),
            "response": topic.get("response", ""),
            "handlers": handlers,
        })


def _inspect_consumers(document: ET.Element, path: str, report: InspectionReport) -> None:
    seen: set[str] = set()
    for consumer in document:
        if _local(consumer.tag) != "consumer":
            continue
        if not _required(consumer, ("name", "queue"), report, path, "STUDIO-MQ-010", "consumer"):
            continue
        name = consumer.get("name", "")
        if name in seen:
            _diag(report, path, "STUDIO-MQ-011", "error", f"Duplicate consumer name {name!r}")
        seen.add(name)
        connection = consumer.get("connection", "")
        if connection and connection not in VALID_CONNECTIONS:
            _diag(report, path, "STUDIO-MQ-012", "error", f"Consumer {name!r} uses unsupported connection {connection!r}")
        for attribute in ("maxMessages", "maxIdleTime", "sleep"):
            raw = consumer.get(attribute)
            if raw is None:
                continue
            minimum = 1 if attribute == "maxMessages" else 0
            try:
                number = int(raw)
                if number < minimum:
                    raise ValueError
            except ValueError:
                _diag(
                    report,
                    path,
                    "STUDIO-MQ-013",
                    "error",
                    f"Consumer {name!r} has invalid {attribute}; expected integer >= {minimum}",
                )
        if (consumer.get("maxIdleTime") is not None or consumer.get("sleep") is not None) and consumer.get("maxMessages") is None:
            _diag(
                report,
                path,
                "STUDIO-MQ-014",
                "warning",
                f"Consumer {name!r} sets maxIdleTime or sleep without maxMessages",
            )
        spawn = consumer.get("onlySpawnWhenMessageAvailable")
        if spawn is not None and spawn not in {"0", "1"}:
            _diag(
                report,
                path,
                "STUDIO-MQ-015",
                "error",
                f"Consumer {name!r} onlySpawnWhenMessageAvailable must be '0' or '1'",
            )
        report.consumers.append({
            "path": path,
            "name": name,
            "queue": consumer.get("queue", ""),
            "handler": consumer.get("handler", ""),
            "consumerInstance": consumer.get("consumerInstance", ""),
            "connection": connection,
        })


def _inspect_topology(document: ET.Element, path: str, report: InspectionReport) -> None:
    exchange_names: set[str] = set()
    binding_ids: set[str] = set()
    for exchange in document:
        if _local(exchange.tag) != "exchange":
            continue
        if not _required(exchange, ("name",), report, path, "STUDIO-MQ-020", "exchange"):
            continue
        name = exchange.get("name", "")
        if name in exchange_names:
            _diag(report, path, "STUDIO-MQ-021", "error", f"Duplicate exchange name {name!r}")
        exchange_names.add(name)
        exchange_type = exchange.get("type", "topic")
        if exchange_type != "topic":
            _diag(
                report,
                path,
                "STUDIO-MQ-022",
                "error",
                f"Exchange {name!r} has type {exchange_type!r}; Magento supports the 'topic' exchange type",
            )
        connection = exchange.get("connection", "")
        if connection and connection not in VALID_CONNECTIONS:
            _diag(report, path, "STUDIO-MQ-023", "error", f"Exchange {name!r} uses unsupported connection {connection!r}")
        for attribute in ("durable", "autoDelete", "internal"):
            _validate_bool(exchange, attribute, report, path, "STUDIO-MQ-024", "exchange")
        report.exchanges.append({
            "path": path,
            "name": name,
            "type": exchange_type,
            "connection": connection,
            "durable": exchange.get("durable", "true"),
        })
        for binding in exchange:
            if _local(binding.tag) != "binding":
                continue
            valid = _required(binding, ("id", "topic", "destination"), report, path, "STUDIO-MQ-025", "binding")
            if not valid:
                continue
            binding_id = binding.get("id", "")
            if binding_id in binding_ids:
                _diag(report, path, "STUDIO-MQ-026", "error", f"Duplicate binding id {binding_id!r}")
            binding_ids.add(binding_id)
            destination_type = binding.get("destinationType", "queue")
            if destination_type not in {"queue", "exchange"}:
                _diag(
                    report,
                    path,
                    "STUDIO-MQ-027",
                    "error",
                    f"Binding {binding_id!r} destinationType must be 'queue' or 'exchange'",
                )
            _validate_bool(binding, "disabled", report, path, "STUDIO-MQ-028", "binding")
            if binding.get("disabled", "false").strip().lower() != "true":
                report.bindings.append({
                    "path": path,
                    "exchange": name,
                    "id": binding_id,
                    "topic": binding.get("topic", ""),
                    "destination": binding.get("destination", ""),
                    "destinationType": destination_type,
                })


def _inspect_publishers(document: ET.Element, path: str, report: InspectionReport) -> None:
    seen_topics: set[str] = set()
    for publisher in document:
        if _local(publisher.tag) != "publisher":
            continue
        if not _required(publisher, ("topic",), report, path, "STUDIO-MQ-030", "publisher"):
            continue
        topic = publisher.get("topic", "")
        if topic in seen_topics:
            _diag(report, path, "STUDIO-MQ-031", "error", f"Duplicate publisher definition for topic {topic!r}")
        seen_topics.add(topic)
        _validate_bool(publisher, "disabled", report, path, "STUDIO-MQ-032", "publisher")
        enabled_connections: list[ET.Element] = []
        for connection in publisher:
            if _local(connection.tag) != "connection":
                continue
            connection_name = connection.get("name", "")
            if connection_name and connection_name not in VALID_CONNECTIONS:
                _diag(
                    report, path, "STUDIO-MQ-033", "error",
                    f"Publisher for {topic!r} uses unsupported connection {connection_name!r}",
                )
            _validate_bool(connection, "disabled", report, path, "STUDIO-MQ-034", "publisher connection")
            if connection.get("disabled", "false").strip().lower() != "true":
                enabled_connections.append(connection)
        if len(enabled_connections) > 1:
            _diag(
                report, path, "STUDIO-MQ-035", "error",
                f"Publisher for {topic!r} enables more than one connection",
            )
        for connection in enabled_connections:
            report.publishers.append({
                "path": path,
                "topic": topic,
                "connection": connection.get("name", ""),
                "exchange": connection.get("exchange", ""),
            })
        if not enabled_connections and publisher.get("disabled", "false").strip().lower() != "true":
            _diag(
                report, path, "STUDIO-MQ-036", "warning",
                f"Publisher for {topic!r} has no explicit enabled connection; runtime connection resolution may apply",
            )


def inspect_module(module_path: str | Path) -> InspectionReport:
    """Inspect Magento XML files beneath a module/project directory.

    The scanner skips common generated/dependency directories. It does not run
    official XSD validation or resolve Magento's merged runtime configuration.
    """
    root = Path(module_path).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError(f"Magento module/project path is not a directory: {root}")

    report = InspectionReport(root=str(root))
    candidates: list[Path] = []
    for name in sorted(CONFIG_NAMES):
        for path in root.rglob(name):
            try:
                relative_parts = path.relative_to(root).parts
            except ValueError:
                continue
            if any(part in SKIP_DIRS for part in relative_parts):
                continue
            if path.is_file() and not path.is_symlink():
                candidates.append(path)

    for path in sorted(set(candidates)):
        relative = _relative(path, root)
        report.files_scanned.append(relative)
        document = _parse_xml(path, root, report)
        if document is None:
            continue
        if path.name == "di.xml":
            _inspect_di(document, relative, report)
        elif path.name == "communication.xml":
            _inspect_communication(document, relative, report)
        elif path.name == "queue_consumer.xml":
            _inspect_consumers(document, relative, report)
        elif path.name == "queue_topology.xml":
            _inspect_topology(document, relative, report)
        elif path.name == "queue_publisher.xml":
            _inspect_publishers(document, relative, report)

    if not report.files_scanned:
        _diag(
            report,
            ".",
            "STUDIO-PROJECT-001",
            "warning",
            "No recognized Magento DI or message-queue XML files were found",
        )

    declared_topics = {str(topic["name"]) for topic in report.topics}
    topology_queues = {
        binding["destination"]
        for binding in report.bindings
        if binding["destinationType"] == "queue"
    }
    exchanges = {exchange["name"] for exchange in report.exchanges}

    for binding in report.bindings:
        if binding["topic"] not in declared_topics and not any(
            marker in binding["topic"] for marker in ("*", "#")
        ):
            _diag(
                report, binding["path"], "STUDIO-MQ-040", "warning",
                f"Binding topic {binding['topic']!r} is not declared in the inspected files; it may come from a dependency",
            )

    for consumer in report.consumers:
        if consumer["queue"] not in topology_queues:
            _diag(
                report, consumer["path"], "STUDIO-MQ-041", "warning",
                f"Consumer queue {consumer['queue']!r} has no enabled queue destination in the inspected topology; it may be external",
            )

    for publisher in report.publishers:
        if publisher["topic"] not in declared_topics:
            _diag(
                report, publisher["path"], "STUDIO-MQ-042", "warning",
                f"Publisher topic {publisher['topic']!r} was not found in the inspected module; it may be declared by a dependency",
            )
        if publisher["exchange"] and publisher["exchange"] not in exchanges:
            _diag(
                report, publisher["path"], "STUDIO-MQ-043", "warning",
                f"Publisher exchange {publisher['exchange']!r} is not declared in the inspected topology; it may be external",
            )

    return report
