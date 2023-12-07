#!/bin/bash

print_tree() {
    local dir=$1
    local indent=$2

    # Print the name of the directory
    echo "$indent$(basename "$dir")"
    indent+="    "

    # Loop through the contents of the directory
    for file in "$dir"/*; do
        # Check if the file exists (to handle empty directories)
        if [ -e "$file" ]; then
            # If it's a directory, recursively call print_tree
            if [ -d "$file" ]; then
                print_tree "$file" "$indent"
            else
                # If it's a file, just print its name
                echo "${indent}$(basename "$file")"
            fi
        fi
    done
}

# Start the tree from the current directory
print_tree "$(pwd)" ""
