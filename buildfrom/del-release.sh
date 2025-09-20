#!/bin/sh

#set -e

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <version> <channel>"
    exit 1
fi
version="$1"
channel="$2"
shdir=$(dirname $0) 

trap 'exit 1' USR1
handleVersions() {
    while read -r release; do 
    checkingVersion=$(printf "$release" | jq -r ".version")
    checkingChannel=$(printf "$release" | jq -r ".channel")
    if [ "$checkingVersion" = "$version" ] && [ "$checkingChannel" = "$channel" ]; then
        del_cdn_plat() {
            cdn_url=$(printf "$release" | jq -r ".$1")
            ls ".$cdn_url" > /dev/null 2>&1
            if [ $? -ne 0 ]; then
                echo "Could not find $1"
                return
            fi
            if [ "$cdn_url" = "" ]; then
                echo "Property does not exsist"
                return
            fi
            rm ".$cdn_url"
        }
        del_cdn_plat win
        del_cdn_plat sig_win
        del_cdn_plat linux
        del_cdn_plat sig_linux
        del_cdn_plat macos
        del_cdn_plat sig_macos
        jq --argjson release "$release" '.releases |= map(select(. != $release))' release_index.json | $shdir/sponge.sh release_index.json
        line=$(cat "download-archive.html" | grep "version=\"$checkingVersion\"" | grep "Channel: $checkingChannel")
        escaped_line=$(printf '%s\n' "$line" | sed 's/[^^]/[&]/g; s/\^/\\^/g')
        if echo "$OSTYPE" | grep -q 'darwin'; then
            sed -i "" "/^$escaped_line$/d" "download-archive.html"
        else
            sed -i "/^$escaped_line$/d" "download-archive.html"
        fi
        
        return
    fi
    done
    echo "No sutch release" >&2
    kill -USR1 "$$"
}
cat "./release_index.json" | jq -c ".releases[]" | handleVersions