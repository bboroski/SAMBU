from __future__ import annotations

import unittest

from sambu.ecosystems import (
    ImprintedClosure,
    biometric_taxonomy_sort,
    countercurrent_sync,
    v_vector_stream,
    wetland_ecosystem_loop,
)
from sambu.interpreter import execute


class EcosystemPrimitiveTests(unittest.TestCase):
    def run_sambu(self, source: str) -> list[str]:
        output: list[str] = []
        execute(source, output=output.append)
        return output

    def test_imprint_closure_freezes_first_context_for_every_invocation(self):
        output = self.run_sambu('''
fn react(context, amount) { return context.resistance_after + amount }
let state = capture_node("rival", "flock", 30, 5)
let bound = imprint_closure(react, state)
print(bound(2))
print(bound(3))
''')
        self.assertEqual(output, ["27", "28"])

    def test_imprint_context_is_detached_and_recursively_immutable(self):
        source = {"nested": [1, 2]}
        closure = ImprintedClosure(lambda args: args[0]["nested"][0], source)
        source["nested"][0] = 99
        self.assertEqual(closure([]), 1)
        with self.assertRaises(TypeError):
            closure.context["nested"].append(3)
        with self.assertRaises(TypeError):
            closure.context["nested"][0] = 4
        with self.assertRaises(TypeError):
            closure.context["nested"] = []

    def test_imprint_closure_rejects_unsupported_or_cyclic_context(self):
        cyclic: list[object] = []
        cyclic.append(cyclic)
        with self.assertRaises(ValueError):
            ImprintedClosure(lambda args: None, cyclic)
        with self.assertRaises(TypeError):
            ImprintedClosure(lambda args: None, object())

    def test_v_vector_stream_partitions_every_index_once(self):
        plan = v_vector_stream([19, 4, 0.6, 1])
        assignments = plan.get("assignments")
        ranges = [(item.get("start"), item.get("stop")) for item in assignments]
        self.assertEqual(plan.get("covered_items"), 19)
        self.assertEqual(plan.get("phase"), 1)
        self.assertEqual(ranges[0], (0, 12))
        covered = [index for start, stop in ranges for index in range(start, stop)]
        self.assertEqual(covered, list(range(19)))
        self.assertEqual(len({item.get("worker") for item in assignments}), 4)
        self.assertTrue(plan.get("plan_only"))
        self.assertFalse(plan.get("workers_started"))

    def test_v_vector_stream_handles_single_worker_and_empty_input(self):
        one = v_vector_stream([7, 1])
        empty = v_vector_stream([0, 3])
        self.assertEqual(one.get("assignments")[0].get("count"), 7)
        self.assertEqual(empty.get("covered_items"), 0)
        self.assertEqual(len(empty.get("assignments")), 3)

    def test_v_vector_stream_rejects_invalid_bounds(self):
        with self.assertRaises(ValueError):
            v_vector_stream([10, 2, 1.1])
        with self.assertRaises(ValueError):
            v_vector_stream([10, 0])
        with self.assertRaises(ValueError):
            v_vector_stream([10, 2.5])

    def test_countercurrent_sync_obeys_capacity_and_transfer_budgets(self):
        plan = countercurrent_sync([
            ["hot-a", "hot-b"], ["cold-a", "cold-b", "cold-c"], 3, 1, 1
        ])
        self.assertEqual(plan.get("hot_after"), ["hot-a", "hot-b", "cold-a"])
        self.assertEqual(plan.get("cold_after"), ["cold-b", "cold-c"])
        self.assertEqual(plan.get("promoted_count"), 1)
        self.assertEqual(plan.get("demoted_count"), 0)
        self.assertTrue(plan.get("capacity_satisfied"))
        self.assertFalse(plan.get("storage_transfer_executed"))

    def test_countercurrent_sync_exposes_unmet_eviction_pressure(self):
        plan = countercurrent_sync([["a", "b", "c", "d"], [], 2, 2, 1])
        self.assertEqual(plan.get("demoted_count"), 1)
        self.assertFalse(plan.get("capacity_satisfied"))
        self.assertEqual(plan.get("pending_evictions"), 1)

    def test_countercurrent_sync_rejects_negative_budget(self):
        with self.assertRaises(ValueError):
            countercurrent_sync([[], [], 2, -1, 0])

    def test_biometric_taxonomy_sort_builds_deterministic_trait_tree(self):
        result = biometric_taxonomy_sort([
            [["duck", 7], ["goose", 3], ["chicken", 1], ["loon", 5], ["swan", 3]],
            ["webbed", "waterfowl", "diver"],
        ])
        self.assertEqual(result.get("taxa_order"), ["chicken", "duck", "goose", "loon", "swan"])
        self.assertFalse(result.get("phylogeny_inferred"))

        def collect(node):
            if node.get("kind") == "leaf":
                return list(node.get("taxa"))
            return collect(node.get("present")) + collect(node.get("absent"))

        leaves = collect(result.get("root"))
        self.assertEqual(sorted(leaves), result.get("taxa_order"))
        self.assertEqual(len(leaves), len(set(leaves)))

    def test_biometric_taxonomy_sort_rejects_invalid_masks_and_names(self):
        with self.assertRaises(ValueError):
            biometric_taxonomy_sort([[["duck", 4]], ["webbed", "diving"]])
        with self.assertRaises(ValueError):
            biometric_taxonomy_sort([[["duck", 1], ["duck", 0]], ["webbed"]])
        with self.assertRaises(ValueError):
            biometric_taxonomy_sort([[["duck", 1]], ["webbed", "webbed"]])

    def test_wetland_loop_recommends_bounded_scale_up(self):
        plan = wetland_ecosystem_loop([900, 100, 4, 2, 12, 0.75])
        self.assertEqual(plan.get("desired_workers"), 12)
        self.assertEqual(plan.get("worker_delta"), 8)
        self.assertEqual(plan.get("action"), "scale_up")
        self.assertAlmostEqual(plan.get("projected_utilization"), 0.75)
        self.assertFalse(plan.get("workers_started_or_stopped"))
        self.assertFalse(plan.get("gc_modified"))

    def test_wetland_loop_reports_capacity_ceiling(self):
        plan = wetland_ecosystem_loop([1200, 100, 4, 2, 10, 0.75])
        self.assertEqual(plan.get("desired_workers"), 10)
        self.assertTrue(plan.get("capacity_limited"))
        self.assertEqual(plan.get("resource_pressure"), "over_capacity")

    def test_wetland_loop_rejects_inconsistent_worker_limits(self):
        with self.assertRaises(ValueError):
            wetland_ecosystem_loop([100, 10, 5, 6, 4])
        with self.assertRaises(ValueError):
            wetland_ecosystem_loop([100, 10, 5, 0, 4])

    def test_all_five_functions_are_available_through_exact_name_aliases(self):
        output = self.run_sambu('''
fn echo(context, value) { return value }
let c = ImprintClosure(echo, 7)
let v = V_VectorStream(4, 2)
let s = CountercurrentSync([1], [2], 2, 1, 0)
let t = BiometricTaxonomySort([["bird", 1]], ["feathered"])
let w = WetlandEcosystemLoop(50, 100, 1, 1, 3)
print(c(9))
print(v.covered_items)
print(s.capacity_satisfied)
print(t.phylogeny_inferred)
print(w.action)
''')
        self.assertEqual(output, ["9", "4", "true", "false", "steady"])


if __name__ == "__main__":
    unittest.main()
