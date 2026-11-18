"""Minimal Liber Primus toolkit used by BreakingLiberPrimus.ipynb.

The modules are vendored, with path changes only, from the liber-primus rig in
github.com/Dukotah/cicada3301 (commit 6b945291):

  gematria    the 29-rune Gematria Primus table (rune, index, transliteration, prime)
  ciphers     shift / Atbash / Vigenere / running-key / prime and totient keystreams
  stats       index of coincidence, doublet rate, entropy, chi-square
  score       quadgram English-likeness score
  solve       interrupter-aware decoding and the interrupter beam search
  corpus      parser for the scream314 page-by-page transcription
  skipdecode  the anti-repeat (key-skip) encipher model and the skip-aware beam decoder

`sources` is new: it loads the vendored data files and checks their SHA-256 pins.
"""
