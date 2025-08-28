#!/bin/sh
# Init venv
if command -v source >/dev/null 2>&1; then
  source ./.venv/bin/activate
else
  . ./.venv/bin/activate
fi
# Config updates (setup update dir)
mkdir -p preserve/updates
rm -rf preserve/updates/*
mkdir preserve/updates/acode

cp ./gui/updates.py preserve/updates/acode
cp ./gui/common.py preserve/updates/acode
cp ./gui/loaders.py preserve/updates/acode
cp ./gui/collapsibleSection.py preserve/updates/acode
cp ./gui/_types.py preserve/updates/acode
cp ./gui/release_manifest.py preserve/updates/acode

printf "import acode.updates\nprint('up')\nacode.updates.startApp()" | tee preserve/updates/main.py
selfPath=$(realpath .)
printf "assets_root=\"$selfPath\"" | tee preserve/updates/assets_root.py
# Config updates (start updates)
python3 preserve/updates/main.py
# Config updates (delete updates dir content)
rm -rf preserve/updates/*
# Actualy start
python3 main.py