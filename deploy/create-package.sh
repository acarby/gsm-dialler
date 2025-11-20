#!/bin/bash
# Create deployment package for GSM Dialler

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PACKAGE_NAME="gsm-dialler-package-$(date +%Y%m%d-%H%M%S)"
PACKAGE_DIR="/tmp/$PACKAGE_NAME"

echo "Creating deployment package..."
echo "Package name: $PACKAGE_NAME"
echo ""

# Create package directory
mkdir -p "$PACKAGE_DIR/gsm-dialler"

# Copy all project files
echo "Copying project files..."
cp -r "$PROJECT_DIR"/* "$PACKAGE_DIR/gsm-dialler/" 2>/dev/null || true

# Exclude unnecessary files
rm -rf "$PACKAGE_DIR/gsm-dialler/.git" 2>/dev/null || true
rm -rf "$PACKAGE_DIR/gsm-dialler/.cursor-server" 2>/dev/null || true
rm -rf "$PACKAGE_DIR/gsm-dialler/__pycache__" 2>/dev/null || true
rm -rf "$PACKAGE_DIR/gsm-dialler/*.pyc" 2>/dev/null || true
rm -rf "$PACKAGE_DIR/gsm-dialler/gsmdialler-data" 2>/dev/null || true

# Create tarball
cd /tmp
echo "Creating tarball..."
tar -czf "$PACKAGE_NAME.tar.gz" "$PACKAGE_NAME"

echo ""
echo "Package created: /tmp/$PACKAGE_NAME.tar.gz"
echo ""
echo "To deploy on another Pi:"
echo "  1. scp /tmp/$PACKAGE_NAME.tar.gz pi@raspberrypi.local:~/"
echo "  2. ssh pi@raspberrypi.local"
echo "  3. tar -xzf $PACKAGE_NAME.tar.gz"
echo "  4. cd $PACKAGE_NAME/gsm-dialler/deploy"
echo "  5. sudo bash install.sh"

