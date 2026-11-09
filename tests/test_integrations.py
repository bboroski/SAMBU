from __future__ import annotations
import importlib.util
import unittest

from sambu.integrations import django, fastapi, flask

class OptionalIntegrationImportsTests(unittest.TestCase):
    def test_adapter_modules_import_without_framework_packages(self):
        self.assertTrue(callable(django.create_urlpatterns))
        self.assertTrue(callable(fastapi.create_router))
        self.assertTrue(callable(flask.create_blueprint))

def build_ui(principal):
    from sambu.jiu_jitsu import JiuJitsuApp, ViewDefinition, ViewNode
    app=JiuJitsuApp(principal)
    app.register_view(ViewDefinition("/", "Home", ViewNode("home", "page")))
    app.navigate("/")
    return app

@unittest.skipUnless(importlib.util.find_spec("flask"), "Flask extra is not installed")
class FlaskAdapterFactoryTests(unittest.TestCase):
    def test_blueprint_serves_snapshot_for_host_resolved_principal(self):
        from flask import Flask
        blueprint=flask.create_blueprint(lambda p: build_ui(p), lambda: "alice")
        app=Flask("sambu-test")
        app.register_blueprint(blueprint)
        response=app.test_client().get("/sambu/snapshot")
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.get_json()["route"],"/")

@unittest.skipUnless(importlib.util.find_spec("django"), "Django extra is not installed")
class DjangoAdapterFactoryTests(unittest.TestCase):
    def test_urlpatterns_are_registered(self):
        patterns=django.create_urlpatterns(lambda p: build_ui(p), lambda request: "alice")
        routes=[item.pattern._route for item in patterns]
        self.assertIn("snapshot/",routes)
        self.assertIn("modals/close/",routes)

@unittest.skipUnless(importlib.util.find_spec("fastapi"), "FastAPI extra is not installed")
class FastAPIAdapterFactoryTests(unittest.TestCase):
    def test_router_resolves_request_annotations_and_static_modal_route(self):
        router=fastapi.create_router(lambda p: build_ui(p), lambda request: "alice")
        paths=[item.path for item in router.routes]
        self.assertIn("/sambu/snapshot",paths)
        self.assertIn("/sambu/modals/close",paths)
        self.assertLess(paths.index("/sambu/modals/close"),paths.index("/sambu/modals/{modal_id}"))

if __name__ == "__main__":
    unittest.main()
