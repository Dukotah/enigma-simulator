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

[nsa]: https://www.nsa.gov
[wiki-enigma]: https://en.wikipedia.org/wiki/Enigma_machine
[wiki-ww2]: https://en.wikipedia.org/wiki/World_War_II
