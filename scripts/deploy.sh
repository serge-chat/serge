#!/bin/bash

set -x

# Install python bindings
pip install llama-cpp-python==0.1.78 || {
	echo 'Failed to install llama-cpp-python'
	exit 1
}

# Start Dragonfly instance
mkdir -p /data/db
/usr/local/bin/dragonfly --noversion_check --logtostderr --dbnum 0 --bind localhost --port 6379 --save_schedule "*:*" --dbfilename dragonfly --dir /data/db &

# Start the API
cd /usr/src/app/api || exit 1
uvicorn src.serge.main:app --host 0.0.0.0 --port 8008 || {
	echo 'Failed to start main app'
	exit 1
}
