#!/bin/bash

set -x

# Install python dependencies
pip install -e ./api || {
	echo 'Failed to install python dependencies'
	exit 1
}

# Install python bindings
pip install llama-cpp-python==0.1.77 || {
	echo 'Failed to install llama-cpp-python'
	exit 1
}

# Start Dragonfly instance
mkdir -p /data/db
/usr/local/bin/dragonfly --noversion_check --logtostderr --dbnum 0 --bind localhost --port 6379 --save_schedule "*:*" --dbfilename dragonfly --dir /data/db &

# Start the web server
cd /usr/src/app/web || exit 1
npm run dev -- --host 0.0.0.0 --port 8008 &

# Start the API
cd /usr/src/app/api || exit 1
uvicorn src.serge.main:api_app --reload --host 0.0.0.0 --port 9124 --root-path /api/ || {
	echo 'Failed to start main app'
	exit 1
}
