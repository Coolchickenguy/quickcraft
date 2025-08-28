#!/bin/bash
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <file> <private_key.pem>"
  exit 1
fi

FILE="$1"
PRIVKEY="$2"
SIG="$1.sig"

if [[ ! -f "$FILE" || ! -f "$PRIVKEY" ]]; then
  echo "File or private key not found"
  exit 1
fi

# Sign the file directly using PKCS#1 v1.5 + SHA256 digestinfo (compatible with Python cryptography)
openssl dgst -sha256 -sign "$PRIVKEY" -out "$SIG" "$FILE"

printf "Signed $FILE -> " >&2
echo "$SIG"