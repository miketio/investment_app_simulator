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





def get_market_value(self):
    """
    Calculate the total market value of the portfolio excluding cash.

    :return: Total market value of the portfolio.
    """
    return self.get_portfolio_value() - sum(txn['quantity'] for txn in self.assets['CASH'].values())


def get_dividend_yield(self, date: str):
    """
    Calculate the overall dividend yield of the portfolio as of a specific date.
    :param date: The date for which to fetch the dividend yield.
    :return: Dividend yield as a percentage of market value as of the specified date.
    """
    total_dividends = 0.0
    total_market_value = 0.0

    for symbol, transactions in self.assets.items():
        if symbol == 'CASH':
            continue

        stock = yf.Ticker(symbol)
        dividend_yield = stock.info.get('dividendYield', 0.0)

        # Fetch the stock price as of the specific date
        price_at_date = self.data_fetcher.get_price_at_date(symbol, date)
        total_quantity = sum(txn['quantity'] for txn in transactions.values())
        market_value = price_at_date * total_quantity

        total_dividends += market_value * dividend_yield
        total_market_value += market_value

    if total_market_value == 0:
        return 0.0
    return (total_dividends / total_market_value) * 100

def get_yield_on_cost(self, date: str):
    """
    Calculate the yield on cost of the portfolio as of a specific date.
    :param date: The date for which to fetch the yield on cost.
    :return: Yield on cost as a percentage.
    """
    total_dividends = 0.0
    total_cost = 0.0

    for symbol, transactions in self.assets.items():
        if symbol == 'CASH':
            continue

        stock = yf.Ticker(symbol)
        dividend_yield = stock.info.get('dividendYield', 0.0)

        # Total cost based on original purchase price
        total_cost += sum(txn['quantity'] * txn['price'] for txn in transactions.values())
        
        # Calculate dividends up to the specific date
        total_dividends += dividend_yield * total_cost

    if total_cost == 0:
        return 0.0
    return (total_dividends / total_cost) * 100

def get_last_change_percent(self):
    """
    Calculate the percentage change in portfolio value over the last period.

    :return: Percentage change in portfolio value.
    """
    if not self.simulation_date:
        return 0.0
    previous_date = (datetime.strptime(self.simulation_date, "%Y-%m-%d")- timedelta(days=1)).strftime("%Y-%M-%d")
    current_value = self.get_portfolio_value(date=self.simulation_date)
    previous_value = self.get_portfolio_value(date=previous_date)
    if previous_value == 0:
        return 0.0
    return ((current_value - previous_value) / previous_value) * 100

def get_dividend_data(self, date: str):
    """
    Get cumulative dividend data for the portfolio from Yahoo Finance up to a specific date.
    :param date: The date for which to fetch cumulative dividend data.
    :return: A DataFrame containing the cumulative dividend data up to the specified date.
    """
    dividend_data = {}
    
    for symbol, transactions in self.assets.items():
        if symbol == 'CASH':
            continue
        
        stock = yf.Ticker(symbol)
        dividends = stock.dividends  # Get full dividend history
        
        # Filter dividends up to the specified date
        dividends = dividends[dividends.index <= date]

        if not dividends.empty:
            cumulative_dividends = dividends.sum()  # Sum up dividends
            total_quantity = sum(txn['quantity'] for txn in transactions.values())
            dividend_data[symbol] = cumulative_dividends * total_quantity
        else:
            dividend_data[symbol] = 0.0
    
    # Convert to DataFrame
    dividend_df = pd.DataFrame(dividend_data.items(), columns=["Symbol", "Cumulative Dividend"])
    return dividend_df

