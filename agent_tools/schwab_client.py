"""
Schwab API Client for AI-Trader
Provides real-time market data from Schwab API
"""

import os
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()


class SchwabAPIClient:
    """Client for Schwab Trading API"""

    def __init__(self):
        self.base_url = "https://api.schwabapi.com"
        self.client_id = os.getenv("SCHWAB_CLIENT_ID")
        self.client_secret = os.getenv("SCHWAB_CLIENT_SECRET")
        self.access_token = os.getenv("SCHWAB_ACCESS_TOKEN")
        self.refresh_token = os.getenv("SCHWAB_REFRESH_TOKEN")

        if not self.client_id or not self.client_secret:
            raise ValueError("Schwab API credentials not found in environment variables")

    def _get_headers(self, include_content_type: bool = False) -> Dict[str, str]:
        """Get headers for API requests"""
        if not self.access_token:
            raise ValueError("No access token available. Please authenticate first.")

        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

        # Only include Content-Type for POST/PUT requests with body data
        if include_content_type:
            headers["Content-Type"] = "application/json"

        return headers

    def refresh_access_token(self) -> bool:
        """Refresh the access token using refresh token"""
        if not self.refresh_token:
            print("❌ No refresh token available")
            return False

        token_url = f"{self.base_url}/v1/oauth/token"

        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        try:
            response = requests.post(token_url, data=data, headers=headers)
            response.raise_for_status()

            token_data = response.json()
            self.access_token = token_data.get("access_token")

            # Update refresh token if provided
            if "refresh_token" in token_data:
                self.refresh_token = token_data["refresh_token"]

            print("✅ Access token refreshed successfully")
            return True

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to refresh token: {e}")
            return False

    def get_quote(self, symbol: str) -> Optional[Dict]:
        """Get real-time quote for a symbol"""
        # Schwab uses query parameters for symbols
        symbol_upper = symbol.upper()
        url = f"{self.base_url}/marketdata/v1/quotes?symbols={symbol_upper}"

        try:
            response = requests.get(url, headers=self._get_headers())

            # Try to refresh token if unauthorized
            if response.status_code == 401:
                print("🔄 Token expired, refreshing...")
                if self.refresh_access_token():
                    response = requests.get(url, headers=self._get_headers(), params=params)
                else:
                    return None

            response.raise_for_status()
            data = response.json()

            # Extract quote for the symbol
            if symbol in data:
                return data[symbol]

            return None

        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching quote for {symbol}: {e}")
            return None

    def get_quotes_bulk(self, symbols: List[str]) -> Dict[str, Dict]:
        """Get quotes for multiple symbols at once"""
        # Schwab API allows up to 500 symbols per request
        symbols_str = ",".join([s.upper() for s in symbols])
        url = f"{self.base_url}/marketdata/v1/quotes?symbols={symbols_str}"

        try:
            response = requests.get(url, headers=self._get_headers())

            if response.status_code == 401:
                if self.refresh_access_token():
                    response = requests.get(url, headers=self._get_headers())
                else:
                    return {}

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching bulk quotes: {e}")
            return {}

    def get_price_history(self, symbol: str, period_type: str = "day",
                         period: int = 1, frequency_type: str = "minute",
                         frequency: int = 1) -> Optional[Dict]:
        """
        Get price history/candles for a symbol

        Args:
            symbol: Stock symbol
            period_type: 'day', 'month', 'year', 'ytd'
            period: Number of periods
            frequency_type: 'minute', 'daily', 'weekly', 'monthly'
            frequency: Frequency interval
        """
        url = f"{self.base_url}/marketdata/v1/pricehistory"

        params = {
            "symbol": symbol,
            "periodType": period_type,
            "period": period,
            "frequencyType": frequency_type,
            "frequency": frequency
        }

        try:
            response = requests.get(url, headers=self._get_headers(), params=params)

            if response.status_code == 401:
                if self.refresh_access_token():
                    response = requests.get(url, headers=self._get_headers(), params=params)
                else:
                    return None

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching price history for {symbol}: {e}")
            return None

    def format_quote_for_trading(self, quote_data: Dict) -> Dict[str, float]:
        """
        Format Schwab quote data to match AI-Trader expected format

        Returns dict with buy_price, sell_price, high, low, volume
        """
        if not quote_data or "quote" not in quote_data:
            return {}

        quote = quote_data["quote"]

        return {
            "buy_price": quote.get("askPrice", quote.get("lastPrice", 0)),
            "sell_price": quote.get("bidPrice", quote.get("lastPrice", 0)),
            "last_price": quote.get("lastPrice", 0),
            "high": quote.get("highPrice", 0),
            "low": quote.get("lowPrice", 0),
            "volume": quote.get("totalVolume", 0),
            "timestamp": quote.get("quoteTime", 0)
        }


# Test function
if __name__ == "__main__":
    client = SchwabAPIClient()

    # Test single quote
    print("Testing AAPL quote...")
    quote = client.get_quote("AAPL")
    if quote:
        formatted = client.format_quote_for_trading(quote)
        print(f"AAPL: ${formatted.get('last_price', 0):.2f}")

    # Test bulk quotes
    print("\nTesting bulk quotes...")
    symbols = ["AAPL", "MSFT", "GOOGL"]
    quotes = client.get_quotes_bulk(symbols)
    print(f"Got {len(quotes)} quotes")
