#!/bin/bash

# (Optional) setup Python env
# virtualenv --python=python3.7.1 venv
source venv/bin/activate
pip install -r requirements.txt

# Install correct version
m 4.0.3

# Launch Sharded cluster
# mlaunch init --single --sharded 16 --mongos 16 --port 30000
# Each shard is a single node but is a RS with an oplog! (for Change Streams etc)
mlaunch init --replicaset --nodes 1 --sharded 16 --mongos 16 --port 30000
# mlaunch start

# Enable sharding
mongo localhost:30000/mydb --eval 'sh.enableSharding("mydb");
db.dummy.createIndex({telephone: 1, name: 1});
sh.shardCollection("mydb.dummy", { telephone : 1 } )'

# Set a very small oplog (1MB) on each mongod
#for i in {0..15}
#do
#  mongo --port $((30016+i)) --eval 'db.adminCommand({replSetResizeOplog: 1, size: 1})'
#done

# Generate data
npm install -g mgeneratejs
mgeneratejs -n 10000 template.json | mongoimport --uri mongodb://localhost:30000/mydb -c dummy

# Generate more data in a subshell to trigger oplog turnover
(
   for (( c=1; c<=500; c++ ))
   do
     mgeneratejs -n 1000 template.json | mongoimport --uri mongodb://localhost:30000/mydb -c dummy
     sleep 60 # sleep for a minute
   done
) &

# Launch loop in python
python loop.py &
# Launch change stream in separate python thread
python cs.py &

# Shut down cluster
# mlaunch kill
