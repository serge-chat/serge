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
	if [ "$SERGE_GPU_NVIDIA_SUPPORT" = true ]; then
		pip_command="python -m pip install -v llama-cpp-python==$LLAMA_PYTHON_VERSION --only-binary=:all: --extra-index-url=https://smartappli.github.io/llama-cpp-python-cuBLAS-wheels/$cpu_feature/cu122"
	elif [ "$SERGE_GPU_AMD_SUPPORT" = true ]; then
		pip_command="python -m pip install -v llama-cpp-python==$LLAMA_PYTHON_VERSION --only-binary=:all: --extra-index-url=https://smartappli.github.io/llama-cpp-python-cuBLAS-wheels/$cpu_feature/rocm5.6.1"
	else
		pip_command="python -m pip install -v llama-cpp-python==$LLAMA_PYTHON_VERSION --only-binary=:all: --extra-index-url=https://smartappli.github.io/llama-cpp-python-cuBLAS-wheels/$cpu_feature/cpu"
	fi
fi

echo "Recommended install command for llama-cpp-python: $pip_command"

# Install python vendor dependencies
pip install -r /usr/src/app/requirements.txt || {
	echo 'Failed to install python dependencies from requirements.txt'
	exit 1
}

# Install python dependencies
pip install -e ./api || {
	echo 'Failed to install python dependencies'
	exit 1
}

# Install python bindings
eval "$pip_command" || {
	echo 'Failed to install llama-cpp-python'
	exit 1
}

# Start Redis instance
redis-server /etc/redis/redis.conf &

# Start the web server
cd /usr/src/app/web || exit 1
npm run dev -- --host 0.0.0.0 --port 8008 &

# Start the API
cd /usr/src/app/api || exit 1
hypercorn_cmd="hypercorn src.serge.main:app --bind 0.0.0.0:8008"
[ "$SERGE_ENABLE_IPV6" = true ] && hypercorn_cmd+=" --bind [::]:8008"

$hypercorn_cmd || {
	echo 'Failed to start main app'
	exit 1
}
