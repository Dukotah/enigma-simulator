# Vendored from github.com/Dukotah/cicada3301 liber-primus/analysis/campaign18_skip/skipdecode.py (commit 6b945291). Imports made package-relative; the gate() demo is dropped (the notebooks run it).
"""Campaign XVIII -- filter-aware, skip-tolerant re-decode (open item 2c).

THESIS.  Campaigns X/XI proved LP2's cipher is an OTP whose output was passed
through an ACTIVE, plaintext-aware doublet-suppression filter (~83% strong): the
only model that reproduces both observed statistics (doublet 0.66%, IoC.N 1.00).
The natural mechanism for that is KEY-SKIP: when enciphering, if the next output
rune would equal the previous one, advance (skip) the key symbol ~83% of the time
and try the next. That DESYNCHRONISES the key from the plaintext after the first
skip (~1 per 35 runes). Consequence: every prior keytext test -- all 112+ of them --
assumed RIGID 1:1 alignment, so *even the correct keytext* would decode to English
for ~30 runes and then turn to noise, scoring as a null over the full page.

This module (1) builds the key-skip encipher model, (2) builds a beam decoder that
tracks the desync, and (3) VALIDATES on synthetic ciphertext that the beam recovers
a known key which the rigid decoder misses -- the project's mandatory gate before
any null or hit is trusted. The corpus sweep lives in sweep.py and only runs if the
gate passes here.

"""
import random

from . import gematria as gp
from . import score as _score

N = gp.N
Q = _score.default()                   # quadgram model (.d dict, .floor)


# ----------------------------------------------------------------- encoding
_ALIAS = {"V": 1, "K": 5, "Z": 15, "Q": 5}


def eng_to_idx(text):
    """English/Latin text -> Gematria indices, greedy multi-letter runes.
    Lenient: any char that is neither a mappable letter nor an alias is
    dropped (spaces, punctuation, digits, newlines) -- same as reading the
    running key off the letters only."""
    s = text.upper()
    out, i, n = [], 0, len(s)
    while i < n:
        for t, idx in gp._TRANS_SORTED:
            if s.startswith(t, i):
                out.append(idx); i += len(t); break
        else:
            a = _ALIAS.get(s[i])
            if a is not None:
                out.append(a)
            i += 1
    return out


def idx_to_trans(idxs):
    return "".join(gp.IDX_TO_TRANS[i % N] for i in idxs)


# ---------------------------------------------------------- encipher models
def encipher_keyskip(P, K, sign=-1, supp=0.83, seed=3301):
    """Model A. Encipher plaintext indices P under keystream K so that the
    DECODE relation is p = (c + sign*k) mod N (matches lp.ciphers).

    Key-skip filter: if the emitted rune would double the previous emitted rune,
    reject this key symbol (advance the key) with probability `supp` and retry.
    Returns (ciphertext_indices, skip_counts, key_indices_used)."""
    rng = random.Random(seed)
    C, skips, used = [], [], []
    j, c_prev = 0, None
    for p in P:
        nsk = 0
        while True:
            c = (p - sign * K[j]) % N          # invert p = c + sign*k
            if c_prev is not None and c == c_prev and rng.random() < supp:
                j += 1
                nsk += 1
                continue
            break
        C.append(c); skips.append(nsk); used.append(j)
        j += 1
        c_prev = c
    return C, skips, used


# --------------------------------------------------------------- beam decode
def _quad_delta(tl, add, floor, d):
    """Score of quadgrams newly completed when `add` is appended to `tl`."""
    L1 = len(tl)
    s = tl + add
    L2 = len(s)
    tot = 0.0
    for e in range(max(4, L1 + 1), L2 + 1):     # e = end (exclusive) of a quad
        tot += d.get(s[e - 4:e], floor)
    return tot


def beam_decode(C, K, sign=-1, o=0, beam_w=400, max_skip=3):
    """Skip-tolerant beam decode of ciphertext C under keystream K starting at
    key offset `o`. Recovers the most English-like plaintext consistent with the
    key-skip model. Returns dict(score, plain_idx, ptr_end, translit)."""
    d, floor = Q.d, Q.floor
    if o + len(C) + max_skip * len(C) >= len(K):
        # not enough key material for worst-case skipping
        Kx = K + [0] * (len(C) * (max_skip + 1) + 8)
    else:
        Kx = K
    # hypothesis: (cumscore, last_accepted_key_index, translit, plain_idx, c_prev)
    p0 = (C[0] + sign * Kx[o]) % N
    t0 = gp.IDX_TO_TRANS[p0]
    beams = [(0.0, o, t0, [p0], C[0])]
    for i in range(1, len(C)):
        ci = C[i]
        nxt = []
        for (sc, pa, tl, pidx, cprev) in beams:
            for dsk in range(0, max_skip + 1):
                acc = pa + 1 + dsk               # accepted key index
                if acc >= len(Kx):
                    break
                p = (ci + sign * Kx[acc]) % N
                # validity: each skipped key would have produced a doubled rune
                ok = True
                for m in range(pa + 1, acc):
                    if (p - sign * Kx[m]) % N != cprev:
                        ok = False
                        break
                if not ok:
                    continue
                add = gp.IDX_TO_TRANS[p]
                nsc = sc + _quad_delta(tl, add, floor, d)
                nxt.append((nsc, acc, tl + add, pidx + [p], ci))
        if not nxt:
            break
        nxt.sort(key=lambda x: x[0], reverse=True)
        beams = nxt[:beam_w]
    best = max(beams, key=lambda x: x[0])
    tl = best[2]
    # Report on the PROJECT's canonical scale (score_norm), so results are
    # directly comparable to the ledger's English -4.0 / thresh -5.2 / noise -7.5.
    return {"score": Q.score_norm(tl), "beam_score": best[0], "plain_idx": best[3],
            "ptr_end": best[1], "translit": tl}


def rigid_decode(C, K, sign=-1, o=0):
    """Classic 1:1 running-key decode (what every prior test did)."""
    p = [(C[i] + sign * K[o + i]) % N for i in range(len(C))]
    tl = idx_to_trans(p)
    return {"score": Q.score_norm(tl), "plain_idx": p, "translit": tl}
