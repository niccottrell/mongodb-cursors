import time

from pymongo import MongoClient

mongodb_uri = "mongodb://localhost:30000/"
client = MongoClient(mongodb_uri)

db = client.mydb
collection = db.dummy

cursor = collection.watch()
print("Got watch on collection: " + collection.name)
document = next(cursor)
while document is not None:
    print(document)
    time.sleep(1) # sleep for a second
    document = next(cursor)

print("Finished collection watch")
