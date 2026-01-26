#!/bin/bash
set -e

APP_NAME="TG_Client"
ARCH="arm64"
ICON_SRC="pictures/icon.icns"

rm -rf dist

pyinstaller \
  --clean \
  --onefile \
  --name "$APP_NAME" \
  --target-arch "$ARCH" \
  --add-data ".env:." \
  --add-data "materials:materials" \
  main.py

rm -rf build *.spec

echo "🎁 Wrapping CLI binary into macOS .app bundle..."

# Create .app bundle structure explicitly
mkdir -p "dist/${APP_NAME}.app/Contents/MacOS"
mkdir -p "dist/${APP_NAME}.app/Contents/Resources"

# Copy binary output directly
cp "dist/${APP_NAME}" "dist/${APP_NAME}.app/Contents/Resources/${APP_NAME}"

# Copy icon (renamed to icon.icns)
cp "$ICON_SRC" "dist/${APP_NAME}.app/Contents/Resources/icon.icns"

# launcher
cat > "dist/${APP_NAME}.app/Contents/MacOS/launcher" << EOF
#!/bin/bash
APP_DIR="\$(cd "\$(dirname "\$0")" && pwd)"
BIN="\$APP_DIR/../Resources/$APP_NAME"

osascript -e 'on run argv
    set binPath to item 1 of argv
    tell application "Terminal"
        do script (quoted form of binPath)
        activate
    end tell
end run' "\$BIN"
EOF

# Make launcher executable
chmod +x "dist/${APP_NAME}.app/Contents/MacOS/launcher"

# Info.plist
cat > "dist/${APP_NAME}.app/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleName</key>
  <string>$APP_NAME</string>

  <key>CFBundleExecutable</key>
  <string>launcher</string>

  <key>CFBundleIconFile</key>
  <string>icon</string>

  <key>CFBundleIdentifier</key>
  <string>com.alisherka.tgclient</string>

  <key>CFBundlePackageType</key>
  <string>APPL</string>

  <key>LSUIElement</key>
  <false/>

  <key>CFBundleVersion</key>
  <string>1.0</string>
</dict>
</plist>
EOF

echo "✅ App built successfully!"