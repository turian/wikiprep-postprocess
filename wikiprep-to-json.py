#!/usr/bin/python
"""
wikiprep-to-json.py

written by Joseph Turian
copyright (C) 2011, MetaOptimize LLC
released under the BSD license

Postprocess XML output from wikiprep (Wikipedia preprocessor) into one
JSON element per line (suitable for mongoimport).
This uses cElementTree.

USAGE:
    ./wikiprep-to-json.py enwiki-20110526-pages-articles.gum.xml.*.gz > enwiki-20110526-pages-articles.json
"""

import sys

from common.file import myopen
import common.json

import xmlwikiprep

assert len(sys.argv) > 1

tot = 0
for fil in sys.argv[1:]:
    f = myopen(fil)
    for doc in xmlwikiprep.read(f):
        print common.json.dumps(doc)
