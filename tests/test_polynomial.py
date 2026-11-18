import unittest
from fractions import Fraction

from bmath import Polynomial
from bmath.polynomial import nonzero_point

P = Polynomial
x, y = P.variable("x"), P.variable("y")


class Arithmetic(unittest.TestCase):
    def test_boolean_algebra_rules(self) -> None:
        self.assertEqual(x * x, x)
        self.assertEqual(x - x, 0)
        self.assertEqual(~x, 1 - x)
        self.assertEqual(x * ~x, 0)

    def test_plain_numbers(self) -> None:
        self.assertEqual(x + 1, 1 + x)
        self.assertEqual(2 * x, x + x)
        self.assertEqual(x * Fraction(1, 2) + x * Fraction(1, 2), x)
        with self.assertRaises(TypeError):
            x + "a"  # type: ignore[operator]

    def test_equality(self) -> None:
        self.assertEqual(x + y, y + x)
        self.assertNotEqual(x, y)
        self.assertNotEqual(x, "x")
        self.assertEqual(P(), 0)


class Inspection(unittest.TestCase):
    def test_variables(self) -> None:
        self.assertEqual((x * y + 1).variables(), {"x", "y"})
        self.assertEqual(P.constant(3).variables(), frozenset())

    def test_evaluate(self) -> None:
        poly = 1 - x + x * y
        self.assertEqual(poly.evaluate({"x": True, "y": False}), 0)
        self.assertEqual(poly.evaluate({"x": 1, "y": 1}), 1)

    def test_nonzero_point(self) -> None:
        self.assertIsNone(nonzero_point(P()))
        poly = x * y - x  # zero at x=0 and at x=y=1; nonzero only at x=1, y=0
        point = nonzero_point(poly)
        assert point is not None
        self.assertNotEqual(poly.evaluate({"x": "x" in point, "y": "y" in point}), 0)


class Formatting(unittest.TestCase):
    def test_str(self) -> None:
        rain, wind = P.variable("rain"), P.variable("wind")
        v0, v1, v2, v10 = (P.variable(f"v{i}") for i in (0, 1, 2, 10))
        cases = {
            "0": P(),
            "-3": P.constant(-3),
            "3 - x + 2xy": 2 * x * y - x + 3,
            "-x": -x,
            "x/3": x * Fraction(1, 3),
            "-2xy/3": x * y * Fraction(-2, 3),
            "0.5x + 2y": x * 0.5 + y * 2.0,
            "-rain + 2*rain*wind": 2 * rain * wind - rain,
            "rain*x": rain * x,
            "v0 + v2 + v10 - v0*v1*v10": v0 + v2 + v10 - v0 * v1 * v10,
        }
        for text, poly in cases.items():
            with self.subTest(text=text):
                self.assertEqual(str(poly), text)

    def test_invalid_names(self) -> None:
        for name in ("", "2", "a*b"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                P.variable(name)


if __name__ == "__main__":
    unittest.main()
