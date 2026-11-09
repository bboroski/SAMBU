"""SAMBU-language built-ins for the sparse voxel package.

The language layer exposes bounded, inspectable operations. GPU dispatch,
engine resource lifetime and asynchronous uploads remain responsibilities of
the consuming game-engine adapter.
"""
from __future__ import annotations

from typing import Callable

from .values import Record, number_value
from .voxels import (
    SparseLaplacian, SparseVoxelGrid, SparseVoxelOctree,
    SpielmanSpectralSparsifier, engine_payload, graph_from_voxels,
    plan_frame_updates, VoxelGraph,
)


def _integer(value: object, name: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
    return value


def _grid(value: object) -> SparseVoxelGrid:
    if isinstance(value, SparseVoxelGrid):
        return value
    if isinstance(value, Record):
        candidate = value.get("grid")
        if isinstance(candidate, SparseVoxelGrid):
            return candidate
    raise TypeError("expected a voxel grid created by voxel_grid()")


def _grid_factory(args: list[object]) -> Record:
    if len(args) > 2:
        raise TypeError("voxel_grid(chunk_size=16, max_voxels=2000000) expects at most 2 arguments")
    size = _integer(args[0], "chunk_size", 1, 256) if args else 16
    limit = _integer(args[1], "max_voxels", 1, 2_000_000) if len(args) == 2 else 2_000_000
    grid = SparseVoxelGrid(chunk_size=size, max_voxels=limit)
    return Record({"schema": "sambu.voxel_handle.v1", "grid": grid})


def _set_voxel(args: list[object]) -> Record:
    if len(args) not in {4, 5}:
        raise TypeError("voxel_set(grid, x, y, z, material=1) expects 4 or 5 arguments")
    grid = _grid(args[0])
    x, y, z = (_integer(args[i], name, -(1 << 31), (1 << 31)-1) for i, name in zip((1,2,3),("x","y","z")))
    material = _integer(args[4], "material", 1, 65535) if len(args) == 5 else 1
    grid.set_voxel(x, y, z, material)
    return Record({"updated": True, "voxel_count": grid.voxel_count, "dirty_chunks": [list(c) for c in grid.dirty_chunks]})


def _remove_voxel(args: list[object]) -> bool:
    if len(args) != 4:
        raise TypeError("voxel_remove(grid, x, y, z) expects 4 arguments")
    grid = _grid(args[0])
    x, y, z = (_integer(args[i], name, -(1 << 31), (1 << 31)-1) for i, name in zip((1,2,3),("x","y","z")))
    return grid.remove_voxel(x, y, z)


def _get_voxel(args: list[object]) -> int | None:
    if len(args) != 4:
        raise TypeError("voxel_get(grid, x, y, z) expects 4 arguments")
    grid = _grid(args[0])
    x, y, z = (_integer(args[i], name, -(1 << 31), (1 << 31)-1) for i, name in zip((1,2,3),("x","y","z")))
    return grid.get_voxel(x, y, z)


def _voxel_count(args: list[object]) -> int:
    if len(args) != 1:
        raise TypeError("voxel_count(grid) expects 1 argument")
    return _grid(args[0]).voxel_count


def _voxel_mesh(args: list[object]) -> Record:
    if len(args) != 1:
        raise TypeError("voxel_mesh(grid) expects 1 argument")
    mesh = _grid(args[0]).build_surface_mesh()
    return Record({
        "vertices": [list(v) for v in mesh.vertices],
        "normals": [list(n) for n in mesh.normals],
        "indices": list(mesh.indices),
        "face_materials": list(mesh.face_materials),
        "face_count": mesh.face_count,
        "triangle_count": mesh.triangle_count,
    })


def _voxel_chunks(args: list[object]) -> list[Record]:
    if len(args) != 1:
        raise TypeError("voxel_chunks(grid) expects 1 argument")
    return [
        Record({
            "coordinate": list(chunk.coordinate),
            "chunk_size": chunk.chunk_size,
            "voxel_count": chunk.voxel_count,
            "voxels": [list(item) for item in chunk.voxels],
        })
        for chunk in _grid(args[0]).iter_chunks()
    ]


def _frame_plan(args: list[object]) -> Record:
    if len(args) != 4:
        raise TypeError("voxel_frame_plan(frame, grid, camera_chunk, max_chunks) expects 4 arguments")
    frame = _integer(args[0], "frame", 0, (1 << 31)-1)
    grid = _grid(args[1])
    camera = args[2]
    if not isinstance(camera, list) or len(camera) != 3:
        raise TypeError("camera_chunk must be an array of three integers")
    camera_coord = tuple(_integer(camera[i], f"camera_chunk[{i}]", -(1 << 31), (1 << 31)-1) for i in range(3))
    maximum = _integer(args[3], "max_chunks", 0, 1_000_000)
    plan = plan_frame_updates(frame, grid.dirty_chunks, camera_coord, max_chunks=maximum)
    return Record({
        "frame_index": plan.frame_index,
        "selected_chunks": [list(c) for c in plan.selected_chunks],
        "deferred_chunks": [list(c) for c in plan.deferred_chunks],
        "max_chunks": plan.max_chunks,
    })


def _voxel_raycast(args: list[object]) -> Record | None:
    if len(args) not in {3,4}:
        raise TypeError("voxel_raycast(grid, origin, direction, max_distance=1000000) expects 3 or 4 arguments")
    grid = _grid(args[0])
    if not isinstance(args[1], list) or not isinstance(args[2], list):
        raise TypeError("origin and direction must be arrays of three numbers")
    max_distance = number_value(args[3], "max_distance") if len(args)==4 else 1_000_000.0
    hit = grid.raycast(tuple(args[1]), tuple(args[2]), max_distance=max_distance)
    if hit is None:
        return None
    return Record({"coordinate": list(hit.coordinate), "material": hit.material_id, "distance": hit.distance})


def _voxel_octree(args: list[object]) -> Record:
    if len(args) != 1:
        raise TypeError("voxel_octree(grid) expects 1 argument")
    tree = SparseVoxelOctree.build(_grid(args[0]))
    return Record({
        "tree": tree,
        "node_count": tree.node_count,
        "side_length": tree.side_length,
        "minimum": list(tree.minimum),
        "schema": "sambu.sparse_voxel_octree.v1",
    })


def _octree_get(args: list[object]) -> int | None:
    if len(args) != 4:
        raise TypeError("voxel_octree_get(octree, x, y, z) expects 4 arguments")
    record = args[0]
    if not isinstance(record, Record) or not isinstance(record.get("tree"), SparseVoxelOctree):
        raise TypeError("first argument must be a voxel_octree() result")
    coordinates = tuple(_integer(args[i], name, -(1 << 31), (1 << 31)-1) for i,name in zip((1,2,3),("x","y","z")))
    return record.get("tree").query(coordinates)


def _voxel_export(args: list[object]) -> str:
    if len(args) not in {1,2}:
        raise TypeError("voxel_export(grid, engine='generic') expects 1 or 2 arguments")
    engine = args[1] if len(args)==2 else "generic"
    if not isinstance(engine,str):
        raise TypeError("engine must be a string")
    payload = engine_payload(_grid(args[0]),engine,include_surface_mesh=False)
    import json
    return json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(",",":"))


