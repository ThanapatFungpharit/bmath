from .monomials import names_of
from .polynomial import Polynomial
from .terms import Monomial


def nonzero_point(poly: Polynomial) -> Monomial | None:
    """Return a point where ``poly`` is nonzero, or None if it is the zero polynomial.

    The point is given as the frozenset of variables set to 1; every other
    variable is 0.

    Why this works: at the point where exactly the variables in S are 1, a
    multilinear polynomial evaluates to the sum of coefficients of the
    monomials contained in S. A monomial of minimum size has no other
    monomial strictly inside it, so at its own point the sum is just its
    (nonzero) coefficient.
    """
    masks = poly._terms
    if not masks:
        return None
    degree = min(mask.bit_count() for mask in masks)
    # Names are only built for the lowest-degree terms (for a stable choice).
    lowest = (names_of(mask) for mask in masks if mask.bit_count() == degree)
    return min(lowest, key=sorted)
