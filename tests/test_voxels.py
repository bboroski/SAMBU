from __future__ import annotations
import math
import unittest

from sambu.voxels import (
    GraphEdge, SparseLaplacian, SparseVoxelGrid, SparseVoxelOctree, SpielmanSpectralSparsifier,
    VoxelFrame, VoxelGraph, decode_morton3, encode_morton3, engine_payload,
    graph_from_voxels, plan_frame_updates, supported_engines,
)


class VoxelFrameAndIndexTests(unittest.TestCase):
    def test_affine_frame_roundtrip(self):
        frame=VoxelFrame(
            origin=(10.0,20.0,30.0),
            voxel_size=2.0,
            axes=((0.0,-1.0,0.0),(1.0,0.0,0.0),(0.0,0.0,1.0)),
        )
        world=frame.grid_to_world((1.0,2.0,3.0))
        self.assertEqual(world,(6.0,22.0,36.0))
        restored=frame.world_to_grid(world)
        for a,b in zip(restored,(1.0,2.0,3.0)):
            self.assertAlmostEqual(a,b)

    def test_singular_frame_is_rejected(self):
        with self.assertRaises(ValueError):
            VoxelFrame(axes=((1,0,0),(2,0,0),(0,0,1)))

    def test_morton_signed_coordinate_roundtrip(self):
        for coord in ((0,0,0),(-17,4,31),(1048575,-1048576,7)):
            self.assertEqual(decode_morton3(encode_morton3(*coord)),coord)
        with self.assertRaises(ValueError):
            encode_morton3(1 << 20,0,0)


class SparseVoxelGridTests(unittest.TestCase):
    def test_chunking_negative_coordinates_and_dirty_upload_ack(self):
        grid=SparseVoxelGrid(chunk_size=16)
        grid.set_voxel(-1,-1,-1,7)
        grid.set_voxel(16,0,0,2)
        chunks=list(grid.iter_chunks())
        self.assertEqual([chunk.coordinate for chunk in chunks],[(-1,-1,-1),(1,0,0)])
        self.assertEqual(grid.dirty_chunks,((-1,-1,-1),(1,0,0)))
        grid.acknowledge_chunks([(-1,-1,-1)])
        self.assertEqual(grid.dirty_chunks,((1,0,0),))

    def test_face_culling_hides_internal_faces(self):
        grid=SparseVoxelGrid()
        grid.set_voxel(0,0,0,3)
        single=grid.build_surface_mesh()
        self.assertEqual((single.face_count,single.triangle_count),(6,12))
        grid.set_voxel(1,0,0,3)
        joined=grid.build_surface_mesh()
        self.assertEqual((joined.face_count,joined.triangle_count),(10,20))

    def test_ray_cast_hits_first_occupied_cell(self):
        grid=SparseVoxelGrid()
        grid.set_voxel(2,0,0,9)
        hit=grid.raycast((0.5,0.5,0.5),(1,0,0),max_distance=10)
        self.assertIsNotNone(hit)
        self.assertEqual(hit.coordinate,(2,0,0))
        self.assertEqual(hit.material_id,9)
        self.assertAlmostEqual(hit.distance,1.5)
        self.assertIsNone(grid.raycast((0.5,3.5,0.5),(1,0,0),max_distance=10))

    def test_json_roundtrip_and_large_coordinate_fallback(self):
        grid=SparseVoxelGrid()
        grid.set_voxel(1 << 22,-3,0,15)
        restored=SparseVoxelGrid.from_json(grid.to_json())
        self.assertEqual(restored.get_voxel(1 << 22,-3,0),15)
        self.assertEqual(list(restored.iter_voxels(morton_order=True))[0][0],(1 << 22,-3,0))

    def test_magica_vox_nested_chunk_roundtrip(self):
        grid=SparseVoxelGrid()
        grid.set_voxel(-2,3,4,11)
        grid.set_voxel(-1,3,4,17)
        binary=grid.to_magica_vox()
        self.assertTrue(binary.startswith(b"VOX "))
        restored=SparseVoxelGrid.from_magica_vox(binary)
        self.assertEqual(restored.voxel_count,2)
        self.assertEqual(restored.get_voxel(0,0,0),1)
        self.assertEqual(restored.get_voxel(1,0,0),2)
        self.assertEqual(restored.bounds,((0,0,0),(1,0,0)))

    def test_upload_frame_budget_is_nearest_first(self):
        plan=plan_frame_updates(12,[(3,0,0),(1,0,0),(2,0,0)],(0,0,0),max_chunks=2)
        self.assertEqual(plan.selected_chunks,((1,0,0),(2,0,0)))
        self.assertEqual(plan.deferred_chunks,((3,0,0),))


