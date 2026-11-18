"""Rendering polynomials as plain ASCII text.

Examples: ``1 - x + 2xy``, ``x/3``, ``-2*rain*wind``, ``v0 + v1 - v0*v1``.

* Factors are juxtaposed (``2xy``) when every variable is a single letter;
  otherwise they are separated by ``*`` so that longer names stay
  unambiguous (``ab*c`` is not ``abc``, and ``v0*v1`` is not ``v0v1``).
* A coefficient of 1 is omitted, and rational coefficients are written as
  a quotient (``2xy/3``).
* Subtraction uses ``-``.
* Terms go from the constant up by degree, then in natural name order.
"""

from fractions import Fraction

from .names import name_order
from .terms import Coefficient, Monomial, Terms

MINUS = "-"


def _order(
    item: tuple[Monomial, Coefficient],
) -> tuple[int, list[tuple[str, int, str]]]:
    # Constant first, then by degree, then by (natural) variable names.
    monomial, _ = item
    return len(monomial), sorted(map(name_order, monomial))


def _quotient(coef: Coefficient) -> tuple[str, str | None]:
    """A nonnegative coefficient as (numerator, denominator or None)."""
    if isinstance(coef, Fraction):
        if coef.denominator == 1:
            return str(coef.numerator), None
        return str(coef.numerator), str(coef.denominator)
    if isinstance(coef, float) and coef.is_integer():
        return str(int(coef)), None
    return str(coef), None


def _format_term(monomial: Monomial, coef: Coefficient) -> str:
    """Render one term with a nonnegative coefficient, e.g. ``2xy`` or ``x/3``."""
    numerator, denominator = _quotient(coef)
    names = sorted(monomial, key=name_order)

    if not names:
        body = numerator
    else:
        juxtapose = all(len(name) == 1 for name in names)
        separator = "" if juxtapose else "*"
        product = separator.join(names)
        body = product if numerator == "1" else f"{numerator}{separator}{product}"

    return body if denominator is None else f"{body}/{denominator}"


def format_terms(terms: Terms) -> str:
    """Render a mapping of monomial -> coefficient in math notation."""
    if not terms:
        return "0"

    parts: list[str] = []
    for monomial, coef in sorted(terms.items(), key=_order):
        negative = coef < 0
        term = _format_term(monomial, -coef if negative else coef)
        if not parts:
            parts.append(f"{MINUS}{term}" if negative else term)
        else:
            parts.append(f"{MINUS if negative else '+'} {term}")
    return " ".join(parts)
