import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
from portfolio_manager import Portfolio  # Assuming Portfolio class exists
from color_palette import GENERAL_COLORS, GRAPH_COLORS, PIE_CHART_COLORS, TABLE_COLORS
from dash import dash_table
import html
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
ROUNDDIGIT = 3

def plot_just_figure(start_date: str, end_date: str):
    """
    Plot the the figure without any data.

    Args:
    portfolio (Portfolio): The user's portfolio.
    start_date (str): The start date of the range.
    end_date (str): The end date of the range.
    
    Returns:
    A Plotly figure object showing the portfolio's growth.
    """
        # Create an empty figure with axes titles and limits
    fig = go.Figure(layout=go.Layout(
        xaxis={'title': 'Date', 'range': [start_date, end_date]},
        yaxis={'title': 'Price ($)', 'range': [-1, 1]}  # Adjust the y-axis range as needed
    ))

    # Update the layout with additional styling
    fig.update_layout(
        plot_bgcolor=GENERAL_COLORS['background'],
        paper_bgcolor=GENERAL_COLORS['background'],
        font_color=GENERAL_COLORS['text_primary'],
        xaxis_title="Date",
        yaxis_title="Price ($)",
        xaxis=dict(tickangle=45)
    )
# Function to plot a pie chart showing portfolio asset allocation breakdown using Plotly
def plot_allocation_breakdown(portfolio: Portfolio):
    """
    Pie chart showing how the portfolio is distributed across different assets using Plotly.

    Args:
    portfolio (Portfolio): The user's portfolio object containing asset data.
    
    Returns:
    A Plotly figure object.
    """
    labels = []
    sizes = []
    
    # Calculate the total value of each asset
    for symbol, transactions in portfolio.assets.items():
        if symbol == 'CASH':
            total_quantity = sum(txn['quantity'] for txn in transactions.values())
            labels.append(symbol)
            sizes.append(round(total_quantity, ROUNDDIGIT))
        else:
            total_quantity = sum(txn['quantity'] for txn in transactions.values())
            current_price = portfolio.data_fetcher.get_real_time_price(symbol)
            asset_value = total_quantity * current_price
            labels.append(symbol)
            sizes.append(round(asset_value, ROUNDDIGIT))

    fig = px.pie(names=labels, values=sizes, title='Portfolio Asset Allocation Breakdown',
                 color_discrete_sequence=PIE_CHART_COLORS)
    fig.update_layout(
        plot_bgcolor=GENERAL_COLORS['background'],
        paper_bgcolor=GENERAL_COLORS['background'],
        font_color=GENERAL_COLORS['text_primary']
    )
    return fig

def plot_portfolio_growth_over_time(portfolio: Portfolio, start_date: str, end_date: str):
    """
    Plot the portfolio's value over a range of dates, using historical data.

    Args:
    portfolio (Portfolio): The user's portfolio.
    start_date (str): The start date of the range.
    end_date (str): The end date of the range.
    
    Returns:
    A Plotly figure object showing the portfolio's growth.
    """
    # Fetch the portfolio's value over the date range
    date_range = pd.date_range(start=start_date, end=end_date)
    portfolio_values = portfolio.get_portfolio_value(date=start_date, end_date=end_date)

    # Create a DataFrame for plotting
    simulation_data = pd.DataFrame({
        'Date': date_range,
        'Portfolio Value': [round(value, ROUNDDIGIT) for value in portfolio_values]
    })
    simulation_data.set_index('Date', inplace=True)

    # Plot the portfolio growth
    fig = px.line(simulation_data, x=simulation_data.index, y='Portfolio Value', 
                  title='Portfolio Growth Over Time', markers=True,
                  color_discrete_sequence=[GRAPH_COLORS['line_blue']])
    
    fig.update_layout(
        plot_bgcolor=GENERAL_COLORS['background'],
        paper_bgcolor=GENERAL_COLORS['background'],
        font_color=GENERAL_COLORS['text_primary'],
        xaxis_title="Date",
        yaxis_title="Portfolio Value ($)",
        xaxis=dict(tickangle=45)
    )
    return fig

