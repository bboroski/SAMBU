"""Sparse voxel storage, spatial frames, Morton ordering, meshing and ray traversal."""
from __future__ import annotations

from dataclasses import dataclass
import json
import math
import struct
from collections import defaultdict
from collections.abc import Iterator, Mapping
from typing import TypeAlias

Coord: TypeAlias = tuple[int, int, int]
Vec3: TypeAlias = tuple[float, float, float]
Matrix3: TypeAlias = tuple[Vec3, Vec3, Vec3]

_MAX_COORD = (1 << 31) - 1
_MIN_COORD = -(1 << 31)
_MORTON_BIAS = 1 << 20
_MAX_VOXELS = 2_000_000


def _finite3(value: object, name: str) -> Vec3:
    if not isinstance(value, (tuple, list)) or len(value) != 3:
        raise TypeError(f"{name} must contain exactly three numbers")
    if any(isinstance(item, bool) for item in value):
        raise TypeError(f"{name} values must be numeric, not booleans")
    result = tuple(float(item) for item in value)
    if not all(math.isfinite(item) for item in result):
        raise ValueError(f"{name} values must be finite")
    return result  # type: ignore[return-value]


def _exact_coord(value: object, name: str) -> Coord:
    if not isinstance(value, (tuple, list)) or len(value) != 3:
        raise TypeError(f"{name} must contain exactly three integer coordinates")
    if any(isinstance(item, bool) or not isinstance(item, int) for item in value):
        raise TypeError(f"{name} coordinates must be integers")
    if any(item < _MIN_COORD or item > _MAX_COORD for item in value):
        raise ValueError(f"{name} coordinates must fit signed 32-bit integers")
    return (value[0], value[1], value[2])


def _determinant(m: Matrix3) -> float:
    a, b, c = m
    return (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - a[1] * (b[0] * c[2] - b[2] * c[0])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
    )


def _inverse(m: Matrix3) -> Matrix3:
    a, b, c = m
    det = _determinant(m)
    if abs(det) < 1e-12:
        raise ValueError("voxel frame axes must form an invertible basis")
    inv = (
        (b[1] * c[2] - b[2] * c[1], a[2] * c[1] - a[1] * c[2], a[1] * b[2] - a[2] * b[1]),
        (b[2] * c[0] - b[0] * c[2], a[0] * c[2] - a[2] * c[0], a[2] * b[0] - a[0] * b[2]),
        (b[0] * c[1] - b[1] * c[0], a[1] * c[0] - a[0] * c[1], a[0] * b[1] - a[1] * b[0]),
    )
    return tuple(tuple(value / det for value in row) for row in inv)  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class VoxelFrame:
    """Affine grid frame in world coordinates. Axes is a row-major 3x3 basis."""

    origin: Vec3 = (0.0, 0.0, 0.0)
    voxel_size: float = 1.0
    axes: Matrix3 = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))

    def __post_init__(self) -> None:
        object.__setattr__(self, "origin", _finite3(self.origin, "origin"))
        if isinstance(self.voxel_size, bool) or not math.isfinite(self.voxel_size) or self.voxel_size <= 0:
            raise ValueError("voxel_size must be finite and greater than zero")
        if len(self.axes) != 3 or any(len(row) != 3 for row in self.axes):
            raise ValueError("axes must be a 3x3 matrix")
        axes = tuple(_finite3(row, "axis row") for row in self.axes)
        object.__setattr__(self, "axes", axes)
        _inverse(axes)

    def grid_to_world(self, position: tuple[float, float, float]) -> Vec3:
        x, y, z = _finite3(position, "grid position")
        return tuple(
            self.origin[row] + self.voxel_size * (
                self.axes[row][0] * x + self.axes[row][1] * y + self.axes[row][2] * z
            )
            for row in range(3)
        )  # type: ignore[return-value]

    def world_to_grid(self, position: Vec3) -> Vec3:
        world = _finite3(position, "world position")
        relative = tuple((world[i] - self.origin[i]) / self.voxel_size for i in range(3))
        inverse = _inverse(self.axes)
        return tuple(
            sum(inverse[row][column] * relative[column] for column in range(3))
            for row in range(3)
        )  # type: ignore[return-value]


