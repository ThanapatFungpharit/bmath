"""Multiplication of dense multilinear polynomials through truth tables.

Multiplying term by term costs |p|*|q| monomial products. When both factors
are dense over the same V variables that is up to 2^V * 2^V = 4^V.

A multilinear polynomial is determined by its values on {0, 1}^V, and the
product of two polynomials takes the product of their values at every point.
So instead:

1. Turn each factor into its table of values. The value at the point where
   exactly the variables in S are 1 is the sum of the coefficients of the
   monomials inside S (the "zeta" or subset-sum transform).
2. Multiply the two tables entry by entry.
3. Turn the result back into coefficients by inclusion-exclusion (the
   Moebius transform, the inverse of step 1).

Each transform costs O(V*2^V) additions, for O(V*2^V) in total. The
transforms are written as list-slice updates, so the inner loops run in C.

Only exact coefficients (``int``, ``Fraction``) take this path: the
transforms add and subtract in a different order than term-by-term
multiplication, which would change float rounding.
"""

from collections.abc import Callable, Mapping
from fractions import Fraction
from operator import add, mul, sub
from typing import Any

from .monomials import indices
from .terms import Coefficient

MAX_VARIABLES = 22
"""Largest table built: 2^22 entries, a few tens of MB per table."""


def is_exact(terms: Mapping[int, Coefficient]) -> bool:
    return all(isinstance(value, (int, Fraction)) for value in terms.values())


def worthwhile(left_size: int, right_size: int, variables: int) -> bool:
    """Whether the table method is expected to beat term-by-term products.

    Term-by-term does ``left_size * right_size`` Python-level steps; the
    table method does about ``3*V*2^V`` C-level steps plus ``2^V``
    Python-level ones to read the result back.
    """
    if variables > MAX_VARIABLES:
        return False
    table = 1 << variables
    return left_size * right_size > table * (variables + 12) // 4


def _transform(values: list[Any], op: Callable[[Any, Any], Any]) -> None:
    """In place: with ``add``, every entry S becomes the sum over subsets of S;
    with ``sub``, that is undone."""
    size = len(values)
    step = 1
    while step < size:
        span = 2 * step
        blocks = size // span
        if step <= blocks:
            # Few offsets: entries with this bit set form `step` strided slices.
            for offset in range(step):
                high = slice(step + offset, size, span)
                values[high] = map(op, values[high], values[offset:size:span])
        else:
            # Few blocks: each block's upper half is one contiguous slice.
            for base in range(0, size, span):
                high = slice(base + step, base + span)
                values[high] = map(op, values[high], values[base : base + step])
        step = span


def multiply(
    left: Mapping[int, Coefficient],
    right: Mapping[int, Coefficient],
    support: int,
) -> dict[int, Coefficient]:
    """Product of two polynomials whose variables all lie in ``support``."""
    positions = list(indices(support))
    count = len(positions)
    size = 1 << count
    low = positions[0] if positions else 0
    contiguous = support >> low == size - 1

    # Global masks <-> table indices 0 .. 2^count - 1.
    compress: Callable[[int], int]
    expand: Callable[[int], int]
    if contiguous:  # the usual case: variables registered one after another

        def compress(mask: int) -> int:
            return mask >> low

        def expand(index: int) -> int:
            return index << low

    else:
        local = {1 << position: 1 << i for i, position in enumerate(positions)}

        def compress(mask: int) -> int:
            index = 0
            while mask:
                lowest = mask & -mask
                index |= local[lowest]
                mask ^= lowest
            return index

        # Expand 8 table bits at a time through precomputed tables.
        tables: list[list[int]] = []
        for start in range(0, count, 8):
            chunk = positions[start : start + 8]
            table = [0] * (1 << len(chunk))
            for value in range(1, len(table)):
                lowest = value & -value
                table[value] = table[value ^ lowest] | (
                    1 << chunk[lowest.bit_length() - 1]
                )
            tables.append(table)

        def expand(index: int) -> int:
            mask = 0
            for table in tables:
                mask |= table[index & 0xFF]
                index >>= 8
            return mask

    def values_of(terms: Mapping[int, Coefficient]) -> list[Any]:
        values: list[Any] = [0] * size
        for mask, coefficient in terms.items():
            values[compress(mask)] = coefficient
        _transform(values, add)
        return values

    product = list(map(mul, values_of(left), values_of(right)))
    _transform(product, sub)
    return {expand(index): value for index, value in enumerate(product) if value}
