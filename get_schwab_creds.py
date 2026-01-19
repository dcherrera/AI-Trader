#!/usr/bin/env python3
"""
Extract Schwab credentials from TradeAssist app's UserDefaults
"""

import subprocess
import json
import base64

def get_user_defaults(domain="com.davidherrera.TradeAssist"):
    """Read UserDefaults for TradeAssist app"""
    try:
        # Try to export all defaults
        result = subprocess.run(
            ["defaults", "export", domain, "-"],
            capture_output=True,
            text=False
        )

        if result.returncode == 0:
            # Parse plist data
            plist_data = result.stdout
            # Convert to JSON for easier parsing
            json_result = subprocess.run(
                ["plutil", "-convert", "json", "-o", "-", "-"],
                input=plist_data,
                capture_output=True,
                text=True
            )

            if json_result.returncode == 0:
                return json.loads(json_result.stdout)

        return None
    except Exception as e:
        print(f"Error reading UserDefaults: {e}")
        return None

def extract_schwab_accounts(defaults_data):
    """Extract Schwab accounts from UserDefaults"""
    if not defaults_data:
        return None

    # Look for stored_schwab_accounts key
    accounts_data = defaults_data.get("stored_schwab_accounts")
    if accounts_data:
        try:
            # Decode base64 if needed
            if isinstance(accounts_data, str):
                accounts_json = json.loads(accounts_data)
            else:
                accounts_json = accounts_data

            return accounts_json
        except Exception as e:
            print(f"Error parsing accounts data: {e}")

    return None

def extract_tokens(defaults_data):
    """Extract Schwab tokens from UserDefaults"""
    if not defaults_data:
        return None

    return {
        "access_token": defaults_data.get("schwab_access_token"),
        "refresh_token": defaults_data.get("schwab_refresh_token"),
        "environment": defaults_data.get("schwab_environment")
    }

def main():
    print("🔍 Searching for Schwab credentials in TradeAssist...")
    print()

    # Try different possible bundle identifiers
    possible_domains = [
        "com.davidherrera.TradeAssist",
        "com.yourcompany.TradeAssist",
        "TradeAssist"
    ]

    found = False
    for domain in possible_domains:
        print(f"Trying domain: {domain}")
        defaults = get_user_defaults(domain)

        if defaults:
            print("✅ Found UserDefaults data!")

            # Extract accounts
            accounts = extract_schwab_accounts(defaults)
            if accounts:
                print("\n📋 Stored Schwab Accounts:")
                for i, account in enumerate(accounts, 1):
                    print(f"\nAccount {i}:")
                    print(f"  Name: {account.get('name', 'N/A')}")
                    print(f"  Client ID: {account.get('clientId', 'N/A')[:20]}...")
                    print(f"  Has Client Secret: {bool(account.get('clientSecret'))}")
                    print(f"  Has Access Token: {bool(account.get('accessToken'))}")
                    print(f"  Has Refresh Token: {bool(account.get('refreshToken'))}")
                    print(f"  Environment: {account.get('environment', 'N/A')}")

                # Show instructions for copying
                print("\n📝 To use these credentials:")
                print("1. Run this script with --export flag to save to .env")
                print("   OR")
                print("2. Manually copy the values to your .env file")

                found = True
                break

            # Try extracting tokens directly
            tokens = extract_tokens(defaults)
            if any(tokens.values()):
                print("\n🔑 Found Tokens:")
                if tokens['access_token']:
                    print(f"  Access Token: {tokens['access_token'][:30]}...")
                if tokens['refresh_token']:
                    print(f"  Refresh Token: {tokens['refresh_token'][:30]}...")
                if tokens['environment']:
                    print(f"  Environment: {tokens['environment']}")

                found = True
                break

    if not found:
        print("\n❌ No Schwab credentials found in UserDefaults")
        print("\n💡 Alternative method:")
        print("1. Open your TradeAssist app")
        print("2. Go to Settings > Schwab Account")
        print("3. Your credentials should be visible or can be re-entered")
        print("4. Manually copy them to the .env file")

if __name__ == "__main__":
    main()
