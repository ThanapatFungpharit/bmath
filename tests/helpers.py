from collections.abc import Iterable, Iterator
from itertools import product

from bmath import (
    AND,
    FALSE,
    OR,
    TRUE,
    BooleanExpr,
    BooleanVariable,
    Iff,
    IfThen,
    Not,
)

x, y, z, w = (BooleanVariable(name) for name in "xyzw")


def assignments(names: Iterable[str]) -> Iterator[dict[str, bool]]:
    """Every assignment of the given variable names (brute-force oracle)."""
    names = sorted(names)
    for values in product([False, True], repeat=len(names)):
        yield dict(zip(names, values))


# A spread of expressions covering every connective, constants and nesting.
SAMPLES: list[BooleanExpr] = [
    x,
    ~x,
    x & y,
    x | y,
    x >> y,
    ~Iff(x, y),
    Iff(x, y),
    TRUE,
    FALSE,
    TRUE & x,
    FALSE | x,
    x >> FALSE,
    Iff(x, TRUE),
    x | ~x,
    x & ~x,
    (((x | ~x) & y) & z) | z,
    (x & (x >> y)) >> y,
    ((x >> y) & (y >> z)) >> (x >> z),
    ((x >> y) >> x) >> x,
    Not(AND(x, y)),
    OR(Not(x), Not(y)),
    (x & y) | (y & z) | (x & z),
    Iff(Iff(Iff(x, y), z), w),
    Iff(Iff(x, y), z),
    Not(Iff(x, IfThen(y, Not(z)))) | (w & ~x),
]
