"""SAMBU language public API."""

from ._version import __version__

from .apple_devices import (  # noqa: F401
    AppleDevice, AppleDeviceToolkit, AppleDiagnosticReport, Diagnostic,
    HardwareTest, HardwareTestReport, ToolStatus,
)
from .i18n import LanguageManager, normalize_language, translate  # noqa: F401

from .ast import (  # noqa: F401
    ArrayExpr, BinaryExpr, CallExpr, ClassStatement, ExpressionStatement,
    FieldExpr, ForStatement, FunctionStatement, IfStatement, IndexExpr,
    InterfaceStatement, LetStatement, LiteralExpr, NameExpr, Program, ReturnStatement,
    SetFieldStatement, TraitStatement, UnaryExpr,
)
from .interpreter import execute  # noqa: F401
from .lexer import SambuSyntaxError, Token, tokenize  # noqa: F401
from .parser import parse, parse_ast  # noqa: F401
from .source import SourcePosition, SourceSpan  # noqa: F401

from .judo import (  # noqa: F401
    ArchitectureMetrics, ArchitectureReport, Component, Connection, Finding,
    Judo, JudoArchitecture, JudoPolicy,
)
from .aikido import (  # noqa: F401
    Aikido, AikidoError, AikidoHub, BudgetExceeded, InferenceExhausted,
    InferenceRequest, InferenceResult, ModelProfile, NoModelAvailable,
)
from .jiu_jitsu import (  # noqa: F401
    AccessDenied, DualActionButton, JiuJitsu, JiuJitsuApp, JiuJitsuError, ModalDefinition,
    ModalManager, Role, RoleManager, ViewController, ViewDefinition,
    ViewNode, ViewSnapshot,
)

from .filtering import (  # noqa: F401
    FilterConfigurationError, FilterEvaluation, FilterRule,
    FilteringEngine, RuleEvaluation,
)

from .chunking import ChunkManifest, chunked, plan_chunks  # noqa: F401
from .patching import PatchConflict, PatchReceipt, PatchSet, TextPatch  # noqa: F401
from .trust import (  # noqa: F401
    ArtifactVerification, PortfolioArtifact, PortfolioVerification,
    PortfolioVerifier, trust_dig,
)

from .anatidae import AnatidaeProfile  # noqa: F401
from .voxels import (  # noqa: F401
    ENGINE_PROFILES, EngineProfile, FramePlan, GraphEdge, OctreeNode,
    SparseLaplacian, SparseVoxelGrid, SparseVoxelOctree,
    SpectralSparsifierResult, SpielmanSpectralSparsifier, SurfaceMesh,
    VoxelChunk, VoxelFrame, VoxelGraph, VoxelHit, decode_morton3,
    encode_morton3, engine_payload, graph_from_voxels, plan_frame_updates,
    supported_engines,
)

from .concurrency import (  # noqa: F401
    Actor, ActorSnapshot, ActorStoppedError, AuthorizationError,
    ChannelEmptyError, ChannelFullError, ConcurrencyError, DualAuthorizationGate,
    FiberHandle, FiberRunReport, FiberScheduler, MailboxFullError,
    ModuleMetadata, ResourceScope, ResourceScopeError, SchedulerLimitError,
    SleepTicks, Supervisor, SupervisorEvent, TypedChannel, YieldNow,
    sleep_ticks, yield_now,
)

from .autonomy import (  # noqa: F401
    AutonomyError, AutonomyPolicy, CapabilityDenied, ChangeEvaluation,
    ChangeProposal, ExecutionPlan, ExperimentLedger, ExperimentRecord,
    LedgerFull, ResourceBudget, RiskTier, SambuMachine, TaskManifest,
    fingerprint,
)

from .continuity import (  # noqa: F401
    ContinuityError, CycleCapacityError, CycleController, CycleEvent, CyclePhase,
    SignalCapacityError, SignalDecision, SignalDisposition, SignalEnvelope,
    SignalGuard, TransitionDenied,
)

from .articulatory import (  # noqa: F401
    ACTIVE_WORDS, ARTICULATORY_WORDS, BUILTIN_ALIASES, KEYWORD_ALIASES,
    RESERVED_WORDS, ArticulatoryWord, filter_articulatory_words,
    lookup_articulatory_word,
)


from .nun import (  # noqa: F401
    BoundaryProfile, GenesisFinding, GenesisManifest, GenesisReport,
    GenesisSpec, NunEngine, NunError, PrimordialState,
)

from .creative_metadata import (  # noqa: F401
    CLUSTER_BY_ID, CREATIVE_CLUSTERS, ONTOLOGY_VERSION, SAFETY_FLAGS,
    CreativeCluster, CreativeMetadata, CreativeMetadataError,
    validate_metadata_document,
)

from .creative_learning import (  # noqa: F401
    CREATIVE_PREFERENCE_FEATURES, CreativeLearningError, CreativeLearningProfile,
)
