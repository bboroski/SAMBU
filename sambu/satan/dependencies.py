"""Language-aware dependency impact primitives (Python AST adapter first)."""
from __future__ import annotations

import ast
from collections import defaultdict, deque
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PythonContract:
    module: str
    definitions: tuple[str, ...]
    imports: tuple[str, ...]


class PythonContractIndex:
    """Extract module-level Python names and imports without executing source."""

    def parse(self, module: str, source: str) -> PythonContract:
        if not module or len(module) > 512:
            raise ValueError("module must be 1..512 characters")
        if not isinstance(source, str):
            raise TypeError("source must be text")
        tree = ast.parse(source, filename=module)
        definitions: set[str] = set()
        imports: set[str] = set()
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                definitions.add(node.name)
            elif isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module)
        return PythonContract(module, tuple(sorted(definitions)), tuple(sorted(imports)))


class DependencyGraph:
    """Directed graph where an edge A -> B means B consumes A."""

    def __init__(self) -> None:
        self._consumers: dict[str, set[str]] = defaultdict(set)
        self._contracts: dict[str, PythonContract] = {}

    def add_dependency(self, provider: str, consumer: str) -> None:
        if not provider or not consumer or provider == consumer:
            raise ValueError("provider and consumer must be distinct non-empty names")
        self._consumers[provider].add(consumer)

    def index_python(self, contract: PythonContract) -> None:
        self._contracts[contract.module] = contract
        for imported in contract.imports:
            self.add_dependency(imported, contract.module)

    def affected(self, changed_provider: str, *, include_self: bool = True) -> tuple[str, ...]:
        visited = {changed_provider} if include_self else set()
        queue = deque([changed_provider])
        while queue:
            current = queue.popleft()
            for consumer in sorted(self._consumers.get(current, ())):
                if consumer not in visited:
                    visited.add(consumer)
                    queue.append(consumer)
        return tuple(sorted(visited))

    def changed_contract(self, module: str, new_source: str) -> dict:
        old = self._contracts.get(module)
        new = PythonContractIndex().parse(module, new_source)
        old_names = set(old.definitions) if old else set()
        new_names = set(new.definitions)
        return {
            "module": module,
            "added": tuple(sorted(new_names - old_names)),
            "removed": tuple(sorted(old_names - new_names)),
            "affected": self.affected(module),
            "review_required": bool(old_names - new_names),
        }
