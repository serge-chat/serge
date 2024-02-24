#!/bin/bash

set -x
source serge.env

# Get CPU Architecture
cpu_arch=$(uname -m)

# Function to detect CPU features
detect_cpu_features() {
	cpu_info=$(lscpu)
	if echo "$cpu_info" | grep -q "avx512"; then
		echo "AVX512"
	elif echo "$cpu_info" | grep -q "avx2"; then
		echo "AVX2"
	elif echo "$cpu_info" | grep -q "avx"; then
		echo "AVX"
	else
		echo "basic"
	fi
}

# Check if the CPU architecture is aarch64/arm64
if [ "$cpu_arch" = "aarch64" ]; then
	pip_command="python -m pip install -v llama-cpp-python==$LLAMA_PYTHON_VERSION --only-binary=:all: --extra-index-url=https://gaby.github.io/arm64-wheels/"
else
	# Use @smartappli provided wheels
	cpu_feature=$(detect_cpu_features)
	pip_command="python -m pip install -v llama-cpp-python==$LLAMA_PYTHON_VERSION --only-binary=:all: --extra-index-url=https://smartappli.github.io/serge-wheels/$cpu_feature/cpu"
fi

echo "Recommended install command for llama-cpp-python: $pip_command"

# Handle termination signals
_term() {
	echo "Received termination signal!"
	kill -TERM "$redis_process" 2>/dev/null
	kill -TERM "$serge_process" 2>/dev/null
}

# Install python bindings
eval "$pip_command" || {
	echo 'Failed to install llama-cpp-python'
	exit 1
}

# Start Redis instance
redis-server /etc/redis/redis.conf &
redis_process=$!

# Start the API
cd /usr/src/app/api || exit 1
hypercorn_cmd="hypercorn src.serge.main:app --bind 0.0.0.0:8008"
if [ "$SERGE_ENABLE_IPV6" = true ] && [ "$SERGE_ENABLE_IPV4" != true ]; then
	hypercorn_cmd="hypercorn src.serge.main:app --bind [::]:8008"
elif [ "$SERGE_ENABLE_IPV4" = true ] && [ "$SERGE_ENABLE_IPV6" = true ]; then
	hypercorn_cmd="hypercorn src.serge.main:app --bind 0.0.0.0:8008 --bind [::]:8008"
fi

$hypercorn_cmd || {
	echo 'Failed to start main app'
	exit 1
} &

serge_process=$!

# Set up a signal trap and wait for processes to finish
trap _term TERM
wait $redis_process $serge_process
