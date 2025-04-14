import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from data_fetcher import IT_COMPANIES

def plot_stock_performance(stock_df, selected_companies):
    """
    Create a line chart for stock prices over time.
    
    Args:
        stock_df (DataFrame): Stock data with Date, Close, and Symbol columns
        selected_companies (list): Names of selected companies
        
    Returns:
        plotly.graph_objects.Figure: Interactive line chart
    """
    if stock_df.empty:
        # Return empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No stock data available for the selected period",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    # Create mapping from symbol to company name
    symbol_to_company = {v: k for k, v in {company: stock_df[stock_df['Symbol'] == IT_COMPANIES[company]]['Symbol'].iloc[0] 
                        for company in selected_companies 
                        if not stock_df[stock_df['Symbol'] == IT_COMPANIES[company]].empty}.items()}
    
    # Create figure
    fig = px.line(
        stock_df, 
        x='Date', 
        y='Close', 
        color='Symbol',
        labels={'Close': 'Stock Price (USD)', 'Date': 'Date', 'Symbol': 'Company'},
        title='Stock Price Trends',
        hover_data=['Open', 'High', 'Low', 'Close']
    )
    
    # Update traces to use company names instead of symbols
    for trace in fig.data:
        symbol = trace.name
        if symbol in symbol_to_company:
            trace.name = symbol_to_company[symbol]
    
    # Update layout
    fig.update_layout(
        hovermode='x unified',
        legend_title_text='Company',
        height=500
    )
    
    # Add range slider
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=[
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ]
            ),
            rangeslider=dict(visible=True),
            type="date"
        )
    )
    
    return fig

def plot_exchange_rates(exchange_df, base_currency):
    """
    Create a line chart for exchange rates over time.
    
    Args:
        exchange_df (DataFrame): Exchange rate data indexed by date
        base_currency (str): The base currency used
        
    Returns:
        plotly.graph_objects.Figure: Interactive line chart
    """
    if exchange_df.empty:
        # Return empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No exchange rate data available for the selected period",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    # Reset index to make Date a column
    exchange_df = exchange_df.reset_index()
    
    # Melt DataFrame for plotting
    melted_df = pd.melt(
        exchange_df, 
        id_vars=['Date'], 
        var_name='Currency', 
        value_name='Rate'
    )
    
    # Create figure
    fig = px.line(
        melted_df, 
        x='Date', 
        y='Rate', 
        color='Currency',
        labels={'Rate': f'Exchange Rate (per {base_currency})', 'Date': 'Date', 'Currency': 'Currency'},
        title=f'Exchange Rates (Base: {base_currency})'
    )
    
    # Update layout
    fig.update_layout(
        hovermode='x unified',
        legend_title_text='Currency',
        height=500
    )
    
    # Add range slider
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=[
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ]
            ),
            rangeslider=dict(visible=True),
            type="date"
        )
    )
    
    return fig

def create_stock_comparison(stock_df, selected_companies):
    """
    Create a normalized comparison chart for stock performance.
    
    Args:
        stock_df (DataFrame): Stock data with Date, Close, and Symbol columns
        selected_companies (list): Names of selected companies
        
    Returns:
        plotly.graph_objects.Figure: Interactive line chart showing normalized performance
    """
    if stock_df.empty:
        # Return empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No stock data available for the selected period",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    # Create symbol to company name mapping for later use
    symbol_to_company = {IT_COMPANIES[company]: company for company in selected_companies}
    
    # Create figure
    fig = go.Figure()
    
    # Get unique symbols
    symbols = stock_df['Symbol'].unique()
    
    for symbol in symbols:
        # Get data for this symbol
        symbol_data = stock_df[stock_df['Symbol'] == symbol].sort_values('Date')
        
        if symbol_data.empty:
            continue
            
        # Normalize to first day = 100%
        first_price = symbol_data['Close'].iloc[0]
        normalized_prices = (symbol_data['Close'] / first_price) * 100
        
        # Add line for this symbol
        company_name = symbol_to_company.get(symbol, symbol)
        fig.add_trace(
            go.Scatter(
                x=symbol_data['Date'],
                y=normalized_prices,
                name=company_name,
                mode='lines',
                hovertemplate='%{y:.2f}% of initial value<br>Date: %{x}<extra></extra>'
            )
        )
    
    # Update layout
    fig.update_layout(
        title='Relative Stock Performance (Normalized to 100%)',
        xaxis_title='Date',
        yaxis_title='Performance (%)',
        hovermode='x unified',
        legend_title_text='Company',
        height=500
    )
    
    # Add range slider
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=[
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ]
            ),
            rangeslider=dict(visible=True),
            type="date"
        )
    )
    
    # Add reference line at 100%
    fig.add_shape(
        type="line",
        x0=stock_df['Date'].min(),
        y0=100,
        x1=stock_df['Date'].max(),
        y1=100,
        line=dict(
            color="gray",
            width=1,
            dash="dash",
        ),
    )
    
    return fig

def create_volume_chart(stock_df, selected_companies):
    """
    Create a bar chart for trading volumes.
    
    Args:
        stock_df (DataFrame): Stock data with Date, Volume, and Symbol columns
        selected_companies (list): Names of selected companies
        
    Returns:
        plotly.graph_objects.Figure: Interactive bar chart for trading volumes
    """
    if stock_df.empty:
        # Return empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No volume data available for the selected period",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    # Create symbol to company name mapping
    symbol_to_company = {IT_COMPANIES[company]: company for company in selected_companies}
    
    # Ensure dates are in datetime format
    stock_df['Date'] = pd.to_datetime(stock_df['Date'])
    
    # Calculate weekly averages to make the chart cleaner
    stock_df['Week'] = stock_df['Date'].dt.isocalendar().week
    stock_df['Year'] = stock_df['Date'].dt.isocalendar().year
    
    # Group by symbol and week
    weekly_volume = stock_df.groupby(['Symbol', 'Year', 'Week'])['Volume'].mean().reset_index()
    
    # Create a proper date for each week (use the first day of the week)
    def get_week_date(row):
        return pd.to_datetime(f"{row['Year']}-{row['Week']:02d}-1", format='%Y-%W-%w')
    
    weekly_volume['Date'] = weekly_volume.apply(get_week_date, axis=1)
    
    # Create figure
    fig = px.bar(
        weekly_volume, 
        x='Date', 
        y='Volume', 
        color='Symbol',
        labels={'Volume': 'Average Weekly Volume', 'Date': 'Week', 'Symbol': 'Company'},
        title='Trading Volume Trends (Weekly Average)'
    )
    
    # Update traces to use company names instead of symbols
    for trace in fig.data:
        symbol = trace.name
        if symbol in symbol_to_company:
            trace.name = symbol_to_company[symbol]
    
    # Update layout
    fig.update_layout(
        hovermode='x unified',
        legend_title_text='Company',
        height=500
    )
    
    # Add range slider
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=[
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ]
            ),
            rangeslider=dict(visible=True),
            type="date"
        )
    )
    
    return fig
