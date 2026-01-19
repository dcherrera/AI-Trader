"""
Schwab Real-Time Price Tool for AI-Trader
Fetches live market data from Schwab API instead of local JSON files
"""

from fastmcp import FastMCP
import sys
import os
from typing import Dict, List, Any
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from agent_tools.schwab_client import SchwabAPIClient
from tools.general_tools import get_config_value

mcp = FastMCP("SchwabPrices")

# Initialize Schwab client
try:
    schwab_client = SchwabAPIClient()
    print("✅ Schwab API client initialized")
except Exception as e:
    print(f"❌ Failed to initialize Schwab client: {e}")
    schwab_client = None


@mcp.tool()
def get_real_time_price(symbol: str) -> Dict[str, Any]:
    """
    Get real-time price for a stock symbol from Schwab API

    Args:
        symbol: Stock symbol (e.g., "AAPL", "MSFT")

    Returns:
        Dict containing:
        - symbol: Stock symbol
        - current_price: Current market price
        - bid_price: Bid price
        - ask_price: Ask price
        - high: Day's high
        - low: Day's low
        - volume: Trading volume
        - timestamp: Quote timestamp
    """
    if not schwab_client:
        return {"error": "Schwab API client not initialized"}

    try:
        quote_data = schwab_client.get_quote(symbol)
        if not quote_data:
            return {"error": f"No quote data available for {symbol}"}

        formatted = schwab_client.format_quote_for_trading(quote_data)

        return {
            "symbol": symbol,
            "current_price": formatted.get("last_price", 0),
            "bid_price": formatted.get("sell_price", 0),
            "ask_price": formatted.get("buy_price", 0),
            "high": formatted.get("high", 0),
            "low": formatted.get("low", 0),
            "volume": formatted.get("volume", 0),
            "timestamp": formatted.get("timestamp", 0),
            "status": "success"
        }

    except Exception as e:
        return {"error": f"Failed to fetch price for {symbol}: {str(e)}"}


@mcp.tool()
def get_multiple_prices(symbols: str) -> Dict[str, Any]:
    """
    Get real-time prices for multiple stock symbols from Schwab API

    Args:
        symbols: Comma-separated stock symbols (e.g., "AAPL,MSFT,GOOGL")

    Returns:
        Dict with prices for each symbol
    """
    if not schwab_client:
        return {"error": "Schwab API client not initialized"}

    try:
        # Parse symbols
        symbol_list = [s.strip() for s in symbols.split(",")]

        # Get bulk quotes
        quotes = schwab_client.get_quotes_bulk(symbol_list)

        result = {}
        for symbol in symbol_list:
            if symbol in quotes:
                formatted = schwab_client.format_quote_for_trading({symbol: quotes[symbol]})
                result[f"{symbol}_price"] = formatted.get("last_price", 0)
                result[f"{symbol}_bid"] = formatted.get("sell_price", 0)
                result[f"{symbol}_ask"] = formatted.get("buy_price", 0)
            else:
                result[symbol] = {"error": "No data available"}

        return result

    except Exception as e:
        return {"error": f"Failed to fetch prices: {str(e)}"}


@mcp.tool()
def get_market_status() -> Dict[str, Any]:
    """
    Get current market status (open/closed, next open time, etc.)

    Returns:
        Dict with market status information
    """
    now = datetime.now()

    # Simple market hours check (9:30 AM - 4:00 PM ET on weekdays)
    # This is a simplified version - production should use Schwab's market hours API
    is_weekday = now.weekday() < 5  # Monday = 0, Friday = 4
    current_hour = now.hour
    current_minute = now.minute

    is_market_hours = (
        is_weekday and
        ((current_hour == 9 and current_minute >= 30) or
         (current_hour > 9 and current_hour < 16) or
         (current_hour == 16 and current_minute == 0))
    )

    return {
        "is_open": is_market_hours,
        "current_time": now.isoformat(),
        "day_of_week": now.strftime("%A"),
        "market_session": "regular_hours" if is_market_hours else "closed"
    }


if __name__ == "__main__":
    port = int(os.getenv("GETPRICE_HTTP_PORT", "8003"))
    print(f"🚀 Starting Schwab Price Tool on port {port}")
    mcp.run(transport="streamable-http", port=port)
