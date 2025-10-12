#!/bin/bash

# Build script for Swift ScreenBlocker app

echo "Building Swift ScreenBlocker app..."

# Check if Xcode is installed
if ! command -v xcodebuild &> /dev/null; then
    echo "Error: Xcode command line tools not found."
    echo "Install with: xcode-select --install"
    exit 1
fi

# Navigate to the Swift app directory
cd "$(dirname "$0")/macos_app"

# Build the app
echo "Building ScreenBlocker.xcodeproj..."
xcodebuild -project ScreenBlocker.xcodeproj \
           -scheme ScreenBlocker \
           -configuration Release \
           -derivedDataPath ./build \
           build

if [ $? -eq 0 ]; then
    echo "Build successful!"
    echo "App location: ./build/Build/Products/Release/ScreenBlocker.app"
    
    # Copy to a more accessible location
    cp -r "./build/Build/Products/Release/ScreenBlocker.app" "../ScreenBlocker.app"
    echo "App copied to: ./ScreenBlocker.app"
    echo ""
    echo "To run the app:"
    echo "  open ScreenBlocker.app"
    echo ""
    echo "Note: You'll need to grant Screen Recording permission in System Settings"
else
    echo "Build failed!"
    exit 1
fi
