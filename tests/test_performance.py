"""Tests for the fast paths: bitmask monomials, dense products, caching and
early exits. Each fast path must give exactly the slow path's answer."""

import pickle
import random
import time
import unittest
from fractions import Fraction
from functools import reduce

from bmath import (
    AND,
    OR,
    BooleanExpr,
    BooleanVariable,
    Iff,
    Polynomial,
    equivalent,
    is_contradiction,
    is_satisfiable,
    is_tautology,
)
from bmath.polynomial import dense
from helpers import SAMPLES, assignments, x, y


def sparse_product(a: Polynomial, b: Polynomial) -> Polynomial:
    """Term-by-term product through the public API, for comparison."""
    total = Polynomial()
    for ma, ca in a.terms.items():
        for mb, cb in b.terms.items():
            total = total + Polynomial({ma | mb: ca * cb})
    return total


def random_polynomial(
    rng: random.Random, names: list[str], count: int, fractions: bool = False
) -> Polynomial:
    terms: dict[frozenset[str], int | Fraction] = {}
    for _ in range(count):
        monomial = frozenset(n for n in names if rng.random() < 0.5)
        value = rng.randint(-3, 3)
        terms[monomial] = Fraction(value, rng.randint(1, 4)) if fractions else value
    return Polynomial(terms)


def or_chain(names: list[str]) -> BooleanExpr:
    variables: list[BooleanExpr] = [BooleanVariable(n) for n in names]
    return reduce(OR, variables)


class DenseProduct(unittest.TestCase):
    def test_matches_term_by_term(self) -> None:
        rng = random.Random(7)
        # Non-contiguous variables (interleaved with unused, already-registered
        # ones) exercise the general index mapping, not just the shift.
        registered = [f"d{i}" for i in range(20)]
        for name in registered:
            Polynomial.variable(name)
        for names in (registered[:9], registered[::2], registered[3:17:3]):
            for fractions in (False, True):
                a = random_polynomial(rng, names, 200, fractions)
                b = random_polynomial(rng, names, 150, fractions)
                support = 0
                for poly in (a, b):
                    support |= poly._variable_mask()
                product = Polynomial._from_masks(
                    dense.multiply(a._terms, b._terms, support)
                )
                with self.subTest(names=names, fractions=fractions):
                    self.assertEqual(product, sparse_product(a, b))
                    self.assertEqual(a * b, product)

    def test_floats_never_take_the_table_path(self) -> None:
        a = Polynomial({frozenset(): 0.1})
        self.assertFalse(dense.is_exact(a._terms))

    def test_or_and_not_or_is_fast(self) -> None:
        # Both sides are dense over the same 14 variables: 16383^2 (about 2.7e8)
        # term products term by term, about 0.1 s with tables.
        names = [f"q{i}" for i in range(14)]
        left = or_chain(names)
        right = or_chain(names[::-1])
        start = time.perf_counter()
        self.assertTrue(is_contradiction(left & ~right))
        self.assertLess(time.perf_counter() - start, 10)


class PolynomialValues(unittest.TestCase):
    def test_immutable_terms(self) -> None:
        poly = x.to_polynomial()
        with self.assertRaises(TypeError):
            poly.terms[frozenset()] = 1  # type: ignore[index]

    def test_pickle_by_name(self) -> None:
        poly = 2 * Polynomial.variable("x") * Polynomial.variable("y") - 1
        self.assertEqual(pickle.loads(pickle.dumps(poly)), poly)
        self.assertEqual(dict(poly.terms), {frozenset({"x", "y"}): 2, frozenset(): -1})

    def test_missing_variable_raises(self) -> None:
        with self.assertRaises(KeyError):
            (x & y).to_polynomial().evaluate({"x": True})


class Caching(unittest.TestCase):
    def test_result_is_cached(self) -> None:
        expr = (x | y) & ~x
        self.assertIs(expr.to_polynomial(), expr.to_polynomial())

    def test_cached_subexpressions_are_reused(self) -> None:
        inner = Iff(BooleanVariable("c0"), BooleanVariable("c1"))
        poly = inner.to_polynomial()
        outer = inner | BooleanVariable("c2")
        self.assertEqual(
            outer.to_polynomial(),
            poly + Polynomial.variable("c2") - poly * Polynomial.variable("c2"),
        )
        # substitute keeps unchanged sub-expressions, and their caches.
        self.assertIs(outer.substitute({"c2": True}).children()[0], inner)
        self.assertIs(inner._cached_polynomial, poly)


class EarlyExit(unittest.TestCase):
    def test_refuted_without_polynomial(self) -> None:
        # OR of 40 variables has 2^40 - 1 terms; a probe settles it instead.
        expr = or_chain([f"e{i}" for i in range(40)])
        self.assertFalse(is_tautology(expr))
        self.assertTrue(is_satisfiable(expr))
        self.assertFalse(equivalent(expr, BooleanVariable("e0")))
        self.assertIsNone(expr._cached_polynomial)

    def test_split_conjunction_stops_at_first_failure(self) -> None:
        big = or_chain([f"s{i}" for i in range(40)])
        self.assertFalse(is_tautology(AND(x & ~x, big)))
        self.assertIsNone(big._cached_polynomial)

    def test_shared_subexpressions_are_checked_once(self) -> None:
        expr: BooleanExpr = x | ~x
        for _ in range(64):
            expr = AND(expr, expr)  # 2^64 paths, 66 distinct nodes
        self.assertTrue(is_tautology(expr))
        self.assertFalse(is_contradiction(expr))

    def test_answers_match_truth_tables(self) -> None:
        for expr in SAMPLES:
            table = [expr.evaluate(a) for a in assignments(expr.variables())]
            for wrapped in (expr, ~expr, expr >> x, x >> expr, OR(expr, expr)):
                rows = [wrapped.evaluate(a) for a in assignments(wrapped.variables())]
                with self.subTest(expr=str(wrapped)):
                    self.assertEqual(is_tautology(wrapped), all(rows))
                    self.assertEqual(is_contradiction(wrapped), not any(rows))
            self.assertEqual(is_tautology(expr), all(table))


if __name__ == "__main__":
    unittest.main()
