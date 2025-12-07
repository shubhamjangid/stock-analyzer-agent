import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import json
import os
from src.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def safe_extract(data: Dict, *keys, default: Any = None) -> Any:
    """Safely extract nested dictionary values"""
    current = data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key, default)
        else:
            return default
    return current


def calculate_sma(prices: List[float], period: int) -> Optional[float]:
    """Calculate Simple Moving Average"""
    if not prices or len(prices) < period:
        return None
    return sum(prices[-period:]) / period


def calculate_rsi(prices: List[float], period: int = 14) -> Optional[float]:
    """Calculate Relative Strength Index (RSI)"""
    if not prices or len(prices) < period + 1:
        return None
    
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    
    gains = [delta if delta > 0 else 0 for delta in deltas]
    losses = [-delta if delta < 0 else 0 for delta in deltas]
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100 if avg_gain > 0 else 0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return round(rsi, 2)

    
def init_langsmith_tracing():
    """
    Initialize LangSmith / LangChain tracing based on environment variables.
    Does nothing if LANGSMITH_TRACING is false.
    """
    if not Config.LANGSMITH_TRACING:
        return

    # LangSmith (new-style) environment variables
    os.environ.setdefault("LANGSMITH_TRACING", "true")
    os.environ.setdefault("LANGSMITH_API_KEY", Config.LANGSMITH_API_KEY)
    os.environ.setdefault("LANGSMITH_ENDPOINT", Config.LANGSMITH_ENDPOINT)
    os.environ.setdefault("LANGSMITH_PROJECT", Config.LANGSMITH_PROJECT)

    # Backwards-compatible LangChain v2 tracing envs (some guides still use these)
    os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
    os.environ.setdefault("LANGCHAIN_ENDPOINT", Config.LANGSMITH_ENDPOINT)
    os.environ.setdefault("LANGCHAIN_API_KEY", Config.LANGSMITH_API_KEY)
    os.environ.setdefault("LANGCHAIN_PROJECT", Config.LANGSMITH_PROJECT)

    logger.info(
        f"LangSmith tracing enabled for project '{Config.LANGSMITH_PROJECT}' "
        f"at endpoint {Config.LANGSMITH_ENDPOINT}"
    )