#!/bin/bash

if [[ -z $1 ]]; then
    echo "Usage: $0 <venv_dir>"
    exit 1
fi

venv_dir=$1

case $2 in
    "install")
        echo "Installing dependencies..."
        requirements=$(find . -name "requirements.txt" -type f)
        if [[ -z $requirements ]]; then
            echo "No dependencies to install."
            exit 0
        fi

        for req in $requirements; do
            "$venv_dir/bin/pip3" install -r "$req"
        done
        ;;
    "create")
        echo "Creating virtual environment..."
        python -m venv $venv_dir
        ;;
    *)
        echo "Usage: $0 <venv_dir> <install|create>"
        exit 1
        ;;
esac