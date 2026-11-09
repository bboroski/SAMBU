from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO

from sambu_studio.cli import main
from sambu_studio.magento import inspect_module


class MagentoStudioInspectorTests(unittest.TestCase):
    def write(self, root: Path, relative: str, content: str) -> None:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def valid_module(self, root: Path) -> None:
        self.write(root, "etc/di.xml", """<?xml version="1.0"?>
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <preference for="Vendor\\Api\\ThingInterface" type="Vendor\\Model\\Thing"/>
  <type name="Vendor\\Model\\Thing">
    <plugin name="audit" type="Vendor\\Plugin\\Audit" sortOrder="20" disabled="false"/>
  </type>
</config>""")
        self.write(root, "etc/communication.xml", """<?xml version="1.0"?>
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <topic name="heavy.order.place" request="string">
    <handler name="heavyOrderProcessor" type="Vendor\\Model\\Consumer" method="process"/>
  </topic>
</config>""")
        self.write(root, "etc/queue_topology.xml", """<?xml version="1.0"?>
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <exchange name="magento" type="topic" connection="amqp">
    <binding id="heavy-order-binding" topic="heavy.order.place" destination="heavy_orders_queue"/>
  </exchange>
</config>""")
        self.write(root, "etc/queue_publisher.xml", """<?xml version="1.0"?>
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <publisher topic="heavy.order.place">
    <connection name="amqp" exchange="magento"/>
  </publisher>
</config>""")
        self.write(root, "etc/queue_consumer.xml", """<?xml version="1.0"?>
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <consumer name="heavyOrderConsumer" queue="heavy_orders_queue"
            handler="Vendor\\Model\\Consumer::process"
            connection="amqp" maxMessages="100"/>
</config>""")

    def test_valid_di_and_queue_configuration_is_indexed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.valid_module(root)
            report = inspect_module(root)
            self.assertTrue(report.is_valid, report.diagnostics)
            self.assertEqual(len(report.preferences), 1)
            self.assertEqual(report.preferences[0]["for"], "Vendor\\Api\\ThingInterface")
            self.assertEqual(len(report.plugins), 1)
            self.assertEqual(report.plugins[0]["sortOrder"], 20)
            self.assertEqual(len(report.topics), 1)
            self.assertEqual(len(report.consumers), 1)
            self.assertEqual(len(report.exchanges), 1)
            self.assertEqual(len(report.bindings), 1)
            self.assertEqual(len(report.publishers), 1)
            self.assertEqual(report.warning_count, 0)

    def test_invalid_topic_and_direct_exchange_are_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(root, "etc/communication.xml", """<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <topic name="heavy.order.place" xsi:type="object"/>
</config>""")
            self.write(root, "etc/queue_topology.xml", """<config>
  <exchange name="magento" type="direct" connection="amqp">
    <binding id="b1" topic="heavy.order.place" destination="heavy_orders_queue"/>
  </exchange>
</config>""")
            report = inspect_module(root)
            codes = {d.code for d in report.diagnostics}
            self.assertFalse(report.is_valid)
            self.assertIn("STUDIO-MQ-003", codes)
            self.assertIn("STUDIO-MQ-004", codes)
            self.assertIn("STUDIO-MQ-022", codes)

    def test_cross_file_consumer_and_publisher_links_are_warned(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(root, "etc/communication.xml", '<config><topic name="order.place" request="string"/></config>')
            self.write(root, "etc/queue_consumer.xml", '<config><consumer name="orders" queue="missing_queue"/></config>')
            self.write(root, "etc/queue_publisher.xml", '<config><publisher topic="order.place"><connection name="amqp" exchange="missing_exchange"/></publisher></config>')
            report = inspect_module(root)
            self.assertEqual(report.error_count, 0)
            self.assertEqual(report.warning_count, 2)
            self.assertEqual({d.code for d in report.diagnostics}, {"STUDIO-MQ-041", "STUDIO-MQ-043"})

    def test_xml_dtd_and_entity_declarations_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(root, "etc/di.xml", '<!DOCTYPE config [<!ENTITY x "boom">]><config/>')
            report = inspect_module(root)
            self.assertIn("STUDIO-XML-004", {d.code for d in report.diagnostics})
            self.assertFalse(report.preferences)

    def test_malformed_xml_and_non_utf8_are_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(root, "etc/di.xml", "<config><broken></config>")
            report = inspect_module(root)
            self.assertIn("STUDIO-XML-005", {d.code for d in report.diagnostics})

    def test_vendor_generated_and_var_folders_are_skipped(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(root, "vendor/package/etc/di.xml", "<config/>")
            self.write(root, "generated/code/etc/di.xml", "<config/>")
            self.write(root, "var/cache/etc/di.xml", "<config/>")
            report = inspect_module(root)
            self.assertEqual(report.files_scanned, [])
            self.assertEqual(report.warning_count, 1)

    def test_cli_text_and_json_exit_codes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.valid_module(root)
            text_output = StringIO()
            with redirect_stdout(text_output):
                code = main(["inspect", str(root)])
            self.assertEqual(code, 0)
            self.assertIn("Static checks passed", text_output.getvalue())

            json_output = StringIO()
            with redirect_stdout(json_output):
                code = main(["inspect", str(root), "--format", "json"])
            self.assertEqual(code, 0)
            payload = json.loads(json_output.getvalue())
            self.assertEqual(payload["schema_version"], 1)
            self.assertEqual(payload["summary"]["plugins"], 1)

    def test_cli_returns_nonzero_for_invalid_configuration(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(root, "etc/di.xml", "<config>")
            output = StringIO()
            with redirect_stdout(output):
                code = main(["inspect", str(root)])
            self.assertEqual(code, 1)


    def test_invalid_utf8_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "etc" / "di.xml"
            path.parent.mkdir(parents=True)
            path.write_bytes(b"<config>\xff</config>")
            report = inspect_module(root)
            self.assertIn("STUDIO-XML-003", {d.code for d in report.diagnostics})

    def test_oversized_xml_is_rejected_before_parsing(self):
        from sambu_studio.magento import MAX_XML_BYTES
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(root, "etc/di.xml", "<config>" + (" " * MAX_XML_BYTES) + "</config>")
            report = inspect_module(root)
            self.assertIn("STUDIO-XML-002", {d.code for d in report.diagnostics})

    def test_symlinked_xml_is_not_followed(self):
        import os
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            outside = root.parent / (root.name + "-outside.xml")
            outside.write_text("<config><preference for='A' type='B'/></config>", encoding="utf-8")
            link = root / "etc" / "di.xml"
            link.parent.mkdir(parents=True)
            try:
                link.symlink_to(outside)
            except (OSError, NotImplementedError):
                outside.unlink(missing_ok=True)
                self.skipTest("symlink creation is not supported on this platform")
            report = inspect_module(root)
            self.assertEqual(report.files_scanned, [])
            outside.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
