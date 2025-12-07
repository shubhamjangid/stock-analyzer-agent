import logging
import yfinance as yf
from typing import Dict, Any

from src.utils import (
    safe_extract
)

logger = logging.getLogger(__name__)


def perform_fundamental_analysis(ticker: str) -> Dict[str, Any]:
    """
    Perform comprehensive fundamental analysis for a given stock ticker.
    
    Args:
        ticker: Stock ticker symbol (e.g., "AAPL")
    
    Returns:
        Dictionary containing fundamental metrics
    """
    try:
        logger.info(f"Fetching fundamental data for {ticker}...")
        
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Extract key metrics
        fundamentals = {
            "ticker": ticker,
            "company_name": safe_extract(info, "longName", default="N/A"),
            "sector": safe_extract(info, "sector", default="N/A"),
            "industry": safe_extract(info, "industry", default="N/A"),
            "market_cap": safe_extract(info, "marketCap", default=0),
            "pe_ratio": safe_extract(info, "trailingPE", default=None),
            "forward_pe": safe_extract(info, "forwardPE", default=None),
            "ps_ratio": safe_extract(info, "priceToSalesTrailing12Months", default=None),
            "pb_ratio": safe_extract(info, "priceToBook", default=None),
            "eps": safe_extract(info, "trailingEps", default=None),
            "earnings_growth": safe_extract(info, "earningsGrowth", default=None),
            "revenue": safe_extract(info, "totalRevenue", default=None),
            "revenue_per_share": safe_extract(info, "revenuePerShare", default=None),
            "gross_profit": safe_extract(info, "grossProfits", default=None),
            "operating_margin": safe_extract(info, "operatingMargins", default=None),
            "profit_margin": safe_extract(info, "profitMargins", default=None),
            "debt_to_equity": safe_extract(info, "debtToEquity", default=None),
            "current_ratio": safe_extract(info, "currentRatio", default=None),
            "roe": safe_extract(info, "returnOnEquity", default=None),
            "roa": safe_extract(info, "returnOnAssets", default=None),
            "dividend_yield": safe_extract(info, "dividendYield", default=None),
            "payout_ratio": safe_extract(info, "payoutRatio", default=None),
            "book_value": safe_extract(info, "bookValue", default=None),
            "52_week_high": safe_extract(info, "fiftyTwoWeekHigh", default=None),
            "52_week_low": safe_extract(info, "fiftyTwoWeekLow", default=None),
            "current_price": safe_extract(info, "currentPrice", default=None),
        }
        
        # Fallback: fetch historical data if current_price not available
        if not fundamentals["current_price"]:
            hist = stock.history(period="1d")
            if not hist.empty:
                fundamentals["current_price"] = hist["Close"].iloc[-1]
        
        logger.info(f"Fundamental analysis completed for {ticker}")
        return fundamentals
    
    except Exception as e:
        logger.error(f"Error fetching fundamental data for {ticker}: {e}")
        return {
            "ticker": ticker,
            "error": str(e),
            "error_type": "fundamental_analysis_failed"
        }