import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from portfolio_manager import Portfolio
import plotly.graph_objs as go
from visualization import (
    plot_diversification_pie,
    plot_portfolio_profit_over_time,
    plot_current_actives_table,
    plot_operation_history_table,
    plot_asset_growth_over_time,
    plot_detailed_stock_data_table
)
from datetime import datetime, timedelta
from color_palette import GENERAL_COLORS, GRAPH_COLORS, PIE_CHART_COLORS, TABLE_COLORS  # Import the color palette

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], suppress_callback_exceptions=True)

# Initialize portfolio object
initial_date = "2023-02-01"
portfolio = Portfolio(initial_date)
portfolio.load_portfolio()

# Define the Portfolio Panel layout
portfolio_panel_layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    dcc.DatePickerSingle(
                        id='date-picker',
                        min_date_allowed=datetime(2000, 1, 1),
                        max_date_allowed=datetime.today().strftime('%Y-%m-%d'),
                        initial_visible_month=initial_date,
                        date=initial_date,
                        display_format='YYYY-MM-DD',
                        style={'background-color': GENERAL_COLORS['panel_background'], 'color': GENERAL_COLORS['text_primary'], 'margin-top': '10px'}
                    ),
                    width=6
                ),
                dbc.Col(
                    html.Div(id='current-portfolio-info', style={'color': GENERAL_COLORS['text_primary']}),
                    width=6
                ),
            ],
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(id='plot_portfolio_profit_over_time', style={"height": "400px"}),
                    width=9
                ),
                dbc.Col(
                    dcc.Graph(id='plot_diversification_pie', style={"height": "400px"}),
                    width=3
                ),
            ],
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(id='plot_current_actives_table'),
                    width=8
                ),
                dbc.Col(
                    html.Div(id='plot_operation_history_table'),
                    width=4
                ),
            ],
            className="mb-4",
        ),
        dbc.Col(
            [
                dcc.Dropdown(
                    id='portfolio-action',
                    options=[
                        {'label': 'Buy Asset', 'value': 'buy'},
                        {'label': 'Sell Asset', 'value': 'sell'},
                        {'label': 'Add Cash', 'value': 'add_cash'}  # New option for adding cash
                    ],
                    value='add_cash',
                    style={'background-color': 'white', 'color': 'black'},
                ),
                html.Br(),
                dcc.Input(id='asset-symbol', type='text', placeholder="Asset Symbol", debounce=True, style={'display': 'none', 'color': '#ffffff'}),
                html.Br(),
                dcc.Input(id='asset-quantity', type='number', placeholder="Quantity", debounce=True, style={'display': 'none', 'color': '#ffffff'}),
                html.Br(),
                dcc.Input(id='cash-amount', type='number', placeholder="Cash Amount", debounce=True, style={'display': 'none', 'color': '#ffffff'}),
                html.Br(),
                html.Button('Execute', id='submit-transaction', n_clicks=0, style={'background-color': '#1a1aff', 'color': 'white'}),
            ],
            width=4,
            style={"background-color": "#121212", "padding": "20px", "border-radius": "10px"}
        ),
        dcc.Store(id='portfolio-updated', data=False),  # Hidden store to track portfolio update
        dcc.Interval(id='interval-update', interval=10*1000, n_intervals=0)  # Update every 10 seconds
    ],
    fluid=True,
    style={"background-color": GENERAL_COLORS['background']}
)

# Define the Investment Screen layout
investment_screen_layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    dcc.Input(id='stock-id', type='text', placeholder="Stock ID", style={'color': GENERAL_COLORS['black']}),
                    width=4
                ),
                dbc.Col(
                    dcc.Input(id='buy-amount', type='number', placeholder="Buy Amount", style={'color': GENERAL_COLORS['black']}),
                    width=4
                ),
                dbc.Col(
                    html.Button('Buy', id='buy-button', n_clicks=0, style={'background-color': GRAPH_COLORS['line_blue'], 'color': GENERAL_COLORS['text_primary']}),
                    width=4
                ),
            ],
            className="mb-4",
        ),
        dbc.Row(
            dbc.Col(
                dcc.Graph(id='plot_asset_growth_over_time', style={"height": "300px"}),
                width=12
            ),
            className="mb-4",
        ),
        dbc.Row(
            dbc.Col(
                html.Div(id='plot_detailed_stock_data_table'),
                width=12
            ),
            className="mb-4",
        ),
    ],
    fluid=True,
    style={"background-color": GENERAL_COLORS['background']}
)

# App layout with navigation
app.layout = html.Div([
    dcc.Tabs(id="tabs", value='portfolio-panel', children=[
        dcc.Tab(
            label='Portfolio Panel', 
            value='portfolio-panel', 
            style={'background-color': GENERAL_COLORS['background'], 'color': GENERAL_COLORS['text_primary']},
            selected_style={'background-color': GENERAL_COLORS['black'], 'color': GENERAL_COLORS['text_primary']}
        ),
        dcc.Tab(
            label='Investment Screen', 
            value='investment-screen', 
            style={'background-color': GENERAL_COLORS['background'], 'color': GENERAL_COLORS['text_primary']},
            selected_style={'background-color': GENERAL_COLORS['black'], 'color': GENERAL_COLORS['text_primary']}
        ),
    ]),
    html.Div(id='tabs-content')
])

