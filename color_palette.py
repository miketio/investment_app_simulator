# Define the color palette based on the image

colors = {
    'background': '#1e1e1e',   # Dark gray background
    'panel_background': '#2a2a2a',  # Slightly lighter gray for cards/panels
    'primary_text': '#d0d0d0',  # Light gray text
    'secondary_text': '#a0a0a0',  # Muted gray for secondary text
    'positive': '#6dcf73',  # Bright green for gains/positive changes
    'negative': '#ff6347',  # Bright red for losses/negative changes
    'highlight_yellow': '#f1c40f',  # Bright yellow for highlights
    'blue': '#3498db',  # Light blue for trends and graphs
    'orange': '#e67e22',  # Orange for pie charts or highlights
    'green': '#2ecc71',  # Green for trends in line charts
    'red': '#e74c3c',  # Red for trends in line charts
    'purple': '#9b59b6',  # Purple for additional segments in pie charts
    'link_text': '#3498db',  # Light blue for links
    'black': '#000000',
    'white': '#ffffff'
}

# Example color usage in the app
GENERAL_COLORS = {
    'background': colors['background'],
    'panel_background': colors['panel_background'],
    'text_primary': colors['primary_text'],
    'text_secondary': colors['secondary_text'],
    'accent_positive': colors['positive'],
    'accent_negative': colors['negative'],
    'highlight': colors['highlight_yellow'],
    'black': colors['black'],
    'white': colors['white']
}

GRAPH_COLORS = {
    'line_blue': colors['blue'],
    'line_red': colors['red'],
    'line_green': colors['green'],
    'highlight_yellow': colors['highlight_yellow'],
    'bar_orange': colors['orange'],
    'marker': colors['highlight_yellow']
}

PIE_CHART_COLORS = [
    colors['blue'], colors['highlight_yellow'], colors['red'],
    colors['green'], colors['purple'], colors['orange']
]

# Example: Table Styling
TABLE_COLORS = {
    'header_background': colors['panel_background'],
    'header_text': colors['primary_text'],
    'row_background': colors['background'],
    'row_text_positive': colors['positive'],
    'row_text_negative': colors['negative']
}

# Example usage in a graph or table:
# print("APP_COLORS:", GENERAL_COLORS)
# print("GRAPH_COLORS:", GRAPH_COLORS)
# print("TABLE_COLORS:", TABLE_COLORS)
