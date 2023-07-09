#!/bin/bash

set -x

# Install python bindings
pip install llama-cpp-python==0.1.69 || {
	echo 'Failed to install llama-cpp-python'
	exit 1
}

# Start Redis instance
redis-server /etc/redis/redis.conf &

# Start the API
cd /usr/src/app/api
uvicorn src.serge.main:app --host 0.0.0.0 --port 8008 || {
	echo 'Failed to start main app'
	exit 1
}