def _voxel_spectral_profile(args: list[object]) -> Record:
    if len(args) != 1:
        raise TypeError("voxel_spectral_profile(grid) expects 1 argument")
    graph = graph_from_voxels(_grid(args[0]))
    laplacian = SparseLaplacian(graph)
    return Record({
        "graph": graph,
        "laplacian": laplacian,
        "vertex_count": graph.vertex_count,
        "edge_count": graph.edge_count,
        "matrix_nonzeros": laplacian.nnz,
        "connected_components": len(laplacian._components),
    })


def _voxel_solve_field(args: list[object]) -> Record:
    if len(args) != 2:
        raise TypeError("voxel_solve_field(spectral_profile, values) expects 2 arguments")
    profile, values = args
    if not isinstance(profile,Record) or not isinstance(profile.get("laplacian"),SparseLaplacian):
        raise TypeError("first argument must be a voxel_spectral_profile() result")
    if not isinstance(values,list) or len(values)!=profile.get("vertex_count"):
        raise ValueError("values must be an array with one value per graph vertex")
    solved = profile.get("laplacian").solve_vector(values)
    return Record({"values":list(solved),"vertex_count":len(solved),"solver":"jacobi_preconditioned_conjugate_gradient"})


def _voxel_sparsify(args: list[object]) -> Record:
    if len(args) not in {1,2,3}:
        raise TypeError("voxel_sparsify(spectral_profile, epsilon=0.5, seed=0) expects 1 to 3 arguments")
    profile = args[0]
    if not isinstance(profile,Record) or not isinstance(profile.get("graph"), VoxelGraph):
        raise TypeError("first argument must be a voxel_spectral_profile() result")
    epsilon = number_value(args[1],"epsilon") if len(args)>=2 else 0.5
    seed = _integer(args[2],"seed",0,(1 << 31)-1) if len(args)==3 else 0
    result = SpielmanSpectralSparsifier().sparsify(profile.get("graph"),epsilon=epsilon,seed=seed)
    return Record({
        "graph": result.graph,
        "original_edges": result.original_edges,
        "retained_edges": result.retained_edges,
        "edge_reduction": result.edge_reduction,
        "epsilon": result.epsilon,
        "failure_probability": result.failure_probability,
        "method": "spielman_srivastava_effective_resistance_sampling",
    })


VOXEL_BUILTINS: dict[str, Callable[[list[object]], object]] = {
    "voxel_grid": _grid_factory,
    "voxel_set": _set_voxel,
    "voxel_remove": _remove_voxel,
    "voxel_get": _get_voxel,
    "voxel_count": _voxel_count,
    "voxel_mesh": _voxel_mesh,
    "voxel_chunks": _voxel_chunks,
    "voxel_frame_plan": _frame_plan,
    "voxel_raycast": _voxel_raycast,
    "voxel_octree": _voxel_octree,
    "voxel_octree_get": _octree_get,
    "voxel_export": _voxel_export,
    "voxel_spectral_profile": _voxel_spectral_profile,
    "voxel_solve_field": _voxel_solve_field,
    "voxel_sparsify": _voxel_sparsify,
}

__all__=["VOXEL_BUILTINS"]
