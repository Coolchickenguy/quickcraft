#!/bin/sh

set -e
path="$(realpath "$1")"

echo "Moving $path to cdn" >&2

sum=$(cat $path | md5sum | cut -d' ' -f1)
ext=""
case "${1##*/}" in
    *.tar.*)
        ext="${path#*.}"
        ;;
    *)
        ext="${path##*.}"
        ;;
esac
new_path="./cdn/$sum.$ext"
mv "$path" "$new_path"
echo "$new_path"