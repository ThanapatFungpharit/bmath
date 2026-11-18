from collections.abc import Callable

from bmath import BooleanExpr, BooleanVariable

type Subject = BooleanExpr | Callable[[], object]
"""An example: an expression to show, or a thunk whose result (or error) is shown."""

type Section = tuple[str, list[tuple[str, Subject]]]
"""A titled group of (description, subject) examples."""

x = BooleanVariable("x")
y = BooleanVariable("y")
z = BooleanVariable("z")
w = BooleanVariable("w")