def plot_asset_growth_over_time(portfolio: Portfolio, symbol: str, start_date: str, end_date: str):
    """
    Plot the price of a single asset in the portfolio over a range of dates.

    Args:
    portfolio (Portfolio): The user's portfolio object.
    symbol (str): The symbol of the asset to plot (e.g., 'AAPL').
    start_date (str): The start date of the range (format: 'YYYY-MM-DD').
    end_date (str): The end date of the range (format: 'YYYY-MM-DD').
    
    Returns:
    A Plotly figure object showing the asset's price growth over time.
    """

    # Fetch stock data for the specified date range
    prices = portfolio.data_fetcher.fetch_stock_data(symbol, start_date=start_date, end_date=end_date)

    # Create a DataFrame for plotting
    asset_data = pd.DataFrame({
        'Date': prices.index,  # Assuming prices have Date as the index
        'Price': prices['Close'].round(ROUNDDIGIT)  # Assuming 'Close' column holds the closing prices
    })
    asset_data.set_index('Date', inplace=True)

    # Extract buy transactions for the symbol
    buy_transactions = [
        {'Date': txn['date'], 'Quantity': txn['quantity'], 'Price': txn['price']}
        for txn in portfolio.assets.get(symbol, {}).values()
        if txn['quantity'] > 0
    ]
    buy_df = pd.DataFrame(buy_transactions)

    # Plot the asset's price over time
    fig = px.line(asset_data, x=asset_data.index, y='Price', 
                  title=f'Growth of {symbol} Over Time', markers=True,
                  color_discrete_sequence=[GRAPH_COLORS['line_blue']])
    
    # Add red dots for buy transactions
    if not buy_df.empty:
        buy_df['Date'] = pd.to_datetime(buy_df['Date'])
        buy_df.set_index('Date', inplace=True)
        buy_df['Price'] = buy_df['Price'].round(ROUNDDIGIT)
        fig.add_scatter(x=buy_df.index, y=buy_df['Price'], 
                        mode='markers', marker=dict(color=GRAPH_COLORS['marker'], size=10), 
                        name='Buy Transactions', text=buy_df.apply(lambda row: f"Quantity: {row['Quantity']}<br>Price: ${row['Price']:.2f}", axis=1),
                        hovertemplate='Date: %{x}<br>%{text}<extra></extra>')

    fig.update_layout(
        plot_bgcolor=GENERAL_COLORS['background'],
        paper_bgcolor=GENERAL_COLORS['background'],
        font_color=GENERAL_COLORS['text_primary'],
        xaxis_title="Date",
        yaxis_title="Price ($)",
        xaxis=dict(tickangle=45)
    )
    return fig

def plot_portfolio_profit_over_time(portfolio: Portfolio, start_date: str, end_date: str):
    """
    Plot the portfolio's profit over a range of dates, using historical data.

    Args:
    portfolio (Portfolio): The user's portfolio.
    start_date (str): The start date of the range.
    end_date (str): The end date of the range.
    
    Returns:
    A Plotly figure object showing the portfolio's profit.
    """
    # Fetch the portfolio's value over the date range
    date_range = pd.date_range(start=start_date, end=end_date)
    portfolio_values = portfolio.get_portfolio_value(date=start_date, end_date=end_date)

    # Initialize cumulative inflows
    cumulative_inflows = pd.Series(0.0, index=date_range)
    
    # Calculate cumulative cash inflows using boolean indexing
    for inflow in portfolio.cash_inflows:
        inflow_date = pd.to_datetime(inflow['date'])
        inflow_amount = inflow['amount']
        cumulative_inflows[date_range >= inflow_date] += inflow_amount

    # Calculate profit by subtracting cumulative cash inflows from portfolio values
    profit_values = [round(value - inflow, ROUNDDIGIT) for value, inflow in zip(portfolio_values, cumulative_inflows)]

    # Create a DataFrame for plotting
    simulation_data = pd.DataFrame({
        'Date': date_range,
        'Profit': profit_values
    })
    simulation_data.set_index('Date', inplace=True)

    # Extract buy transactions for plotting
    buy_transactions = []
    for symbol, transactions in portfolio.assets.items():
        if symbol == 'CASH':
            continue
        for txn in transactions.values():
            if txn['quantity'] > 0:
                buy_transactions.append({
                    'Date': txn['date'],
                    'Symbol': symbol,
                    'Quantity': txn['quantity']
                })
    buy_df = pd.DataFrame(buy_transactions)

    # Plot the portfolio profit
    fig = px.line(simulation_data, x=simulation_data.index, y='Profit', 
                  title='Portfolio Profit Over Time', markers=True,
                  color_discrete_sequence=[GRAPH_COLORS['line_blue']])
    
    # Add red dots for buy transactions
    if not buy_df.empty:
        buy_df['Date'] = pd.to_datetime(buy_df['Date'])
        buy_df_grouped = buy_df.groupby('Date').agg({
            'Symbol': lambda x: '<br>'.join(x),
            'Quantity': lambda x: '<br>'.join(map(str, x))
        }).reset_index()
        buy_df_grouped['Text'] = buy_df_grouped.apply(lambda row: f"Symbol: {row['Symbol']}<br>Quantity: {row['Quantity']}", axis=1)
        fig.add_scatter(x=buy_df_grouped['Date'], y=buy_df_grouped['Date'].map(simulation_data['Profit']), 
                        mode='markers', marker=dict(color=GRAPH_COLORS['marker'], size=10), 
                        name='Buy Transactions', text=buy_df_grouped['Text'],
                        hovertemplate='Date: %{x}<br>%{text}<extra></extra>')

    fig.update_layout(
        plot_bgcolor=GENERAL_COLORS['background'],
        paper_bgcolor=GENERAL_COLORS['background'],
        font_color=GENERAL_COLORS['text_primary'],
        xaxis_title="Date",
        yaxis_title="Profit ($)",
        xaxis=dict(tickangle=45)
    )
    return fig

