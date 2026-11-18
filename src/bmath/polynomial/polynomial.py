from collections.abc import Mapping
from numbers import Number
from types import MappingProxyType
from typing import Any, ClassVar, Self, cast

from . import dense
from .formatting import format_terms
from .monomials import bit, mask_of, names_of
from .names import validate_variable_name
from .terms import Coefficient, Monomial, Terms

type _Masks = dict[int, Coefficient]
"""Terms keyed by monomial bitmask (see ``monomials``)."""


def _combine(left: _Masks, right: _Masks, sign: int) -> _Masks:
    """Terms of ``left + sign * right``, without zero coefficients."""
    result = dict(left)
    for monomial, coefficient in right.items():
        total = result.get(monomial, 0) + sign * coefficient
        if total:
            result[monomial] = total
        else:
            result.pop(monomial, None)
    return result


def _scalar(value: object) -> Coefficient | None:
    """``value`` if it is a plain number, otherwise None."""
    if isinstance(value, Number):
        return cast(Coefficient, value)
    return None


class Polynomial:
    """A multilinear polynomial with variables over {0, 1}, so x*x = x.

    Polynomials are immutable: every operation returns a new one.
    """

    __slots__ = ("_support", "_terms")

    _terms: _Masks  # monomial bitmask -> nonzero coefficient
    _support: int | None  # mask of all variables, computed on first use

    def __init__(self, terms: Terms | None = None) -> None:
        self._terms = {
            mask_of(monomial): coefficient
            for monomial, coefficient in (terms or {}).items()
            if coefficient != 0
        }
        self._support = None

    @classmethod
    def _from_masks(cls, terms: _Masks) -> Polynomial:
        # Internal constructor: ``terms`` is a fresh dict without zero
        # coefficients, so skip the conversion and the zero filter.
        poly = cls.__new__(cls)
        poly._terms = terms
        poly._support = None
        return poly

    @staticmethod
    def constant(value: Coefficient) -> Polynomial:
        return Polynomial._from_masks({0: value} if value != 0 else {})

    @staticmethod
    def variable(name: str) -> Polynomial:
        return Polynomial._from_masks({bit(validate_variable_name(name)): 1})

    @property
    def terms(self) -> Mapping[Monomial, Coefficient]:
        """The terms as a read-only mapping of monomial -> nonzero coefficient."""
        return MappingProxyType(
            {names_of(mask): value for mask, value in self._terms.items()}
        )

    def simplify(self) -> Self:
        """Kept for compatibility: polynomials are always stored simplified."""
        return self

    def _variable_mask(self) -> int:
        support = self._support
        if support is None:
            support = 0
            for mask in self._terms:
                support |= mask
            self._support = support
        return support

    def variables(self) -> frozenset[str]:
        """Names of the variables that occur with a nonzero coefficient."""
        return names_of(self._variable_mask())

    def evaluate(self, assignment: Mapping[str, Any]) -> Coefficient:
        """Value at a point, given a mapping of variable name -> bool/0/1."""
        false = 0
        for name in self.variables():
            if not assignment[name]:
                false |= bit(name)
        total: Coefficient = 0
        for monomial, coefficient in self._terms.items():
            if not monomial & false:
                total += coefficient
        return total

    @staticmethod
    def _coerce(value: object) -> Polynomial | None:
        # Plain numbers act as constant polynomials.
        if isinstance(value, Polynomial):
            return value
        scalar = _scalar(value)
        return None if scalar is None else Polynomial.constant(scalar)

    def __add__(self, other: Polynomial | Coefficient) -> Polynomial:
        poly = Polynomial._coerce(other)
        if poly is None:
            return NotImplemented
        return Polynomial._from_masks(_combine(self._terms, poly._terms, 1))

    def __sub__(self, other: Polynomial | Coefficient) -> Polynomial:
        poly = Polynomial._coerce(other)
        if poly is None:
            return NotImplemented
        return Polynomial._from_masks(_combine(self._terms, poly._terms, -1))

    def __rsub__(self, other: Coefficient) -> Polynomial:
        poly = Polynomial._coerce(other)
        if poly is None:
            return NotImplemented
        return poly - self

    def __neg__(self) -> Polynomial:
        return Polynomial._from_masks({k: -v for k, v in self._terms.items()})

    def __mul__(self, other: Polynomial | Coefficient) -> Polynomial:
        scalar = _scalar(other)
        if scalar is not None:
            # Scaling needs no monomial products.
            return Polynomial._from_masks(
                {k: v * scalar for k, v in self._terms.items() if v * scalar}
            )
        if not isinstance(other, Polynomial):
            return NotImplemented

        # Loop over the smaller polynomial in the outer loop.
        outer, inner = self._terms, other._terms
        if len(outer) > len(inner):
            outer, inner = inner, outer

        if len(outer) > 16:  # tiny products never pay for a table
            support = self._variable_mask() | other._variable_mask()
            if (
                dense.worthwhile(len(outer), len(inner), support.bit_count())
                and dense.is_exact(outer)
                and dense.is_exact(inner)
            ):
                return Polynomial._from_masks(dense.multiply(outer, inner, support))

        result: _Masks = {}
        get = result.get
        for a, ca in outer.items():
            for b, cb in inner.items():
                # x*x = x, so the product of monomials is their union
                monomial = a | b
                result[monomial] = get(monomial, 0) + ca * cb

        return Polynomial._from_masks({k: v for k, v in result.items() if v})

    # Addition and multiplication are commutative.
    def __radd__(self, other: Coefficient) -> Polynomial:
        return self + other

    def __rmul__(self, other: Coefficient) -> Polynomial:
        return self * other

    def __invert__(self) -> Polynomial:
        # NOT x = 1 - x
        return 1 - self

    def __eq__(self, other: object) -> bool:
        # Terms are kept simplified (no zero coefficients), so equal
        # polynomials always have equal term dicts.
        poly = Polynomial._coerce(other)
        if poly is None:
            return NotImplemented
        return self._terms == poly._terms

    __hash__: ClassVar[None]  # type: ignore[assignment]  # compared by value, unhashable

    def __reduce__(self) -> tuple[type[Polynomial], tuple[dict[Monomial, Coefficient]]]:
        # Pickle by variable names: bit indices differ between processes.
        return Polynomial, (dict(self.terms),)

    def __repr__(self) -> str:
        return str(dict(self.terms))

    def __str__(self) -> str:
        return format_terms(self.terms)
