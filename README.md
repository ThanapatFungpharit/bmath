# bmath

Boolean expressions, their exact polynomial form, and analysis built on it.

Every boolean function has exactly one multilinear polynomial over the
integers (using x^2 = x). bmath converts expressions into that polynomial,
which makes equivalence, tautology and variable-dependence checks exact.

## Building expressions

```python
from bmath import BooleanVariable, TRUE, FALSE, Iff

x, y, z = BooleanVariable("x"), BooleanVariable("y"), BooleanVariable("z")

expr = (x & y) | ~z >> x  # see the precedence note below
print(expr)  # (x & y) | (~z -> x)
print(expr.to_polynomial())  # x + z - xz
```

| Connective | Class | Operator | Rendered |
|---|---|---|---|
| negation | `Not(a)` | `~a` | `~a` |
| conjunction | `AND(a, b)` | `a & b` | `a & b` |
| disjunction | `OR(a, b)` | `a \| b` | `a \| b` |
| implication | `IfThen(a, b)` | `a >> b` | `a -> b` |
| biconditional | `Iff(a, b)` | - | `a <=> b` |
| constants | `TRUE`, `FALSE` | - | `T`, `F` |

Operators follow **Python** precedence: `~` > `>>` > `&` > `|`.
So `a | b >> c` is `a | (b -> c)`; write `(a | b) >> c` for the usual reading.

Variable names must be ASCII Python identifiers (`x`, `rain`, `v0`).
All output is plain ASCII, with the symbols in the table above. Polynomials
write products side by side (`2xy`), using `*` when a name is longer than
one character (`2*rain*wind`, `v0*v1`).
Expressions are immutable and hashable.

Every operation walks the expression with an explicit loop rather than
recursion, so expressions of any depth work without touching Python's
recursion limit. A sub-expression reused in several places is processed once
(except by `str` and `repr`, which write it out each time).

## Working with expressions

```python
expr.variables()  # frozenset({'x', 'y', 'z'})
expr.evaluate({"x": True, "y": False, "z": False})  # True
expr.substitute({"z": x | y})  # replace variables by expressions or bools
expr.children()  # direct sub-expressions
```

## Analysis

```python
from bmath import (
    is_tautology,
    is_contradiction,
    is_satisfiable,
    equivalent,
    dependent_variables,
    redundant_variables,
    satisfying_assignment,
    counterexample,
    truth_table,
)

is_tautology(((x >> y) & (y >> z)) >> (x >> z))  # True
equivalent(~(x & y), ~x | ~y)  # True

demo = (((x | ~x) & y) & z) | z
dependent_variables(demo)  # frozenset({'z'})
redundant_variables(demo)  # frozenset({'x', 'y'})

counterexample(x >> y)  # {'x': True, 'y': False}
satisfying_assignment(x & ~x)  # None
```

`truth_table` lists the rows of an expression. A variable the result does not
depend on is shown as `*` instead of doubling the rows:

```python
print(truth_table((x & y) | x))
# x y result
# 1 * 1
# 0 * 0

table = truth_table(x | y)
table.variables  # ('x', 'y')
table.rows[0]  # Row(inputs=(True, True), result=True); None marks a *

# Look up a result like a dict; only dependent variables are needed.
t = truth_table((x & y) | x)
t.get({"x": True})  # True (y is independent, so it may be left out)
t.get({"y": True})  # None: x is missing (t[...] raises KeyError instead)
t.get({"y": True}, False)  # False, the default
```

All of these are exact. They are computed from the polynomial, whose size can
grow exponentially with the number of variables (for example, an OR of *n*
variables has 2^n - 1 terms), so they are intended for small and medium inputs.

Some things keep the cost down:

- **Early exits.** `is_tautology`, `is_contradiction`, `is_satisfiable` and
  `equivalent` first evaluate the expression at a few fixed assignments. One
  wrong value settles the answer as False without building a polynomial.
  Tautologies of `&` (and contradictions of `|`, `->`) are checked one side at a
  time, stopping at the first side that fails.
- **Caching.** `to_polynomial()` stores its result on the expression it was
  called on. Later calls, and any larger expression containing it, reuse it.
- **Dense products.** Multiplying two polynomials that are dense over the same
  *V* variables takes O(*V* * 2^*V*) through their truth tables rather than
  O(4^*V*) term by term (integer and fraction coefficients only).

Note that `str` and `repr` write shared sub-expressions out in full, so their
output can be exponentially longer than the expression.

## Polynomials

```python
from bmath import Polynomial

p = Polynomial.variable("x")
q = Polynomial.variable("y")
print(2 * p * q - p + 1)  # 1 - x + 2xy
(p * ~p) == 0  # True
(p + q).variables()  # frozenset({'x', 'y'})
(p + q).evaluate({"x": 1, "y": 1})  # 2
```

## Development

```sh
uv run python examples/catalogue.py          # print the example catalogue
uv run python -m unittest discover -s tests  # run the tests
uv run mypy                                   # type-check (strict) src, tests and examples
```
