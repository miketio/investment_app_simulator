import yfinance as yf
import json
from collections import defaultdict
from datetime import datetime
import time
from datetime import datetime, timedelta
import pandas as pd
import copy
from data_fetcher import DataFetcher
from collections import defaultdict
from portrfolio_manager_functions import (
    get_market_value,
    get_dividend_yield,
    get_yield_on_cost,
    get_last_change_percent,
    get_dividend_data,
    get_diversification_data,
    get_income_data,
    analyze_sustainability_score,
    get_detailed_stock_data,
    get_operation_history,
    get_current_actives
)


class Portfolio:
    """
    A class to manage a portfolio of stocks and cash.
    """
    
    def __init__(self, simulation_date: str = None):
        """
        Initialize the portfolio. Optionally set a simulation date.
        :param simulation_date: Date for the simulation in 'YYYY-MM-DD' format.
        """
        self.assets = {"CASH": {}}  # Starting with cash asset
        self.total_value = 0.0  # Total value of the portfolio
        self.data_fetcher = DataFetcher()  # Instance of DataFetcher
        self.simulation_date = simulation_date  # Date for simulated transactions
        self.transaction_id = 0  # Unique transaction ID
        self.cash_inflows = []  # Track cash inflows with dates
    
    get_market_value = get_market_value
    get_dividend_yield = get_dividend_yield
    get_yield_on_cost = get_yield_on_cost
    get_last_change_percent = get_last_change_percent
    get_dividend_data = get_dividend_data
    get_diversification_data = get_diversification_data
    get_income_data = get_income_data
    analyze_sustainability_score = analyze_sustainability_score
    get_detailed_stock_data = get_detailed_stock_data
    get_operation_history = get_operation_history
    get_current_actives = get_current_actives
    
    def add_cash(self, amount: float, inflow: bool = True):
        """
        Add cash to the portfolio.

        :param amount: The amount of cash to add
        :param inflow: True if the cash is from an external source, False if it is a transaction
        """
        symbol = "CASH"
        current_cash = sum(txn['quantity'] for txn in self.assets[symbol].values())
        if current_cash + amount <= 0:
            print("Total cash balance must be greater than zero.")
            return
        
        self.transaction_id += 1
        transaction = {
            'quantity': amount,
            'price': 1,
            'date': self.simulation_date or datetime.datetime.now().strftime("%Y-%m-%d")
        }
        self.assets[symbol][self.transaction_id] = transaction
        if inflow and amount > 0:
            self.cash_inflows.append({'amount': amount, 'date': transaction['date']})  # Track cash inflows with dates
        print(f"Added ${amount:.2f} to cash.")


    def buy_asset(self, symbol: str, quantity: int):
        """
        Simulate buying assets.

        :param symbol: The stock symbol to buy
        :param quantity: The number of shares to buy
        """
        symbol = symbol.upper()
        if quantity <= 0:
            print("Quantity must be greater than zero.")
            return

        # Fetch price for the asset based on simulation date or real-time
        if self.simulation_date:
            price = self.data_fetcher.get_price_at_date(symbol, self.simulation_date)
        else:
            price = self.data_fetcher.get_real_time_price(symbol)
        
        if price <= 0:
            print(f"Failed to retrieve the price for {symbol}. Transaction aborted.")
            return
        
        cost = quantity * price
        cash_balance = sum(txn['quantity'] for txn in self.assets['CASH'].values())
        if cost > cash_balance:
            print("Not enough cash balance to buy this asset.")
            return

        # Deduct cash
        self.add_cash(-cost, inflow=False)  # Mark as transaction

        # Add the asset transaction
        self.transaction_id += 1
        transaction = {
            'quantity': quantity,
            'price': price,
            'date': self.simulation_date or datetime.datetime.now().strftime("%Y-%m-%d")
        }
        if symbol not in self.assets:
            self.assets[symbol] = {}
        self.assets[symbol][self.transaction_id] = transaction

        print(f"Bought {quantity} of {symbol} at ${price:.2f} each.")

    def sell_asset(self, symbol: str, quantity: int):
        """
        Simulate selling assets.

        :param symbol: The stock symbol to sell
        :param quantity: The number of shares to sell
        """
        symbol = symbol.upper()
        if symbol not in self.assets or not self.assets[symbol]:
            print(f"{symbol} is not in the portfolio.")
            return

        total_quantity = sum(txn['quantity'] for txn in self.assets[symbol].values())
        if quantity <= 0 or quantity > total_quantity:
            print("Invalid quantity for selling.")
            return

        # Fetch price for the asset based on simulation date or real-time
        if self.simulation_date:
            price = self.data_fetcher.get_price_at_date(symbol, self.simulation_date)
        else:
            price = self.data_fetcher.get_real_time_price(symbol)
        
        if price <= 0:
            print(f"Failed to retrieve the price for {symbol}. Transaction aborted.")
            return

        # Calculate the sale value
        sale_value = quantity * price
        # Add cash from sale
        self.add_cash(sale_value, inflow=False)  # Mark as transaction

        # Update the asset quantity
        remaining_quantity = quantity
        for txn_id, txn in list(self.assets[symbol].items()):
            if remaining_quantity <= 0:
                break
            if txn['quantity'] <= remaining_quantity:
                remaining_quantity -= txn['quantity']
                del self.assets[symbol][txn_id]
            else:
                self.assets[symbol][txn_id]['quantity'] -= remaining_quantity
                remaining_quantity = 0
        self.assets = {key: value for key, value in self.assets.items() if value}   
        # print(self.assets)
        print(f"Sold {quantity} of {symbol} at ${price:.2f} each.")

    def show_portfolio(self):
        """
        Display the assets in the user's portfolio along with their details.
        """
        if not self.assets:
            print("Your portfolio is empty.")
            return

        print("\nCurrent Portfolio:")
        for symbol, transactions in self.assets.items():
            if symbol == 'CASH':
                total_cash = sum(txn['quantity'] for txn in transactions.values())
                print(f"{symbol}: ${total_cash:.2f} cash")
                continue
            total_quantity = sum(txn['quantity'] for txn in transactions.values())
            avg_purchase_price = sum(txn['quantity'] * txn['price'] for txn in transactions.values()) / total_quantity
            if self.simulation_date:
                current_price = self.data_fetcher.get_price_at_date(symbol, self.simulation_date)
            else:
                current_price = self.data_fetcher.get_real_time_price(symbol)
            print(f"{symbol}: {total_quantity} shares @ ${current_price:.2f} each (Avg. Purchase Price: ${avg_purchase_price:.2f})")
        
        print(f"\nTotal Portfolio Value: ${self.get_portfolio_value():.2f}")

    def save_portfolio(self, filename='portfolio.json'):
        """
        Save the current portfolio to a JSON file.

        :param filename: The name of the file to save the portfolio
        """
        with open(filename, 'w') as f:
            json.dump({
                'assets': self.assets,
                'simulation_date': self.simulation_date,
                'cash_inflows': self.cash_inflows
            }, f)
        print(f"Portfolio saved to {filename}")

    def load_portfolio(self, filename='portfolio.json'):
        """
        Load the portfolio from a JSON file.

        :param filename: The name of the file to load the portfolio
        """
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                self.assets = data['assets']
                self.simulation_date = data.get('simulation_date', None)
                self.cash_inflows = data['cash_inflows']
                self.transaction_id =  max(int(identifier) for asset_data in data['assets'].values() for identifier in asset_data.keys() if identifier.isdigit())
            print(f"Portfolio loaded from {filename}")
        except Exception as e:
            print(f"Error loading portfolio: {e}")

    def copy(self):
        """
        Create a deep copy of the Portfolio object.

        :return: A deep copy of the current portfolio instance.
        """
        return copy.deepcopy(self)
    
    def get_portfolio_value(self, date: str = "Not set", end_date = None) -> float:
        """
        Calculate the current total value of the portfolio based on the latest prices.

        :return: Total portfolio value (cash + assets)
        """
        if date == "Not set":
            date = self.simulation_date

        if not end_date:
            total_value = sum(txn['quantity'] for txn in self.assets['CASH'].values())  # Start with cash
            for symbol, transactions in self.assets.items():
                if symbol == 'CASH':
                    continue  # Skip cash since it's already counted
                if self.simulation_date:
                    price_at_date = self.data_fetcher.get_price_at_date(symbol, date)
                else:
                    price_at_date = self.data_fetcher.get_real_time_price(symbol)
                total_quantity = sum(txn['quantity'] for txn in transactions.values())
                total_value += price_at_date * total_quantity
            return total_value
        else:
            date_range = pd.date_range(start=date, end=end_date)
            date_range = date_range.strftime('%Y-%m-%d')
            combined_prices = pd.DataFrame(index=date_range)
            for symbol, transactions in self.assets.items():
                if symbol == 'CASH':
                    continue  # Skip cash since it's already counted
                prices = self.data_fetcher.fetch_stock_data(symbol, start_date=date, end_date=end_date)
                if prices is not None and not prices.empty:
                    # Rename 'Close' to symbol name for clarity
                    prices.rename(columns={'Close': symbol}, inplace=True)
                    prices.index = prices.index.strftime('%Y-%m-%d')
                    combined_prices = combined_prices.join(prices[[symbol]], how='outer')
            # Forward fill missing prices
            combined_prices.ffill(inplace=True)
            
            # Calculate portfolio values
            total_values = []
            for single_date in date_range:
                # Calculate cash balance up to the current date
                total_cash = sum(txn['quantity'] for txn in self.assets['CASH'].values() if txn['date'] <= single_date)
                total_value = total_cash  # Start with cash

                for symbol, transactions in self.assets.items():
                    if symbol == 'CASH':
                        continue
                    # Get the price for the specific date using the symbol directly
                    price_at_date = combined_prices.loc[single_date, symbol] if single_date in combined_prices.index else 0
                    total_quantity = sum(txn['quantity'] for txn in transactions.values() if txn['date'] <= single_date)
                    total_value += price_at_date * total_quantity

                total_values.append(total_value)
            return total_values


    def get_cash(self):
        """
        Return the current cash balance.

        :return: Current cash balance.
        """
        if 'CASH' not in self.assets or not self.assets['CASH']:
            return 0
        return sum(txn['quantity'] for txn in self.assets['CASH'].values())

    def set_total_value(self):
        self.total_value = self.get_portfolio_value()

if __name__ == "__main__":
    # Example usage of Portfolio class
    # Set the simulation date to '2023-02-01'
    my_portfolio = Portfolio(simulation_date="2023-02-01")
    # Load portfolio if it exists
    my_portfolio.load_portfolio()
    my_portfolio.add_cash(10000)
    # Buying and selling assets at the specified simulation date
    my_portfolio.buy_asset("AAPL", 10)  # Buy 10 shares of AAPL on 2023-02-01
    my_portfolio.buy_asset("TSLA", 5)   # Buy 5 shares of TSLA on 2023-02-01
    my_portfolio.sell_asset("AAPL", 15)  # Sell 5 shares of AAPL on 2023-02-01
    
    # # Show current portfolio
    # print(my_portfolio.get_portfolio_value(date="2023-02-01", end_date="2023-02-20"))
    # print(my_portfolio.get_detailed_stock_data("2024-10-08"))

    # Save portfolio to file
    # my_portfolio.save_portfolio()
