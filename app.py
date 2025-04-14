import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go
from data_fetcher import (
    get_stock_data, 
    get_exchange_rates, 
    get_it_sector_news,
    IT_COMPANIES
)
from visualizations import (
    plot_stock_performance,
    plot_exchange_rates,
    create_stock_comparison,
    create_volume_chart
)
from news_analyzer import analyze_sentiment, display_news

# Page configuration
st.set_page_config(
    page_title="IT Sector Financial Dashboard",
    page_icon="💹",
    layout="wide"
)

# Main title
st.title("IT Sector Financial Dashboard")

# Sidebar for controls
st.sidebar.header("Dashboard Controls")

# Date range selector
today = datetime.date.today()
past_year = today - datetime.timedelta(days=365)

start_date = st.sidebar.date_input(
    "Start Date",
    value=past_year,
    max_value=today - datetime.timedelta(days=1)
)

end_date = st.sidebar.date_input(
    "End Date",
    value=today,
    min_value=start_date,
    max_value=today
)

# Company selection
selected_companies = st.sidebar.multiselect(
    "Select IT Companies",
    options=IT_COMPANIES.keys(),
    default=list(IT_COMPANIES.keys())[:5]  # Default to first 5 companies
)

# Base currency for exchange rates
base_currency = st.sidebar.selectbox(
    "Base Currency",
    options=["USD", "EUR", "GBP", "JPY", "CAD"],
    index=0
)

# Main dashboard tabs
tab1, tab2, tab3 = st.tabs(["Stock Performance", "Exchange Rates", "IT Sector News"])

# Check if companies are selected
if not selected_companies:
    st.warning("Please select at least one company from the sidebar.")
else:
    company_symbols = [IT_COMPANIES[company] for company in selected_companies]

    with tab1:
        st.header("Stock Performance")
        
        # Loading data indicator
        with st.spinner("Loading stock data..."):
            try:
                # Fetch stock data
                stock_df = get_stock_data(company_symbols, start_date, end_date)
                
                # Stock performance metrics
                st.subheader("Stock Price Overview")
                
                # Display stock performance chart
                stock_fig = plot_stock_performance(stock_df, selected_companies)
                st.plotly_chart(stock_fig, use_container_width=True)
                
                # Stock comparison
                st.subheader("Stock Price Comparison")
                comparison_fig = create_stock_comparison(stock_df, selected_companies)
                st.plotly_chart(comparison_fig, use_container_width=True)
                
                # Trading volume
                st.subheader("Trading Volume")
                volume_fig = create_volume_chart(stock_df, selected_companies)
                st.plotly_chart(volume_fig, use_container_width=True)
                
                # Key metrics table
                st.subheader("Key Metrics")
                
                # Calculate key metrics for each stock
                metrics_data = []
                
                for i, company in enumerate(selected_companies):
                    symbol = IT_COMPANIES[company]
                    company_data = stock_df[stock_df['Symbol'] == symbol]
                    
                    if not company_data.empty:
                        start_price = company_data.iloc[0]['Close']
                        end_price = company_data.iloc[-1]['Close']
                        price_change = end_price - start_price
                        percent_change = (price_change / start_price) * 100
                        high = company_data['High'].max()
                        low = company_data['Low'].min()
                        volume_avg = company_data['Volume'].mean()
                        
                        metrics_data.append({
                            "Company": company,
                            "Symbol": symbol,
                            "Start Price": f"${start_price:.2f}",
                            "End Price": f"${end_price:.2f}",
                            "Change": f"${price_change:.2f}",
                            "Change %": f"{percent_change:.2f}%",
                            "High": f"${high:.2f}",
                            "Low": f"${low:.2f}",
                            "Avg. Volume": f"{volume_avg:.0f}"
                        })
                
                metrics_df = pd.DataFrame(metrics_data)
                st.dataframe(metrics_df, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error loading stock data: {str(e)}")

    with tab2:
        st.header("Exchange Rates")
        
        with st.spinner("Loading exchange rate data..."):
            try:
                # Target currencies
                target_currencies = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CNY", "INR"]
                
                # Remove base currency from targets
                if base_currency in target_currencies:
                    target_currencies.remove(base_currency)
                
                # Fetch exchange rate data
                exchange_df = get_exchange_rates(base_currency, target_currencies, start_date, end_date)
                
                # Display exchange rates chart
                exchange_fig = plot_exchange_rates(exchange_df, base_currency)
                st.plotly_chart(exchange_fig, use_container_width=True)
                
                # Latest exchange rates
                st.subheader(f"Latest Exchange Rates (Base: {base_currency})")
                
                latest_rates = {}
                for currency in target_currencies:
                    currency_data = exchange_df[currency].iloc[-1] if not exchange_df.empty else "N/A"
                    latest_rates[currency] = currency_data
                
                # Create two columns for exchange rate display
                col1, col2 = st.columns(2)
                
                for i, (currency, rate) in enumerate(latest_rates.items()):
                    rate_display = f"{float(rate):.4f}" if rate != "N/A" else "N/A"
                    if i % 2 == 0:
                        col1.metric(f"{currency}/{base_currency}", rate_display)
                    else:
                        col2.metric(f"{currency}/{base_currency}", rate_display)
            
            except Exception as e:
                st.error(f"Error loading exchange rate data: {str(e)}")

    with tab3:
        st.header("IT Sector News")
        
        with st.spinner("Loading latest news..."):
            try:
                # Fetch news
                news_items = get_it_sector_news(selected_companies)
                
                if news_items:
                    # Analyze sentiment of news headlines
                    sentiment_results = analyze_sentiment(news_items)
                    
                    # Display sentiment summary
                    st.subheader("News Sentiment Analysis")
                    
                    sentiment_counts = {
                        "Positive": sum(1 for s in sentiment_results if s > 0),
                        "Neutral": sum(1 for s in sentiment_results if s == 0),
                        "Negative": sum(1 for s in sentiment_results if s < 0)
                    }
                    
                    # Create sentiment pie chart
                    fig = px.pie(
                        values=list(sentiment_counts.values()),
                        names=list(sentiment_counts.keys()),
                        color=list(sentiment_counts.keys()),
                        color_discrete_map={'Positive': 'green', 'Neutral': 'gray', 'Negative': 'red'},
                        title="News Sentiment Distribution"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display news articles
                    st.subheader("Latest IT Sector News")
                    display_news(news_items, sentiment_results)
                    
                else:
                    st.info("No news articles found for the selected companies.")
                
            except Exception as e:
                st.error(f"Error loading news data: {str(e)}")

# Footer
st.markdown("---")
st.caption("Data sources: Yahoo Finance, Exchange Rates API, NewsAPI")
st.caption("© 2023 IT Sector Financial Dashboard")
