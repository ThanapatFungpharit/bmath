"""Print a catalogue of bmath examples, including edge cases that fail on purpose.

Run with:  uv run python examples/catalogue.py
"""

from analysis import ANALYSIS_SECTIONS
from bmath import BooleanExpr
from edge_cases import EDGE_CASE_SECTIONS
from expressions import EXPRESSION_SECTIONS
from polynomials import POLYNOMIAL_SECTIONS
from variables import Section, Subject

SECTIONS: list[Section] = (
    EXPRESSION_SECTIONS + ANALYSIS_SECTIONS + POLYNOMIAL_SECTIONS + EDGE_CASE_SECTIONS
)


def show(subject: Subject) -> list[str]:
    """Return the lines describing one example, capturing any failure."""
    try:
        value = subject() if callable(subject) else subject
        if not isinstance(value, BooleanExpr):
            return [f"-> {value}"]
        return [f"expr: {value}", f"poly: {value.to_polynomial()}"]
    except Exception as error:  # noqa: BLE001 - showing any failure is the point
        return [f"!! {type(error).__name__}: {error}"]


def main() -> None:
    for title, examples in SECTIONS:
        print(f"== {title} ==")
        for description, subject in examples:
            print(f"  {description}")
            for line in show(subject):
                print(f"    {line}")
        print()


if __name__ == "__main__":
    main()
