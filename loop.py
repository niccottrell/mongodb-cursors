import datetime
import pymongo
import time
from pymongo import MongoClient

mongodb_uri = "mongodb://localhost:30000/"
projection = {}
doc_count = 0
batch_size = 50 # The number of documents to load per batch
sleep_time = 3 # The number seconds to sleep _per document_ to simulate some processing
nct = False  # True should avoid Cursor not found
ctm = 150000  # cursorTimeoutMillis (Default is 10 minutes)
use_session = True # If False, the driver will use an implicit session per command (see https://jira.mongodb.org/browse/DOCS-11255)
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
if (use_session):
    session = client.start_session()
else
    session = None
try:
    for doc in collection.find({}, projection, batch_size=batch_size, no_cursor_timeout=nct, session=session):
       doc_count += 1
       if doc_count % 10 == 0:
           print("Count " + str(doc_count) + ": " + str(datetime.datetime.now()))
       time.sleep(sleep_time)
       # Periodically refresh the session to keep it and the cursor alive.
       if (use_session): client.admin.command('refreshSessions', [], session=session)
except pymongo.errors.CursorNotFound as err:
    print(err)
    delta = datetime.datetime.now() - start
    deltaParams = divmod(delta.days * 86400 + delta.seconds, 60)
    print("Took %d minutes, %d seconds to fail" % deltaParams)
