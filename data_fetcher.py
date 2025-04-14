import pandas as pd
import yfinance as yf
from forex_python.converter import CurrencyRates
from datetime import datetime, timedelta
import requests
import os
import time

# Define IT sector companies with their stock symbols
IT_COMPANIES = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Google (Alphabet)": "GOOGL",
    "Amazon": "AMZN",
    "Meta (Facebook)": "META",
    "Tesla": "TSLA",
    "NVIDIA": "NVDA",
    "Intel": "INTC",
    "AMD": "AMD",
    "IBM": "IBM",
    "Oracle": "ORCL",
    "Cisco": "CSCO",
    "Adobe": "ADBE",
    "Salesforce": "CRM",
    "PayPal": "PYPL",
    "Netflix": "NFLX",
    "Dell": "DELL",
    "HP": "HPQ",
    "Qualcomm": "QCOM",
    "Texas Instruments": "TXN"
}

def get_stock_data(symbols, start_date, end_date):
    """
    Fetch stock data for the given symbols within the date range.
    
    Args:
        symbols (list): List of stock symbols to fetch
        start_date (datetime.date): Start date for the data
        end_date (datetime.date): End date for the data
        
    Returns:
        DataFrame: Combined stock data with 'Symbol' column added
    """
    # Convert dates to strings for yfinance
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    all_data = []
    
    for symbol in symbols:
        try:
            # Fetch data for this symbol
            stock_data = yf.download(symbol, start=start_str, end=end_str, progress=False)
            
            # Skip if no data
            if stock_data.empty:
                continue
                
            # Add symbol column and reset index to make date a column
            stock_data['Symbol'] = symbol
            stock_data.reset_index(inplace=True)
            
            all_data.append(stock_data)
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
    
    # Combine all data into one DataFrame
    if not all_data:
        return pd.DataFrame()  # Return empty DataFrame if no data
        
    combined_data = pd.concat(all_data, ignore_index=True)
    return combined_data

def get_exchange_rates(base_currency, target_currencies, start_date, end_date):
    """
    Fetch historical exchange rates for the given period.
    
    Args:
        base_currency (str): Base currency code (e.g., 'USD')
        target_currencies (list): List of target currency codes
        start_date (datetime.date): Start date for the data
        end_date (datetime.date): End date for the data
        
    Returns:
        DataFrame: Exchange rate data indexed by date
    """
    # Initialize currency rates object
    c = CurrencyRates()
    
    # Create date range
    date_range = []
    current_date = start_date
    while current_date <= end_date:
        # Only include weekdays to reduce API calls (markets closed on weekends)
        if current_date.weekday() < 5:  # Monday to Friday
            date_range.append(current_date)
        current_date += timedelta(days=1)
    
    # Sample dates if there are too many (to prevent excessive API calls)
    if len(date_range) > 30:
        # Take roughly 30 samples across the date range
        step = max(1, len(date_range) // 30)
        date_range = date_range[::step]
        if date_range[-1] != end_date:
            date_range.append(end_date)
    
    # Fetch rates for each date
    exchange_data = {}
    
    for date in date_range:
        try:
            exchange_data[date] = {}
            dt = datetime.combine(date, datetime.min.time())
            
            for currency in target_currencies:
                try:
                    # Skip if base and target are the same
                    if base_currency == currency:
                        continue
                    
                    # Get exchange rate
                    rate = c.get_rate(base_currency, currency, dt)
                    exchange_data[date][currency] = rate
                    
                    # Add small delay to avoid API rate limits
                    time.sleep(0.1)
                except Exception as e:
                    print(f"Error fetching rate for {currency} on {date}: {e}")
                    exchange_data[date][currency] = None
                    
        except Exception as e:
            print(f"Error processing date {date}: {e}")
    
    # Convert to DataFrame
    df = pd.DataFrame.from_dict(exchange_data, orient='index')
    df.index.name = 'Date'
    
    return df

def get_it_sector_news(company_names, limit=20):
    """
    Fetch news related to the selected IT companies.
    
    Args:
        company_names (list): List of company names to search for
        limit (int): Maximum number of news items to return
        
    Returns:
        list: List of news items with title, description, source, url, etc.
    """
    # Get API key from environment with fallback
    news_api_key = os.getenv("NEWS_API_KEY", "")
    
    if not news_api_key:
        return [{"title": "News API key not available", 
                "description": "Please set the NEWS_API_KEY environment variable.",
                "source": {"name": "System"},
                "url": "#",
                "publishedAt": datetime.now().isoformat(),
                "urlToImage": None}]
    
    # Create search query from company names
    query = " OR ".join([f'"{company}"' for company in company_names])
    query += " AND (technology OR IT OR tech OR software OR hardware OR digital)"
    
    # Endpoint
    url = "https://newsapi.org/v2/everything"
    
    # Parameters
    params = {
        "q": query,
        "apiKey": news_api_key,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": limit
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if response.status_code == 200 and data.get("status") == "ok":
            news_items = data.get("articles", [])
            
            # Format dates and filter for relevance
            for item in news_items:
                if "publishedAt" in item:
                    try:
                        published_date = datetime.strptime(item["publishedAt"], "%Y-%m-%dT%H:%M:%SZ")
                        item["publishedAt"] = published_date.strftime("%Y-%m-%d %H:%M")
                    except:
                        item["publishedAt"] = "Unknown date"
            
            return news_items
        else:
            error_message = data.get("message", "Unknown error")
            print(f"News API error: {error_message}")
            return [{"title": f"Error fetching news: {error_message}", 
                    "description": "Please check your API key and try again.",
                    "source": {"name": "System"},
                    "url": "#",
                    "publishedAt": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "urlToImage": None}]
            
    except Exception as e:
        print(f"Exception fetching news: {e}")
        return [{"title": f"Error connecting to News API: {str(e)}", 
                "description": "Please check your internet connection and try again.",
                "source": {"name": "System"},
                "url": "#",
                "publishedAt": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "urlToImage": None}]
