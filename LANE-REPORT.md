# LANE 1 report: enigma-simulator

## 1. Upstream contribution rules

- Upstream has no CONTRIBUTING.md (checked `upstream/master` tree and the
  NationalSecurityAgency/.github org repo, which only holds workflow templates).
- License: MIT plus the US-Government public-domain notice in `LICENSE`; kept unchanged.
- Upstream has been inactive since 2020-08; the maintainer said publicly there is no domain
  expert to review changes. Nothing was opened upstream (lane rule 2).

## 2. What changed

### Branch `lane/restore-and-fix` (upstream-shaped, one commit on `upstream/master`)

- `machine.py`: the right rotor is now the fast rotor and the signal enters there; new
  `Enigma.step_rotors()` adds the middle-rotor double step. Before, the left rotor stepped
  fastest and nothing double-stepped, so ciphertexts disagreed with every other simulator
  (issue #5). Re-implements the analysis of PR #6 (Zanion, 2019, never merged); credited in the
  commit body.
- `tests/test_machine.py` + `pytest.ini`: known-answer tests. Vectors were derived by running the
  independent `py-enigma` package (EnigmaMachine, reflector B, rings AAA) and include the
  standard `AAAAA@AAA -> BDZGO`, PR #6's `MEU -> GDXTZ`, the double-step sequences
  `ADU->ADV->AEW->BFX` and `KDO->...->LFU`, a plugboard case, a 700-letter stream, and the
  16,900 period. 11 of 13 tests fail on the old code.
- `make_data.py`: regenerates the never-committed `chains.pickle`, `message_key_encrypts.pickle`
  and `encrypt1-3.txt` (issues #2, #3) deterministically from `rejewski.py`'s secrets. It
  enciphers all 26 plaintext letters per setting instead of sampling random message keys, so the
  full 105,456-setting catalog builds in about 40 to 100 s, not the ~15 min the brief expected. A
  `--quick` mode was therefore not needed and was dropped (a partial catalog also broke the
  notebook's example lookup). The files total 2.5 MB and are committed.
- Notebooks: kernelspec Python 3, outputs refreshed with the fixed machine, stale text fixed
  ("four" encrypt files, `'ZEUATW'`, "2" candidates: with the fixed machine the secret's index
  maps to 1 catalog entry), the master's file-writing cells now compare against the shipped files,
  and the author's TODO cell was removed. `rejewski.py` and the master notebook: `i is 1` ->
  `i == 1` (SyntaxWarning on 3.8+).
- `README.md` run instructions (issue #1), `requirements.txt` pinned, `.gitignore`,
  `.github/workflows/ci.yml` (pytest on 3.10-3.13, byte-identical data regeneration check, both
  notebooks executed).

### Branch `lane/liber-primus` (fork-only, on top of the above)

- `BreakingLiberPrimus.ipynb` (6 exercise blanks) and `LiberPrimusSolutions.ipynb`: the Enigma
  arc applied to Cicada 3301's Liber Primus: scenario, rune machinery and cipher round trips,
  six solved pages re-derived and compared with `SOLVED-PAGES.json`, IoC / flatness / doublet
  deficit (86 vs 446.7 expected, z = -17.37), a 991-candidate keystream catalog (218,020 decodes)
  against a same-size shuffled null with AN END / WELCOME / KOAN as positive controls, and the
  inverted ending: plant-and-recover, rigid vs skip-aware decoding under the anti-repeat filter,
  and pad vs SHA-256-derived keystream reproducing LP2's signature, closing with the rig's
  verbatim `current_verdict` (OTP-class, not "information-theoretically unsolvable"). Every
  printed number is computed in the notebook; no TODOs.
- `lp/`: minimal package vendored from `Dukotah/cicada3301` `liber-primus` (commit 6b945291):
  gematria, ciphers, stats, score, solve, corpus, skipdecode (path changes only), plus new
  `sources.py` (SHA-256 pins for all 8 data files and the PROBLEM.json stream identity),
  `catalog.py`, `reference.py`. Copyrighted keytexts (Gibson's *Agrippa*, Crowley) were
  deliberately NOT vendored; only Self-Reliance (PD), the solved-page text and a keyword list.
- `lp/cache/catalog.json` + `make_lp_cache.py`: the ~1 min catalog sweep is cached and
  parameter-hashed; notebooks recompute if stale. `tests/test_lp.py`, CI executes both LP
  notebooks, README section including what the notebook is NOT.

## 3. Evidence

```
$ python -m pytest -q                      # branch A
13 passed in 5.89s
$ git stash; python -m pytest -q           # old machine.py
11 failed, 2 passed in 4.52s
$ python make_data.py                      # run twice, git diff empty both times
catalog: 17576 day keys x 6 rotor orders -> 20680 distinct indices in 96 s
chains.pickle                    2487687 bytes  sha256 a188d1485b6e1469
message_key_encrypts.pickle         7243 bytes  sha256 67e11c2633b3fb35
CI run 44219117769 (lane/restore-and-fix): test (3.10) (3.11) (3.12) (3.13) all passed,
including "Data files are reproducible" and both notebooks executing.

CI run 44219489694 (lane/liber-primus): 3.10-3.13 all passed, all four notebooks executed.
$ python -m pytest -q                      # branch B
21 passed in 12.95s
$ jupyter nbconvert --execute --inplace LiberPrimusSolutions.ipynb   # 40 s
$ jupyter nbconvert --execute --inplace BreakingLiberPrimus.ipynb    # 47 s
$ python make_lp_cache.py
991 candidates; 218020 real and 218020 null decodes in 54 s  (max RSS 25.7 MB)
Notebook excerpts:
  sha256 of the stream: 023312066df4...af1585   matches PROBLEM.json: True
  03.jpg  Vigenere DIVINITY  7 interrupters, fitness -4.344   matches SOLVED-PAGES.json: True
  73.jpg  totient of the primes, p-1  1 interrupters, fitness -4.573
  doublets observed 86, expected for random 446.7, z = -17.37
  max of the same-size shuffled null: -6.207   max of the real catalog: -6.330
  73.jpg  best prime-1@0  fitness -5.282  above the null max: True
  correct key, rigid decode     fitness -7.524  runes recovered  14.1 %
  correct key, skip-aware beam  fitness -4.478  runes recovered 100.0 %
  one-time pad + filter         doublets 0.61 %  IoC*29 1.0001
  SHA-256(short seed) + filter  doublets 0.58 %  IoC*29 0.9994
  LP2 unsolved                  doublets 0.66 %  IoC*29 0.9999
```

## 4. Competing work

- Issue #1 (no run instructions), #2 (closed, file missing), #3 (`message_key_encrypts.pickle`
  missing), #5 (wrong encryption): all addressed by branch A.
  https://github.com/NationalSecurityAgency/enigma-simulator/issues
- PR #6 (Zanion, 2019-open): stepping direction + double step + pytest. Branch A re-implements
  it (same fix, cleaner double-step logic in `Enigma.step_rotors`, more vectors) and adds the data
  and docs PR #6 lacked. https://github.com/NationalSecurityAgency/enigma-simulator/pull/6
- PR #7 (merged) corrected a wiring table; already in the base.

## 5. Draft upstream PR text

**Title:** Fix rotor stepping and double step; restore notebook data files; add tests and CI

**Body:**

The simulator stepped the left rotor fastest and never double-stepped the middle rotor, so
its output did not match a real Enigma I (#5). This PR makes the right rotor the fast rotor,
feeds the signal in there, and adds the double step, following the analysis in #6 by
@Zanion. Known-answer tests cover `AAAAA` at `AAA` -> `BDZGO`, the double-step sequence
`ADU -> ADV -> AEW -> BFX`, a plugboard case and a 700-letter stream, cross-checked against
the independent py-enigma package.

The notebooks load `chains.pickle`, `message_key_encrypts.pickle` and `encrypt1-3.txt`, which
were never committed (#2, #3). `make_data.py` regenerates them deterministically from the
secrets in `rejewski.py` (about a minute for the full catalog), and the 2.5 MB of output is
committed so the exercise runs from a clone. The README now explains how to run it (#1), the
notebooks use a Python 3 kernel with refreshed outputs, and CI runs pytest on 3.10-3.13,
checks the data files regenerate byte-identically, and executes both notebooks.

Fixes #1, #3, #5. Supersedes #6.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

(Owner: the `@Zanion` mention will notify that user; keep it only if you want to.)

## 6. Land probability and next steps

**Low.** The repo has been silent since 2020 and the maintainer has said there is nobody to
review Enigma changes, so the PR would likely sit like #6 has.

Owner next steps:
1. Optionally open the PR above from `lane/restore-and-fix` (one commit on upstream/master).
2. Link `BreakingLiberPrimus.ipynb` on `lane/liber-primus` from the cicada3301 README (and
   `docs/OPEN-LANES.md` as an on-ramp); consider making `lane/liber-primus` the fork's showcase
   branch or merging it into a non-default branch people land on.
3. Maybe post it (the "Rejewski's method vs. the Liber Primus, with an inverted ending" angle).
4. Licensing note: `lp/data/` carries third-party transcriptions (rtkd/krisyotam, scream314) as
   your cicada3301 repo already does; confirm you are comfortable with that in this fork.
