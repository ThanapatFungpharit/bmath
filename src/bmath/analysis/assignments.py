from ..expr import BooleanExpr
from ..polynomial import Monomial, nonzero_point


def _assignment(
    expr: BooleanExpr, true_names: Monomial | None
) -> dict[str, bool] | None:
    if true_names is None:
        return None
    return {name: name in true_names for name in sorted(expr.variables())}


def satisfying_assignment(expr: BooleanExpr) -> dict[str, bool] | None:
    """An assignment (name -> bool) that makes ``expr`` true, or None if none exists."""
    return _assignment(expr, nonzero_point(expr.to_polynomial()))


def counterexample(expr: BooleanExpr) -> dict[str, bool] | None:
    """An assignment (name -> bool) that makes ``expr`` false, or None if it is a tautology."""
    return _assignment(expr, nonzero_point(1 - expr.to_polynomial()))
