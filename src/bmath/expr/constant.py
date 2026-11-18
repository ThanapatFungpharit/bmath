from collections.abc import Sequence
from dataclasses import dataclass
from typing import ClassVar

from ..polynomial import Polynomial
from .base import Assignment, BooleanExpr, RenderPart, Substitution


@dataclass(frozen=True, eq=False, repr=False)
class BooleanConstant(BooleanExpr):
    value: bool

    _parenthesize: ClassVar[bool] = False

    def _validate(self) -> None:
        if not isinstance(self.value, bool):
            raise TypeError(
                f"BooleanConstant.value must be a bool, not {type(self.value).__name__}"
            )

    def children(self) -> tuple[BooleanExpr, ...]:
        return ()

    def _rebuild(
        self, children: Sequence[BooleanExpr], mapping: Substitution
    ) -> BooleanExpr:
        return self

    def _evaluate(self, values: Sequence[bool], assignment: Assignment) -> bool:
        return self.value

    def _polynomial(self, polys: Sequence[Polynomial]) -> Polynomial:
        return Polynomial.constant(int(self.value))

    def _render_parts(self) -> list[RenderPart]:
        return ["T" if self.value else "F"]


TRUE = BooleanConstant(True)
FALSE = BooleanConstant(False)
