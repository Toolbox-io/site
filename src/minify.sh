#!/bin/bash

echo "$PATH"

files=$(find . -not -path '*/node_modules/*' | grep -E '.*\.(ts)' | xargs)

for file in $files; do
  filewext="${file%.*}"
  echo "$file"
  terser "$filewext".js -o "$filewext".js -m
done