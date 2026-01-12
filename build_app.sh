#!/bin/bash
set -e

APP_NAME="TG Client"
ARCH="arm64"

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

# echo "🎁 Wrapping CLI binary into macOS .app bundle..."

# APP_BUNDLE="dist/$APP_NAME.app"
# BIN_PATH="dist/$APP_NAME"
# APP_BIN_PATH="$APP_BUNDLE/Contents/Resources/$APP_NAME"

# mkdir -p "$APP_BUNDLE/Contents/MacOS"
# mkdir -p "$APP_BUNDLE/Contents/Resources"

# cp "$BIN_PATH" "$APP_BIN_PATH"

# cat > "$APP_BUNDLE/Contents/MacOS/launcher" << EOF
# #!/bin/bash
# APP_DIR="\$(cd "\$(dirname "\$0")" && pwd)"
# BIN="\$APP_DIR/../Resources/$APP_NAME"

# osascript -e 'on run argv
#     set binPath to item 1 of argv
#     tell application "Terminal"
#         do script (quoted form of binPath)
#         activate
#     end tell
# end run' "\$BIN"
# EOF

# chmod +x "$APP_BUNDLE/Contents/MacOS/launcher"

# cat > "$APP_BUNDLE/Contents/Info.plist" << EOF
# <?xml version="1.0" encoding="UTF-8"?>
# <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
#  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
# <plist version="1.0">
# <dict>
#   <key>CFBundleName</key>
#   <string>$APP_NAME</string>

#   <key>CFBundleExecutable</key>
#   <string>launcher</string>

#   <key>CFBundleIdentifier</key>
#   <string>com.alisherka.tgclient</string>

#   <key>CFBundlePackageType</key>
#   <string>APPL</string>

#   <key>LSUIElement</key>
#   <false/>

#   <key>CFBundleVersion</key>
#   <string>1.0</string>
# </dict>
# </plist>
# EOF

echo "✅ App built successfully!"
