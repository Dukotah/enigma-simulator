"""The hypothesis catalog: score a library of candidate keystreams against ciphertext.

New for BreakingLiberPrimus.ipynb (not part of the vendored rig). Every candidate is applied
rigidly (key position i deciphers cipher position i), in both directions (C-K and C+K), with
and without Atbash, to the first L runes of each target, and the result is scored with the
quadgram fitness. A same-size null is produced by running the identical catalog against
order-shuffled copies of the targets.

run() takes about a minute on the 55 unsolved segments; make_lp_cache.py stores its output in
lp/cache/catalog.json and load_or_run() reuses it when the parameters match.
"""
import hashlib
import json
import math
import os
import random

from . import ciphers, gematria as gp, score, skipdecode as sk, sources

L = 120
N = gp.N
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache", "catalog.json")
HIST_LO, HIST_HI, HIST_BIN = -10.0, -2.0, 0.02

_Q = score.default()
_D, _FLOOR, _T = _Q.d, _Q.floor, gp.TRANSLIT


def fitness(idxs):
    """Mean quadgram log10-probability of the transliteration; same value as
    score.Quadgram.score_norm, computed without the regex pass."""
    s = "".join(_T[p] for p in idxs)
    n = len(s) - 3
    return sum(_D.get(s[i:i + 4], _FLOOR) for i in range(n)) / n


def library(length=L):
    """List of (name, keystream) candidates."""
    lib = []
    arith = {"primes": ciphers.prime_stream(length + 50),
             "prime-1": ciphers.prime_totient_stream(length + 50),
             "totient(n)": ciphers.totient_stream(length + 50)}
    for name, st in arith.items():
        for o in range(50):
            lib.append((f"{name}@{o}", st[o:o + length]))
    for w in sources.keytext("thematic.txt").split():
        k = gp.keyword_to_indices(w)
        for ph in range(len(k)):
            lib.append((f"vigenere:{w}/{ph}", ciphers.repeat_key(k[ph:] + k[:ph], length)))
    for name in ("solved_plaintext.txt", "self_reliance.txt"):
        K = sk.eng_to_idx(sources.keytext(name))
        for o in range(0, len(K) - length, 100):
            lib.append((f"running:{name}@{o}", K[o:o + length]))
    return lib


def sweep(targets, lib, length=L):
    """Score every (target, candidate, sign, atbash). Returns summary statistics, the top 10
    and a histogram of all scores."""
    nbins = int(round((HIST_HI - HIST_LO) / HIST_BIN))
    hist = [0] * nbins
    n = 0
    s1 = s2 = 0.0
    top = []
    for tname, C in targets:
        C = list(C[:length])
        for atb in (False, True):
            c = [N - 1 - x for x in C] if atb else C
            for kname, K in lib:
                for sign in (-1, 1):
                    sc = fitness([(a + sign * b) % N for a, b in zip(c, K)])
                    n += 1
                    s1 += sc
                    s2 += sc * sc
                    b = int((sc - HIST_LO) / HIST_BIN)
                    hist[min(max(b, 0), nbins - 1)] += 1
                    if len(top) < 10 or sc > top[-1][0]:
                        top.append((sc, tname, kname, sign, atb))
                        top.sort(reverse=True)
                        del top[10:]
    mean = s1 / n
    return {"n": n, "mean": mean, "sd": math.sqrt(max(s2 / n - mean * mean, 0.0)),
            "max": top[0][0], "top": top, "hist": hist}


def shuffled(targets, seed=3301, length=L):
    rng = random.Random(seed)
    out = []
    for name, C in targets:
        c = list(C[:length])
        rng.shuffle(c)
        out.append((name + "/shuffled", c))
    return out


def unsolved_targets():
    return [(f"segment {i}", s) for i, s in enumerate(sources.unsolved_segments())]


def params_key(lib):
    h = hashlib.sha256()
    for name, K in lib:
        h.update(name.encode())
        h.update(bytes(K))
    h.update(sources.stream_sha256(sources.unsolved_stream()).encode())
    h.update(repr((L, HIST_LO, HIST_HI, HIST_BIN)).encode())
    return h.hexdigest()


def run():
    lib = library()
    targets = unsolved_targets()
    return {"params": params_key(lib), "library_size": len(lib),
            "real": sweep(targets, lib), "null": sweep(shuffled(targets), lib)}


def load_or_run(path=CACHE):
    """Return the cached catalog result if its parameters match, else recompute it."""
    lib = library()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            res = json.load(f)
        if res.get("params") == params_key(lib):
            res["source"] = "cache"
            return res
    res = run()
    res["source"] = "computed"
    return res
