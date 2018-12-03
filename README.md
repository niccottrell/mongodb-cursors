# mongodb-cursors
Sharded cluster repro to try and break cursors with timeout

Steps:
1. Build a sharded cluster with 16 shards and 16 mongoses
1. Enable sharding
1. Insert test data 
1. Set cursor timeout lower than default 10 minutes
1. Using pymongo connect and load batches of data, trying to get a cursor timeout

## Launch
* `./init.sh`
* `python loop.py`
