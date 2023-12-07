#!/bin/bash

dir="$(pwd)"

find "$dir" -name '*.py' | while read -r file; do
    echo "$file":
    echo '```'
    cat "$file"
    echo '```'
    echo ""
done
