# Sparse voxel systems

SAMBU 0.11 provides a sparse voxel core, a language-level interface, CPU reference algorithms, spectral graph tools, portable data contracts and starter engine bridges.

## Quick SAMBU example

~~~sambu
let world = voxel_grid(16, 100000)
voxel_set(world, 0, 0, 0, 2)
voxel_set(world, 1, 0, 0, 2)
voxel_set(world, 2, 0, 0, 3)
let mesh = voxel_mesh(world)
let octree = voxel_octree(world)
let graph = voxel_spectral_profile(world)
let solution = voxel_solve_field(graph, [1, 0, -1])
print(voxel_count(world))
print(mesh.face_count)
print(octree.node_count)
print(solution.values[0])
~~~

Run the complete example with: sambu examples/voxel_world.sambu

## Core data model

SparseVoxelGrid stores occupied cells only. Each cell uses a signed 32-bit integer coordinate and a material ID from 1 through 65535. The default maximum grid size is 2,000,000 occupied cells; the chunk size is configurable from 1 to 256.

VoxelFrame maps cell coordinates to world coordinates with an origin, a uniform voxel scale and an invertible 3×3 basis. This supports translation, rotation, axis permutation and general invertible affine bases. Non-finite and singular frames are rejected.

encode_morton3 and decode_morton3 use a 63-bit Morton key with signed 21-bit coordinates per axis. Grid coordinates outside that key range remain valid in the sparse grid; Morton-ordered iteration places those exceptional coordinates in a deterministic fallback order.

## Frame budgeting and mesh building

- iter_chunks() groups occupied cells by integer chunk coordinate and emits deterministic local coordinates.
- Every insertion or removal marks its chunk dirty.
- plan_frame_updates() prioritizes the nearest dirty chunks up to a caller-specified per-frame budget. It computes a plan only; the host acknowledges uploads only after they actually complete.
- build_surface_mesh() removes faces shared by adjacent occupied voxels and emits grid-local vertices, normals, indices and per-face materials.
- raycast() uses Amanatides–Woo 3D grid traversal in the configured voxel frame.
- SparseVoxelOctree recursively stores occupied octants and represents empty regions through absent child bits.

The CPU mesh builder is a reference exposed-face mesher. It is not yet a greedy mesher, transvoxel LOD implementation, dual contouring, or a GPU geometry emitter. It also enforces a default one-million-visible-face allocation ceiling; callers can lower or raise the explicit max_faces bound up to the configured hard limit. Exceeding the ceiling fails before mesh arrays are allocated.

## Spielman spectral systems

A voxel graph is built from occupied cells and six-neighbour adjacency. SparseLaplacian stores the graph Laplacian in CSR form and provides matrix-vector multiplication, Jacobi-preconditioned conjugate-gradient solving and effective-resistance queries.

~~~python
from sambu.voxels import SparseVoxelGrid, SparseLaplacian, graph_from_voxels

grid = SparseVoxelGrid()
for x in range(3):
    grid.set_voxel(x, 0, 0)

graph = graph_from_voxels(grid)
laplacian = SparseLaplacian(graph)
solution = laplacian.solve_vector([1.0, 0.0, -1.0])
print(solution)
~~~

SpielmanSpectralSparsifier uses edge effective resistance as a sampling signal and reweights retained edges. This is a bounded CPU reference inspired by Spielman–Srivastava spectral sparsification. It is not a full nearly-linear-time Spielman–Teng solver, a certified error bound for each random sample, or a practical GPU solution for a huge voxel world. The current exact-resistance path is limited to small graphs (512 vertices and 8,192 edges by default). For larger scenes, use a compiled sparse solver, approximate resistance sketches, multilevel graph methods or engine/GPU compute.

The graph Laplacian has a constant nullspace on each connected component. The solver therefore requires the right-hand side to sum to zero independently in every connected component and returns a zero-mean solution on each component.

## MagicaVoxel and engine interchange

