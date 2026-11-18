"""Monomials stored as bitmasks.

Inside a ``Polynomial`` a monomial is an ``int`` whose set bits are its
variables. Each variable name gets a bit index the first time it is seen,
and keeps it for the life of the process. The product of two monomials
(x*x = x) is then ``a | b`` and the degree is ``mask.bit_count()``: both
are single machine-level operations instead of frozenset unions and hashes.

Masks are an internal detail. The public API still speaks in frozensets of
names (``Monomial``), and pickled polynomials store names, since bit indices
differ between processes.
"""

import threading
from collections.abc import Iterable, Iterator

_INDEX: dict[str, int] = {}
_NAMES: list[str] = []
_LOCK = threading.Lock()


def bit(name: str) -> int:
    """The single-bit mask of variable ``name``, registering it if new."""
    try:
        return 1 << _INDEX[name]
    except KeyError:
        with _LOCK:
            index = _INDEX.setdefault(name, len(_NAMES))
            if index == len(_NAMES):
                _NAMES.append(name)
        return 1 << index


def mask_of(names: Iterable[str]) -> int:
    """The mask of a product of variables."""
    mask = 0
    for name in names:
        mask |= bit(name)
    return mask


def indices(mask: int) -> Iterator[int]:
    """Bit indices set in ``mask``, lowest first. Costs O(set bits)."""
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def names_of(mask: int) -> frozenset[str]:
    """The variable names in a mask."""
    return frozenset(_NAMES[index] for index in indices(mask))
