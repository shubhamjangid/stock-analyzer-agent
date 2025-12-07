import logging
import yfinance as yf
from typing import Dict, Optional, Any

from src.config import Config
from src.utils import (
    calculate_sma, 
    calculate_rsi
)

logger = logging.getLogger(__name__)


def get_technical_indicators(ticker: str, period_days: int = 200) -> Dict[str, Any]:
    """
    Calculate technical indicators including SMA and RSI.
    
    Args:
        ticker: Stock ticker symbol
        period_days: Number of days of historical data to fetch
    
    Returns:
        Dictionary containing technical indicators
    """
    try:
        logger.info(f"Calculating technical indicators for {ticker}...")
        
        stock = yf.Ticker(ticker)
        hist = stock.history(period=f"{period_days}d")
        
        if hist.empty:
            raise ValueError(f"No historical data available for {ticker}")
        
        prices = hist["Close"].tolist()
        
        # Calculate moving averages
        sma_50 = calculate_sma(prices, Config.TECHNICAL_PERIOD_SHORT)
        sma_200 = calculate_sma(prices, Config.TECHNICAL_PERIOD_LONG)
        
        # Calculate RSI
        rsi = calculate_rsi(prices, Config.RSI_PERIOD)
        
        # Current price
        current_price = prices[-1] if prices else None
        
        # Price change
        price_change = None
        price_change_pct = None
        if len(prices) > 1:
            price_change = current_price - prices[0]
            price_change_pct = (price_change / prices[0] * 100) if prices[0] != 0 else 0
        
        # Golden cross / Death cross detection
        golden_cross = None
        if sma_50 and sma_200:
            if sma_50 > sma_200:
                golden_cross = "Golden Cross (Bullish)"
            elif sma_50 < sma_200:
                golden_cross = "Death Cross (Bearish)"
        
        # Volume analysis
        avg_volume = hist["Volume"].mean() if "Volume" in hist.columns else None
        current_volume = hist["Volume"].iloc[-1] if "Volume" in hist.columns else None
        volume_trend = "High" if current_volume and avg_volume and current_volume > avg_volume * 1.2 else "Normal"
        
        indicators = {
            "ticker": ticker,
            "analysis_period_days": period_days,
            "current_price": current_price,
            "price_change": price_change,
            "price_change_pct": price_change_pct,
            "sma_50": sma_50,
            "sma_200": sma_200,
            "golden_cross_status": golden_cross,
            "rsi": rsi,
            "rsi_signal": get_rsi_signal(rsi) if rsi else None,
            "avg_volume": avg_volume,
            "current_volume": current_volume,
            "volume_trend": volume_trend,
            "high_52w": hist["High"].max(),
            "low_52w": hist["Low"].min(),
        }
        
        logger.info(f"Technical analysis completed for {ticker}")
        return indicators
    
    except Exception as e:
        logger.error(f"Error calculating technical indicators for {ticker}: {e}")
        return {
            "ticker": ticker,
            "error": str(e),
            "error_type": "technical_analysis_failed"
        }


def get_rsi_signal(rsi: Optional[float]) -> Optional[str]:
    """Convert RSI value to trading signal"""
    if rsi is None:
        return None
    
    if rsi >= Config.RSI_OVERBOUGHT:
        return "Overbought - Potential Sell Signal"
    elif rsi <= Config.RSI_OVERSOLD:
        return "Oversold - Potential Buy Signal"
    else:
        return "Neutral"