# Callbacks to update the content based on selected tab
@app.callback(
    Output('tabs-content', 'children'),
    [Input('tabs', 'value')]
)
def render_content(tab):
    if tab == 'portfolio-panel':
        return portfolio_panel_layout
    elif tab == 'investment-screen':
        return investment_screen_layout

# Callbacks for updating the portfolio and dashboard
@app.callback(
    Output('current-portfolio-info', 'children'),
    [Input('date-picker', 'date')]
)
def update_portfolio_info(selected_date):
    portfolio_value = portfolio.get_portfolio_value(selected_date)
    return f"Total Portfolio Value: ${portfolio_value:.2f}"

from dash.dependencies import Input, Output, State
from datetime import datetime, timedelta

@app.callback(
    [Output('plot_diversification_pie', 'figure'),
     Output('plot_portfolio_profit_over_time', 'figure'),
     Output('plot_current_actives_table', 'children'),
     Output('plot_operation_history_table', 'children')],
    [Input('portfolio-updated', 'data'),
     Input('date-picker', 'date')]
)
def update_portfolio_and_plots(is_updated, selected_date):

    # Update the plots based on the selected date
    end_date = selected_date
    start_date = (datetime.strptime(selected_date, "%Y-%m-%d") - timedelta(days=30)).strftime("%Y-%m-%d")

    diversification_pie = plot_diversification_pie(portfolio)
    portfolio_profit = plot_portfolio_profit_over_time(portfolio, start_date, end_date)
    current_actives_table_component = plot_current_actives_table(portfolio)
    operation_history_table_component = plot_operation_history_table(portfolio)

    return (diversification_pie, 
            portfolio_profit, 
            current_actives_table_component, 
            operation_history_table_component)

@app.callback(
    [Output('plot_asset_growth_over_time', 'figure'),
     Output('plot_asset_growth_over_time', 'style')],
    [Input('stock-id', 'value')]
)
def update_asset_growth(stock_id):
    end_date = portfolio.simulation_date
    start_date = (datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=30)).strftime("%Y-%m-%d")
    
    if stock_id:
        asset_growth = plot_asset_growth_over_time(portfolio, stock_id, start_date, end_date)
        return asset_growth, {"height": "300px", "display": "block"}
    
    # Convert start_date and end_date to datetime objects
    start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")
    
    # Create an empty figure with axes titles and limits
    fig = go.Figure(layout=go.Layout(
        xaxis={'title': 'Date', 'range': [start_date_dt, end_date_dt]},
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

    # Return the figure and style
    return fig, {"height": "300px", "display": "block"}

@app.callback(
    Output('plot_detailed_stock_data_table', 'children'),
    [Input('tabs', 'value')]
)
def update_detailed_stock_data_table(tab):
    if tab == 'investment-screen':
        detailed_stock_data_component = plot_detailed_stock_data_table(portfolio)
        return detailed_stock_data_component
    return ""
# New function to update the portfolio
def update_portfolio(action, symbol, quantity, cash_amount):
    if action == 'buy' and symbol and quantity:
        portfolio.buy_asset(symbol, quantity)
    elif action == 'sell' and symbol and quantity:
        portfolio.sell_asset(symbol, quantity)
    elif action == 'add_cash' and cash_amount:
        portfolio.add_cash(cash_amount)

# Callback for updating the portfolio
@app.callback(
    [Output('portfolio-updated', 'data')],
    [Input('submit-transaction', 'n_clicks')],
    [State('portfolio-action', 'value'),
     State('asset-symbol', 'value'),
     State('asset-quantity', 'value'),
     State('cash-amount', 'value')]
)
def update_portfolio_callback(n_clicks, action, symbol, quantity, cash_amount):
    if n_clicks > 0:
        update_portfolio(action, symbol, quantity, cash_amount)
    return [True]

@app.callback(
    [Output('asset-symbol', 'style'),
     Output('asset-quantity', 'style'),
     Output('cash-amount', 'style')],
    [Input('portfolio-action', 'value'),
     Input('portfolio-updated', 'data')],
    [State('portfolio-action', 'value'),
     State('asset-symbol', 'value')]
)
def update_dashboard(action, portfolio_updated, current_action, symbol):
    asset_symbol_style = {'display': 'none', 'color': '#000000'}
    asset_quantity_style = {'display': 'none', 'color': '#000000'}
    cash_amount_style = {'display': 'none', 'color': '#000000'}

    if action == 'buy':
        asset_symbol_style = {'display': 'block', 'color': '#000000'}
        asset_quantity_style = {'display': 'block', 'color': '#000000'}
        if portfolio_updated:
            return asset_symbol_style, asset_quantity_style, cash_amount_style
        return asset_symbol_style, asset_quantity_style, cash_amount_style

    elif action == 'sell':
        asset_symbol_style = {'display': 'block', 'color': '#000000'}
        asset_quantity_style = {'display': 'block', 'color': '#000000'}
        if portfolio_updated and current_action == 'sell' and symbol:
            return asset_symbol_style, asset_quantity_style, cash_amount_style
        return asset_symbol_style, asset_quantity_style, cash_amount_style

    elif action == 'add_cash':
        cash_amount_style = {'display': 'block', 'color': '#000000'}
        if portfolio_updated:
            return asset_symbol_style, asset_quantity_style, cash_amount_style
        return asset_symbol_style, asset_quantity_style, cash_amount_style

    return asset_symbol_style, asset_quantity_style, cash_amount_style


if __name__ == '__main__':
    app.run_server(debug=True)
