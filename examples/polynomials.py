from fractions import Fraction

from bmath import Polynomial
from variables import Section

P = Polynomial
px = P.variable("x")
py = P.variable("y")


def _read_missing_term() -> Polynomial:
    p = P.variable("x")
    _ = p.terms.get(frozenset({"q"}))  # just a read
    return p


# (section title, [(description, thunk), ...])
# Thunks are evaluated lazily so that failures can be shown instead of crashing.
POLYNOMIAL_SECTIONS: list[Section] = [
    (
        "Polynomial: construction",
        [
            ("zero polynomial", lambda: P()),
            ("constant 1", lambda: P.constant(1)),
            ("constant -3", lambda: P.constant(-3)),
            ("variable", lambda: px),
            ("multi-letter variable names", lambda: P.variable("ab") * P.variable("c")),
        ],
    ),
    (
        "Polynomial: arithmetic",
        [
            ("x + x", lambda: px + px),
            ("x - x", lambda: px - px),
            ("-x", lambda: -px),
            ("x * x (idempotent: x^2 = x)", lambda: px * px),
            ("(x + y) * (x - y)", lambda: (px + py) * (px - py)),
            ("~x", lambda: ~px),
            ("~(x + x): NOT of a non-boolean value", lambda: ~(px + px)),
        ],
    ),
    (
        "Polynomial: coefficient types",
        [
            ("float coefficient", lambda: P.constant(0.5) * px),
            ("Fraction coefficient", lambda: P.constant(Fraction(1, 3)) * px),
            ("large coefficient", lambda: P.constant(10**20) * px),
        ],
    ),
    (
        "Polynomial: formatting and variable names",
        [
            ("2*x*y renders as", lambda: P.constant(2) * px * py),
            ("variable named 'a*b' (rejected)", lambda: P.variable("a*b")),
            ("product a*b", lambda: P.variable("a") * P.variable("b")),
            ("variable named '' (rejected)", lambda: P.variable("")),
            ("variable named '2' (rejected)", lambda: P.variable("2") * P.constant(3)),
        ],
    ),
    (
        "Polynomial: Python protocols",
        [
            ("x + 1", lambda: px + 1),
            ("1 + x", lambda: 1 + px),
            ("1 - x", lambda: 1 - px),
            ("2 * x", lambda: 2 * px),
            ("x * 0.5", lambda: px * 0.5),
            ("x + 'a' (not a number)", lambda: px + "a"),  # type: ignore[operator]
            ("x == x (separate objects)", lambda: P.variable("x") == P.variable("x")),
            ("x + y == y + x", lambda: px + py == py + px),
            ("x == y", lambda: px == py),
            ("x * ~x == 0 (compare with a plain number)", lambda: px * ~px == 0),
            ("~x == 1", lambda: ~px == 1),
            ("repr(x + y)", lambda: repr(px + py)),
            (
                "looking up a missing term leaves the polynomial unchanged",
                _read_missing_term,
            ),
        ],
    ),
]
