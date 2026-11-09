from __future__ import annotations
import unittest
from sambu.integrations import django, fastapi, flask

class OptionalIntegrationImportsTests(unittest.TestCase):
    def test_modules_import_without_framework_packages(self):
        self.assertTrue(callable(django.create_urlpatterns))
        self.assertTrue(callable(fastapi.create_router))
        self.assertTrue(callable(flask.create_blueprint))

if __name__ == "__main__": unittest.main()
