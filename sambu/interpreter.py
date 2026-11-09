"""Public execution API."""
from __future__ import annotations

from collections.abc import Callable

from .parser import parse
from .runtime import Interpreter


def execute(source: str, output: Callable[[str], None] = print) -> object:
    """Parse and execute a SAMBU source string."""
    return Interpreter(output=output).run(parse(source))
