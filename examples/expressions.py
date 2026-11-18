from bmath import AND, FALSE, OR, TRUE, Iff, IfThen, Not
from variables import Section, w, x, y, z

# (section title, [(description, expression), ...])
EXPRESSION_SECTIONS: list[Section] = [
    (
        "Basics",
        [
            ("variable", x),
            ("negation", Not(x)),
            ("conjunction", AND(x, y)),
            ("disjunction", OR(x, y)),
            ("implication", IfThen(x, y)),
        ],
    ),
    (
        "Identities",
        [
            ("idempotence of AND", AND(x, x)),
            ("idempotence of OR", OR(x, x)),
            ("double negation", Not(Not(x))),
            ("absorption: x & (x | y)", AND(x, OR(x, y))),
            ("absorption: x | (x & y)", OR(x, AND(x, y))),
        ],
    ),
    (
        "Tautologies (should reduce to 1)",
        [
            ("excluded middle", OR(x, Not(x))),
            ("self-implication", IfThen(x, x)),
            ("modus ponens", IfThen(AND(x, IfThen(x, y)), y)),
            ("contraposition", IfThen(IfThen(x, y), IfThen(Not(y), Not(x)))),
            (
                "hypothetical syllogism",
                IfThen(AND(IfThen(x, y), IfThen(y, z)), IfThen(x, z)),
            ),
        ],
    ),
    (
        "Contradictions (should reduce to 0)",
        [
            ("non-contradiction", AND(x, Not(x))),
            ("negated excluded middle", Not(OR(x, Not(x)))),
        ],
    ),
    (
        "De Morgan",
        [
            ("~(x & y)", Not(AND(x, y))),
            ("~x | ~y", OR(Not(x), Not(y))),
            ("~(x | y)", Not(OR(x, y))),
            ("~x & ~y", AND(Not(x), Not(y))),
        ],
    ),
    (
        "Derived connectives",
        [
            ("exclusive or", OR(AND(x, Not(y)), AND(Not(x), y))),
            ("XNOR / biconditional", AND(IfThen(x, y), IfThen(y, x))),
            ("NAND", Not(AND(x, y))),
            ("NOR", Not(OR(x, y))),
            (
                "3-way exclusive or",
                OR(
                    AND(OR(AND(x, Not(y)), AND(Not(x), y)), Not(z)),
                    AND(Not(OR(AND(x, Not(y)), AND(Not(x), y))), z),
                ),
            ),
        ],
    ),
    (
        "Constants and the Iff connective",
        [
            ("true constant", TRUE),
            ("x & T", AND(x, TRUE)),
            ("x | T", OR(x, TRUE)),
            ("x -> F", IfThen(x, FALSE)),
            ("biconditional connective", Iff(x, y)),
            ("Iff chain", Iff(Iff(x, y), z)),
        ],
    ),
    (
        "Larger expressions",
        [
            ("majority of 3", OR(OR(AND(x, y), AND(y, z)), AND(x, z))),
            ("distributivity", AND(x, OR(y, z))),
            ("4-variable OR", OR(OR(x, y), OR(z, w))),
            ("implication chain (right-nested)", IfThen(x, IfThen(y, IfThen(z, w)))),
            ("implication chain (left-nested)", IfThen(IfThen(IfThen(x, y), z), w)),
            ("original demo", OR(AND(AND(OR(x, Not(x)), y), z), z)),
        ],
    ),
]
