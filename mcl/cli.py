"""Canonical MCL command entry points."""
from __future__ import annotations

from typing import Sequence

from sambu.cli import main as _language_main
from sambu_studio.cli import main as _studio_main
from sambu_ide.app import main as _ide_main


def main(argv: Sequence[str] | None = None) -> int:
    """Run the MCL language command line."""
    return _language_main(None if argv is None else list(argv))


def studio_main() -> int:
    """Run the MCL static XML inspection utility."""
    return _studio_main()


def ide_main() -> None:
    """Launch the MCL desktop editor."""
    _ide_main()
