"""Engine-neutral payload contracts and capability profiles for voxel adapters."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Mapping

from .core import SparseVoxelGrid


@dataclass(frozen=True, slots=True)
class EngineProfile:
    identifier: str
    engine_family: str
    integration_surface: str
    gpu_compute_surface: str
    recommended_transfer: str
    notes: str


ENGINE_PROFILES: dict[str, EngineProfile] = {
    "unity": EngineProfile(
        "unity", "Unity", "Mesh / MeshData / MeshFilter",
        "ComputeShader + ComputeBuffer / GraphicsBuffer",
        "C# bridge + mesh arrays + optional compute buffers",
        "Use chunk-local meshes and upload changed chunks only.",
    ),
    "unreal": EngineProfile(
        "unreal", "Unreal Engine", "UProceduralMeshComponent / Runtime Mesh Component",
        "Render Dependency Graph (RDG) + RHI compute",
        "C++ component or plugin + procedural mesh sections",
        "ProceduralMeshComponent is documented as experimental; pin engine versions.",
    ),
    "godot": EngineProfile(
        "godot", "Godot", "ArrayMesh / SurfaceTool / MeshInstance3D",
        "RenderingDevice storage buffers + compute pipelines",
        "GDScript or GDExtension + ArrayMesh surfaces",
        "RenderingDevice is not available in headless or Compatibility rendering mode.",
    ),
    "bevy": EngineProfile(
        "bevy", "Bevy", "Assets<Mesh> + Mesh3d",
        "RenderDevice / RenderQueue + wgpu compute pipelines",
        "Rust plugin + Mesh attributes and indices",
        "Bevy APIs evolve; pin a tested Bevy release in the host Cargo.toml.",
    ),
    "o3de": EngineProfile(
        "o3de", "Open 3D Engine", "Atom RPI FeatureProcessor / Mesh feature",
        "Atom RHI compute + FrameGraph",
        "C++ Gem + Atom FeatureProcessor / RPI",
        "Keep GPU resources in the renderer integration layer, not the core voxel model.",
    ),
    "generic": EngineProfile(
        "generic", "Custom engine", "JSON voxel schema / mesh arrays / MagicaVoxel VOX",
        "Host-selected Vulkan, Direct3D, Metal, OpenGL or WebGPU compute",
        "Implement the SAMBU voxel payload contract in a host adapter",
        "Use engine_payload() and the documented coordinate-frame contract.",
    ),
}


def supported_engines() -> tuple[str, ...]:
    """List engine adapters and the generic extension target."""
    return tuple(ENGINE_PROFILES)


def engine_payload(
    grid: SparseVoxelGrid,
    engine: str = "generic",
    *,
    include_surface_mesh: bool = True,
) -> dict[str, object]:
    """Serialize a portable chunk/mesh payload for a named engine bridge."""
    if engine not in ENGINE_PROFILES:
        raise ValueError(f"unsupported engine {engine!r}; choose from {', '.join(ENGINE_PROFILES)}")
    profile = ENGINE_PROFILES[engine]
    chunks = []
    for chunk in grid.iter_chunks():
        # Five bytes per cell: uint8 local x/y/z, uint16 material (little endian).
        packed = bytearray()
        for x, y, z, material in chunk.voxels:
            packed.extend((x, y, z))
            packed.append(material & 0xFF)
            packed.append((material >> 8) & 0xFF)
        chunks.append({
            "coordinate": list(chunk.coordinate),
            "chunk_size": chunk.chunk_size,
            "voxel_count": chunk.voxel_count,
            "cell_stride_bytes": 5,
            "cells_little_endian_hex": bytes(packed).hex(),
        })
    frame = {
        "origin": list(grid.frame.origin),
        "voxel_size": grid.frame.voxel_size,
        "axes": [list(row) for row in grid.frame.axes],
        "coordinate_convention": "integer cell coordinates; world = origin + voxel_size * axes * grid_position",
    }
    payload: dict[str, object] = {
        "schema": "sambu.engine_voxels.v1",
        "engine": asdict(profile),
        "frame": frame,
        "chunk_size": grid.chunk_size,
        "voxel_count": grid.voxel_count,
        "chunks": chunks,
        "index_format": "uint32",
        "vertex_space": "voxel-grid-local",
    }
    if include_surface_mesh:
        mesh = grid.build_surface_mesh()
        payload["surface_mesh"] = {
            "vertices": [list(vertex) for vertex in mesh.vertices],
            "normals": [list(normal) for normal in mesh.normals],
            "indices": list(mesh.indices),
            "face_materials": list(mesh.face_materials),
            "triangle_count": mesh.triangle_count,
        }
    return payload


__all__ = ["EngineProfile", "ENGINE_PROFILES", "supported_engines", "engine_payload"]
