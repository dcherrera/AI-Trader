#!/bin/bash
# Extract Schwab API credentials from TradeAssist app's UserDefaults

echo "🔍 Searching for Schwab credentials in TradeAssist UserDefaults..."
echo ""

# Get the app's bundle identifier
BUNDLE_ID="com.yourcompany.TradeAssist"

# Try to read from UserDefaults
echo "📋 Checking UserDefaults for Schwab tokens..."
defaults read ~/Library/Preferences/${BUNDLE_ID}.plist 2>/dev/null | grep -i "schwab" || echo "No direct Schwab keys found in plist"

echo ""
echo "🔑 Looking for token-related keys..."
defaults read ~/Library/Preferences/${BUNDLE_ID}.plist 2>/dev/null | grep -i "token\|client\|secret" || echo "Using alternative method..."

echo ""
echo "📝 To manually extract your credentials:"
echo "1. Open your TradeAssist app"
echo "2. Go to Schwab settings/connection"
echo "3. Your app should have:"
echo "   - Client ID (from Schwab Developer Portal)"
echo "   - Client Secret (from Schwab Developer Portal)"
echo "   - Access Token (obtained after OAuth)"
echo "   - Refresh Token (obtained after OAuth)"
echo ""
echo "4. Copy these values and add them to:"
echo "   ${PWD}/.env"
