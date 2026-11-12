"""Satan cross-repository coordination primitives for SAMBU.

The package provides signed event envelopes, a durable Nexus ledger,
dependency impact analysis, and a policy-gated change pipeline.
It does not execute generated code or merge/deploy changes.
"""
from .mesh import MeshEnvelope, MeshError, create_envelope, forward_envelope, verify_envelope
from .nexus import Nexus
from .dependencies import DependencyGraph, PythonContractIndex
from .autonomy import ChangePipeline, ChangeProposal, PipelineDecision

__all__ = [
    "MeshEnvelope", "MeshError", "create_envelope", "forward_envelope",
    "verify_envelope", "Nexus", "DependencyGraph", "PythonContractIndex",
    "ChangePipeline", "ChangeProposal", "PipelineDecision",
]
