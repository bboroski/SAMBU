"""Reproducible micro-benchmarks for SAMBU sparse voxel primitives.

Run with: python benchmarks/benchmark_voxels.py --size 16
Optional small spectral solve: --include-spectral --size 6

Results are measurements from the current host, never hard-coded performance claims.
"""
from __future__ import annotations

import argparse
import json
import platform
import statistics
import time
from typing import Callable

from sambu.voxels import (
    SparseLaplacian,
    SparseVoxelGrid,
    SparseVoxelOctree,
    graph_from_voxels,
    plan_frame_updates,
)


def measure(operation: Callable[[], object], repeats: int) -> tuple[object, dict[str, float]]:
    samples = []
    result = None
    for _ in range(repeats):
        start = time.perf_counter()
        result = operation()
        samples.append(time.perf_counter() - start)
    return result, {
        "minimum_seconds": min(samples),
        "median_seconds": statistics.median(samples),
        "maximum_seconds": max(samples),
        "repeats": repeats,
    }


def build_cube(size: int, chunk_size: int) -> SparseVoxelGrid:
    grid = SparseVoxelGrid(chunk_size=chunk_size, max_voxels=size ** 3)
    for z in range(size):
        for y in range(size):
            for x in range(size):
                material = 1 + ((x + 3 * y + 7 * z) % 16)
                grid.set_voxel(x, y, z, material)
    return grid


def run(size: int, chunk_size: int, repeats: int, include_spectral: bool) -> dict[str, object]:
    grid, build_timing = measure(lambda: build_cube(size, chunk_size), repeats)
    assert isinstance(grid, SparseVoxelGrid)

    mesh, mesh_timing = measure(grid.build_surface_mesh, repeats)
    tree, octree_timing = measure(lambda: SparseVoxelOctree.build(grid), repeats)
    chunks, chunk_timing = measure(lambda: tuple(grid.iter_chunks()), repeats)
    dirty_plan, plan_timing = measure(
        lambda: plan_frame_updates(
            1, grid.dirty_chunks, (0, 0, 0), max_chunks=max(1, min(64, len(grid.dirty_chunks))),
        ),
        repeats,
    )

    report: dict[str, object] = {
        "schema": "sambu.voxel_benchmark.v1",
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "configuration": {
            "size": size,
            "chunk_size": chunk_size,
            "repeats": repeats,
            "include_spectral": include_spectral,
        },
        "counts": {
            "voxels": grid.voxel_count,
            "chunks": len(chunks),
            "dirty_chunks": len(grid.dirty_chunks),
            "planned_upload_chunks": len(dirty_plan.selected_chunks),
            "deferred_upload_chunks": len(dirty_plan.deferred_chunks),
            "octree_nodes": tree.node_count,
            "visible_surface_faces": mesh.face_count,
            "surface_triangles": mesh.triangle_count,
            "surface_vertices": len(mesh.vertices),
        },
        "timings": {
            "grid_build": build_timing,
            "chunk_materialization": chunk_timing,
            "frame_plan": plan_timing,
            "octree_build": octree_timing,
            "surface_mesh_build": mesh_timing,
        },
        "notes": [
            "This is a CPU-side Python micro-benchmark, not an engine or GPU benchmark.",
            "Compare runs on the same hardware, Python build, chunk size and workload.",
            "The filled cube workload favours regular adjacency; sparse fractal and terrain workloads behave differently.",
        ],
    }

    if include_spectral:
        graph, graph_timing = measure(lambda: graph_from_voxels(grid), repeats)
        laplacian, lap_timing = measure(lambda: SparseLaplacian(graph), repeats)
        rhs = [0.0] * graph.vertex_count
        if rhs:
            rhs[0] = 1.0
            rhs[-1] -= 1.0
        solution, solve_timing = measure(lambda: laplacian.solve_vector(rhs), repeats)
        report["counts"]["graph_vertices"] = graph.vertex_count
        report["counts"]["graph_edges"] = graph.edge_count
        report["counts"]["laplacian_nonzeros"] = laplacian.nnz
        report["counts"]["field_solution_values"] = len(solution)
        report["timings"]["voxel_graph_build"] = graph_timing
        report["timings"]["laplacian_build"] = lap_timing
        report["timings"]["laplacian_solve"] = solve_timing

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark SAMBU sparse voxel reference algorithms.")
    parser.add_argument("--size", type=int, default=16, help="side length of the filled voxel cube (1..64)")
    parser.add_argument("--chunk-size", type=int, default=16)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--include-spectral", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not 1 <= args.size <= 64:
        parser.error("--size must be between 1 and 64")
    if not 1 <= args.chunk_size <= 256:
        parser.error("--chunk-size must be between 1 and 256")
    if not 1 <= args.repeats <= 20:
        parser.error("--repeats must be between 1 and 20")
    if args.include_spectral and args.size > 6:
        parser.error("--include-spectral is deliberately bounded to size <= 6")

    report = run(args.size, args.chunk_size, args.repeats, args.include_spectral)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"SAMBU voxel benchmark — {report['environment']['python']} / {report['environment']['platform']}")
        for name, value in report["counts"].items():
            print(f"{name}: {value}")
        print("\nMedian timings:")
        for name, value in report["timings"].items():
            print(f"  {name}: {value['median_seconds']:.6f} s")
        print("\nMeasurements only; no cross-machine performance claim is implied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
