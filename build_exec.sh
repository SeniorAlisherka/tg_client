#!/bin/bash
set -e

APP_NAME="TG_Client"
ARCH="arm64"

rm -rf dist

pyinstaller \
  --clean \
  --onefile \
  --name "$APP_NAME" \
  --target-arch "$ARCH" \
  --add-data ".env:." \
  --add-data "materials:materials" \
  --add-binary "lib/libtdjson.dylib:lib" \
  --add-binary "lib/libtdjson.1.8.58.dylib:lib" \
  main.py

rm -rf build *.spec

echo "📦 Binary built at: dist/$APP_NAME"