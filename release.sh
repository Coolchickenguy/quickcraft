#!/bin/sh

zip -r release.zip quickcraft-installer
name=$(echo $(./mv-cdn.sh release.zip) | sed 's/^.//')
echo "File name is $name" >&2
./setter.sh index.html "$name" dl0
