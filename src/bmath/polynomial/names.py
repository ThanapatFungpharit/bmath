def validate_variable_name(name: object) -> str:
    """Return ``name`` if it is a usable variable name, otherwise raise.

    Names must be ASCII identifiers (letters, digits and underscores, not
    starting with a digit) so that rendered text is unambiguous plain ASCII.
    """
    if not isinstance(name, str):
        raise TypeError(f"variable name must be a str, not {type(name).__name__}")
    if not (name.isascii() and name.isidentifier()):
        raise ValueError(
            f"invalid variable name {name!a}: must be an identifier "
            "(ASCII letters, digits, underscores; not starting with a digit)"
        )
    return name


_DIGITS = "0123456789"


def split_name(name: str) -> tuple[str, str]:
    """Split a name into its base and trailing digits: ``"v12"`` -> ``("v", "12")``.

    A name made only of a base keeps empty digits; a name whose base would be
    empty (impossible for identifiers) is returned whole.
    """
    base = name.rstrip(_DIGITS)
    if not base:
        return name, ""
    return base, name[len(base) :]


def display_name(name: str) -> str:
    """How a variable name is displayed: as itself, so ``v12`` reads ``v12``."""
    return name


def name_order(name: str) -> tuple[str, int, str]:
    """Sort key putting ``v2`` before ``v10`` (natural order)."""
    base, digits = split_name(name)
    return base, int(digits) if digits else -1, name
