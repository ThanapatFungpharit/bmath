import unittest
from collections.abc import Iterable

from bmath import (
    BooleanExpr,
    counterexample,
    dependent_variables,
    equivalent,
    is_contradiction,
    is_satisfiable,
    is_tautology,
    redundant_variables,
    satisfying_assignment,
)
from helpers import SAMPLES, assignments, x, y, z


def truth_values(expr: BooleanExpr, names: Iterable[str] | None = None) -> list[bool]:
    names = expr.variables() if names is None else names
    return [expr.evaluate(a) for a in assignments(names)]


def depends_on(expr: BooleanExpr, name: str) -> bool:
    names = sorted(expr.variables())
    for a in assignments(names):
        if expr.evaluate({**a, name: False}) != expr.evaluate({**a, name: True}):
            return True
    return False


class AnalysisMatchesBruteForce(unittest.TestCase):
    def test_tautology_contradiction_satisfiable(self) -> None:
        for expr in SAMPLES:
            values = truth_values(expr)
            with self.subTest(expr=str(expr)):
                self.assertEqual(is_tautology(expr), all(values))
                self.assertEqual(is_contradiction(expr), not any(values))
                self.assertEqual(is_satisfiable(expr), any(values))

    def test_equivalent(self) -> None:
        for a in SAMPLES:
            for b in SAMPLES:
                names = a.variables() | b.variables()
                with self.subTest(a=str(a), b=str(b)):
                    self.assertEqual(
                        equivalent(a, b),
                        truth_values(a, names) == truth_values(b, names),
                    )

    def test_dependent_and_redundant_variables(self) -> None:
        for expr in SAMPLES:
            expected = {n for n in expr.variables() if depends_on(expr, n)}
            with self.subTest(expr=str(expr)):
                self.assertEqual(dependent_variables(expr), expected)
                self.assertEqual(redundant_variables(expr), expr.variables() - expected)

    def test_witnesses(self) -> None:
        for expr in SAMPLES:
            values = truth_values(expr)
            sat, cex = satisfying_assignment(expr), counterexample(expr)
            with self.subTest(expr=str(expr)):
                if any(values):
                    assert sat is not None
                    self.assertTrue(expr.evaluate(sat))
                    self.assertEqual(set(sat), set(expr.variables()))
                else:
                    self.assertIsNone(sat)
                if all(values):
                    self.assertIsNone(cex)
                else:
                    assert cex is not None
                    self.assertFalse(expr.evaluate(cex))

    def test_named_examples(self) -> None:
        demo = (((x | ~x) & y) & z) | z
        self.assertEqual(dependent_variables(demo), {"z"})
        self.assertEqual(redundant_variables(demo), {"x", "y"})
        self.assertTrue(is_tautology(((x >> y) & (y >> z)) >> (x >> z)))
        self.assertEqual(counterexample(x >> y), {"x": True, "y": False})


if __name__ == "__main__":
    unittest.main()
