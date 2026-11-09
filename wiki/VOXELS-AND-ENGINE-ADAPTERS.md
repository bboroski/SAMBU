# Sparse voxels and game-engine adapters

SAMBU 0.11 includes a sparse voxel core, language-level built-ins, CPU reference algorithms, spectral graph tools, data interchange and starter engine bridges.

## Quick example

```sambu
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
```

Run the repository example with `sambu examples/voxel_world.sambu`.

## Sparse grid

The core stores occupied cells rather than allocating a dense 3D array.

Documented properties:
- signed 32-bit integer cell coordinates;
- material identifiers from 1 to 65,535;
- configurable chunk size from 1 to 256;
- default occupied-cell ceiling of 2,000,000;
- deterministic chunk iteration;
- dirty-chunk tracking after insertion or removal.

## Coordinate frames and Morton order

`VoxelFrame` maps grid coordinates to world coordinates using an origin, uniform voxel scale and invertible 3×3 basis. Non-finite and singular frames are rejected.

`encode_morton3` and `decode_morton3` use a 63-bit Morton key with signed 21-bit coordinates per axis. Coordinates outside that key range can still exist in the sparse grid and use a deterministic fallback ordering for Morton iteration.

## Meshing and ray traversal

- `build_surface_mesh()` removes faces shared by adjacent occupied cells and emits vertices, normals, indices and face materials.
- `raycast()` uses Amanatides–Woo 3D grid traversal in the configured frame.
- `SparseVoxelOctree` stores occupied octants and represents empty regions with absent child bits.
- `plan_frame_updates()` prioritizes dirty chunks up to a caller-defined per-frame budget.

The CPU mesher is a reference exposed-face mesher, not greedy meshing, transvoxel LOD, dual contouring or a complete GPU geometry pipeline. The frame planner calculates a plan; the host acknowledges uploads only after they actually complete.

## Spectral graph tools

The voxel graph is constructed from occupied cells and six-neighbour adjacency. The sparse Laplacian uses CSR storage and supports:
- matrix-vector multiplication;
- Jacobi-preconditioned conjugate-gradient solving;
- effective-resistance queries;
- a bounded Spielman–Srivastava-style sparsifier.

The exact-resistance path is intentionally limited to small graphs by default. The Laplacian has a constant nullspace on each connected component, so the solver requires the right-hand side to sum to zero within each component and returns a zero-mean solution per component.

This is a bounded CPU reference, not a certified large-scale nearly-linear solver or a production GPU spectral engine.

## Interchange

The core supports a basic MagicaVoxel VOX v150 single-model round trip and a renderer-neutral engine payload.

The compact voxel transfer record is five bytes:
- local x, y and z coordinates as uint8;
- material ID as uint16;
- little-endian encoding.

The payload can also carry the coordinate frame, chunk coordinates, surface vertices, normals, triangle indices and material IDs. Engine-specific GPU buffers may require padding and alignment; the Unity bridge expands transfer records to an aligned eight-byte representation.

## Starter engine bridges

| Engine | Starter source path | Notes |
|---|---|---|
| Unity | `engine_adapters/unity/` | C# bridge and HLSL compute path |
| Unreal Engine | `engine_adapters/unreal/` | ProceduralMeshComponent example; host-side production renderer work remains |
| Godot | `engine_adapters/godot/` | ArrayMesh bridge and RenderingDevice capability check |
| Bevy 0.20.1 | `engine_adapters/bevy/` | Rust mesh bridge; host must pin Bevy |
| Open 3D Engine | `engine_adapters/o3de/` | Renderer-neutral mesh data contract for Atom integration |

Other registered engine names may only have generic payload profiles. A profile is not proof that an SDK-specific plugin is implemented or tested.

## Scaling guidance

1. Store occupied cells only.
2. Partition the world into bounded chunks.
3. Track changed chunks and rebuild only dirty regions.
4. Bound uploads per frame.
5. Use the CPU algorithm as a reference path.
6. Use host-specific compute pipelines only after validating buffer layout, resource lifetime and platform support.
7. Add greedy meshing, LOD, asynchronous uploads and GPU-driven rendering in the host engine when required.

## Further reading

- [Detailed voxel guide](../docs/VOXELS.md)
- [Engine adapter matrix](../engine_adapters/README.md)
