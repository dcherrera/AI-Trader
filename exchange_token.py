#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
from schwab_oauth import exchange_code_for_tokens
import asyncio

# The authorization code from OAuth flow
auth_code = "C0.b2F1dGgyLmJkYy5zY2h3YWIuY29t.q4C-1eOs3b7tl0HFMrCzVIUhBt6LKeXdhktXgDBQhcI@"

print("🔄 Exchanging authorization code for tokens...")
asyncio.run(exchange_code_for_tokens(auth_code))
