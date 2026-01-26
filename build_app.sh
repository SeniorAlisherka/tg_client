#!/bin/bash
set -e

APP_NAME="TG_Client"
ARCH="arm64"
ICON_SRC="pictures/icon.icns"
DMG_NAME="${APP_NAME}.dmg"

echo "🚀 Building macOS app..."

# Clean dist
rm -rf dist

# === Build CLI binary ===
pyinstaller \
  --clean \
  --onefile \
  --name "$APP_NAME" \
  --target-arch "$ARCH" \
  --add-data ".env:." \
  --add-data "materials:materials" \
  main.py

# Clean build artifacts
rm -rf build *.spec

echo "📦 Wrapping into .app bundle..."

# === Create .app structure ===
mkdir -p "dist/${APP_NAME}.app/Contents/MacOS"
mkdir -p "dist/${APP_NAME}.app/Contents/Resources"

# Copy binary
cp "dist/${APP_NAME}" "dist/${APP_NAME}.app/Contents/Resources/${APP_NAME}"

# Copy icon
cp "$ICON_SRC" "dist/${APP_NAME}.app/Contents/Resources/icon.icns"

# Create launcher script (spawns Terminal)
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

chmod +x "dist/${APP_NAME}.app/Contents/MacOS/launcher"

# Minimal plist
cat > "dist/${APP_NAME}.app/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleExecutable</key>
  <string>launcher</string>
  <key>CFBundleIconFile</key>
  <string>icon</string>
</dict>
</plist>
EOF

echo "📀 Creating DMG..."

# Create DMG with app-drop UX
create-dmg \
  --volname "$APP_NAME" \
  --window-size 600 400 \
  --icon-size 120 \
  --icon "${APP_NAME}.app" 150 200 \
  --app-drop-link 450 200 \
  "dist/$DMG_NAME" \
  "dist/${APP_NAME}.app"

echo "🎉 DMG ready: dist/$DMG_NAME"