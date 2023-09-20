#!/bin/bash

set -x

# Handle termination signals
_term() {
	echo "Received termination signal!"
	kill -TERM "$redis_process" 2>/dev/null
	kill -TERM "$serge_process" 2>/dev/null
}

# Install python bindings
export UNAME_M=$(dpkg --print-architecture)
pip install llama-cpp-python==0.1.78 || {
	echo 'Failed to install llama-cpp-python'
	exit 1
}

# Start Redis instance
redis-server /etc/redis/redis.conf &
redis_process=$!

# Start the API
cd /usr/src/app/api || exit 1
uvicorn src.serge.main:app --host 0.0.0.0 --port 8008 || {
	echo 'Failed to start main app'
	exit 1
} &
serge_process=$!

# Set up a signal trap and wait for processes to finish
trap _term TERM
wait $redis_process $serge_process
