import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

class DataFetcher:
    """
    A class to fetch stock data from Yahoo Finance using yfinance.
    """
    
    def get_real_time_price(self, symbol: str) -> float:
        """
        Fetch the real-time price for a given symbol.

        :param symbol: Stock symbol
        :return: Current price as a float
        """
        try:
            stock = yf.Ticker(symbol)
            latest_price = stock.history(period="1d")["Close"].iloc[-1]
            return latest_price
        except Exception as e:
            print(f"Error fetching real-time price for {symbol}: {e}")
            return 0.0

    def get_price_at_date(self, symbol: str, date: str) -> float:
        """
        Fetch the historical price for a given symbol at a specific date.
        If no data is available for that exact date, look back for up to 2 weeks
        and return the last available price.

        :param symbol: Stock symbol
        :param date: Date in 'YYYY-MM-DD' format
        :return: Price at the given date or last available price within 2 weeks, as a float
        """
        try:
            stock = yf.Ticker(symbol)
            target_date = datetime.strptime(date, "%Y-%M-%d")
            
            # Fetch price for the given date
            history = stock.history(start=target_date.strftime("%Y-%M-%d"), end=(target_date + timedelta(days=1)).strftime("%Y-%M-%d"))
            
            if not history.empty:
                return history["Close"].iloc[-1]  # Return the price if available

            # If no data is found for the exact date, look back 2 weeks
            start_date = target_date - timedelta(days=14)
            history = stock.history(start=start_date.strftime("%Y-%M-%d"), end=(target_date + timedelta(days=1)).strftime("%Y-%M-%d"))
            
            # Check if there's any available price within the 2-week range

            if not history.empty:
                last_available_price = history["Close"].iloc[-1]  # Get the last available price in the range
                return last_available_price
            else:
                print(f"No available data for {symbol} within the last 2 weeks from {date}.")
                return 0.0  # Return 0.0 if no data is found within the 2-week range

        except Exception as e:
            print(f"Error fetching historical price for {symbol} on {date}: {e}")
            return 0.0
        
    # Helper function to fetch historical stock data using yfinance
    def fetch_stock_data(self, symbol: str, interval: str = "1d", start_date: str = "2020-01-01", end_date: str = "2023-01-01") -> pd.DataFrame:
        """
        Fetch historical stock data for the given symbol and time period using yfinance.

        Args:
        symbol (str): The stock ticker symbol.
        interval (str): Data interval (e.g., "1d" for daily). Default is "1d".
        start_date (str): The start date for fetching data.
        end_date (str): The end date for fetching data.

        Returns:
        pd.DataFrame: A DataFrame containing the historical stock data.
        """
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(interval=interval, start=start_date, end=end_date)
            if data.empty:
                print(f"No data found for {symbol}.")
                return None
            return data
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