def _spread21(value: int) -> int:
    value &= 0x1FFFFF
    value = (value | (value << 32)) & 0x1F00000000FFFF
    value = (value | (value << 16)) & 0x1F0000FF0000FF
    value = (value | (value << 8)) & 0x100F00F00F00F00F
    value = (value | (value << 4)) & 0x10C30C30C30C30C3
    value = (value | (value << 2)) & 0x1249249249249249
    return value


def _compact21(value: int) -> int:
    value &= 0x1249249249249249
    value = (value ^ (value >> 2)) & 0x10C30C30C30C30C3
    value = (value ^ (value >> 4)) & 0x100F00F00F00F00F
    value = (value ^ (value >> 8)) & 0x1F0000FF0000FF
    value = (value ^ (value >> 16)) & 0x1F00000000FFFF
    value = (value ^ (value >> 32)) & 0x1FFFFF
    return value


def encode_morton3(x: int, y: int, z: int) -> int:
    """Encode signed 21-bit voxel coordinates into a 63-bit Morton key."""
    values = (x, y, z)
    if any(isinstance(v, bool) or not isinstance(v, int) for v in values):
        raise TypeError("Morton coordinates must be integers")
    if any(v < -(1 << 20) or v >= (1 << 20) for v in values):
        raise ValueError("Morton coordinates must be in [-2^20, 2^20-1]")
    bx, by, bz = (v + (1 << 20) for v in values)
    return _spread21(bx) | (_spread21(by) << 1) | (_spread21(bz) << 2)


def decode_morton3(code: int) -> Coord:
    if isinstance(code, bool) or not isinstance(code, int) or code < 0 or code >= (1 << 63):
        raise ValueError("Morton key must be an unsigned 63-bit integer")
    return (
        _compact21(code) - (1 << 20),
        _compact21(code >> 1) - (1 << 20),
        _compact21(code >> 2) - (1 << 20),
    )


@dataclass(frozen=True, slots=True)
class VoxelChunk:
    coordinate: Coord
    chunk_size: int
    voxels: tuple[tuple[int, int, int, int], ...]

    @property
    def voxel_count(self) -> int:
        return len(self.voxels)


@dataclass(frozen=True, slots=True)
class SurfaceMesh:
    vertices: tuple[Vec3, ...]
    normals: tuple[Vec3, ...]
    indices: tuple[int, ...]
    face_materials: tuple[int, ...]

    @property
    def triangle_count(self) -> int:
        return len(self.indices) // 3

    @property
    def face_count(self) -> int:
        return len(self.face_materials)


@dataclass(frozen=True, slots=True)
class VoxelHit:
    coordinate: Coord
    material_id: int
    distance: float


@dataclass(frozen=True, slots=True)
class FramePlan:
    frame_index: int
    selected_chunks: tuple[Coord, ...]
    deferred_chunks: tuple[Coord, ...]
    max_chunks: int
    lod_distance: float


def plan_frame_updates(
    frame_index: int,
    dirty_chunks: Iterator[Coord] | tuple[Coord, ...] | list[Coord] | set[Coord],
    camera_chunk: Coord,
    *,
    max_chunks: int,
    lod_distance: float = 0.0,
) -> FramePlan:
    """Select nearest dirty chunks for one bounded frame upload budget."""
    if isinstance(frame_index, bool) or not isinstance(frame_index, int) or frame_index < 0:
        raise ValueError("frame_index must be a non-negative integer")
    if isinstance(max_chunks, bool) or not isinstance(max_chunks, int) or max_chunks < 0:
        raise ValueError("max_chunks must be a non-negative integer")
    camera = _exact_coord(camera_chunk, "camera_chunk")
    if isinstance(lod_distance, bool) or not math.isfinite(lod_distance) or lod_distance < 0:
        raise ValueError("lod_distance must be finite and non-negative")
    unique = {_exact_coord(coord, "dirty chunk") for coord in dirty_chunks}
    ordered = sorted(unique, key=lambda item: (
        sum((item[i] - camera[i]) ** 2 for i in range(3)), item
    ))
    return FramePlan(frame_index, tuple(ordered[:max_chunks]), tuple(ordered[max_chunks:]), max_chunks, float(lod_distance))


