#!/bin/bash

# Usage: ./goto filename.ext

# Check for argument
if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <filename>"
    exit 1
fi

# Find the first matching file
FILE_PATH=$(find . -name "$1" -print -quit)

# Check if file was found
if [[ -z "$FILE_PATH" ]]; then
    echo "File '$1' not found."
    exit 1
fi

# Get the directory of the file
DIR_PATH=$(dirname "$FILE_PATH")

# Change to that directory
cd $DIR_PATH 
