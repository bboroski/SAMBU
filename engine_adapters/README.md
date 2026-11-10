<p align="center"><img src="../assets/duck-ui/duck-mark.svg" alt="SAMBU duck mark" width="88" /></p>
<p align="center"><strong>SAMBU · ENGINE ADAPTERS</strong></p>
<p align="center"><em>Sparse voxel engine bridge contracts</em></p>
<p align="center"><a href="../README.md">Project overview</a> · <a href="../README.en.md">English overview</a> · <a href="../README.ru.md">Russian overview</a></p>
<hr />

# SAMBU voxel engine adapters

SAMBU 0.11 ships a renderer-neutral sparse voxel model and starter bridges for five major engine families. These are integration source files, not prebuilt engine plugins: each engine SDK must be installed in the host project, and the bridge must be compiled there. Maintained starter source bridges target five major engine families; the additional registered profiles describe the common payload contract only.

| Engine | Bridge | Geometry path | Compute path |
|---|---|---|---|
| Unity | unity/SambuVoxelBridge.cs | Mesh / MeshFilter | ComputeShader + GraphicsBuffer |
| Unreal Engine | unreal/SambuVoxelBridge.h/.cpp | UProceduralMeshComponent | Host RDG / RHI compute shader |
| Godot | godot/SambuVoxelBridge.gd | ArrayMesh / MeshInstance3D | RenderingDevice |
| Bevy 0.20.1 | bevy/ Rust crate | Assets<Mesh> / Mesh3d | Render-world wgpu pipeline |
| Open 3D Engine | o3de/SambuVoxelMeshData.h | Atom RPI FeatureProcessor | Atom RHI / FrameGraph |
| Flax, Stride, UNIGINE, OGRE, Source 2 | Generic payload profiles | Host-specific renderer integration | Host-selected compute API |
| CRYENGINE, Roblox Studio, Babylon.js, Three.js, PlayCanvas, Cocos Creator, Defold, jMonkeyEngine, Panda3D | Generic payload profiles | Host-specific renderer integration | Host-selected compute API |

An unlisted engine can consume engine_payload(grid, "generic"), the JSON voxel schema, triangle arrays, or MagicaVoxel .vox interchange. Generic is an extension contract, not an assertion that every engine has already been integrated.

## Shared payload contract

engine_payload(grid, engine) exports:
- a world/grid coordinate frame;
- chunk coordinates;
- 5-byte little-endian voxel records: local x/y/z as uint8, material as uint16;
- uint32 triangle indices, grid-local vertices, normals and per-face material IDs.

The C# bridge expands 5-byte transfer records to an 8-byte structured GPU record. Its DispatchVisibleFaceMasks() helper runs the Unity visibility pass, and DispatchCompactVoxelMesher() follows with count, offset scan and mesh emission. GPU layouts must obey target API alignment; do not reinterpret transfer bytes as an arbitrary C++ or HLSL struct.

## Runtime strategy

1. Store only occupied cells; split the world into bounded chunks.
2. Sort chunks/cells spatially (Morton/Z-order) for locality.
3. Rebuild only dirty chunks and schedule bounded uploads per frame with plan_frame_updates.
4. Cull internal faces on CPU or use the supplied compute kernels to build six-bit exposed-face masks.
5. In Unity, dispatch count -> group-offset scan -> face emission; use the GPU-produced indexed-draw arguments and avoid synchronous per-frame readback. For other engines, port this three-stage pipeline to the host compute API.
6. For large scenes, add greedy meshing, LOD, async upload and GPU-driven indirect draws in the host engine.
6. Keep physics/collision meshes at a lower update rate and resolution than render geometry.

The GLSL kernel marks exposed faces. Unity additionally includes a three-dispatch HLSL path: per-group visible-face counts, a group-offset prefix scan, then compact vertex/index/material emission with indexed-draw arguments. This is a simple face mesher, not greedy meshing; allocate output capacity for up to six visible faces per voxel (or use a bounded chunk budget). The CPU build_surface_mesh() remains the reference face-culling path. It enforces a max_faces allocation ceiling; large scenes should be processed chunk by chunk or through the Unity GPU path.

## Engine notes

### Unity

Enable compute-shader support on the target platform and check SystemInfo.supportsComputeShaders. Upload only dirty chunks. The bridge uses the public Mesh API; for very large batches, replace it with version-specific MeshData writable mesh data and a Burst/job pipeline. GraphicsBuffer uses an aligned 8-byte record rather than the compact 5-byte wire representation.

### Unreal Engine

Enable the Procedural Mesh Component plugin and add its module to the consuming Build.cs. The public UProceduralMeshComponent API is useful for a bridge prototype, but Epic currently documents this component as experimental. For production-scale terrain, use a custom scene proxy / RDG-managed buffers and pin integration to the project Unreal version.

### Godot

Attach SambuVoxelBridge.gd to a node and assign a MeshInstance3D. RenderingDevice exposes compute pipelines and storage buffers, but it is unavailable in headless mode and with the Compatibility renderer. Keep the CPU ArrayMesh path as a fallback.

### Bevy

Add the local crate as a Cargo dependency and pin the Bevy version with the host app. The starter mesh builder targets Bevy 0.20.1 (current profile release at repository update). For compute, implement a render-world node using the Bevy render device and queue; do not perform blocking GPU readback in the frame loop.

### Open 3D Engine

Use the C++ mesh data contract inside a Gem. The Gem should own an Atom RPI FeatureProcessor and allocate/update GPU resources through Atom RHI and the frame graph. The header intentionally stops at validated engine-neutral arrays; resource ownership and render-pass registration belong to the host O3DE project.

## Shader kernels

- shaders/sambu_visible_faces.comp: GLSL 450 compute kernel for storage-image occupancy.
- unity/SambuVisibleFaces.compute: Unity HLSL visibility-mask pass.
- unity/SambuCompactVoxelMesh.compute: Unity HLSL count/scan/emit pipeline that builds compact triangle buffers and indirect indexed-draw arguments.

These passes write one six-bit face mask per occupied cell. A second prefix-sum/compaction pass is required to allocate exact vertex/index ranges.


## Registered payload-only profiles

The Python engine registry also knows the identifiers flax, stride, unigine, ogre and source2. For those targets, engine_payload() labels the engine family and returns the same portable chunk/frame/mesh data, but there is no SDK-specific implementation in this repository yet. A named profile is not a claim of a compiled or tested native plugin.

The core cannot provide one universal native plugin for literally every game engine or SDK version: APIs, licensing, renderer backends, GPU resource lifetimes and supported platforms differ. The JSON/mesh interchange format is the stable boundary intended to make additional adapters small and testable.