def get_diversification_data(self, date: str):
    """
    Get diversification data for the portfolio by sector on a specific date.
    :param date: The date for which to fetch diversification data.
    :return: A DataFrame containing the portfolio's diversification by sector as of the specified date.
    """
    diversification_data = defaultdict(float)

    for symbol, transactions in self.assets.items():
        if symbol == 'CASH':
            continue

        stock = yf.Ticker(symbol)
        info = stock.info
        sector = info.get('sector', 'Unknown')

        # Fetch the stock price as of the specific date
        price_at_date = self.data_fetcher.get_price_at_date(symbol, date)
        total_quantity = sum(txn['quantity'] for txn in transactions.values())
        diversification_data[sector] += price_at_date * total_quantity

    # Convert to DataFrame
    diversification_df = pd.DataFrame(list(diversification_data.items()), columns=['Sector', 'Value'])
    return diversification_df

def get_income_data(self, date: str):
    """
    Get monthly income data (dividends) for the portfolio as of a specific date.
    :param date: The date for which to fetch income data.
    :return: A DataFrame containing the monthly income data up to the specified date.
    """
    income_data = defaultdict(float)

    for symbol, transactions in self.assets.items():
        if symbol == 'CASH':
            continue

        stock = yf.Ticker(symbol)
        dividends = stock.dividends

        # Filter dividends up to the specified date
        dividends = dividends[dividends.index <= date]

        if not dividends.empty:
            # Group dividends by month and sum them using 'ME'
            monthly_income = dividends.resample('ME').sum()  # Changed 'M' to 'ME'
            total_quantity = sum(txn['quantity'] for txn in transactions.values())
            for div_date, amount in monthly_income.items():
                income_data[div_date.strftime('%B %Y')] += amount * total_quantity

    # Convert to DataFrame
    income_df = pd.DataFrame(income_data.items(), columns=['Month', 'Amount'])
    return income_df

def analyze_sustainability_score(self,esg_data):
    """
    Analyze the sustainability score by comparing totalEsg, environmentScore, socialScore, and governanceScore to peer ones
    and give a rate from 1 to 5. Also, check for any problems in the company and return true if any issues are found in the specified categories.

    Args:
    esg_data (dict): A dictionary containing ESG data.

    Returns:
    dict: A dictionary containing the ratings and problem status.
    """
    ratings = {}
    
    def calculate_rating(score, peer_performance):
        min_score = peer_performance['min']
        avg_score = peer_performance['avg']
        max_score = peer_performance['max']
    
        third_range1 = (avg_score - min_score) / 3
        third_range2 = (-avg_score + max_score) / 3
        if score <= min_score + third_range1:
            return "Very low"
        elif score <= min_score + 2 * third_range1:
            return "Low"
        elif score >= max_score - third_range2:
            return "Very high"
        elif score >= max_score - 2 * third_range2:
            return "High"
        else:
            return "Average"

    ratings['totalEsg'] = calculate_rating(esg_data.esgScores['totalEsg'], esg_data.esgScores['peerEsgScorePerformance'])
    ratings['environmentScore'] = calculate_rating(esg_data.esgScores['environmentScore'], esg_data.esgScores['peerEnvironmentPerformance'])
    ratings['socialScore'] = calculate_rating(esg_data.esgScores['socialScore'], esg_data.esgScores['peerSocialPerformance'])
    ratings['governanceScore'] = calculate_rating(esg_data.esgScores['governanceScore'], esg_data.esgScores['peerGovernancePerformance'])

    # Check for any problems in the specified categories
    problems = [
        'adult', 'alcoholic', 'animalTesting', 'catholic', 'controversialWeapons',
        'smallArms', 'furLeather', 'gambling', 'gmo', 'militaryContract', 'nuclear',
        'pesticides', 'palmOil', 'coal', 'tobacco'
    ]
    
    has_problems = any(esg_data.esgScores.get(problem, False) for problem in problems)

    return {
        'ratings': ratings,
        'has_problems': has_problems
    }