class VoxelOctreeTests(unittest.TestCase):
    def test_octree_queries_occupied_and_empty_cells(self):
        grid=SparseVoxelGrid()
        grid.set_voxel(-5,2,1,4)
        grid.set_voxel(-2,2,1,8)
        tree=SparseVoxelOctree.build(grid)
        self.assertEqual(tree.query((-5,2,1)),4)
        self.assertEqual(tree.query((-2,2,1)),8)
        self.assertIsNone(tree.query((-4,2,1)))
        self.assertGreater(tree.node_count,2)

    def test_empty_octree(self):
        tree=SparseVoxelOctree.build(SparseVoxelGrid())
        self.assertEqual(tree.node_count,1)
        self.assertIsNone(tree.query((0,0,0)))


class SpielmanVoxelMatrixTests(unittest.TestCase):
    def test_grid_graph_and_laplacian_structure(self):
        grid=SparseVoxelGrid()
        for x in range(3):
            grid.set_voxel(x,0,0)
        graph=graph_from_voxels(grid)
        self.assertEqual((graph.vertex_count,graph.edge_count),(3,2))
        lap=SparseLaplacian(graph)
        self.assertEqual(lap.nnz,7)
        self.assertEqual(lap.matvec((1,0,-1)),(1.0,0.0,-1.0))

    def test_laplacian_solve_and_effective_resistance(self):
        graph=VoxelGraph(((0,0,0),(1,0,0),(2,0,0)),(
            GraphEdge(0,1),GraphEdge(1,2),
        ))
        lap=SparseLaplacian(graph)
        solved=lap.solve_vector((1,0,-1))
        for actual,expected in zip(solved,(1,0,-1)):
            self.assertAlmostEqual(actual,expected)
        self.assertAlmostEqual(lap.effective_resistance(0,2),2.0,places=6)
        with self.assertRaises(ValueError):
            lap.solve_vector((1,0,0))

    def test_sparsifier_is_seeded_and_reweights_retained_edges(self):
        nodes=tuple((i,0,0) for i in range(20))
        edges=tuple(GraphEdge(i,j) for i in range(20) for j in range(i+1,20))
        graph=VoxelGraph(nodes,edges)
        sampler=SpielmanSpectralSparsifier()
        first=sampler.sparsify(graph,epsilon=0.95,failure_probability=0.9,seed=19)
        second=sampler.sparsify(graph,epsilon=0.95,failure_probability=0.9,seed=19)
        self.assertEqual(first.sampled_edges,second.sampled_edges)
        self.assertLessEqual(first.retained_edges,first.original_edges)
        self.assertEqual(first.graph.vertex_count,20)
        self.assertTrue(all(edge.weight>0 for edge in first.graph.edges))
        self.assertTrue(all(0<sample[3]<=1 for sample in first.sampled_edges))

    def test_sparsifier_rejects_oversized_exact_cpu_graph(self):
        graph=VoxelGraph(tuple((i,0,0) for i in range(5)),tuple(GraphEdge(i,i+1) for i in range(4)))
        with self.assertRaises(ValueError):
            SpielmanSpectralSparsifier(max_vertices=4).sparsify(graph)


class EngineBridgeContractTests(unittest.TestCase):
    def test_engine_registry_and_payload_are_portable(self):
        self.assertTrue({"unity","unreal","godot","bevy","o3de","flax","stride","unigine","ogre","source2","cryengine","roblox","babylonjs","threejs","playcanvas","cocos","defold","jmonkeyengine","panda3d","generic"}.issubset(set(supported_engines())))
        grid=SparseVoxelGrid(chunk_size=8)
        grid.set_voxel(0,0,0,513)
        payload=engine_payload(grid,"unity")
        self.assertEqual(payload["schema"],"sambu.engine_voxels.v1")
        self.assertEqual(payload["chunks"][0]["cell_stride_bytes"],5)
        self.assertEqual(payload["surface_mesh"]["triangle_count"],12)

    def test_unknown_engine_fails_clearly(self):
        with self.assertRaises(ValueError):
            engine_payload(SparseVoxelGrid(),"unknown-engine")


if __name__=="__main__":
    unittest.main()
