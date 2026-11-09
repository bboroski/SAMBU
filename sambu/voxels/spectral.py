"""Sparse voxel graphs and Spielman-style spectral sparsification.

The implementation uses matrix-free conjugate gradients for graph Laplacians
and effective-resistance sampling. It is intentionally bounded to small and
medium CPU-side graphs; production-scale solvers should use a compiled backend.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import Mapping, Sequence

from .core import Coord, SparseVoxelGrid


@dataclass(frozen=True, slots=True)
class GraphEdge:
    u: int
    v: int
    weight: float = 1.0

    def __post_init__(self) -> None:
        if isinstance(self.u, bool) or not isinstance(self.u, int) or self.u < 0:
            raise ValueError("edge u must be a non-negative integer")
        if isinstance(self.v, bool) or not isinstance(self.v, int) or self.v < 0:
            raise ValueError("edge v must be a non-negative integer")
        if self.u == self.v:
            raise ValueError("self-loop edges are not supported")
        if not math.isfinite(self.weight) or self.weight <= 0:
            raise ValueError("edge weight must be finite and positive")


@dataclass(frozen=True, slots=True)
class VoxelGraph:
    nodes: tuple[Coord, ...]
    edges: tuple[GraphEdge, ...]

    def __post_init__(self) -> None:
        if len(self.nodes) > 100_000:
            raise ValueError("voxel graph may contain at most 100,000 nodes")
        if len(self.edges) > 1_000_000:
            raise ValueError("voxel graph may contain at most 1,000,000 edges")
        seen: set[tuple[int, int]] = set()
        for edge in self.edges:
            if not isinstance(edge, GraphEdge):
                raise TypeError("edges must contain GraphEdge instances")
            if edge.u >= len(self.nodes) or edge.v >= len(self.nodes):
                raise ValueError("edge endpoint is outside the node array")
            key = (min(edge.u, edge.v), max(edge.u, edge.v))
            if key in seen:
                raise ValueError("parallel edges must be combined before constructing VoxelGraph")
            seen.add(key)

    @property
    def vertex_count(self) -> int:
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        return len(self.edges)

    @property
    def nonzero_count(self) -> int:
        return self.vertex_count + 2 * self.edge_count

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": "sambu.voxel_graph.v1",
            "nodes": [list(node) for node in self.nodes],
            "edges": [{"u": edge.u, "v": edge.v, "weight": edge.weight} for edge in self.edges],
        }


def graph_from_voxels(grid: SparseVoxelGrid, *, face_conductance: float = 1.0) -> VoxelGraph:
    """Build a 6-neighbour undirected graph over occupied voxel cells."""
    if not math.isfinite(face_conductance) or face_conductance <= 0:
        raise ValueError("face_conductance must be finite and positive")
    nodes = tuple(coord for coord, _ in grid.iter_voxels(morton_order=True))
    indices = {coord: index for index, coord in enumerate(nodes)}
    edges: list[GraphEdge] = []
    for coord, index in indices.items():
        x, y, z = coord
        for neighbour in ((x + 1, y, z), (x, y + 1, z), (x, y, z + 1)):
            other = indices.get(neighbour)
            if other is not None:
                edges.append(GraphEdge(index, other, face_conductance))
    return VoxelGraph(nodes, tuple(edges))


class SparseLaplacian:
    """CSR graph Laplacian L = D - A with matrix-free products and CG solves."""

    def __init__(self, graph: VoxelGraph):
        self.graph = graph
        n = graph.vertex_count
        rows: list[dict[int, float]] = [dict() for _ in range(n)]
        diagonal = [0.0] * n
        adjacency: list[list[int]] = [[] for _ in range(n)]
        for edge in graph.edges:
            diagonal[edge.u] += edge.weight
            diagonal[edge.v] += edge.weight
            rows[edge.u][edge.v] = rows[edge.u].get(edge.v, 0.0) - edge.weight
            rows[edge.v][edge.u] = rows[edge.v].get(edge.u, 0.0) - edge.weight
            adjacency[edge.u].append(edge.v)
            adjacency[edge.v].append(edge.u)
        self.diagonal = tuple(diagonal)
        row_ptr = [0]
        columns: list[int] = []
        values: list[float] = []
        for index, row in enumerate(rows):
            if diagonal[index]:
                row[index] = diagonal[index]
            for column, value in sorted(row.items()):
                if value:
                    columns.append(column)
                    values.append(value)
            row_ptr.append(len(columns))
        self.row_ptr = tuple(row_ptr)
        self.columns = tuple(columns)
        self.values = tuple(values)
        self._adjacency = tuple(tuple(row) for row in adjacency)
        self._components = self._find_components()

    @classmethod
    def from_grid(cls, grid: SparseVoxelGrid, *, face_conductance: float = 1.0) -> "SparseLaplacian":
        return cls(graph_from_voxels(grid, face_conductance=face_conductance))

    @property
    def size(self) -> int:
        return self.graph.vertex_count

    @property
    def nnz(self) -> int:
        return len(self.values)

    def _find_components(self) -> tuple[tuple[int, ...], ...]:
        visited: set[int] = set()
        components: list[tuple[int, ...]] = []
        for start in range(self.size):
            if start in visited:
                continue
            stack = [start]
            visited.add(start)
            component: list[int] = []
            while stack:
                current = stack.pop()
                component.append(current)
                for neighbour in self._adjacency[current]:
                    if neighbour not in visited:
                        visited.add(neighbour)
                        stack.append(neighbour)
            components.append(tuple(component))
        return tuple(components)

    def matvec(self, vector: Sequence[float]) -> tuple[float, ...]:
        if len(vector) != self.size:
            raise ValueError(f"vector length must be {self.size}")
        result = [0.0] * self.size
        for row in range(self.size):
            total = 0.0
            for position in range(self.row_ptr[row], self.row_ptr[row + 1]):
                total += self.values[position] * float(vector[self.columns[position]])
            result[row] = total
        return tuple(result)

    def _check_balanced_rhs(self, rhs: Sequence[float]) -> None:
        for component in self._components:
            total = sum(rhs[index] for index in component)
            scale = max(1.0, sum(abs(rhs[index]) for index in component))
            if abs(total) > 1e-9 * scale:
                raise ValueError("Laplacian right-hand side must sum to zero in every connected component")

    def solve_vector(
        self,
        rhs: Sequence[float],
        *,
        tolerance: float = 1e-8,
        max_iterations: int | None = None,
    ) -> tuple[float, ...]:
        """Solve Lx=b in the zero-mean subspace using Jacobi-preconditioned CG."""
        if len(rhs) != self.size:
            raise ValueError(f"right-hand side length must be {self.size}")
        b = tuple(float(value) for value in rhs)
        if not all(math.isfinite(value) for value in b):
            raise ValueError("right-hand side values must be finite")
        if not math.isfinite(tolerance) or not 0 < tolerance < 1:
            raise ValueError("tolerance must be between zero and one")
        self._check_balanced_rhs(b)
        if not b or max((abs(value) for value in b), default=0.0) == 0.0:
            return tuple(0.0 for _ in b)
        if max_iterations is None:
            max_iterations = max(32, min(20_000, self.size * 8))
        if isinstance(max_iterations, bool) or not isinstance(max_iterations, int) or max_iterations < 1:
            raise ValueError("max_iterations must be a positive integer")

        x = [0.0] * self.size
        r = list(b)
        z = [r[i] / self.diagonal[i] if self.diagonal[i] > 0 else 0.0 for i in range(self.size)]
        p = z[:]
        rz = sum(r[i] * z[i] for i in range(self.size))
        norm_b = math.sqrt(sum(value * value for value in b))
        threshold = tolerance * max(norm_b, 1e-30)

        for _ in range(max_iterations):
            ap = self.matvec(p)
            denominator = sum(p[i] * ap[i] for i in range(self.size))
            if denominator <= 1e-30:
                break
            alpha = rz / denominator
            for i in range(self.size):
                x[i] += alpha * p[i]
                r[i] -= alpha * ap[i]
            norm_r = math.sqrt(sum(value * value for value in r))
            if norm_r <= threshold:
                # Pin the arbitrary additive constant independently in each component.
                for component in self._components:
                    mean = sum(x[i] for i in component) / len(component)
                    for i in component:
                        x[i] -= mean
                return tuple(x)
            z = [r[i] / self.diagonal[i] if self.diagonal[i] > 0 else 0.0 for i in range(self.size)]
            next_rz = sum(r[i] * z[i] for i in range(self.size))
            if rz == 0:
                break
            beta = next_rz / rz
            p = [z[i] + beta * p[i] for i in range(self.size)]
            rz = next_rz
        residual = math.sqrt(sum(value * value for value in self.matvec(x)[i:i+1] for i in range(0))) if False else math.sqrt(
            sum((a - b_value) ** 2 for a, b_value in zip(self.matvec(x), b))
        )
        if residual > threshold * 10:
            raise RuntimeError(f"conjugate-gradient solver did not converge; residual={residual:.3g}")
        for component in self._components:
            mean = sum(x[i] for i in component) / len(component)
            for i in component:
                x[i] -= mean
        return tuple(x)

    def solve(
        self,
        rhs: Mapping[Coord, float],
        *,
        tolerance: float = 1e-8,
        max_iterations: int | None = None,
    ) -> dict[Coord, float]:
        """Solve a coordinate-keyed voxel field on the graph Laplacian."""
        unknown = set(rhs) - set(self.graph.nodes)
        if unknown:
            raise KeyError(f"right-hand side references {len(unknown)} unknown voxel coordinates")
        vector = [float(rhs.get(node, 0.0)) for node in self.graph.nodes]
        result = self.solve_vector(vector, tolerance=tolerance, max_iterations=max_iterations)
        return dict(zip(self.graph.nodes, result))

    def effective_resistance(self, u: int, v: int, *, tolerance: float = 1e-7) -> float:
        if not (0 <= u < self.size and 0 <= v < self.size) or u == v:
            raise ValueError("effective resistance requires two distinct valid node indices")
        rhs = [0.0] * self.size
        rhs[u], rhs[v] = 1.0, -1.0
        solution = self.solve_vector(rhs, tolerance=tolerance)
        return max(0.0, solution[u] - solution[v])


@dataclass(frozen=True, slots=True)
class SpectralSparsifierResult:
    graph: VoxelGraph
    epsilon: float
    failure_probability: float
    original_edges: int
    retained_edges: int
    sampled_edges: tuple[tuple[int, int, float, float], ...]

    @property
    def edge_reduction(self) -> float:
        if self.original_edges == 0:
            return 0.0
        return 1.0 - self.retained_edges / self.original_edges

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": "sambu.spielman_sparsifier.v1",
            "epsilon": self.epsilon,
            "failure_probability": self.failure_probability,
            "original_edges": self.original_edges,
            "retained_edges": self.retained_edges,
            "edge_reduction": self.edge_reduction,
            "edges": [{"u":u,"v":v,"weight":w,"sampling_probability":p} for u,v,w,p in self.sampled_edges],
        }


class SpielmanSpectralSparsifier:
    """Effective-resistance edge sampler inspired by Spielman-Srivastava sparsification.

    Sampling is randomized; the output is an expected spectral approximation, not a
    deterministic per-input error certificate. Exact resistance estimation here is
    bounded to <=512 vertices and <=8192 edges.
    """

    def __init__(self, *, max_vertices: int = 512, max_edges: int = 8192):
        self.max_vertices = max_vertices
        self.max_edges = max_edges

    def sparsify(
        self,
        graph: VoxelGraph,
        *,
        epsilon: float = 0.5,
        failure_probability: float = 0.1,
        seed: int = 0,
    ) -> SpectralSparsifierResult:
        if not math.isfinite(epsilon) or not 0 < epsilon < 1:
            raise ValueError("epsilon must be strictly between 0 and 1")
        if not math.isfinite(failure_probability) or not 0 < failure_probability < 1:
            raise ValueError("failure_probability must be strictly between 0 and 1")
        if graph.vertex_count > self.max_vertices or graph.edge_count > self.max_edges:
            raise ValueError(
                f"exact CPU resistance sampler is limited to {self.max_vertices} vertices "
                f"and {self.max_edges} edges"
            )
        if not graph.edges:
            return SpectralSparsifierResult(graph, epsilon, failure_probability, 0, 0, ())
        laplacian = SparseLaplacian(graph)
        rng = random.Random(seed)
        strength = 2.0 * math.log(2.0 * max(2, graph.vertex_count) / failure_probability) / (epsilon * epsilon)
        kept: list[GraphEdge] = []
        samples: list[tuple[int, int, float, float]] = []
        for edge in graph.edges:
            resistance = laplacian.effective_resistance(edge.u, edge.v)
            leverage = min(1.0, max(0.0, edge.weight * resistance))
            probability = min(1.0, strength * leverage)
            if probability >= 1.0 or rng.random() < probability:
                reweighted = edge.weight / probability if probability > 0 else edge.weight
                kept.append(GraphEdge(edge.u, edge.v, reweighted))
                samples.append((edge.u, edge.v, reweighted, probability))
        sparse = VoxelGraph(graph.nodes, tuple(kept))
        return SpectralSparsifierResult(
            sparse, epsilon, failure_probability, graph.edge_count, len(kept), tuple(samples),
        )


__all__ = [
    "GraphEdge", "VoxelGraph", "graph_from_voxels", "SparseLaplacian",
    "SpectralSparsifierResult", "SpielmanSpectralSparsifier",
]
