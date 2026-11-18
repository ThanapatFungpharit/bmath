from collections.abc import Sequence
from dataclasses import dataclass
from typing import ClassVar

from ..polynomial import Polynomial
from .base import Assignment, BooleanExpr, RenderPart


@dataclass(frozen=True, eq=False, repr=False)
class Not(BooleanExpr, operator="__invert__"):
    expr: BooleanExpr

    _parenthesize: ClassVar[bool] = False

    def _evaluate(self, values: Sequence[bool], assignment: Assignment) -> bool:
        (value,) = values
        return not value

    def _polynomial(self, polys: Sequence[Polynomial]) -> Polynomial:
        (poly,) = polys
        return ~poly

    def _render_parts(self) -> list[RenderPart]:
        return ["~", self.expr]
