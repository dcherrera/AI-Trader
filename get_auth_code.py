#!/usr/bin/env python3
"""
Get Schwab authorization code - Following official API documentation
"""

import os
import webbrowser
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("SCHWAB_CLIENT_ID")
CALLBACK_URL = "https://lively-tarsier-11a576.netlify.app/callback.html"

print("=" * 70)
print("SCHWAB OAUTH - Step 1: Get Authorization Code")
print("=" * 70)
print()
print("Following official Schwab Trader API documentation (Page 3)")
print()

# Exactly as documented - only client_id and redirect_uri
auth_url = f"https://api.schwabapi.com/v1/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={CALLBACK_URL}"

print("Opening authorization URL in browser...")
print()
print(f"URL: {auth_url}")
print()
print("📋 INSTRUCTIONS:")
print("1. Login to your Schwab account")
print("2. Authorize the application")
print("3. You'll be redirected to callback page")
print("4. Copy the 'code' parameter from the URL")
print()

webbrowser.open(auth_url)

print("✅ Browser opened!")
print()
print("After authorization, the URL will look like:")
print("https://lively-tarsier-11a576.netlify.app/callback.html?code=XXXXX&session=YYYYY")
print()
print("Copy just the code part (after code= and before &)")
