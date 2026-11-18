from collections.abc import Sequence
from dataclasses import dataclass

from ..polynomial import Polynomial
from .base import Assignment, BooleanExpr, RenderPart


@dataclass(frozen=True, eq=False, repr=False)
class Iff(BooleanExpr):
    left: BooleanExpr
    right: BooleanExpr

    def _evaluate(self, values: Sequence[bool], assignment: Assignment) -> bool:
        left, right = values
        return left == right

    def _polynomial(self, polys: Sequence[Polynomial]) -> Polynomial:
        # a <=> b  is  (a & b) | (~a & ~b)  =  1 - a - b + 2ab
        a, b = polys
        return (a * b) * 2 - a - b + 1

    def _render_parts(self) -> list[RenderPart]:
        return [self.left, " <=> ", self.right]
