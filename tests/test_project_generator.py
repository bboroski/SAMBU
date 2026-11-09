from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from sambu.interpreter import execute
from sambu.project import ProjectGenerationError, create_project, generate_scaffold, parse_field_specs
from sambu.cli import main


class ProjectGeneratorTests(unittest.TestCase):
    def test_new_project_creates_conventional_layout_and_runnable_entrypoint(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "blog_app"
            created = create_project("blog_app", root)
            for relative in (
                "Sambu.toml", "src/main.sambu", "app/models",
                "app/controllers", "app/views", "config/routes.sambu",
            ):
                self.assertTrue((root / relative).exists(), relative)
            self.assertGreaterEqual(len(created), 9)
            execute((root / "src/main.sambu").read_text(encoding="utf-8"))

    def test_new_project_rejects_unsafe_names_and_nonempty_destinations(self):
        with tempfile.TemporaryDirectory() as temporary:
            occupied = Path(temporary) / "occupied"
            occupied.mkdir()
            (occupied / "keep.txt").write_text("keep", encoding="utf-8")
            with self.assertRaises(ProjectGenerationError):
                create_project("../escape", Path(temporary) / "escape")
            with self.assertRaises(ProjectGenerationError):
                create_project("safe_app", occupied)
            self.assertEqual((occupied / "keep.txt").read_text(encoding="utf-8"), "keep")

    def test_scaffold_creates_model_controller_views_migration_routes_and_test(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "app"
            create_project("blog_app", root)
            generated = generate_scaffold(root, "Post", ["title:string", "body:text"])
            expected = (
                "app/models/post.sambu",
                "app/controllers/posts_controller.sambu",
                "app/views/posts/index.html",
                "app/views/posts/show.html",
                "app/views/posts/new.html",
                "db/migrate/0001_create_posts.sambu",
                "test/posts.sambu",
                "config/routes/posts.sambu",
            )
            for relative in expected:
                self.assertTrue((root / relative).is_file(), relative)
            self.assertEqual(len(generated), len(expected))
            execute((root / "app/models/post.sambu").read_text(encoding="utf-8"))
            output: list[str] = []
            execute((root / "test/posts.sambu").read_text(encoding="utf-8"), output=output.append)
            self.assertEqual(output, ["[title, body]"])

    def test_migration_sequence_increments_without_overwriting(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "app"
            create_project("blog_app", root)
            generate_scaffold(root, "Post", ["title:string"])
            generate_scaffold(root, "Comment", ["body:text"])
            self.assertTrue((root / "db/migrate/0001_create_posts.sambu").exists())
            self.assertTrue((root / "db/migrate/0002_create_comments.sambu").exists())

    def test_scaffold_rejects_invalid_model_and_field_declarations(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "app"
            create_project("blog_app", root)
            for model, fields in (
                ("posts", ["title:string"]),
                ("Post", ["id:integer"]),
                ("Post", ["title:unknown"]),
                ("Post", ["title:string", "title:text"]),
            ):
                with self.assertRaises(ProjectGenerationError):
                    generate_scaffold(root, model, fields)
            with self.assertRaises(ProjectGenerationError):
                parse_field_specs([])

    def test_scaffold_never_overwrites_existing_generated_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "app"
            create_project("blog_app", root)
            generate_scaffold(root, "Post", ["title:string"])
            model_path = root / "app/models/post.sambu"
            before = model_path.read_text(encoding="utf-8")
            with self.assertRaises(ProjectGenerationError):
                generate_scaffold(root, "Post", ["title:text"])
            self.assertEqual(model_path.read_text(encoding="utf-8"), before)

    def test_cli_new_and_generate_scaffold_commands(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "api_app"
            self.assertEqual(main(["new", "api_app", "--path", str(root)]), 0)
            self.assertEqual(
                main(["generate", "scaffold", "Post", "title:string", "--path", str(root)]),
                0,
            )
            self.assertTrue((root / "db/migrate/0001_create_posts.sambu").is_file())


if __name__ == "__main__":
    unittest.main()
