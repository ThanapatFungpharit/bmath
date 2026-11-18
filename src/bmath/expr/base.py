from collections.abc import Callable, Mapping, Sequence
from dataclasses import Field, fields
from typing import TYPE_CHECKING, Any, ClassVar, cast

from ..polynomial import Polynomial

if TYPE_CHECKING:
    from .conjunction import AND
    from .disjunction import OR
    from .implication import IfThen
    from .negation import Not

type Assignment = Mapping[str, bool]
"""Truth values of variables, by name."""

type Substitution = Mapping[str, BooleanExpr | bool]
"""Replacements for variables, by name."""

type RenderPart = str | BooleanExpr
"""A piece of rendered text: literal text, or a child rendered as an operand."""


_FIELD_NAMES: dict[type[BooleanExpr], tuple[str, ...]] = {}


def _field_names(cls: type[BooleanExpr]) -> tuple[str, ...]:
    """Dataclass field names of an expression class, cached per class."""
    try:
        return _FIELD_NAMES[cls]
    except KeyError:
        names = _FIELD_NAMES[cls] = tuple(field.name for field in fields(cls))
        return names


def _write[I](root: I, pieces: Callable[[I], Sequence[str | I]]) -> str:
    """Concatenate text pieces without recursion.

    ``pieces(item)`` returns strings and further items; items are expanded
    in place. Text is joined once at the end, so output of size n costs O(n)
    instead of the O(n^2) of building nested strings.
    """
    out: list[str] = []
    stack: list[str | I] = [root]
    while stack:
        item = stack.pop()
        if isinstance(item, str):
            out.append(item)
        else:
            stack.extend(reversed(pieces(item)))
    return "".join(out)


