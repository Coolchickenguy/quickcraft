#!/bin/sh

# Read all stdin into a variable
buffer=""
while IFS= read -r line; do
  buffer="${buffer}${line}
"
done

# Write buffer to the target file
printf "%s" "$buffer" > "$1"
