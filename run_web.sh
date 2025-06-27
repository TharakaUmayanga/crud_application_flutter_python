#!/bin/bash

# Flutter Web CRUD Application Build & Run Script

echo "🌐 Flutter Web CRUD Application"
echo "==============================="
echo ""

# Check if Flutter is installed
if ! command -v flutter &> /dev/null; then
    echo "❌ Flutter is not installed or not in PATH"
    echo "Please install Flutter and try again"
    exit 1
fi

echo "✅ Flutter found: $(flutter --version | head -n 1)"
echo ""

# Navigate to project directory
cd "$(dirname "$0")"

echo "🔧 Enabling Flutter web support..."
flutter config --enable-web

echo ""
echo "📦 Installing dependencies..."
flutter pub get

echo ""
echo "🔍 Running static analysis..."
flutter analyze --fatal-infos

echo ""
echo "🌐 Building for web..."
flutter build web --release

echo ""
echo "🚀 Starting web server..."
echo "🔗 Application will be available at: http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the web server
flutter run -d web-server --web-port 8080

echo ""
echo "📋 Web Features Available:"
echo "   ✅ Responsive design for desktop and mobile"
echo "   ✅ Create new users with validation"
echo "   ✅ View user list with pagination"
echo "   ✅ Edit existing users"
echo "   ✅ Delete users with confirmation"
echo "   ✅ View detailed user information"
echo "   ✅ Upload profile pictures (web-compatible)"
echo "   ✅ Form validation with error messages"
echo "   ✅ Progressive Web App (PWA) support"
echo ""
echo "🔧 Backend Integration:"
echo "   - Update lib/config/app_config.dart"
echo "   - Set useMockData = false"
echo "   - Update apiBaseUrl to your backend URL"
echo ""
