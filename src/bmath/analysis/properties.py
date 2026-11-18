"""Tautology, contradiction and equivalence checks.

All answers are exact: they are settled by the polynomial. Before building
one, two cheap steps can end the check early:

* **Splitting.** A conjunction is a tautology exactly when both sides are,
  so ``is_tautology(a & b)`` checks ``a`` and then ``b`` and stops at the
  first failure, without ever multiplying the two polynomials. Likewise for
  ``~``, contradictions of ``|`` and ``->``.
* **Probing.** The expression is evaluated at a few assignments, each costing
  one walk of the expression. A single assignment with the wrong value
  proves the answer is False. Most non-tautologies fail on one of them.

A True answer still needs the polynomial, since no number of probes can
prove it. Polynomials that are already cached are used directly.
"""

import random
from collections.abc import Iterator

from ..expr import AND, OR, BooleanExpr, IfThen, Not

_RANDOM_PROBES = 4
"""Random assignments tried, in addition to all-false and all-true."""


def _probes(names: list[str]) -> Iterator[dict[str, bool]]:
    yield dict.fromkeys(names, False)
    if not names:
        return
    yield dict.fromkeys(names, True)
    rng = random.Random(0)  # fixed seed: same probes, same work, every run
    for _ in range(_RANDOM_PROBES):
        yield {name: rng.random() < 0.5 for name in names}


def _always(expr: BooleanExpr, value: bool) -> bool:
    """True if ``expr`` evaluates to ``value`` under every assignment."""
    seen: set[tuple[int, bool]] = set()
    goals: list[tuple[BooleanExpr, bool]] = [(expr, value)]
    while goals:
        node, value = goals.pop()
        if (id(node), value) in seen:
            continue
        seen.add((id(node), value))

        poly = node._cached_polynomial
        if poly is None:
            # Split into sub-goals that must all hold (checked left first).
            match node, value:
                case Not(expr=inner), _:
                    goals.append((inner, not value))
                    continue
                case AND(left=left, right=right), True:
                    goals += [(right, True), (left, True)]
                    continue
                case OR(left=left, right=right), False:
                    goals += [(right, False), (left, False)]
                    continue
                case IfThen(condition=condition, consequence=consequence), False:
                    goals += [(consequence, False), (condition, True)]
                    continue

            names = sorted(node.variables())
            if any(node.evaluate(probe) is not value for probe in _probes(names)):
                return False
            poly = node.to_polynomial()

        if poly != int(value):
            return False
    return True


def is_tautology(expr: BooleanExpr) -> bool:
    """True if ``expr`` is true under every assignment."""
    return _always(expr, True)


def is_contradiction(expr: BooleanExpr) -> bool:
    """True if ``expr`` is false under every assignment."""
    return _always(expr, False)


def is_satisfiable(expr: BooleanExpr) -> bool:
    """True if some assignment makes ``expr`` true."""
    return not is_contradiction(expr)


def equivalent(a: BooleanExpr, b: BooleanExpr) -> bool:
    """True if ``a`` and ``b`` have the same truth value under every assignment."""
    if a is b:
        return True
    if a._cached_polynomial is None or b._cached_polynomial is None:
        names = sorted(a.variables() | b.variables())
        if any(a.evaluate(probe) != b.evaluate(probe) for probe in _probes(names)):
            return False
    return a.to_polynomial() == b.to_polynomial()
