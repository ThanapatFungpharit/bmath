from collections.abc import Sequence
from dataclasses import dataclass

from ..polynomial import Polynomial
from .base import Assignment, BooleanExpr, RenderPart


@dataclass(frozen=True, eq=False, repr=False)
class IfThen(BooleanExpr, operator="__rshift__"):
    condition: BooleanExpr
    consequence: BooleanExpr

    def _evaluate(self, values: Sequence[bool], assignment: Assignment) -> bool:
        condition, consequence = values
        return (not condition) or consequence

    def _polynomial(self, polys: Sequence[Polynomial]) -> Polynomial:
        # a -> b  is  ~a | b  =  1 - a + ab
        a, b = polys
        return a * b - a + 1

    def _render_parts(self) -> list[RenderPart]:
        return [self.condition, " -> ", self.consequence]
