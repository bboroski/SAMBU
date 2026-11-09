"""Sparse occupied-node octree with implicit empty-space skipping."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterator
from .core import Coord, SparseVoxelGrid


@dataclass(frozen=True, slots=True)
class OctreeNode:
    origin: Coord
    size: int
    voxel_count: int
    child_mask: int
    children: tuple[tuple[int, "OctreeNode"], ...] = ()
    material_id: int | None = None

    @property
    def is_leaf(self) -> bool:
        return self.size == 1

    def child(self, octant: int) -> "OctreeNode | None":
        for index,node in self.children:
            if index==octant: return node
        return None

    def contains(self, coordinate: Coord) -> bool:
        return all(self.origin[i] <= coordinate[i] < self.origin[i]+self.size for i in range(3))


class SparseVoxelOctree:
    """Compact occupied-only octree; empty children are represented by clear mask bits."""

    def __init__(self, root: OctreeNode, minimum: Coord, side_length: int):
        self.root=root
        self.minimum=minimum
        self.side_length=side_length

    @classmethod
    def build(cls, grid: SparseVoxelGrid) -> "SparseVoxelOctree":
        entries=tuple(grid.iter_voxels(morton_order=True))
        if not entries:
            return cls(OctreeNode((0,0,0),1,0,0),(0,0,0),1)
        coords=[coord for coord,_ in entries]
        minimum=tuple(min(p[i] for p in coords) for i in range(3))
        maximum=tuple(max(p[i] for p in coords) for i in range(3))
        extent=max(maximum[i]-minimum[i]+1 for i in range(3))
        side=1 << (extent-1).bit_length()
        normalized=[((p[0]-minimum[0],p[1]-minimum[1],p[2]-minimum[2]),mat) for p,mat in entries]

        def build_node(origin: Coord, size: int, items: list[tuple[Coord,int]]) -> OctreeNode:
            if size==1:
                return OctreeNode(origin,1,len(items),0,(),items[0][1])
            half=size//2
            buckets: dict[int,list[tuple[Coord,int]]]={}
            for position,material in items:
                octant=(1 if position[0]>=origin[0]+half else 0)
                octant|=(2 if position[1]>=origin[1]+half else 0)
                octant|=(4 if position[2]>=origin[2]+half else 0)
                buckets.setdefault(octant,[]).append((position,material))
            children=[]; mask=0
            for octant in sorted(buckets):
                child_origin=(
                    origin[0]+(half if octant&1 else 0),
                    origin[1]+(half if octant&2 else 0),
                    origin[2]+(half if octant&4 else 0),
                )
                children.append((octant,build_node(child_origin,half,buckets[octant])))
                mask|=1<<octant
            return OctreeNode(origin,size,len(items),mask,tuple(children))
        return cls(build_node((0,0,0),side,normalized),minimum,side)

    def query(self, coordinate: Coord) -> int | None:
        local=tuple(coordinate[i]-self.minimum[i] for i in range(3))
        if not self.root.contains(local): return None
        node=self.root
        while not node.is_leaf:
            half=node.size//2
            octant=(1 if local[0]>=node.origin[0]+half else 0)
            octant|=(2 if local[1]>=node.origin[1]+half else 0)
            octant|=(4 if local[2]>=node.origin[2]+half else 0)
            child=node.child(octant)
            if child is None: return None
            node=child
        return node.material_id

    def iter_nodes(self) -> Iterator[OctreeNode]:
        stack=[self.root]
        while stack:
            node=stack.pop()
            yield node
            stack.extend(child for _,child in reversed(node.children))

    @property
    def node_count(self) -> int:
        return sum(1 for _ in self.iter_nodes())

    def to_dict(self) -> dict[str, object]:
        def encode(node: OctreeNode) -> dict[str, object]:
            return {
                "origin":list(node.origin),"size":node.size,"voxel_count":node.voxel_count,
                "child_mask":node.child_mask,"material_id":node.material_id,
                "children":[{"octant":index,"node":encode(child)} for index,child in node.children],
            }
        return {"schema":"sambu.sparse_voxel_octree.v1","minimum":list(self.minimum),"side_length":self.side_length,"node_count":self.node_count,"root":encode(self.root)}


__all__=["OctreeNode","SparseVoxelOctree"]
