#!/bin/sh

echo "Moving $1 to cdn" >&2

sum=$(cat $1 | md5sum | cut -d' ' -f1)
ext=""
case "$1" in
    *.tar.*[^.]*)
        ext=${1#*.}
        ;;
    *)
        ext=${1##*.}
        ;;
esac
path="./cdn/$sum.$ext"
mv $1 $path
echo $path