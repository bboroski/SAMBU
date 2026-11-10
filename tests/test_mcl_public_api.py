from mcl import MclMachine, MclRuntimeError, MclSyntaxError
from mcl.access import AccessComposition
from mcl.architecture import ArchitectureGraph
from mcl.biology import BiologicalProfile
from mcl.inference import InferenceBudgetRouter


def test_canonical_mcl_names_resolve_to_implemented_components():
    from sambu.machine import SambuMachine
    from sambu.runtime import SambuRuntimeError
    from sambu.lexer import SambuSyntaxError
    from sambu.judo import JudoArchitecture
    from sambu.aikido import Aikido
    from sambu.jiu_jitsu import JiuJitsu
    from sambu.anatidae import AnatidaeProfile

    assert MclMachine is SambuMachine
    assert MclRuntimeError is SambuRuntimeError
    assert MclSyntaxError is SambuSyntaxError
    assert ArchitectureGraph is JudoArchitecture
    assert InferenceBudgetRouter is Aikido
    assert AccessComposition is JiuJitsu
    assert BiologicalProfile is AnatidaeProfile
