from __future__ import annotations

import unittest

from sambu.filtering import FilterConfigurationError, FilteringEngine
from sambu.interpreter import execute
from sambu.values import LENGTH, Quantity, Record


class CoqFilteringTests(unittest.TestCase):
    def run_sambu(self, source: str):
        output: list[str] = []
        result = execute(source, output=output.append)
        return result, output

    def test_filter_keeps_matches_and_rejections_in_input_order(self):
        _, output = self.run_sambu("""
let people = [
  ["Ada", 31, "active"],
  ["Bo", 16, "pending"],
  ["Cy", 24, "active"],
  ["Dee", 42, "blocked"]
]
let result = coq_filter(people, [
  ["1", "gte", 18],
  ["2", "eq", "active"]
])
print(result.input_count)
print(result.matched_count)
print(result.rejected_count)
print(result.items[0][0])
print(result.items[1][0])
print(result.rejected[0][0])
print(result.execution)
print(result.mutated_input)
""")
        self.assertEqual(
            output,
            ["4", "2", "2", "Ada", "Cy", "Bo", "in_memory_pure_filter", "false"],
        )

    def test_all_any_and_reusable_rule(self):
        _, output = self.run_sambu("""
let item = ["Ada", 31, "active"]
let status_rule = coq_rule("2", "eq", "active")
print(coq_match(item, [["1", "gte", 18], status_rule], "all"))
print(coq_match(item, [["1", "lt", 18], status_rule], "any"))
""")
        self.assertEqual(output, ["true", "true"])

    def test_explain_reports_every_rule_and_missing_path(self):
        _, output = self.run_sambu("""
let result = coq_explain(["Bo", 16], [
  ["1", "gte", 18],
  ["3", "exists"],
  ["0", "starts_with", "B"]
], "all")
print(result.matched)
print(result.rules_checked)
print(result.results[0].reason)
print(result.results[1].reason)
print(result.results[2].matched)
""")
        self.assertEqual(output, ["false", "3", "not_matched", "path_missing", "true"])

    def test_pipeline_is_sequential_and_reports_each_stage(self):
        _, output = self.run_sambu("""
let values = [
  ["Ada", 31, "active"],
  ["Bo", 16, "pending"],
  ["Cy", 24, "review"],
  ["Dee", 42, "blocked"]
]
let result = coq_pipeline(values, [
  ["all", [["1", "gte", 18]]],
  ["any", [["2", "eq", "active"], ["2", "eq", "review"]]]
])
print(result.input_count)
print(result.output_count)
print(result.stages[0].output_count)
print(result.stages[1].output_count)
print(result.items[0][0])
print(result.items[1][0])
print(result.execution)
""")
        self.assertEqual(
            output,
            ["4", "2", "3", "2", "Ada", "Cy", "in_memory_pure_pipeline"],
        )

    def test_text_operators_are_case_insensitive_when_requested(self):
        _, output = self.run_sambu("""
print(coq_match(["Ada", "Active User"], [
  ["1", "icontains", "ACTIVE"],
  ["1", "istarts_with", "active"]
]))
""")
        self.assertEqual(output, ["true"])

    def test_between_and_collection_length_operators(self):
        _, output = self.run_sambu("""
print(coq_match(["Ada", [1, 2, 3], 7], [
  ["2", "between", [5, 9]],
  ["1", "length_eq", 3]
]))
""")
        self.assertEqual(output, ["true"])

    def test_empty_input_is_valid_and_is_not_mutated(self):
        _, output = self.run_sambu("""
let data = []
let result = coq_filter(data, [["0", "eq", "x"]])
print(result.input_count)
print(result.matched_count)
print(count(data))
""")
        self.assertEqual(output, ["0", "0", "0"])

    def test_record_paths_and_quantity_comparisons(self):
        engine = FilteringEngine()
        profile = Record({
            "age": 21,
            "verified": None,
            "height": Quantity(1.8, LENGTH),
        })
        rules = [
            ["age", "gte", 18],
            ["verified", "is_null"],
            ["height", "gt", Quantity(1.7, LENGTH)],
        ]
        result = engine.filter([profile], rules)
        self.assertEqual(result.get("matched_count"), 1)
        self.assertIs(result.get("items")[0], profile)

    def test_missing_and_null_are_distinct(self):
        engine = FilteringEngine()
        item = Record({"present": None})
        missing = engine.evaluate(item, [["absent", "missing"]])
        present = engine.evaluate(item, [["present", "exists"]])
        null_value = engine.evaluate(item, [["present", "is_null"]])
        self.assertTrue(missing.matched)
        self.assertTrue(present.matched)
        self.assertTrue(null_value.matched)

    def test_mismatched_types_fail_closed(self):
        _, output = self.run_sambu("""
let item = ["Ada", "thirty"]
let result = coq_explain(item, [["1", "gte", 18]])
print(result.matched)
print(result.results[0].reason)
""")
        self.assertEqual(output, ["false", "type_mismatch"])

    def test_invalid_operators_paths_and_empty_rules_are_rejected(self):
        with self.assertRaisesRegex(FilterConfigurationError, "unsupported filter operator"):
            execute('coq_match(["Ada"], [["0", "eval", "1 + 1"]])')
        with self.assertRaisesRegex(FilterConfigurationError, "dunder"):
            execute('coq_match(["Ada"], [["__class__", "exists"]])')
        with self.assertRaisesRegex(FilterConfigurationError, "1 to 256"):
            execute('coq_match(["Ada"], [])')

    def test_invalid_between_and_membership_rules_are_rejected(self):
        with self.assertRaisesRegex(FilterConfigurationError, "minimum cannot exceed maximum"):
            execute('coq_match([7], [["0", "between", [9, 2]]])')
        with self.assertRaisesRegex(TypeError, "array of candidate values"):
            execute('coq_match([7], [["0", "in", 7]])')

    def test_length_rejects_negative_or_fractional_bounds(self):
        with self.assertRaises(FilterConfigurationError):
            execute('coq_match(["abc"], [["0", "length_eq", -1]])')
        with self.assertRaises(FilterConfigurationError):
            execute('coq_match(["abc"], [["0", "length_eq", 1.5]])')

    def test_limits_are_explicit(self):
        engine = FilteringEngine()
        with self.assertRaisesRegex(FilterConfigurationError, "at most 100,000"):
            engine.filter([None] * 100_001, [["$", "exists"]])
        with self.assertRaisesRegex(FilterConfigurationError, "at most 64"):
            engine.pipeline([], [["all", [["$", "exists"]]]] * 65)


if __name__ == "__main__":
    unittest.main()
