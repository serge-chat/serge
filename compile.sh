#!/bin/bash

if ! command -v llama &> /dev/null
then
    cd /usr/src/app/llama.cpp
    make 
    mv main /usr/bin/llama
    cd /usr/src/app
    rm -rf llama.cpp
fi