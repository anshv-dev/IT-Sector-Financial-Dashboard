# IT Sector Financial Dashboard

A Streamlit-based financial dashboard that aggregates and visualizes IT sector metrics including stocks, exchange rates, and news.

## Features

- **Stock Performance**: Track and visualize stock prices and trading volumes for major IT companies
- **Exchange Rates**: Monitor currency exchange rates for major global currencies
- **IT Sector News**: View latest news from the tech industry with sentiment analysis

## Technologies Used

- **Python**: Core programming language
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive data visualization
- **NLTK**: Natural language processing for sentiment analysis
- **YFinance**: Yahoo Finance API wrapper for stock data
- **Forex-Python**: For currency exchange rates

## Getting Started

1. Clone the repository:
```bash
git clone https://github.com/anshv-dev/IT-Sector-Financial-Dashboard.git
cd IT-Sector-Financial-Dashboard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## Project Structure

- `app.py`: Main Streamlit application
- `data_fetcher.py`: Functions for retrieving financial data (stocks, exchange rates, news)
- `visualizations.py`: Functions for creating interactive charts and graphs
- `news_analyzer.py`: News processing and sentiment analysis functionality

## Screenshot

![Dashboard Screenshot](generated-icon.png)

## License

MIT License