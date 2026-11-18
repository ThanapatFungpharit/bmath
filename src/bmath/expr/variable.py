from collections.abc import Sequence
from dataclasses import dataclass
from typing import ClassVar

from ..polynomial import Polynomial, display_name, validate_variable_name
from .base import Assignment, BooleanExpr, RenderPart, Substitution
from .constant import FALSE, TRUE


@dataclass(frozen=True, eq=False, repr=False)
class BooleanVariable(BooleanExpr):
    symbol: str

    _parenthesize: ClassVar[bool] = False

    def _validate(self) -> None:
        validate_variable_name(self.symbol)

    def children(self) -> tuple[BooleanExpr, ...]:
        return ()

    def _own_variables(self) -> Sequence[str]:
        return (self.symbol,)

    def _rebuild(
        self, children: Sequence[BooleanExpr], mapping: Substitution
    ) -> BooleanExpr:
        if self.symbol not in mapping:
            return self
        value = mapping[self.symbol]
        if isinstance(value, bool):
            return TRUE if value else FALSE
        if not isinstance(value, BooleanExpr):
            raise TypeError(
                f"substitute value for {self.symbol!r} must be a BooleanExpr "
                f"or bool, not {type(value).__name__}"
            )
        return value

    def _evaluate(self, values: Sequence[bool], assignment: Assignment) -> bool:
        try:
            return bool(assignment[self.symbol])
        except KeyError:
            raise KeyError(f"no value assigned to variable {self.symbol!r}") from None

    def _polynomial(self, polys: Sequence[Polynomial]) -> Polynomial:
        return Polynomial.variable(self.symbol)

    def _render_parts(self) -> list[RenderPart]:
        return [display_name(self.symbol)]
