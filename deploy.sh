#!/bin/bash

mongod &

mv /usr/src/app/node_modules /usr/src/app/web/node_modules -r

# Start the web server
cd web && HOST=0.0.0.0 PORT=8008 node build &
  
# Start the API
cd api && uvicorn main:app --host 0.0.0.0 --port 9124 --root-path /api/ &

# Wait for any process to exit
wait -n
  
# Exit with status of process that exited first
exit $?