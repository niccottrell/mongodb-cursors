# mongodb-cursors
Sharded cluster repro to try and break cursors with timeout

Steps:
1. Build a sharded cluster with 16 shards and 16 mongoses
1. Enable sharding
1. Insert test data 
1. Set cursor timeout lower than default 10 minutes
1. Using pymongo connect and load batches of data, trying to get a cursor timeout

## Preparation

- You may need to install Python 3.7 for your environment
- You may need to setup the environment with `python -m venv` and comment out the `virtualenv` line

## Experimentation

Feel free to change the following lines to test combinations of settings:
```python
batch_size = 50 # The number of documents to load per batch
sleep_time = 3 # The number seconds to sleep _per document_ to simulate some processing
nct = False  # True should avoid Cursor not found
ctm = 150000  # cursorTimeoutMillis (Default is 10 minutes)
```

If `batch_size * sleep_time` exceeds the cursor timeout, the client should normally receive a [CursorNotFound](http://api.mongodb.com/python/current/api/pymongo/errors.html?highlight=cursornotfound#pymongo.errors.CursorNotFound) exception.

## Launch

1. `./init.sh` - This will init the environment, launch the MongoDB cluster and start the test. 
1. `python loop.py` - If you already have the environment up, you can just test the cursor timeout with this command 
