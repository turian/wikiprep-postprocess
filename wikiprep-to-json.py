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

##import cElementTree
import xml.etree.cElementTree as cElementTree
import sys
import string

from common.file import myopen
from common.stats import stats
import common.json

assert len(sys.argv) > 1

tot = 0
for fil in sys.argv[1:]:
    print >> sys.stderr, "Reading %s..." % fil
    print >> sys.stderr, stats()
    f = myopen(fil)
    doc = {}
    cnt = 0
    for event, elem in cElementTree.iterparse(f):
        if elem.tag == "title":
            doc["title"] = ("".join(elem.itertext()))
        elif elem.tag == "text":
            doc["text"] = ("".join(elem.itertext()))
        elif elem.tag == "link":
            # Skip internal links
            if elem.get("url") is None: continue

            if "external links" not in doc: doc["external links"] = []
            doc["external links"].append([elem.get("url"), ("".join(elem.itertext()))])
        elif elem.tag == "links":
            doc["links"] = [int(i) for i in string.split("".join(elem.itertext()))]
        elif elem.tag == "categories":
            doc["categories"] = [int(i) for i in string.split("".join(elem.itertext()))]
        elif elem.tag == "page":
            doc["_id"] = int(elem.get("id"))
            print common.json.dumps(doc)
            cnt += 1
            tot += 1
            title = None
            text = None
            id = None
            links = []
            categories = []
            external_links = []

            # Free the memory of the building tree
            elem.clear()
            if cnt % 1000 == 0:
                print >> sys.stderr, "Read %d articles from %s (%d total read)" % (cnt, fil, tot)
                print >> sys.stderr, stats()
    #    if elem.tag == "record":
    #            ... process record element ...
    #                    elem.clear()
    print >> sys.stderr, "...done reading %s" % fil
    print >> sys.stderr, stats()
