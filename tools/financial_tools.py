import yfinance as yf
from datetime import datetime
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import json
import pandas as pd

class StockInput(BaseModel):
    """Input schema for YFinanceStockTool."""
    symbol: str = Field(..., description="The stock symbol to analyze (e.g., 'AAPL', 'GOOGL')")

class HistoricalDataInput(BaseModel):
    """Input schema for Historical Stock Data Tool."""
    symbol: str = Field(..., description="The stock symbol to analyze (e.g., 'AAPL', 'GOOGL')")
    period: str = Field("1y", description="Period to fetch data for: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max")
    interval: str = Field("1d", description="Data interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo")

class YFinanceStockTool(BaseTool):
    name: str = "stock_data_tool"
    description: str = """
    A tool for getting real-time and historical stock market data.
    Use this tool when you need specific stock information like:
    - Latest stock price from most recent trading day
    - Current price and trading volume
    - Historical price data
    - Company financials and metrics
    - Company information and business summary
    """
    args_schema: type[BaseModel] = StockInput

    def _run(self, symbol: str) -> str:
        try:
            stock = yf.Ticker(symbol)
            
            # Get basic info
            info = stock.info
            
            # Get recent market data
            hist = stock.history(period="1mo")
            
            # Get the latest trading day's data
            latest_data = hist.iloc[-1]
            latest_date = latest_data.name.strftime('%Y-%m-%d')
            
            # Format 52-week data with dates
            hist_1y = stock.history(period="1y")
            fifty_two_week_high_date = hist_1y['High'].idxmax().strftime('%Y-%m-%d')
            fifty_two_week_low_date = hist_1y['Low'].idxmin().strftime('%Y-%m-%d')
            
            # Prepare the response
            response = {
                "company_name": info.get("longName", "N/A"),
                "latest_trading_data": {
                    "date": latest_date,
                    "price": latest_data['Close'],
                    "volume": latest_data['Volume'],
                    "change": f"{((latest_data['Close'] - latest_data['Open']) / latest_data['Open'] * 100):.2f}%"
                },
                "52_week_high": {
                    "price": info.get("fiftyTwoWeekHigh", "N/A"),
                    "date": fifty_two_week_high_date
                },
                "52_week_low": {
                    "price": info.get("fiftyTwoWeekLow", "N/A"),
                    "date": fifty_two_week_low_date
                },
                "market_cap": info.get("marketCap", "N/A"),
                "pe_ratio": info.get("forwardPE", "N/A"),
                "dividend_yield": info.get("dividendYield", "N/A"),
                "business_summary": info.get("longBusinessSummary", "N/A"),
                "analyst_rating": info.get("recommendationKey", "N/A")
            }
            
            return json.dumps(response, indent=2)
            
        except Exception as e:
            return f"Error fetching data for {symbol}: {str(e)}"

    def _arun(self, symbol: str) -> str:
        # Async implementation if needed
        raise NotImplementedError("Async version not implemented")

class HistoricalStockDataTool(BaseTool):
    name: str = "historical_stock_data_tool"
    description: str = """
    A tool for getting historical stock market data in a format suitable for visualizations.
    Use this tool when you need to generate charts and analyze trends over time.
    The data returned is ideal for creating price charts, volume analysis, and technical indicators.
    """
    args_schema: type[BaseModel] = HistoricalDataInput

    def _run(self, symbol: str, period: str = "1y", interval: str = "1d") -> str:
        try:
            stock = yf.Ticker(symbol)
            
            # Get historical data
            hist = stock.history(period=period, interval=interval)
            
            # Reset index to make Date a column
            hist = hist.reset_index()
            
            # Convert Date to string format
            hist['Date'] = hist['Date'].dt.strftime('%Y-%m-%d')
            
            # Calculate some basic technical indicators
            if len(hist) > 20:
                # 20-day moving average
                hist['MA20'] = hist['Close'].rolling(window=20).mean()
                
                # 50-day moving average
                if len(hist) > 50:
                    hist['MA50'] = hist['Close'].rolling(window=50).mean()
                
                # Relative Strength Index (RSI)
                delta = hist['Close'].diff()
                gain = delta.where(delta > 0, 0).rolling(window=14).mean()
                loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
                rs = gain / loss
                hist['RSI'] = 100 - (100 / (1 + rs))
            
            # Convert to JSON
            result = {
                "symbol": symbol,
                "period": period,
                "interval": interval,
                "data": hist.to_dict(orient='records')
            }
            
            return json.dumps(result)
            
        except Exception as e:
            return f"Error fetching historical data for {symbol}: {str(e)}"

    def _arun(self, symbol: str, period: str = "1y", interval: str = "1d") -> str:
        # Async implementation if needed
        raise NotImplementedError("Async version not implemented")