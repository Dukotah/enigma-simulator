"""Vendored data files, pinned by SHA-256, and loaders for them.

Every file under lp/data/ was copied byte-for-byte from github.com/Dukotah/cicada3301
(commit 6b945291). The pins below are checked by verify(); the ciphertext pin is the one
published in that repository's liber-primus/PROBLEM.json.

  krisyotam_runes.txt   transcription of the whole Liber Primus, pages separated by '%'
                        (rtkd/iddqd 2017 community transcription lineage, krisyotam copy)
  scream314_lp.md       scream314's page-by-page write-up with the solved pages' transforms
                        (github.com/scream314/cicada3301), parsed by lp.corpus
  english_quadgrams.txt quadgram counts from public-domain Project Gutenberg texts
                        (KJV, Moby Dick, Pride and Prejudice, War and Peace)
  PROBLEM.json          the rig's machine-readable statement of the unsolved problem
  SOLVED-PAGES.json     the rig's derived plaintexts of the solved pages
  keys/                 candidate key material: Emerson's Self-Reliance (public domain),
                        the solved-page plaintexts, and a list of thematic keywords
"""
import hashlib
import json
import os

from . import gematria as gp

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

PINS = {
    "english_quadgrams.txt": "fb82963d1fc4a64b9fc6121f8ca88139fd5b15083dddc9a59f8b14bdb8fe4062",
    "krisyotam_runes.txt": "9b211a06a4bc31d60516edfad274f145aca0d8bc397d88889313d67adf0cbc55",
    "scream314_lp.md": "0f7545d470f2056b45b5de2c8c116ecdea66969fdca6be57ccbd8e591e40ee92",
    "PROBLEM.json": "0b3dc541ab9b4722cb54ad4643bc0f85d3bbce5548008aaea701b34120207e52",
    "SOLVED-PAGES.json": "cd3c6d55800375dea4d5d95f87f758ba5e832396e63fb2130f1079eb63bafc85",
    "keys/self_reliance.txt": "b2f3dbd3866e0bec5ae41ac29df09b537c2ef18fa1b88678966587b824ca92f0",
    "keys/solved_plaintext.txt": "821cb3c89872bc33114055c9cdf81c7b38b33d3ac5711eaf753eeebaeefc6473",
    "keys/thematic.txt": "f9db06ae01ed8437b98eeedaafe002fabab1665752b3be55c2ce5e25ba205d7f",
}


def sha256_file(name):
    with open(os.path.join(DATA, name), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def verify():
    """Return {file: True/False} for every pinned data file."""
    return {name: sha256_file(name) == pin for name, pin in PINS.items()}


def stream_sha256(idxs):
    """The ciphertext identity used in PROBLEM.json: sha256 of the comma-joined indices."""
    return hashlib.sha256(",".join(map(str, idxs)).encode()).hexdigest()


def problem():
    with open(os.path.join(DATA, "PROBLEM.json"), encoding="utf-8") as f:
        return json.load(f)


def solved_pages():
    with open(os.path.join(DATA, "SOLVED-PAGES.json"), encoding="utf-8") as f:
        return json.load(f)


def segments():
    """All 57 rune segments of LP2 as lists of indices: [:-2] are the unsolved
    segments 0-54, [-2] is AN END (solved), [-1] is PARABLE (plaintext)."""
    with open(os.path.join(DATA, "krisyotam_runes.txt"), encoding="utf-8") as f:
        text = f.read()
    pages = [gp.runes_to_indices(s) for s in text.split("%")]
    return [p for p in pages if p]


def unsolved_segments():
    return segments()[:-2]


def unsolved_stream():
    """The 12,956-rune unsolved stream, flattened."""
    return [i for seg in unsolved_segments() for i in seg]


def keytext(name):
    with open(os.path.join(DATA, "keys", name), encoding="utf-8", errors="ignore") as f:
        return f.read()
