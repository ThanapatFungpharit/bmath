import time

from bmath import AND, OR, BooleanExpr, BooleanVariable, Not
from variables import Section, x, y, z


def _nested_not(depth: int) -> BooleanExpr:
    expr: BooleanExpr = x
    for _ in range(depth):
        expr = Not(expr)
    return expr


def _or_of(n: int) -> BooleanExpr:
    variables = [BooleanVariable(f"v{i}") for i in range(n)]
    expr: BooleanExpr = variables[0]
    for v in variables[1:]:
        expr = OR(expr, v)
    return expr


def _term_count(expr: BooleanExpr) -> str:
    start = time.perf_counter()
    poly = expr.to_polynomial()
    elapsed = time.perf_counter() - start
    return f"{len(poly.terms)} terms in {elapsed:.3f}s"


# (section title, [(description, thunk), ...])
EDGE_CASE_SECTIONS: list[Section] = [
    (
        "Expressions: equality and hashing",
        [
            ("AND(x, y) == AND(x, y)", lambda: AND(x, y) == AND(x, y)),
            (
                "AND(x, y) == AND(y, x) (equivalent, not equal)",
                lambda: AND(x, y) == AND(y, x),
            ),
            (
                "~(x & y) and ~x | ~y give equal polynomials?",
                lambda: (
                    Not(AND(x, y)).to_polynomial() == OR(Not(x), Not(y)).to_polynomial()
                ),
            ),
            (
                "x | ~x is a tautology (polynomial == 1)?",
                lambda: OR(x, Not(x)).to_polynomial() == 1,
            ),
            (
                "hash(AND(x, y)) == hash(AND(x, y))",
                lambda: hash(AND(x, y)) == hash(AND(x, y)),
            ),
            ("{x, y, x} as a set", lambda: len({x, y, BooleanVariable("x")})),
            ("expressions are immutable", lambda: setattr(x, "symbol", "q")),
        ],
    ),
    (
        "Expressions: invalid input",
        [
            ("AND(x, True)", lambda: AND(x, True)),  # type: ignore[arg-type]
            ("AND(x, 'y')", lambda: AND(x, "y")),  # type: ignore[arg-type]
            ("Not(None)", lambda: Not(None)),  # type: ignore[arg-type]
            ("x & 1", lambda: x & 1),  # type: ignore[operator]
            ("BooleanVariable(42)", lambda: BooleanVariable(42)),  # type: ignore[arg-type]
            ("BooleanVariable('')", lambda: BooleanVariable("")),
        ],
    ),
    (
        "Expressions: operators",
        [
            ("x & y", lambda: x & y),
            ("x | y", lambda: x | y),
            ("~x", lambda: ~x),
            ("x >> y", lambda: x >> y),
            ("~(x & y) == Not(AND(x, y))", lambda: ~(x & y) == Not(AND(x, y))),
            (
                "De Morgan with operators",
                lambda: (~(x | y)).to_polynomial() == (~x & ~y).to_polynomial(),
            ),
            ("x & y | z (& binds tighter than |, as in logic)", lambda: x & y | z),
            ("x | y >> z (Python: >> binds tighter than |)", lambda: x | y >> z),
            (
                "(x | y) >> z (parenthesize for usual logic precedence)",
                lambda: (x | y) >> z,
            ),
        ],
    ),
    (
        "Expressions: unusual variable names",
        [
            (
                "name with spaces (rejected)",
                lambda: AND(BooleanVariable("is raining"), y),
            ),
            (
                "non-ASCII name (rejected)",
                lambda: OR(BooleanVariable("\u03b1"), y),
            ),
            (
                "name that looks like an operator (rejected)",
                lambda: AND(BooleanVariable("&"), y),
            ),
        ],
    ),
    (
        "Expressions: scale",
        [
            (
                "~ nested 500 deep -> polynomial",
                lambda: _nested_not(500).to_polynomial(),
            ),
            (
                "~ nested 2000 deep -> polynomial",
                lambda: _nested_not(2000).to_polynomial(),
            ),
            ("~ nested 2000 deep -> str", lambda: str(_nested_not(2000))),
            ("OR of 8 variables", lambda: _term_count(_or_of(8))),
            ("OR of 12 variables", lambda: _term_count(_or_of(12))),
            ("OR of 16 variables", lambda: _term_count(_or_of(16))),
        ],
    ),
]
