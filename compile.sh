#!/bin/bash

if ! command -v llama &> /dev/null
then
    cd /usr/src/app
    git clone https://github.com/ggerganov/llama.cpp.git --branch master-d5850c5
    cd llama.cpp
    make 
    mv main /usr/bin/llama
fi