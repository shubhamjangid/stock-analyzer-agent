import logging
import yfinance as yf
from typing import Dict, Optional, Any

from src.utils import (
    safe_extract
)

logger = logging.getLogger(__name__)

def check_analyst_ratings(ticker: str) -> Dict[str, Any]:
    """
    Fetch consensus analyst ratings and price targets.
    
    Args:
        ticker: Stock ticker symbol
    
    Returns:
        Dictionary containing analyst ratings and targets
    """
    try:
        logger.info(f"Fetching analyst ratings for {ticker}...")
        
        stock = yf.Ticker(ticker)
        info = stock.info
        
        ratings = {
            "ticker": ticker,
            "target_price": safe_extract(info, "targetMeanPrice", default=None),
            "target_price_high": safe_extract(info, "targetHighPrice", default=None),
            "target_price_low": safe_extract(info, "targetLowPrice", default=None),
            "number_of_analysts": safe_extract(info, "numberOfAnalystOpinions", default=0),
            "recommendation_key": safe_extract(info, "recommendationKey", default="none"),
            "recommendation": map_recommendation(safe_extract(info, "recommendationKey")),
        }

        logger.info(f"Analyst ratings fetch completed for {ticker}")
        return ratings
    
    except Exception as e:
        logger.error(f"Error fetching analyst ratings for {ticker}: {e}")
        return {
            "ticker": ticker,
            "error": str(e),
            "error_type": "analyst_ratings_failed",
            "recommendation": "unknown"
        }


def map_recommendation(key: Optional[str]) -> str:
    """Map yfinance recommendation key to human-readable format"""
    recommendation_map = {
        "strongBuy": "Strong Buy",
        "buy": "Buy",
        "hold": "Hold",
        "sell": "Sell",
        "strongSell": "Strong Sell",
        "none": "No Rating",
    }
    return recommendation_map.get(key, "Unknown")