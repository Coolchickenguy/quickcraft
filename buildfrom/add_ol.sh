#!/bin/sh

# Check if the script has received the proper args
if [ "$#" -ne 3 ]; then
    echo "Adds a element to an ol. Usage: $0 <file> <html> <hid (the ____-pre/post)>"
    exit 1
fi

file="$1"
new_value="$2"
hid="$3"
# Check if the file exists
if [ ! -f "$file" ]; then
    echo "File '$file' not found!"
    exit 1
fi

# Regex-based html parsing works fine, not a bad idea at all :)
# Don't know why I added macos support to this part of the build system
# Handle in-place editing with proper compatibility
if echo "$OSTYPE" | grep -q 'darwin'; then
    # For macOS, use sed with -i argument that requires an empty string for backup
    sed -i "" -e "/<!--$hid-pre-->/, /<!--$hid-post-->/ {
        s#</ol>#$new_value\n</ol>#
    }" "$file"
else
    # For Linux, use sed with -i without any argument for in-place editing
    sed -i -e "/<!--$hid-pre-->/, /<!--$hid-post-->/ {
        s#</ol>#$new_value\n</ol>#
    }" "$file"

fi

# Check if the sed command was successful
if [ $? -eq 0 ]; then
    echo "Updated the file successfully."
else
    echo "Failed to update the file."
fi