# Function to plot cumulative dividends over time
def plot_dividend_cumulative(portfolio: Portfolio):
    """
    Plot the cumulative dividends over time.

    Args:
    portfolio (Portfolio): The user's portfolio object.
    
    Returns:
    A Plotly figure object showing the cumulative dividends.
    """
    dividend_data = portfolio.get_dividend_data(portfolio.simulation_date)

    # Ensure that the DataFrame contains 'Cumulative Dividend' and a time index
    if 'Cumulative Dividend' in dividend_data.columns:
        # Create a 'Year' column from the index or a specific date column if necessary
        if 'Date' in dividend_data.columns:
            dividend_data['Year'] = pd.to_datetime(dividend_data['Date']).dt.year  # Convert 'Date' column to datetime
        else:
            # If no date column exists, create a placeholder for 'Year' (or handle accordingly)
            dividend_data['Year'] = range(len(dividend_data))

        fig = px.bar(dividend_data, x='Year', y='Cumulative Dividend', title='Cumulative Dividends Over Time')
        fig.update_layout(xaxis_title="Year", yaxis_title="Cumulative Dividend ($)")
    else:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=[], y=[], name="No Data"))
        fig.update_layout(title='No Dividend Data Available', xaxis_title="Year", yaxis_title="Cumulative Dividend ($)")
        
    return fig

# Function to plot diversification pie chart
def plot_diversification_pie(portfolio: Portfolio):
    """
    Plot the diversification of the portfolio.

    Args:
    portfolio (Portfolio): The user's portfolio object.
    
    Returns:
    A Plotly figure object showing the diversification.
    """
    diversification_data = portfolio.get_diversification_data(portfolio.simulation_date)

    # Check if the DataFrame is empty
    if not diversification_data.empty:
        diversification_data['Value'] = diversification_data['Value'].round(ROUNDDIGIT)
        fig = px.pie(diversification_data, names='Sector', values='Value', title='Portfolio Diversification',
                     color_discrete_sequence=PIE_CHART_COLORS)
    else:
        fig = go.Figure()
        fig.add_trace(go.Pie(labels=[], values=[], name="No Data"))
        fig.update_layout(title='No Diversification Data Available')
    
    fig.update_layout(
        plot_bgcolor=GENERAL_COLORS['background'],
        paper_bgcolor=GENERAL_COLORS['background'],
        font_color=GENERAL_COLORS['text_primary']
    )
    
    return fig

