import datetime
import pymongo
import time
from pymongo import MongoClient

mongodb_uri = "mongodb://localhost:30000/"
projection = {}
batch_size = 50
sleep_time = 3 # seconds
doc_count = 0
nct = False  # True should avoid Cursor not found
ctm = 300000  # cursorTimeoutMillis (Default is 10 minutes)

client = MongoClient(mongodb_uri, w="majority", socketTimeoutMS=600000,
                         waitQueueTimeoutMS=30000, readPreference='primary')

db = client.mydb
collection = db.dummy

# db.adminCommand( { "getParameter": 1, "cursorTimeoutMillis": 1 } )
paramDict = client.admin.command("getParameter", 1, cursorTimeoutMillis=1)
print("Current cursorTimeoutMillis=%d" % (paramDict[u'cursorTimeoutMillis']))

# db.adminCommand( { "setParameter": 1, "cursorTimeoutMillis": X } )
for x in range(32): # for each mongos and mongod
    port = 30000 + x
    print("Changing cursorTimeoutMillis=%d on port %d" % (ctm, port))
    clientAdmin = MongoClient('localhost', port)
    clientAdmin.admin.command("setParameter", 1, cursorTimeoutMillis=ctm)
    # Check param
    paramDict = client.admin.command("getParameter", 1, cursorTimeoutMillis=1)
    print("Checking port %d, cursorTimeoutMillis=%d" % (port,  paramDict[u'cursorTimeoutMillis']))

print("Batch size: %d" % (batch_size))
print("Sleep per doc: %d seconds"% (sleep_time))
print("Time for each batch: %d minutes" % ((batch_size * sleep_time) / 60))
print("Cursor timeout: %d minutes" % (ctm  / 1000 * 60))

start = datetime.datetime.now()
print("Start time: %s" % (start))
try:
    for doc in collection.find({}, projection, batch_size=batch_size, no_cursor_timeout=nct):
       doc_count += 1
       if doc_count % 10 == 0:
           print("Count " + str(doc_count) + ": " + str(datetime.datetime.now()))
       time.sleep(sleep_time)
except pymongo.errors.CursorNotFound as err:
    print(err)
    delta = datetime.datetime.now() - start
    deltaParams = divmod(delta.days * 86400 + delta.seconds, 60)
    print("Took %d minutes, %d seconds to fail" % deltaParams)
