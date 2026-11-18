'''
Checks for the vendored Liber Primus toolkit used by BreakingLiberPrimus.ipynb: the data files
match their SHA-256 pins, the unsolved stream matches the identity published in PROBLEM.json,
and the solved pages are re-derived exactly (following liber-primus/tests/validate.py in
github.com/Dukotah/cicada3301).
'''
import json

import pytest

from lp import catalog, ciphers, corpus, gematria as gp, solve, sources
from lp.reference import brute_simple

SOLVED = {p['page_label']: p['plaintext_transliteration'] for p in sources.solved_pages()['pages']}


def test_data_pins():
    assert all(sources.verify().values())


def test_unsolved_stream_identity():
    u = sources.unsolved_stream()
    ident = sources.problem()['ciphertext_identity']
    assert len(u) == ident['n_runes']
    assert sources.stream_sha256(u) == ident['sha256_of_comma_joined_indices']


@pytest.mark.parametrize('label', ['Runes - 01.jpg', '05.jpg', '06.jpg'])
def test_simple_pages(label):
    _, _, out = brute_simple(gp.runes_to_indices(corpus.page_by_label(label)['runes']))[0]
    assert gp.indices_to_translit(out) == SOLVED[label]


@pytest.mark.parametrize('label, stream', [
    ('03.jpg', lambda n: ciphers.repeat_key(gp.keyword_to_indices('DIVINITY'), n)),
    ('14.jpg', lambda n: ciphers.repeat_key(gp.keyword_to_indices('FIRFUMFERENFE'), n)),
])
def test_keystream_pages(label, stream):
    runes = corpus.page_by_label(label)['runes']
    res = solve.find_interrupters(runes, stream(len(gp.runes_to_indices(runes))), sign=-1, beam_width=500)
    assert res['plaintext'] == SOLVED[label]


def test_catalog_cache_is_current():
    with open(catalog.CACHE, encoding='utf-8') as f:
        assert json.load(f)['params'] == catalog.params_key(catalog.library())
