#!/bin/sh

# Check if the script has received three arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <win/linux/macos> <manifest>"
    exit 1
fi

try_cp() {
    files=$1
    to=$2
    eval "set -- $files"
    if [ -e "$1" ]; then
        for arg in "$@"
        do
            #echo "$arg $to" >&2
            cp -r "$arg" "$to"
        done
    else
        echo "Cp skipped" >&2
    fi
}
platform=$1
shdir=$(dirname $0)
builddir="build/build-$platform"
rm -rf "$builddir"
mkdir -p "$builddir"
mkdir "$builddir/assets"
try_cp "$shdir/sources/assets-all/*" "$builddir/assets"

printf "$2 "> "$builddir/assets/release_manifest.json"
if [ "$1" = "win" ]; then
    try_cp "$shdir/sources/assets-win/*" "$builddir/assets"
    try_cp "$shdir/sources/main-win/*" "$builddir"
    buildzip=$(realpath "build/build-$platform.zip")
    oldPath=$(realpath .)
    cd "$builddir"
    zip -q -r "$buildzip" .
    cd "$oldPath"
    echo "$buildzip"
fi

build_unix() {
    try_cp "$shdir/sources/assets-unix/*" "$builddir/assets"
    try_cp "$shdir/sources/main-unix/*" "$builddir"
    buildtargz=$(realpath "build/build-$platform.tar.gz")
    oldPath=$(realpath .)
    cd "$builddir"
    tar -czf "$buildtargz" *
    cd "$oldPath"
    echo "$buildtargz"
}

if [ "$1" = "linux" ]; then
    try_cp "$shdir/sources/assets-linux/*" "$builddir/assets"
    try_cp "$shdir/sources/main-linux/*" "$builddir"
    build_unix
fi

if [ "$1" = "macos" ]; then
    try_cp "$shdir/sources/assets-macos/*" "$builddir/assets"
    try_cp "$shdir/sources/main-macos/*" "$builddir"
    build_unix
fi
