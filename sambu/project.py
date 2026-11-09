"""Convention-first starter generator for the Python-hosted SAMBU CLI."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable


class ProjectGenerationError(ValueError):
    """A project or scaffold could not be created safely."""


_PROJECT = re.compile(r"^[a-z][a-z0-9_]{0,47}$")
_MODEL = re.compile(r"^[A-Z][A-Za-z0-9]{0,47}$")
_FIELD = re.compile(r"^[a-z][a-z0-9_]{0,47}$")
_TYPES = {"string", "text", "integer", "float", "decimal", "boolean", "datetime", "date", "json"}
_RESERVED = {"id", "created_at", "updated_at", "deleted_at"}


@dataclass(frozen=True, slots=True)
class FieldSpec:
    name: str
    type_name: str


def _snake(name: str) -> str:
    first = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", first).lower()


def _plural(word: str) -> str:
    if len(word) > 1 and word.endswith("y") and word[-2] not in "aeiou":
        return word[:-1] + "ies"
    return word + "es" if word.endswith(("s", "x", "z", "ch", "sh")) else word + "s"


def parse_field_specs(values: Iterable[str]) -> tuple[FieldSpec, ...]:
    result: list[FieldSpec] = []
    seen: set[str] = set()
    for value in values:
        if not isinstance(value, str) or value.count(":") != 1:
            raise ProjectGenerationError(f"invalid field {value!r}; expected name:type")
        name, type_name = value.split(":", 1)
        if not _FIELD.fullmatch(name):
            raise ProjectGenerationError(f"invalid field name {name!r}")
        if name in _RESERVED:
            raise ProjectGenerationError(f"field name {name!r} is reserved")
        if name in seen:
            raise ProjectGenerationError(f"duplicate field {name!r}")
        if type_name not in _TYPES:
            raise ProjectGenerationError(f"unsupported field type {type_name!r}")
        seen.add(name)
        result.append(FieldSpec(name, type_name))
    if not result:
        raise ProjectGenerationError("a scaffold needs at least one field")
    return tuple(result)


def _write(root: Path, files: dict[str, str], *, allow_populated: bool) -> list[Path]:
    """Write a generated file set without following links or overwriting files.

    Project creation requires a missing or empty destination. Scaffold generation
    is allowed inside an existing project, but every generated target must be new.
    """
    root = root.expanduser()
    if root.is_symlink():
        raise ProjectGenerationError(f"destination {root} must not be a symbolic link")
    if root.exists():
        if not root.is_dir():
            raise ProjectGenerationError(f"destination {root} is not a directory")
        if not allow_populated and any(root.iterdir()):
            raise ProjectGenerationError(f"destination {root} is not empty")
    else:
        if allow_populated:
            raise ProjectGenerationError(f"destination {root} must be an existing SAMBU project")
        root.mkdir(parents=True, exist_ok=True)

    targets: list[tuple[Path, str]] = []
    for relative, content in files.items():
        rel = Path(relative)
        if rel.is_absolute() or ".." in rel.parts:
            raise ProjectGenerationError(f"unsafe generated path {relative!r}")
        target = root / rel
        if target.is_symlink():
            raise ProjectGenerationError(f"refusing to write through symbolic link {target}")
        parent = root
        for part in rel.parts[:-1]:
            parent = parent / part
            if parent.is_symlink():
                raise ProjectGenerationError(f"refusing to write through symbolic link {parent}")
        if target.exists():
            raise ProjectGenerationError(f"refusing to overwrite {target}")
        targets.append((target, content))

    created: list[Path] = []
    try:
        for target, content in targets:
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("x", encoding="utf-8", newline="\n") as handle:
                handle.write(content)
            created.append(target)
    except OSError as exc:
        for path in reversed(created):
            try:
                path.unlink()
            except OSError:
                pass
        raise ProjectGenerationError(f"could not write project files: {exc}") from exc
    return created


def create_project(name: str, destination: Path | str | None = None) -> list[Path]:
    if not isinstance(name, str) or not _PROJECT.fullmatch(name):
        raise ProjectGenerationError("name must be lowercase snake_case (letters, digits and underscores)")
    root = Path(destination) if destination is not None else Path(name)
    files = {
        "Sambu.toml": f'''[project]
name = "{name}"
version = "0.1.0"
language_edition = "0.11"

[conventions]
models = "app/models"
controllers = "app/controllers"
views = "app/views"
routes = "config/routes.sambu"
migrations = "db/migrate"

[server]
host = "127.0.0.1"
port = 3000
# Reserved settings: the HTTP runtime is not implemented in 0.11.
''',
        "README.md": f'''# {name}

Convention-based SAMBU application starter.

Run the currently supported language entry point:

~~~bash
sambu src/main.sambu
~~~

The MVC, routing, ORM, templates and migration files are contracts for the
planned SAMBU web runtime. They are not an active Rails-compatible framework.
The generator itself uses only the Python standard library in the current
Python-hosted CLI; it is not self-hosted yet.
''',
        ".gitignore": "__pycache__/\n*.py[cod]\n.sambu-cache/\n.env\n.venv/\n",
        "src/main.sambu": f'''fn main() {{
  print("Welcome to SAMBU application: {name}")
}}

main()
''',
        "config/routes.sambu": '''# Planned SAMBU route DSL. This file is not executable in language version 0.11.
# root "welcome#index"
# resources posts
''',
        "app/models/application_record.sambu": "# Planned model base; persistence is not implemented yet.\n",
        "app/controllers/application_controller.sambu": "# Planned request lifecycle; HTTP runtime is not implemented yet.\n",
        "app/views/layouts/application.html": '''<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>SAMBU</title></head>
<body><main><!-- rendered application view --></main></body>
</html>
''',
        "db/migrate/README.md": "Migration files are specifications until a database adapter and transactional runner exist.\n",
        "test/README.md": "Generated tests are starters; a framework-aware web test client is planned.\n",
    }
    return _write(root, files, allow_populated=False)


def generate_scaffold(
    project_root: Path | str,
    model_name: str,
    field_declarations: Iterable[str],
) -> list[Path]:
    root = Path(project_root).expanduser()
    if not root.is_dir() or not (root / "Sambu.toml").is_file():
        raise ProjectGenerationError(f"{root} is not a SAMBU project (Sambu.toml missing)")
    if not isinstance(model_name, str) or not _MODEL.fullmatch(model_name):
        raise ProjectGenerationError("model name must be PascalCase, e.g. Post or BodyAcceptance")

    model = _snake(model_name)
    table = _plural(model)
    fields = parse_field_specs(field_declarations)
    migration_dir = root / "db" / "migrate"
    numbers = [
        int(match.group(1))
        for path in migration_dir.glob("*.sambu") if migration_dir.exists()
        if (match := re.match(r"^(\d+)_", path.name))
    ]
    next_number = max(numbers, default=0) + 1
    if next_number > 9999:
        raise ProjectGenerationError("migration sequence exhausted (maximum 9999)")
    names = [field.name for field in fields]
    names_literal = "[" + ", ".join(repr(name) for name in names) + "]"
    field_comments = "\n".join(f"# column {field.name}: {field.type_name}" for field in fields)
    migration_comments = "\n".join(f"#   {field.name}: {field.type_name}" for field in fields)
    migration = f"{next_number:04d}_create_{table}.sambu"
    files = {
        f"app/models/{model}.sambu": (
            f"# Model contract for {model_name}; ORM/persistence are planned.\n"
            f"# Convention table: {table}\n{field_comments}\n"
            f"fn {model}_field_names() {{ return {names_literal} }}\n"
        ),
        f"app/controllers/{table}_controller.sambu": (
            f"# Controller action starters; HTTP lifecycle is planned.\n"
            f"fn {table}_index() {{ return [] }}\n"
            f"fn {table}_new() {{ return [] }}\n"
        ),
        f"app/views/{table}/index.html": f"<!-- Generated index for {model_name}. -->\n<h1>{table.replace('_', ' ').title()}</h1>\n",
        f"app/views/{table}/show.html": f"<!-- Generated show view for {model_name}. -->\n<h1>{model_name}</h1>\n",
        f"app/views/{table}/new.html": "<!-- Generated form starter; validation and CSRF helpers are planned. -->\n",
        f"db/migrate/{migration}": (
            f"# Migration specification for table {table}; not executable yet.\n"
            f"# column id: integer primary_key\n{migration_comments}\n"
            "# column created_at: datetime\n# column updated_at: datetime\n"
        ),
        f"test/{table}.sambu": (
            f"# Executable starter, not a framework-aware web test yet.\n"
            f"fn expected_{model}_fields() {{ return {names_literal} }}\n"
            f"print(expected_{model}_fields())\n"
        ),
        f"config/routes/{table}.sambu": (
            f"# Planned resource route declaration for {table}.\n"
            f"# resources {table}\n"
            "# Actions: index, show, new, create, edit, update, destroy.\n"
        ),
    }
    return _write(root, files, allow_populated=True)
