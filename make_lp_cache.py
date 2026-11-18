#!/usr/bin/env python3
'''
Regenerate lp/cache/catalog.json, the hypothesis-catalog sweep that BreakingLiberPrimus.ipynb
and LiberPrimusSolutions.ipynb load. The notebooks recompute it themselves (about a minute)
when the cache is missing or was built with different parameters.

Usage:
  python make_lp_cache.py
'''
import json
import os
import time

from lp import catalog


def main():
    start = time.time()
    res = catalog.run()
    os.makedirs(os.path.dirname(catalog.CACHE), exist_ok=True)
    with open(catalog.CACHE, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(res, f, indent=1)
        f.write('\n')
    print('%d candidates; %d real and %d null decodes in %.0f s -> %s'
          % (res['library_size'], res['real']['n'], res['null']['n'], time.time() - start, catalog.CACHE))


if __name__ == '__main__':
    main()