def get_detailed_stock_data(self, date: str):
    """
    Get detailed stock data including price and performance as of a specific date.
    :param date: The date for which to fetch detailed stock data.
    :return: A DataFrame containing the detailed stock data as of the specified date.
    """
    detailed_data = []

    for symbol, transactions in self.assets.items():
        if symbol == 'CASH':
            continue

        stock = yf.Ticker(symbol)
        info = stock.info
        # Fetch current price as of the specified date
        current_price = self.data_fetcher.get_price_at_date(symbol, date)

        # Analyze sustainability score
            # Analyze sustainability score
        esg_scores = stock.sustainability
        sustainability_analysis = self.analyze_sustainability_score(esg_scores) if not esg_scores.empty else {'ratings': {}, 'has_problems': False}# Calculate cost basis, market value, and , gains/losses
        
        
        total_quantity = sum(txn['quantity'] for txn in transactions.values())
        total_cost_basis = sum(txn['quantity'] * txn['price'] for txn in transactions.values())
        market_value = current_price * total_quantity
        gain_loss = market_value - total_cost_basis
        gain_loss_pct = (gain_loss / total_cost_basis) * 100 if total_cost_basis != 0 else 0.0
        
        # Get analyst recommendations summary
        recommendations_summary = stock.recommendations
        recommendations_data = {
            'Strong Buy': recommendations_summary.get('strongBuy', [0])[0],
            'Buy': recommendations_summary.get('buy', [0])[0],
            'Hold': recommendations_summary.get('hold', [0])[0],
            'Sell': recommendations_summary.get('sell', [0])[0],
            'Strong Sell': recommendations_summary.get('strongSell', [0])[0]
        }
        advice = max(recommendations_data, key=recommendations_data.get)
        # Get institutional holders summary
        institutional_holders_summary = stock.major_holders
        holders_data = {
            'Insiders Percent Held':  round(institutional_holders_summary.iloc[0]["Value"],3) ,
            # 'Institutions Percent Held': institutional_holders_summary.iloc[1]["Value"] ,
            'Institutions Float Percent Held': round(institutional_holders_summary.iloc[2]["Value"],2) ,
            'Institutions Count': institutional_holders_summary.iloc[3]["Value"] 
        }

        detailed_data.append({
            'Symbol': symbol,
            'Name': info.get('longName', 'Unknown'),
            'Sector': info.get('sector', 'Unknown'),
            'Industry': info.get('industry', 'Unknown'),
            'Forward P/E': round(info.get('forwardPE', 0),2),
            'Price/Sales': round(info.get('priceToSalesTrailing12Months', 0),2),
            'Price/Book': round(info.get('priceToBook', 0),2),
            'Beta': round(info.get('beta', 0),2),
            'EPS (TTM)': info.get('trailingEps', 0),
            **sustainability_analysis['ratings'],
            'Has Problems': sustainability_analysis['has_problems'],
            **holders_data,
            'Advice': advice
        })
        # detailed_data.append({
        #     'Symbol': symbol,
        #     'Name': info.get('longName', 'Unknown'),
        #     'Sector': info.get('sector', 'Unknown'),
        #     'Industry': info.get('industry', 'Unknown'),
        #     'Country': info.get('country', 'Unknown'),
        #     'Market Cap': info.get('marketCap', 0),
        #     'Enterprise Value': info.get('enterpriseValue', 0),
        #     'Trailing P/E': info.get('trailingPE', 0),
        #     'Forward P/E': info.get('forwardPE', 0),
        #     'PEG Ratio': info.get('pegRatio', 0),
        #     'Price/Sales': info.get('priceToSalesTrailing12Months', 0),
        #     'Price/Book': info.get('priceToBook', 0),
        #     'Previous Close': info.get('previousClose', 0),
        #     'Open': info.get('open', 0),
        #     'Beta': info.get('beta', 0),
        #     'Dividend Rate': info.get('dividendRate', 0),
        #     'Dividend Yield': info.get('dividendYield', 0),
        #     'Ex-Dividend Date': info.get('exDividendDate', 'N/A'),
        #     'Payout Ratio': info.get('payoutRatio', 0),
        #     'Earnings Date': info.get('earningsDate', 'N/A'),
        #     'EPS (TTM)': info.get('trailingEps', 0),
        #     'EPS (Forward)': info.get('forwardEps', 0),
        #     'Revenue (TTM)': info.get('totalRevenue', 0),
        #     'Major Holders': info.get('majorHoldersBreakdown', 'N/A'),
        #     'Institutional Holders': info.get('institutionalHolders', 'N/A'),
        #     'Mutual Fund Holders': info.get('fundHolders', 'N/A'),
        #     'Insider Transactions': info.get('insiderTransactions', 'N/A'),
        #     'Analyst Price Targets': info.get('targetMeanPrice', 0),
        #     'Earnings Estimate': info.get('earningsEstimate', 'N/A'),
        #     'Revenue Estimate': info.get('revenueEstimate', 'N/A'),
        #     'EPS Trend': info.get('epsTrend', 'N/A'),
        #     'EPS Revisions': info.get('epsRevisions', 'N/A'),
        #     'Growth Estimates': info.get('growthEstimates', 'N/A'),
        #     'Sustainability Scores': info.get('sustainability', 'N/A'),
        #     'Options Expirations': info.get('optionExpirationDates', 'N/A'),
        #     'Quantity': total_quantity,
        #     'Cost Basis': total_cost_basis,
        #     'Market Value': market_value,
        #     'Gain/Loss $': gain_loss,
        #     'Gain/Loss %': gain_loss_pct
        # })

    # Convert to DataFrame
    detailed_df = pd.DataFrame(detailed_data)
    return detailed_df

