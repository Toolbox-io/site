#!/bin/bash

# Usage: ./scss-watcher.sh path/to/file.scss

input_file="$1"
output_file="${input_file%.scss}.css"

npx sass \
    "$input_file:$output_file" \
    --no-source-map \
    -s compressed && \
    postcss "$output_file" --use autoprefixer --no-map -o "$output_file"