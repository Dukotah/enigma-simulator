# enigma-simulator

This enigma-simulator project is an educational tool which simulates the
workings of an [Enigma machine][wiki-enigma], the Germans' main military
encryption tool during [World War II][wiki-ww2]. The software allows users to
encrypt and decrypt messages. Additionally, the simulation includes a
step-by-step guide that teaches users how to recover Enigma keys.

This project was created and maintained by the [National Security Agency][nsa].

## Running it

Requires Python 3.10 or newer.

```
git clone https://github.com/NationalSecurityAgency/enigma-simulator
cd enigma-simulator
python -m venv .venv && . .venv/bin/activate     # or: uv venv && . .venv/bin/activate
pip install -r requirements.txt                   # or: uv pip install -r requirements.txt
jupyter notebook BreakingEnigma.ipynb
```

The simulator on its own:

```
>>> from machine import Enigma
>>> e = Enigma('AAA', None, ['I', 'II', 'III'])
>>> e.encipher('AAAAA')
'BDZGO'
```

Tests: `pytest`.

## What the notebook teaches

`BreakingEnigma.ipynb` is the exercise; `MasterEnigmaCracker.ipynb` is the
worked solution. The exercise follows Marian Rejewski's 1930s attack on the
doubly enciphered message key, not the later Bletchley Park bombe:

1. A short tutorial on the simulator (rotors I, II, III, reflector B, plugboard).
2. Each intercepted message starts with its three-letter message key
   enciphered twice under the day key. Letters 1 and 4, 2 and 5, and 3 and 6
   are encryptions of the same plaintext letter, so a day's traffic gives three
   permutations, AD, BE and CF.
3. The cycle structure of those permutations does not depend on the
   plugboard, so it can be looked up in a catalog computed for every rotor order
   and starting position (6 x 26^3 = 105,456 settings).
4. The few settings the catalog returns are tested by decrypting the message
   key and then the messages, which also exposes the plugboard pairs.

## Data files

The notebooks load `chains.pickle` (the cycle-length catalog),
`message_key_encrypts.pickle` and `encrypt1.txt` to `encrypt3.txt`. All of
them are produced by `make_data.py` from the secret settings in `rejewski.py`,
deterministically, so `python make_data.py` regenerates byte-identical copies.
The full catalog build takes about 40 seconds on one core.

## Rotor stepping

The right rotor is the fast rotor and the middle rotor double-steps, as on the
real machine (sequence `ADU -> ADV -> AEW -> BFX` for rotors I, II, III). Ring
settings are fixed at `AAA`. Earlier versions stepped the left rotor fastest
and did not double-step, so their ciphertexts do not match other simulators.
The fix follows the analysis in pull request #6 by Zanion.

## The Liber Primus notebook (fork-only extension)

`BreakingLiberPrimus.ipynb` (exercise, with blanks) and `LiberPrimusSolutions.ipynb`
(worked solutions) apply the same arc to the unsolved pages of Cicada 3301's
*Liber Primus* (2014):

1. Scenario and materials: the 29-rune Gematria Primus, a transcription whose
   unsolved part is checked against a published SHA-256, and the solved pages.
2. The cipher machinery: rune, index and prime; shift, Atbash, Vigenere,
   running-key and prime-stream round trips.
3. Known structure: the six solved pages (A WARNING, SOME WISDOM, the two
   KOANs, WELCOME with key DIVINITY, AN END with the totient-of-primes stream)
   are re-derived and compared with the recorded plaintexts.
4. Statistics the key cannot hide: index of coincidence, frequency flatness,
   and the doublet deficit (adjacent repeated runes far below the random rate,
   which no additive keyed cipher produces).
5. A hypothesis catalog: about a thousand candidate keystreams scored against
   every unsolved segment, compared with the same catalog run on shuffled
   ciphertext, with solved pages as positive controls.
6. An inverted ending: a planted key is recovered, a planted key behind an
   anti-repeat filter is missed by rigid decoding and recovered by a skip-aware
   decoder, and both a one-time pad and a short-seed derived keystream behind
   that filter reproduce the unsolved stream's statistics.

What it is not: it is not a solution, and it does not claim the pages are
unsolvable. The unsolved pages behave like a one-time pad, but a keystream
derived from a short seed is not excluded. The cipher code and data in `lp/`
are vendored from the `liber-primus` rig in
[github.com/Dukotah/cicada3301](https://github.com/Dukotah/cicada3301), with
every data file pinned by SHA-256 in `lp/sources.py`; that repository holds the
full analysis, the methods paper (`PAPER.md`) and open lanes
(`docs/OPEN-LANES.md`). The catalog sweep is cached in `lp/cache/catalog.json`;
`python make_lp_cache.py` rebuilds it (about a minute) and the notebooks
recompute it themselves if it is missing or stale. Each notebook executes in
under a minute with the cache.

This extension is not part of the NSA project and is not endorsed by NSA.

[nsa]: https://www.nsa.gov
[wiki-enigma]: https://en.wikipedia.org/wiki/Enigma_machine
[wiki-ww2]: https://en.wikipedia.org/wiki/World_War_II