def get_operation_history(self):
        """
        Get the operation history of the portfolio.

        Returns:
        pd.DataFrame: A DataFrame containing the operation history.
        """
        history = []

        for symbol, transactions in self.assets.items():
            for txn_id, txn in transactions.items():
                operation = {
                    'Transaction ID': int(txn_id),
                    'Symbol': symbol,
                    'Quantity': round(txn['quantity'],2),
                    'Price': round(txn['price'],2),
                    'Date': txn['date'],
                    'Type': 'Cash' if symbol == 'CASH' else ('Buy' if txn['quantity'] > 0 else 'Sell')
                }
                history.append(operation)

        # Convert to DataFrame
        history_df = pd.DataFrame(history)
        return history_df

def get_current_actives(self):
    """
    Get the current actives of the portfolio.

    Returns:
    pd.DataFrame: A DataFrame containing the current actives.
    """
    actives = []

    for symbol, transactions in self.assets.items():
        if symbol == 'CASH':
            continue  # Skip cash transactions
        total_quantity = sum(txn['quantity'] for txn in transactions.values())
        if self.simulation_date:
            current_price = self.data_fetcher.get_price_at_date(symbol, self.simulation_date)
            one_month_ago = (datetime.strptime(self.simulation_date, "%Y-%m-%d") - timedelta(days=30)).strftime("%Y-%m-%d")
            one_year_ago = (datetime.strptime(self.simulation_date, "%Y-%m-%d") - timedelta(days=365)).strftime("%Y-%m-%d")
            price_one_month_ago = self.data_fetcher.get_price_at_date(symbol, one_month_ago)
            price_one_year_ago = self.data_fetcher.get_price_at_date(symbol, one_year_ago)
        else:
            current_price = self.data_fetcher.get_real_time_price(symbol)
            one_month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            one_year_ago = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
            price_one_month_ago = self.data_fetcher.get_price_at_date(symbol, one_month_ago)
            price_one_year_ago = self.data_fetcher.get_price_at_date(symbol, one_year_ago)

        current_value = total_quantity * current_price
        change_over_month = ((current_price - price_one_month_ago) / price_one_month_ago) * 100 if price_one_month_ago else 0
        change_over_year = ((current_price - price_one_year_ago) / price_one_year_ago) * 100 if price_one_year_ago else 0

        actives.append({
            'Symbol': symbol,
            'Number of Stocks': total_quantity,
            'Current Price': round(current_price, 2),
            'Current Value': round(current_value, 2),
            'Change Over Month (%)': round(change_over_month, 2),
            'Change Over Year (%)': round(change_over_year, 2)
        })

    # Convert to DataFrame
    actives_df = pd.DataFrame(actives)
    return actives_df