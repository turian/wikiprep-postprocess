#!/usr/bin/python

DATABASE = "wikipedia-enwiki-20101011"
COLLECTION = "docs"

INSERT_EVERY = 1000

##import cElementTree
import xml.etree.cElementTree as cElementTree
import sys
import string

from common.file import myopen
from common.stats import stats
import common.json
import common.mongodb

from optparse import OptionParser

parser = OptionParser()
parser.add_option("-c", "--collection", dest="collection", help="collection name")
parser.add_option("-d", "--database", dest="database", help="database name")
parser.add_option("-p", "--port", dest="port", help="port number for mongodb", type="int")
parser.add_option("--hostname", dest="hostname", help="hostname for mongodb")
(options, args) = parser.parse_args()

if DATABASE in common.mongodb.connection().database_names():
    print >> sys.stderr, "WARNING: %s database already exists, with %d docs in collection %s" % (DATABASE, common.mongodb.collection(DATABASE=DATABASE, name=COLLECTION).count(), COLLECTION)
collection = common.mongodb.collection(DATABASE=DATABASE, name=COLLECTION)

docs_to_add = []
def add_document(doc):
    global docs_to_add
    docs_to_add.append(doc)
    if len(docs_to_add) > INSERT_EVERY:
        insert_flush()

def insert_flush():
    global docs_to_add
    print >> sys.stderr, "Inserting %d articles to %s (collection contains %d articles)..." % (len(docs_to_add), collection, collection.count())
    print >> sys.stderr, stats()
    collection.insert(docs_to_add)
    print >> sys.stderr, "...done inserting %d articles to %s (collection contains %d articles)" % (len(docs_to_add), collection, collection.count())
    print >> sys.stderr, stats()
    docs_to_add = []

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
            add_document(doc)            
#            collection.save(doc)
#            print common.json.dumps(doc, indent=4)
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
                print >> sys.stderr, "Read %d articles from %s (%d total read, db contains %d articles)" % (cnt, fil, tot, collection.count())
                print >> sys.stderr, stats()
    #    if elem.tag == "record":
    #            ... process record element ...
    #                    elem.clear()
    print >> sys.stderr, "...done reading %s" % fil
    print >> sys.stderr, stats()

insert_flush()
