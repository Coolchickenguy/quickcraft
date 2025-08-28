#!/bin/sh

set -e

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <name>"
    exit 1
fi
name="$1"
shdir=$(dirname $0) 

keyBase="keys/$name"
mkdir -p "$keyBase"

openssl genpkey -algorithm RSA -out "$keyBase/private.pem" -pkeyopt rsa_keygen_bits:4096
openssl rsa -in "$keyBase/private.pem" -pubout -out "$keyBase/public.pem"
echo "$name" | tee "$keyBase/name"
$shdir/sign.sh "$keyBase/name" "$keyBase/private.pem"
jq --arg public_key "$(cat "$keyBase/public.pem")" --arg name "$name" --arg name_sig "$(cat "$keyBase/name.sig" | base64)" '.publishers[$public_key] = {"name_sig": $name_sig, "name": $name}' release_index.json | $shdir/sponge.sh release_index.json
