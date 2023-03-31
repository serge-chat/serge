#!/bin/bash
./compile.sh

redis-server

mongod &

mongod --quiet --logpath /dev/null &

python3 /usr/src/app/api/src/serge/worker/orchestrator.py &
# Start the API
cd api && uvicorn src.serge.main:app --host 0.0.0.0 --port 8008 &

# Wait for any process to exit
wait -n
  
# Exit with status of process that exited first
exit $?