_FACE_DATA = (
    ((1, 0, 0), ((1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1))),
    ((-1, 0, 0), ((0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0))),
    ((0, 1, 0), ((0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0))),
    ((0, -1, 0), ((0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1))),
    ((0, 0, 1), ((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1))),
    ((0, 0, -1), ((0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0))),
)


class SparseVoxelGrid:
    """Sparse integer voxel map with deterministic chunks and renderer-neutral export."""

    def __init__(self, *, frame: VoxelFrame | None = None, chunk_size: int = 16, max_voxels: int = _MAX_VOXELS):
        if isinstance(chunk_size, bool) or not isinstance(chunk_size, int) or not 1 <= chunk_size <= 256:
            raise ValueError("chunk_size must be an integer from 1 to 256")
        if isinstance(max_voxels, bool) or not isinstance(max_voxels, int) or not 1 <= max_voxels <= _MAX_VOXELS:
            raise ValueError(f"max_voxels must be an integer from 1 to {_MAX_VOXELS:,}")
        self.frame = frame or VoxelFrame()
        self.chunk_size = chunk_size
        self.max_voxels = max_voxels
        self._voxels: dict[Coord, int] = {}
        self._dirty_chunks: set[Coord] = set()

    @property
    def voxel_count(self) -> int:
        return len(self._voxels)

    @property
    def dirty_chunks(self) -> tuple[Coord, ...]:
        return tuple(sorted(self._dirty_chunks))

    @property
    def bounds(self) -> tuple[Coord, Coord] | None:
        if not self._voxels:
            return None
        coords = tuple(self._voxels)
        return (
            tuple(min(p[i] for p in coords) for i in range(3)),  # type: ignore[arg-type]
            tuple(max(p[i] for p in coords) for i in range(3)),  # type: ignore[arg-type]
        )

    def _coord(self, x: int, y: int, z: int) -> Coord:
        values = (x, y, z)
        if any(isinstance(v, bool) or not isinstance(v, int) for v in values):
            raise TypeError("voxel coordinates must be integers")
        if any(v < _MIN_COORD or v > _MAX_COORD for v in values):
            raise ValueError("voxel coordinates must fit signed 32-bit integers")
        return values

    def _chunk_key(self, coord: Coord) -> Coord:
        return tuple(v // self.chunk_size for v in coord)  # type: ignore[return-value]

    def set_voxel(self, x: int, y: int, z: int, material_id: int = 1) -> None:
        coord = self._coord(x, y, z)
        if isinstance(material_id, bool) or not isinstance(material_id, int) or not 1 <= material_id <= 65535:
            raise ValueError("material_id must be an integer from 1 to 65535")
        if coord not in self._voxels and len(self._voxels) >= self.max_voxels:
            raise ValueError(f"voxel grid limit ({self.max_voxels:,}) exceeded")
        if self._voxels.get(coord) != material_id:
            self._voxels[coord] = material_id
            self._dirty_chunks.add(self._chunk_key(coord))

    def remove_voxel(self, x: int, y: int, z: int) -> bool:
        coord = self._coord(x, y, z)
        if coord not in self._voxels:
            return False
        del self._voxels[coord]
        self._dirty_chunks.add(self._chunk_key(coord))
        return True

    def get_voxel(self, x: int, y: int, z: int) -> int | None:
        return self._voxels.get(self._coord(x, y, z))

    def is_solid(self, x: int, y: int, z: int) -> bool:
        return self.get_voxel(x, y, z) is not None

    def iter_voxels(self, *, morton_order: bool = False) -> Iterator[tuple[Coord, int]]:
        if morton_order:
            def key(position: Coord):
                try:
                    return (0, encode_morton3(*position))
                except ValueError:
                    return (1, position)
            for coord in sorted(self._voxels, key=key):
                yield coord, self._voxels[coord]
        else:
            for coord in sorted(self._voxels):
                yield coord, self._voxels[coord]

    def iter_chunks(self) -> Iterator[VoxelChunk]:
        grouped: dict[Coord, list[tuple[int, int, int, int]]] = defaultdict(list)
        for (x, y, z), material in self._voxels.items():
            key = self._chunk_key((x, y, z))
            local = (x - key[0] * self.chunk_size, y - key[1] * self.chunk_size, z - key[2] * self.chunk_size)
            grouped[key].append((*local, material))
        for key in sorted(grouped):
            entries = tuple(sorted(grouped[key], key=lambda v: encode_morton3(v[0], v[1], v[2])))
            yield VoxelChunk(key, self.chunk_size, entries)

    def acknowledge_chunks(self, chunks: Iterator[Coord] | tuple[Coord, ...] | list[Coord]) -> None:
        for chunk in chunks:
            key = _exact_coord(chunk, "chunk coordinate")
            self._dirty_chunks.discard(key)

    def build_surface_mesh(self, *, max_faces: int = 1_000_000) -> SurfaceMesh:
        """Build exposed faces, rejecting unexpectedly large allocations before emission."""
        if isinstance(max_faces, bool) or not isinstance(max_faces, int) or not 0 <= max_faces <= 12_000_000:
            raise ValueError("max_faces must be an integer from 0 to 12,000,000")
        visible_faces = 0
        for (x, y, z), _material in self._voxels.items():
            for (dx, dy, dz), _corners in _FACE_DATA:
                if (x + dx, y + dy, z + dz) not in self._voxels:
                    visible_faces += 1
                    if visible_faces > max_faces:
                        raise ValueError(
                            f"surface mesh requires more than max_faces={max_faces:,}; "
                            "build smaller chunks or use the engine GPU mesher"
                        )

        vertices: list[Vec3] = []
        normals: list[Vec3] = []
        indices: list[int] = []
        materials: list[int] = []
        for (x, y, z), material in self.iter_voxels(morton_order=True):
            for (dx, dy, dz), corners in _FACE_DATA:
                if (x + dx, y + dy, z + dz) in self._voxels:
                    continue
                base = len(vertices)
                for cx, cy, cz in corners:
                    vertices.append((x + cx, y + cy, z + cz))
                    normals.append((float(dx), float(dy), float(dz)))
                indices.extend((base, base + 1, base + 2, base, base + 2, base + 3))
                materials.append(material)
        return SurfaceMesh(tuple(vertices), tuple(normals), tuple(indices), tuple(materials))

    def raycast(self, origin_world: Vec3, direction_world: Vec3, *, max_distance: float = 1_000_000.0, max_steps: int = 1_000_000) -> VoxelHit | None:
        """Amanatides-Woo traversal. Direction is normalized in world space."""
        if not math.isfinite(max_distance) or max_distance < 0:
            raise ValueError("max_distance must be finite and non-negative")
        if isinstance(max_steps, bool) or not isinstance(max_steps, int) or max_steps < 1:
            raise ValueError("max_steps must be a positive integer")
        origin = self.frame.world_to_grid(origin_world)
        direction = _finite3(direction_world, "ray direction")
        magnitude = math.sqrt(sum(v * v for v in direction))
        if magnitude <= 1e-15:
            raise ValueError("ray direction cannot be zero")
        direction = tuple(v / magnitude for v in direction)  # type: ignore[assignment]
        inverse = _inverse(self.frame.axes)
        grid_direction = tuple(
            sum(inverse[row][col] * direction[col] for col in range(3)) / self.frame.voxel_size
            for row in range(3)
        )
        cell = [math.floor(v) for v in origin]
        step = [1 if v > 0 else (-1 if v < 0 else 0) for v in grid_direction]
        t_delta = [abs(1.0 / v) if v != 0 else math.inf for v in grid_direction]
        t_max = []
        for axis in range(3):
            if step[axis] > 0:
                t_max.append((cell[axis] + 1 - origin[axis]) / grid_direction[axis])
            elif step[axis] < 0:
                t_max.append((cell[axis] - origin[axis]) / grid_direction[axis])
            else:
                t_max.append(math.inf)
        distance = 0.0
        for _ in range(max_steps):
            coord = (cell[0], cell[1], cell[2])
            material = self._voxels.get(coord)
            if material is not None and distance <= max_distance:
                return VoxelHit(coord, material, max(0.0, distance))
            axis = min(range(3), key=lambda i: t_max[i])
            distance = t_max[axis]
            if not math.isfinite(distance) or distance > max_distance:
                return None
            cell[axis] += step[axis]
            t_max[axis] += t_delta[axis]
        raise RuntimeError(f"voxel ray traversal exceeded max_steps={max_steps}")

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": "sambu.voxel_grid.v1",
            "chunk_size": self.chunk_size,
            "frame": {"origin": list(self.frame.origin), "voxel_size": self.frame.voxel_size, "axes": [list(row) for row in self.frame.axes]},
            "voxels": [{"x": x, "y": y, "z": z, "material": material} for (x,y,z),material in self.iter_voxels(morton_order=True)],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    @classmethod
    def from_dict(cls, data: Mapping[str, object], *, max_voxels: int = _MAX_VOXELS) -> "SparseVoxelGrid":
        if data.get("schema") != "sambu.voxel_grid.v1":
            raise ValueError("unsupported voxel grid schema")
        frame_data = data.get("frame")
        if not isinstance(frame_data, Mapping):
            raise ValueError("voxel grid frame must be an object")
        frame = VoxelFrame(
            origin=tuple(frame_data.get("origin", (0,0,0))),  # type: ignore[arg-type]
            voxel_size=float(frame_data.get("voxel_size", 1.0)),
            axes=tuple(tuple(row) for row in frame_data.get("axes", ((1,0,0),(0,1,0),(0,0,1)))),  # type: ignore[arg-type]
        )
        grid = cls(frame=frame, chunk_size=int(data.get("chunk_size", 16)), max_voxels=max_voxels)
        voxels = data.get("voxels")
        if not isinstance(voxels, list) or len(voxels) > max_voxels:
            raise ValueError(f"voxels must be an array with at most {max_voxels:,} items")
        for entry in voxels:
            if not isinstance(entry, Mapping):
                raise ValueError("voxel entries must be objects")
            grid.set_voxel(int(entry["x"]), int(entry["y"]), int(entry["z"]), int(entry["material"]))
        grid._dirty_chunks.clear()
        return grid

    @classmethod
    def from_json(cls, source: str, *, max_voxels: int = _MAX_VOXELS) -> "SparseVoxelGrid":
        data = json.loads(source)
        if not isinstance(data, Mapping):
            raise ValueError("voxel JSON root must be an object")
        return cls.from_dict(data, max_voxels=max_voxels)

    def to_magica_vox(self, palette: Mapping[int, tuple[int,int,int,int]] | None = None) -> bytes:
        """Export a bounded MagicaVoxel VOX v150 scene with one SIZE/XYZI model."""
        if not self._voxels:
            raise ValueError("cannot export an empty voxel grid")
        bounds = self.bounds
        assert bounds is not None
        minimum, maximum = bounds
        dimensions = tuple(maximum[i] - minimum[i] + 1 for i in range(3))
        if any(size > 256 for size in dimensions):
            raise ValueError("MagicaVoxel VOX model dimensions cannot exceed 256 per axis")
        materials = sorted(set(self._voxels.values()))
        if len(materials) > 255:
            raise ValueError("MagicaVoxel palette supports at most 255 used materials")
        mapping = {material: i + 1 for i, material in enumerate(materials)}
        colors = palette or {}
        for material in materials:
            color = colors.get(material, ((material*73)%256,(material*151)%256,(material*199)%256,255))
            if len(color) != 4 or any(not 0 <= int(c) <= 255 for c in color):
                raise ValueError(f"invalid RGBA palette entry for material {material}")
        palette_entries = [
            tuple(map(int, colors.get(material, ((material*73)%256,(material*151)%256,(material*199)%256,255))))
            for material in materials
        ] + [(0,0,0,255)] * (256 - len(materials))
        rgba = bytes(channel for color in palette_entries for channel in color)
        size_content = struct.pack("<III", *dimensions)
        xyz = bytearray(struct.pack("<I", len(self._voxels)))
        for (x,y,z),material in self.iter_voxels(morton_order=True):
            xyz.extend(bytes((x-minimum[0],y-minimum[1],z-minimum[2],mapping[material])))
        def chunk(name: bytes, content: bytes, children: bytes = b"") -> bytes:
            return name + struct.pack("<II",len(content),len(children)) + content + children
        children = chunk(b"SIZE",size_content) + chunk(b"XYZI",bytes(xyz)) + chunk(b"RGBA",rgba)
        return b"VOX " + struct.pack("<I",150) + chunk(b"MAIN",b"",children)

    @classmethod
    def from_magica_vox(cls, payload: bytes, *, chunk_size: int = 16, max_voxels: int = _MAX_VOXELS) -> "SparseVoxelGrid":
        """Read the first SIZE/XYZI model from a basic MagicaVoxel v150 file."""
        if not isinstance(payload,(bytes,bytearray)) or len(payload)<20 or payload[:4]!=b"VOX ":
            raise ValueError("invalid MagicaVoxel VOX header")
        if struct.unpack_from("<I",payload,4)[0] < 150:
            raise ValueError("only MagicaVoxel VOX version 150 or newer is supported")
        size, points = None, None

        def visit(start: int, end: int) -> None:
            nonlocal size, points
            cursor = start
            while cursor + 12 <= end:
                chunk_id = payload[cursor:cursor+4]
                content_size, child_size = struct.unpack_from("<II", payload, cursor+4)
                content_start = cursor + 12
                content_end = content_start + content_size
                children_end = content_end + child_size
                if content_end > end or children_end > end:
                    raise ValueError("truncated MagicaVoxel chunk")
                content = payload[content_start:content_end]
                if chunk_id == b"SIZE" and content_size >= 12:
                    size = struct.unpack_from("<III", content, 0)
                elif chunk_id == b"XYZI" and content_size >= 4:
                    count = struct.unpack_from("<I", content, 0)[0]
                    if count > max_voxels or 4 + count * 4 > content_size:
                        raise ValueError("MagicaVoxel voxel count exceeds limit or chunk is truncated")
                    points = [tuple(content[4+i*4:8+i*4]) for i in range(count)]
                if child_size:
                    visit(content_end, children_end)
                cursor = children_end

        visit(8, len(payload))
        
        if size is None or points is None: raise ValueError("MagicaVoxel file is missing SIZE or XYZI chunks")
        if any(axis<1 or axis>256 for axis in size): raise ValueError("invalid MagicaVoxel model dimensions")
        grid=cls(chunk_size=chunk_size,max_voxels=max_voxels)
        for x,y,z,color in points:
            if x>=size[0] or y>=size[1] or z>=size[2] or color==0: raise ValueError("invalid MagicaVoxel voxel coordinate or palette index")
            grid.set_voxel(x,y,z,color)
        grid._dirty_chunks.clear()
        return grid


__all__ = ["VoxelFrame","VoxelChunk","SurfaceMesh","VoxelHit","FramePlan","SparseVoxelGrid","encode_morton3","decode_morton3","plan_frame_updates"]
