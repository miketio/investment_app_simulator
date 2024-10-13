# Investment Dashboard

This Investment Dashboard is a web application built using Dash and Plotly, designed to help users manage and visualize their investment portfolios. The dashboard provides two main screens: the Portfolio Panel and the Investment Screen.

## Features

### Portfolio Panel
- **Date Picker**: Select a date to view the portfolio's status on that specific day.
- **Current Portfolio Info**: Displays the total value of the portfolio.
- **Diversification Pie Chart**: Visual representation of the portfolio's asset allocation.
- **Portfolio Profit Over Time**: Line chart showing the portfolio's profit over a selected date range.
- **Current Actives Table**: Detailed table of current active investments.
- **Operation History Table**: Table showing the history of operations performed on the portfolio.

### Investment Screen
- **Stock ID Input**: Enter the stock symbol to view its details.
- **Buy Amount Input**: Specify the amount of stock to buy.
- **Buy Button**: Execute the purchase of the specified stock.
- **Asset Growth Over Time**: Line chart showing the growth of the selected asset over time.
- **Detailed Stock Data Table**: Table displaying detailed information about the selected stock.

## Interactivity
- **Clickable Symbols**: In the Detailed Stock Data Table, clicking on a stock symbol will automatically switch to the Investment Screen, populate the Stock ID input with the selected symbol, and update the Asset Growth Over Time chart.
