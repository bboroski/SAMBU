"""Canonical MCL command entry points."""
from __future__ import annotations

from typing import Sequence

from sambu.cli import main as _language_main


def main(argv: Sequence[str] | None = None) -> int:
    """Run the MCL language command line."""
    return _language_main(None if argv is None else list(argv))


def studio_main() -> int:
    """Run the MCL static XML inspection utility."""
    from sambu_studio.cli import main as studio_main\n\n    return studio_main()


def ide_main() -> None:
    """Launch the MCL desktop editor."""
    from sambu_ide.app import main as ide_main\n\n    ide_main()