class BooleanExpr:
    """Base class of all expressions.

    Every traversal (evaluation, polynomial conversion, rendering,
    substitution, equality, hashing, repr) runs on an explicit stack instead
    of the call stack, so arbitrarily deep expressions never hit Python's
    recursion limit. Subclasses only describe one node at a time through the
    ``_evaluate``, ``_polynomial``, ``_render_parts`` and ``_rebuild`` hooks,
    which receive the already-computed results of their children (rendering
    hooks return their text as pieces instead).

    Subclasses are frozen dataclasses declared with ``eq=False, repr=False``
    so that the iterative ``__eq__``, ``__hash__`` and ``__repr__`` defined
    here are used instead of the recursive ones dataclasses would generate.
    """

    # Set by every subclass's dataclass decorator; declared here so that
    # ``fields()`` accepts any expression type.
    __dataclass_fields__: ClassVar[dict[str, Field[Any]]]

    # Hash of the node, computed once in ``__post_init__``.
    _hash: int

    # Result of ``to_polynomial`` on this node, once computed. Safe to keep
    # because both expressions and polynomials are immutable.
    _cached_polynomial: Polynomial | None = None

    # Whether this expression is parenthesized when nested inside another.
    # Compound expressions are; atoms and ~ set this to False.
    _parenthesize: ClassVar[bool] = True

    def __init_subclass__(cls, *, operator: str | None = None, **kwargs: Any) -> None:
        # A connective names the Python operator that builds it, e.g.
        # `class AND(BooleanExpr, operator="__and__")` makes `a & b` mean
        # AND(a, b). Registering from the subclass side keeps this base
        # class free of imports from its subclasses.
        super().__init_subclass__(**kwargs)
        if operator is not None:
            build = cast(Callable[..., BooleanExpr], cls)
            setattr(BooleanExpr, operator, lambda *operands: build(*operands))

    if TYPE_CHECKING:
        # Static view of the operators registered by ``__init_subclass__``.
        def __and__(self, other: BooleanExpr, /) -> AND: ...
        def __or__(self, other: BooleanExpr, /) -> OR: ...
        def __rshift__(self, other: BooleanExpr, /) -> IfThen: ...
        def __invert__(self) -> Not: ...

    # -- construction -------------------------------------------------------

    def __post_init__(self) -> None:
        self._validate()
        # Children are built first and already carry their hash, so hashing
        # here is O(1) per node and never recurses.
        values = tuple(getattr(self, name) for name in _field_names(type(self)))
        object.__setattr__(self, "_hash", hash((type(self), values)))

    def _validate(self) -> None:
        # Every dataclass field of a connective is a sub-expression.
        # Atoms (variables, constants) override this with their own checks.
        for name in _field_names(type(self)):
            value = getattr(self, name)
            if not isinstance(value, BooleanExpr):
                raise TypeError(
                    f"{type(self).__name__}.{name} must be a "
                    f"BooleanExpr, not {type(value).__name__}"
                )

    # -- traversal ----------------------------------------------------------

    def children(self) -> tuple[BooleanExpr, ...]:
        """Direct sub-expressions, in field order."""
        return tuple(getattr(self, name) for name in _field_names(type(self)))

    def _fold[T](
        self,
        visit: Callable[[BooleanExpr, list[T]], T],
        known: Callable[[BooleanExpr], T | None] | None = None,
    ) -> T:
        """Combine results bottom-up with ``visit(node, child_results)``.

        Runs without recursion. A sub-expression shared by several parents
        (expressions are immutable, so sharing is common) is visited once,
        and its result is released as soon as its last parent has used it,
        so only the results still needed are kept in memory.

        If ``known(node)`` returns a result, it is used as the node's result
        and the node's children are not visited at all.
        """
        found: dict[int, T] = {}

        def resolved(node: BooleanExpr) -> bool:
            if known is None:
                return False
            value = known(node)
            if value is None:
                return False
            found[id(node)] = value
            return True

        # Pass 1: count how many parent edges point at each node.
        uses = {id(self): 1}
        pending: list[BooleanExpr] = [] if resolved(self) else [self]
        while pending:
            for child in pending.pop().children():
                key = id(child)
                if key in uses:
                    uses[key] += 1
                else:
                    uses[key] = 1
                    if not resolved(child):
                        pending.append(child)

        # Pass 2: post-order evaluation on an explicit stack.
        results: dict[int, T] = {}  # id(node) -> result; nodes stay alive via self
        stack: list[tuple[BooleanExpr, bool]] = [(self, False)]
        while stack:
            node, expanded = stack.pop()
            key = id(node)
            if key in results:
                continue
            if key in found:
                results[key] = found.pop(key)
                continue
            children = node.children()
            if expanded or not children:
                values: list[T] = []
                for child in children:
                    child_key = id(child)
                    values.append(results[child_key])
                    uses[child_key] -= 1
                    if not uses[child_key]:
                        del results[child_key]
                results[key] = visit(node, values)
            else:
                stack.append((node, True))
                stack.extend(
                    (child, False)
                    for child in reversed(children)
                    if id(child) not in results
                )
        return results[id(self)]

    def variables(self) -> frozenset[str]:
        """Names of all variables that appear in the expression."""
        names: set[str] = set()
        seen: set[int] = set()
        stack: list[BooleanExpr] = [self]
        while stack:
            node = stack.pop()
            if id(node) in seen:
                continue
            seen.add(id(node))
            names.update(node._own_variables())
            stack.extend(node.children())
        return frozenset(names)

    def substitute(self, mapping: Substitution) -> BooleanExpr:
        """Replace variables by name with expressions (or bools).

        Returns a new expression; variables not in ``mapping`` are kept.
        Unchanged sub-expressions are reused rather than copied.
        """
        return self._fold(lambda node, children: node._rebuild(children, mapping))

    def evaluate(self, assignment: Assignment) -> bool:
        """Truth value under ``assignment``, a mapping of name -> bool."""
        return self._fold(lambda node, values: node._evaluate(values, assignment))

    def to_polynomial(self) -> Polynomial:
        """The unique multilinear polynomial of this boolean function.

        The result is cached on this node, and any sub-expression that
        already has a cached polynomial is not walked again. Only the nodes
        ``to_polynomial`` is called on keep their polynomial: caching every
        intermediate result would hold on to all of them at once.
        """
        poly = self._cached_polynomial
        if poly is None:
            poly = self._fold(
                lambda node, polys: node._polynomial(polys),
                known=lambda node: node._cached_polynomial,
            )
            object.__setattr__(self, "_cached_polynomial", poly)
        return poly

    def __str__(self) -> str:
        type Item = tuple[BooleanExpr, bool]  # (node, nested inside another?)

        def pieces(item: Item) -> list[str | Item]:
            node, nested = item
            parts: list[str | Item] = [
                (part, True) if isinstance(part, BooleanExpr) else part
                for part in node._render_parts()
            ]
            if nested and node._parenthesize:
                return ["(", *parts, ")"]
            return parts

        return _write((self, False), pieces)

    def as_operand(self) -> str:
        """How this expression reads when nested inside another one."""
        text = str(self)
        return f"({text})" if self._parenthesize else text

    # -- per-node hooks -----------------------------------------------------

    def _own_variables(self) -> Sequence[str]:
        return ()

    def _rebuild(
        self, children: Sequence[BooleanExpr], mapping: Substitution
    ) -> BooleanExpr:
        if all(new is old for new, old in zip(children, self.children())):
            return self
        return cast(Callable[..., BooleanExpr], type(self))(*children)

    def _evaluate(self, values: Sequence[bool], assignment: Assignment) -> bool:
        raise NotImplementedError

    def _polynomial(self, polys: Sequence[Polynomial]) -> Polynomial:
        raise NotImplementedError

    def _render_parts(self) -> list[RenderPart]:
        """Text of this node as strings and child expressions, in order.

        Children are rendered as operands (parenthesized where needed).
        """
        raise NotImplementedError

    # -- identity -----------------------------------------------------------

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BooleanExpr):
            return NotImplemented
        seen: set[tuple[int, int]] = set()
        stack: list[tuple[BooleanExpr, BooleanExpr]] = [(self, other)]
        while stack:
            a, b = stack.pop()
            if a is b or (id(a), id(b)) in seen:
                continue
            if type(a) is not type(b) or a._hash != b._hash:
                return False
            seen.add((id(a), id(b)))
            for name in _field_names(type(a)):
                va, vb = getattr(a, name), getattr(b, name)
                if isinstance(va, BooleanExpr):
                    stack.append((va, vb))
                elif va != vb:
                    return False
        return True

    def __repr__(self) -> str:
        def pieces(node: BooleanExpr) -> list[str | BooleanExpr]:
            parts: list[str | BooleanExpr] = [f"{type(node).__name__}("]
            for i, name in enumerate(_field_names(type(node))):
                value = getattr(node, name)
                if i:
                    parts.append(", ")
                parts.append(value if isinstance(value, BooleanExpr) else repr(value))
            parts.append(")")
            return parts

        return _write(self, pieces)
