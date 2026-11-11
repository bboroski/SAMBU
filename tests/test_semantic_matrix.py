import math
import unittest

from sambu.semantic_matrix import (
    SemanticMatrixError, expand_relations, multiply,
)


class SemanticMatrixTests(unittest.TestCase):
    def test_matrix_multiplication(self):
        self.assertEqual(
            multiply(((1, 2), (3, 4)), ((5, 6), (7, 8))),
            ((19.0, 22.0), (43.0, 50.0)),
        )

    def test_expansion_discovers_two_hop_relation(self):
        direct = ((0, 1, 0), (0, 0, 1), (0, 0, 0))
        expanded = expand_relations(direct, depth=2, damping=0.5)
        self.assertGreater(expanded[0][2], 0.0)
        self.assertEqual(expanded[0][0], 0.0)
        self.assertAlmostEqual(sum(expanded[0]), 1.0)

    def test_empty_row_remains_empty(self):
        expanded = expand_relations(((0, 0), (1, 0)), depth=3)
        self.assertEqual(expanded[0], (0.0, 0.0))

    def test_rejects_non_square_and_non_finite(self):
        with self.assertRaises(SemanticMatrixError):
            multiply(((1, 2),), ((1,),))
        with self.assertRaises(SemanticMatrixError):
            expand_relations(((0, float("nan")), (0, 0)))

    def test_rejects_overflowing_matrix_products(self):
        cases = (
            (((1e308,),), ((2.0,),)),
            (((1.0, 1.0),), ((1e308,), (1e308,))),
        )
        for left, right in cases:
            with self.subTest(left=left, right=right):
                with self.assertRaises(SemanticMatrixError):
                    multiply(left, right)

    def test_normalizes_large_finite_rows_without_overflow(self):
        expanded = expand_relations(((1e308, 1e308), (0.0, 1.0)), depth=1)
        self.assertEqual(expanded[0], (0.0, 1.0))
        self.assertTrue(all(math.isfinite(value) for row in expanded for value in row))

    def test_resource_bounds(self):
        with self.assertRaises(SemanticMatrixError):
            expand_relations(((0,),), depth=7)
        with self.assertRaises(SemanticMatrixError):
            expand_relations(((0,),), damping=1.5)


if __name__ == "__main__":
    unittest.main()
