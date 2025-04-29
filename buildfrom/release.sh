#!/bin/sh

# Check if the script has received the proper args
if [ "$#" -ne 4 ]; then
    echo "Usage: $0 <version> <rootUrl> <name (of builder)> <channel>"
    exit 1
fi

version="$1"
shdir=$(dirname $0) 
rootUrl=$2
name=$3
channel=$4
# Handle siginal from handleVersions
trap 'exit 1' USR1
handleVersions() {
    while read -r release; do 
    checkingVersion=$(printf "$release" | jq -r ".version")
    checkingChannel=$(printf "$release" | jq -r ".channel")
    if [ "$checkingVersion" = "$version" ] && [ "$checkingChannel" = "$channel" ]; then
        echo "Release already exists" >&2
        kill -USR1 "$$"
    fi
    done
}
cat "./release_index.json" | jq -c ".releases[]" | handleVersions


gen_manifest() {
    jq -n --arg rootUrl $rootUrl --arg name $name --arg platform $1 --arg version $version --arg channel $channel '{"vendor":{"rootUrl": $rootUrl, "name": $name}, "platform": $platform, "version":$version, "channel": $channel}'
    return $?
}
echo "Building for windows" >&2
win_manifest=$(gen_manifest "win")
zip_name_win=$($shdir/build_plat.sh win "$win_manifest")
name_win=$(echo $($shdir/mv-cdn.sh $zip_name_win) | sed 's/^.//')

echo "Building for linux" >&2

linux_manifest=$(gen_manifest "linux")
zip_name_linux=$($shdir/build_plat.sh linux "$linux_manifest")
name_linux=$(echo $($shdir/mv-cdn.sh $zip_name_linux) | sed 's/^.//')

echo "Building for macos" >&2

macos_manifest=$(gen_manifest "macos")
zip_name_macos=$($shdir/build_plat.sh macos "$macos_manifest")
name_macos=$(echo $($shdir/mv-cdn.sh $zip_name_macos) | sed 's/^.//')

echo "Updating downloads" >&2
$shdir/setter.sh index.html "$name_win" dlwin
$shdir/setter.sh index.html "$name_linux" dllinux
$shdir/setter.sh index.html "$name_macos" dlmacos
$shdir/add_ol.sh download-archive.html "<li version=\"$version\"><p>Channel: $channel</p><ul><li><a href=\"$name_win\">DOWNLOAD WINDOWS</a></li><li><a href=\"$name_linux\">DOWNLOAD LINUX</a></li><li><a href=\"$name_macos\">DOWNLOAD MACOS</a></li></ul></li>" "archive"
echo "Updating assets index" >&2
# Buffer via sponge.sh so the file is not overwritten before it is read
jq --arg version $version --arg name_win $name_win --arg name_linux $name_linux --arg name_macos $name_macos --arg channel $channel '.releases += [{"version":$version,"win":$name_win,"linux":$name_linux,"macos":$name_macos,"channel":$channel}]' release_index.json | $shdir/sponge.sh release_index.json
rm -rf build