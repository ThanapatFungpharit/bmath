from collections.abc import Iterator
from dataclasses import dataclass, field
from itertools import product
from typing import NamedTuple, overload

from ..expr import Assignment, BooleanExpr
from ..polynomial import display_name
from ..polynomial.names import name_order
from .dependence import dependent_variables

INDEPENDENT = "*"
"""How a variable that never affects the result is shown."""


class Row(NamedTuple):
    """One line of a truth table.

    ``inputs`` follows ``TruthTable.variables``; an entry is None for a
    variable that never affects the result (shown as ``*``).
    """

    inputs: tuple[bool | None, ...]
    result: bool


@dataclass(frozen=True)
class TruthTable:
    """A truth table that can be printed and looked up.

    Independent variables (shown as ``*``) don't multiply the rows. ``str()``
    renders the table, for example for ``(x & y) | x``::

        x y result
        1 * 1
        0 * 0

    Look up a result by assignment, like a dict. Only the dependent
    variables are needed; other names in the assignment are ignored::

        table.get({"x": True})              # True
        table.get({"x": True, "y": False})  # True: y is independent
        table.get({"y": True})              # None: x is missing
        table.get({"y": True}, False)       # False (the default)
        table[{"x": False}]                 # False; KeyError if not found

    Lookups use an index built once, so each costs O(dependent variables).
    """

    variables: tuple[str, ...]
    rows: tuple[Row, ...]
    _dependent: tuple[str, ...] = field(init=False, repr=False, compare=False)
    _index: dict[tuple[bool, ...], bool] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not self.rows:
            raise ValueError("a truth table needs at least one row")
        columns = len(self.variables)
        first = self.rows[0].inputs
        positions = [i for i, value in enumerate(first) if value is not None]
        index: dict[tuple[bool, ...], bool] = {}
        for inputs, result in self.rows:
            if len(inputs) != columns:
                raise ValueError(
                    f"row {inputs} has {len(inputs)} inputs for {columns} variables"
                )
            if [i for i, value in enumerate(inputs) if value is not None] != positions:
                raise ValueError("every row must mark the same variables with *")
            key = tuple(bool(inputs[i]) for i in positions)
            if key in index:
                raise ValueError(f"duplicate row {inputs}")
            index[key] = result
        dependent = tuple(self.variables[i] for i in positions)
        object.__setattr__(self, "_dependent", dependent)
        object.__setattr__(self, "_index", index)

    @property
    def dependent(self) -> tuple[str, ...]:
        """Variables the result depends on: the ones a lookup needs."""
        return self._dependent

    @property
    def independent(self) -> tuple[str, ...]:
        """Variables shown as ``*``: they never change the result."""
        return tuple(name for name in self.variables if name not in self._dependent)

    def __getitem__(self, assignment: Assignment) -> bool:
        """The result under ``assignment``; KeyError if it can't be looked up."""
        key: list[bool] = []
        for name in self._dependent:
            try:
                key.append(bool(assignment[name]))
            except KeyError:
                raise KeyError(f"no value assigned to variable {name!r}") from None
        try:
            return self._index[tuple(key)]
        except KeyError:
            point = dict(zip(self._dependent, key))
            raise KeyError(f"no row for {point}") from None

    @overload
    def get(self, assignment: Assignment) -> bool | None: ...
    @overload
    def get[T](self, assignment: Assignment, default: T) -> bool | T: ...
    def get(self, assignment: Assignment, default: object = None) -> object:
        """The result under ``assignment``, or ``default`` if it can't be looked up."""
        try:
            return self[assignment]
        except KeyError:
            return default

    def __len__(self) -> int:
        return len(self.rows)

    def __iter__(self) -> Iterator[Row]:
        return iter(self.rows)

    def __str__(self) -> str:
        header = [*map(display_name, self.variables), "result"]
        lines = [header]
        for inputs, result in self.rows:
            cells = [INDEPENDENT if v is None else str(int(v)) for v in inputs]
            lines.append([*cells, str(int(result))])
        widths = [len(cell) for cell in header]
        return "\n".join(
            " ".join(cell.ljust(width) for cell, width in zip(line, widths)).rstrip()
            for line in lines
        )


def truth_table(expr: BooleanExpr) -> TruthTable:
    """The truth table of ``expr``, with a column for each of its variables.

    Only the variables the result depends on are enumerated, 1 before 0;
    the others are marked independent. So the table has 2^d rows for d
    dependent variables, however many variables the expression mentions.
    """
    variables = tuple(sorted(expr.variables(), key=name_order))
    dependent = dependent_variables(expr)
    enumerated = [name for name in variables if name in dependent]

    rows: list[Row] = []
    for values in product((True, False), repeat=len(enumerated)):
        point = dict(zip(enumerated, values))
        # Independent variables can take any value; False is as good as any.
        result = expr.evaluate({name: point.get(name, False) for name in variables})
        rows.append(Row(tuple(point.get(name) for name in variables), result))
    return TruthTable(variables, tuple(rows))
