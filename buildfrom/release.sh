#!/bin/sh

shdir=$(dirname $0) 

echo "Building for windows" >&2

zip_name_win=$($shdir/build_plat.sh win)
name_win=$(echo $($shdir/mv-cdn.sh $zip_name_win) | sed 's/^.//')

echo "Building for linux" >&2
zip_name_linux=$($shdir/build_plat.sh linux)
name_linux=$(echo $($shdir/mv-cdn.sh $zip_name_linux) | sed 's/^.//')

echo "Building for macos" >&2
zip_name_macos=$($shdir/build_plat.sh macos)
name_macos=$(echo $($shdir/mv-cdn.sh $zip_name_macos) | sed 's/^.//')

echo "Updating downloads" >&2
$shdir/setter.sh index.html "$name_win" dlwin
$shdir/setter.sh index.html "$name_linux" dllinux
$shdir/setter.sh index.html "$name_macos" dlmacos

rm -rf build