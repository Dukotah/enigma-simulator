#!/usr/bin/env python3
'''
Regenerate the data files that BreakingEnigma.ipynb and MasterEnigmaCracker.ipynb load:

  chains.pickle                 the cycle-length catalog: index string -> [(day key, rotor order), ...]
  message_key_encrypts.pickle   doubly enciphered message keys sent under the secret day key
  encrypt1.txt .. encrypt3.txt  messages enciphered under the first message key

The secret day key, rotor order, plugboard and plaintexts come from rejewski.py. Everything is
deterministic: the same command produces byte-identical files.

Usage:
  python make_data.py

The catalog covers all 6 rotor orders x 17,576 day keys (105,456 settings). Each setting is
enciphered once per plaintext letter rather than with random message keys until the permutations
fill up, so the whole build takes well under a minute on one core.
'''
import argparse
import hashlib
import pickle
import random
import time
from itertools import permutations, product

import machine
import rejewski

ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
ROTORS = ['I', 'II', 'III']
# Message key of the first entry in message_key_encrypts.pickle; encrypt1-3.txt are sent under it.
FIRST_MESSAGE_KEY = 'TDS'
MESSAGE_KEY_COUNT = 500
SEED = 1932


def chain_index(enigma, day_key):
    '''
    Cycle-length index of the AD, BE and CF permutations for one day key (no plugboard).

    For every plaintext letter p, the ciphertext of pppppp at the day key gives one pair for each
    permutation (letter 1 -> letter 4, 2 -> 5, 3 -> 6). Running all 26 letters gives the complete
    permutations, so no random sampling is needed.
    '''
    perms = [{}, {}, {}]
    for p in ALPHABET:
        enigma.set_rotor_position(day_key)
        c = enigma.encipher(p * 6)
        for i in range(3):
            perms[i][c[i]] = c[i + 3]
    return rejewski.generate_chain_index(rejewski.make_chains_from_permutation_dict(perms))


def make_catalog(orders):
    enigma = machine.Enigma()
    catalog = {}
    for key in product(ALPHABET, repeat=3):
        for order in orders:
            enigma.set_rotor_order(list(order))
            index = chain_index(enigma, ''.join(key))
            catalog.setdefault(index, []).append((key, order))
    return catalog


def make_message_key_encrypts(count, seed):
    rng = random.Random(seed)
    keys = [FIRST_MESSAGE_KEY] + [''.join(rng.choice(ALPHABET) for _ in range(3)) for _ in range(count - 1)]
    enigma = machine.Enigma(rejewski.SECRET_DAY_KEY, rejewski.SECRET_SWAPS, rejewski.SECRET_ROTOR_ORDER)
    encrypts = []
    for key in keys:
        enigma.set_rotor_position(rejewski.SECRET_DAY_KEY)
        encrypts.append(enigma.encipher(key + key))
    return encrypts


def make_messages():
    enigma = machine.Enigma(FIRST_MESSAGE_KEY, rejewski.SECRET_SWAPS, rejewski.SECRET_ROTOR_ORDER)
    out = []
    for msg in (rejewski.msg1, rejewski.msg2, rejewski.msg3):
        enigma.set_rotor_position(FIRST_MESSAGE_KEY)
        out.append(enigma.encipher(msg))
    return out


def write(path, data):
    with open(path, 'wb') as f:
        f.write(data)
    print('%-30s %9d bytes  sha256 %s' % (path, len(data), hashlib.sha256(data).hexdigest()[:16]))


def main():
    argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter).parse_args()
    orders = list(permutations(ROTORS))
    start = time.time()
    catalog = make_catalog(orders)
    print('catalog: %d day keys x %d rotor orders -> %d distinct indices in %.0f s'
          % (26 ** 3, len(orders), len(catalog), time.time() - start))
    write('chains.pickle', pickle.dumps(catalog, protocol=2))

    encrypts = make_message_key_encrypts(MESSAGE_KEY_COUNT, SEED)
    write('message_key_encrypts.pickle', pickle.dumps(encrypts, protocol=2))
    for i, text in enumerate(make_messages(), 1):
        write('encrypt%d.txt' % i, text.encode('ascii'))


if __name__ == '__main__':
    main()
