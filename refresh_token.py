#!/usr/bin/env python3
"""
Refresh Schwab access token using refresh token from TradeAssist
"""

import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("SCHWAB_CLIENT_ID")
CLIENT_SECRET = os.getenv("SCHWAB_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("SCHWAB_REFRESH_TOKEN")

print("=" * 70)
print("SCHWAB TOKEN REFRESH")
print("=" * 70)
print()

if not all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN]):
    print("❌ Missing credentials in .env file")
    exit(1)

# Prepare credentials for Basic Auth
credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()

headers = {
    "Authorization": f"Basic {encoded_credentials}",
    "Content-Type": "application/x-www-form-urlencoded"
}

data = {
    "grant_type": "refresh_token",
    "refresh_token": REFRESH_TOKEN
}

print("🔄 Refreshing access token...")
print(f"🔑 Using refresh token: {REFRESH_TOKEN[:30]}...")
print()

try:
    response = requests.post(
        "https://api.schwabapi.com/v1/oauth/token",
        headers=headers,
        data=data
    )

    print(f"📊 Response Status: {response.status_code}")

    if response.status_code == 200:
        tokens = response.json()

        print("✅ Successfully refreshed token!")
        print()
        print("📋 New tokens:")
        print()
        print(f"SCHWAB_ACCESS_TOKEN={tokens['access_token']}")
        print(f"SCHWAB_REFRESH_TOKEN={tokens.get('refresh_token', REFRESH_TOKEN)}")
        print()
        print(f"⏰ Expires in: {tokens.get('expires_in', 0)} seconds")

        # Update .env file
        update = input("\n💾 Update .env file with new tokens? (y/n): ").strip().lower()
        if update == 'y':
            env_path = ".env"
            with open(env_path, 'r') as f:
                lines = f.readlines()

            with open(env_path, 'w') as f:
                for line in lines:
                    if line.startswith('SCHWAB_ACCESS_TOKEN='):
                        f.write(f'SCHWAB_ACCESS_TOKEN={tokens["access_token"]}\n')
                    elif line.startswith('SCHWAB_REFRESH_TOKEN='):
                        new_refresh = tokens.get('refresh_token', REFRESH_TOKEN)
                        f.write(f'SCHWAB_REFRESH_TOKEN={new_refresh}\n')
                    else:
                        f.write(line)

            print("✅ Updated .env file!")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"❌ Exception: {e}")