SparseVoxelGrid.to_magica_vox() / from_magica_vox() provide a bounded basic MagicaVoxel VOX v150 single-model round trip. The current importer reads the first SIZE/XYZI model and material palette indices; advanced scene graphs, transforms, animation, multiple models and full material metadata are outside this basic bridge.

engine_payload(grid, engine) emits the affine world/grid frame, chunk coordinates and local occupied cells, a compact 5-byte little-endian transfer record (uint8 local x/y/z plus uint16 material), optional uint32 surface-mesh indices, grid-local vertices, normals and face materials, and the engine profile/capability notes.

The Unity bridge expands compact 5-byte records to an aligned 8-byte GPU structured-buffer representation. Do not directly reinterpret the transfer bytes as an engine-specific GPU structure without checking alignment and byte order.

## Engines

Maintained starter bridge source is provided for:

- Unity: C# Mesh/GraphicsBuffer bridge plus a compute shader. Current Unity documentation includes MeshData and compute-readable mesh buffers; a production implementation can move chunk generation into writable MeshData and Burst/Jobs.
- Unreal Engine: ProceduralMeshComponent example plus module rules. Epic marks ProceduralMeshComponent experimental; large-scale terrain should use a version-pinned renderer path such as a custom scene proxy and RDG/RHI-managed buffers.
- Godot: ArrayMesh surface bridge and RenderingDevice capability check. Compute requires a RenderingDevice-based renderer; headless and Compatibility modes do not expose it.
- Bevy 0.20.1: Rust mesh bridge. Pin the exact Bevy release in the host project; Bevy APIs evolve.
- Open 3D Engine: renderer-neutral mesh data contract intended for an Atom RPI FeatureProcessor and RHI-managed resources owned by a host Gem.

Additional payload-only profiles exist for Flax, Stride, UNIGINE, OGRE, Source 2, CRYENGINE, Roblox Studio, Babylon.js, Three.js, PlayCanvas, Cocos Creator, Defold, jMonkeyEngine and Panda3D. Their SDK-specific plugins are not included. No repository can honestly claim a verified native integration for every engine/version/platform combination.

See engine adapter source and notes at ../engine_adapters/README.md.

## GPU compute stages

The included GLSL and Unity HLSL visibility kernels calculate a six-bit exposed-face mask for every occupied voxel. Unity's C# DispatchVisibleFaceMasks() and DispatchCompactVoxelMesher() helpers orchestrate the passes. Unity also has engine_adapters/unity/SambuCompactVoxelMesh.compute, a three-dispatch GPU pipeline:
1. CountVisibleFaces performs group-local scan and stores per-group face totals.
2. ScanGroupOffsets computes exclusive offsets and writes indexed-draw arguments.
3. EmitVisibleFaces writes compact grid-local vertices, normals, uint32 indices and material IDs.

The Unity pass emits two triangles per visible voxel face. It is not a greedy mesher and does not merge adjacent coplanar faces. Output capacity must be bounded/allocated for up to six visible faces per input voxel (or work must be split into smaller chunks). Vulkan/GLSL consumers can use the first visibility pass and port the documented count/scan/emit stages to their compute pipeline; a full shared Vulkan emission kernel is not yet supplied.

Do not read back every voxel or face mask to the CPU each frame. Keep chunk data resident on the GPU where the renderer permits it, and transfer only changed chunk payloads.

## Benchmarks

Run the reproducible CPU reference benchmark:

~~~bash
python benchmarks/benchmark_voxels.py --size 16 --repeats 3
python benchmarks/benchmark_voxels.py --size 6 --include-spectral --json
~~~

The harness reports actual wall-clock measurements and workload counts for the host machine. It is not a GPU benchmark; compare identical sizes, chunk settings, hardware and Python builds. The optional graph-solver run is capped at a small grid.

## Security and safety limits

Voxel JSON input is bounded by the caller's max_voxels argument. Coordinates, material IDs, chunk sizes, traversal step counts, and graph size have explicit validation. The package does not load native engine binaries, execute shaders itself, perform GPU work, contact a game engine over a network, or write project assets. Those operations remain host integration responsibilities.
