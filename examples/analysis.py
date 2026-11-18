from collections.abc import Iterable

from bmath import (
    AND,
    OR,
    Iff,
    Not,
    counterexample,
    dependent_variables,
    equivalent,
    is_contradiction,
    is_satisfiable,
    is_tautology,
    redundant_variables,
    satisfying_assignment,
    truth_table,
)
from variables import Section, w, x, y, z

demo = OR(AND(AND(OR(x, Not(x)), y), z), z)
syllogism = ((x >> y) & (y >> z)) >> (x >> z)


def _names(names: Iterable[str]) -> str:
    return "{" + ", ".join(sorted(names)) + "}"


# (section title, [(description, thunk), ...])
ANALYSIS_SECTIONS: list[Section] = [
    (
        "Analysis: tautology, contradiction, satisfiability",
        [
            ("is_tautology(x | ~x)", lambda: is_tautology(x | ~x)),
            ("is_tautology(hypothetical syllogism)", lambda: is_tautology(syllogism)),
            ("is_tautology(x -> y)", lambda: is_tautology(x >> y)),
            ("is_contradiction(x & ~x)", lambda: is_contradiction(x & ~x)),
            ("is_satisfiable(~(x <=> y))", lambda: is_satisfiable(~Iff(x, y))),
            (
                "is_satisfiable(~(x <=> y) & (x <=> y))",
                lambda: is_satisfiable(~Iff(x, y) & Iff(x, y)),
            ),
        ],
    ),
    (
        "Analysis: equivalence",
        [
            (
                "De Morgan: ~(x & y) == ~x | ~y",
                lambda: equivalent(~(x & y), ~x | ~y),
            ),
            (
                "~(x <=> y) == (x & ~y) | (~x & y)",
                lambda: equivalent(~Iff(x, y), (x & ~y) | (~x & y)),
            ),
            (
                "x <=> y == (x -> y) & (y -> x)",
                lambda: equivalent(Iff(x, y), (x >> y) & (y >> x)),
            ),
            ("x -> y == y -> x ?", lambda: equivalent(x >> y, y >> x)),
            (
                "x -> y == ~y -> ~x (contrapositive)",
                lambda: equivalent(x >> y, ~y >> ~x),
            ),
        ],
    ),
    (
        "Analysis: which variables matter",
        [
            (f"mentioned in {demo}", lambda: _names(demo.variables())),
            ("  ...actually depends on", lambda: _names(dependent_variables(demo))),
            ("  ...redundant", lambda: _names(redundant_variables(demo))),
            (
                "redundant in x -> (y -> x)",
                lambda: _names(redundant_variables(x >> (y >> x))),
            ),
            (
                "depends on, (x & y) | (x & ~y) | (w & ~w)",
                lambda: _names(dependent_variables((x & y) | (x & ~y) | (w & ~w))),
            ),
        ],
    ),
    (
        "Analysis: witnesses",
        [
            (
                "satisfying_assignment(x & ~y & z)",
                lambda: satisfying_assignment(x & ~y & z),
            ),
            ("satisfying_assignment(x & ~x)", lambda: satisfying_assignment(x & ~x)),
            ("counterexample(x -> y)", lambda: counterexample(x >> y)),
            (
                "counterexample((x | y) -> (x & y))",
                lambda: counterexample((x | y) >> (x & y)),
            ),
            ("counterexample(x | ~x)", lambda: counterexample(x | ~x)),
        ],
    ),
    (
        "Expressions: evaluate and substitute",
        [
            (
                "(x -> y) <=> z at x=1, y=0, z=1",
                lambda: Iff(x >> y, z).evaluate({"x": True, "y": False, "z": True}),
            ),
            ("evaluate with a missing variable", lambda: (x & y).evaluate({"x": True})),
            (
                "(x & y) | z with z := ~(x <=> y)",
                lambda: ((x & y) | z).substitute({"z": ~Iff(x, y)}),
            ),
            (
                "(x & y) | z with x := True",
                lambda: ((x & y) | z).substitute({"x": True}),
            ),
            (
                "is_tautology(x | y with y := ~x)",
                lambda: is_tautology((x | y).substitute({"y": ~x})),
            ),
        ],
    ),
    (
        "Analysis: truth tables (* = the result does not depend on it)",
        [
            (
                "truth_table((x & y) | x)",
                lambda: "\n" + str(truth_table((x & y) | x)),
            ),
            ("truth_table(x | y)", lambda: "\n" + str(truth_table(x | y))),
            ("truth_table(x <=> y)", lambda: "\n" + str(truth_table(Iff(x, y)))),
            ("truth_table(demo)", lambda: "\n" + str(truth_table(demo))),
        ],
    ),
]
