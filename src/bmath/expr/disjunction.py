from collections.abc import Sequence
from dataclasses import dataclass

from ..polynomial import Polynomial
from .base import Assignment, BooleanExpr, RenderPart


@dataclass(frozen=True, eq=False, repr=False)
class OR(BooleanExpr, operator="__or__"):
    left: BooleanExpr
    right: BooleanExpr

    def _evaluate(self, values: Sequence[bool], assignment: Assignment) -> bool:
        left, right = values
        return left or right

    def _polynomial(self, polys: Sequence[Polynomial]) -> Polynomial:
        a, b = polys
        return a + b - a * b

    def _render_parts(self) -> list[RenderPart]:
        return [self.left, " | ", self.right]
