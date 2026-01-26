#!/bin/bash
set -e

APP_NAME="TG_Client"
ARCH="arm64"

pyinstaller \
  --clean \
  --onefile \
  --name "$APP_NAME" \
  --target-arch "$ARCH" \
  --add-data ".env:." \
  --add-data "materials:materials" \
  main.py

rm -rf build *.spec

echo "📦 Binary built at: dist/$APP_NAME"