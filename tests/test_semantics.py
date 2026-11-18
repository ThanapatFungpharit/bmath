import unittest

from helpers import SAMPLES, assignments


class PolynomialAgreesWithEvaluation(unittest.TestCase):
    def test_polynomial_matches_truth_value_everywhere(self) -> None:
        for expr in SAMPLES:
            poly = expr.to_polynomial()
            for assignment in assignments(expr.variables()):
                with self.subTest(expr=str(expr), assignment=assignment):
                    self.assertEqual(
                        poly.evaluate(assignment), int(expr.evaluate(assignment))
                    )


if __name__ == "__main__":
    unittest.main()
