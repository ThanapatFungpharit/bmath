import sys
import unittest

from bmath import AND, TRUE, BooleanExpr, BooleanVariable, Iff, Not, is_tautology
from helpers import x, y

# Far beyond the default recursion limit, so any recursive traversal fails.
DEPTH = max(20 * sys.getrecursionlimit(), 20_000)


def deep_chain(depth: int = DEPTH) -> BooleanExpr:
    """x wrapped in `depth` connectives of every kind."""
    expr: BooleanExpr = x
    for i in range(depth):
        match i % 5:
            case 0:
                expr = Not(expr)
            case 1:
                expr = expr & y
            case 2:
                expr = expr | x
            case 3:
                expr = ~Iff(expr, y)
            case 4:
                expr = Iff(expr, x) >> y
    return expr


class DeepExpressions(unittest.TestCase):
    def setUp(self) -> None:
        self.expr = deep_chain()

    def test_polynomial_matches_evaluation(self) -> None:
        poly = self.expr.to_polynomial()
        for values in ({"x": a, "y": b} for a in (False, True) for b in (False, True)):
            self.assertEqual(poly.evaluate(values), int(self.expr.evaluate(values)))

    def test_structure(self) -> None:
        self.assertEqual(self.expr.variables(), {"x", "y"})
        self.assertIs(self.expr.substitute({}), self.expr)
        self.assertNotEqual(self.expr.substitute({"y": True}), self.expr)
        self.assertEqual(deep_chain(), self.expr)
        self.assertEqual(hash(deep_chain()), hash(self.expr))
        is_tautology(self.expr)

    def test_rendering(self) -> None:
        small = deep_chain(5)
        self.assertEqual(str(small), "(~(((~x & y) | x) <=> y) <=> x) -> y")
        text = str(self.expr)
        self.assertTrue(text.endswith(" -> y"))
        self.assertEqual(text.count("("), text.count(")"))
        self.assertTrue(repr(self.expr).startswith("IfThen(Iff("))

    def test_nested_not(self) -> None:
        expr: BooleanExpr = x
        for _ in range(DEPTH):
            expr = Not(expr)
        self.assertEqual(str(expr), "~" * DEPTH + "x")
        self.assertEqual(expr.to_polynomial(), x.to_polynomial())


class SharedSubexpressions(unittest.TestCase):
    def test_shared_nodes_are_visited_once(self) -> None:
        # As a tree this has 2**64 leaves; shared, it is 65 nodes.
        expr: BooleanExpr = x
        for _ in range(64):
            expr = AND(expr, expr)
        self.assertEqual(expr.to_polynomial(), x.to_polynomial())
        self.assertTrue(expr.evaluate({"x": True}))
        self.assertEqual(expr.variables(), {"x"})
        self.assertEqual(expr.substitute({"x": TRUE}).to_polynomial(), 1)
        self.assertEqual(expr, AND(*expr.children()))

    def test_variable_substitution_with_bool_reuses_constants(self) -> None:
        self.assertIs(BooleanVariable("q").substitute({"q": True}), TRUE)


if __name__ == "__main__":
    unittest.main()
