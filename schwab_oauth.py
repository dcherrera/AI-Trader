#!/usr/bin/env python3
"""
Schwab OAuth Helper - Get access and refresh tokens
"""

import os
import webbrowser
from urllib.parse import urlencode, parse_qs, urlparse
from dotenv import load_dotenv
import requests
import base64

load_dotenv()

CLIENT_ID = os.getenv("SCHWAB_CLIENT_ID")
CLIENT_SECRET = os.getenv("SCHWAB_CLIENT_SECRET")
CALLBACK_URL = "https://lively-tarsier-11a576.netlify.app/callback.html"

def start_oauth_flow():
    """Open browser for OAuth authorization"""

    # Build authorization URL - manually to control encoding
    # Schwab requires specific formatting with scopes
    auth_url = (
        f"https://api.schwabapi.com/v1/oauth/authorize?"
        f"client_id={CLIENT_ID}&"
        f"redirect_uri={CALLBACK_URL}&"
        f"response_type=code&"
        f"scope=AccountAccess%20Trading"
    )

    print("🌐 Opening Schwab authorization page in your browser...")
    print()
    print("📋 Steps:")
    print("1. Login to your Schwab account")
    print("2. Authorize the TradeAssist app")
    print("3. You'll be redirected to a callback page")
    print("4. Copy the ENTIRE URL from the browser address bar")
    print("5. Paste it back here")
    print()

    webbrowser.open(auth_url)

    return input("📝 Paste the callback URL here: ").strip()

def exchange_code_for_tokens(auth_code):
    """Exchange authorization code for access/refresh tokens"""

    token_url = "https://api.schwabapi.com/v1/oauth/token"

    # Prepare credentials
    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": CALLBACK_URL
    }

    print("🔄 Exchanging authorization code for tokens...")

    try:
        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()

        tokens = response.json()

        print("✅ Successfully obtained tokens!")
        print()
        print("📋 Add these to your .env file:")
        print()
        print(f"SCHWAB_ACCESS_TOKEN={tokens['access_token']}")
        print(f"SCHWAB_REFRESH_TOKEN={tokens['refresh_token']}")
        print()
        print(f"⏰ Token expires in: {tokens.get('expires_in', 0)} seconds")

        # Optionally auto-update .env
        update = input("\n💾 Auto-update .env file? (y/n): ").strip().lower()
        if update == 'y':
            update_env_file(tokens['access_token'], tokens['refresh_token'])

        return tokens

    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting tokens: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def update_env_file(access_token, refresh_token):
    """Update .env file with new tokens"""
    env_path = ".env"

    with open(env_path, 'r') as f:
        lines = f.readlines()

    with open(env_path, 'w') as f:
        for line in lines:
            if line.startswith('SCHWAB_ACCESS_TOKEN='):
                f.write(f'SCHWAB_ACCESS_TOKEN={access_token}\n')
            elif line.startswith('SCHWAB_REFRESH_TOKEN='):
                f.write(f'SCHWAB_REFRESH_TOKEN={refresh_token}\n')
            else:
                f.write(line)

    print("✅ Updated .env file with new tokens!")

def main():
    print("🔑 Schwab OAuth Token Generator")
    print("=" * 50)
    print()

    if not CLIENT_ID or not CLIENT_SECRET:
        print("❌ Error: SCHWAB_CLIENT_ID and SCHWAB_CLIENT_SECRET must be set in .env")
        return

    print(f"📱 Using Client ID: {CLIENT_ID[:20]}...")
    print()

    # Start OAuth flow
    callback_url = start_oauth_flow()

    # Extract code from callback URL
    parsed = urlparse(callback_url)
    params = parse_qs(parsed.query)

    if 'code' in params:
        auth_code = params['code'][0]
        print(f"✅ Got authorization code: {auth_code[:20]}...")

        # Exchange for tokens
        exchange_code_for_tokens(auth_code)
    else:
        print("❌ No authorization code found in URL")
        print("Make sure you copied the complete callback URL")

if __name__ == "__main__":
    main()
