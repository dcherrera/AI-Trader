#!/usr/bin/env python3
"""
Simple script to get Schwab OAuth token
"""

import os
import webbrowser
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("SCHWAB_CLIENT_ID")
CALLBACK_URL = "https://lively-tarsier-11a576.netlify.app/callback.html"

# Build authorization URL - MUST include scopes for Schwab
auth_url = (
    f"https://api.schwabapi.com/v1/oauth/authorize?"
    f"client_id={CLIENT_ID}&"
    f"redirect_uri={CALLBACK_URL}&"
    f"response_type=code&"
    f"scope=AccountAccess%20Trading"
)

print("=" * 70)
print("SCHWAB OAUTH - GET NEW TOKEN")
print("=" * 70)
print()
print("📋 INSTRUCTIONS:")
print()
print("1. I will open the Schwab authorization page in your browser")
print("2. Login to your Schwab account and authorize the app")
print("3. You'll be redirected to a callback page that shows the code")
print("4. Copy the authorization code (the part after ?code=)")
print("5. Come back here and provide the code")
print()
print("🌐 Opening browser in 3 seconds...")
print()
print(f"🔗 URL: {auth_url}")
print()

import time
time.sleep(3)
webbrowser.open(auth_url)

print()
print("✅ Browser opened!")
print()
print("After you authorize, paste the authorization code here")
print("(Look for ?code=XXXXXXXXXX in the callback URL)")
print()
