from collections.abc import Mapping
from fractions import Fraction

type Monomial = frozenset[str]
"""A product of distinct variables, given by their names (x*x = x)."""

type Coefficient = int | float | Fraction
"""A coefficient. Other ``numbers.Number`` types are also accepted at runtime."""

type Terms = Mapping[Monomial, Coefficient]
"""A polynomial as a mapping of monomial -> coefficient."""
