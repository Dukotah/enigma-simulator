"""Reference implementations for the exercises in BreakingLiberPrimus.ipynb.

The student notebook leaves these as blanks and uses the versions here in later cells, so the
notebook still runs top to bottom with the blanks unfilled.
"""
from . import ciphers, gematria as gp
from .catalog import fitness


def brute_simple(idxs):
    """Try direct and Atbash, each with every shift in both directions; return the
    candidates sorted best first as (fitness, label, plaintext_indices)."""
    cands = []
    for atb in (False, True):
        base = ciphers.atbash_indices(idxs) if atb else list(idxs)
        for k in range(gp.N):
            for sign in (-1, 1):
                out = [(c + sign * k) % gp.N for c in base]
                label = ("atbash+" if atb else "") + "shift%+d" % (sign * k)
                cands.append((fitness(out), label, out))
    cands.sort(key=lambda x: x[0], reverse=True)
    return cands


def doublet_rate(idxs):
    """Fraction of adjacent positions holding the same rune."""
    return sum(a == b for a, b in zip(idxs, idxs[1:])) / (len(idxs) - 1)
