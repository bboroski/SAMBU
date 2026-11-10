"""Canonical public namespace for the Multidomain Computation Language (MCL).

The historical sambu implementation package remains available as a
source-compatibility layer while projects migrate to the mcl namespace.
"""
from sambu import *  # noqa: F401,F403
from sambu import __version__

from sambu.lexer import MclSyntaxError
from sambu.runtime import MclRuntimeError
from sambu.machine import MclMachine

# Canonical, responsibility-oriented names for legacy domain components.
try:
    from sambu.judo import ArchitectureGraph
    from sambu.judo import ArchitecturePolicy
    from sambu.aikido import InferenceBudgetRouter
    from sambu.aikido import InferenceRouteHub
    from sambu.jiu_jitsu import AccessComposition
    from sambu.jiu_jitsu import AccessControlledApplication
    from sambu.anatidae import BiologicalProfile
except ImportError:
    # Keep the minimal language interface importable if optional domain modules
    # are unavailable in a reduced installation.
    pass
