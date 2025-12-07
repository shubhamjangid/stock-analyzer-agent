import logging
import yfinance as yf
import requests
from typing import Dict, Any
from transformers import pipeline

from src.config import Config
from src.utils import (
    safe_extract
)

logger = logging.getLogger(__name__)


def fetch_realtime_news(ticker: str, limit: int = None) -> Dict[str, Any]:
    """
    Fetch latest news articles for a given ticker using NewsAPI.
    
    Args:
        ticker: Stock ticker symbol
        limit: Maximum number of articles to fetch
    
    Returns:
        Dictionary containing news articles and sentiment analysis
    """
    limit = limit or Config.NEWS_ARTICLES_LIMIT
    
    try:
        logger.info(f"Fetching news for {ticker}...")
    
        stock = yf.Ticker(ticker)
        info = stock.info
        company_name = safe_extract(info, "longName", default="N/A")
        
        # Use NewsAPI
        url = "https://newsapi.org/v2/everything"
        # url = "https://newsapi.org/v2/top-headlines"
        params = {
            "q": f"{company_name} stock OR {ticker}",
            "apiKey": Config.NEWS_API_KEY,
            # "country": "in",
            "sortBy": "publishedAt",
            "language": "en",
            "pageSize": limit,
        }
        
        response = requests.get(url, params=params, timeout=Config.TIMEOUT_SECONDS)
        response.raise_for_status()
        
        data = response.json()
        articles = data.get("articles", [])
        
        # Process articles
        processed_articles = []
        sentiment_scores = []
        
        for article in articles[:limit]:
            article_sentiment = calculate_article_sentiment(article)
            sentiment_scores.append(article_sentiment)
            
            processed_articles.append({
                "title": article.get("title"),
                "source": safe_extract(article, "source", "name", default="Unknown"),
                "published_at": article.get("publishedAt"),
                "url": article.get("url"),
                "description": article.get("description"),
                "sentiment_score": article_sentiment,
            })
        
        # Calculate aggregate sentiment
        overall_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        
        news_data = {
            "ticker": ticker,
            "total_articles_found": data.get("totalResults", 0),
            "articles_fetched": len(processed_articles),
            "articles": processed_articles,
            "overall_sentiment_score": round(overall_sentiment, 3),
            "sentiment_label": get_sentiment_label(overall_sentiment),
        }
        
        logger.info(f"✓ News fetch completed for {ticker} ({len(processed_articles)} articles)")
        return news_data
    
    except Exception as e:
        logger.error(f"Unexpected error fetching news for {ticker}: {e}")
        return {
            "ticker": ticker,
            "error": str(e),
            "error_type": "news_processing_failed",
            "articles": [],
            "overall_sentiment_score": 0,
        }


def calculate_article_sentiment(article: Dict[str, Any]) -> float:
    """
    Sentiment analysis using HuggingFace multilingual model.
    Returns score between -1 (very negative) and 1 (very positive).
    """

    try:
        title = (article.get("title") or "").strip()
        description = (article.get("description") or "").strip()
        
        # Combine title and description
        text = f"{title} {description}".strip()
        
        if not text or len(text) < 3:
            return 0.0
        
        # Load sentiment analysis model
        sentiment_pipeline = pipeline(
            "text-classification",
            model="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
        )

        # Get sentiment from model
        result = sentiment_pipeline(text)[0]
        
        label = result["label"].lower()
        score = result["score"]
        
        # Map to -1 to 1 scale
        if "positive" in label:
            sentiment = score
        elif "negative" in label:
            sentiment = -score
        else:  # neutral
            sentiment = 0.0
        
        return round(sentiment, 2)
    
    except Exception as e:
        logger.warning(f"Error in sentiment analysis: {e}")
        return 0.0

def get_sentiment_label(sentiment_score: float) -> str:
    """Convert sentiment score to label"""
    if sentiment_score > 0.25:
        return "Positive"
    elif sentiment_score < -0.25:
        return "Negative"
    else:
        return "Neutral"
