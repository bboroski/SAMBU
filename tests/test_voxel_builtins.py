from __future__ import annotations
import unittest
from sambu.interpreter import execute


class VoxelLanguageTests(unittest.TestCase):
    def run_sambu(self, source: str) -> list[str]:
        output=[]
        execute(source, output=output.append)
        return output

    def test_grid_mutation_mesh_and_octree(self):
        out=self.run_sambu(
            "let world = voxel_grid(16, 100)\n"
            "voxel_set(world, 0, 0, 0, 3)\n"
            "voxel_set(world, 1, 0, 0, 3)\n"
            "let mesh = voxel_mesh(world)\n"
            "let tree = voxel_octree(world)\n"
            "print(voxel_count(world))\nprint(mesh.face_count)\n"
            "print(mesh.triangle_count)\nprint(voxel_octree_get(tree, 1, 0, 0))\n"
            "print(voxel_get(world, 5, 0, 0))"
        )
        self.assertEqual(out,["2","10","20","3","null"])

    def test_frame_budget_and_chunks(self):
        out=self.run_sambu(
            "let world = voxel_grid(8)\n"
            "voxel_set(world, 0, 0, 0)\n"
            "voxel_set(world, 20, 0, 0)\n"
            "let frame = voxel_frame_plan(1, world, [0, 0, 0], 1)\n"
            "print(count(frame.selected_chunks))\n"
            "print(count(frame.deferred_chunks))\n"
            "print(count(voxel_chunks(world)))"
        )
        self.assertEqual(out,["1","1","2"])

    def test_raycast_and_engine_export(self):
        out=self.run_sambu(
            "let world = voxel_grid()\n"
            "voxel_set(world, 2, 0, 0, 9)\n"
            "let hit = voxel_raycast(world, [0.5, 0.5, 0.5], [1, 0, 0])\n"
            "let data = voxel_export(world, \\"unity\\")\n"
            "print(hit.material)\nprint(hit.distance)\nprint(len(data) > 0)"
        )
        self.assertEqual(out,["9","1.5","true"])

    def test_spectral_laplacian_and_sparsification(self):
        out=self.run_sambu(
            "let world = voxel_grid()\n"
            "voxel_set(world, 0, 0, 0)\n"
            "voxel_set(world, 1, 0, 0)\n"
            "voxel_set(world, 2, 0, 0)\n"
            "let profile = voxel_spectral_profile(world)\n"
            "let solved = voxel_solve_field(profile, [1, 0, -1])\n"
            "let sparse = voxel_sparsify(profile, 50%, 7)\n"
            "print(profile.vertex_count)\nprint(profile.edge_count)\n"
            "print(solved.values[0])\nprint(sparse.retained_edges)"
        )
        self.assertEqual(out,["3","2","1","2"])

    def test_voxel_grid_limits(self):
        with self.assertRaises(ValueError):
            execute("voxel_grid(0)")
        with self.assertRaises(ValueError):
            execute("voxel_grid(16, 0)")


if __name__ == "__main__":
    unittest.main()
