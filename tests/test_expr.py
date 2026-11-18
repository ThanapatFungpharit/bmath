import unittest
from dataclasses import FrozenInstanceError

from bmath import (
    AND,
    FALSE,
    OR,
    TRUE,
    BooleanConstant,
    BooleanVariable,
    Iff,
    IfThen,
    Not,
)
from helpers import x, y, z


class Construction(unittest.TestCase):
    def test_operators_build_connectives(self) -> None:
        self.assertEqual(x & y, AND(x, y))
        self.assertEqual(x | y, OR(x, y))
        self.assertEqual(~x, Not(x))
        self.assertEqual(x >> y, IfThen(x, y))
        with self.assertRaises(TypeError):
            x ^ y  # type: ignore[operator]  # XOR was removed

    def test_invalid_operands_rejected(self) -> None:
        # Deliberately ill-typed: these check the runtime validation.
        for build in (
            lambda: AND(x, True),  # type: ignore[arg-type]
            lambda: Not(None),  # type: ignore[arg-type]
            lambda: x & 1,  # type: ignore[operator]
            lambda: Iff(x, "y"),  # type: ignore[arg-type]
            lambda: BooleanConstant(1),  # type: ignore[arg-type]
        ):
            with self.assertRaises(TypeError):
                build()

    def test_invalid_variable_names_rejected(self) -> None:
        with self.assertRaises(TypeError):
            BooleanVariable(42)  # type: ignore[arg-type]
        for name in ("", "2", "a*b", "is raining", "&", "\u03b1"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                BooleanVariable(name)

    def test_immutable_and_hashable(self) -> None:
        with self.assertRaises(FrozenInstanceError):
            x.symbol = "q"  # type: ignore[misc]
        self.assertEqual(len({x & y, AND(x, y), y & x}), 2)


class Rendering(unittest.TestCase):
    def test_str(self) -> None:
        cases = {
            x: "x",
            ~x: "~x",
            ~(x & y): "~(x & y)",
            (x | y) >> ~z: "(x | y) -> ~z",
            Iff(x, y): "x <=> y",
            TRUE: "T",
            FALSE & ~TRUE: "F & ~T",
            x >> (y >> z): "x -> (y -> z)",
        }
        for expr, text in cases.items():
            with self.subTest(text=text):
                self.assertEqual(str(expr), text)


class Structure(unittest.TestCase):
    def test_variables(self) -> None:
        self.assertEqual((x & ~y | TRUE).variables(), {"x", "y"})
        self.assertEqual(TRUE.variables(), frozenset())

    def test_children(self) -> None:
        self.assertEqual((x & y).children(), (x, y))
        self.assertEqual(x.children(), ())

    def test_substitute(self) -> None:
        expr = (x & y) | z
        self.assertEqual(expr.substitute({"z": x | y}), (x & y) | (x | y))
        self.assertEqual(expr.substitute({"x": True}), (TRUE & y) | z)
        self.assertEqual(expr.substitute({}), expr)
        with self.assertRaises(TypeError):
            expr.substitute({"x": 1})  # type: ignore[dict-item]

    def test_evaluate(self) -> None:
        expr = ~Iff(x >> y, z)  # true when they differ
        self.assertTrue(expr.evaluate({"x": True, "y": False, "z": True}))
        with self.assertRaises(KeyError):
            expr.evaluate({"x": False})  # y and z missing, even though x -> y is true


if __name__ == "__main__":
    unittest.main()
