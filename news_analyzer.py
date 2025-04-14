import streamlit as st
import pandas as pd
import re
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Download NLTK data for sentiment analysis
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

def analyze_sentiment(news_items):
    """
    Analyze sentiment of news headlines, either using pre-computed sentiment
    or using NLTK's VADER sentiment analyzer.
    
    Args:
        news_items (list): List of news dictionaries containing titles
        
    Returns:
        list: List of sentiment scores (-1 to 1) corresponding to each headline
    """
    sentiment_scores = []
    
    for item in news_items:
        # Check if the news item already has a sentiment score
        if "sentiment" in item:
            sentiment_scores.append(item["sentiment"])
            continue
            
        # Otherwise, try to analyze the sentiment using NLTK
        try:
            # Initialize the sentiment analyzer
            sid = SentimentIntensityAnalyzer()
            
            title = item.get('title', '')
            
            # Skip if title is empty
            if not title:
                sentiment_scores.append(0)
                continue
            
            # Get sentiment scores
            scores = sid.polarity_scores(title)
            
            # Compound score ranges from -1 (very negative) to +1 (very positive)
            sentiment_scores.append(scores['compound'])
            
        except Exception as e:
            print(f"Error analyzing sentiment for: {item.get('title', 'N/A')}: {e}")
            sentiment_scores.append(0)  # Neutral if error
    
    return sentiment_scores

def get_sentiment_color(score):
    """Return a color based on sentiment score."""
    if score > 0.2:
        return "green"  # Positive
    elif score < -0.2:
        return "red"    # Negative
    else:
        return "gray"   # Neutral

def get_sentiment_label(score):
    """Return a label based on sentiment score."""
    if score > 0.2:
        return "Positive"
    elif score < -0.2:
        return "Negative"
    else:
        return "Neutral"

def display_news(news_items, sentiment_scores):
    """
    Display news items in an interactive format with sentiment analysis.
    
    Args:
        news_items (list): List of news dictionaries
        sentiment_scores (list): List of sentiment scores for each news item
    """
    if not news_items:
        st.info("No news articles found.")
        return
    
    # Group news by sentiment
    sentiment_groups = {}
    for i, item in enumerate(news_items):
        if i < len(sentiment_scores):
            sentiment = get_sentiment_label(sentiment_scores[i])
            if sentiment not in sentiment_groups:
                sentiment_groups[sentiment] = []
            sentiment_groups[sentiment].append((item, sentiment_scores[i]))
    
    # Add sentiment filter
    sentiment_filter = st.multiselect(
        "Filter by sentiment",
        options=["Positive", "Neutral", "Negative"],
        default=["Positive", "Neutral", "Negative"]
    )
    
    # Count articles in each category
    sentiment_counts = {
        label: len(items) for label, items in sentiment_groups.items()
    }
    
    # Display counters
    cols = st.columns(3)
    cols[0].metric("Positive Articles", sentiment_counts.get("Positive", 0))
    cols[1].metric("Neutral Articles", sentiment_counts.get("Neutral", 0))
    cols[2].metric("Negative Articles", sentiment_counts.get("Negative", 0))
    
    st.markdown("---")
    
    # Display filtered news
    for sentiment in sentiment_filter:
        if sentiment in sentiment_groups and sentiment_groups[sentiment]:
            with st.expander(f"{sentiment} News ({len(sentiment_groups[sentiment])})", expanded=True):
                for item, score in sentiment_groups[sentiment]:
                    title = item.get('title', 'No title available')
                    source = item.get('source', {}).get('name', 'Unknown source')
                    published_at = item.get('publishedAt', 'Unknown date')
                    url = item.get('url', '#')
                    description = item.get('description', 'No description available')
                    
                    # Create container for the news item
                    news_container = st.container()
                    
                    with news_container:
                        # Title with sentiment indicator and link
                        st.markdown(
                            f"<h3 style='color:{get_sentiment_color(score)};margin-bottom:0px;'>"
                            f"{title}</h3>", 
                            unsafe_allow_html=True
                        )
                        
                        # Source and date info
                        st.markdown(
                            f"<p style='margin-top:0px;'><small>"
                            f"Source: {source} | Published: {published_at} | "
                            f"Sentiment: {get_sentiment_label(score)}</small></p>",
                            unsafe_allow_html=True
                        )
                        
                        # Description 
                        if description:
                            # Truncate long descriptions
                            if len(description) > 300:
                                description = description[:297] + "..."
                            st.markdown(description)
                        
                        # Link to full article
                        st.markdown(f"[Read full article]({url})", unsafe_allow_html=True)
                        
                        st.markdown("---")
