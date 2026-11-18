import unittest
from itertools import product

from bmath import (
    TRUE,
    BooleanVariable,
    Iff,
    Row,
    TruthTable,
    redundant_variables,
    truth_table,
)
from helpers import SAMPLES, x, y, z


class TruthTables(unittest.TestCase):
    def test_example(self) -> None:
        self.assertEqual(str(truth_table((x & y) | x)), "x y result\n1 * 1\n0 * 0")

    def test_full_table_when_every_variable_matters(self) -> None:
        table = truth_table(x | y)
        self.assertEqual(table.variables, ("x", "y"))
        self.assertEqual(
            table.rows,
            (
                Row((True, True), True),
                Row((True, False), True),
                Row((False, True), True),
                Row((False, False), False),
            ),
        )

    def test_constants_and_contradictions(self) -> None:
        self.assertEqual(str(truth_table(TRUE)), "result\n1")
        self.assertEqual(str(truth_table(x & ~x)), "x result\n* 0")

    def test_columns_align_and_use_math_names(self) -> None:
        v0, v10 = BooleanVariable("v0"), BooleanVariable("v10")
        self.assertEqual(
            str(truth_table(v10 & v0)).splitlines()[:2], ["v0 v10 result", "1  1   1"]
        )

    def test_rows_match_evaluation(self) -> None:
        for expr in [*SAMPLES, ~Iff(x, y) | (z & ~z)]:
            table = truth_table(expr)
            redundant = redundant_variables(expr)
            with self.subTest(expr=str(expr)):
                self.assertEqual(
                    len(table.rows), 2 ** (len(table.variables) - len(redundant))
                )
                for inputs, result in table.rows:
                    marked = {n for n, v in zip(table.variables, inputs) if v is None}
                    self.assertEqual(marked, redundant)
                    # Every way of filling in the * columns gives the same result.
                    for fill in product((False, True), repeat=len(marked)):
                        point = dict(zip(sorted(marked), fill))
                        assignment = {
                            n: point[n] if v is None else v
                            for n, v in zip(table.variables, inputs)
                        }
                        self.assertEqual(expr.evaluate(assignment), result)


class Lookup(unittest.TestCase):
    def test_get(self) -> None:
        table = truth_table((x & y) | x)
        self.assertIs(table.get({"x": True}), True)
        self.assertIs(table.get({"x": False, "y": True}), False)  # y ignored
        self.assertIs(table.get({"x": True, "zzz": False}), True)  # extra names
        self.assertIsNone(table.get({"y": True}))  # x missing
        self.assertEqual(table.get({}, "n/a"), "n/a")
        self.assertEqual((table.dependent, table.independent), (("x",), ("y",)))

    def test_getitem(self) -> None:
        table = truth_table(~Iff(x, y))
        self.assertTrue(table[{"x": True, "y": False}])
        with self.assertRaisesRegex(KeyError, "'y'"):
            table[{"x": True}]

    def test_constant_table_needs_no_variables(self) -> None:
        self.assertIs(truth_table(x | ~x).get({}), True)

    def test_matches_evaluation(self) -> None:
        for expr in SAMPLES:
            table = truth_table(expr)
            with self.subTest(expr=str(expr)):
                for values in product((False, True), repeat=len(table.variables)):
                    point = dict(zip(table.variables, values))
                    self.assertEqual(table[point], expr.evaluate(point))
                self.assertEqual(list(table), list(table.rows))
                self.assertEqual(len(table), len(table.rows))

    def test_built_by_hand(self) -> None:
        # A partial table: a missing row is a failed lookup, not an error.
        table = TruthTable(("a", "b"), (Row((True, None), False),))
        self.assertIs(table.get({"a": True}), False)
        self.assertIsNone(table.get({"a": False}))
        self.assertEqual(table, TruthTable(("a", "b"), (Row((True, None), False),)))
        self.assertEqual(len({table}), 1)  # still hashable

    def test_invalid_tables(self) -> None:
        bad = {
            "no rows": ((), ()),
            "wrong width": (("a",), (Row((True, False), True),)),
            "mixed *": (("a",), (Row((True,), True), Row((None,), False))),
            "duplicate": (("a",), (Row((True,), True), Row((True,), False))),
        }
        for reason, (variables, rows) in bad.items():
            with self.subTest(reason), self.assertRaises(ValueError):
                TruthTable(variables, rows)


if __name__ == "__main__":
    unittest.main()
