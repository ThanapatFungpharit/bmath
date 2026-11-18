from collections.abc import Sequence
from dataclasses import dataclass

from ..polynomial import Polynomial
from .base import Assignment, BooleanExpr, RenderPart


@dataclass(frozen=True, eq=False, repr=False)
class AND(BooleanExpr, operator="__and__"):
    left: BooleanExpr
    right: BooleanExpr

    def _evaluate(self, values: Sequence[bool], assignment: Assignment) -> bool:
        # Both sides are always evaluated, so missing variables are reported.
        left, right = values
        return left and right

    def _polynomial(self, polys: Sequence[Polynomial]) -> Polynomial:
        a, b = polys
        return a * b

    def _render_parts(self) -> list[RenderPart]:
        return [self.left, " & ", self.right]
