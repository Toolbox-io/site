#!/bin/bash

shopt -s expand_aliases

# shellcheck disable=SC2139
alias node="$HOME/Library/Application\ Support/JetBrains/PyCharm2025.1/node/versions/22.16.0/bin/node"
alias terser="node \"$HOME/Library/Application Support/JetBrains/PyCharm2025.1/node/versions/22.16.0/bin/terser\""

files=$(find . -not -path '*/node_modules/*' | grep -E '.*\.(ts)' | xargs)

for file in $files; do
  filewext="${file%.*}"
  echo "$file"
  terser "$filewext".js -o "$filewext".min.js -m
done

