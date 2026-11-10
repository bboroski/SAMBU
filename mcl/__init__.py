"""Canonical public namespace for the Multidomain Computation Language (MCL).

The historical sambu implementation package remains available as a
source-compatibility layer while projects migrate to the mcl namespace.
"""
from sambu import *  # noqa: F401,F403
from sambu import __version__

from sambu.lexer import SambuSyntaxError as MclSyntaxError
from sambu.runtime import SambuRuntimeError as MclRuntimeError
from sambu.machine import SambuMachine as MclMachine

# Canonical, responsibility-oriented names for legacy domain components.
try:
    from sambu.judo import JudoArchitecture as ArchitectureGraph
    from sambu.judo import JudoPolicy as ArchitecturePolicy
    from sambu.aikido import Aikido as InferenceBudgetRouter
    from sambu.aikido import AikidoHub as InferenceRouteHub
    from sambu.jiu_jitsu import JiuJitsu as AccessComposition
    from sambu.jiu_jitsu import JiuJitsuApp as AccessControlledApplication
    from sambu.anatidae import AnatidaeProfile as BiologicalProfile
except ImportError:
    # Keep the minimal language interface importable if optional domain modules
    # are unavailable in a reduced installation.
    pass
