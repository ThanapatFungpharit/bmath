from ..expr import BooleanExpr


def dependent_variables(expr: BooleanExpr) -> frozenset[str]:
    """Variables whose value can change the result of ``expr``.

    The polynomial of a boolean function is unique, so a variable affects
    the function exactly when it appears in the polynomial.
    """
    return expr.to_polynomial().variables()


def redundant_variables(expr: BooleanExpr) -> frozenset[str]:
    """Variables that appear in ``expr`` but never affect its result."""
    return expr.variables() - dependent_variables(expr)