def create_clickable_table(dataframe, table_id, sort_by=None, drop_column=None, highlight_columns=None):
    """
    Create a clickable Dash DataTable with sorting, column deletion, and conditional formatting.

    Args:
    dataframe (pd.DataFrame): The data to display in the table.
    table_id (str): The ID for the table.
    sort_by (str, optional): Column name to sort by. Defaults to None.
    drop_column (str, optional): Column name to drop. Defaults to None.
    highlight_columns (list, optional): Columns to apply conditional formatting. Defaults to None.

    Returns:
    A Dash DataTable component.
    """
    if not dataframe.empty:
        if drop_column and drop_column in dataframe.columns:
            dataframe = dataframe.drop(columns=[drop_column])
        
        if sort_by and sort_by in dataframe.columns:
            dataframe = dataframe.sort_values(by=sort_by, ascending=False)

        data = dataframe.to_dict('records')
        columns = [{'name': col, 'id': col, 'presentation': 'markdown'} for col in dataframe.columns]

        style_data_conditional = [
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': TABLE_COLORS['row_background']
            }
        ]

        if highlight_columns:
            for col in highlight_columns:
                style_data_conditional.extend([
                    {
                        'if': {
                            'filter_query': f'{{{col}}} > 0',
                            'column_id': col
                        },
                        'backgroundColor': TABLE_COLORS['row_text_positive'],
                        'color': GENERAL_COLORS['white']
                    },
                    {
                        'if': {
                            'filter_query': f'{{{col}}} < 0',
                            'column_id': col
                        },
                        'backgroundColor': TABLE_COLORS['row_text_negative'],
                        'color': GENERAL_COLORS['white']
                    }
                ])

        table = dash_table.DataTable(
            id=table_id,
            columns=columns,
            data=data,
            sort_action='native',
            style_table={'height': '600px', 'overflowY': 'auto'},
            style_header={
                'backgroundColor': TABLE_COLORS['header_background'],
                'color': TABLE_COLORS['header_text'],
                'fontWeight': 'bold'
            },
            style_cell={
                'backgroundColor': GENERAL_COLORS['panel_background'],
                'color': GENERAL_COLORS['text_primary'],
                'textAlign': 'left'
            },
            style_data_conditional=style_data_conditional
        )
    else:
        table = html.Div("No Data Available", style={'color': GENERAL_COLORS['text_primary']})

    return table




def plot_income_table(portfolio):
    income_data = portfolio.get_income_data(portfolio.simulation_date)
    return create_clickable_table(income_data, 'income-table')

def plot_detailed_stock_data_table(portfolio):
    detailed_stock_data = portfolio.get_detailed_stock_data(portfolio.simulation_date)
    return create_clickable_table(detailed_stock_data, 'detailed-stock-data-table', highlight_columns=['Change'])

def plot_operation_history_table(portfolio):
    operation_history = portfolio.get_operation_history()
    return create_clickable_table(operation_history, 'operation-history-table', sort_by='Transaction ID')

def plot_current_actives_table(portfolio):
    current_actives = portfolio.get_current_actives()
    return create_clickable_table(current_actives, 'current-actives-table', sort_by='Current Value', drop_column='Current Value', highlight_columns=['Change Over Month (%)','Change Over Year (%)'])
def show_table(table_component):
    """
    Display a Dash DataTable in a standalone Dash app.

    Args:
    table_component: The Dash DataTable component to display.
    """
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    app.layout = html.Div([
        dbc.Row(
            dbc.Col(
                table_component,
                width=12
            ),
            className="mb-4",
        ),
    ])

    app.run_server(debug=True)

# Example usage of visualization functions
if __name__ == "__main__":
    # Example portfolio
    my_portfolio = Portfolio(simulation_date="2023-01-10")
    
    my_portfolio.add_cash(10000)

    # Simulate buying some assets
    my_portfolio.buy_asset('AAPL', 10)  # Buy 10 shares of AAPL
    my_portfolio.buy_asset('GOOGL', 5)  # Buy 5 shares of GOOGL

    # # Plot asset allocation breakdown
    # allocation_fig = plot_allocation_breakdown(my_portfolio)
    # allocation_fig.show()

    # # Plot the portfolio growth over a date range
    # growth_fig = plot_portfolio_growth_over_time(my_portfolio, '2022-12-10', "2023-02-10")
    # growth_fig.show()

    # profit_fig = plot_portfolio_profit_over_time(my_portfolio, '2022-12-10', "2023-02-10")
    # profit_fig.show()

    # # # Plot the price of an asset (AAPL) over a range of dates
    # asset_fig = plot_asset_growth_over_time(my_portfolio, 'AAPL', '2022-01-01', "2023-02-10")
    # asset_fig.show()

    # # # # Plot cumulative dividends over time
    # # # dividend_fig = plot_dividend_cumulative(my_portfolio)
    # # # dividend_fig.show()

    # # Plot diversification pie chart
    # diversification_fig = plot_diversification_pie(my_portfolio)
    # diversification_fig.show()

    # # # Plot stock ticker table
    # # stock_ticker_table = plot_stock_ticker_table(my_portfolio)
    # # show_table(stock_ticker_table)

    # # # Plot income table
    # # income_table = plot_income_table(my_portfolio)
    # # show_table(income_table)

    # Plot detailed stock data table
    # detailed_stock_data_table = plot_detailed_stock_data_table(my_portfolio)
    # show_table(detailed_stock_data_table)

    # # Plot operation history table
    # operation_history = plot_operation_history_table(my_portfolio)
    # show_table(operation_history)

    # # Plot current actives table
    current_actives_table = plot_current_actives_table(my_portfolio)
    show_table(current_actives_table)